"""
app/ui.py -- Kopita Frontend Portal
=====================================
Antarmuka pengguna utama Kopita berbasis Streamlit.
Alur: Upload Gambar -> Analisis -> Tampilkan Prediksi & Metrik.

Aturan (.rules.md):
  - TIDAK mengimpor torch, torchvision, atau library AI apapun.
  - TIDAK memuat berkas model .pth secara langsung.
  - Semua inferensi terjadi di backend melalui app/api_client.py.
  - Gaya visual dikelola terpusat oleh app/style.py.
  - Tidak ada emoji di seluruh teks antarmuka.

REBRAND (docs/REBRAND_GUIDE.md):
  - Nama publik: Kopita
  - Nama file model backend: best_torajigrade_model.pth (JANGAN DIUBAH)
  - Variabel kelas backend: CLASSES (JANGAN DIUBAH)
"""

import sys
from pathlib import Path

import streamlit as st
from PIL import Image

# Pastikan root proyek ada di sys.path agar import app.* berjalan
# baik saat lokal maupun di dalam container Docker.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.api_client import predict_image, check_health, PredictResult, APIError
from app import style


# =============================================================
# KONFIGURASI HALAMAN
# Wajib dipanggil PERTAMA sebelum widget apapun.
# REBRANDING: page_title menggunakan nama publik "Kopita".
# (lihat docs/REBRAND_GUIDE.md -- jangan ubah backend paths)
# =============================================================
st.set_page_config(
    page_title="Kopita - AI Cerdas, Transaksi Pas, Kopi Berkualitas",
    page_icon="assets/logo.png" if (Path(_ROOT / "logo.png")).exists() else None,
    layout="wide",
)

# Suntikkan CSS global tema Warm Earthy Espresso
# (.rules.md Section 3B: UI feedback & visual state)
style.inject_global_css()


# =============================================================
# FUNGSI HELPER -- di-cache (.rules.md Section 3B point 1)
# =============================================================

@st.cache_data
def get_class_config() -> dict:
    """Mapping label tampilan per kelas prediksi (tanpa emoji)."""
    return {
        "Dark":   {"label": "Dark  --  Sangrai Tua"},
        "Green":  {"label": "Green  --  Biji Mentah"},
        "Light":  {"label": "Light  --  Sangrai Muda"},
        "Medium": {"label": "Medium  --  Sangrai Sedang"},
    }


@st.cache_data
def _load_image_from_path(path: str) -> Image.Image | None:
    """Muat gambar statis dari path absolut -- di-cache agar efisien."""
    try:
        return Image.open(path)
    except Exception:
        return None


@st.cache_data
def _load_logo() -> Image.Image | None:
    """
    Muat logo resmi Kopita dari root proyek.
    Mencoba 'logo.png' (nama aktual yang tersedia di repositori).

    CATATAN KEAMANAN (docs/REBRAND_GUIDE.md):
      - Hanya memuat berkas gambar logo UI -- BUKAN model .pth.
      - Tidak mengubah jalur model/best_torajigrade_model.pth.
    """
    for name in ("logo-kopita.png", "logo.png"):
        p = _ROOT / name
        if p.exists():
            try:
                return Image.open(str(p))
            except Exception:
                continue
    return None


# =============================================================
# SIDEBAR -- Render termasuk logo
# =============================================================
_logo = _load_logo()
style.render_sidebar_content(logo_image=_logo)


# =============================================================
# HEADER UTAMA: Logo + Judul + Tagline + Misi
# =============================================================

# Logo di halaman utama -- centered via kolom padding
if _logo is not None:
    _lc, _mc, _rc = st.columns([2, 3, 2])
    with _mc:
        st.image(_logo, use_column_width=True)  # Streamlit 1.32.0

# Judul -- Deep Espresso (#472D2D)
st.markdown(
    "<h1 class='kopita-title'>Kopita</h1>",
    unsafe_allow_html=True,
)

# Tagline resmi
st.markdown(
    "<p class='kopita-tagline'>AI Cerdas, Transaksi Pas, Kopi Berkualitas</p>",
    unsafe_allow_html=True,
)

# Deskripsi misi -- filosofi keadilan transaksi UMKM
st.markdown(
    """
    <p class='kopita-mission'>
    Kopita hadir untuk mengakhiri penilaian kualitas kopi yang subjektif
    dan tidak terstandar. Dengan teknologi <em>computer vision</em> berbasis AI,
    Kopita memberikan standarisasi objektif berbasis data nyata
    &mdash; mewujudkan transaksi yang <strong>transparan dan adil</strong>
    bagi petani kopi dan UMKM roastery di Toraja, Sulawesi Selatan.
    </p>
    """,
    unsafe_allow_html=True,
)

