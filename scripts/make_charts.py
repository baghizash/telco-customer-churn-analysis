"""
Menghasilkan 12 chart PNG untuk analisis Telco Customer Churn.
Sumber data : data/telco_churn.db (tabel customers, 7.032 baris bersih)
Keluaran    : charts/*.png
Cara pakai  : python scripts/make_charts.py
"""
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

# ---- palet warna konsisten ----
TEAL = "#1F7A8C"     # utama
TEAL_DK = "#14505C"  # aksen gelap
ORANGE = "#E86A33"   # sorotan risiko tinggi
GREY = "#B0BEC5"     # netral
BG = "#F7F9FA"
TXT = "#2B3A42"

BASE_DIR = Path(__file__).resolve().parent.parent
DB = BASE_DIR / "data" / "telco_churn.db"
OUT = BASE_DIR / "charts"
OUT.mkdir(exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "text.color": TXT,
    "axes.labelcolor": TXT,
    "xtick.color": TXT,
    "ytick.color": TXT,
})


def query(sql):
    with sqlite3.connect(DB) as con:
        return pd.read_sql_query(sql, con)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("tulis:", name)


def bar(ax, labels, values, title, xlabel, ylabel="Churn rate (%)",
        colors=None, annotate=True, fmt="{:.1f}%"):
    colors = colors or [TEAL] * len(labels)
    bars = ax.bar(labels, values, color=colors, edgecolor="white", width=0.62)
    ax.set_title(title, pad=14)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, max(values) * 1.22 if max(values) else 1)
    ax.spines[["top", "right"]].set_visible(False)
    if annotate:
        for b, v in zip(bars, values):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.6,
                    fmt.format(v), ha="center", va="bottom", fontsize=10,
                    fontweight="bold")


def rate_q(col, where=""):
    return f"""SELECT {col}, ROUND(100.0*SUM(Churn='Yes')/COUNT(*),1) rate,
                     COUNT(*) n FROM customers {where}
              GROUP BY {col}"""


# ---------- 01. churn keseluruhan (donut) ----------
df = query("""SELECT COUNT(*) total, SUM(Churn='Yes') churn FROM customers""")
total, churn = int(df.loc[0, "total"]), int(df.loc[0, "churn"])
fig, ax = plt.subplots(figsize=(6, 6))
ax.pie([churn, total - churn], colors=[ORANGE, TEAL],
       startangle=90, wedgeprops=dict(width=0.42, edgecolor="white"))
ax.text(0, 0.08, f"{100*churn/total:.1f}%", ha="center", fontsize=26, fontweight="bold")
ax.text(0, -0.18, "churn", ha="center", fontsize=12)
ax.set_title(f"Tingkat Churn Keseluruhan\n{churn} dari {total} pelanggan churn", pad=18)
ax.legend([f"Churn: {churn}", f"Bertahan: {total-churn}"], loc="lower center",
          bbox_to_anchor=(0.5, -0.14), ncol=2, frameon=False)
save(fig, "01_churn_overall.png")

# ---------- 02. churn per kontrak ----------
df = query("""SELECT Contract, ROUND(100.0*SUM(Churn='Yes')/COUNT(*),1) rate,
                     COUNT(*) n FROM customers GROUP BY Contract
              ORDER BY rate DESC""")
labels = {"Month-to-month": "Bulanan", "One year": "1 tahun", "Two year": "2 tahun"}
fig, ax = plt.subplots(figsize=(7.5, 4.6))
bar(ax, [labels.get(x, x) for x in df["Contract"]], df["rate"],
    "Churn per Jenis Kontrak", "Jenis kontrak",
    colors=[ORANGE if r == df["rate"].max() else TEAL for r in df["rate"]])
for t, n in zip(ax.get_xticklabels(), df["n"]):
    t.set_text(f"{t.get_text()}\n(n={n})")
save(fig, "02_churn_contract.png")

