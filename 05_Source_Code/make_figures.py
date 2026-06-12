"""Generate publication figures for the phishing cross-dataset study."""
import re, numpy as np, pandas as pd, warnings, os; warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from urllib.parse import urlparse
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, roc_curve, auc, accuracy_score

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

plt.rcParams.update({"font.size":10,"figure.dpi":150,"savefig.dpi":300,"savefig.bbox":"tight"})
OUT=BASE_DIR + "/"
IP=re.compile(r"(\d{1,3}\.){3}\d{1,3}")
def feats(u):
    u=str(u); p=urlparse(u if "//" in u else "http://"+u); host,path=p.netloc,p.path
    dg=sum(c.isdigit() for c in u); sp=sum(not c.isalnum() for c in u)
    return [len(u),len(host),len(path),u.count("."),u.count("-"),u.count("_"),u.count("/"),
        u.count("?"),u.count("="),u.count("@"),u.count("&"),u.count("%"),dg,dg/max(len(u),1),
        sp,sp/max(len(u),1),1 if IP.search(host) else 0,1 if p.scheme=="https" else 0,
        max(host.count(".")-1,0),1 if "@" in u else 0,len(host.split(".")[-1]) if "." in host else 0,
        max((len(t) for t in re.split(r"[\W_]+",u)),default=0)]

d1=pd.read_csv(resolve_path("../04_Dataset/Raw_Dataset/PhiUSIIL_Dataset.csv")); y1=(d1["label"].values==0).astype(int); u1=np.array(d1["URL"].astype(str).values)
d2=pd.read_excel(resolve_path("../04_Dataset/Raw_Dataset/PhishDataset_20000.xlsx")); y2=np.array(d2["Labels"].values.astype(int)); u2=np.array(d2["URLs"].astype(str).values)
X1=np.array([feats(u) for u in u1]); X2=np.array([feats(u) for u in u2])
Xtr,Xte,ytr,yte,utr,ute=train_test_split(X1,y1,u1,test_size=0.2,random_state=42,stratify=y1)
sc=StandardScaler().fit(Xtr)
svm=LinearSVC(C=1.0,random_state=42,max_iter=5000).fit(sc.transform(Xtr),ytr)
rf =RandomForestClassifier(n_estimators=200,n_jobs=-1,random_state=42).fit(sc.transform(Xtr),ytr)
tf=TfidfVectorizer(analyzer="char_wb",ngram_range=(3,5),max_features=20000)
Ztr=tf.fit_transform(utr); svm_nlp=LinearSVC(C=1.0,random_state=42,max_iter=5000).fit(Ztr,ytr)

def acc(m,X,y): return accuracy_score(y,m.predict(X))
in_acc=[acc(svm,sc.transform(Xte),yte),acc(rf,sc.transform(Xte),yte),acc(svm_nlp,tf.transform(ute),yte)]
cr_acc=[acc(svm,sc.transform(X2),y2),acc(rf,sc.transform(X2),y2),acc(svm_nlp,tf.transform(u2),y2)]
labels=["SVM\n(lexical)","RF\n(lexical)","SVM\n(NLP char)"]

# Fig 1: generalization gap
fig,ax=plt.subplots(figsize=(6,4)); x=np.arange(3); w=0.38
ax.bar(x-w/2,in_acc,w,label="In-distribution (PhiUSIIL hold-out)",color="#2c7fb8")
ax.bar(x+w/2,cr_acc,w,label="Cross-dataset (PhishDataset)",color="#d95f0e")
ax.axhline(0.5,ls="--",c="gray",lw=1); ax.text(2.3,0.515,"chance",color="gray",fontsize=8)
for i,(a,b) in enumerate(zip(in_acc,cr_acc)):
    ax.text(i-w/2,a+.01,f"{a:.3f}",ha="center",fontsize=8); ax.text(i+w/2,b+.01,f"{b:.3f}",ha="center",fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylim(0,1.08); ax.set_ylabel("Accuracy")
ax.set_title("Generalization gap: ~99% in-distribution collapses to chance cross-dataset")
ax.legend(fontsize=8,loc="lower left"); plt.savefig(OUT+"fig1_generalization_gap.png"); plt.close()

# Fig 2: confusion matrices SVM lexical
fig,axes=plt.subplots(1,2,figsize=(8,3.4))
for ax,(Xx,yy,ti) in zip(axes,[(sc.transform(Xte),yte,"In-distribution (PhiUSIIL)"),(sc.transform(X2),y2,"Cross-dataset (PhishDataset)")]):
    cm=confusion_matrix(yy,svm.predict(Xx)); 
    im=ax.imshow(cm,cmap="Blues")
    for (i,j),v in np.ndenumerate(cm): ax.text(j,i,f"{v}",ha="center",va="center",fontsize=9,color="black")
    ax.set_xticks([0,1]); ax.set_xticklabels(["legit","phish"]); ax.set_yticks([0,1]); ax.set_yticklabels(["legit","phish"])
    ax.set_xlabel("Predicted"); ax.set_ylabel("True"); ax.set_title(ti,fontsize=10)
fig.suptitle("SVM (lexical): clean in-distribution vs collapsed cross-dataset",fontsize=10)
plt.savefig(OUT+"fig2_confusion_matrices.png"); plt.close()

# Fig 3: ROC
fig,ax=plt.subplots(figsize=(5.2,4.6))
def roc(m,X,y,lab,**k):
    s=m.decision_function(X); fpr,tpr,_=roc_curve(y,s); ax.plot(fpr,tpr,label=f"{lab} (AUC={auc(fpr,tpr):.3f})",**k)
roc(svm,sc.transform(Xte),yte,"SVM lexical | in-dist",color="#2c7fb8")
roc(svm,sc.transform(X2),y2,"SVM lexical | cross",color="#d95f0e")
roc(svm_nlp,tf.transform(u2),y2,"SVM NLP-char | cross",color="#31a354")
ax.plot([0,1],[0,1],"--",c="gray",lw=1)
ax.set_xlabel("False Positive Rate"); ax.set_ylabel("True Positive Rate"); ax.set_title("ROC: lexical fails cross-dataset, char n-gram retains ranking")
ax.legend(fontsize=8,loc="lower right"); plt.savefig(OUT+"fig3_roc_curves.png"); plt.close()

# Fig 4: asymmetry
X2tr,X2te,y2tr,y2te=train_test_split(X2,y2,test_size=0.2,random_state=42,stratify=y2)
sc2=StandardScaler().fit(X2tr); svm2=LinearSVC(C=1.0,random_state=42,max_iter=5000).fit(sc2.transform(X2tr),y2tr)
fig,ax=plt.subplots(figsize=(5.6,4))
pairs=["Train PhiUSIIL\n→ Test PhishDataset","Train PhishDataset\n→ Test PhiUSIIL"]
vals=[acc(svm,sc.transform(X2),y2),acc(svm2,sc2.transform(X1),y1)]
bars=ax.bar(pairs,vals,color=["#d95f0e","#2c7fb8"],width=0.55)
ax.axhline(0.5,ls="--",c="gray",lw=1)
for b,v in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,v+.01,f"{v:.3f}",ha="center")
ax.set_ylim(0,1.05); ax.set_ylabel("Cross-dataset accuracy")
ax.set_title("Asymmetry: easy benchmark teaches non-transferable shortcuts")
plt.savefig(OUT+"fig4_asymmetry.png"); plt.close()
print("figures saved:", in_acc, cr_acc)
