import streamlit as st
import requests
from PIL import Image

# =============================================================
# KONFIGURASI HALAMAN
# REBRANDING: page_title & UI menggunakan nama publik "Kopita"
# (lihat docs/REBRAND_GUIDE.md — frontend wajib tampilkan Kopita)
# =============================================================
st.set_page_config(
    page_title="Kopita - Cerdas Menilai Kopi",
    page_icon="☕",
    layout="centered"
)

# =============================================================
# KONFIGURASI STATIS — di-cache agar tidak di-reload tiap interaksi
# (.rules.md Section 3B point 1: wajib @st.cache_resource / @st.cache_data)
# =============================================================
@st.cache_data
def get_class_config() -> dict:
    """Mapping ikon dan label kelas yang ditampilkan ke pengguna."""
    return {
        "Dark":   {"icon": "🖤", "label": "Dark (Sangrai Tua)"},
        "Green":  {"icon": "🌿", "label": "Green (Biji Mentah)"},
        "Light":  {"icon": "🌟", "label": "Light (Sangrai Muda)"},
        "Medium": {"icon": "☕", "label": "Medium (Sangrai Sedang)"},
    }

@st.cache_data
def get_api_url() -> str:
    """URL backend FastAPI — terpusat agar mudah diubah."""
    return "http://127.0.0.1:8000/predict"


# =============================================================
# HEADER UTAMA
# =============================================================
st.markdown(
    "<h1 style='text-align: center; color: #4E3629;'>☕ Kopita</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center; color: #7F5A44;'>"
    "<b>AI Penilai Kualitas Kopi untuk Transaksi Adil UMKM Roastery Toraja</b>"
    "</p>",
    unsafe_allow_html=True
)
st.write("---")

# =============================================================
# PANEL UPLOAD GAMBAR
# (.rules.md Section 3B point 2: Satu Layar Utama MVP)
# =============================================================
uploaded_file = st.file_uploader(
    "📷 Unggah foto biji kopi Anda (JPG / PNG)",
    type=["jpg", "jpeg", "png"],
    help="Foto terbaik: tampak atas, pencahayaan merata, fokus pada biji kopi."
)

if uploaded_file is not None:
    # Tampilkan pratinjau gambar yang diunggah
    image = Image.open(uploaded_file)
    col_img, col_info = st.columns([1, 1])

    with col_img:
        st.image(
            image,
            caption="📸 Biji Kopi yang Diunggah",
            use_column_width=True  # Streamlit 1.32.0 — use_column_width
        )

    with col_info:
        st.markdown("#### ℹ️ Info Gambar")
        st.markdown(f"- **Nama berkas:** `{uploaded_file.name}`")
        st.markdown(f"- **Ukuran:** `{uploaded_file.size / 1024:.1f} KB`")
        st.markdown(f"- **Dimensi:** `{image.width} × {image.height} px`")
        st.markdown(f"- **Mode:** `{image.mode}`")
        st.markdown("---")
        st.markdown(
            "<small style='color:#888;'>Model akan meresize gambar ke "
            "<b>224×224 px</b> secara otomatis sesuai spesifikasi input "
            "MobileNetV3-Small.</small>",
            unsafe_allow_html=True
        )

    st.write("")

    # ─── TOMBOL ANALISIS ─────────────────────────────────────────────────────
    # (.rules.md Section 3B: Unggah → Tombol → Tampilkan Prediksi)
    if st.button("🔍 Mulai Analisis Kopi", use_container_width=False):
        with st.spinner("⏳ Model AI Kopita sedang menganalisis foto biji kopi Anda..."):
            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
            }
            try:
                response = requests.post(get_api_url(), files=files, timeout=30)

                # ─── HASIL SUKSES ─────────────────────────────────────────────
                if response.status_code == 200:
                    result = response.json()
                    class_cfg = get_class_config()
                    pred  = result["prediction"]
                    conf  = result["confidence"]
                    icon  = class_cfg.get(pred, {}).get("icon", "☕")
                    label = class_cfg.get(pred, {}).get("label", pred)

                    st.write("---")

                    # Kartu hasil utama
                    st.success(f"## {icon} Hasil Prediksi: **{label}**")

                    # Confidence score sebagai metric
                    col_conf, col_kelas = st.columns(2)
                    with col_conf:
                        st.metric(
                            label="🎯 Tingkat Keyakinan Model",
                            value=conf,
                            help="Skor softmax dari MobileNetV3-Small (semakin tinggi = semakin yakin)"
                        )
                    with col_kelas:
                        st.metric(
                            label="🏷️ Kategori Kelas",
                            value=pred,
                        )

                    st.write("")

                    # Detail tekstur biji kopi
                    st.markdown("### 📊 Analisis Tekstur & Tingkat Sangrai")
                    st.info(f"**Deskripsi Fisik:**\n\n{result['detail']}")

                    # Rekomendasi bisnis UMKM
                    st.markdown("### 💡 Rekomendasi Strategi Komersial UMKM")
                    st.warning(f"**Saran Bisnis:**\n\n{result['rekomendasi_bisnis']}")

                    st.write("---")
                    st.markdown(
                        "<small style='color:#888;'>⚙️ Inferensi dijalankan oleh "
                        "MobileNetV3-Small (CPU) via Kopita API Engine. "
                        "Akurasi model: 97%+ pada dataset uji.</small>",
                        unsafe_allow_html=True
                    )

                # ─── ERROR DARI SERVER (400 / 500) ────────────────────────────
                elif response.status_code == 400:
                    err = response.json().get("detail", "Format berkas tidak valid.")
                    st.error(f"❌ **Berkas Tidak Valid:** {err}")

                elif response.status_code == 500:
                    err = response.json().get("detail", "Terjadi kesalahan internal.")
                    st.error(f"🔴 **Error Server (500):** {err}")

                else:
                    st.error(
                        f"⚠️ Server merespons dengan status tak terduga: "
                        f"`HTTP {response.status_code}`"
                    )

            # ─── ERROR KONEKSI ─────────────────────────────────────────────────
            except requests.exceptions.ConnectionError:
                st.error(
                    "🔌 **Koneksi Gagal!** Backend FastAPI tidak dapat dijangkau.\n\n"
                    "Pastikan server sudah berjalan:\n"
                    "```bash\n"
                    "uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload\n"
                    "```"
                )
            except requests.exceptions.Timeout:
                st.error("⏱️ **Request Timeout!** Server terlalu lama merespons (>30 detik).")
            except Exception as e:
                st.error(f"🚨 **Error tidak terduga:** `{str(e)}`")
