"""
Flask REST API Server - Phishing URL Detection API
Alternative to Streamlit for programmatic access
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import re
import os
from urllib.parse import urlparse
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
import pandas as pd
from functools import lru_cache
import warnings
warnings.filterwarnings("ignore")

# Helper to resolve files regardless of where API is run from
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
    # Fallback to checking from root if in Docker (so ../04_Dataset could be at ./04_Dataset relative to api_server.py's dir)
    if relative_path.startswith("../"):
        stripped = relative_path.lstrip("./").replace("../", "")
        path_docker = os.path.abspath(os.path.join(BASE_DIR, stripped))
        if os.path.exists(path_docker):
            return path_docker
        path_root = os.path.abspath(os.path.join(os.getcwd(), stripped))
        if os.path.exists(path_root):
            return path_root
    return path_from_base

app = Flask(__name__)
CORS(app)

# Feature extraction
IP_RE = re.compile(r"(\d{1,3}\.){3}\d{1,3}")

def extract_features(url):
    """Extract 22 lexical features from URL"""
    u = str(url)
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

FNAMES = ["url_len","host_len","path_len","n_dot","n_hyphen","n_us","n_slash","n_q","n_eq",
          "n_at","n_amp","n_pct","n_dig","dig_ratio","n_spec","spec_ratio","has_ip","is_https",
          "n_subdom","has_at","tld_len","longest_token"]

@lru_cache(maxsize=1)
def get_model():
    """Load and train model (cached)"""
    df = pd.read_csv(resolve_path("../04_Dataset/Raw_Dataset/PhiUSIIL_Dataset.csv"))
    u = np.array(df["URL"].astype(str).values)
    y = np.array((df["label"].values==0).astype(int))
    
    X = np.array([extract_features(url) for url in u])
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    sc = StandardScaler().fit(Xtr)
    svm = LinearSVC(C=1.0, random_state=42, max_iter=5000)
    svm.fit(sc.transform(Xtr), ytr)
    
    return svm, sc

# ===== API ENDPOINTS =====

@app.route("/", methods=["GET"])
def home():
    """API Documentation"""
    return jsonify({
        "name": "Phishing URL Detector API",
        "version": "1.0",
        "endpoints": {
            "POST /predict": "Predict if URL is phishing",
            "POST /batch": "Batch predict multiple URLs",
            "GET /status": "API health status",
            "GET /features": "Get list of features"
        }
    })

@app.route("/status", methods=["GET"])
def status():
    """Health check"""
    return jsonify({
        "status": "ok",
        "service": "Phishing URL Detector",
        "model": "SVM with 22 lexical features"
    })

@app.route("/features", methods=["GET"])
def get_features():
    """Get feature names"""
    return jsonify({
        "features": FNAMES,
        "count": len(FNAMES),
        "type": "lexical"
    })

@app.route("/predict", methods=["POST"])
def predict():
    """
    Predict single URL
    Request: {"url": "https://example.com"}
    Response: {"url": "...", "prediction": "legitimate", "confidence": 0.95, "features": {...}}
    """
    try:
        data = request.get_json()
        if not data or "url" not in data:
            return jsonify({"error": "Missing 'url' field"}), 400
        
        url = data["url"]
        features = extract_features(url)
        
        svm, scaler = get_model()
        X_test = scaler.transform([features])
        prediction = svm.predict(X_test)[0]
        score = svm.decision_function(X_test)[0]
        
        return jsonify({
            "url": url,
            "prediction": "legitimate" if prediction == 1 else "phishing",
            "confidence": float(abs(score)),
            "raw_score": float(score),
            "features": {fname: fval for fname, fval in zip(FNAMES, features)},
            "model": "SVM"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/batch", methods=["POST"])
def batch_predict():
    """
    Predict multiple URLs
    Request: {"urls": ["url1", "url2", ...]}
    Response: [{"url": "...", "prediction": "...", "confidence": ...}, ...]
    """
    try:
        data = request.get_json()
        if not data or "urls" not in data:
            return jsonify({"error": "Missing 'urls' array"}), 400
        
        urls = data["urls"]
        if not isinstance(urls, list):
            return jsonify({"error": "'urls' must be an array"}), 400
        
        svm, scaler = get_model()
        results = []
        
        for url in urls:
            try:
                features = extract_features(url)
                X_test = scaler.transform([features])
                prediction = svm.predict(X_test)[0]
                score = svm.decision_function(X_test)[0]
                
                results.append({
                    "url": url,
                    "prediction": "legitimate" if prediction == 1 else "phishing",
                    "confidence": float(abs(score)),
                    "raw_score": float(score)
                })
            except Exception as e:
                results.append({
                    "url": url,
                    "error": str(e)
                })
        
        return jsonify({
            "count": len(results),
            "results": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Detailed analysis with cross-dataset performance
    Returns performance metrics and model confidence
    """
    try:
        data = request.get_json()
        if not data or "url" not in data:
            return jsonify({"error": "Missing 'url' field"}), 400
        
        url = data["url"]
        features = extract_features(url)
        
        svm, scaler = get_model()
        X_test = scaler.transform([features])
        prediction = svm.predict(X_test)[0]
        score = svm.decision_function(X_test)[0]
        
        return jsonify({
            "url": url,
            "prediction": "legitimate" if prediction == 1 else "phishing",
            "confidence": float(abs(score)),
            "analysis": {
                "model": "LinearSVC (Lexical Features)",
                "in_distribution_accuracy": 0.9930,
                "cross_dataset_accuracy": 0.4960,
                "features_count": 22,
                "training_samples": "188,636"
            },
            "warning": "This model achieves 99.3% accuracy on PhiUSIIL but only 49.6% on PhishDataset (independent dataset). Use with caution for production.",
            "features": {fname: fval for fname, fval in zip(FNAMES, features)}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
