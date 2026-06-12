# UAS Kecerdasan Buatan — Deteksi URL Phishing (Cross-Dataset Audit)

**Nama:** _[isi]_  ·  **NIM:** _[isi]_  ·  **Kelas:** _[isi]_
**Judul:** Beyond 99% Accuracy: A Cross-Dataset Audit of NLP and SVM Phishing-URL Detection on the PhiUSIIL Benchmark
**Jurnal acuan:** Aritonang dkk. (2026), JUTIF 7(1), 552–570. DOI: 10.52436/1.jutif.2026.7.1.5334

---

## Research Gap
- **G1 — Benchmark saturation:** pada PhiUSIIL hampir semua subset fitur (bahkan string URL mentah) mencapai ≥99.7%; akurasi 99.99% adalah sifat dataset, bukan keunggulan metode.
- **G2 — Kontribusi NLP tak terisolasi & marginal:** paper acuan men-drop kolom URL; setelah diisolasi NLP hanya +0.1% in-distribution.
- **G3 — Tanpa uji generalisasi lintas-distribusi:** tak ada studi PhiUSIIL yang menguji ke dataset phishing berbeda (skenario deployment nyata).

## Novelty
- **N1** Demonstrasi saturasi via feature-availability ablation.
- **N2** Protokol evaluasi cross-dataset (train D1 → test D2, dan reverse) + analisis asimetri.
- **N3** Isolasi NLP → representasi level-karakter URL adalah satu-satunya sinyal transferable (arah konstruktif).

## Research Method
- **RM1** Replikasi pipeline acuan (≈99.99%) + ablation subset fitur.
- **RM2** Evaluasi cross-dataset (D1↔D2) dengan ekstraktor fitur identik; baseline SVM/RF/LogReg; isolasi NLP char n-gram; metrik Acc/Prec/Rec/F1/AUC + confusion matrix.

## Ringkasan Hasil
| | In-distribution (PhiUSIIL) | Cross-dataset (PhishDataset) |
|---|---|---|
| SVM lexical | acc 0.993 / AUC 0.997 | **acc 0.496 / AUC 0.790** |
| RF lexical | acc 0.996 / AUC 0.998 | **acc 0.498 / AUC 0.496** |
| SVM NLP-char | acc 0.998 / AUC 0.999 | acc 0.613 / **AUC 0.940** |
| Reverse (D2→D1) | — | **PhiUSIIL acc 0.901 / AUC 0.974** |

**Temuan:** model 99.x% di PhiUSIIL runtuh ke ~50% (tebak acak) di dataset independen; asimetri (D2→D1 = 90%) membuktikan sampling bias; char n-gram satu-satunya yang mempertahankan sinyal cross-dataset (AUC 0.94).

---

## Cara Menjalankan (juga README untuk 05_Source_Code)
**Library:** Python 3.10+, `pandas numpy scikit-learn scipy matplotlib openpyxl`
```bash
pip install pandas numpy scikit-learn scipy matplotlib openpyxl
```
**Dataset:** taruh `Dataset.csv` (PhiUSIIL) dan `data_bal - 20000.xlsx` (PhishDataset) sesuai path di skrip (lihat `04_Dataset/Dataset_Source.txt`).
**Eksekusi:**
```bash
python experiment.py        # RM1: replikasi + saturation ablation  -> experiment_results.json
python crossdataset.py      # RM2: cross-dataset + reverse + NLP     -> crossdataset_results.json
python make_figures.py      # 4 figur -> fig1..fig4.png
```

---

## Struktur Folder
`Nama_NIM_UAS_AI/` — lihat `STRUKTUR_FOLDER.md` untuk pemetaan lengkap tiap berkas ke 11 subfolder + checklist.

## Catatan penting (wajib dibereskan sebelum submit)
1. Isi semua placeholder `[isi]` (nama, NIM, kelas, universitas, email) di README, paper, dan slide.
2. Verifikasi kuartil/indeks `(cek)` di `02_Literature_Mapping.md`; ganti P10 (IJCA, non-Scopus); verifikasi P3 (TSP).
3. Download 10 PDF referensi ke `01_Paper/`.
4. Format 2-kolom final: paste isi `Draft_Artikel_IEEE.docx` ke template IEEE resmi.
5. Jalankan Turnitin (≤15%); cross-check md5 dataset ke UCI resmi.
