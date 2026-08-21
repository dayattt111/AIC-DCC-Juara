#!/bin/bash
# =============================================================
# start.sh — Hugging Face Spaces & Container Entrypoint Script
# =============================================================
# 1. Menjalankan FastAPI backend secara terisolasi di localhost (127.0.0.1)
#    agar aman di dalam kontainer dan tidak terbuka ke internet publik.
# 2. Menjalankan Streamlit frontend di port 7860 (0.0.0.0) di foreground
#    sebagai antarmuka web publik Hugging Face Spaces.
# =============================================================

# Default port jika tidak didefinisikan di environment
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-7860}"

echo "============================================================"
echo " Starting Kopita AI Production Services..."
echo " Backend Engine : 127.0.0.1:${BACKEND_PORT} (Internal Only)"
echo " Frontend Portal: 0.0.0.0:${FRONTEND_PORT} (Public Entrypoint)"
echo "============================================================"

# 1. Jalankan FastAPI Backend di latar belakang (Internal Localhost Only)
uvicorn app.main:app \
    --host 127.0.0.1 \
    --port "${BACKEND_PORT}" \
    --workers 1 &

# Tunggu sejenak hingga backend FastAPI siap menerima request
sleep 2

# 2. Jalankan Streamlit Frontend di latar depan (Foreground - Port 7860 HF)
exec streamlit run app/ui.py \
    --server.port "${FRONTEND_PORT}" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false
