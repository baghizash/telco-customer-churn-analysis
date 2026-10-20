# DAX Measures — Telco Customer Churn

## Catatan level (PENTING — baca dulu)

Model ini memakai **satu tabel fakta saja** dengan satu grain yang tegas:

| Tabel fakta | Grain (1 baris =) | Untuk visual... |
|---|---|---|
| `fact_pelanggan` | 1 pelanggan bersih | Semua halaman: churn keseluruhan, per kontrak, per internet, per pembayaran, per tenure, per layanan dukungan, dan pendapatan |

**Tidak ada baris agregat, baris subtotal, atau baris ringkasan di dalam `fact_pelanggan`.** Setiap baris adalah satu pelanggan, jadi setiap measure di bawah membaca tepat satu grain — tidak perlu guard atau filter level. Dimensi hanya menyaring, tidak pernah menambah baris:

Relasi: `dim_kontrak[kontrak_id]` 1—* `fact_pelanggan[kontrak_id]`, `dim_internet[internet_id]` 1—* `fact_pelanggan[internet_id]`, `dim_pembayaran[pembayaran_id]` 1—* `fact_pelanggan[pembayaran_id]`. Semua relasi satu arah (single direction) dari dimensi ke fakta.

Catatan pembersihan: data mentah berisi 7.043 baris. Sebanyak 11 baris memiliki `TotalCharges` kosong (string kosong), semuanya `tenure_bulan` 0 dan tidak churn — pelanggan tanpa riwayat tagihan. Sama seperti analisis asli (`scripts/load_to_sqlite.py`), ke-11 baris itu **dihapus, bukan diisi**, sehingga kit ini berisi **7.032 pelanggan**. Jumlah churn tidak berubah (1.869). Angka 7.043 adalah jumlah baris mentah, bukan jumlah pelanggan pada kit ini.

Kolom kunci pada fakta: `churn_flag` bernilai 1 untuk churn dan 0 untuk bertahan; `churn_label` adalah teks aslinya (`Yes` / `No`). Semua measure memakai `churn_flag`.

## Verifikasi angka (dihitung ulang dari CSV kit ini)

| Ukuran | Nilai yang harus tampil |
|---|---|
| Total pelanggan | 7.032 |
| Total churn | 1.869 |
| Persen churn keseluruhan | 26,6% (1.869 dari 7.032) |
| Persen churn kontrak Month-to-month | 42,7% (1.655 dari 3.875) |
| Persen churn kontrak One year | 11,3% (166 dari 1.472) |
| Persen churn kontrak Two year | 2,8% (48 dari 1.685; nilai eksak 2,85%) |
| Persen churn Fiber optic | 41,9% (1.297 dari 3.096) |
| Persen churn DSL | 19,0% (459 dari 2.416) |
| Persen churn tanpa internet | 7,4% (113 dari 1.520) |
| Persen churn Electronic check | 45,3% (1.071 dari 2.365) |
| Persen churn kelompok tenure 0-12 bulan | 47,7% (1.037 dari 2.175) |
| Segmen kombinasi Fiber optic + Month-to-month | 54,6% (1.162 dari 2.128) |
| Rata-rata tenure semua pelanggan | 32,42 bulan |
| Rata-rata tenure pelanggan churn | 17,98 bulan |
| Rata-rata tenure pelanggan bertahan | 37,65 bulan |
| Rata-rata tagihan bulanan semua pelanggan | USD 64,80 |
| Rata-rata tagihan bulanan pelanggan churn | USD 74,44 |
| Rata-rata tagihan bulanan pelanggan bertahan | USD 61,31 |
| Total pendapatan bulanan | USD 455.661,00 |
| Revenue At Risk (tagihan bulanan pelanggan churn) | USD 139.130,85 per bulan |
| Persen Revenue At Risk dari total pendapatan bulanan | 30,5% |

Visual keseluruhan WAJIB menampilkan angka di atas. Jika berbeda, cek: visual memakai `fact_pelanggan` (bukan CSV mentah di `data/raw/` yang masih berisi 7.043 baris), dan tidak ada filter halaman atau slicer yang masih aktif.

## Measures — INTI (tabel `fact_pelanggan`)

```dax
Total Pelanggan =
COUNTROWS ( fact_pelanggan )

Total Churn =
SUM ( fact_pelanggan[churn_flag] )

Total Bertahan =
[Total Pelanggan] - [Total Churn]

Persen Churn =
DIVIDE ( [Total Churn], [Total Pelanggan] )

Rata-rata Tenure =
AVERAGE ( fact_pelanggan[tenure_bulan] )

Rata-rata Tagihan Bulanan =
AVERAGE ( fact_pelanggan[monthly_charges] )

Rata-rata Total Tagihan =
AVERAGE ( fact_pelanggan[total_charges] )

Total Pendapatan Bulanan =
SUM ( fact_pelanggan[monthly_charges] )
```

