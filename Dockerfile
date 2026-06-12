FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY 05_Source_Code/app.py .
COPY 05_Source_Code/experiment.py .
COPY 05_Source_Code/crossdataset.py .
COPY 05_Source_Code/make_figures.py .
COPY 05_Source_Code/*.json ./
COPY 05_Source_Code/*.png ./
COPY 04_Dataset ./04_Dataset

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
