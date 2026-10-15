#!/usr/bin/env python3
"""Build Portofolio-Analisis-Telco-Churn.pptx (16:9, 10 slides, ID).
Style mirrors build_ppt.py from the HR Attrition project."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn

NAVY = RGBColor(0x1E, 0x3A, 0x8A)
TEAL = RGBColor(0x0D, 0x94, 0x88)
DARK = RGBColor(0x1F, 0x29, 0x37)
GRAY = RGBColor(0x6B, 0x72, 0x80)
LIGHTBLUE = RGBColor(0x93, 0xC5, 0xFD)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CHARTS = "/home/hatch/workspace/telco-churn/charts"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]


def solid_bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def textbox(slide, left, top, width, height):
    tx = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tx.text_frame
    tf.word_wrap = True
    return tf


def add_par(tf, text, size, color, bold=False, italic=False, first=False, align=None):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.space_after = Pt(8)
    if align is not None:
        p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    return p


def add_bullet(tf, text, size=17, first=False):
    p = add_par(tf, text, size, DARK, first=first)
    pPr = p._p.get_or_add_pPr()
    pPr.append(pPr.makeelement(qn("a:buChar"), {"char": "\u2022"}))
    pPr.set("marL", "171450")
    pPr.set("indent", "-171450")
    p.space_after = Pt(10)
    p.space_before = Pt(2)
    return p


def content_title(slide, text):
    tf = textbox(slide, 0.7, 0.3, 11.9, 0.9)
    add_par(tf, text, 30, NAVY, bold=True, first=True)
    bar = slide.shapes.add_shape(1, Inches(0.7), Inches(1.15), Inches(1.5), Inches(0.06))
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL
    bar.line.fill.background()


def content_slide(title, bullets, chart=None, caption=None, full_width=False):
    s = prs.slides.add_slide(blank)
    solid_bg(s, WHITE)
    content_title(s, title)
    bw = 11.9 if full_width else 5.6
    tf = textbox(s, 0.7, 1.5, bw, 5.2)
    for i, b in enumerate(bullets):
        add_bullet(tf, b, first=(i == 0))
    if chart:
        s.shapes.add_picture(f"{CHARTS}/{chart}.png", Inches(6.8), Inches(1.5),
                             width=Inches(5.8), height=Inches(3.48))
        ctf = textbox(s, 6.8, 5.15, 5.8, 0.5)
        add_par(ctf, caption, 12, GRAY, italic=True, first=True, align=PP_ALIGN.CENTER)
    return s


# ---------- Slide 1: Judul ----------
s = prs.slides.add_slide(blank)
solid_bg(s, NAVY)
tf = textbox(s, 1.0, 1.6, 11.3, 2.2)
add_par(tf, "Analisis Telco Customer Churn dengan SQL dan Python", 40, WHITE, bold=True, first=True)
tf = textbox(s, 1.0, 3.8, 11.3, 1.2)
add_par(tf, "Studi Kasus: IBM Sample Telco Customer Churn — Siapa yang Pergi, Kenapa, dan Berapa Pendapatan yang Hilang", 20, WHITE, first=True)
tf = textbox(s, 1.0, 5.6, 11.3, 1.0)
add_par(tf, "BAGHIZ ASSHIDDIQIE ARASYA", 24, LIGHTBLUE, bold=True, first=True)
tf = textbox(s, 1.0, 6.3, 11.3, 0.8)
add_par(tf, "Data Analyst Portfolio Project", 14, GRAY, first=True)

# ---------- Slide 2: Latar Belakang ----------
content_slide("Latar Belakang", [
    "Dataset IBM Sample Telco Customer Churn: 7.032 pelanggan bersih dengan 21 kolom demografi, layanan, kontrak, dan tagihan",
    "Pertanyaan utama: pelanggan mana yang berhenti berlangganan, kenapa mereka pergi, dan berapa pendapatan yang hilang",
    "Churn rate keseluruhan 26,6 persen atau 1.869 pelanggan, lebih dari 1 dari 4 pelanggan pergi",
    "Tujuan analisis: menemukan segmen paling rawan churn lalu menyusun rekomendasi retensi yang konkret dan terukur",
], full_width=True)

# ---------- Slide 3: Data dan Metodologi ----------
content_slide("Data dan Metodologi", [
    "Data dimuat ke SQLite lalu dianalisis dengan query SQL asli: agregasi, grouping, dan perbandingan antar segmen",
    "Pembersihan penting: kolom TotalCharges tiba sebagai teks dengan 11 nilai kosong tersembunyi (semua tenure 0, belum pernah ditagih), 11 baris itu dihapus karena imputasi berarti mengarang data",
    "Pandas dipakai untuk eksplorasi lanjutan dan pembuatan 12 chart visual",
    "Churn didefinisikan sebagai kolom Churn bernilai Yes; rate dihitung sebagai Yes dibagi total pelanggan",
    "Segmen yang dianalisis: kontrak, masa berlangganan, layanan internet, metode pembayaran, tagihan, layanan dukungan, demografi, dan segmen kombinasi",
], full_width=True)

# ---------- Slide 4: Temuan 1, kontrak ----------
content_slide("Temuan 1: Kontrak Bulanan Paling Berisiko", [
    "Kontrak bulanan (month-to-month) churn 42,7 persen, 15 kali lipat kontrak 2 tahun yang hanya 2,8 persen",
    "Kontrak bulanan mencakup 55,1 persen pelanggan tetapi menyumbang 88,6 persen dari semua churn",
    "Kontrak 1 tahun churn 11,3 persen, jauh lebih aman dibanding bulanan",
    "Tanpa komitmen jangka panjang, pelanggan pergi kapan saja dan hampir tanpa hambatan",
], chart="02_churn_contract", caption="Churn rate per jenis kontrak")

# ---------- Slide 5: Temuan 2, pelanggan baru ----------
content_slide("Temuan 2: Tahun Pertama Paling Kritis", [
    "Pelanggan baru 0 sampai 12 bulan churn 47,7 persen, hampir separuh pergi di tahun pertama",
    "Pelanggan baru menyumbang 55,5 persen dari semua churn, padahal hanya 30,9 persen dari basis pelanggan",
    "Churn turun bertahap sampai 9,5 persen setelah 4 tahun berlangganan",
    "Siapa yang bertahan melewati tahun pertama cenderung setia, jadi onboarding awal adalah investasi terbaik",
], chart="03_churn_tenure", caption="Churn rate per masa berlangganan")

# ---------- Slide 6: Temuan 3, fiber + pembayaran ----------
content_slide("Temuan 3: Fiber Mahal tapi Ditinggalkan", [
    "Pelanggan Fiber optic churn 41,9 persen, lebih dari dua kali DSL yang 19,0 persen",
    "Pelanggan yang membayar dengan cek elektronik churn 45,3 persen, hampir 3 kali lipat kartu kredit otomatis 15,3 persen",
    "Tagihan bulanan 71 sampai 90 USD churn 37,8 persen, tertinggi di antara band tagihan",
    "Sinyal masalah nilai: pelanggan membayar paling mahal tetapi merasa layanannya tidak sepadan, dan pembayaran manual membuat pergi terasa mudah",
], chart="04_churn_internet", caption="Churn rate per layanan internet")

# ---------- Slide 7: Temuan 4, dukungan + demografi ----------
content_slide("Temuan 4: Dukungan Melindungi, Lansia Rentan", [
    "Pelanggan internet tanpa Tech Support churn 41,6 persen, dibanding yang memakai hanya 15,2 persen",
    "Tanpa Online Security churn 41,8 persen, dibanding yang memakai 14,6 persen",
    "Senior citizen churn 41,7 persen, pelanggan tanpa pasangan 33,0 persen, tanpa tanggungan 31,3 persen",
    "Gender hampir tidak berpengaruh: perempuan 27,0 persen vs laki-laki 26,2 persen",
], chart="07_churn_support", caption="Churn: Tech Support dan Online Security")

# ---------- Slide 8: Temuan 5, kombinasi + pendapatan ----------
content_slide("Temuan 5: Risiko Menumpuk dan Pendapatan Hilang", [
    "Fiber optic plus kontrak bulanan churn 54,6 persen, lebih dari separuh pergi",
    "Kontrak bulanan plus pelanggan baru churn 51,4 persen, kombinasi dua faktor rawan",
    "Pendapatan yang hilang akibat churn: 139.131 USD per bulan, atau 30,5 persen dari seluruh pendapatan bulanan",
    "Pelanggan yang churn membayar rata-rata 74,44 USD per bulan vs 61,31 USD yang bertahan, yang pergi adalah pelanggan bernilai lebih tinggi",
], chart="10_churn_combo", caption="Churn pada segmen kombinasi paling rawan")

# ---------- Slide 9: Rekomendasi ----------
content_slide("Rekomendasi Retensi", [
    "Bangun program onboarding 12 bulan pertama: sapa proaktif di bulan ke-1, 3, dan 6 plus cek kepuasan dini",
    "Konversi kontrak bulanan ke kontrak tahunan dengan insentif: diskon loyalitas, harga terkunci, dan bonus layanan",
    "Audit nilai layanan Fiber optic: tinjau kualitas jaringan per area, harga, dan komunikasi manfaatnya",
    "Dorong auto-pay dan migrasi dari cek elektronik dengan insentif kecil",
    "Tawarkan Tech Support dan Online Security proaktif, bundel dukungan gratis 3 bulan untuk segmen rawan",
    "Perhatian khusus untuk lansia dan pelanggan yang hidup sendiri dengan jalur dukungan yang lebih personal",
], full_width=True)

# ---------- Slide 10: Penutup ----------
s = prs.slides.add_slide(blank)
solid_bg(s, NAVY)
tf = textbox(s, 1.0, 1.8, 11.3, 1.2)
add_par(tf, "Kesimpulan", 36, WHITE, bold=True, first=True)
tf = textbox(s, 1.0, 3.0, 11.3, 3.0)
add_bullet(tf, "Kontrak bulanan, tahun pertama, dan fiber optic adalah tiga pendorong churn terbesar", size=18, first=True)
for b in [
    "Fokus retensi pada segmen kombinasi: fiber plus kontrak bulanan (54,6 persen) dan kontrak bulanan plus pelanggan baru (51,4 persen)",
    "Churn bukan sekadar angka pelanggan: 139.131 USD pendapatan hilang setiap bulan",
    "Tech stack: SQL di SQLite, Python dengan pandas, matplotlib, dan seaborn",
]:
    add_bullet(tf, b, size=18)
for p in tf.paragraphs:
    for r in p.runs:
        r.font.color.rgb = WHITE
tf = textbox(s, 1.0, 6.2, 11.3, 0.8)
add_par(tf, "BAGHIZ ASSHIDDIQIE ARASYA", 20, LIGHTBLUE, bold=True, first=True)

prs.save("/home/hatch/workspace/your_files/Portofolio-Analisis-Telco-Churn.pptx")
print("saved")
