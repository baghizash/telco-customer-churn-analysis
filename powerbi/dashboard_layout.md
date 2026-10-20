# Dashboard Layout — Telco Customer Churn (4 halaman, 16:9)

Palet (sama dengan palet chart pada analisis asli): biru utama `#4E7FA6`, biru gelap `#33536E` (judul dan penekanan), pink churn `#C75B7F` (hanya untuk churn dan risiko), oat netral `#C9BFA9`, latar oat `#EFE7D8`, tinta `#2E3138`.
Font: Segoe UI / Calibri. Satu ide per halaman, judul rata kiri, angka kunci besar.
Semua halaman membaca satu-satunya tabel fakta `fact_pelanggan` beserta ketiga dimensinya.

## Halaman 1 — Ringkasan Churn
- **KPI cards (4)**: Total Pelanggan **7.032**; Persen Churn **26,6%** (1.869 churn); Revenue At Risk **USD 139.130,85 per bulan** (30,5% dari total pendapatan bulanan USD 455.661,00); Rata-rata Tenure **32,42 bulan**.
- **Donut chart**: komposisi pelanggan menurut `churn_label` (Churn 1.869 vs Bertahan 5.163). Warna churn pink, bertahan biru utama.
- **Bar chart**: Persen Churn per `dim_kontrak[kontrak]` (Month-to-month 42,7%; One year 11,3%; Two year 2,8%).
- **Bar chart kecil**: Persen Churn per `dim_internet[layanan_internet]` (Fiber optic 41,9%; DSL 19,0%; No 7,4%).
- **Slicers**: Kontrak, Layanan Internet. (Kartu KPI keseluruhan dikecualikan dari interaksi slicer lewat Edit Interactions, supaya angka acuan halaman tidak berubah.)
- Catatan kaki: "Sumber: IBM Sample Telco Customer Churn via Kaggle. 7.032 pelanggan bersih; 11 baris tanpa riwayat tagihan dikeluarkan, lihat README."

## Halaman 2 — Kontrak, Tenure, dan Pembayaran
- **Bar chart**: Persen Churn per `kelompok_tenure` pada `fact_pelanggan` (0-12 bulan 47,7%; 13-24 bulan 28,7%; 25-48 bulan 20,4%; 49-72 bulan 9,5%). Urutkan menurut urutan kelompok, bukan menurut nilai.
- **Bar chart horizontal**: Persen Churn per `dim_pembayaran[metode_pembayaran]` (Electronic check 45,3%; Mailed check 19,2%; Bank transfer (automatic) 16,7%; Credit card (automatic) 15,3%).
- **Tabel segmen kombinasi**: Kontrak × Layanan Internet berisi Total Pelanggan, Total Churn, dan Persen Churn. Sorot sel Fiber optic + Month-to-month: **54,6%** (1.162 dari 2.128), nilai tertinggi pada tabel.
- **Kartu pembanding tenure**: Rata-rata Tenure Pelanggan Churn **17,98 bulan** vs Rata-rata Tenure Pelanggan Bertahan **37,65 bulan**.
- **Slicers**: Kontrak, Metode Pembayaran.

## Halaman 3 — Layanan, Dukungan, dan Demografi
- **Bar chart berpasangan**: Persen Churn menurut `online_security` (No 41,8%; Yes 14,6%; No internet service 7,4%) dan menurut `tech_support` (No 41,6%; Yes 15,2%; No internet service 7,4%). Kategori "No internet service" selalu ditampilkan terpisah, jangan digabung dengan "No".
- **Bar chart kecil**: Persen Churn menurut `online_backup` (No 39,9%; Yes 21,6%) dan `device_protection` (No 39,1%; Yes 22,5%).
- **Bar chart demografi**: Persen Churn menurut `senior_citizen` (Senior 41,7%; Non-senior 23,7%), `partner` (No 33,0%; Yes 19,7%), dan `dependents` (No 31,3%; Yes 15,5%).
- **Bar chart**: Persen Churn menurut `paperless_billing` (Yes 33,6%; No 16,4%).
- **Slicers**: Layanan Internet, Kontrak.

## Halaman 4 — Pendapatan Berisiko dan Metodologi
- **KPI cards (3)**: Total Pendapatan Bulanan **USD 455.661,00**; Revenue At Risk **USD 139.130,85**; Persen Revenue At Risk **30,5%**.
- **Bar chart**: Revenue At Risk per `dim_kontrak[kontrak]` (Month-to-month USD 120.847,10; One year USD 14.118,45; Two year USD 4.165,30).
- **Bar chart**: Revenue At Risk per `dim_pembayaran[metode_pembayaran]` (Electronic check USD 84.288,75; Bank transfer (automatic) USD 20.091,90; Credit card (automatic) USD 17.946,60; Mailed check USD 16.803,60).
- **Kartu pembanding tagihan**: Rata-rata Tagihan Pelanggan Churn **USD 74,44** vs Rata-rata Tagihan Pelanggan Bertahan **USD 61,31** — yang pergi justru pelanggan yang membayar lebih mahal.
- **Tabel metodologi** (ketik manual): sumber data (IBM Sample Telco Customer Churn via Kaggle, satu perusahaan telekomunikasi fiktif); grain fakta 1 baris per pelanggan; pembersihan (11 baris `TotalCharges` kosong, semuanya tenure 0 dan tidak churn, dihapus bukan diisi; 7.043 baris mentah menjadi 7.032); definisi churn (`Churn` = Yes, `churn_flag` = 1); definisi Revenue At Risk (jumlah `monthly_charges` pelanggan churn, per bulan); keterbatasan (data satu potret statis tanpa tanggal churn, jadi tidak ada tren waktu; `total_charges` adalah akumulasi seumur berlangganan, bukan pendapatan bulanan).
- **Tombol navigasi** kembali ke Halaman 1.

## Aturan konsisten
- Judul halaman: 20pt bold, rata kiri, warna biru gelap `#33536E`.
- Angka KPI: 28pt bold biru gelap; persen 1 desimal; uang format USD 2 desimal dengan pemisah ribuan.
- Warna pink `#C75B7F` hanya untuk churn, Persen Churn tertinggi, dan Revenue At Risk. Segmen lain memakai biru utama atau oat netral — jangan beri pink pada angka yang bukan risiko.
- Urutan kategori selalu mengikuti urutan logis datanya (kontrak: Month-to-month, One year, Two year; tenure: 0-12, 13-24, 25-48, 49-72 bulan), bukan urutan abjad dan bukan urutan nilai, kecuali pada bar chart horizontal Halaman 2 dan 4 yang memang diurutkan menurut nilai.
- Tidak ada visual yang membaca CSV mentah di `data/raw/`: semua visual membaca `fact_pelanggan` dan dimensinya.
- Setiap halaman mencantumkan catatan sumber di kaki halaman.
