"""
app/style.py — Kopita UI Visual Engine
=======================================
Modul ini menyimpan seluruh CSS kustom dan generator komponen HTML
untuk tema visual "Warm Earthy Espresso" Kopita.

Aturan modul ini:
  - TIDAK mengimpor torch, torchvision, atau library AI apapun.
  - TIDAK melakukan HTTP request ke backend.
  - Hanya boleh berisi fungsi-fungsi yang menghasilkan string HTML/CSS
    atau memanggil st.markdown() untuk menyuntikkan gaya.
"""

import streamlit as st


# ─── Palet Warna Dinamis per Kelas ──────────────────────────────────────────
# Setiap kelas deteksi memiliki warna khas yang merepresentasikan
# kondisi fisik biji kopi secara visual dan intuitif.
CLASS_COLORS: dict[str, str] = {
    "Green":  "#2E7D32",   # Hijau segar  — biji mentah, belum disangrai
    "Light":  "#D4A373",   # Cokelat keemasan — sangrai muda, terang
    "Medium": "#A98467",   # Cokelat hangat   — sangrai sedang, ideal
    "Dark":   "#4E3629",   # Cokelat pekat    — sangrai tua, gelap
}

# Warna teks kontras per kelas (agar terbaca di atas background bilah)
CLASS_TEXT_COLORS: dict[str, str] = {
    "Green":  "#FFFFFF",
    "Light":  "#4E3629",
    "Medium": "#FFFFFF",
    "Dark":   "#FFFFFF",
}


