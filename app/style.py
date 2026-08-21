"""
app/style.py -- Kopita UI Visual Engine
========================================
Seluruh CSS global, komponen HTML kustom, dan fungsi render
untuk tema "Warm Earthy Espresso" Kopita.

Palet Warna Resmi:
  #472D2D  Deep Espresso   -- teks utama, heading, navigasi krusial
  #553939  Warm Mocha      -- background sidebar, border komponen
  #704F4F  Medium Cocoa    -- teks sekunder, label, deskripsi pendukung
  #A77979  Earthy Rose     -- aksen CTA, border kartu sukses, gauge fill
  #FDFBF7  Off-White/Ivory -- background halaman utama

Aturan modul ini (.rules.md Section 2):
  - TIDAK mengimpor torch, torchvision, atau library AI apapun.
  - TIDAK melakukan HTTP request.
  - Hanya CSS, HTML string, dan st.markdown().
  - File model 'best_torajigrade_model.pth' TIDAK disentuh.
"""

import streamlit as st


# =============================================================
# PALET WARNA RESMI KOPITA
# =============================================================
PALETTE: dict[str, str] = {
    "deep_espresso": "#472D2D",
    "warm_mocha":    "#553939",
    "medium_cocoa":  "#704F4F",
    "earthy_rose":   "#A77979",
    "ivory":         "#FDFBF7",
}

# Warna gauge per kelas deteksi
CLASS_COLORS: dict[str, str] = {
    "Green":  "#2E7D32",
    "Light":  "#D4A373",
    "Medium": "#A77979",
    "Dark":   "#472D2D",
}

CLASS_TEXT_COLORS: dict[str, str] = {
    "Green":  "#FFFFFF",
    "Light":  "#472D2D",
    "Medium": "#FFFFFF",
    "Dark":   "#FFFFFF",
}