# ---------- 03. churn per band tenure ----------
df = query("""SELECT CASE WHEN tenure<=12 THEN '0-12' WHEN tenure<=24 THEN '13-24'
        WHEN tenure<=48 THEN '25-48' ELSE '49-72' END band,
        ROUND(100.0*SUM(Churn='Yes')/COUNT(*),1) rate, COUNT(*) n
        FROM customers GROUP BY band ORDER BY MIN(tenure)""")
fig, ax = plt.subplots(figsize=(7.5, 4.6))
bar(ax, df["band"], df["rate"], "Churn per Masa Berlangganan (tenure)",
    "Masa berlangganan (bulan)",
    colors=[ORANGE if r == df["rate"].max() else TEAL for r in df["rate"]])
save(fig, "03_churn_tenure.png")

# ---------- 04. churn per layanan internet ----------
df = query("""SELECT InternetService, ROUND(100.0*SUM(Churn='Yes')/COUNT(*),1) rate,
                     COUNT(*) n FROM customers GROUP BY InternetService
              ORDER BY rate DESC""")
labels = {"Fiber optic": "Fiber optic", "DSL": "DSL", "No": "Tanpa internet"}
fig, ax = plt.subplots(figsize=(7.5, 4.6))
bar(ax, [labels.get(x, x) for x in df["InternetService"]], df["rate"],
    "Churn per Layanan Internet", "Layanan internet",
    colors=[ORANGE if r == df["rate"].max() else TEAL for r in df["rate"]])
save(fig, "04_churn_internet.png")

# ---------- 05. churn per metode pembayaran ----------
df = query("""SELECT PaymentMethod, ROUND(100.0*SUM(Churn='Yes')/COUNT(*),1) rate,
                     COUNT(*) n FROM customers GROUP BY PaymentMethod
              ORDER BY rate""")
labels = {"Electronic check": "Cek elektronik", "Mailed check": "Cek pos",
          "Bank transfer (automatic)": "Transfer bank (otomatis)",
          "Credit card (automatic)": "Kartu kredit (otomatis)"}
fig, ax = plt.subplots(figsize=(9, 5.2))
colors = [ORANGE if r == df["rate"].max() else TEAL for r in df["rate"]]
bars = ax.barh([labels.get(x, x) for x in df["PaymentMethod"]], df["rate"],
               color=colors, edgecolor="white")
ax.set_title("Churn per Metode Pembayaran (diurutkan, dengan jumlah pelanggan)", pad=14)
ax.set_xlabel("Churn rate (%)")
ax.spines[["top", "right"]].set_visible(False)
for b, v, n in zip(bars, df["rate"], df["n"]):
    ax.text(v + 0.6, b.get_y() + b.get_height() / 2, f"{v:.1f}%  (n={n})",
            va="center", fontsize=9.5)
ax.set_xlim(0, df["rate"].max() * 1.5)
save(fig, "05_churn_payment.png")

# ---------- 06. churn per band tagihan bulanan ----------
df = query("""SELECT CASE WHEN MonthlyCharges<=35 THEN '<= 35'
        WHEN MonthlyCharges<=70 THEN '36-70'
        WHEN MonthlyCharges<=90 THEN '71-90' ELSE '> 90' END band,
        ROUND(100.0*SUM(Churn='Yes')/COUNT(*),1) rate, COUNT(*) n
        FROM customers GROUP BY band ORDER BY MIN(MonthlyCharges)""")
fig, ax = plt.subplots(figsize=(7.5, 4.6))
bar(ax, df["band"], df["rate"], "Churn per Band Tagihan Bulanan (USD)",
    "Tagihan bulanan (USD)",
    colors=[ORANGE if r == df["rate"].max() else TEAL for r in df["rate"]])
save(fig, "06_churn_monthly_charges.png")

# ---------- 07. tech support + online security ----------
fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
for ax, col, title in zip(axes,
        ["TechSupport", "OnlineSecurity"],
        ["Churn per Tech Support", "Churn per Online Security"]):
    d = query(f"""SELECT {col}, ROUND(100.0*SUM(Churn='Yes')/COUNT(*),1) rate
                 FROM customers GROUP BY {col}""")
    d = d[d[col] != "No internet service"]
    labels2 = {"No": "Tidak pakai", "Yes": "Pakai"}
    bar(ax, [labels2.get(x, x) for x in d[col]], d["rate"], title, col,
        colors=[ORANGE if r == d["rate"].max() else TEAL for r in d["rate"]])
