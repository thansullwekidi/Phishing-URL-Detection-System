"""
Streamlit Web App - Phishing URL Detection (SIMPLE VERSION)
RUN WITH: streamlit run app_simple.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
import re
from urllib.parse import urlparse
import warnings
warnings.filterwarnings("ignore")

# ===== CONFIG =====
st.set_page_config(page_title="Phishing Detector", page_icon="🔍", layout="wide")
st.title("🔍 Phishing URL Detector")
st.markdown("Cross-Dataset Audit - Research Application")

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("## 📋 Menu")
    page = st.radio("Select", [
        "📊 Results",
        "🧪 Test URL",
        "📈 Charts"
    ])

# ===== PAGE 1: RESULTS =====
if page == "📊 Results":
    st.markdown("## Experiment Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 In-Distribution (PhiUSIIL)")
        data = {
            "Model": ["SVM Lexical", "Random Forest", "SVM NLP-Char"],
            "Accuracy": ["99.99%", "100.00%", "99.78%"],
            "AUC": ["1.0000", "1.0000", "0.9989"]
        }
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    
    with col2:
        st.markdown("### ⚠️ Cross-Dataset (PhishDataset)")
        data = {
            "Model": ["SVM Lexical", "Random Forest", "SVM NLP-Char"],
            "Accuracy": ["49.60% ❌", "49.75% ❌", "61.33% ✅"],
            "AUC": ["0.7847", "0.4960", "0.9401"]
        }
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    
    st.markdown("---")
    st.markdown("### Key Finding")
    st.error("""
    **Models achieving 99%+ accuracy on PhiUSIIL collapse to ~50% on independent datasets!**
    
    Only character n-gram NLP shows better transfer (61.33% AUC 0.94)
    """)

# ===== PAGE 2: TEST URL =====
elif page == "🧪 Test URL":
    st.markdown("## Test Phishing Detection")
    
    # Feature extractor
    IP_RE = re.compile(r"(\d{1,3}\.){3}\d{1,3}")
    
    def extract_features(url):
        u = str(url)
        p = urlparse(u if "//" in u else "http://"+u)
        host, path = p.netloc, p.path
        digits = sum(c.isdigit() for c in u)
        special = sum(not c.isalnum() for c in u)
        
        features = {
            "URL Length": len(u),
            "Host Length": len(host),
            "Path Length": len(path),
            "Dot Count": u.count("."),
            "Hyphen Count": u.count("-"),
            "Underscore Count": u.count("_"),
            "Slash Count": u.count("/"),
            "Question Mark": u.count("?"),
            "Equals Count": u.count("="),
            "At Symbol": u.count("@"),
            "Ampersand": u.count("&"),
            "Percent": u.count("%"),
            "Digit Count": digits,
            "Digit Ratio": round(digits/max(len(u),1), 3),
            "Special Char Count": special,
            "Special Char Ratio": round(special/max(len(u),1), 3),
            "Has IP": "Yes" if IP_RE.search(host) else "No",
            "Is HTTPS": "Yes" if p.scheme=="https" else "No",
            "Subdomains": max(host.count(".")-1, 0),
            "Has @ Symbol": "Yes" if "@" in u else "No",
            "TLD Length": len(host.split(".")[-1]) if "." in host else 0,
        }
        return features
    
    st.markdown("### Enter URL to Analyze")
    url_input = st.text_input("URL:", value="https://example.com")
    
    if st.button("🔍 Analyze URL", use_container_width=True):
        features = extract_features(url_input)
        
        st.markdown("### 📋 URL Features Extracted")
        feat_df = pd.DataFrame(list(features.items()), columns=["Feature", "Value"])
        st.dataframe(feat_df, use_container_width=True)
        
        # Simple heuristics
        score = 0
        reasons = []
        
        # Check various indicators
        if "@" in url_input:
            score += 3
            reasons.append("⚠️ Contains @ symbol (often in phishing URLs)")
        
        if "http://" in url_input and not url_input.startswith("http://localhost"):
            score += 1
            reasons.append("⚠️ Uses HTTP instead of HTTPS")
        
        if url_input.count(".") > 5:
            score += 2
            reasons.append("⚠️ Many dots (suspicious)")
        
        if any(x in url_input.lower() for x in ["bit.ly", "short.link", "tinyurl"]):
            score += 2
            reasons.append("⚠️ Uses URL shortener")
        
        if len(url_input) > 100:
            score += 1
            reasons.append("⚠️ Very long URL")
        
        st.markdown("---")
        st.markdown("### 🎯 Analysis Result")
        
        col1, col2 = st.columns(2)
        with col1:
            if score >= 5:
                st.error(f"⚠️ POTENTIALLY PHISHING\nRisk Score: {score}/10")
            elif score >= 2:
                st.warning(f"⚠️ SUSPICIOUS\nRisk Score: {score}/10")
            else:
                st.success(f"✅ LIKELY LEGITIMATE\nRisk Score: {score}/10")
        
        with col2:
            if reasons:
                st.markdown("**Risk Factors:**")
                for reason in reasons:
                    st.markdown(f"• {reason}")
            else:
                st.markdown("**No red flags detected** ✅")

# ===== PAGE 3: CHARTS =====
elif page == "📈 Charts":
    st.markdown("## Experiment Visualizations")
    
    # Create simple visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### In-Distribution vs Cross-Dataset")
        data = {
            "Model": ["SVM\nLexical", "RF\nLexical", "SVM\nNLP"],
            "In-Dist": [99.99, 100.0, 99.78],
            "Cross-Dataset": [49.60, 49.75, 61.33]
        }
        df = pd.DataFrame(data)
        st.bar_chart(df.set_index("Model"))
    
    with col2:
        st.markdown("### Asymmetry Test")
        data = {
            "Direction": ["D1→D2\n(Phishing)", "D2→D1\n(Legitimate)"],
            "Accuracy": [49.6, 90.14]
        }
        df = pd.DataFrame(data)
        st.bar_chart(df.set_index("Direction"))
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ROC AUC Comparison")
        data = {
            "Model": ["SVM Lex", "RF Lex", "SVM NLP"],
            "In-Dist": [0.9968, 0.9978, 0.9991],
            "Cross": [0.7847, 0.4960, 0.9401]
        }
        df = pd.DataFrame(data)
        st.line_chart(df.set_index("Model"))
    
    with col2:
        st.markdown("### 5-Fold CV (F1 Score)")
        data = {
            "Feature Set": ["FULL\n(50 feat)", "URL-only\n(22 feat)"],
            "F1 Mean": [0.9999, 0.9972],
            "F1 Std": [0.0000, 0.0001]
        }
        df = pd.DataFrame(data)
        st.bar_chart(df.set_index("Feature Set"))

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    📚 UAS Kecerdasan Buatan - Phishing URL Detection  
    Reference: Aritonang et al. (2026), JUTIF 7(1)
</div>
""", unsafe_allow_html=True)
