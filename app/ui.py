import streamlit as st
import requests
from PIL import Image

st.set_page_config(page_title="TorajiGrade - Cerdas Menilai Kopi", page_icon="☕", layout="centered")

# Header & Subtitle
st.markdown("<h1 style='text-align: center; color: #4E3629;'>☕ TorajiGrade</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7F5A44;'><b>AI Penilai Tingkat Sangrai & Validasi Kopi Toraja untuk Transaksi Adil UMKM Roastery</b></p>", unsafe_allow_html=True)
st.write("---")

# Widget Upload Gambar
uploaded_file = st.file_uploader("Unggah foto biji kopi Anda (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Tampilkan gambar yang diunggah pengguna
    image = Image.open(uploaded_file)
    st.image(image, caption="Biji Kopi yang Diunggah", use_column_width=True)

    # Tombol Analisis
    if st.button("Mulai Analisis"):
        with st.spinner("Model AI sedang menganalisis foto kopi Anda..."):
            # Kirim data gambar ke backend FastAPI secara sinkron
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            try:
                # Menghubungkan Streamlit ke FastAPI lokal
                response = requests.post("http://127.0.0.1:8000/predict", files=files)

                if response.status_code == 200:
                    result = response.json()

                    # Layout kartu hasil yang cantik
                    st.success(f"### 🎉 Hasil Prediksi: {result['prediction']} ({result['confidence']})")

                    st.markdown("### 📊 Detail Tekstur")
                    st.info(result['detail'])

                    st.markdown("### 💡 Strategi Komersial UMKM")
                    st.warning(result['rekomendasi_bisnis'])
                else:
                    st.error("Gagal mendapatkan analisis dari server backend.")
            except Exception as e:
                st.error("Koneksi ke server backend terputus. Harap jalankan FastAPI terlebih dahulu!")
