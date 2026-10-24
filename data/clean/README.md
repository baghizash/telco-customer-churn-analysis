# Log Pembersihan Data — Telco Customer Churn

Dokumen ini mencatat setiap aturan pembersihan yang menghasilkan file bersih,
jumlah baris yang terdampak per aturan, dan cara mereproduksinya dari data mentah.
File bersih ini adalah basis yang sama dengan yang dipakai analisis SQL, notebook,
chart, dan kit Power BI proyek ini.

## File

| | |
|---|---|
| File mentah | `data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv` |
| File bersih | `data/clean/telco_customer_churn_clean.csv` |
| Script reproduksi | `scripts/clean_data.py` |
| Basis pembanding | Tabel `customers` di `data/telco_churn.db` (dibuat `scripts/load_to_sqlite.py`) dan `powerbi/fact_pelanggan.csv` |

## Ringkasan sebelum dan sesudah

| Ukuran | Mentah | Bersih |
|---|---|---|
| Baris | 7.043 | 7.032 |
| Kolom | 21 | 21 |
| Pelanggan churn (`Churn = Yes`) | 1.869 | 1.869 |
| Churn rate | 26,5% (dari basis mentah) | **26,6%** (1.869 dari 7.032) |
| Missing value tersisa | 11 sel tersembunyi (lihat aturan 2) | 0 |

## Aturan pembersihan

### 1. Nama kolom dibersihkan dari spasi di tepi
- Tindakan: `df.columns = df.columns.str.strip()`.
- Baris terdampak: 0. Kolom terdampak: 0 (tidak ada nama kolom yang berubah).

### 2. `TotalCharges` dikonversi dari teks ke angka
- Masalah: kolom ini tiba sebagai teks. Tepat **11 sel** berisi satu spasi (`" "`),
  bukan string kosong dan bukan `NULL`, sehingga tidak terdeteksi oleh pemeriksaan
  missing value biasa.
- Tindakan: `pd.to_numeric(TotalCharges, errors="coerce")`; 11 sel itu menjadi `NaN`.
- Sel terdampak: **11 sel** pada 11 baris. Nilai numerik lain tidak berubah
  (rentang sesudah konversi: 18,8 sampai 8.684,8).

### 3. Sebelas baris tanpa `TotalCharges` dihapus
- Tindakan: baris dengan `TotalCharges` kosong dihapus, **bukan** diimputasi
  dengan 0 atau median.
- Baris terdampak: **11 baris dihapus** (7.043 menjadi 7.032).
- Alasan bisnis: ke-11 baris itu semuanya `tenure = 0` dan `Churn = No`, yaitu
  pelanggan yang pergi sebelum tagihan pertama terbit dan tidak punya riwayat
  tagihan sama sekali. Mengisi nilainya berarti mengarang data.
- Akibat pada metrik: jumlah churn tetap 1.869, hanya penyebut yang berubah,
  jadi churn rate yang dilaporkan adalah 26,6%.
- `customerID` ke-11 baris yang dihapus: 4472-LVYGI, 3115-CZMZD, 5709-LVOEQ,
  4367-NUYAO, 1371-DWPAZ, 7644-OMVMY, 3213-VVOLG, 2520-SGTTA, 2923-ARZLG,
  4075-WKNIU, 2775-SEFEE.

### 4. Pemeriksaan yang hasilnya nol
Pemeriksaan berikut dijalankan oleh script dan tidak menghapus atau mengubah baris apa pun:
- Baris duplikat persis: **0**.
- `customerID` duplikat: **0** (`customerID` unik pada 7.032 baris bersih).
- Missing value pada 20 kolom selain `TotalCharges`: **0 sel**.

## Kolom turunan

- **Tidak ada kolom turunan yang ditambahkan** pada file bersih ini. Nama, urutan
  kolom, dan urutan baris sama dengan file mentah setelah penghapusan 11 baris,
  dan isinya identik dengan tabel `customers` di SQLite.
- Kolom turunan hanya dibuat di hilir untuk Power BI oleh `powerbi/build_kit_csv.py`
  pada `powerbi/fact_pelanggan.csv`: `kelompok_tenure` (0-12, 13-24, 25-48,
  49-72 bulan dari `tenure`), `churn_flag` (1 bila `Churn = Yes`), serta ID
  pengganti `kontrak_id`, `internet_id`, dan `pembayaran_id`. Kolom kolom itu
  tidak masuk ke file bersih ini.

## Cara reproduksi

```bash
~/workspace/mienv/bin/python scripts/clean_data.py
```

Script membaca file mentah, menerapkan aturan 1 sampai 3, menjalankan pemeriksaan
aturan 4, menulis `data/clean/telco_customer_churn_clean.csv`, dan berhenti
dengan assertion bila jumlah baris bukan 7.032 atau jumlah churn bukan 1.869.

## Verifikasi (dijalankan 2026-10-24)

- File bersih dibaca ulang secara independen: **7.032 baris x 21 kolom**, missing value 0.
- Churn dihitung ulang dari file bersih: 1.869 dari 7.032 = **26,6%**.
- Pendapatan berisiko dihitung ulang dari file bersih: jumlah `MonthlyCharges`
  pelanggan churn = **139.130,85 USD per bulan**.
- Himpunan `customerID` file bersih **sama persis** dengan himpunan `customer_id`
  pada `powerbi/fact_pelanggan.csv` (7.032 ID, tanpa selisih).
- Isi file bersih **identik** dengan tabel `customers` di `data/telco_churn.db`
  (perbandingan per sel, 7.032 baris x 21 kolom).
