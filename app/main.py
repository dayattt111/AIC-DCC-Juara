import io
import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image, ImageOps
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Literal

# ===========================================================
# REBRANDING NOTE (lihat docs/REBRAND_GUIDE.md):
#   - Judul API publik  : "Kopita API Engine" ✅
#   - Nama file model   : tetap 'best_torajigrade_model.pth' ⚠️ JANGAN DIUBAH
#   - Variabel internal : tetap menggunakan codename 'torajigrade'
# ===========================================================
app = FastAPI(
    title="Kopita API Engine",
    version="1.0",
    description="API inferensi AI untuk penilaian kualitas tingkat sangrai biji kopi Toraja (Kopita)."
)

# 1. Konfigurasi Model & Kelas (Sesuaikan dengan dataset: Dark, Green, Light, Medium)
CLASSES = ['Dark', 'Green', 'Light', 'Medium']

# Device komputasi: dibaca dari env (default: cpu)
DEVICE_NAME = os.getenv("DEVICE", "cpu")
DEVICE = torch.device(DEVICE_NAME)

# Inisialisasi arsitektur MobileNetV3-Small
model = models.mobilenet_v3_small()
in_features: int = model.classifier[-1].in_features
model.classifier[-1] = nn.Linear(in_features, len(CLASSES))

# Memuat bobot hasil latihan secara aman (default: model/best_torajigrade_model.pth)
MODEL_PATH = os.getenv("MODEL_PATH", "model/best_torajigrade_model.pth")
try:
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()
    print(f"✅ Model TorajiGrade berhasil dimuat dari {MODEL_PATH} pada device {DEVICE}!")
except Exception as e:
    print(f"❌ Gagal memuat model: {str(e)}")

# Pipeline Normalisasi Tensor PyTorch (Standard ImageNet mean & std)
tensor_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


def sanitize_and_preprocess_image(raw_image: Image.Image) -> torch.Tensor:
    """
    Fungsi Sanitasi Citra Presisi - Metode Letterbox Padding (0% Terpotong, 0% Terdistorsi):
      1. Konversi ke RGB murni (menghilangkan alpha channel jika PNG).
      2. Resize proporsional tanpa memotong bagian manapun dari gambar asli.
         Biji kopi di posisi pinggir (kiri, kanan, atas, bawah) dijamin 100% utuh masuk.
      3. Berikan padding warna netral pada ruang sisa agar dimensi persegi 224x224 px terpenuhi.
      4. Konversi ke Tensor Float32 [1, 3, 224, 224] & Normalisasi ImageNet.

    Returns:
        Tensor berukuran [1, 3, 224, 224] siap diinferensi oleh model.
    """
    # 1. Konversi ke RGB murni
    rgb_img = raw_image.convert("RGB")

    # 2. Hitung skala proporsional agar 100% gambar asli masuk ke 224x224 px
    w, h = rgb_img.size
    scale = min(224.0 / w, 224.0 / h)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))

    # 3. Resize proporsional menggunakan interpolasi presisi tinggi Lanczos
    resized_img = rgb_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # 4. Buat kanvas netral 224x224 px dan tempelkan gambar di tengah (Letterbox)
    canvas = Image.new("RGB", (224, 224), (128, 128, 128))
    pad_x = (224 - new_w) // 2
    pad_y = (224 - new_h) // 2
    canvas.paste(resized_img, (pad_x, pad_y))

    # 5. Konversi ke Tensor PyTorch [1, 3, 224, 224]
    tensor = tensor_transform(canvas).unsqueeze(0).to(DEVICE)
    return tensor

# --- Pydantic Response Schemas (Kontrak API ketat sesuai .rules.md Section 3A) ---
class HealthResponse(BaseModel):
    status: Literal["active"]
    message: str

class PredictResponse(BaseModel):
    status: Literal["success"]
    prediction: str
    confidence: str
    detail: str
    rekomendasi_bisnis: str


@app.get("/", response_model=HealthResponse)
def home() -> HealthResponse:
    return HealthResponse(
        status="active",
        message="Kopita API Engine is running."
    )

@app.post("/predict", response_model=PredictResponse)
async def predict(file: UploadFile = File(...)) -> PredictResponse:
    # Validasi tipe file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Format berkas harus berupa gambar (JPG/PNG)!")

    try:
        # Membaca gambar dari request
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Preprocessing & Sanitasi Citra Presisi (Smart Lanczos Center Crop -> Tensor [1, 3, 224, 224])
        tensor = sanitize_and_preprocess_image(image)

        # Jalankan prediksi secara sinkron (Sesuai regulasi COMPFEST)
        with torch.no_grad():
            outputs = model(tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            confidence, predicted_idx = torch.max(probabilities, 0)

        class_name = CLASSES[predicted_idx.item()]
        score = confidence.item() * 100

        # Narasi komersial (Smart Commerce) spesifik untuk kopi Toraja
        metadata = {
            "Dark": {
                "deskripsi": "Tingkat sangrai Dark (Tua). Warna cokelat sangat gelap mendekati kehitaman dengan permukaan biji mulai mengeluarkan minyak alami.",
                "saran": "Sangat cocok untuk produk kopi tradisional (Kopi Tubruk khas Toraja) atau racikan kopi susu kekinian yang membutuhkan rasa pahit bold."
            },
            "Green": {
                "deskripsi": "Biji kopi mentah (Green Beans). Belum melalui proses pemanasan atau penyangraian.",
                "saran": "Lakukan penyortiran fisik lanjutan untuk memisahkan kotoran. Pastikan kadar air biji ideal berada di rentang 11-12% sebelum disangrai."
            },
            "Light": {
                "deskripsi": "Tingkat sangrai Light (Muda). Warna cokelat terang, body sangat ringan, dengan tingkat keasaman (acidity) khas Arabika Toraja yang dominan.",
                "saran": "Gunakan profil ini khusus untuk metode seduh manual (manual brew seperti V60/Filter) guna menonjolkan aroma buah-buahan asli kopi Toraja."
            },
            "Medium": {
                "deskripsi": "Tingkat sangrai Medium (Sedang). Tingkat kematangan paling ideal. Keseimbangan rasa manis alami (sweetness) dan keasaman yang sangat stabil.",
                "saran": "Sangat direkomendasikan untuk penjualan komersial ke kedai kopi lokal sebagai bahan dasar espresso base atau kopi hitam harian."
            }
        }

        return PredictResponse(
            status="success",
            prediction=class_name,
            confidence=f"{score:.2f}%",
            detail=metadata[class_name]["deskripsi"],
            rekomendasi_bisnis=metadata[class_name]["saran"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan sistem: {str(e)}")
