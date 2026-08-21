"""
app/style.py — Kopita UI Visual Engine
=======================================
Modul ini menyimpan seluruh CSS kustom dan generator komponen HTML
untuk tema visual "Warm Earthy Espresso" Kopita.

Palet Warna Resmi Kopita:
  #472D2D  Deep Espresso  — teks utama, heading, navigasi krusial
  #553939  Warm Mocha     — background sidebar, border komponen
  #704F4F  Medium Cocoa   — teks sekunder, ikon, kartu informasi sekunder
  #A77979  Earthy Rose    — aksen utama, tombol CTA, hover state, highlight
  #FDFBF7  Off-White/Ivory — background halaman utama (premium, bersih)

Aturan modul ini (.rules.md Section 2):
  - TIDAK mengimpor torch, torchvision, atau library AI apapun.
  - TIDAK melakukan HTTP request ke backend.
  - Hanya berisi fungsi yang menghasilkan string HTML/CSS
    atau memanggil st.markdown() untuk menyuntikkan gaya.
  - File model 'best_torajigrade_model.pth' TIDAK disentuh di sini.
"""

import streamlit as st


# =============================================================
# PALET WARNA RESMI KOPITA
# (digunakan di seluruh modul UI agar konsisten)
# =============================================================
PALETTE: dict[str, str] = {
    "deep_espresso": "#472D2D",   # Teks utama, heading besar
    "warm_mocha":    "#553939",   # Background sidebar, borders
    "medium_cocoa":  "#704F4F",   # Teks sekunder, ikon, kartu sekunder
    "earthy_rose":   "#A77979",   # Aksen CTA, hover, highlight
    "ivory":         "#FDFBF7",   # Background halaman utama
}

# ─── Palet Warna Dinamis per Kelas Deteksi ───────────────────────────────────
# Warna bilah gauge menyesuaikan kondisi fisik biji kopi secara intuitif.
CLASS_COLORS: dict[str, str] = {
    "Green":  "#2E7D32",   # Hijau segar  — biji mentah, belum disangrai
    "Light":  "#D4A373",   # Cokelat keemasan — sangrai muda, terang
    "Medium": "#A77979",   # Earthy Rose (selaras palet Kopita) — sangrai sedang
    "Dark":   "#472D2D",   # Deep Espresso — sangrai tua, gelap pekat
}

# Warna teks kontras per kelas (keterbacaan di atas bilah warna)
CLASS_TEXT_COLORS: dict[str, str] = {
    "Green":  "#FFFFFF",
    "Light":  "#472D2D",
    "Medium": "#FFFFFF",
    "Dark":   "#FFFFFF",
}


