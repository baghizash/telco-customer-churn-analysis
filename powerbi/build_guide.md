# Panduan Membangun Dashboard — Power BI Desktop

## 1. Persiapan (5 menit)
1. (Opsional, untuk membuat ulang CSV) Jalankan `python powerbi/build_kit_csv.py` dari folder proyek. Script itu membaca `data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv`, menerapkan pembersihan yang sama dengan analisis asli, dan menulis ulang keempat CSV di folder ini.
2. Buka Power BI Desktop → Get Data → Text/CSV → impor keempat CSV di folder ini:
   `fact_pelanggan.csv`, `dim_kontrak.csv`, `dim_internet.csv`, `dim_pembayaran.csv`.
3. Pastikan tipe data: `tenure_bulan`, `senior_citizen`, dan `churn_flag` = Whole Number; `monthly_charges` dan `total_charges` = Decimal Number; `customer_id` dan semua kolom `*_id` serta kolom teks lainnya = Text. Power BI kadang membaca `customer_id` seperti `0002-ORFBO` dengan benar sebagai teks, tetapi periksa juga `senior_citizen` dan `churn_flag` agar tidak terbaca sebagai teks.
4. Sembunyikan kolom `kontrak_id`, `internet_id`, dan `pembayaran_id` pada `fact_pelanggan` dari Report view (klik kanan kolom → Hide in report view). Kolom itu hanya untuk relasi; label yang tampil di visual selalu dari tabel dimensi.
5. Buka Model view. Buat relasi (semuanya satu-ke-banyak, single direction, dari dimensi ke fakta):
   - `dim_kontrak[kontrak_id]` → `fact_pelanggan[kontrak_id]`
   - `dim_internet[internet_id]` → `fact_pelanggan[internet_id]`
   - `dim_pembayaran[pembayaran_id]` → `fact_pelanggan[pembayaran_id]`
6. Tidak ada tabel tanggal pada model ini: dataset adalah satu potret statis tanpa tanggal churn, jadi tidak perlu Mark as Date Table dan tidak ada halaman tren waktu.

## 2. Measures (10 menit)
1. Salin seluruh blok DAX dari `measures_dax.md` ke dalam model (buat satu tabel measure khusus, atau gunakan folder display: "Inti", "Pendapatan dan Risiko", dan "Segmen Acuan").
2. Baca bagian "Catatan level" di `measures_dax.md` SEBELUM membuat visual — terutama catatan 7.043 baris mentah vs 7.032 pelanggan bersih.
3. Atur format: measure persen sebagai Percentage 1 desimal; measure uang sebagai Currency USD 2 desimal.
4. Uji cepat: buat card dengan `Total Pelanggan`, `Persen Churn`, dan `Revenue At Risk` tanpa filter apa pun → harus **7.032**, **26,6%**, dan **USD 139.130,85**. Jika `Total Pelanggan` menunjukkan 7.043, visual membaca CSV mentah, bukan `fact_pelanggan`.

## 3. Bangun 4 halaman (30–45 menit)
Ikuti `dashboard_layout.md` halaman per halaman:
- Halaman 1: ringkasan — KPI keseluruhan, donut churn, Persen Churn per kontrak dan per internet.
- Halaman 2: kontrak, tenure, dan pembayaran — termasuk tabel kombinasi kontrak × internet.
- Halaman 3: layanan, dukungan, dan demografi — kategori "No internet service" selalu terpisah dari "No".
- Halaman 4: pendapatan berisiko per kontrak dan per pembayaran, plus tabel metodologi yang diketik manual dari `dashboard_layout.md`.

## 4. Verifikasi akhir (10 menit)
- [ ] Tanpa filter: Total Pelanggan 7.032; Total Churn 1.869; Persen Churn 26,6%; Revenue At Risk USD 139.130,85 per bulan; Persen Revenue At Risk 30,5%.
- [ ] Halaman 1: Persen Churn Month-to-month 42,7% dan Two year 2,8%; Fiber optic 41,9%.
- [ ] Halaman 2: kelompok tenure 0-12 bulan 47,7%; Electronic check 45,3%; kombinasi Fiber optic + Month-to-month 54,6%.
- [ ] Halaman 3: tanpa Online Security 41,8%; tanpa Tech Support 41,6%; senior citizen 41,7%.
- [ ] Halaman 4: Revenue At Risk per kontrak Month-to-month USD 120.847,10; rata-rata tagihan pelanggan churn USD 74,44 vs bertahan USD 61,31.
- [ ] Tidak ada visual yang membaca `data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv` secara langsung.
- [ ] Simpan sebagai `Telco-Churn-Analysis.pbix` (file .pbix tidak di-push ke GitHub — GitHub tidak bisa me-render-nya; simpan screenshot dashboard sebagai gantinya bila perlu).

## Troubleshooting
- **Total Pelanggan 7.043, bukan 7.032**: sumber visual adalah CSV mentah. Hapus tabel mentah dari model dan arahkan semua visual ke `fact_pelanggan` yang sudah dibersihkan.
- **Persen Churn tampil 0,27 atau 2660%**: format measure belum diatur. Measure mengembalikan rasio; atur formatnya ke Percentage dengan 1 angka desimal.
- **Label kontrak atau pembayaran kosong pada sebagian baris**: ada `*_id` pada fakta yang tidak terpetakan di dimensi. Jalankan ulang `build_kit_csv.py` (script berhenti dengan assertion bila ada nilai yang tidak terpetakan), lalu Refresh data.
- **Kelompok tenure terurut abjad secara janggal**: urutan teks menaruh "13-24 bulan" sebelum "0-12 bulan" pada sebagian visual. Atur sort manual lewat urutan kemunculan pada layout (0-12, 13-24, 25-48, 49-72) atau urutkan visual menurut nilai bila urutan logis tidak tersedia.
- **Kategori "No internet service" menyatu dengan "No"**: keduanya nilai yang berbeda pada data asli dan churn-nya jauh berbeda (7,4% vs sampai 41,8%). Jangan buat kolom penggabung; tampilkan apa adanya.
- **Angka tidak cocok dengan README**: pastikan tidak ada slicer atau filter halaman yang tertinggal aktif, dan visual memakai `Persen Churn` (bukan rata-rata manual atas `churn_label`).
