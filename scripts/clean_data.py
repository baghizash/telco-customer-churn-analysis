"""
Membuat dataset bersih Telco Customer Churn sebagai CSV mandiri.

Sumber : data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv  (7.043 baris x 21 kolom)
Keluaran: data/clean/telco_customer_churn_clean.csv      (7.032 baris x 21 kolom)

Aturan pembersihan (sama persis dengan scripts/load_to_sqlite.py dan
powerbi/build_kit_csv.py, yang menjadi basis analisis/SQL/Power BI):
1. Nama kolom dibersihkan dari spasi di tepi (strip). Tidak ada kolom yang
   berubah nama pada file ini: 0 kolom terdampak.
2. Kolom TotalCharges tiba sebagai teks. Tepat 11 sel berisi satu spasi
   (" ") sehingga tidak terdeteksi sebagai missing oleh isna() biasa.
   TotalCharges dikonversi ke angka dengan pd.to_numeric(errors="coerce");
   11 sel itu menjadi NaN.
3. Ke-11 baris dengan TotalCharges kosong dihapus (bukan diimputasi).
   Semuanya tenure = 0 dan Churn = "No": pelanggan tanpa riwayat tagihan.
   Jumlah churn (1.869) tidak berubah; total berubah 7.043 -> 7.032.
4. Pemeriksaan lain yang dijalankan dan hasilnya nol baris terdampak:
   tidak ada baris duplikat persis (0), customerID unik (0 duplikat),
   tidak ada missing value di 20 kolom lain (0).

Tidak ada kolom turunan yang ditambahkan pada file bersih ini. Kolom
turunan analisis (kelompok_tenure, churn_flag, dan ID dimensi) hanya dibuat
di hilir, di powerbi/fact_pelanggan.csv oleh powerbi/build_kit_csv.py.
Urutan baris dipertahankan persis seperti urutan pada file mentah setelah
penghapusan 11 baris, sama seperti tabel "customers" di SQLite.

Cara pakai:
    ~/workspace/mienv/bin/python scripts/clean_data.py
"""
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
OUT_PATH = BASE_DIR / "data" / "clean" / "telco_customer_churn_clean.csv"


def main() -> None:
    df = pd.read_csv(RAW_PATH)
    n_raw, n_cols_raw = df.shape

    df.columns = df.columns.str.strip()

    n_duplicate_rows = int(df.duplicated().sum())
    n_duplicate_ids = int(df["customerID"].duplicated().sum())
    n_missing_other = int(
        df.drop(columns=["TotalCharges"]).isna().sum().sum()
    )

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    blank = df[df["TotalCharges"].isna()]
    n_blank = int(len(blank))
    assert (blank["tenure"] == 0).all(), "Baris kosong bukan tenure 0!"
    assert (blank["Churn"] == "No").all(), "Baris kosong bukan Churn No!"

    clean = df.dropna(subset=["TotalCharges"]).copy()
    assert clean["customerID"].is_unique, "customerID tidak unik!"
    assert int(clean.isna().sum().sum()) == 0, "Masih ada missing value!"

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(OUT_PATH, index=False)

    churn = int((clean["Churn"] == "Yes").sum())
    rate = churn / len(clean) * 100
    print(f"Baris mentah                 : {n_raw} x {n_cols_raw} kolom")
    print(f"Baris duplikat persis        : {n_duplicate_rows}")
    print(f"customerID duplikat          : {n_duplicate_ids}")
    print(f"Missing di kolom lain        : {n_missing_other}")
    print(f"TotalCharges kosong dihapus  : {n_blank}")
    print(f"Baris bersih                 : {len(clean)} x {clean.shape[1]} kolom")
    print(f"Churn                        : {churn} ({rate:.1f}%)")
    print(f"Tersimpan di                 : {OUT_PATH}")
    assert len(clean) == 7032, f"Diharapkan 7032, dapat {len(clean)}"
    assert churn == 1869, f"Diharapkan 1869 churn, dapat {churn}"
    print("OK: verifikasi 7.032 baris dan churn 26,6% berhasil.")


if __name__ == "__main__":
    main()