fig.suptitle("Layanan Dukungan: Pelanggan Tanpa Tech Support / Online Security Jauh Lebih Rentan Churn",
             fontsize=13, fontweight="bold", y=1.04)
save(fig, "07_churn_support.png")

# ---------- 08. demografi: senior, partner, dependents ----------
fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), sharey=True)
specs = [("SeniorCitizen", "Senior Citizen",
          {0: "Bukan senior", 1: "Senior"}),
         ("Partner", "Pasangan",
          {"No": "Tidak punya", "Yes": "Punya"}),
         ("Dependents", "Tanggungan",
          {"No": "Tidak punya", "Yes": "Punya"})]
for ax, col, title, lab in zip(axes, [s[0] for s in specs], [s[1] for s in specs],
                               [s[2] for s in specs]):
    d = query(f"""SELECT {col}, ROUND(100.0*SUM(Churn='Yes')/COUNT(*),1) rate
                 FROM customers GROUP BY {col}""")
    bar(ax, [lab.get(x, x) for x in d[col]], d["rate"], f"Churn per {title}", title,
        colors=[ORANGE if r == d["rate"].max() else TEAL for r in d["rate"]])
    ax.set_ylabel("Churn rate (%)")
fig.suptitle("Churn per Profil Demografi", fontsize=15, fontweight="bold", y=1.03)
save(fig, "08_churn_demografi.png")

# ---------- 09. pendapatan bulanan yang hilang ----------
df = query("""SELECT SUM(CASE WHEN Churn='Yes' THEN MonthlyCharges ELSE 0 END) lost,
                     SUM(MonthlyCharges) total FROM customers""")
lost, total = float(df.loc[0, "lost"]), float(df.loc[0, "total"])
fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
bars = axes[0].bar(["Bertahan", "Churn (hilang)"],
                   [total - lost, lost], color=[TEAL, ORANGE],
                   edgecolor="white", width=0.55)
axes[0].set_title("Pendapatan Bulanan: Bertahan vs Hilang karena Churn", pad=14)
axes[0].set_ylabel("USD per bulan")
axes[0].spines[["top", "right"]].set_visible(False)
for b, v in zip(bars, [total - lost, lost]):
    axes[0].text(b.get_x() + b.get_width() / 2, v + 8000,
                 f"${v:,.0f}", ha="center", fontsize=11, fontweight="bold")
axes[0].set_ylim(0, total * 1.18)

d2 = query("""SELECT Churn, ROUND(AVG(MonthlyCharges),2) avg_mc,
                     ROUND(AVG(tenure),1) avg_tenure FROM customers GROUP BY Churn""")
d2 = d2.set_index("Churn").loc[["No", "Yes"]].reset_index()
axes[1].bar(["Bertahan", "Churn"], d2["avg_mc"], color=[TEAL, ORANGE],
            edgecolor="white", width=0.55)
axes[1].set_title("Rata-rata Tagihan Bulanan: Churn vs Bertahan", pad=14)
axes[1].set_ylabel("USD per bulan")
axes[1].spines[["top", "right"]].set_visible(False)
for b, v in zip(axes[1].patches, d2["avg_mc"]):
    axes[1].text(b.get_x() + b.get_width() / 2, v + 1.5,
                 f"${v:.2f}", ha="center", fontsize=11, fontweight="bold")
axes[1].set_ylim(0, d2["avg_mc"].max() * 1.18)
fig.suptitle("Pendapatan yang Hilang: $139.131 per Bulan (30,5% dari Total)",
             fontsize=14, fontweight="bold", y=1.03)
save(fig, "09_churn_revenue.png")

