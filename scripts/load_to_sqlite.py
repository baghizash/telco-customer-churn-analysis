"""
Memuat dataset Telco Customer Churn (IBM sample, publik via Kaggle) ke SQLite.

Sumber CSV : data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv
Tujuan DB  : data/telco_churn.db, tabel "customers"

PEMBERSIHAN (keputusan bisnis, terdokumentasi):
- Kolom TotalCharges tiba sebagai TEKS, bukan angka. Di dalamnya tersembunyi
  11 nilai kosong (string kosong) yang tidak terdeteksi df.isna().
  Ke-11 baris itu semuanya tenure = 0, Churn = No: pelanggan yang berhenti
  sebelum tagihan pertama terbit, jadi tidak punya riwayat tagihan sama sekali.
  Keputusan: 11 baris tersebut DIHAPUS, bukan diisi (imputasi median/0 akan
  mengarang nilai untuk pelanggan tanpa riwayat tagihan).
- Hasil: 7.043 baris mentah -> 7.032 baris bersih di database.

Cara pakai:
    python scripts/load_to_sqlite.py
"""
import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
DB_PATH = BASE_DIR / "data" / "telco_churn.db"

INDEXES = {
    "idx_customers_churn": ["Churn"],
    "idx_customers_contract": ["Contract"],
    "idx_customers_internet": ["InternetService"],
    "idx_customers_payment": ["PaymentMethod"],
    "idx_customers_tenure": ["tenure"],
    "idx_customers_monthly": ["MonthlyCharges"],
    "idx_customers_senior": ["SeniorCitizen"],
    "idx_customers_techsupport": ["TechSupport"],
}


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip()

    # TotalCharges: teks -> angka; string kosong menjadi NaN
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    n_blank = int(df["TotalCharges"].isna().sum())
    blank_rows = df[df["TotalCharges"].isna()]
    assert (blank_rows["tenure"] == 0).all(), "Baris kosong bukan tenure 0!"
    assert (blank_rows["Churn"] == "No").all(), "Baris kosong bukan Churn No!"

    df_clean = df.dropna(subset=["TotalCharges"]).copy()

    if DB_PATH.exists():
        DB_PATH.unlink()

    con = sqlite3.connect(DB_PATH)
    df_clean.to_sql("customers", con, index=False)

    cur = con.cursor()
    for name, cols in INDEXES.items():
        cur.execute(
            f"CREATE INDEX {name} ON customers ({', '.join(f'\"{c}\"' for c in cols)})"
        )
    con.commit()

    n = cur.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    con.close()

    print(f"Baris di CSV  : {len(df)}")
    print(f"Nilai kosong tersembunyi di TotalCharges: {n_blank} (semua tenure 0, Churn No)")
    print(f"Baris bersih : {len(df_clean)}")
    print(f"Baris di DB   : {n}")
    print(f"Tersimpan di  : {DB_PATH}")
    assert n == 7032, f"Jumlah baris tidak sesuai! Diharapkan 7032, dapat {n}"
    print("OK: verifikasi 7032 baris berhasil.")


if __name__ == "__main__":
    main()
