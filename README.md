# ☕ Kopita — AI Penilai Kualitas Kopi untuk Transaksi Adil UMKM

> **Kopita** adalah aplikasi AI berbasis *computer vision* yang membantu petani kopi dan pelaku UMKM Roastery Toraja dalam **menilai tingkat kematangan sangrai biji kopi** secara objektif, cepat, dan akurat — demi mewujudkan transaksi yang lebih adil dan transparan.

---

## 🏆 Tentang Proyek

| Atribut | Detail |
|:---|:---|
| **Nama Proyek** | Kopita *(AI Penilai Kualitas Kopi)* |
| **Kompetisi** | AIC DCC Hackathon |
| **Tim** | AIC DCC Juara |
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
      │  Preprocessing → MobileNetV3-Small → Softmax
      ▼
JSON Response  {prediction, confidence, detail, rekomendasi_bisnis}
      │
      ▼
Frontend Streamlit  (Tampilkan kartu hasil + rekomendasi UMKM)
```

---

## 📂 Struktur Direktori

```
002-Hackathon-AIC/
├── app/
│   ├── main.py              # Backend FastAPI (Port 8000) — Inference Engine
│   └── ui.py                # Frontend Streamlit (Port 8501) — Portal UI
├── model/
│   ├── best_torajigrade_model.pth        # Bobot Model PyTorch (~6 MB)
│   └── torajigrade_model_config.json     # Hyperparameter & metadata model
├── notebooks/
│   ├── AIC_DCC_Juara.ipynb  # Notebook pelatihan utama (Google Colab GPU T4)
│   ├── inference.ipynb      # Notebook verifikasi prediksi lokal
│   └── evaluation/          # Confusion matrix & metrik evaluasi model
├── sample_image/            # Gambar uji coba untuk demo & pengujian juri
│   ├── from_dataset_test/
│   ├── from_public_image_out_of_dataset/
│   └── from_camera_manual/
├── profil_team/             # Profil anggota tim
├── requirements.txt         # Dependensi Python (CPU-Only PyTorch)
├── Dockerfile               # Image Docker Python 3.12-slim
└── docker-compose.yml       # Orkestrasi: backend + frontend
```

---

## 🚀 Cara Menjalankan (Lokal)

### Prasyarat
- Python 3.12
- Virtual environment aktif

### Langkah 1 — Siapkan environment
```bash
# Buat dan aktifkan virtual environment
python3.12 -m venv env-dcc-juara
source env-dcc-juara/bin/activate  # Linux/Mac

# Install semua dependensi (PyTorch CPU + FastAPI + Streamlit)
pip install -r requirements.txt
```

### Langkah 2 — Jalankan Backend FastAPI
```bash
# Buka Terminal 1
source env-dcc-juara/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
✅ API berjalan di: `http://127.0.0.1:8000`
📄 Dokumentasi Swagger: `http://127.0.0.1:8000/docs`

### Langkah 3 — Jalankan Frontend Streamlit
```bash
# Buka Terminal 2
source env-dcc-juara/bin/activate
streamlit run app/ui.py --server.port 8501
```
✅ UI berjalan di: `http://localhost:8501`

---

## 🐳 Cara Menjalankan (Docker Compose)

```bash
# Build dan jalankan kedua layanan sekaligus
docker compose up --build

# Hentikan semua container
docker compose down
```

| Service | URL |
|:---|:---|
| Frontend Streamlit | http://localhost:8501 |
| Backend FastAPI | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |

---

## 🔌 API Endpoints

### `GET /` — Health Check
```json
{
  "status": "active",
  "message": "Kopita API Engine is running."
}
```

### `POST /predict` — Prediksi Tingkat Sangrai
**Request:** `multipart/form-data` dengan field `file` berisi gambar JPG/PNG.

**Response Sukses (200):**
```json
{
  "status": "success",
  "prediction": "Medium",
  "confidence": "98.42%",
  "detail": "Tingkat sangrai Medium (Sedang). Keseimbangan rasa manis alami dan keasaman yang sangat stabil.",
  "rekomendasi_bisnis": "Sangat direkomendasikan untuk penjualan komersial ke kedai kopi lokal."
}
```

**Response Error (400):**
```json
{ "detail": "Format berkas harus berupa gambar (JPG/PNG)!" }
```

---

## 🏷️ Kelas Deteksi Model

| Kelas | Deskripsi | Rekomendasi Komersial |
|:---:|:---|:---|
| 🖤 **Dark** | Sangrai tua, warna gelap kehitaman, berminyak | Kopi Tubruk Tradisional Toraja / Espresso Dark Blend |
| 🌿 **Green** | Biji mentah, belum disangrai | Sortasi fisik, cek kadar air 11–12% |
| 🌟 **Light** | Sangrai muda, cokelat terang, acidity tinggi | Manual Brew V60 / Filter / Kalita |
| ☕ **Medium** | Sangrai sedang, keseimbangan ideal | Espresso Base / Kopi Susu UMKM Kekinian |

---

## 📊 Performa Model

- **Arsitektur:** MobileNetV3-Small (fine-tuned dari ImageNet weights)
- **Akurasi:** **97%+** pada validation/test set
- **Input:** Gambar RGB 224×224 px (normalisasi ImageNet)
- **Device:** CPU-Only (ringan, bisa berjalan di laptop tanpa GPU)
- **Training:** 15 epoch · Adam optimizer · CosineAnnealingLR · Google Colab T4 GPU

---

## 👥 Tim Pengembang

| Nama | Peran |
|:---|:---|
| Dayat | ML Engineer / Model Training |
| Mull | Backend Developer |
| Rey | Frontend Developer |
| Sasa | UI/UX & Data Analyst |

---

## 📄 Lisensi

Proyek ini dikembangkan untuk keperluan **AIC DCC Hackathon**. Seluruh hak cipta milik tim AIC DCC Juara.
