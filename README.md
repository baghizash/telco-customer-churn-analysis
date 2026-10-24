# Analisis Telco Customer Churn (Customer Retention Analytics)

Analisis end-to-end tingkat *churn* (pelanggan berhenti berlangganan) menggunakan SQL dan Python:
data dimuat ke SQLite, setiap pertanyaan bisnis dijawab dengan **query SQL asli** (`sql/queries.sql`),
divisualisasikan dalam 12 chart (`charts/`), dan dinarasikan dalam notebook (`analysis.ipynb`).

## Ringkasan Eksekutif

- Churn rate keseluruhan: **26,6%** (1.869 dari 7.032 pelanggan bersih).
- Segmen paling rawan churn: **fiber optic + kontrak bulanan 54,6%** (1.162 dari 2.128),
  **kontrak bulanan + pelanggan baru 51,4%** (1.024 dari 1.994), **cek elektronik 45,3%**
  (1.071 dari 2.365), **kontrak bulanan 42,7%** (1.655 dari 3.875 — menyumbang 88,6% semua churn),
  **fiber optic 41,9%** (1.297 dari 3.096), **tanpa Online Security 41,8%**, **senior citizen 41,7%**
  (476 dari 1.142), **tanpa Tech Support 41,6%**, **pelanggan baru 0-12 bulan 47,7%**
  (1.037 dari 2.175 — menyumbang 55,5% semua churn).
- Pendapatan yang hilang akibat churn: **139.131 USD per bulan**, atau **30,5%** dari seluruh
  pendapatan bulanan. Pelanggan yang churn membayar rata-rata 74,44 USD/bulan vs 61,31 USD yang bertahan —
  yang pergi adalah pelanggan bernilai lebih tinggi.
- Pola umum: pelanggan baru, kontrak bulanan, layanan fiber yang mahal, pembayaran manual tanpa auto-pay,
  dan tanpa layanan dukungan adalah kombinasi yang paling sering pergi. Lihat `analysis.ipynb`
  bagian "Temuan Kunci" untuk tabel lengkap.

## Data

- **Sumber:** IBM Sample Telco Customer Churn — dataset publik via Kaggle
  (kaggle.com/datasets/blastchar/telco-customer-churn), satu perusahaan telekomunikasi fiktif.
- **Ukuran:** 7.043 baris pelanggan mentah × 21 kolom; **7.032 baris bersih** setelah pembersihan
  (lihat di bawah). Tidak ada duplikat customerID.
- **File mentah:** `data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv`.
- **File bersih:** `data/clean/telco_customer_churn_clean.csv` (7.032 baris × 21 kolom, dibuat oleh `scripts/clean_data.py`; log aturan pembersihan lengkap, termasuk baris yang terdampak per aturan, ada di `data/clean/README.md`).
- **Database:** `data/telco_churn.db` (SQLite, dibuat ulang oleh script; tidak di-commit ke git).

## Pembersihan Data (Keputusan Bisnis)

Kolom `TotalCharges` (total tagihan akumulasi) tiba sebagai **teks**, bukan angka. Di dalamnya
tersembunyi **11 nilai kosong** (string kosong) yang tidak terdeteksi `isna()`.
Ke-11 baris itu semuanya `tenure = 0` dan `Churn = No`: pelanggan yang berhenti sebelum tagihan
pertama terbit, jadi tidak punya riwayat tagihan sama sekali.

**Keputusan: 11 baris tersebut dihapus, bukan diisi.** Mengisi dengan 0 atau median berarti
mengarang nilai untuk pelanggan tanpa riwayat tagihan. Karena ke-11 baris itu semuanya `Churn = No`,
jumlah pelanggan churn (1.869) tidak berubah — hanya denominasi total yang berubah dari 7.043
menjadi 7.032, sehingga churn rate yang dilaporkan adalah 26,6%.

## Definisi Metrik

- **Churn:** pelanggan dengan kolom `Churn` bernilai `Yes`.
- **Churn rate** = jumlah churn / total pelanggan pada segmen tersebut.
- **Pendapatan hilang** = jumlah `MonthlyCharges` pelanggan churn.
- Rate pada tiap segmen dihitung langsung dari data via SQL — tidak ada angka yang dikarang.

## Struktur Repo

```
telco-churn/
├── analysis.ipynb                  # notebook naratif (Bahasa Indonesia): SQL + chart + insight
├── README.md
├── requirements.txt
├── .gitignore
├── scripts/
│   ├── load_to_sqlite.py           # load CSV -> data/telco_churn.db (+ index), verifikasi 7032 baris
│   ├── clean_data.py               # buat data/clean/telco_customer_churn_clean.csv dari data mentah
│   └── make_charts.py              # membuat ulang 12 chart dari database
├── sql/
│   └── queries.sql                 # semua query analisis dengan komentar Bahasa Indonesia
├── charts/                         # 12 chart PNG (palet konsisten)
│   ├── 01_churn_overall.png
│   ├── 02_churn_contract.png
│   ├── 03_churn_tenure.png
│   ├── 04_churn_internet.png
│   ├── 05_churn_payment.png
│   ├── 06_churn_monthly_charges.png
│   ├── 07_churn_support.png
│   ├── 08_churn_demografi.png
│   ├── 09_churn_revenue.png
│   ├── 10_churn_combo.png
│   ├── 11_churn_services.png
│   └── 12_churn_totalcharges_paperless.png
└── data/
    ├── raw/WA_Fn-UseC_-Telco-Customer-Churn.csv
    ├── clean/telco_customer_churn_clean.csv   # 7.032 baris bersih (log: data/clean/README.md)
    └── telco_churn.db              # dibuat oleh script, diabaikan git
```