st.divider()

# Indikator status backend (tanpa emoji -- teks bersih)
if not check_health():
    style.render_error_box(
        message=(
            "Backend FastAPI tidak terdeteksi. "
            "Jalankan perintah berikut di terminal:<br>"
            "<code>uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload</code>"
        ),
        label="Koneksi Gagal",
    )


# =============================================================
# LAYOUT UTAMA: 2 KOLOM
# Kiri  (40%): Upload gambar + pratinjau + metadata + tombol
# Kanan (60%): Tab hasil analisis + metrik model ilmiah
# (.rules.md Section 3B point 2: Satu Layar Utama MVP)
# =============================================================
col_left, col_right = st.columns([4, 6], gap="large")

with col_left:
    st.markdown(
        "<p style='font-size:0.95rem;font-weight:600;"
        "color:#472D2D;margin-bottom:0.4rem;'>Unggah Foto Biji Kopi</p>",
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Format yang didukung: JPG, JPEG, PNG",
        type=["jpg", "jpeg", "png"],
        label_visibility="visible",
        help="Foto terbaik: tegak lurus dari atas, pencahayaan merata, fokus pada biji.",
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(
            image,
            caption="Pratinjau Gambar",
            use_column_width=True,  # Streamlit 1.32.0
        )

        # Metadata gambar -- kotak info kustom (bukan st.info)
        with st.expander("Detail Berkas", expanded=False):
            st.markdown(f"- **Nama:** `{uploaded_file.name}`")
            st.markdown(f"- **Ukuran:** `{uploaded_file.size / 1024:.1f} KB`")
            st.markdown(f"- **Dimensi:** `{image.width} x {image.height} px`")
            st.markdown(f"- **Mode warna:** `{image.mode}`")
            st.markdown(
                "<small style='color:#704F4F;'>"
                "Model meresize otomatis ke <b>224 x 224 px</b>."
                "</small>",
                unsafe_allow_html=True,
            )

        st.write("")

        # Tombol Analisis -- CTA Earthy Rose (#A77979)
        # (.rules.md Section 3B: Unggah -> Tombol -> Tampilkan Prediksi)
        analyze_clicked = st.button(
            "Mulai Analisis Kopi",
            type="primary",
        )
    else:
        # Placeholder saat belum ada file -- kotak info kustom
        style.render_info_box(
            message=(
                "Unggah foto biji kopi di atas untuk memulai analisis AI Kopita. "
                "Pastikan foto diambil dengan pencahayaan merata dan kamera fokus "
                "pada permukaan biji kopi."
            ),
            label="Petunjuk",
        )
        analyze_clicked = False


# =============================================================
# KOLOM KANAN: Tab Hasil Analisis & Metrik Model
# =============================================================
with col_right:
    tab_result, tab_metrics = st.tabs(
        ["Hasil Analisis", "Metrik Model  &  Bukti Ilmiah"]
    )

    # ----------------------------------------------------------
    # TAB 1: HASIL ANALISIS
    # ----------------------------------------------------------
    with tab_result:

        if uploaded_file is None:
            st.markdown(
                """
                <div style="text-align:center;padding:3rem 1rem;">
                    <p style="font-size:1.8rem;color:#EDE0D4;
                               font-weight:700;letter-spacing:-0.5px;">
                        Kopita
                    </p>
                    <p style="color:#A77979;font-size:0.9rem;line-height:1.7;">
                        Hasil analisis akan muncul di sini setelah<br>
                        foto biji kopi diunggah dan dianalisis.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        elif uploaded_file is not None and not analyze_clicked:
            style.render_info_box(
                message=(
                    "Foto sudah diunggah. "
                    "Tekan <b>Mulai Analisis Kopi</b> di kolom kiri "
                    "untuk mendapatkan prediksi tingkat sangrai."
                ),
                label="Siap Dianalisis",
            )

        elif analyze_clicked:
            with st.spinner("Model AI Kopita sedang menganalisis gambar..."):
                result = predict_image(
                    filename=uploaded_file.name,
                    file_bytes=uploaded_file.getvalue(),
                    content_type=uploaded_file.type,
                )

            # ── SUKSES ────────────────────────────────────────────
            if isinstance(result, PredictResult):
                class_cfg  = get_class_config()
                pred       = result.prediction
                conf       = result.confidence
                label_text = class_cfg.get(pred, {}).get("label", pred)

                # Kartu hasil grid -- TANPA emoji, layout bersih
                style.render_result_card(
                    label=label_text,
                    prediction=pred,
                    confidence=conf,
                    description=result.detail,
                    business_advice=result.rekomendasi_bisnis,
                )

                # Meteran kematangan dinamis
                style.render_maturity_gauge(
                    prediction=pred,
                    confidence_str=conf,
                )

                # Metric tiles Streamlit (styled via CSS)
                m1, m2 = st.columns(2)
                with m1:
                    st.metric(
                        label="Keyakinan Model",
                        value=conf,
                        help="Skor Softmax MobileNetV3-Small."
                    )
                with m2:
                    st.metric(
                        label="Kelas Terdeteksi",
                        value=pred,
                    )

                st.markdown(
                    "<p class='kopita-footer'>"
                    "Inferensi: MobileNetV3-Small (CPU)  |  "
                    "Kopita API Engine  |  Akurasi 97%+"
                    "</p>",
                    unsafe_allow_html=True,
                )

            # ── ERROR ─────────────────────────────────────────────
            elif isinstance(result, APIError):
                if result.http_status == 400:
                    style.render_error_box(
                        message=result.message,
                        label="Format Berkas Tidak Valid",
                    )
                elif result.http_status == 500:
                    style.render_error_box(
                        message=result.message,
                        label="Error Internal Server (500)",
                    )
                elif result.http_status == 0:
                    style.render_error_box(
                        message=result.message,
                        label="Koneksi ke Backend Gagal",
                    )
                elif result.http_status == 408:
                    style.render_error_box(
                        message=result.message,
                        label="Request Timeout",
                    )
                else:
                    style.render_error_box(
                        message=f"HTTP {result.http_status}: {result.message}",
                        label="Error Tidak Terduga",
                    )

    # ----------------------------------------------------------
    # TAB 2: METRIK MODEL & BUKTI ILMIAH
    # ----------------------------------------------------------
    with tab_metrics:

        st.markdown(
            "<p style='font-size:1rem;font-weight:700;color:#472D2D;"
            "margin-bottom:0.3rem;'>Grafik Evaluasi Pelatihan Model</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='font-size:0.87rem;color:#704F4F;line-height:1.65;"
            "margin-bottom:1rem;'>"
            "Grafik kurva <em>training loss</em> dan <em>validation accuracy</em> "
            "selama 15 epoch pelatihan MobileNetV3-Small di Google Colab GPU T4."
            "</p>",
            unsafe_allow_html=True,
        )

        _METRICS_PATH = str(
            _ROOT / "notebooks" / "images" / "training_metrics.png"
        )
        _CONFMAT_PATH = str(
            _ROOT / "notebooks" / "evaluation" / "torajigrade_confusion_matrix.png"
        )

        metrics_img = _load_image_from_path(_METRICS_PATH)
        if metrics_img is not None:
            st.image(
                metrics_img,
                caption="Kurva Training & Validation -- MobileNetV3-Small (15 Epoch)",
                use_column_width=True,
            )
        else:
            style.render_error_box(
                message="File tidak ditemukan: notebooks/images/training_metrics.png",
                label="Gambar Tidak Tersedia",
            )

        st.divider()

        st.markdown(
            "<p style='font-size:1rem;font-weight:700;color:#472D2D;"
            "margin-bottom:0.3rem;'>Confusion Matrix</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='font-size:0.87rem;color:#704F4F;line-height:1.65;"
            "margin-bottom:1rem;'>"
            "Visualisasi distribusi prediksi pada validation/test set "
            "-- membuktikan akurasi <strong>97%+</strong> secara ilmiah."
            "</p>",
            unsafe_allow_html=True,
        )

        confmat_img = _load_image_from_path(_CONFMAT_PATH)
        if confmat_img is not None:
            st.image(
                confmat_img,
                caption="Confusion Matrix -- 4 Kelas: Dark, Green, Light, Medium",
                use_column_width=True,
            )
        else:
            style.render_error_box(
                message="File tidak ditemukan: notebooks/evaluation/torajigrade_confusion_matrix.png",
                label="Gambar Tidak Tersedia",
            )

        st.divider()

        st.markdown(
            "<p style='font-size:1rem;font-weight:700;color:#472D2D;"
            "margin-bottom:0.8rem;'>Spesifikasi Teknis Model</p>",
            unsafe_allow_html=True,
        )

        spec_col1, spec_col2 = st.columns(2)
        with spec_col1:
            st.markdown(
                """
                | Parameter | Nilai |
                |:---|:---|
                | Arsitektur | MobileNetV3-Small |
                | Task | Multi-class Classification |
                | Kelas Output | Dark, Green, Light, Medium |
                | Input Tensor | RGB 224 x 224 px |
                """
            )
        with spec_col2:
            st.markdown(
                """
                | Parameter | Nilai |
                |:---|:---|
                | Optimizer | Adam |
                | Scheduler | CosineAnnealingLR |
                | Epoch Pelatihan | 15 |
                | Akurasi Validasi | **97%+** |
                """
            )
