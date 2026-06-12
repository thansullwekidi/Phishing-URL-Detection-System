# Panduan Struktur Folder — Nama_NIM_UAS_AI/

Pemetaan setiap berkas yang sudah dibuat ke struktur folder wajib UAS.
Legenda: ✅ = sudah ada (dari sesi ini) · ⬜ = tugasmu

```
Nama_NIM_UAS_AI/
├── README.md                          ✅ (README.md)
├── 01_Paper/                          ⬜ download 10 PDF referensi (lihat 02_Literature_Mapping)
├── 02_Literature_Mapping/
│   └── 02_Literature_Mapping.md       ✅ (Literature Mapping + Comparison Matrix)
├── 03_Gap_Analysis/
│   └── 03_Gap_Analysis.md             ✅ (Gap, Novelty, RM, Framework)
├── 04_Dataset/
│   ├── Dataset_Source.txt             ✅
│   ├── Raw_Dataset/                   ⬜ Dataset.csv (PhiUSIIL) + "data_bal - 20000.xlsx"
│   └── Processed_Dataset/             ⬜ (opsional) hasil preprocessing
├── 05_Source_Code/
│   ├── experiment.py                  ✅ RM1 replikasi + saturation
│   ├── crossdataset.py                ✅ RM2 cross-dataset + reverse + NLP
│   ├── make_figures.py                ✅ generate figur
│   └── README.md                      ✅ (pakai bagian "Cara Menjalankan" di README utama)
├── 06_Model/                          ⬜ (opsional) simpan model .pkl bila diminta
├── 07_Hasil_Eksperimen/
│   ├── experiment_results.json        ✅
│   └── crossdataset_results.json      ✅
├── 08_Visualisasi/
│   ├── fig1_generalization_gap.png    ✅
│   ├── fig2_confusion_matrices.png    ✅
│   ├── fig3_roc_curves.png            ✅
│   └── fig4_asymmetry.png             ✅
├── 09_Draft_IEEE/
│   ├── Draft_Artikel_IEEE.docx        ✅
│   └── Draft_Artikel_IEEE.pdf         ✅
├── 10_Presentasi/
│   ├── Slide_Presentasi.pptx          ✅
│   └── Slide_Presentasi.pdf           ✅
└── 11_Turnitin/
    └── Turnitin_Report.pdf            ⬜ jalankan Turnitin (≤15%)
```

## Checklist akhir (tugasmu)
- [ ] Isi placeholder `[isi]` (nama, NIM, kelas, universitas, email) di README, paper, slide.
- [ ] Download 10 PDF ke `01_Paper/`; isi angka hasil `(cek)` di mapping.
- [ ] Verifikasi kuartil `(cek)`; ganti P10 (IJCA); verifikasi P3 (TSP).
- [ ] Taruh dataset di `04_Dataset/Raw_Dataset/`.
- [ ] Paste paper ke template IEEE resmi → format 2 kolom; export PDF final.
- [ ] Turnitin → `11_Turnitin/`.
- [ ] (Bonus) Push ke GitHub berdokumentasi; set Drive "Anyone with the link can view".

## Bonus yang sudah otomatis terpenuhi
- ✅ Lebih dari satu dataset (PhiUSIIL + PhishDataset).
- ✅ Lebih dari satu metode pembanding (SVM, RF, LogReg).
```
```
