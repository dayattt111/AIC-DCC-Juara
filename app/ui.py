"""
app/ui.py — Kopita Frontend Portal
=====================================
Antarmuka pengguna utama berbasis Streamlit untuk aplikasi Kopita.
Menerapkan alur: Upload Gambar → Analisis → Tampilkan Prediksi.

Aturan (.rules.md):
  - TIDAK mengimpor torch, torchvision, atau library AI apapun.
  - TIDAK memuat berkas model .pth secara langsung.
  - Semua inferensi terjadi di backend via app/api_client.py.
  - Gaya visual dikelola secara terpusat oleh app/style.py.
"""

import sys
import os
from pathlib import Path

import streamlit as st
from PIL import Image

# Pastikan direktori root proyek ada di path agar import app.* berjalan
# baik saat dijalankan lokal maupun di dalam container Docker.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.api_client import predict_image, check_health, PredictResult, APIError
from app import style

# =============================================================
# KONFIGURASI HALAMAN — wajib dipanggil PERTAMA sebelum apapun
# REBRANDING: page_title menggunakan nama publik "Kopita"
# (lihat docs/REBRAND_GUIDE.md)
# =============================================================
st.set_page_config(
    page_title="Kopita - Cerdas Menilai Kopi",
    page_icon="☕",
    layout="wide",
)

# Suntikkan CSS global tema Warm Earthy Espresso
# (.rules.md Section 3B: UI feedback & visual state)
style.inject_global_css()

# Render sidebar: branding + panduan foto
# (Fitur 3: Panduan Pengambilan Gambar di Sidebar)
style.render_sidebar_guidelines()


# =============================================================
# KONFIGURASI STATIS — di-cache agar tidak di-reload tiap render
# (.rules.md Section 3B point 1: wajib @st.cache_resource / @st.cache_data)
# =============================================================
@st.cache_data
def get_class_config() -> dict:
    """Mapping ikon dan label tampilan per kelas prediksi."""
    return {
        "Dark":   {"icon": "🖤", "label": "Dark (Sangrai Tua)"},
        "Green":  {"icon": "🌿", "label": "Green (Biji Mentah)"},
        "Light":  {"icon": "🌟", "label": "Light (Sangrai Muda)"},
        "Medium": {"icon": "☕", "label": "Medium (Sangrai Sedang)"},
    }

@st.cache_data
def _load_image_from_path(path: str) -> Image.Image | None:
    """Muat gambar statis dari path — di-cache agar tidak dibaca berulang."""
    try:
        return Image.open(path)
    except Exception:
        return None


# =============================================================
# HEADER UTAMA
# =============================================================
st.markdown(
    "<h1 class='kopita-title'>☕ Kopita</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p class='kopita-subtitle'>"
    "AI Penilai Kualitas Kopi untuk Transaksi Adil UMKM Roastery Toraja"
    "</p>",
    unsafe_allow_html=True
)

# Indikator status backend — cek koneksi tanpa mengganggu alur utama
if not check_health():
    st.warning(
        "⚠️ **Backend tidak terdeteksi.** "
        "Jalankan `uvicorn app.main:app --port 8000` di terminal.",
        icon="🔌"
    )

st.divider()


# =============================================================
# LAYOUT UTAMA: 2 KOLOM
# Kolom kiri  (40%) : Upload gambar + pratinjau + info metadata
# Kolom kanan (60%) : Tab hasil analisis + metrik model
# (.rules.md Section 3B point 2: Satu Layar Utama MVP)
# =============================================================
col_left, col_right = st.columns([4, 6], gap="large")