# ---------- 10. segmen kombinasi ----------
segs = [
    ("Fiber optic +\nkontrak bulanan",
     "InternetService='Fiber optic' AND Contract='Month-to-month'"),
    ("Kontrak bulanan +\nbaru (<=12 bln)",
     "Contract='Month-to-month' AND tenure<=12"),
    ("Kontrak bulanan\n(semua)",
     "Contract='Month-to-month'"),
    ("Fiber optic\n(semua)",
     "InternetService='Fiber optic'"),
    ("Baru <= 12 bln\n(semua)",
     "tenure<=12"),
]
rows = []
for label, cond in segs:
    d = query(f"""SELECT ROUND(100.0*SUM(Churn='Yes')/COUNT(*),1) rate,
                         COUNT(*) n FROM customers WHERE {cond}""")
    rows.append((label, float(d.loc[0, "rate"]), int(d.loc[0, "n"])))
labels, rates, ns = zip(*rows)
fig, ax = plt.subplots(figsize=(9, 5.2))
bars = ax.barh(list(labels), list(rates),
               color=[ORANGE if r >= 50 else TEAL for r in rates], edgecolor="white")
ax.set_title("Churn pada Segmen Kombinasi Paling Rawan", pad=14)
ax.set_xlabel("Churn rate (%)")
ax.spines[["top", "right"]].set_visible(False)
for b, v, n in zip(bars, rates, ns):
    ax.text(v + 0.8, b.get_y() + b.get_height() / 2, f"{v:.1f}%  (n={n})",
            va="center", fontsize=10)
ax.set_xlim(0, max(rates) * 1.5)
save(fig, "10_churn_combo.png")

# ---------- 11. layanan tambahan lain ----------
fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), sharey=True)
for ax, col, title in zip(axes, ["OnlineBackup", "DeviceProtection", "StreamingTV"],
                          ["Online Backup", "Device Protection", "Streaming TV"]):
    d = query(f"""SELECT {col}, ROUND(100.0*SUM(Churn='Yes')/COUNT(*),1) rate
                 FROM customers GROUP BY {col}""")
    d = d[d[col] != "No internet service"]
    bar(ax, ["Tidak pakai" if x == "No" else "Pakai" for x in d[col]], d["rate"],
        f"Churn per {title}", title,
        colors=[ORANGE if r == d["rate"].max() else TEAL for r in d["rate"]])
    ax.set_ylabel("Churn rate (%)")
fig.suptitle("Layanan Tambahan Lain: Pola Serupa, Efek Lebih Kecil",
             fontsize=14, fontweight="bold", y=1.03)
save(fig, "11_churn_services.png")

# ---------- 12. total charges band + paperless billing ----------
fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
d = query("""SELECT CASE WHEN TotalCharges<=500 THEN '<= 500'
        WHEN TotalCharges<=2000 THEN '501-2000'
        WHEN TotalCharges<=5000 THEN '2001-5000' ELSE '> 5000' END band,
        ROUND(100.0*SUM(Churn='Yes')/COUNT(*),1) rate
        FROM customers GROUP BY band ORDER BY MIN(TotalCharges)""")
bar(axes[0], d["band"], d["rate"], "Churn per Band Total Tagihan (USD)",
    "Total tagihan akumulasi (USD)",
    colors=[ORANGE if r == d["rate"].max() else TEAL for r in d["rate"]])
d = query("""SELECT PaperlessBilling, ROUND(100.0*SUM(Churn='Yes')/COUNT(*),1) rate
             FROM customers GROUP BY PaperlessBilling""")
bar(axes[1], ["Tidak paperless" if x == "No" else "Paperless" for x in d["PaperlessBilling"]],
    d["rate"], "Churn per Paperless Billing", "Paperless billing",
    colors=[ORANGE if r == d["rate"].max() else TEAL for r in d["rate"]])
fig.suptitle("Akumulasi Tagihan dan Paperless Billing",
             fontsize=14, fontweight="bold", y=1.03)
save(fig, "12_churn_totalcharges_paperless.png")

print("Selesai: 12 chart.")
