import os
import sys
import uuid
import threading
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional

# Menambahkan directory parent dari script ini (ai-training-runpod) ke path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.s3_manager import S3Manager
from services.local_storage_manager import LocalStorageManager

app = FastAPI(title="Runpod AI Training Worker")

# Inisialisasi Manager (Hybrid)
# Jika API Key tidak ada, dia akan auto-fallback ke LocalStorageManager nanti
s3 = S3Manager()
local_storage = LocalStorageManager()

class TrainingRequest(BaseModel):
    user_id: str
    audio_path: str # Path di R2/S3 atau lokal
    model_name: Optional[str] = "custom_voice"

def run_training_pipeline(request: TrainingRequest):
    """Fungsi utama yang berjalan di background"""
    training_id = str(uuid.uuid4())[:8]
    work_dir = f"./temp_training_{training_id}"
    os.makedirs(work_dir, exist_ok=True)
    
    print(f"🛠️ [PIPELINE] Memulai proses training {training_id} untuk User {request.user_id}")
    
    try:
        # 1. DOWNLOAD DATASET
        # Cek apakah kita pakai mode S3 atau Lokal
        is_s3 = os.getenv("AWS_ACCESS_KEY_ID") is not None
        
        dataset_local_path = os.path.join(work_dir, "dataset.wav")
        
        if is_s3:
            s3.download_dataset("suara-cloning", request.audio_path, dataset_local_path)
        else:
            local_storage.download_dataset(None, request.audio_path, dataset_local_path)

        # 2. PREPROCESSING (Simulasi)
        print("🔍 [PIPELINE] Preprocessing audio...")
        # Nantinya panggil fungsi dari app/preprocessing/clean.py dsb.

        # 3. START TRAINING (Simulasi panggil train.py)
        print("🚀 [PIPELINE] Memanggil XTTS Trainer...")
        # Import fungsi training asli di sini
        # from app.train.train import start_training
        # start_training(dataset_local_path, work_dir)

        # 4. UPLOAD HASIL
        model_remote_path = f"models/{request.user_id}/{request.model_name}.pth"
        model_local_path = os.path.join(work_dir, "best_model.pth")
        
        # Buat file dummy jika belum ada (hanya untuk testing)
        if not os.path.exists(model_local_path):
            with open(model_local_path, "w") as f: f.write("Dummy Model Data")

        if is_s3:
            s3.upload_model(model_local_path, "suara-cloning", model_remote_path)
        else:
            local_storage.upload_model(model_local_path, None, model_remote_path)
            
        print(f"✅ [PIPELINE] Training {training_id} selesai dan di-upload!")

    except Exception as e:
        print(f"❌ [PIPELINE] Error: {str(e)}")

@app.post("/train")
async def trigger_training(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Endpoint yang dipanggil oleh Laravel"""
    background_tasks.add_task(run_training_pipeline, request)
    return {
        "status": "processing",
        "message": f"Training session started for user {request.user_id}",
        "training_id": str(uuid.uuid4())[:8]
    }

@app.get("/health")
async def health():
    return {"status": "ok", "worker": "runpod-training"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
