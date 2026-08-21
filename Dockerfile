# =============================================================
# Dockerfile — Kopita (Public Brand) / TorajiGrade (Codename)
# Tech Stack: FastAPI:8000 + Streamlit:8501 | PyTorch CPU-Only
# Python 3.12 | Lihat: docs/ARCHITECTURE.md & .rules.md
# =============================================================

# Gunakan Python 3.12 slim agar image sekecil mungkin
FROM python:3.12-slim

# Set working directory di dalam container
WORKDIR /kopita

# Salin requirements.txt lebih dulu agar layer ini di-cache
# selama requirements tidak berubah (optimasi build time)
COPY requirements.txt .

# Install semua dependensi Python
# --no-cache-dir  : hemat ruang disk di dalam image
# -r requirements.txt sudah mencantumkan PyTorch CPU whl index
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode sumber aplikasi ke dalam container
COPY app/ ./app/

# Salin bobot model PyTorch ke dalam container
# PENTING: Nama file 'best_torajigrade_model.pth' TIDAK BOLEH diubah
# (lihat docs/REBRAND_GUIDE.md — codename backend tetap 'torajigrade')
COPY model/ ./model/

# Ekspos kedua port layanan:
#   8000 → FastAPI Backend (uvicorn)
#   8501 → Streamlit Frontend
EXPOSE 8000
EXPOSE 8501

# CMD default: dioverride oleh docker-compose.yml per-layanan
# Contoh untuk backend: uvicorn app.main:app --host 0.0.0.0 --port 8000
CMD ["echo", "Gunakan docker-compose untuk menjalankan layanan Kopita."]
