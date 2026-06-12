# 🚀 Deployment Guide

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Experiments (if needed)
```bash
cd 05_Source_Code
python experiment.py        # Generate experiment_results.json
python crossdataset.py      # Generate crossdataset_results.json  
python make_figures.py      # Generate fig1-4 visualizations
```

### 3. Run Web Application
```bash
cd 05_Source_Code
streamlit run app.py
```

The app will open at: `http://localhost:8501`

---

## Docker Deployment

### Build Image
```bash
docker build -t phishing-detector:latest .
```

### Run Container
```bash
docker run -p 8501:8501 phishing-detector:latest
```

Access at: `http://localhost:8501`

---

## Cloud Deployment Options

### Option 1: Streamlit Cloud (Recommended)
1. Push code to GitHub
2. Go to https://streamlit.io/cloud
3. Connect your GitHub repo
4. Select `05_Source_Code/app.py` as main file
5. Deploy!

**Free tier:** 1 app, unlimited viewers

### Option 2: Heroku
1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: streamlit run 05_Source_Code/app.py --server.port=$PORT
   ```
3. Deploy:
   ```bash
   heroku create <app-name>
   git push heroku main
   ```

### Option 3: AWS/Azure/GCP
- Use Docker image with services like:
  - AWS ECS
  - Azure Container Instances
  - Google Cloud Run

---

## Environment Variables

For production, set in deployment platform:

```bash
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_LOGGER_LEVEL=info
```

---

## Performance Tips

1. **Cache Models**: Already implemented with `@st.cache_resource`
2. **Reduce Data Loading**: Datasets cached after first load
3. **CDN for Images**: Upload fig*.png to CDN for faster serving
4. **Database**: Consider SQLite for storing predictions

---

## Troubleshooting

### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

### Memory Issues with Large Datasets
```python
# Load data in chunks if needed
df = pd.read_csv("file.csv", chunksize=10000)
```

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

---

## API Alternative (Flask)

Want a REST API instead? See `api_server.py` for Flask implementation.

---

## Monitoring & Logging

For production deployment:
- Enable Streamlit analytics
- Setup error tracking (Sentry)
- Monitor resource usage
- Setup automated backups

