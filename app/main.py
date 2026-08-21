import io
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI(title="kopita API", version="1.0")

# 1. Konfigurasi Model & Kelas (Sesuaikan dengan dataset Anda: Dark, Green, Light, Medium)
CLASSES = ['Dark', 'Green', 'Light', 'Medium']
DEVICE = torch.device('cpu') # Dipaksa berjalan di CPU agar sangat ringan di laptop Anda

# Inisialisasi arsitektur MobileNetV3-Small
model = models.mobilenet_v3_small()
in_features = model.classifier.in_features
model.classifier = nn.Linear(in_features, len(CLASSES))

# Memuat bobot hasil latihan dari Colab secara aman
MODEL_PATH = "model/best_torajigrade_model.pth"
try:
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()
    print(f"✅ Model TorajiGrade berhasil dimuat dari {MODEL_PATH}!")
except Exception as e:
    print(f"❌ Gagal memuat model: {str(e)}")

# Pipeline transformator gambar (identik dengan proses validasi/test saat training)
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

@app.get("/")
def home():
    return {"status": "active", "message": "TorajiGrade API Engine is running."}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Validasi tipe file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Format berkas harus berupa gambar (JPG/PNG)!")

    try:
        # Membaca gambar dari request
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Preprocessing gambar agar sesuai format input model
        tensor = preprocess(image).unsqueeze(0).to(DEVICE)

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

        return {
            "status": "success",
            "prediction": class_name,
            "confidence": f"{score:.2f}%",
            "detail": metadata[class_name]["deskripsi"],
            "rekomendasi_bisnis": metadata[class_name]["saran"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan sistem: {str(e)}")
