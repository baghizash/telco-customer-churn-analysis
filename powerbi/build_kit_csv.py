"""
Membangun CSV kit Power BI dari data mentah Telco Customer Churn.

Sumber : ../data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv
Keluaran (di folder ini):
    fact_pelanggan.csv  - grain: 1 baris per pelanggan bersih
    dim_kontrak.csv     - kontrak_id, kontrak
    dim_internet.csv    - internet_id, layanan_internet
    dim_pembayaran.csv  - pembayaran_id, metode_pembayaran

PEMBERSIHAN (sama persis dengan scripts/load_to_sqlite.py):
- TotalCharges tiba sebagai teks; 11 nilai kosong (string kosong) di dalamnya
  semuanya tenure = 0 dan Churn = No (pelanggan tanpa riwayat tagihan).
- Ke-11 baris itu DIHAPUS, bukan diisi, sehingga 7.043 baris mentah menjadi
  7.032 baris bersih. Jumlah churn (1.869) tidak berubah.

ID pengganti (surrogate) dibuat deterministik lewat pemetaan eksplisit di
bawah ini, dan pemetaan yang sama dipakai untuk fact dan semua dim, jadi
relasi di Power BI selalu konsisten walau script dijalankan ulang.

Cara pakai:
    ~/workspace/mienv/bin/python powerbi/build_kit_csv.py
    (atau python powerbi/build_kit_csv.py bila pandas sudah terpasang)
"""
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
KIT_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"

# Pemetaan deterministik: urutan mengikuti durasi / abjad, bukan urutan
# kemunculan di file, supaya hasilnya tidak berubah bila file diurut ulang.
KONTRAK_ID = {
    "Month-to-month": "K01",
    "One year": "K02",
    "Two year": "K03",
}
INTERNET_ID = {
    "DSL": "I01",
    "Fiber optic": "I02",
    "No": "I03",
}
PEMBAYARAN_ID = {
    "Bank transfer (automatic)": "P01",
    "Credit card (automatic)": "P02",
    "Electronic check": "P03",
    "Mailed check": "P04",
}


def tenure_kelompok(tenure: int) -> str:
    """Kelompok masa berlangganan yang sama dengan analisis asli."""
    if tenure <= 12:
        return "0-12 bulan"
    if tenure <= 24:
        return "13-24 bulan"
    if tenure <= 48:
        return "25-48 bulan"
    return "49-72 bulan"


def main() -> None:
    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip()

    # TotalCharges: teks ke angka; string kosong menjadi NaN
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    blank = df[df["TotalCharges"].isna()]
    assert (blank["tenure"] == 0).all(), "Baris kosong bukan tenure 0!"
    assert (blank["Churn"] == "No").all(), "Baris kosong bukan Churn No!"
    n_blank = int(len(blank))

    clean = df.dropna(subset=["TotalCharges"]).copy()
    assert clean["customerID"].is_unique, "customerID tidak unik!"

    fact = pd.DataFrame(
        {
            "customer_id": clean["customerID"],
            "gender": clean["gender"],
            "senior_citizen": clean["SeniorCitizen"].astype(int),
            "partner": clean["Partner"],
            "dependents": clean["Dependents"],
            "tenure_bulan": clean["tenure"].astype(int),
            "kelompok_tenure": clean["tenure"].astype(int).map(tenure_kelompok),
            "phone_service": clean["PhoneService"],
            "multiple_lines": clean["MultipleLines"],
            "kontrak_id": clean["Contract"].map(KONTRAK_ID),
            "internet_id": clean["InternetService"].map(INTERNET_ID),
            "online_security": clean["OnlineSecurity"],
            "online_backup": clean["OnlineBackup"],
            "device_protection": clean["DeviceProtection"],
            "tech_support": clean["TechSupport"],
            "streaming_tv": clean["StreamingTV"],
            "streaming_movies": clean["StreamingMovies"],
            "paperless_billing": clean["PaperlessBilling"],
            "pembayaran_id": clean["PaymentMethod"].map(PEMBAYARAN_ID),
            "monthly_charges": clean["MonthlyCharges"].round(2),
            "total_charges": clean["TotalCharges"].round(2),
            "churn_flag": (clean["Churn"] == "Yes").astype(int),
            "churn_label": clean["Churn"],
        }
    )
    assert fact[["kontrak_id", "internet_id", "pembayaran_id"]].notna().all().all(), (
        "Ada nilai dimensi yang tidak terpetakan!"
    )
    fact = fact.sort_values("customer_id").reset_index(drop=True)

    dim_kontrak = pd.DataFrame(
        {"kontrak_id": list(KONTRAK_ID.values()), "kontrak": list(KONTRAK_ID.keys())}
    )
    dim_internet = pd.DataFrame(
        {
            "internet_id": list(INTERNET_ID.values()),
            "layanan_internet": list(INTERNET_ID.keys()),
        }
    )
    dim_pembayaran = pd.DataFrame(
        {
            "pembayaran_id": list(PEMBAYARAN_ID.values()),
            "metode_pembayaran": list(PEMBAYARAN_ID.keys()),
        }
    )

    fact.to_csv(KIT_DIR / "fact_pelanggan.csv", index=False)
    dim_kontrak.to_csv(KIT_DIR / "dim_kontrak.csv", index=False)
    dim_internet.to_csv(KIT_DIR / "dim_internet.csv", index=False)
    dim_pembayaran.to_csv(KIT_DIR / "dim_pembayaran.csv", index=False)

    total = len(fact)
    churn = int(fact["churn_flag"].sum())
    rev_risk = float(fact.loc[fact["churn_flag"] == 1, "monthly_charges"].sum())
    print(f"Baris mentah            : {len(df)}")
    print(f"Baris kosong TotalCharges dihapus: {n_blank}")
    print(f"Baris fact_pelanggan    : {total}")
    print(f"Total churn             : {churn} ({churn / total * 100:.1f}%)")
    print(f"Revenue at risk         : {rev_risk:.2f} USD per bulan")
    print(f"Tersimpan di            : {KIT_DIR}")
    assert total == 7032, f"Jumlah baris tidak sesuai! Diharapkan 7032, dapat {total}"
    assert churn == 1869, f"Jumlah churn tidak sesuai! Diharapkan 1869, dapat {churn}"
    print("OK: verifikasi 7.032 baris dan 1.869 churn berhasil.")


if __name__ == "__main__":
    main()
