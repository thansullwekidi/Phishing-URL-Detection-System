"""
Cross-dataset generalization test for phishing-URL detection.
D1 = PhiUSIIL (canonical, 235,795) ; D2 = ESDAUNG/PhishDataset balanced (20,000).
Unified label: phishing = 1, legitimate = 0  (PhiUSIIL is flipped; D2 already phishing=1).
Same lexical extractor + char n-gram applied to BOTH -> only distribution differs.
"""
import re, time, json, warnings, numpy as np, pandas as pd, os
warnings.filterwarnings("ignore")
from urllib.parse import urlparse
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, recall_score, precision_score

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

IP_RE = re.compile(r"(\d{1,3}\.){3}\d{1,3}")
def feats(u):
    u = str(u)
    p = urlparse(u if "//" in u else "http://"+u)
    host, path = p.netloc, p.path
    digits = sum(c.isdigit() for c in u)
    special = sum(not c.isalnum() for c in u)
    return [
        len(u), len(host), len(path),
        u.count("."), u.count("-"), u.count("_"), u.count("/"),
        u.count("?"), u.count("="), u.count("@"), u.count("&"), u.count("%"),
        digits, digits/max(len(u),1), special, special/max(len(u),1),
        1 if IP_RE.search(host) else 0,
        1 if p.scheme=="https" else 0,
        max(host.count(".")-1,0), 1 if "@" in u else 0,
        len(host.split(".")[-1]) if "." in host else 0,
        max((len(t) for t in re.split(r"[\W_]+",u)), default=0),
    ]
FNAMES=["url_len","host_len","path_len","n_dot","n_hyphen","n_us","n_slash","n_q","n_eq",
        "n_at","n_amp","n_pct","n_dig","dig_ratio","n_spec","spec_ratio","has_ip","is_https",
        "n_subdom","has_at","tld_len","longest_token"]

# ---- load ----
d1 = pd.read_csv(resolve_path("../04_Dataset/Raw_Dataset/PhiUSIIL_Dataset.csv"))
u1 = np.array(d1["URL"].astype(str).values)
y1 = np.array((d1["label"].values==0).astype(int))            # phishing=1
d2 = pd.read_excel(resolve_path("../04_Dataset/Raw_Dataset/PhishDataset_20000.xlsx"))
u2 = np.array(d2["URLs"].astype(str).values)
y2 = np.array(d2["Labels"].values.astype(int))                 # phishing=1
print("D1 PhiUSIIL:", len(u1), "phishing_frac", round(y1.mean(),3))
print("D2 PhishDS :", len(u2), "phishing_frac", round(y2.mean(),3))

t=time.time()
X1 = np.array([feats(u) for u in u1]); X2 = np.array([feats(u) for u in u2])
print("lexical extract done", round(time.time()-t,1),"s")

Xtr,Xte,ytr,yte = train_test_split(X1,y1,test_size=0.2,random_state=42,stratify=y1)

def run(model, Xtr,ytr, tests):
    model.fit(Xtr,ytr); out={}
    for nm,(Xx,yy) in tests.items():
        pr=model.predict(Xx)
        try: sc=model.decision_function(Xx)
        except: sc=model.predict_proba(Xx)[:,1]
        out[nm]={"acc":round(accuracy_score(yy,pr),4),"f1":round(f1_score(yy,pr),4),
                 "rec":round(recall_score(yy,pr),4),"prec":round(precision_score(yy,pr),4),
                 "auc":round(roc_auc_score(yy,sc),4)}
    return out

# ---- LEXICAL: scale on PhiUSIIL train only ----
sc=StandardScaler().fit(Xtr)
tests={"D1 in-dist (PhiUSIIL hold)":(sc.transform(Xte),yte),
       "D2 CROSS (PhishDataset)":(sc.transform(X2),y2)}
res={}
res["SVM lexical"]=run(LinearSVC(C=1.0,random_state=42,max_iter=5000), sc.transform(Xtr),ytr, tests)
res["RF lexical"]=run(RandomForestClassifier(n_estimators=200,n_jobs=-1,random_state=42), sc.transform(Xtr),ytr, tests)  # fixed: train/test both scaled

# ---- NLP char n-gram: fit on PhiUSIIL train urls only ----
u1tr,u1te,_,_ = train_test_split(u1,y1,test_size=0.2,random_state=42,stratify=y1)
tf=TfidfVectorizer(analyzer="char_wb",ngram_range=(3,5),max_features=20000)
Ztr=tf.fit_transform(u1tr); Zte=tf.transform(u1te); Z2=tf.transform(u2)
res["SVM NLP(char)"]=run(LinearSVC(C=1.0,random_state=42,max_iter=5000), Ztr,ytr,
        {"D1 in-dist (PhiUSIIL hold)":(Zte,yte),"D2 CROSS (PhishDataset)":(Z2,y2)})

# ---- reverse: train D2 -> test D1 (asymmetry) ----
X2tr,X2te,y2tr,y2te=train_test_split(X2,y2,test_size=0.2,random_state=42,stratify=y2)
sc2=StandardScaler().fit(X2tr)
res["SVM lexical (REVERSE D2->D1)"]=run(LinearSVC(C=1.0,random_state=42,max_iter=5000),
        sc2.transform(X2tr),y2tr,
        {"D2 in-dist (hold)":(sc2.transform(X2te),y2te),
         "D1 CROSS (PhiUSIIL)":(sc2.transform(X1),y1)})

for k,v in res.items():
    print("\n###",k)
    for nm,m in v.items(): print(f"  {nm:32s} acc={m['acc']:.4f} f1={m['f1']:.4f} auc={m['auc']:.4f} rec={m['rec']:.4f}")
json.dump(res, open(os.path.join(BASE_DIR, "crossdataset_results.json"),"w"), indent=1)
