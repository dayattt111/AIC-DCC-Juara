# ☕ Kopita — AI Penilai Kualitas Kopi untuk Transaksi Adil UMKM

<div align="center">
  <img src="https://dcc-dp.id/favicon.ico" width="48" alt="DCC Logo" />
  <h3>Dipanegara Computer Club (DCC) &mdash; Universitas Dipa Makassar</h3>
  <p><strong><a href="https://dcc-dp.id">dcc-dp.id</a></strong></p>
</div>

> **Kopita** adalah aplikasi AI berbasis *computer vision* yang membantu petani kopi dan pelaku UMKM Roastery Toraja dalam **menilai tingkat kematangan sangrai biji kopi** secara objektif, cepat, dan akurat — demi mewujudkan transaksi yang lebih adil dan transparan.

---

## 👥 Tim Pengembang (AIC DCC Juara)

Seluruh anggota tim berasal dari **Universitas Dipa Makassar** dan aktif dalam study club **Dipa Computer Club (DCC)** ([dcc-dp.id](https://dcc-dp.id)).

| <img src="profil_team/day.jpeg" width="160" alt="Muhammad Hidayat" /><br>**[Muhammad Hidayat](profil_team/dayat.md)** | <img src="profil_team/mull.jpeg" width="160" alt="Mull" /><br>**[Mull](profil_team/mull.md)** | <img src="profil_team/rey.jpeg" width="160" alt="Rey" /><br>**[Rey](profil_team/rey.md)** | <img src="profil_team/sasa.jpeg" width="160" alt="Sasa" /><br>**[Sasa](profil_team/sasa.md)** |
|:---:|:---:|:---:|:---:|
| **Machine Learning Engineer** | **Backend Developer** | **Frontend Developer** | **UI/UX & Data Analyst** |
| Universitas Dipa Makassar | Universitas Dipa Makassar | Universitas Dipa Makassar | Universitas Dipa Makassar |
| [Dipa Computer Club](https://dcc-dp.id) | [Dipa Computer Club](https://dcc-dp.id) | [Dipa Computer Club](https://dcc-dp.id) | [Dipa Computer Club](https://dcc-dp.id) |
| [GitHub](https://github.com/dayattt111) • [LinkedIn](https://linkedin.com/in/muhammad-amin-hidayat) • [IG](https://instagram.com/ur.dayaa) | [GitHub](https://github.com/) • [LinkedIn](https://linkedin.com/) • [IG](https://instagram.com/) | [GitHub](https://github.com/) • [LinkedIn](https://linkedin.com/) • [IG](https://instagram.com/) | [GitHub](https://github.com/) • [LinkedIn](https://linkedin.com/) • [IG](https://instagram.com/) |

---

## 🏆 Tentang Proyek

| Atribut | Detail |
|:---|:---|
| **Nama Proyek** | Kopita *(AI Penilai Kualitas Kopi)* |
| **Kompetisi** | AIC DCC Hackathon |
| **Tim** | AIC DCC Juara |
| **Organisasi** | Dipa Computer Club (DCC) — [dcc-dp.id](https://dcc-dp.id) |
| **Model AI** | MobileNetV3-Small (PyTorch CPU-Only) |
| **Akurasi** | 97%+ pada validation/test set |
| **Kelas Deteksi** | `Dark` · `Green` · `Light` · `Medium` |

---

## 🗺️ Arsitektur Sistem

```
Pengguna (Browser)
      │  Upload foto biji kopi (JPG/PNG)
      ▼
Frontend Streamlit  :8501
      │  HTTP POST /predict (multipart/form-data)
      ▼
Backend FastAPI     :8000
      │  Sanitasi Letterbox → MobileNetV3-Small → Softmax
      ▼
JSON Response  {status, prediction, confidence, detail, rekomendasi_bisnis}
      │
      ▼
Frontend Streamlit  (Tampilkan Hasil Analisis, Telemetri Teknis, & Rekomendasi UMKM)
```

---

## 📂 Struktur Direktori

```
002-Hackathon-AIC/
├── app/
│   ├── main.py              # Backend FastAPI (Port 8000) — Inference Engine
│   ├── ui.py                # Frontend Streamlit (Port 8501) — Portal UI
│   ├── style.py             # UI Visual Engine (CSS & Komponen Kustom Kopita)
│   └── api_client.py        # Modul Komunikasi HTTP ke Backend
├── model/
│   ├── best_torajigrade_model.pth        # Bobot Model PyTorch (~6 MB)
│   └── torajigrade_model_config.json     # Hyperparameter & metadata model
├── notebooks/
│   ├── AIC_DCC_Juara.ipynb  # Notebook pelatihan utama (Google Colab GPU T4)
│   ├── inference.ipynb      # Notebook verifikasi prediksi lokal
│   └── evaluation/          # Confusion matrix & metrik evaluasi model
├── profil_team/             # Profil & foto anggota tim DCC
│   ├── dayat.md & day.jpeg
│   ├── mull.md & mull.jpeg
│   ├── rey.md & rey.jpeg
│   └── sasa.md & sasa.jpeg
├── sample_image/            # Gambar uji coba untuk demo & pengujian juri
├── .env.example             # Template variabel lingkungan
├── .env                     # Variabel lingkungan aktif
├── requirements.txt         # Dependensi Python produksi
├── requirements_minimum.txt # Dependensi CPU lokal super ringan
├── Dockerfile               # Image Docker Python 3.12-slim
└── docker-compose.yml       # Orkestrasi container: backend + frontend
```

---

## 🌐 Deployment ke Streamlit Community Cloud (100% Gratis & Instan)

Aplikasi Kopita telah dilengkapi fitur **Auto-Start Backend Engine** sehingga dapat langsung dideploy ke **Streamlit Community Cloud (`share.streamlit.io`)** hanya dengan 3 langkah:

1. **Push repositori** ini ke GitHub Anda.
2. Buka [share.streamlit.io](https://share.streamlit.io) lalu klik **New app**.
3. Atur konfigurasi deployment:
   - **Repository**: `username/repo-kopita`
   - **Branch**: `main`
   - **Main file path**: `app/ui.py`
4. Klik **Deploy!** — Streamlit Cloud akan menginstal dependensi dari `requirements.txt` dan backend FastAPI akan otomatis aktif di background.

---

## 🐳 Cara Menjalankan dengan Docker Compose (Komputer Lain / Demo)

Jika pengguna atau juri lain ingin menjalankan seluruh ekosistem di komputer mereka menggunakan Docker:

```bash
# 1. Build dan jalankan seluruh container layanan
docker compose up --build

# 2. Buka di browser:
#    - Frontend Streamlit : http://localhost:8501
#    - Backend FastAPI    : http://localhost:8000
#    - Swagger API Docs   : http://localhost:8000/docs

# 3. Untuk menghentikan layanan:
docker compose down
```

---

## 💻 Cara Menjalankan Secara Lokal (Manual)

### Prasyarat
- Python 3.12 (atau Python 3.10 / 3.11)
- Virtual environment aktif

### Langkah 1 — Siapkan environment & dependensi
```bash
# Buat dan aktifkan virtual environment
python3 -m venv env-dcc-juara
source env-dcc-juara/bin/activate  # Linux/Mac
# env-dcc-juara\Scripts\activate   # Windows

# Install dependensi (Gunakan requirements_minimum.txt untuk CPU lokal yang super ringan)
pip install -r requirements_minimum.txt
```

### Langkah 2 — Jalankan Backend FastAPI
```bash
# Terminal 1:
source env-dcc-juara/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API aktif di: `http://127.0.0.1:8000`
- Dokumentasi API Swagger: `http://127.0.0.1:8000/docs`

### Langkah 3 — Jalankan Frontend Streamlit
```bash
# Terminal 2:
source env-dcc-juara/bin/activate
streamlit run app/ui.py --server.port 8501
```
- UI aktif di: `http://localhost:8501`

---

## 🧪 Validasi API Backend (cURL)

Anda dapat menguji endpoint inferensi secara langsung menggunakan cURL:

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@sample_image/from_dataset_test/medium_1.png"
```

Contoh respon JSON:
```json
{
  "status": "success",
  "prediction": "Medium",
  "confidence": "98.42%",
  "detail": "Tingkat sangrai Medium (Sedang)...",
  "rekomendasi_bisnis": "Profil serbaguna (omni-roast)..."
}
```
