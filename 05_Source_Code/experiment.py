"""
UAS AI - Phishing URL Detection: Leakage-aware re-evaluation of NLP+SVM (PhiUSIIL)
Replicates Aritonang et al. (2026) ~99.99% then audits WHY, via feature-availability
partitioning + quasi-leak ablation + NLP isolation + multi-model baselines.
Dataset: canonical PhiUSIIL (235,795 x 56). label: 1=legitimate, 0=phishing.
"""
import json, time, warnings, numpy as np, pandas as pd, os
warnings.filterwarnings("ignore")
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from scipy.sparse import hstack, csr_matrix

# Helper to resolve files regardless of where script is run from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def resolve_path(relative_path):
    # Try relative to BASE_DIR first
    path_from_base = os.path.abspath(os.path.join(BASE_DIR, relative_path))
    if os.path.exists(path_from_base):
        return path_from_base
    # Fallback to relative to current working directory
    path_from_cwd = os.path.abspath(relative_path)
    if os.path.exists(path_from_cwd):
        return path_from_cwd
    # Fallback to checking from root if in Docker
    if relative_path.startswith("../"):
        stripped = relative_path.lstrip("./").replace("../", "")
        path_docker = os.path.abspath(os.path.join(BASE_DIR, stripped))
        if os.path.exists(path_docker):
            return path_docker
        path_root = os.path.abspath(os.path.join(os.getcwd(), stripped))
        if os.path.exists(path_root):
            return path_root
    return path_from_base

df = pd.read_csv(resolve_path("../04_Dataset/Raw_Dataset/PhiUSIIL_Dataset.csv"))
y = df["label"].values  # 1=legit, 0=phishing

# ---- Feature partitioning ----
QUASI_LEAK = ["URLSimilarityIndex"]  # legit==100.0 always; corr 0.86 (near-deterministic)

URL_ONLY = ["URLLength","DomainLength","IsDomainIP","TLDLegitimateProb","URLCharProb",
    "TLDLength","NoOfSubDomain","HasObfuscation","NoOfObfuscatedChar","ObfuscationRatio",
    "NoOfLettersInURL","LetterRatioInURL","NoOfDegitsInURL","DegitRatioInURL","NoOfEqualsInURL",
    "NoOfQMarkInURL","NoOfAmpersandInURL","NoOfOtherSpecialCharsInURL","SpacialCharRatioInURL",
    "IsHTTPS","CharContinuationRate"]  # derivable from URL string alone (pre-visit)

CONTENT = ["LineOfCode","LargestLineLength","HasTitle","DomainTitleMatchScore","URLTitleMatchScore",
    "HasFavicon","Robots","IsResponsive","NoOfURLRedirect","NoOfSelfRedirect","HasDescription",
    "NoOfPopup","NoOfiFrame","HasExternalFormSubmit","HasSocialNet","HasSubmitButton","HasHiddenFields",
    "HasPasswordField","Bank","Pay","Crypto","HasCopyrightInfo","NoOfImage","NoOfCSS","NoOfJS",
    "NoOfSelfRef","NoOfEmptyRef","NoOfExternalRef"]  # require fetching/rendering the page

FULL = QUASI_LEAK + URL_ONLY + CONTENT  # all 50 numeric (what the paper used)

idx_tr, idx_te = train_test_split(np.arange(len(df)), test_size=0.2, random_state=42, stratify=y)
y_tr, y_te = y[idx_tr], y[idx_te]

def evaluate(name, Xtr, Xte, model):
    t=time.time(); model.fit(Xtr, y_tr)
    pred = model.predict(Xte)
    try:
        score = model.decision_function(Xte)
    except Exception:
        score = model.predict_proba(Xte)[:,1]
    auc = roc_auc_score(y_te, score)
    return {"setup":name,"model":type(model).__name__,
        "acc":round(accuracy_score(y_te,pred),4),
        "prec":round(precision_score(y_te,pred),4),
        "rec":round(recall_score(y_te,pred),4),
        "f1":round(f1_score(y_te,pred),4),
        "auc":round(auc,4),"sec":round(time.time()-t,1)}

def scaled(cols):
    sc = StandardScaler().fit(df.iloc[idx_tr][cols].values)
    return sc.transform(df.iloc[idx_tr][cols].values), sc.transform(df.iloc[idx_te][cols].values)

results=[]
# ---- 1. Structural feature-set ablation (SVM linear = faithful to paper's code) ----
sets = {"FULL (50 feat, =paper)":FULL,
        "minus URLSimilarityIndex":URL_ONLY+CONTENT,
        "URL-only (pre-visit)":URL_ONLY,
        "CONTENT-only (needs fetch)":CONTENT}
for name,cols in sets.items():
    Xtr,Xte = scaled(cols)
    results.append(evaluate(name, Xtr, Xte, LinearSVC(C=1.0, random_state=42, max_iter=5000)))

# ---- 2. Multi-model baseline on FULL vs URL-only ----
for name,cols in {"FULL":FULL,"URL-only":URL_ONLY}.items():
    Xtr,Xte=scaled(cols)
    for m in [LogisticRegression(max_iter=1000),
              RandomForestClassifier(n_estimators=100,n_jobs=-1,random_state=42)]:
        results.append(evaluate(f"{name} [baseline]", Xtr, Xte, m))

# ---- 3. NLP isolation: TF-IDF char n-gram on URL string ----
tf = TfidfVectorizer(analyzer="char_wb", ngram_range=(3,5), max_features=20000)
Xtr_nlp = tf.fit_transform(df.iloc[idx_tr]["URL"].values)
Xte_nlp = tf.transform(df.iloc[idx_te]["URL"].values)
results.append(evaluate("NLP-only (URL char 3-5gram)", Xtr_nlp, Xte_nlp, LinearSVC(C=1.0,random_state=42,max_iter=5000)))
# combined: URL-only structural + NLP
sc=StandardScaler().fit(df.iloc[idx_tr][URL_ONLY].values)
comb_tr=hstack([csr_matrix(sc.transform(df.iloc[idx_tr][URL_ONLY].values)), Xtr_nlp])
comb_te=hstack([csr_matrix(sc.transform(df.iloc[idx_te][URL_ONLY].values)), Xte_nlp])
results.append(evaluate("URL-struct + NLP (combined)", comb_tr, comb_te, LinearSVC(C=1.0,random_state=42,max_iter=5000)))

# ---- 4. 5-fold CV on headline contrast (SVM) ----
cv = StratifiedKFold(5, shuffle=True, random_state=42)
cv_out={}
for name,cols in {"FULL":FULL,"URL-only":URL_ONLY}.items():
    from sklearn.pipeline import make_pipeline
    pipe=make_pipeline(StandardScaler(), LinearSVC(C=1.0,random_state=42,max_iter=5000))
    s=cross_val_score(pipe, df[cols].values, y, cv=cv, scoring="f1")
    cv_out[name]={"f1_mean":round(s.mean(),4),"f1_std":round(s.std(),4)}

res=pd.DataFrame(results)
print(res.to_string(index=False))
print("\n5-fold CV (F1, SVM):", json.dumps(cv_out))
json.dump({"results":results,"cv":cv_out}, open(os.path.join(BASE_DIR, "experiment_results.json"),"w"), indent=1)
