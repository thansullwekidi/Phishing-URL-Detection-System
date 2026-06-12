# Gap Analysis, Novelty & Research Method (REVISI — berbasis bukti eksperimen)
### UAS Kecerdasan Buatan — Deteksi URL Phishing (NLP + SVM)

**Nama / NIM:** _(isi)_
**Topik:** Phishing URL Detection (Cyber Security)
**Jurnal acuan:** Aritonang dkk. (2026), JUTIF Vol. 7 No. 1, hal. 552–570. DOI: 10.52436/1.jutif.2026.7.1.5334.
**Dataset utama (D1):** PhiUSIIL — **235.795** baris × 56 fitur (label `1`=legitimate, `0`=phishing). UCI 967.
**Dataset uji generalisasi (D2):** ESDAUNG/PhishDataset (Aung & Yamana, WI-IAT '21) — 20.000 URL berlabel (PhishTank + IP2Location), `1`=phishing.

> **Catatan revisi.** Framing awal (data leakage) **dibatalkan oleh eksperimen** dan diganti dengan temuan yang terbukti: *benchmark saturation + generalization failure*. Membuang `URLSimilarityIndex` nyaris tak mengubah performa (redundan), jadi leakage **bukan** penyebabnya.

---

## 1. Research Gap (terbukti empiris)

**G1 — Benchmark saturation: 99.99% adalah properti dataset, bukan keunggulan metode.**
Pada PhiUSIIL, hampir semua subset fitur mencapai ≥99.7% — bahkan **string URL mentah (char n-gram) → 99.8%**, dan **fitur URL-only (21, pre-visit) → 99.7%**. Karena apa pun menang ~99.7%+, klaim paper acuan bahwa "NLP+SVM+GridSearch meningkatkan performa" **tidak dapat dibuktikan** — peningkatan apa pun adalah noise benchmark. [High confidence — tabel ablation.]

**G2 — Kontribusi NLP tidak terisolasi & marginal in-distribution.**
Paper acuan men-*drop* kolom `url`, jadi NLP yang diklaim tak masuk model. Setelah diisolasi dengan benar: combined hanya **+0.1%** atas URL-struct in-dist. NLP bukan driver performa seperti yang diklaim. [High confidence.]

**G3 — TIDAK ADA uji generalisasi lintas-distribusi (gap inti).**
Paper acuan dan seluruh lineage PhiUSIIL hanya evaluasi single-split in-distribution. Tak ada yang menguji apakah model PhiUSIIL bekerja pada dataset phishing **berbeda** — skenario deployment sebenarnya. [High confidence.]

*Catatan: `URLSimilarityIndex` memang near-deterministic (legit≡100.0, corr 0.86), tetapi redundan — membuangnya tak menurunkan performa. Jadi disebut sebagai karakteristik dataset, bukan sebab utama.*

---

## 2. Novelty Statement

Kerangka **re-evaluasi sadar-generalisasi** untuk deteksi URL phishing pada PhiUSIIL. Kontribusi bersifat metodologis + diakhiri arah konstruktif.

**N1 — Demonstrasi saturasi.** Ablation lintas subset fitur (full / minus-suspect / URL-only / content-only / NLP) membuktikan benchmark jenuh.

**N2 — Protokol evaluasi cross-dataset + analisis asimetri (inti).** Train PhiUSIIL → test PhishDataset (dan sebaliknya) dengan ekstraktor fitur identik, mengukur generalisasi nyata.

**N3 — Isolasi NLP → arah konstruktif.** Menunjukkan representasi **level-karakter URL** adalah satu-satunya sinyal yang **transfer** lintas-dataset (AUC 0.94), sedangkan fitur leksikal/struktural runtuh. Ini mengubah kritik menjadi rekomendasi: char-level lebih generalizable.

---

## 3. Research Method (RM)

**RM1 — Replikasi + saturasi.** Reproduksi setup paper acuan (≈99.99%) lalu ablation subset fitur (membuktikan G1).

**RM2 — Generalisasi cross-dataset (usulan).**
1. Ekstraktor fitur leksikal URL buatan sendiri (identik di D1 & D2).
2. Train di D1 → uji D1 hold-out (in-dist) **vs** D2 (cross-dist).
3. Reverse (train D2 → test D1) → analisis asimetri = bukti sampling bias.
4. Isolasi NLP char n-gram (lexical vs NLP, in-dist vs cross).

**Baseline/pembanding:** SVM (replikasi) + Random Forest + Logistic Regression; serta kontras **in-distribution vs cross-distribution**.
**Metrik:** Accuracy, Precision, Recall, F1, ROC-AUC, Confusion Matrix.

---

## 4. Ringkasan Hasil Eksperimen (nyata)

**Saturasi (D1, SVM linear):** FULL 99.99% · minus URLSimilarityIndex 99.98% · URL-only 99.66% · NLP-char 99.78% · combined 99.81%. CV 5-fold konsisten.

**Generalisasi cross-dataset:**

| Model / fitur | In-dist (PhiUSIIL) | Cross (PhishDataset) |
|---|---|---|
| SVM lexical | acc 0.993 / AUC 0.997 | **acc 0.496 / AUC 0.790** |
| RF lexical | acc 0.996 / AUC 0.998 | **acc 0.498 / AUC 0.496** |
| SVM NLP-char | acc 0.998 / AUC 0.999 | acc 0.613 / **AUC 0.940** |
| *Reverse* (train D2→D1) | D2 0.865 | **PhiUSIIL 0.901 / AUC 0.974** |

**Temuan:** model 99.x% di PhiUSIIL **runtuh ke ~50% (tebak acak)** di dataset lain; asimetri (D2→D1 = 90%) membuktikan PhiUSIIL mengajari shortcut non-transferable; NLP char satu-satunya yang mempertahankan sinyal (AUC 0.94).

---

## 5. Framework Penelitian
```
D1 PhiUSIIL ─┐                          ┌─ in-dist eval (hold-out)
             ├─ lexical extractor (sama)─┤
D2 PhishDS ──┘   + char n-gram TF-IDF    └─ cross-dataset eval
        │
        ├─ RM1: replikasi + saturation ablation
        └─ RM2: train→test silang (D1↔D2) + isolasi NLP + asimetri
                       │
                       └─ Analisis: saturasi | gagal generalisasi | char-level transferable
```

## 6. Pemetaan Rubrik
Gap (15%)=G1–G3 terbukti · Novelty (15%)=N1–N3 · RM (10%)=RM1+RM2 · Implementasi (15%)=2 dataset, 3 model · Bonus=2 dataset + multi-baseline (sudah terpenuhi) + GitHub.

*Status: Step 2 REVISI terkunci by evidence. Figur di folder 08; hasil di 07.*