with col_left:
    st.markdown("#### 📷 Unggah Foto Biji Kopi")

    uploaded_file = st.file_uploader(
        "Format: JPG / PNG",
        type=["jpg", "jpeg", "png"],
        label_visibility="visible",
        help="Foto terbaik: tegak lurus dari atas, pencahayaan merata, fokus pada biji.",
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(
            image,
            caption="📸 Pratinjau Gambar",
            use_column_width=True,   # Streamlit 1.32.0 — use_column_width
        )

        # Metadata gambar
        with st.expander("ℹ️ Detail Berkas", expanded=False):
            st.markdown(f"- **Nama:** `{uploaded_file.name}`")
            st.markdown(f"- **Ukuran:** `{uploaded_file.size / 1024:.1f} KB`")
            st.markdown(f"- **Dimensi:** `{image.width} × {image.height} px`")
            st.markdown(f"- **Mode warna:** `{image.mode}`")
            st.markdown(
                "<small style='color:#A89080;'>"
                "Model meresize otomatis ke <b>224×224 px</b>.</small>",
                unsafe_allow_html=True
            )

        st.write("")
        # ─── TOMBOL ANALISIS ──────────────────────────────────────────────
        # (.rules.md Section 3B: Unggah → Tombol → Tampilkan Prediksi)
        analyze_clicked = st.button(
            "🔍 Mulai Analisis Kopi",
            type="primary",
            use_container_width=True,
        )
    else:
        st.info(
            "Unggah foto biji kopi Anda di atas untuk memulai analisis AI.",
            icon="☕"
        )
        analyze_clicked = False


# ─── KOLOM KANAN: Tab Hasil & Metrik ──────────────────────────────────────────
with col_right:
    # (Fitur 2: Tab Interaktif Hasil dan Metrik Model)
    tab_result, tab_metrics = st.tabs(
        ["📊 Hasil Analisis", "🔬 Metrik Model & Bukti Ilmiah"]
    )

    # ── TAB 1: HASIL ANALISIS ─────────────────────────────────────────────────
    with tab_result:
        if uploaded_file is None:
            st.markdown(
                "<div style='text-align:center;padding:3rem 1rem;color:#A89080;'>"
                "<p style='font-size:3rem;'>☕</p>"
                "<p>Hasil analisis akan muncul di sini<br>"
                "setelah Anda mengunggah foto dan menekan <b>Mulai Analisis</b>.</p>"
                "</div>",
                unsafe_allow_html=True
            )

        elif uploaded_file is not None and not analyze_clicked:
            st.markdown(
                "<div style='text-align:center;padding:2rem 1rem;color:#A89080;'>"
                "<p style='font-size:2.5rem;'>🔍</p>"
                "<p>Foto sudah diunggah.<br>"
                "Tekan <b>Mulai Analisis Kopi</b> untuk mendapatkan prediksi.</p>"
                "</div>",
                unsafe_allow_html=True
            )

        elif analyze_clicked:
            with st.spinner("⏳ Model AI Kopita sedang menganalisis..."):
                result = predict_image(
                    filename=uploaded_file.name,
                    file_bytes=uploaded_file.getvalue(),
                    content_type=uploaded_file.type,
                )

            # ── SUKSES ────────────────────────────────────────────────────────
            if isinstance(result, PredictResult):
                class_cfg = get_class_config()
                pred  = result.prediction
                conf  = result.confidence
                icon  = class_cfg.get(pred, {}).get("icon", "☕")
                label = class_cfg.get(pred, {}).get("label", pred)

                # Kartu hasil dengan warna aksen dinamis
                # (Fitur 1 & Fitur 2 — Tab Hasil Analisis)
                style.render_result_card(
                    icon=icon,
                    label=label,
                    prediction=pred,
                    description=result.detail,
                    business_advice=result.rekomendasi_bisnis,
                )

                # Meteran kematangan dinamis
                # (Fitur 1: Maturity Gauge)
                style.render_maturity_gauge(
                    prediction=pred,
                    confidence_str=conf,
                )

                # Metric tiles
                m1, m2 = st.columns(2)
                with m1:
                    st.metric(
                        label="🎯 Keyakinan Model",
                        value=conf,
                        help="Skor Softmax MobileNetV3-Small — semakin tinggi semakin yakin."
                    )
                with m2:
                    st.metric(
                        label="🏷️ Kelas Terdeteksi",
                        value=pred,
                    )

                st.markdown(
                    "<p class='kopita-footer'>"
                    "Inferensi: MobileNetV3-Small (CPU) · Kopita API Engine · Akurasi 97%+"
                    "</p>",
                    unsafe_allow_html=True
                )

            # ── ERROR ─────────────────────────────────────────────────────────
            elif isinstance(result, APIError):
                if result.http_status == 400:
                    st.error(f"❌ **Format Tidak Valid:** {result.message}")
                elif result.http_status == 500:
                    st.error(f"🔴 **Error Server (500):** {result.message}")
                elif result.http_status == 0:
                    st.error(f"🔌 **Koneksi Gagal!**\n\n{result.message}")
                elif result.http_status == 408:
                    st.error(f"⏱️ **Request Timeout:** {result.message}")
                else:
                    st.error(f"⚠️ **Error tak terduga (HTTP {result.http_status}):** {result.message}")

    # ── TAB 2: METRIK MODEL & BUKTI ILMIAH ───────────────────────────────────
    # (Fitur 2: Tab Metrik Model)
    with tab_metrics:
        st.markdown("### 📈 Grafik Evaluasi Pelatihan Model")
        st.markdown(
            "Grafik di bawah menunjukkan kurva *training loss* dan *validation accuracy* "
            "selama **15 epoch** pelatihan model **MobileNetV3-Small** di Google Colab GPU T4."
        )

        # Path relatif dari root proyek ke gambar training metrics
        _METRICS_PATH = str(
            Path(__file__).resolve().parent.parent
            / "notebooks" / "images" / "training_metrics.png"
        )
        _CONFMAT_PATH = str(
            Path(__file__).resolve().parent.parent
            / "notebooks" / "evaluation" / "torajigrade_confusion_matrix.png"
        )

        metrics_img = _load_image_from_path(_METRICS_PATH)
        if metrics_img is not None:
            st.image(
                metrics_img,
                caption="Kurva Training & Validation — MobileNetV3-Small (15 Epoch)",
                use_column_width=True,
            )
        else:
            st.warning("Gambar metrik pelatihan tidak ditemukan di `notebooks/images/training_metrics.png`.")

        st.divider()
        st.markdown("### 🧩 Confusion Matrix")
        st.markdown(
            "Confusion matrix di bawah memvisualisasikan distribusi prediksi model "
            "pada **validation/test set** — membuktikan akurasi **97%+** secara ilmiah."
        )

        confmat_img = _load_image_from_path(_CONFMAT_PATH)
        if confmat_img is not None:
            st.image(
                confmat_img,
                caption="Confusion Matrix — 4 Kelas: Dark, Green, Light, Medium",
                use_column_width=True,
            )
        else:
            st.warning("Confusion matrix tidak ditemukan di `notebooks/evaluation/torajigrade_confusion_matrix.png`.")

        st.divider()
        st.markdown("### 🔬 Spesifikasi Teknis Model")
        spec_col1, spec_col2 = st.columns(2)
        with spec_col1:
            st.markdown("""
            | Parameter | Nilai |
            |:---|:---|
            | Arsitektur | MobileNetV3-Small |
            | Task | Multi-class Classification |
            | Kelas | Dark · Green · Light · Medium |
            | Input | RGB 224×224 px |
            """)
        with spec_col2:
            st.markdown("""
            | Parameter | Nilai |
            |:---|:---|
            | Optimizer | Adam |
            | Scheduler | CosineAnnealingLR |
            | Epoch | 15 |
            | Akurasi | **97%+** |
            """)