def inject_global_css() -> None:
    """
    Menyuntikkan CSS global ke halaman Streamlit.
    Dipanggil SEKALI di awal ui.py sebelum komponen lain dirender.
    Mendefinisikan tema Warm Earthy Espresso: font, warna, spacing,
    dan animasi halus untuk keseluruhan tampilan.
    """
    st.markdown(
        """
        <style>
        /* ── Google Font: Inter ────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* ── Root & Body ───────────────────────────────────────── */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* ── App background — nuansa krem hangat ───────────────── */
        .stApp {
            background-color: #FAF6F1;
        }

        /* ── Header H1 Kopita ──────────────────────────────────── */
        .kopita-title {
            text-align: center;
            color: #4E3629;
            font-size: 2.6rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            margin-bottom: 0.1rem;
        }

        /* ── Subtitle tagline ──────────────────────────────────── */
        .kopita-subtitle {
            text-align: center;
            color: #7F5A44;
            font-size: 0.95rem;
            font-weight: 500;
            margin-top: 0;
            margin-bottom: 1rem;
        }

        /* ── Kartu hasil prediksi ──────────────────────────────── */
        .result-card {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 1.4rem 1.6rem;
            box-shadow: 0 4px 20px rgba(78, 54, 41, 0.10);
            border-left: 6px solid #A98467;
            margin-bottom: 1rem;
        }

        /* ── Label kategori di dalam kartu ─────────────────────── */
        .result-class-label {
            font-size: 1.5rem;
            font-weight: 700;
            color: #4E3629;
            margin: 0;
        }

        /* ── Teks deskripsi & saran ─────────────────────────────── */
        .result-description {
            font-size: 0.92rem;
            color: #5A4033;
            line-height: 1.65;
            margin-top: 0.5rem;
        }

        /* ── Footer kecil ───────────────────────────────────────── */
        .kopita-footer {
            text-align: center;
            color: #A89080;
            font-size: 0.78rem;
            margin-top: 1.5rem;
        }

        /* ── Sidebar styling ────────────────────────────────────── */
        section[data-testid="stSidebar"] {
            background-color: #F3EBE1;
        }

        /* ── Gauge bar container ─────────────────────────────────── */
        .gauge-wrapper {
            margin: 1rem 0 0.5rem 0;
        }
        .gauge-label-row {
            display: flex;
            justify-content: space-between;
            font-size: 0.82rem;
            color: #7F5A44;
            margin-bottom: 4px;
            font-weight: 500;
        }
        .gauge-track {
            background-color: #E8DDD4;
            border-radius: 999px;
            height: 22px;
            width: 100%;
            overflow: hidden;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.08);
        }
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
            transition: width 0.6s ease-in-out;
            min-width: 40px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_maturity_gauge(prediction: str, confidence_str: str) -> None:
    """
    Merender bilah kematangan dinamis (Maturity Gauge).

    Warna bilah menyesuaikan kelas prediksi dari backend:
      - Green  → #2E7D32 (hijau segar)
      - Light  → #D4A373 (cokelat keemasan)
      - Medium → #A98467 (cokelat hangat)
      - Dark   → #4E3629 (cokelat gelap)

    Args:
        prediction    : Nama kelas hasil prediksi (misal "Medium").
        confidence_str: String persentase dari API (misal "98.42%").
    """
    # Ambil nilai numerik dari string "98.42%" → 98.42
    try:
        conf_value: float = float(confidence_str.replace("%", "").strip())
    except ValueError:
        conf_value = 0.0

    bar_color: str  = CLASS_COLORS.get(prediction, "#A98467")
    text_color: str = CLASS_TEXT_COLORS.get(prediction, "#FFFFFF")

    # Clamp ke rentang 0–100
    fill_pct: float = max(0.0, min(conf_value, 100.0))

    st.markdown(
        f"""
        <div class="gauge-wrapper">
            <div class="gauge-label-row">
                <span>Tingkat Keyakinan Model</span>
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

    Args:
        icon           : Emoji representasi kelas (misal "☕").
        label          : Label lengkap kelas (misal "Medium (Sangrai Sedang)").
        prediction     : Nama kelas mentah dari API (misal "Medium").
        description    : Deskripsi fisik biji kopi dari metadata backend.
        business_advice: Saran komersial UMKM dari metadata backend.
    """
    accent: str = CLASS_COLORS.get(prediction, "#A98467")

    st.markdown(
        f"""
        <div class="result-card" style="border-left-color:{accent};">
            <p class="result-class-label">{icon} {label}</p>
            <p class="result-description"><b>Deskripsi Fisik:</b><br>{description}</p>
            <hr style="border:none;border-top:1px solid #EDE0D4;margin:0.8rem 0;">
            <p class="result-description"><b>Rekomendasi UMKM:</b><br>{business_advice}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_guidelines() -> None:
    """
    Merender panduan pengambilan foto biji kopi di sidebar.
    Menggunakan st.expander agar tidak memenuhi layar secara default.
    Dipanggil dari ui.py sebelum komponen utama dirender.
    """
    with st.sidebar:
        st.markdown(
            "<h3 style='color:#4E3629;'>☕ Kopita</h3>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='color:#7F5A44;font-size:0.85rem;'>"
            "AI Penilai Kualitas Kopi<br>untuk UMKM Roastery Toraja"
            "</p>",
            unsafe_allow_html=True
        )
        st.divider()

        with st.expander("📷 Panduan Memotret Biji Kopi", expanded=True):
            st.markdown(
                """
                Ikuti panduan berikut untuk mendapatkan hasil analisis **paling akurat**:

                **📏 Jarak**
                Ambil foto tegak lurus dari atas dengan jarak sekitar **10–15 cm** dari objek biji kopi.

                **💡 Pencahayaan**
                Pastikan cahaya cukup **terang dan merata**. Hindari bayangan ekstrem atau pencahayaan dari satu sisi saja.

                **🔍 Fokus**
                Pastikan kamera **fokus penuh** pada sebaran biji kopi — bukan pada latar belakang atau wadah.

                ---
                <small style='color:#A89080;'>
                Model dilatih pada resolusi <b>224×224 px</b>.
                Gambar terlalu gelap atau buram dapat menurunkan akurasi prediksi.
                </small>
                """,
                unsafe_allow_html=True
            )

        st.divider()
        st.markdown(
            "<p style='color:#A89080;font-size:0.75rem;text-align:center;'>"
            "AIC DCC Hackathon 2026<br>Tim AIC DCC Juara"
            "</p>",
            unsafe_allow_html=True
        )
