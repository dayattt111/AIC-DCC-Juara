# =============================================================
# Dockerfile — Kopita Deployment for Hugging Face Spaces
# Tech Stack: FastAPI (Backend Engine) + Streamlit (Frontend Portal)
# Security  : Non-root User (UID 1000) & Internal Backend Isolation
# Python 3.12-slim | Port: 7860 (Hugging Face Default)
# =============================================================

FROM python:3.12-slim

# 1. Set environment variables dasar
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# 2. Buat direktori kerja
WORKDIR /code

# 3. Salin dan install dependencies Python
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /code/requirements.txt

# 4. Buat user sistem non-root dengan UID 1000 (Standar Wajib Hugging Face Spaces)
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# 5. Salin seluruh kode proyek ke dalam kontainer
COPY --chown=user:user . /code

# 6. Berikan izin eksekusi pada skrip entrypoint dan pastikan kepemilikan file
RUN chmod +x /code/start.sh && \
    chown -R user:user /code

# 7. Beralih ke user non-root demi keamanan
USER user

# 8. Ekspos port resmi Hugging Face Spaces
EXPOSE 7860

# 9. Jalankan kedua layanan melalui entrypoint script
CMD ["./start.sh"]
