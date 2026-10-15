-- ============================================================
-- ANALISIS TELCO CUSTOMER CHURN  (Customer Retention Analytics)
-- Tabel: customers  |  Kolom target: Churn ('Yes' = pelanggan berhenti)
-- Churn rate = SUM(Churn='Yes') / COUNT(*)
-- Catatan: tabel berisi 7.032 baris bersih (11 baris tenure 0 tanpa
-- TotalCharges sudah dihapus di load_to_sqlite.py, semua Churn = No).
-- ============================================================

-- a. CHURN RATE KESELURUHAN
-- Berapa banyak pelanggan yang churn dan berapa persen dari total.
SELECT
    COUNT(*)                       AS total_pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers;

-- b. CHURN PER JENIS KONTRAK
-- Kontrak mana yang tingkat churnnya paling tinggi.
SELECT
    Contract,
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
GROUP BY Contract
ORDER BY rate_persen DESC;

-- c. CHURN PER BAND MASA BERLANGGANAN (tenure, bulan)
-- Band: 0-12, 13-24, 25-48, 49-72 bulan.
SELECT
    CASE
        WHEN tenure <= 12  THEN '0-12'
        WHEN tenure <= 24  THEN '13-24'
        WHEN tenure <= 48  THEN '25-48'
        ELSE '49-72'
    END AS band_tenure,
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
GROUP BY band_tenure
ORDER BY MIN(tenure);

-- d. CHURN PER LAYANAN INTERNET
-- DSL vs Fiber optic vs tanpa internet.
SELECT
    InternetService,
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
GROUP BY InternetService
ORDER BY rate_persen DESC;

-- e. CHURN PER METODE PEMBAYARAN
-- Metode pembayaran mana yang churnnya paling tinggi.
SELECT
    PaymentMethod,
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
GROUP BY PaymentMethod
ORDER BY rate_persen DESC;

-- f. CHURN PER BAND TAGIHAN BULANAN (MonthlyCharges, USD)
-- Band: <=35, 36-70, 71-90, >90.
SELECT
    CASE
        WHEN MonthlyCharges <= 35  THEN '<= 35'
        WHEN MonthlyCharges <= 70  THEN '36-70'
        WHEN MonthlyCharges <= 90  THEN '71-90'
        ELSE '> 90'
    END AS band_tagihan,
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
GROUP BY band_tagihan
ORDER BY MIN(MonthlyCharges);

-- g. PENDAPATAN BULANAN YANG HILANG AKIBAT CHURN
-- Total MonthlyCharges pelanggan churn vs total seluruh pelanggan.
SELECT
    SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END) AS pendapatan_hilang_bulanan,
    SUM(MonthlyCharges)                                          AS pendapatan_total_bulanan,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN MonthlyCharges ELSE 0 END)
          / SUM(MonthlyCharges), 1)                              AS persen_pendapatan_hilang
FROM customers;

-- h. RATA-RATA TAGIHAN DAN MASA BERLANGGANAN: CHURN VS BERTAHAN
SELECT
    Churn,
    COUNT(*)                       AS pelanggan,
    ROUND(AVG(MonthlyCharges), 2)  AS rata_tagihan_bulanan,
    ROUND(AVG(tenure), 1)          AS rata_tenure_bulan
FROM customers
GROUP BY Churn;

-- i1. TECH SUPPORT VS CHURN
-- Pelanggan internet tanpa TechSupport vs dengan TechSupport.
SELECT
    TechSupport,
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
GROUP BY TechSupport;

-- i2. ONLINE SECURITY VS CHURN
SELECT
    OnlineSecurity,
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
GROUP BY OnlineSecurity;

-- i3. LAYANAN TAMBAHAN LAIN VS CHURN
-- OnlineBackup, DeviceProtection, StreamingTV, StreamingMovies.
SELECT
    OnlineBackup,
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
GROUP BY OnlineBackup;

SELECT
    DeviceProtection,
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
GROUP BY DeviceProtection;

SELECT
    StreamingTV,
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
GROUP BY StreamingTV;

SELECT
    StreamingMovies,
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
GROUP BY StreamingMovies;

-- j1. SENIOR CITIZEN VS CHURN
SELECT
    SeniorCitizen,
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
GROUP BY SeniorCitizen;

-- j2. PARTNER VS CHURN
SELECT
    Partner,
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
GROUP BY Partner;

-- j3. DEPENDENTS VS CHURN
SELECT
    Dependents,
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
GROUP BY Dependents;

-- j4. GENDER VS CHURN (pembanding: apakah gender berpengaruh?)
SELECT
    gender,
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
GROUP BY gender;

-- j5. PAPERLESS BILLING VS CHURN
SELECT
    PaperlessBilling,
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
GROUP BY PaperlessBilling;

-- k1. KOMBINASI: KONTRAK BULANAN + PELANGGAN BARU (tenure <= 12)
-- Segmen gabungan paling rawan.
SELECT
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
WHERE Contract = 'Month-to-month' AND tenure <= 12;

-- k2. KOMBINASI: FIBER OPTIC + KONTRAK BULANAN
SELECT
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
WHERE InternetService = 'Fiber optic' AND Contract = 'Month-to-month';

-- k3. CHURN PER BAND TOTAL CHARGES (akumulasi tagihan, USD)
-- Band: <=500, 501-2000, 2001-5000, >5000.
SELECT
    CASE
        WHEN TotalCharges <= 500   THEN '<= 500'
        WHEN TotalCharges <= 2000  THEN '501-2000'
        WHEN TotalCharges <= 5000  THEN '2001-5000'
        ELSE '> 5000'
    END AS band_total_tagihan,
    COUNT(*)                       AS pelanggan,
    SUM(Churn = 'Yes')             AS churn,
    ROUND(100.0 * SUM(Churn = 'Yes') / COUNT(*), 1) AS rate_persen
FROM customers
GROUP BY band_total_tagihan
ORDER BY MIN(TotalCharges);
