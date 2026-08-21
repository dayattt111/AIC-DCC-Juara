"""
app/api_client.py — Kopita API Client
======================================
Modul ini mengisolasi seluruh logika komunikasi HTTP antara
Frontend Streamlit dan Backend FastAPI Kopita.

Aturan modul ini (.rules.md Section 2 - Strict Environment Boundaries):
  - TIDAK mengimpor torch, torchvision, atau library AI apapun.
  - TIDAK memuat berkas model .pth secara langsung.
  - Hanya boleh melakukan HTTP request ke backend FastAPI.
  - Mengambil URL dan Timeout secara dinamis dari Environment Variables.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
import requests


def get_api_url() -> str:
    """
    Dapatkan URL dasar backend FastAPI secara dinamis dari environment variable.
    Default aman: http://127.0.0.1:8000
    """
    return os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")


def get_predict_url() -> str:
    """Dapatkan endpoint /predict dinamis."""
    return f"{get_api_url()}/predict"


def get_health_url() -> str:
    """Dapatkan endpoint health check (/) dinamis."""
    return f"{get_api_url()}/"


def get_request_timeout() -> int:
    """
    Dapatkan timeout request dalam detik dari environment variable.
    Default aman: 30 detik.
    """
    try:
        return int(os.getenv("REQUEST_TIMEOUT", "30"))
    except ValueError:
        return 30


@dataclass(frozen=True)
class PredictResult:
    """Representasi terstruktur dari response sukses /predict."""
    status: str
    prediction: str
    confidence: str
    detail: str
    rekomendasi_bisnis: str
    latency_ms: float = 0.0
    raw_response: dict | None = None


@dataclass(frozen=True)
class APIError:
    """Representasi terstruktur dari kondisi error response atau koneksi."""
    http_status: int   # 0 = connection error, 408 = timeout
    message: str


def predict_image(
    filename: str,
    file_bytes: bytes,
    content_type: str,
) -> PredictResult | APIError:
    """
    Kirim gambar ke endpoint POST /predict dan kembalikan hasilnya.

    Args:
        filename    : Nama berkas gambar (misal "kopi.png").
        file_bytes  : Isi berkas dalam bytes.
        content_type: MIME type berkas (misal "image/png").

    Returns:
        PredictResult jika sukses (HTTP 200).
        APIError      jika terjadi error HTTP atau koneksi.
    """
    files = {"file": (filename, file_bytes, content_type)}
    endpoint = get_predict_url()
    timeout = get_request_timeout()

    try:
        t0 = time.perf_counter()
        response = requests.post(
            endpoint,
            files=files,
            timeout=timeout
        )
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        if response.status_code == 200:
            data = response.json()
            return PredictResult(
                status=data.get("status", "success"),
                prediction=data["prediction"],
                confidence=data["confidence"],
                detail=data["detail"],
                rekomendasi_bisnis=data["rekomendasi_bisnis"],
                latency_ms=latency_ms,
                raw_response=data,
            )

        # Error dari server — ambil pesan dari JSON jika ada
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text

        return APIError(http_status=response.status_code, message=detail)

    except requests.exceptions.ConnectionError:
        return APIError(
            http_status=0,
            message=(
                "Backend FastAPI tidak dapat dijangkau. "
                "Pastikan server sudah berjalan:\n"
                "```bash\n"
                "uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload\n"
                "```"
            )
        )
    except requests.exceptions.Timeout:
        return APIError(
            http_status=408,
            message=f"Server tidak merespons dalam {timeout} detik."
        )
    except Exception as exc:
        return APIError(http_status=-1, message=str(exc))


def check_health() -> bool:
    """
    Cek apakah backend FastAPI aktif.

    Returns:
        True  jika GET / mengembalikan HTTP 200.
        False jika tidak dapat terhubung.
    """
    try:
        response = requests.get(get_health_url(), timeout=min(5, get_request_timeout()))
        return response.status_code == 200
    except Exception:
        return False
