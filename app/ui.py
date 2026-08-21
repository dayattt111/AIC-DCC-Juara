"""
app/ui.py -- Kopita Frontend Portal
=====================================
Antarmuka pengguna utama Kopita berbasis Streamlit.
Alur: Upload Gambar -> Analisis (Loading Spinner) -> Tampilkan Prediksi,
Telemetri Teknis, dan Metrik Ilmiah.

Tab Antarmuka:
  1. Hasil Analisis               (User / Business View)
  2. Analisis Teknis & Telemetri  (Engineering / Technical View)
  3. Metrik Model & Bukti Ilmiah  (Scientific / Evaluation View)

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
import warnings
from pathlib import Path

# Untuk mengaktifkan kembali peringatan di terminal, beri tanda pagar (#) pada baris di bawah:
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*expire_cache.*")

import streamlit as st
from PIL import Image

# Pastikan root proyek ada di sys.path agar import app.* berjalan
# baik saat lokal maupun di dalam container Docker.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.api_client import predict_image, check_health, PredictResult, APIError
from app import style


def _html(raw_html: str) -> None:
    """
    Helper lokal untuk merender string HTML bersih.
    Menghapus semua newline dan indentasi agar Markdown parser
    TIDAK PERNAH menginterpretasikannya sebagai Indented Code Block (<pre><code>).
    """
    clean = "".join(line.strip() for line in raw_html.strip().splitlines())
    st.markdown(clean, unsafe_allow_html=True)


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
    Mencoba 'logo-kopita.png' lalu fallback ke 'logo.png'.

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
_html("<h1 class='kopita-title'>Kopita</h1>")

# Tagline resmi
_html("<p class='kopita-tagline'>AI Cerdas, Transaksi Pas, Kopi Berkualitas</p>")

# Deskripsi misi -- filosofi keadilan transaksi UMKM
_html("""
<p class='kopita-mission'>
Kopita hadir untuk mengakhiri penilaian kualitas kopi yang subjektif
dan tidak terstandar. Dengan teknologi <em>computer vision</em> berbasis AI,
Kopita memberikan standarisasi objektif berbasis data nyata
&mdash; mewujudkan transaksi yang <strong>transparan dan adil</strong>
bagi petani kopi dan UMKM roastery di Toraja, Sulawesi Selatan.
</p>
""")

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
# Kanan (60%): 3 Tab Analisis (User, Teknis, Ilmiah)
# =============================================================
col_left, col_right = st.columns([4, 6], gap="large")

with col_left:
    _html("<p style='font-size:0.95rem;font-weight:600;color:#472D2D;margin-bottom:0.4rem;'>Unggah Foto Biji Kopi</p>")

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

        # Metadata gambar
        with st.expander("Detail Berkas", expanded=False):
            st.markdown(f"- **Nama:** `{uploaded_file.name}`")
            st.markdown(f"- **Ukuran:** `{uploaded_file.size / 1024:.1f} KB`")
            st.markdown(f"- **Dimensi:** `{image.width} x {image.height} px`")
            st.markdown(f"- **Mode warna:** `{image.mode}`")
            _html("<small style='color:#704F4F;'>Model meresize otomatis ke <b>224 x 224 px</b>.</small>")

        st.write("")

        # Tombol Analisis -- CTA Earthy Rose (#A77979)
        analyze_clicked = st.button(
            "Mulai Analisis Kopi",
            type="primary",
        )
    else:
        style.render_info_box(
            message=(
                "Unggah foto biji kopi di atas untuk memulai analisis AI Kopita. "
                "Pastikan foto diambil dengan pencahayaan merata dan kamera fokus "
                "pada permukaan biji kopi."
            ),
            label="Petunjuk",
        )
        analyze_clicked = False


# Eksekusi inferensi dan simpan ke session_state agar persisten di seluruh tab
if analyze_clicked and uploaded_file is not None:
    with st.spinner("Model AI Kopita sedang menganalisis biji kopi..."):
        api_result = predict_image(
            filename=uploaded_file.name,
            file_bytes=uploaded_file.getvalue(),
            content_type=uploaded_file.type,
        )
        st.session_state["latest_result"] = api_result
        st.session_state["analyzed_file"] = uploaded_file.name
        st.session_state["image_meta"] = {
            "name": uploaded_file.name,
            "size_kb": f"{uploaded_file.size / 1024:.1f} KB",
            "dimensions": f"{image.width} x {image.height} px",
            "mode": image.mode,
            "content_type": uploaded_file.type,
        }

# Cek apakah ada hasil tersimpan untuk file saat ini
cached_result = st.session_state.get("latest_result")
if uploaded_file is None:
    cached_result = None
    if "latest_result" in st.session_state:
        del st.session_state["latest_result"]


# =============================================================
# KOLOM KANAN: 3 TAB LENGKAP
# =============================================================
with col_right:
    tab_user, tab_tech, tab_metrics = st.tabs(
        [
            "Hasil Analisis",
            "Analisis Teknis & Telemetri",
            "Metrik Model & Bukti Ilmiah",
        ]
    )

    # ----------------------------------------------------------
    # TAB 1: HASIL ANALISIS (USER / BUSINESS VIEW)
    # ----------------------------------------------------------
    with tab_user:
        if uploaded_file is None:
            _html("""
            <div style="text-align:center;padding:3rem 1rem;">
                <p style="font-size:1.8rem;color:#EDE0D4;font-weight:700;letter-spacing:-0.5px;">
                    Kopita
                </p>
                <p style="color:#A77979;font-size:0.9rem;line-height:1.7;">
                    Hasil analisis akan muncul di sini setelah<br>
                    foto biji kopi diunggah dan dianalisis.
                </p>
            </div>
            """)

        elif uploaded_file is not None and cached_result is None:
            style.render_info_box(
                message=(
                    "Foto sudah diunggah. "
                    "Tekan <b>Mulai Analisis Kopi</b> di kolom kiri "
                    "untuk mendapatkan prediksi tingkat sangrai."
                ),
                label="Siap Dianalisis",
            )

        elif cached_result is not None:
            if isinstance(cached_result, PredictResult):
                class_cfg  = get_class_config()
                pred       = cached_result.prediction
                conf       = cached_result.confidence
                label_text = class_cfg.get(pred, {}).get("label", pred)

                # Kartu hasil visual
                style.render_result_card(
                    label=label_text,
                    prediction=pred,
                    confidence=conf,
                    description=cached_result.detail,
                    business_advice=cached_result.rekomendasi_bisnis,
                )

                # Meteran kematangan dinamis
                style.render_maturity_gauge(
                    prediction=pred,
                    confidence_str=conf,
                )

                # Metric tiles Streamlit
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

                _html("<p class='kopita-footer'>Inferensi: MobileNetV3-Small (CPU)  |  Kopita API Engine  |  Akurasi 97%+</p>")

            elif isinstance(cached_result, APIError):
                style.render_error_box(
                    message=cached_result.message,
                    label=f"Error HTTP {cached_result.http_status}",
                )

    # ----------------------------------------------------------
    # TAB 2: ANALISIS TEKNIS & TELEMETRI (ENGINEERING VIEW)
    # ----------------------------------------------------------
    with tab_tech:
        _html("<p style='font-size:1rem;font-weight:700;color:#472D2D;margin-bottom:0.3rem;'>Telemetri Inferensi & Pipeline Teknis</p>")
        _html("""
        <p style='font-size:0.87rem;color:#704F4F;line-height:1.65;margin-bottom:1rem;'>
        Detail teknis proses inferensi, pipeline tensor, metadata HTTP,
        dan payload respon JSON murni dari backend FastAPI.
        </p>
        """)

        if cached_result is None:
            style.render_info_box(
                message="Data teknis akan ditampilkan secara otomatis setelah proses inferensi AI dijalankan.",
                label="Menunggu Eksekusi",
            )
        elif isinstance(cached_result, PredictResult):
            # 1. Metrik Telemetri Request
            tcol1, tcol2, tcol3, tcol4 = st.columns(4)
            with tcol1:
                st.metric(label="Roundtrip Latency", value=f"{cached_result.latency_ms} ms")
            with tcol2:
                st.metric(label="HTTP Status", value="200 OK")
            with tcol3:
                st.metric(label="Target Class", value=cached_result.prediction)
            with tcol4:
                st.metric(label="Softmax Score", value=cached_result.confidence)

            st.divider()

            # 2. Spesifikasi Pipeline Tensor & Komputasi
            _html("<p style='font-size:0.9rem;font-weight:700;color:#472D2D;margin-bottom:0.5rem;'>Pipeline Tensor & Preprocessing</p>")

            pcol1, pcol2 = st.columns(2)
            with pcol1:
                st.markdown(
                    """
                    | Parameter Pipeline | Nilai Teknis |
                    |:---|:---|
                    | Input Tensor Shape | `[1, 3, 224, 224]` |
                    | Data Type | `torch.float32` |
                    | Color Space | `RGB (3 Channels)` |
                    | Target Dimension | `224 x 224 px` (Bilinear Interpolation) |
                    """
                )
            with pcol2:
                st.markdown(
                    """
                    | Parameter Komputasi | Nilai Teknis |
                    |:---|:---|
                    | Normalization Mean | `[0.485, 0.456, 0.406]` (ImageNet) |
                    | Normalization Std | `[0.229, 0.224, 0.225]` (ImageNet) |
                    | Compute Device | `CPU (torch.device('cpu'))` |
                    | Activation Head | `Softmax(dim=0)` |
                    """
                )

            st.divider()

            # 3. Payload JSON Mentah dari API Backend
            _html("<p style='font-size:0.9rem;font-weight:700;color:#472D2D;margin-bottom:0.5rem;'>Raw JSON API Response (POST /predict)</p>")
            if cached_result.raw_response:
                st.json(cached_result.raw_response)

            # 4. Metadata Berkas Citra
            img_meta = st.session_state.get("image_meta", {})
            if img_meta:
                with st.expander("Metadata Berkas Citra Masukan", expanded=False):
                    st.markdown(f"- **Filename:** `{img_meta.get('name')}`")
                    st.markdown(f"- **MIME Type:** `{img_meta.get('content_type')}`")
                    st.markdown(f"- **Payload Size:** `{img_meta.get('size_kb')}`")
                    st.markdown(f"- **Original Dimensions:** `{img_meta.get('dimensions')}`")
                    st.markdown(f"- **Color Mode:** `{img_meta.get('mode')}`")

        elif isinstance(cached_result, APIError):
            style.render_error_box(
                message=f"HTTP Status: {cached_result.http_status}<br>Detail: {cached_result.message}",
                label="API Error Payload",
            )

    # ----------------------------------------------------------
    # TAB 3: METRIK MODEL & BUKTI ILMIAH (SCIENTIFIC VIEW)
    # ----------------------------------------------------------
    with tab_metrics:
        _html("<p style='font-size:1rem;font-weight:700;color:#472D2D;margin-bottom:0.3rem;'>Grafik Evaluasi Pelatihan Model</p>")
        _html("""
        <p style='font-size:0.87rem;color:#704F4F;line-height:1.65;margin-bottom:1rem;'>
        Grafik kurva <em>training loss</em> dan <em>validation accuracy</em>
        selama 15 epoch pelatihan MobileNetV3-Small di Google Colab GPU T4.
        </p>
        """)

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

        _html("<p style='font-size:1rem;font-weight:700;color:#472D2D;margin-bottom:0.3rem;'>Confusion Matrix</p>")
        _html("""
        <p style='font-size:0.87rem;color:#704F4F;line-height:1.65;margin-bottom:1rem;'>
        Visualisasi distribusi prediksi pada validation/test set
        -- membuktikan akurasi <strong>97%+</strong> secara ilmiah.
        </p>
        """)

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

        _html("<p style='font-size:1rem;font-weight:700;color:#472D2D;margin-bottom:0.8rem;'>Spesifikasi Teknis Model</p>")

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