def inject_global_css() -> None:
    """
    Suntikkan CSS global ke Streamlit sekali di awal ui.py.
    """
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Background halaman: Ivory #FDFBF7 */
    .stApp {
        background-color: #FDFBF7;
    }

    /* Teks utama: Deep Espresso #472D2D */
    body, p, span, li, label, div,
    .stMarkdown p,
    .stMarkdown li,
    .stMarkdown span,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {
        color: #472D2D;
    }

    /* Override Khusus Elemen Berlatar Gelap (JSON Viewer, Code Blocks, Tree Views) */
    [data-testid="stJson"],
    [data-testid="stJson"] *,
    [data-testid="stCodeBlock"],
    [data-testid="stCodeBlock"] *,
    div[data-baseweb="tree-view"],
    div[data-baseweb="tree-view"] *,
    .stCodeBlock pre,
    .stCodeBlock code {
        color: #FDFBF7 !important;
        background-color: #382424 !important;
        border-radius: 6px;
    }
    /* Kunci & nilai JSON kontras terang */
    div[data-baseweb="tree-view"] li,
    div[data-baseweb="tree-view"] span {
        color: #E6C594 !important;
    }

    /* Inline Code Blocks (`code`) di Tabel & Markdown */
    :not(pre) > code,
    .stMarkdown :not(pre) > code,
    [data-testid="stMarkdownContainer"] :not(pre) > code,
    table code {
        color: #472D2D !important;
        background-color: #EDE0D4 !important;
        padding: 0.15rem 0.45rem !important;
        border-radius: 4px !important;
        font-weight: 700 !important;
        font-size: 0.85em !important;
        border: 1px solid #D4A373 !important;
    }

    /* Judul utama Kopita */
    .kopita-title {
        text-align: center;
        color: #472D2D;
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.8px;
        margin: 0.2rem 0 0.1rem 0;
        line-height: 1.1;
    }

    /* Tagline resmi */
    .kopita-tagline {
        text-align: center;
        color: #704F4F;
        font-size: 1.0rem;
        font-weight: 600;
        font-style: italic;
        margin: 0.1rem 0 0.6rem 0;
    }

    /* Deskripsi misi */
    .kopita-mission {
        text-align: center;
        color: #704F4F;
        font-size: 0.88rem;
        font-weight: 400;
        max-width: 680px;
        margin: 0 auto 1.2rem auto;
        line-height: 1.75;
    }

    /* Footer kecil */
    .kopita-footer {
        text-align: center;
        color: #A77979;
        font-size: 0.76rem;
        margin-top: 1.5rem;
    }

    /* Sidebar: Warm Mocha #553939 */
    section[data-testid="stSidebar"] {
        background-color: #553939;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #704F4F;
        opacity: 0.6;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] small,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {
        color: #FDFBF7 !important;
    }

    /* Tombol CTA: Earthy Rose #A77979 */
    .stButton > button[kind="primary"] {
        background-color: #A77979 !important;
        color: #FDFBF7 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.55rem 1.4rem !important;
        transition: background-color 0.2s ease, transform 0.1s ease !important;
        letter-spacing: 0.3px !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #704F4F !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button[kind="primary"]:active {
        transform: translateY(0) !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 2px solid #EDE0D4;
    }
    .stTabs [data-baseweb="tab"] {
        color: #704F4F !important;
        font-weight: 500;
        font-size: 0.88rem;
        padding: 0.4rem 1rem;
    }
    .stTabs [aria-selected="true"] {
        color: #472D2D !important;
        border-bottom: 2px solid #A77979 !important;
        font-weight: 700 !important;
    }

    /* Sembunyikan visual bawaan status Streamlit */
    div[data-testid="stAlert"] {
        display: none !important;
    }

    /* Kartu hasil prediksi */
    .result-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 1.4rem 1.5rem;
        box-shadow: 0 4px 18px rgba(71, 45, 45, 0.08);
        border-left: 6px solid #A77979;
        margin-bottom: 1rem;
    }
    .result-card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #472D2D;
        margin: 0 0 0.8rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #EDE0D4;
    }
    .result-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.8rem 1.2rem;
    }
    .result-cell-label {
        font-size: 0.74rem;
        font-weight: 700;
        color: #A77979;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 2px;
    }
    .result-cell-value {
        font-size: 0.92rem;
        color: #472D2D;
        font-weight: 500;
        line-height: 1.55;
    }
    .result-cell-full {
        grid-column: 1 / -1;
    }
    .result-divider {
        grid-column: 1 / -1;
        border: none;
        border-top: 1px solid #EDE0D4;
        margin: 0.2rem 0;
    }

    /* Kotak info kustom */
    .box-info {
        background: #FFFFFF;
        border: 1px solid #704F4F;
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        margin: 0.5rem 0;
        color: #472D2D;
        font-size: 0.88rem;
        line-height: 1.6;
    }
    .box-info-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: #704F4F;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 3px;
    }

    /* Kotak sukses kustom */
    .box-success {
        background: #FDF8F4;
        border: 1px solid #A77979;
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        margin: 0.5rem 0;
        color: #472D2D;
        font-size: 0.88rem;
        line-height: 1.6;
    }
    .box-success-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: #A77979;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 3px;
    }

    /* Kotak error kustom */
    .box-error {
        background: #FFF5F5;
        border: 1px solid #C0392B;
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        margin: 0.5rem 0;
        color: #472D2D;
        font-size: 0.88rem;
        line-height: 1.6;
    }
    .box-error-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: #C0392B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 3px;
    }

    /* Gauge bar */
    .gauge-wrapper {
        margin: 0.9rem 0 0.5rem 0;
    }
    .gauge-label-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.78rem;
        color: #704F4F;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .gauge-track {
        background-color: #EDE0D4;
        border-radius: 999px;
        height: 22px;
        width: 100%;
        overflow: hidden;
        box-shadow: inset 0 1px 3px rgba(71,45,45,0.10);
    }
    .gauge-fill {
        height: 100%;
        border-radius: 999px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 10px;
        font-size: 0.74rem;
        font-weight: 700;
        min-width: 44px;
    }

    [data-testid="stFileUploader"] {
        border-color: #EDE0D4 !important;
    }
    [data-testid="stMetricValue"] {
        color: #472D2D !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #704F4F !important;
        font-size: 0.8rem !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# =============================================================
# KOMPONEN HTML KUSTOM
# =============================================================

def render_info_box(message: str, label: str = "Informasi") -> None:
    """Tampilkan kotak informasi kustom -- menggantikan st.info()."""
    html = f'<div class="box-info"><div class="box-info-label">{label}</div><div>{message}</div></div>'
    st.markdown(html, unsafe_allow_html=True)


def render_success_box(message: str, label: str = "Keterangan") -> None:
    """Tampilkan kotak keterangan/sukses kustom -- menggantikan st.success()."""
    html = f'<div class="box-success"><div class="box-success-label">{label}</div><div>{message}</div></div>'
    st.markdown(html, unsafe_allow_html=True)


def render_error_box(message: str, label: str = "Terjadi Kesalahan") -> None:
    """Tampilkan kotak error kustom -- menggantikan st.error()."""
    html = f'<div class="box-error"><div class="box-error-label">{label}</div><div>{message}</div></div>'
    st.markdown(html, unsafe_allow_html=True)


def render_maturity_gauge(prediction: str, confidence_str: str) -> None:
    """Render bilah kematangan dinamis (Maturity Gauge)."""
    try:
        conf_value: float = float(confidence_str.replace("%", "").strip())
    except ValueError:
        conf_value = 0.0

    bar_color: str = CLASS_COLORS.get(prediction, PALETTE["earthy_rose"])
    text_color: str = CLASS_TEXT_COLORS.get(prediction, "#FFFFFF")
    fill_pct: float = max(0.0, min(conf_value, 100.0))

    html = (
        f'<div class="gauge-wrapper">'
        f'<div class="gauge-label-row">'
        f'<span>Tingkat Keyakinan Model (Confidence Score)</span>'
        f'<span>{fill_pct:.1f}%</span>'
        f'</div>'
        f'<div class="gauge-track">'
        f'<div class="gauge-fill" style="width:{fill_pct}%; background-color:{bar_color}; color:{text_color};">'
        f'{fill_pct:.1f}%'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_result_card(
    label: str,
    prediction: str,
    confidence: str,
    description: str,
    business_advice: str,
) -> None:
    """Render kartu hasil prediksi dalam layout grid 2 kolom yang bersih."""
    accent: str = CLASS_COLORS.get(prediction, PALETTE["earthy_rose"])

    html = (
        f'<div class="result-card" style="border-left-color:{accent};">'
        f'<div class="result-card-title">Hasil Analisis Kopi</div>'
        f'<div class="result-grid">'
        f'<div><div class="result-cell-label">Kelas Terdeteksi</div><div class="result-cell-value">{label}</div></div>'
        f'<div><div class="result-cell-label">Kepercayaan Model</div><div class="result-cell-value">{confidence}</div></div>'
        f'<hr class="result-divider">'
        f'<div class="result-cell-full"><div class="result-cell-label">Karakteristik Fisik</div><div class="result-cell-value">{description}</div></div>'
        f'<div class="result-cell-full"><div class="result-cell-label">Rekomendasi Bisnis UMKM</div><div class="result-cell-value">{business_advice}</div></div>'
        f'</div>'
        f'</div>'
    )
def render_image(image, caption: str | None = None) -> None:
    """
    Render gambar adaptif yang kompatibel di semua versi Streamlit.
    (Mendukung Streamlit baru dengan use_container_width dan Streamlit lama dengan use_column_width).
    """
    try:
        st.image(image, caption=caption, use_container_width=True)
    except TypeError:
        st.image(image, caption=caption, use_column_width=True)


def render_sidebar_content(logo_image=None) -> None:
    """Render konten sidebar Kopita secara lengkap."""
    with st.sidebar:
        if logo_image is not None:
            render_image(logo_image)

        header_html = (
            '<div style="text-align:center;padding:0.4rem 0 0.6rem 0;">'
            '<p style="color:#FDFBF7;font-size:1.2rem;font-weight:800;margin:0;letter-spacing:-0.3px;">Kopita</p>'
            '<p style="color:#FDFBF7;font-size:0.78rem;font-weight:500;opacity:0.85;margin:2px 0 0 0;">'
            'Sistem Cerdas Penilai Kualitas Kopi'
            '</p>'
            '<p style="color:#FDFBF7;font-size:0.75rem;font-weight:400;opacity:0.70;margin:1px 0 0 0;">'
            'UMKM Roastery Toraja'
            '</p>'
            '</div>'
        )
        st.markdown(header_html, unsafe_allow_html=True)
        st.divider()

        with st.expander("Tentang Kopita", expanded=False):
            about_html = (
                '<p style="color:#FDFBF7;font-size:0.83rem;line-height:1.7;margin:0;">'
                'Kopita hadir untuk mengakhiri penilaian kualitas kopi yang '
                'selama ini bersifat <b>subjektif dan tidak terstandar</b> '
                '-- merugikan petani dan UMKM roastery lokal Toraja.'
                '</p><br>'
                '<p style="color:#FDFBF7;font-size:0.83rem;line-height:1.7;margin:0;">'
                'Dengan <b>computer vision</b> berbasis MobileNetV3-Small, '
                'Kopita menghadirkan standarisasi objektif yang mewujudkan '
                'transaksi <b>transparan dan adil</b> bagi seluruh ekosistem '
                'kopi Toraja, Sulawesi Selatan.'
                '</p>'
            )
            st.markdown(about_html, unsafe_allow_html=True)

        with st.expander("Panduan Memotret Biji Kopi", expanded=True):
            guidelines_html = (
                '<p style="color:#FDFBF7;font-size:0.82rem;font-weight:600;margin:0 0 0.6rem 0;">'
                'Ikuti panduan ini untuk hasil analisis paling akurat:'
                '</p>'
                '<p style="color:#FDFBF7;font-size:0.81rem;line-height:1.65;margin:0 0 0.5rem 0;">'
                '<b>Jarak</b><br>Foto tegak lurus dari atas, jarak 10-15 cm dari biji kopi.'
                '</p>'
                '<p style="color:#FDFBF7;font-size:0.81rem;line-height:1.65;margin:0 0 0.5rem 0;">'
                '<b>Pencahayaan</b><br>Cahaya terang dan merata. Hindari bayangan ekstrem atau pencahayaan dari satu sisi saja.'
                '</p>'
                '<p style="color:#FDFBF7;font-size:0.81rem;line-height:1.65;margin:0 0 0.5rem 0;">'
                '<b>Fokus</b><br>Kamera fokus penuh pada sebaran biji kopi, bukan pada latar belakang atau wadah.'
                '</p>'
                '<p style="color:#FDFBF7;font-size:0.74rem;opacity:0.65;margin:0.8rem 0 0 0;line-height:1.5;">'
                'Model dilatih pada resolusi 224x224 px.<br>Gambar buram atau gelap menurunkan akurasi prediksi.'
                '</p>'
            )
            st.markdown(guidelines_html, unsafe_allow_html=True)

        with st.expander("Tim DCC Juara", expanded=False):
            team_html = (
                '<p style="color:#FDFBF7;font-size:0.83rem;line-height:1.7;margin:0 0 0.6rem 0;">'
                'Kopita dikembangkan oleh <b>Tim DCC Juara</b> -- tim '
                'multidisiplin yang meyakini bahwa teknologi terbaik adalah '
                'teknologi yang berdampak nyata bagi masyarakat.'
                '</p>'
                '<p style="color:#FDFBF7;font-size:0.83rem;line-height:1.7;margin:0 0 0.6rem 0;">'
                'Kami membangun Kopita dengan semangat <b>gotong royong</b> '
                'dan komitmen <b>demokratisasi teknologi</b> -- agar inovasi '
                'AI tidak hanya dinikmati korporasi besar, tetapi juga oleh '
                'petani dan UMKM kecil di pelosok Toraja.'
                '</p>'
                '<ul style="color:#FDFBF7;font-size:0.81rem;padding-left:1.1rem;line-height:1.9;margin:0;">'
                '<li><b>Dayat</b> -- ML Engineer, Model Training</li>'
                '<li><b>Mull</b> -- Backend Developer</li>'
                '<li><b>Rey</b> -- Frontend Developer</li>'
                '<li><b>Sasa</b> -- UI/UX, Data Analyst</li>'
                '</ul>'
            )
            st.markdown(team_html, unsafe_allow_html=True)

        st.divider()

        footer_html = (
            '<p style="color:#FDFBF7;font-size:0.70rem;text-align:center;opacity:0.55;margin:0;">'
            'AIC DCC Hackathon 2026<br>Tim AIC DCC Juara'
            '</p>'
        )
        st.markdown(footer_html, unsafe_allow_html=True)