def inject_global_css() -> None:
    """
    Menyuntikkan CSS global ke halaman Streamlit.
    Dipanggil SEKALI di awal ui.py sebelum komponen lain dirender.

    Menerapkan tema Warm Earthy Espresso dengan palet resmi Kopita:
    Deep Espresso (#472D2D), Warm Mocha (#553939), Medium Cocoa (#704F4F),
    Earthy Rose (#A77979), Off-White/Ivory (#FDFBF7).
    """
    st.markdown(
        """
        <style>
        /* ── Google Font: Inter (modern, bersih, mudah dibaca) ─── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        /* ── Root & Body — font global ──────────────────────────── */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* ── Background halaman: #FDFBF7 Off-White/Ivory ────────── */
        /* Memberikan kontras premium — tidak terlalu putih, hangat  */
        .stApp {
            background-color: #FDFBF7;
        }

        /* ── Judul utama Kopita ──────────────────────────────────── */
        /* Warna: #472D2D Deep Espresso                               */
        .kopita-title {
            text-align: center;
            color: #472D2D;
            font-size: 2.8rem;
            font-weight: 800;
            letter-spacing: -0.8px;
            margin-bottom: 0.2rem;
            line-height: 1.1;
        }

        /* ── Tagline resmi Kopita ────────────────────────────────── */
        /* Warna: #704F4F Medium Cocoa (teks sekunder)                */
        .kopita-tagline {
            text-align: center;
            color: #704F4F;
            font-size: 1.0rem;
            font-weight: 600;
            margin-top: 0.1rem;
            margin-bottom: 0.5rem;
            font-style: italic;
        }

        /* ── Misi deskripsi di bawah tagline ────────────────────── */
        /* Warna: #704F4F Medium Cocoa                                */
        .kopita-mission {
            text-align: center;
            color: #704F4F;
            font-size: 0.88rem;
            font-weight: 400;
            max-width: 680px;
            margin: 0 auto 1.2rem auto;
            line-height: 1.7;
        }

        /* ── Kartu hasil prediksi ────────────────────────────────── */
        /* Border-left dinamis per kelas; shadow hangat espresso      */
        .result-card {
            background: #FFFFFF;
            border-radius: 14px;
            padding: 1.4rem 1.6rem;
            box-shadow: 0 4px 24px rgba(71, 45, 45, 0.10);
            border-left: 6px solid #A77979;
            margin-bottom: 1rem;
        }

        /* ── Label kelas di dalam kartu ─────────────────────────── */
        /* Warna: #472D2D Deep Espresso                               */
        .result-class-label {
            font-size: 1.5rem;
            font-weight: 700;
            color: #472D2D;
            margin: 0;
        }

        /* ── Teks deskripsi dan saran di dalam kartu ────────────── */
        /* Warna: #704F4F Medium Cocoa                                */
        .result-description {
            font-size: 0.92rem;
            color: #704F4F;
            line-height: 1.65;
            margin-top: 0.5rem;
        }

        /* ── Footer kecil ───────────────────────────────────────── */
        /* Warna: #A77979 Earthy Rose (subtle, tidak mengganggu)     */
        .kopita-footer {
            text-align: center;
            color: #A77979;
            font-size: 0.78rem;
            margin-top: 1.5rem;
        }

        /* ── Sidebar: background Warm Mocha (#553939) ───────────── */
        /* Warna gelap sidebar memberi kontras premium vs body ivory  */
        section[data-testid="stSidebar"] {
            background-color: #553939;
        }

        /* ── Divider sidebar (border komponen) ─────────────────── */
        section[data-testid="stSidebar"] hr {
            border-color: #704F4F;
        }

        /* ── Teks di dalam sidebar ──────────────────────────────── */
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] li,
        section[data-testid="stSidebar"] small {
            color: #FDFBF7 !important;
        }

        /* ── Gauge bar — container ──────────────────────────────── */
        .gauge-wrapper {
            margin: 1rem 0 0.5rem 0;
        }
        .gauge-label-row {
            display: flex;
            justify-content: space-between;
            font-size: 0.82rem;
            color: #704F4F;
            margin-bottom: 4px;
            font-weight: 600;
        }

        /* ── Gauge bar — track (latar belakang abu kecokelatan) ─── */
        .gauge-track {
            background-color: #EDE0D4;
            border-radius: 999px;
            height: 24px;
            width: 100%;
            overflow: hidden;
            box-shadow: inset 0 2px 5px rgba(71,45,45,0.12);
        }

        /* ── Gauge bar — fill (diisi secara dinamis via inline CSS) */
        /* Warna fill diatur per-kelas dari CLASS_COLORS             */
        .gauge-fill {
            height: 100%;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            font-size: 0.78rem;
            font-weight: 700;
            color: #FFFFFF;
            transition: width 0.7s cubic-bezier(0.4, 0, 0.2, 1);
            min-width: 44px;
        }

        /* ── Tombol Analisis — Earthy Rose (#A77979) sebagai CTA ── */
        .stButton > button[kind="primary"] {
            background-color: #A77979 !important;
            color: #FDFBF7 !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 0.6rem 1.4rem !important;
            transition: background-color 0.2s ease, transform 0.1s ease !important;
        }
        .stButton > button[kind="primary"]:hover {
            background-color: #704F4F !important;
            transform: translateY(-1px) !important;
        }
        .stButton > button[kind="primary"]:active {
            transform: translateY(0px) !important;
        }

        /* ── Tab styling — selaraskan dengan palet ─────────────── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            color: #704F4F;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            color: #472D2D !important;
            border-bottom-color: #A77979 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_maturity_gauge(prediction: str, confidence_str: str) -> None:
    """
    Merender bilah kematangan dinamis (Maturity Gauge).

    Warna bilah menyesuaikan kelas prediksi dari backend:
      - Green  -> #2E7D32 (hijau segar, biji mentah)
      - Light  -> #D4A373 (cokelat keemasan, sangrai muda)
      - Medium -> #A77979 (Earthy Rose Kopita, sangrai sedang)
      - Dark   -> #472D2D (Deep Espresso, sangrai tua)

    Args:
        prediction    : Nama kelas hasil prediksi (misal "Medium").
        confidence_str: String persentase dari API (misal "98.42%").
    """
    try:
        conf_value: float = float(confidence_str.replace("%", "").strip())
    except ValueError:
        conf_value = 0.0

    bar_color: str  = CLASS_COLORS.get(prediction, PALETTE["earthy_rose"])
    text_color: str = CLASS_TEXT_COLORS.get(prediction, "#FFFFFF")
    fill_pct: float = max(0.0, min(conf_value, 100.0))

    st.markdown(
        f"""
        <div class="gauge-wrapper">
            <div class="gauge-label-row">
                <span>Tingkat Keyakinan Model (Confidence Score)</span>
                <span>{fill_pct:.1f}%</span>
            </div>
            <div class="gauge-track">
                <div class="gauge-fill"
                     style="width:{fill_pct}%;
                            background-color:{bar_color};
                            color:{text_color};">
                    {fill_pct:.1f}%
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result_card(
    icon: str,
    label: str,
    prediction: str,
    description: str,
    business_advice: str,
) -> None:
    """
    Merender kartu hasil prediksi dengan warna aksen dinamis
    sesuai kelas yang terdeteksi.

    Warna border-left menggunakan CLASS_COLORS per kelas.
    Teks menggunakan palet resmi Kopita (Deep Espresso & Medium Cocoa).

    Args:
        icon           : Emoji representasi kelas (misal "").
        label          : Label lengkap kelas (misal "Medium (Sangrai Sedang)").
        prediction     : Nama kelas mentah dari API (misal "Medium").
        description    : Deskripsi fisik biji kopi dari metadata backend.
        business_advice: Saran komersial UMKM dari metadata backend.
    """
    accent: str = CLASS_COLORS.get(prediction, PALETTE["earthy_rose"])

    st.markdown(
        f"""
        <div class="result-card" style="border-left-color:{accent};">
            <p class="result-class-label">{icon} {label}</p>
            <p class="result-description">
                <b>Deskripsi Fisik:</b><br>{description}
            </p>
            <hr style="border:none;border-top:1px solid #EDE0D4;margin:0.8rem 0;">
            <p class="result-description">
                <b>Rekomendasi UMKM:</b><br>{business_advice}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_guidelines() -> None:
    """
    Merender sidebar Kopita yang berisi:
      1. Branding mini Kopita dengan filosofi sosial-ekonomi
      2. Panduan memotret biji kopi untuk akurasi optimal
      3. Narasi Tim DCC Juara & nilai gotong royong Kopita
      4. Footer kredit hackathon

    Dipanggil dari ui.py sebelum komponen utama dirender.
    Background sidebar: #553939 Warm Mocha (lihat inject_global_css).
    """
    with st.sidebar:
        # ── Branding mini ─────────────────────────────────────────────
        st.markdown(
            f"""
            <h2 style='color:#FDFBF7;font-size:1.5rem;font-weight:800;
                        margin-bottom:0.1rem;'>Kopita</h2>
            <p style='color:#FDFBF7;font-size:0.78rem;font-weight:500;
                       opacity:0.85;margin-top:0;'>
                AI Cerdas, Transaksi Pas, Kopi Berkualitas
            </p>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        # ── Filosofi & Misi ────────────────────────────────────────────
        with st.expander("Tentang Kopita", expanded=False):
            st.markdown(
                """
                <p style='font-size:0.84rem;line-height:1.7;color:#FDFBF7;'>
                Kopita hadir untuk menghentikan praktik penilaian kualitas
                kopi yang selama ini bersifat <b>subjektif dan tidak terstandar</b>
                — merugikan petani kopi dan UMKM roastery lokal Toraja.
                </p>
                <p style='font-size:0.84rem;line-height:1.7;color:#FDFBF7;'>
                Dengan memanfaatkan <b>computer vision</b> berbasis
                MobileNetV3-Small yang dilatih pada data biji kopi nyata,
                Kopita menghadirkan standarisasi objektif yang dapat
                diakses siapa saja — mewujudkan transaksi yang
                <b>transparan dan adil</b> bagi seluruh ekosistem kopi Toraja.
                </p>
                """,
                unsafe_allow_html=True,
            )

        # ── Panduan Memotret ───────────────────────────────────────────
        with st.expander("Panduan Memotret Biji Kopi", expanded=True):
            st.markdown(
                """
                <p style='font-size:0.84rem;color:#FDFBF7;font-weight:600;
                           margin-bottom:0.5rem;'>
                Ikuti panduan ini untuk hasil analisis paling akurat:
                </p>

                <p style='font-size:0.83rem;color:#FDFBF7;line-height:1.65;'>
                <b>Jarak</b><br>
                Foto tegak lurus dari atas, jarak <b>10-15 cm</b> dari biji kopi.
                </p>

                <p style='font-size:0.83rem;color:#FDFBF7;line-height:1.65;'>
                <b>Pencahayaan</b><br>
                Cahaya <b>terang dan merata</b>. Hindari bayangan ekstrem
                atau cahaya dari satu sisi saja.
                </p>

                <p style='font-size:0.83rem;color:#FDFBF7;line-height:1.65;'>
                <b>Fokus</b><br>
                Kamera <b>fokus penuh</b> pada sebaran biji kopi,
                bukan pada latar belakang atau wadah.
                </p>

                <p style='font-size:0.76rem;color:#FDFBF7;opacity:0.7;
                           margin-top:0.8rem;'>
                Model dilatih pada resolusi <b>224x224 px</b>.
                Gambar buram atau terlalu gelap akan menurunkan akurasi.
                </p>
                """,
                unsafe_allow_html=True,
            )

        # ── Profil Tim ─────────────────────────────────────────────────
        with st.expander("Tim DCC Juara", expanded=False):
            st.markdown(
                """
                <p style='font-size:0.84rem;line-height:1.7;color:#FDFBF7;'>
                Kopita dikembangkan oleh <b>Tim DCC Juara</b> — sebuah tim
                multidisiplin yang meyakini bahwa teknologi terbaik adalah
                teknologi yang berdampak nyata bagi masyarakat.
                </p>
                <p style='font-size:0.84rem;line-height:1.7;color:#FDFBF7;'>
                Kami membangun Kopita dengan semangat <b>gotong royong</b>
                dan komitmen terhadap <b>demokratisasi teknologi</b> —
                agar inovasi AI tidak hanya dinikmati oleh perusahaan besar,
                tetapi juga dapat diakses oleh petani kopi dan UMKM kecil
                di pelosok Toraja, Sulawesi Selatan.
                </p>
                <ul style='font-size:0.82rem;color:#FDFBF7;
                            padding-left:1.2rem;line-height:1.8;'>
                    <li><b>Dayat</b> — ML Engineer & Model Training</li>
                    <li><b>Mull</b> — Backend Developer</li>
                    <li><b>Rey</b> — Frontend Developer</li>
                    <li><b>Sasa</b> — UI/UX & Data Analyst</li>
                </ul>
                """,
                unsafe_allow_html=True,
            )

        # ── Footer kredit ──────────────────────────────────────────────
        st.divider()
        st.markdown(
            """
            <p style='color:#FDFBF7;font-size:0.72rem;text-align:center;
                       opacity:0.6;margin:0;'>
                AIC DCC Hackathon 2026<br>Tim AIC DCC Juara
            </p>
            """,
            unsafe_allow_html=True,
        )
