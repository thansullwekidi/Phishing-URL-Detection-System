# Literature Mapping & Comparison Matrix (REVISI)
### UAS Kecerdasan Buatan — Deteksi URL Phishing

**Tema:** Phishing URL/Website Detection (ML & NLP), 2020–2026.
**Fungsi:** menopang gap **G1 (saturation), G2 (NLP marginal), G3 (tanpa uji generalisasi cross-dataset)**.

> Kuartil/indeks bertanda `(cek)` **wajib diverifikasi sendiri** (Scimago/SINTA/PDF). Tidak ada quartile/angka yang dikarang.

---

## 1. Sepuluh Paper Utama

| # | Penulis (Th) | Inti | Venue | Reputasi |
|---|---|---|---|---|
| P1 | Prasad & Chandra (2024) | Framework PhiUSIIL (similarity index + incremental) — **sumber dataset D1** | Computers & Security (Elsevier) | Scopus Q1 |
| P2 | Aritonang dkk. (2026) — **acuan** | NLP+SVM, 99.99% single-split | JUTIF 7(1) | SINTA 2 `(cek)` |
| P3 | **Aung & Yamana (2024/21)** — PhiSN | Segmentasi+NLP; **sumber dataset D2 (cross-test)** | J. Information Processing / WI-IAT'21 | Scopus/IEEE `(cek)` |
| P4 | Kalla & Kuraku (2023) | NLP+ML URL | Journal on AI (TSP) | `(cek indeks)` |
| P5 | Haq dkk. (2024) | CNN deep learning | Applied Sciences (MDPI) | Scopus Q1/Q2 `(cek)` |
| P6 | Asiri, Xiao & Li (2024) | PhishTransformer | Electronics (MDPI) | Scopus Q2/Q3 `(cek)` |
| P7 | Shombot dkk. (2024) | SVM phishing | Cyber Security and Applications (Elsevier) | Scopus `(cek)` |
| P8 | Catal dkk. (2022) | SLR deep learning phishing | Knowledge & Information Systems (Springer) | Scopus Q1/Q2 `(cek)` |
| P9 | Safi & Singh (2023) | SLR teknik deteksi | JKSU-CIS (Elsevier) | Scopus Q1 `(cek)` |
| P10 | John-Otumu dkk. (2025) | ANN+Ridge pada PhiUSIIL | IJCA | ⚠️ Non-Scopus — bukti pola saja |

> Ganti P10 dgn paper PhiUSIIL ber-venue lebih kuat (Procedia CS 2025 / Springer) bila dosen ketat.

---

## 2. Comparison Matrix (kekurangan → gap)

| Artikel | Dataset | Metode | Hasil | Kekurangan → gap |
|---|---|---|---|---|
| P1 | PhiUSIIL | similarity index | sgt tinggi | Single dataset; tak uji generalisasi → **G3** |
| P2 (acuan) | PhiUSIIL | NLP+SVM | 99.99% | Saturasi tak disadari; NLP di-drop; single-split → **G1,G2,G3** |
| P3 Aung&Yamana | PhishTank+IP2Loc | segmentasi+NLP | tinggi | Tetap evaluasi in-dataset → **G3** |
| P4 Kalla&Kuraku | URL | NLP+ML | naik | NLP tak diisolasi → **G2** |
| P5 Haq | URL | CNN | unggul | Berat; in-dataset saja |
| P6 Asiri | URL | Transformer | tinggi | in-dataset saja |
| P7 Shombot | URL | SVM | baik | Fitur statis; in-dataset → **G3** |
| P8 Catal | SLR | review DL | — | Tak menyoroti generalisasi lintas-dataset |
| P9 Safi&Singh | SLR | review | — | Menegaskan protokol evaluasi tak konsisten → **G3** |
| P10 John-Otumu | PhiUSIIL | ANN+Ridge | tinggi | Pola ~99% PhiUSIIL berulang, tanpa uji cross → **G1,G3** |

**Inti sintesis:** seluruh lineage melaporkan ~99% pada **satu** dataset/in-distribution. **Tak satu pun** menguji generalisasi ke dataset phishing berbeda. Itulah celah yang penelitian ini isi dan buktikan (collapse ke ~50% cross-dataset).

---

## 3. Referensi Metodologi (anchor untuk protokol cross-dataset / external validation)
- Studi yang menekankan **realistic/cross-distribution evaluation** & bahaya metrik in-distribution yang inflasi (mis. "more realistic evaluation of ML" — bearing fault, arXiv 2509.22267; "subject-independence" gesture eval, arXiv 2602.17854) — gunakan sebagai dasar bahwa external/cross-dataset validation adalah praktik wajib.
- Studi data leakage (Parkinson's, MDPI `(cek)`; "Data Leakage in Notebooks", arXiv 2209.03345) — relevan untuk membahas mengapa skor in-distribution bisa menyesatkan.

> Tambahkan 1–2 referensi **dataset bias / external validation** agar G3 makin kokoh secara akademik.

---

## 4. To-do verifikasi
1. Konfirmasi semua `(cek)` (Scimago/SINTA); ganti P10, verifikasi P4.
2. Unduh PDF P1–P10 → `01_Paper/`; isi angka spesifik.
3. Sitir D2 (Aung & Yamana) sebagai sumber dataset cross-test.

*Status: Step 3 REVISI selesai — sintesis kini berpusat pada gap generalisasi (terbukti).*
