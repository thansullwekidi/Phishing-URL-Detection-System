# 🚀 Quick Start - Phishing URL Detector

## ⚡ 30-Second Setup

### 1. **Install & Run**
```bash
pip install -r requirements.txt
cd 05_Source_Code
streamlit run app.py
```

**Opens automatically at:** http://localhost:8501

---

## 📋 What You Get

### ✅ **Web Application** (Streamlit)
- **🏠 Home**: Overview & key statistics
- **🔬 Experiment Results**: All model performance metrics
- **📊 Cross-Dataset Analysis**: Generalization audit findings
- **🧪 Test Detector**: Real-time URL classification
- **📈 Visualizations**: 4 publication-ready figures

### ✅ **REST API** (Flask) - Optional
```bash
python api_server.py
```
Runs on `http://localhost:5000`

---

## 🔍 Testing the Detector

### Via Web App
1. Go to **🧪 Test Detector** tab
2. Enter any URL
3. Click **🔍 Analyze**
4. See prediction + feature breakdown

### Via API
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

**Response:**
```json
{
  "url": "https://example.com",
  "prediction": "legitimate",
  "confidence": 2.45,
  "model": "SVM"
}
```

---

## 🐳 Docker Deployment

### Build & Run
```bash
docker build -t phishing-detector:latest .
docker run -p 8501:8501 phishing-detector:latest
```

---

## ☁️ Cloud Deployment

### Streamlit Cloud (Easiest)
1. Push to GitHub
2. Sign up at https://streamlit.io/cloud
3. Connect repository → Select `05_Source_Code/app.py`
4. **Done!** Your app is live

### Heroku
```bash
heroku create <app-name>
git push heroku main
```

### AWS/Azure/GCP
Use Docker image + container services

---

## 📊 Key Findings Summary

| Metric | In-Distribution | Cross-Dataset | Gap |
|--------|-----------------|----------------|-----|
| **SVM Lexical** | 99.30% | **49.60%** | 49.7% ↓ |
| **Random Forest** | 99.65% | **49.75%** | 49.9% ↓ |
| **SVM NLP-Char** | 99.79% | **61.33%** | 38.5% ↓ |

**🎯 Insight**: Character n-gram NLP is **12% better** on unseen datasets!

---

## 📁 Project Structure

```
📂 Project_Root/
├── 05_Source_Code/
│   ├── app.py                    ← Streamlit app (RUN THIS)
│   ├── api_server.py             ← Flask API (optional)
│   ├── experiment.py             ← Ablation study
│   ├── crossdataset.py           ← Cross-dataset test
│   ├── make_figures.py           ← Generate visualizations
│   ├── experiment_results.json
│   ├── crossdataset_results.json
│   ├── fig*.png                  (4 visualizations)
│   └── *.py                      (all scripts)
├── 04_Dataset/
│   └── Raw_Dataset/
│       ├── PhiUSIIL_Dataset.csv  (235,795 URLs)
│       └── PhishDataset_20000.xlsx (20,000 URLs)
├── requirements.txt              ← Dependencies
├── Dockerfile                    ← Docker config
├── DEPLOYMENT.md                 ← Full deployment guide
└── README.md
```

---

## 🔧 Troubleshooting

### **Port Already in Use**
```bash
streamlit run app.py --server.port 8502
```

### **ModuleNotFoundError**
```bash
pip install --upgrade -r requirements.txt
```

### **Slow First Load**
- First run caches model (takes ~2 min)
- Subsequent loads are instant

### **Missing Datasets**
- Ensure `04_Dataset/Raw_Dataset/` has both CSV files
- Re-run `experiment.py` and `crossdataset.py` if needed

---

## 📞 Support

### Environment Info
```bash
python -c "import sys; print(sys.version)"
python -m pip list
```

### Logs
Streamlit: `~/.streamlit/logs/`
Flask: Check terminal output

### Documentation
- Full guide: See `DEPLOYMENT.md`
- Research paper: See `09_Draft_IEEE/`

---

## 🎉 You're Ready!

Your phishing detector is now:
- ✅ Running locally
- ✅ Ready to test URLs
- ✅ Ready to deploy to cloud
- ✅ API-accessible for integrations

**Happy testing!** 🔍
