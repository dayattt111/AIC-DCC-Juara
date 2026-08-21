"""
app/api_client.py — Kopita API Client
======================================
Modul ini mengisolasi seluruh logika komunikasi HTTP antara
Frontend Streamlit dan Backend FastAPI Kopita.

Aturan modul ini (.rules.md Section 2 - Strict Environment Boundaries):
  - TIDAK mengimpor torch, torchvision, atau library AI apapun.
  - TIDAK memuat berkas model .pth secara langsung.
  - Hanya boleh melakukan HTTP request ke backend FastAPI.
"""

from __future__ import annotations

import requests
from dataclasses import dataclass

# URL backend FastAPI — ubah di sini jika port atau host berubah
_BACKEND_URL: str = "http://127.0.0.1:8000"
_PREDICT_ENDPOINT: str = f"{_BACKEND_URL}/predict"
_HEALTH_ENDPOINT: str  = f"{_BACKEND_URL}/"
_REQUEST_TIMEOUT: int  = 30  # detik


@dataclass(frozen=True)
class PredictResult:
    """Representasi terstruktur dari response sukses /predict."""
    status: str
    prediction: str
    confidence: str
    detail: str
    rekomendasi_bisnis: str


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

    try:
        response = requests.post(
            _PREDICT_ENDPOINT,
            files=files,
            timeout=_REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            return PredictResult(
                status=data.get("status", "success"),
                prediction=data["prediction"],
                confidence=data["confidence"],
                detail=data["detail"],
                rekomendasi_bisnis=data["rekomendasi_bisnis"],
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
            message=f"Server tidak merespons dalam {_REQUEST_TIMEOUT} detik."
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
        response = requests.get(_HEALTH_ENDPOINT, timeout=5)
        return response.status_code == 200
    except Exception:
        return False