## Measures — PENDAPATAN DAN RISIKO (tabel `fact_pelanggan`)

```dax
Revenue At Risk =
CALCULATE (
    SUM ( fact_pelanggan[monthly_charges] ),
    fact_pelanggan[churn_flag] = 1
)

Persen Revenue At Risk =
DIVIDE ( [Revenue At Risk], [Total Pendapatan Bulanan] )

Pendapatan Pelanggan Bertahan =
CALCULATE (
    SUM ( fact_pelanggan[monthly_charges] ),
    fact_pelanggan[churn_flag] = 0
)

Rata-rata Tagihan Pelanggan Churn =
CALCULATE (
    AVERAGE ( fact_pelanggan[monthly_charges] ),
    fact_pelanggan[churn_flag] = 1
)

Rata-rata Tagihan Pelanggan Bertahan =
CALCULATE (
    AVERAGE ( fact_pelanggan[monthly_charges] ),
    fact_pelanggan[churn_flag] = 0
)

Rata-rata Tenure Pelanggan Churn =
CALCULATE (
    AVERAGE ( fact_pelanggan[tenure_bulan] ),
    fact_pelanggan[churn_flag] = 1
)

Rata-rata Tenure Pelanggan Bertahan =
CALCULATE (
    AVERAGE ( fact_pelanggan[tenure_bulan] ),
    fact_pelanggan[churn_flag] = 0
)
```

## Measures — SEGMEN ACUAN (tabel `fact_pelanggan`)

Measure di bawah ini mengunci satu segmen untuk kartu verifikasi. Untuk visual per segmen biasa (bar chart per kontrak, per internet, per pembayaran, per kelompok tenure), **jangan** pakai measure ini: cukup letakkan kolom dimensi pada sumbu visual dan pakai `Persen Churn` biasa — konteks filter dari dimensi yang membedakannya.

```dax
Persen Churn Kontrak Bulanan =
CALCULATE (
    [Persen Churn],
    dim_kontrak[kontrak] = "Month-to-month"
)

Persen Churn Kontrak Dua Tahun =
CALCULATE (
    [Persen Churn],
    dim_kontrak[kontrak] = "Two year"
)

Persen Churn Fiber Optic =
CALCULATE (
    [Persen Churn],
    dim_internet[layanan_internet] = "Fiber optic"
)

Persen Churn Cek Elektronik =
CALCULATE (
    [Persen Churn],
    dim_pembayaran[metode_pembayaran] = "Electronic check"
)

Persen Churn Tenure Awal =
CALCULATE (
    [Persen Churn],
    fact_pelanggan[kelompok_tenure] = "0-12 bulan"
)
```

## Aturan pakai

1. Satu-satunya tabel fakta adalah `fact_pelanggan`. Semua measure membaca tabel itu; dimensi hanya dipakai sebagai sumbu, legend, atau slicer.
2. Atur format `Persen Churn`, `Persen Revenue At Risk`, dan semua measure segmen acuan sebagai **Percentage dengan 1 angka desimal** di Power BI. Measure sengaja mengembalikan rasio (contoh 0,266), bukan angka yang sudah dikali 100, supaya format persen bawaan tampil benar.
3. Atur format measure uang (`Rata-rata Tagihan Bulanan`, `Total Pendapatan Bulanan`, `Revenue At Risk`, dan turunannya) sebagai Currency USD dengan 2 angka desimal.
4. `Persen Churn` bersifat peka konteks: nilai yang sama berubah mengikuti slicer atau sumbu yang aktif. Kartu KPI keseluruhan di Halaman 1 tidak boleh terkena slicer segmen apa pun selain yang memang dirancang untuk halaman itu.
5. Jangan menjumlahkan `total_charges` untuk membandingkan pendapatan antarperiode: kolom itu akumulasi seumur berlangganan tiap pelanggan, bukan pendapatan satu bulan. Pendapatan bulanan selalu dari `monthly_charges`.
6. Uji tiap measure tanpa filter apa pun dulu sebelum membangun halaman penuh: tanpa filter, `Total Pelanggan` harus 7.032, `Total Churn` 1.869, `Persen Churn` 26,6%, dan `Revenue At Risk` USD 139.130,85.
