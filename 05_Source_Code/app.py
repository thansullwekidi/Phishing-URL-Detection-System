"""
Streamlit Web App - Phishing URL Detection Deployment
Cross-Dataset Audit of NLP and SVM Phishing-URL Detection

RUN WITH: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
import time
import re
import os
from urllib.parse import urlparse
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from PIL import Image
import warnings
warnings.filterwarnings("ignore")

# Helper to resolve files regardless of where Streamlit is run from
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
    # Fallback to checking inside 05_Source_Code if run from root directory
    if not relative_path.startswith("05_Source_Code") and not relative_path.startswith("../"):
        path_in_source = os.path.abspath(os.path.join(os.getcwd(), "05_Source_Code", relative_path))
        if os.path.exists(path_in_source):
            return path_in_source
    # Fallback to checking from root if in Docker (so ../04_Dataset could be at ./04_Dataset relative to app.py's dir)
    if relative_path.startswith("../"):
        stripped = relative_path.lstrip("./").replace("../", "")
        path_docker = os.path.abspath(os.path.join(BASE_DIR, stripped))
        if os.path.exists(path_docker):
            return path_docker
        path_root = os.path.abspath(os.path.join(os.getcwd(), stripped))
        if os.path.exists(path_root):
            return path_root
    return path_from_base


# Page config
st.set_page_config(page_title="Phishing URL Detector", page_icon="🔍", layout="wide")

# Custom CSS for Premium UI
st.markdown("""
<style>
    /* Import Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* Global styles */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* Gradient Header Title */
    .title-container {
        padding: 1.5rem 0 2rem 0;
    }
    
    .title-gradient {
        background: linear-gradient(135deg, #a855f7 0%, #3b82f6 50%, #14b8a6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        letter-spacing: -1px;
    }
    
    .subtitle-accent {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 400;
    }

    /* Premium Container Cards */
    .premium-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(12px);
    }
    
    .premium-card:hover {
        transform: translateY(-4px);
        border-color: rgba(139, 92, 246, 0.3);
        box-shadow: 0 15px 35px rgba(139, 92, 246, 0.15);
    }

    /* Metric Layout inside Cards */
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 8px 0;
    }
    
    .metric-value-red {
        background: linear-gradient(90deg, #ef4444, #f97316);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .metric-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    
    .metric-desc {
        font-size: 0.85rem;
        color: #64748b;
    }

    /* Custom Badges */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-right: 8px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-blue { background: rgba(59, 130, 246, 0.15); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.2); }
    .badge-purple { background: rgba(139, 92, 246, 0.15); color: #8b5cf6; border: 1px solid rgba(139, 92, 246, 0.2); }
    .badge-pink { background: rgba(236, 72, 153, 0.15); color: #ec4899; border: 1px solid rgba(236, 72, 153, 0.2); }
    .badge-green { background: rgba(20, 184, 166, 0.15); color: #14b8a6; border: 1px solid rgba(20, 184, 166, 0.2); }

    /* Custom styled buttons */
    .stButton>button {
        background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.2) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4) !important;
        border: none !important;
    }
    
    /* Input element styling */
    .stTextInput input {
        background-color: #1e293b !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        padding: 10px 16px !important;
    }
    
    .stTextInput input:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
    }

    /* Sidebar clean styling */
    [data-testid="stSidebar"] {
        background-color: #0b1329 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
</style>
""", unsafe_allow_html=True)

# Title Header Section
st.markdown("""
<div class="title-container">
    <div class="title-gradient">🔍 Phishing URL Detection System</div>
    <div class="subtitle-accent">Cross-Dataset Audit of NLP and SVM Phishing-URL Detection</div>
    <div style="font-size: 0.85rem; color: #64748b; margin-top: 5px;">Riset Akademis: Aritonang et al. (2026) + Analisis Kebocoran Lintas-Dataset</div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='margin-top: 10px; font-size: 1.5rem;'>🧭 Navigasi</h2>", unsafe_allow_html=True)
    page = st.radio("Pilih Halaman:", [
        "🏠 Dashboard Home",
        "🔬 Hasil Eksperimen 1",
        "📊 Analisis Lintas-Dataset",
        "🧪 Uji Detektor URL",
        "📈 Visualisasi Grafik"
    ])

# ===== PAGE 1: HOME =====
if page == "🏠 Dashboard Home":
    
    st.markdown("""
    <div style="padding: 10px 0;">
        <h2 style="color: #a855f7; margin: 0; font-family: 'Outfit';">Selamat Datang di Portal Audit Phishing</h2>
        <p style="color: #94a3b8; font-size: 1.1rem; margin: 5px 0 0 0;">Platform investigasi ilmiah celah generalisasi deteksi URL Phishing berbasis SVM dan NLP.</p>
    </div>
    <div style='height: 15px;'></div>
    """, unsafe_allow_html=True)
    
    # 4 Quick Stats Metrics
    st.markdown("### 📊 Ringkasan Statistik Penelitian")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown("""
        <div class="premium-card" style="text-align: center;">
            <div class="metric-label">Dataset PhiUSIIL</div>
            <div class="metric-value">235,795</div>
            <div class="metric-desc">URLs (Benchmark D1)</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class="premium-card" style="text-align: center;">
            <div class="metric-label">PhishDataset</div>
            <div class="metric-value">20,000</div>
            <div class="metric-desc">URLs (Independen D2)</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown("""
        <div class="premium-card" style="text-align: center;">
            <div class="metric-label">Akurasi In-Dist</div>
            <div class="metric-value">99.99%</div>
            <div class="metric-desc">SVM + Fitur Lengkap</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown("""
        <div class="premium-card" style="text-align: center;">
            <div class="metric-label">Penurunan Akurasi</div>
            <div class="metric-value metric-value-red">50.4% ↓</div>
            <div class="metric-desc">Collapse ke Tebakan Acak</div>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="premium-card" style="height: 100%;">
            <h3 style="color: #3b82f6;">📖 Tentang Aplikasi & Riset</h3>
            <p>Sistem ini dirancang untuk mendemonstrasikan fenomena ilmiah <b>generalization gap</b> dalam teknologi deteksi URL phishing:</p>
            <ul>
                <li>Model pembelajaran mesin yang mencapai performa sempurna <b>(99.99% akurasi)</b> pada benchmark PhiUSIIL mengalami penurunan tajam.</li>
                <li>Saat diuji menggunakan dataset independen (PhishDataset), akurasi model <b>kolaps ke ~50%</b> (tidak lebih baik dari tebakan acak).</li>
                <li>Pendekatan berbasis <b>Character n-gram NLP</b> terbukti lebih kokoh dan mampu mentransfer informasi pola teks dengan lebih baik <b>(akurasi 61.33%)</b>.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="premium-card" style="height: 100%;">
            <h3 style="color: #8b5cf6;">⚠️ Research Gap & Solusi</h3>
            <div style="margin-bottom: 12px;">
                <span class="badge badge-blue">G1</span> <b>Benchmark Saturation:</b> Performa tinggi pada dataset dipicu oleh properti intrinsik data, bukan keunggulan model.
            </div>
            <div style="margin-bottom: 12px;">
                <span class="badge badge-purple">G2</span> <b>NLP Contribution:</b> Kontribusi NLP terdistorsi karena sebagian besar fitur berfokus pada konten setelah URL diakses.
            </div>
            <div style="margin-bottom: 12px;">
                <span class="badge badge-pink">G3</span> <b>Cross-Dataset Audit:</b> Literatur sebelumnya mengabaikan uji coba model pada dataset luar.
            </div>
            <hr style="opacity: 0.1; margin: 15px 0;">
            <div style="margin-bottom: 5px;">
                <span class="badge badge-green">Solusi Novel</span> <b>Ablasi Fitur Lintas-Dataset:</b> Kami mengisolasi fitur berbasis leksikal URL untuk mengevaluasi ketahanan model sebenarnya.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ===== PAGE 2: EXPERIMENT RESULTS =====
elif page == "🔬 Hasil Eksperimen 1":
    st.markdown("## Eksperimen 1: Ablasi Fitur & Saturasi Benchmark")
    
    st.markdown("""
    <div class="premium-card">
        <h4>🔬 Deskripsi Eksperimen 1</h4>
        <p>Eksperimen ini membuktikan bahwa akurasi tinggi (>99%) pada dataset in-distribution disebabkan oleh saturasi fitur (seperti fitur URLSimilarityIndex). Pemisahan / ablasi kelompok fitur dilakukan untuk melihat ketergantungan model terhadap masing-masing jenis fitur.</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        with open(resolve_path("experiment_results.json")) as f:
            exp_data = json.load(f)
        
        results_df = pd.DataFrame(exp_data["results"])
        st.markdown("### 📊 Kinerja Model (Uji Internal / In-Distribution)")
        st.dataframe(results_df[["setup", "model", "acc", "prec", "rec", "f1", "auc"]], use_container_width=True)
        
        st.markdown("### 🔄 5-Fold Cross-Validation (F1 Score)")
        cv_data = exp_data["cv"]
        cv_df = pd.DataFrame([
            {"Kelompok Fitur": "Fitur LENGKAP (50)", "F1 Mean": cv_data["FULL"]["f1_mean"], "F1 Std": cv_data["FULL"]["f1_std"]},
            {"Kelompok Fitur": "Hanya URL", "F1 Mean": cv_data["URL-only"]["f1_mean"], "F1 Std": cv_data["URL-only"]["f1_std"]}
        ])
        st.dataframe(cv_df, use_container_width=True)
        
        st.success("✅ Terkonfirmasi: Semua model mencapai akurasi 99%+ secara in-distribution. Ini membuktikan saturasi benchmark data.")
    except FileNotFoundError:
        st.error("⚠️ File experiment_results.json tidak ditemukan. Jalankan file experiment.py terlebih dahulu.")

# ===== PAGE 3: CROSS-DATASET ANALYSIS =====
elif page == "📊 Analisis Lintas-Dataset":
    st.markdown("## Eksperimen 2: Evaluasi Lintas-Dataset (Generalisasi)")
    
    st.markdown("""
    <div class="premium-card">
        <h4>🧬 Analisis Celah Generalisasi</h4>
        <p>Evaluasi sesungguhnya dari model deteksi phishing diukur dari kemampuannya mendeteksi URL baru dari dataset yang sama sekali belum pernah dipelajari (PhishDataset). Di bawah ini adalah hasil pengujian performa transferibilitas model.</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        with open(resolve_path("crossdataset_results.json")) as f:
            cross_data = json.load(f)
        
        for model_name, results in cross_data.items():
            st.markdown(f"### 🤖 {model_name}")
            
            rows = []
            for test_name, metrics in results.items():
                row = {"Skenario Uji": test_name}
                row.update(metrics)
                rows.append(row)
            
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)
            
            # Highlight key findings
            if "D2 CROSS" in str(results):
                d2_acc = list(results.values())[1].get("acc", 0) if len(results) > 1 else 0
                if d2_acc < 0.6:
                    st.error(f"⚠️ GENERALIZATION FAILURE (Gagal Lintas-Dataset): Akurasi model anjlok menjadi {d2_acc*100:.2f}% pada PhishDataset.")
                else:
                    st.success(f"✅ BETTER TRANSFER (Hasil Lebih Baik): Model mempertahankan akurasi sebesar {d2_acc*100:.2f}%.")
        
        st.markdown("""
        <div class="premium-card" style="margin-top: 25px;">
            <h4 style="color: #14b8a6;">💡 Temuan Penting:</h4>
            <ul>
                <li><b>SVM Lexical & Random Forest:</b> Akurasi kolaps menjadi ~49% (sama seperti menebak acak koin).</li>
                <li><b>SVM NLP-Char:</b> Akurasi mencapai 61.33% dengan nilai ROC AUC 0.94, menunjukkan pola teks n-gram adalah fitur yang paling mampu digeneralisasi.</li>
                <li><b>Efek Asimetri:</b> Melatih model pada dataset yang lebih sulit (PhishDataset) dan mengujinya pada dataset yang lebih mudah (PhiUSIIL) menghasilkan akurasi 90.14%, membuktikan bias benchmark yang ekstrim.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("⚠️ File crossdataset_results.json tidak ditemukan. Jalankan file crossdataset.py terlebih dahulu.")

# ===== PAGE 4: TEST DETECTOR =====
elif page == "🧪 Uji Detektor URL":
    st.markdown("## Uji Coba Real-Time Detektor Phishing")
    
    # Feature extraction function
    IP_RE = re.compile(r"(\d{1,3}\.){3}\d{1,3}")
    def extract_features(url):
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
    
    FNAMES=["url_len","host_len","path_len","n_dot","n_hyphen","n_us","n_slash","n_q","n_eq",
            "n_at","n_amp","n_pct","n_dig","dig_ratio","n_spec","spec_ratio","has_ip","is_https",
            "n_subdom","has_at","tld_len","longest_token"]
    
    # Load and train model (cached)
    @st.cache_resource
    def train_detector():
        df = pd.read_csv(resolve_path("../04_Dataset/Raw_Dataset/PhiUSIIL_Dataset.csv"))
        u = np.array(df["URL"].astype(str).values)
        y = np.array((df["label"].values==0).astype(int))
        
        X = np.array([extract_features(url) for url in u])
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        sc = StandardScaler().fit(Xtr)
        svm = LinearSVC(C=1.0, random_state=42, max_iter=5000)
        svm.fit(sc.transform(Xtr), ytr)
        
        return svm, sc
    
    try:
        svm, scaler = train_detector()
        
        st.markdown("""
        <div class="premium-card">
            <h4>🧪 Uji URL Secara Interaktif</h4>
            <p>Masukkan alamat URL lengkap di bawah ini untuk dievaluasi oleh model SVM deteksi phishing berbasis 22 fitur leksikal.</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])
        with col1:
            test_url = st.text_input("Input Alamat URL:", "https://example-phishing-site.com")
        with col2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            analyze_clicked = st.button("🔍 Menganalisis URL")
            
        if analyze_clicked:
            features = extract_features(test_url)
            X_test = scaler.transform([features])
            prediction = svm.predict(X_test)[0]
            score = svm.decision_function(X_test)[0]
            
            st.markdown("### 🎯 Hasil Analisis URL")
            if prediction == 1:
                st.markdown(f"""
                <div class="premium-card" style="border-left: 5px solid #14b8a6; background: rgba(20, 184, 166, 0.05);">
                    <h3 style="color: #14b8a6; margin: 0 0 10px 0;">✅ URL TERDETEKSI AMAN (LEGITIMATE)</h3>
                    <p style="margin: 0;">Sistem mendeteksi URL <b>{test_url}</b> aman dari indikasi phishing.</p>
                    <div style="margin-top: 15px;">
                        <span class="metric-label">Confidence Score</span>
                        <div class="metric-value" style="background: linear-gradient(90deg, #14b8a6, #34d399); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.8rem;">{abs(score):.4f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="premium-card" style="border-left: 5px solid #ef4444; background: rgba(239, 68, 68, 0.05);">
                    <h3 style="color: #ef4444; margin: 0 0 10px 0;">⚠️ PERINGATAN: URL PHISHING TERDETEKSI</h3>
                    <p style="margin: 0;">Sistem mendeteksi adanya indikasi penipuan (phishing) pada URL <b>{test_url}</b>.</p>
                    <div style="margin-top: 15px;">
                        <span class="metric-label">Confidence Score</span>
                        <div class="metric-value-red" style="font-size: 1.8rem; font-weight: 800; background: linear-gradient(90deg, #ef4444, #f87171); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{abs(score):.4f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Feature breakdown
            with st.expander("📋 Rincian Nilai Fitur Leksikal URL"):
                feat_df = pd.DataFrame({
                    "Nama Fitur": FNAMES,
                    "Nilai Ekstraksi": features
                })
                st.dataframe(feat_df, use_container_width=True)
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Pastikan file dataset berada di folder: 04_Dataset/Raw_Dataset/")

# ===== PAGE 5: VISUALIZATIONS =====
elif page == "📈 Visualisasi Grafik":
    st.markdown("## Visualisasi Grafik Hasil Riset")
    
    st.markdown("""
    <div class="premium-card">
        <h4>📈 Galeri Publikasi Grafik</h4>
        <p>Grafik di bawah ini menggambarkan kesimpulan visual dari ketidakmampuan model melakukan generalisasi lintas dataset, perbandingan kurva ROC, serta matriks kebingungan (confusion matrices).</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display generated figures
    figs = [
        ("fig1_generalization_gap.png", "Grafik 1: Perbedaan Akurasi In-Distribution vs Lintas-Dataset"),
        ("fig2_confusion_matrices.png", "Grafik 2: Confusion Matrices - Model SVM Leksikal"),
        ("fig3_roc_curves.png", "Grafik 3: Kurva Perbandingan ROC (Leksikal vs NLP)"),
        ("fig4_asymmetry.png", "Grafik 4: Analisis Asimetris Pembelajaran Pintasan (Shortcut Learning)")
    ]
    
    for fig_name, description in figs:
        try:
            img = Image.open(resolve_path(fig_name))
            st.markdown(f"### 📈 {description}")
            st.image(img, use_column_width=True)
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        except FileNotFoundError:
            st.warning(f"⚠️ Gambar {fig_name} tidak ditemukan. Silakan jalankan script make_figures.py terlebih dahulu.")
    
    st.info("💡 Semua visualisasi grafik di atas digenerasikan oleh script make_figures.py.")

# Footer
st.markdown("""
<hr style="opacity: 0.1; margin: 40px 0 20px 0;">
<div style='text-align: center; color: #64748b; font-size: 0.85rem;'>
    <p>📚 <b>Tugas UAS Kecerdasan Buatan</b> - Audit Lintas-Dataset Deteksi URL Phishing</p>
    <p>Referensi Ilmiah: Aritonang et al. (2026), JUTIF 7(1), 552–570</p>
</div>
""", unsafe_allow_html=True)