## Yang Dikerjakan

1. Pemuatan data CSV ke SQLite dengan pembersihan `TotalCharges` (teks ke angka, 11 baris
   tanpa riwayat tagihan dihapus dengan alasan bisnis), index pada kolom yang sering dipakai
   di `WHERE`/`GROUP BY`, plus verifikasi jumlah baris = 7.032.
2. Analisis 10 pertanyaan bisnis (churn keseluruhan; kontrak; masa berlangganan; layanan internet;
   metode pembayaran; tagihan bulanan dan pendapatan hilang; layanan dukungan; demografi;
   segmen kombinasi; layanan tambahan dan akumulasi tagihan) — semuanya dengan query SQL
   yang tersimpan di `sql/queries.sql`.
3. Visualisasi 12 chart PNG dengan palet warna dan gaya yang konsisten.
4. Notebook naratif Bahasa Indonesia: tiap section berisi penjelasan singkat, query SQL yang dijalankan
   langsung ke database (hasil tampil sebagai tabel), chart, dan insight 1-2 kalimat.
   Notebook lolos uji *restart kernel + run all* tanpa error.
5. Rekomendasi retensi berbasis temuan (di notebook dan di bawah).

## Cara Reproduce

```bash
pip install -r requirements.txt
python scripts/load_to_sqlite.py   # membuat data/telco_churn.db, verifikasi 7032 baris
python scripts/clean_data.py       # membuat data/clean/telco_customer_churn_clean.csv, verifikasi 7032 baris
# buka analysis.ipynb di Jupyter lalu jalankan semua sel,
# atau buat ulang chart: python scripts/make_charts.py
```

## Rekomendasi Retensi

1. **Program onboarding 12 bulan pertama yang terstruktur.** Pelanggan baru churn 47,7% —
   sapa proaktif di bulan ke-1, 3, dan 6; tawarkan tur layanan dan cek kepuasan dini.
2. **Konversi kontrak bulanan ke kontrak tahunan dengan insentif.** Kontrak bulanan churn 42,7%
   dan menyumbang 88,6% semua churn — diskon loyalitas, harga terkunci, dan bonus layanan
   untuk yang pindah ke kontrak 1-2 tahun.
3. **Audit nilai layanan Fiber optic.** Churn 41,9% pada layanan termahal adalah alarm —
   tinjau kualitas jaringan per area, harga, dan komunikasi manfaatnya.
4. **Dorong auto-pay dan migrasi dari cek elektronik.** Cek elektronik churn 45,3% —
   insentif kecil untuk pindah ke kartu kredit atau transfer bank otomatis.
5. **Tawarkan Tech Support dan Online Security secara proaktif.** Tanpa dukungan churn 41,6%,
   dengan dukungan 15,2% — bundel dukungan gratis 3 bulan untuk pelanggan baru dan segmen rawan.
6. **Perhatian khusus untuk lansia dan pelanggan yang hidup sendiri.** Senior churn 41,7%,
   tanpa pasangan 33,0% — jalur dukungan yang lebih personal dan mudah dijangkau.

## Dashboard Power BI

Kit Power BI tersedia di folder `powerbi/`: `fact_pelanggan.csv` (grain 1 baris per pelanggan bersih, 7.032 baris), `dim_kontrak.csv`, `dim_internet.csv`, `dim_pembayaran.csv`, script pembangkitnya `build_kit_csv.py`, serta `measures_dax.md`, `dashboard_layout.md`, `build_guide.md`, dan pratinjau `dashboard_preview_halaman1.png`. Angka verifikasi pada kit: churn 26,6% (1.869 dari 7.032), churn kontrak Month-to-month 42,7% vs Two year 2,8%, dan Revenue At Risk USD 139.130,85 per bulan.

Ringkasan 4 halaman dashboard (16:9):

1. **Ringkasan Churn** — KPI keseluruhan, donut churn vs bertahan, churn per kontrak dan per layanan internet.
2. **Kontrak, Tenure, dan Pembayaran** — churn per kelompok tenure, per metode pembayaran, dan tabel kombinasi kontrak × internet (tertinggi: Fiber optic + Month-to-month 54,6%).
3. **Layanan, Dukungan, dan Demografi** — churn menurut Online Security, Tech Support, layanan tambahan, senior citizen, partner, dependents, dan paperless billing.
4. **Pendapatan Berisiko dan Metodologi** — Revenue At Risk per kontrak dan per pembayaran, pembanding tagihan churn vs bertahan, dan tabel metodologi.

File `.pbix` dibangun lokal di Power BI Desktop mengikuti `powerbi/build_guide.md` (nama berkas yang disarankan: `Telco-Churn-Analysis.pbix`) dan tidak di-commit ke repo ini karena GitHub tidak bisa me-render-nya. Screenshot dashboard ditambahkan setelah build selesai.

## Deliverables lain di repo ini
- Portofolio-Analisis-Telco-Churn.pptx — deck portofolio 10 slide (16:9)
- Modul-Analisis-Telco-Churn.pdf — modul belajar step-by-step (21 halaman)
