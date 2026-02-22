import os
import sys
import uuid
import shutil
import threading
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional

# Menambahkan directory parent dari script ini (ai-training-runpod) ke path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.s3_manager import S3Manager
from services.local_storage_manager import LocalStorageManager
from app.preprocessing.split_audio import split_long_audio
from app.preprocessing.make_metadata import transcribe_with_google
from app.train.train import run_training

app = FastAPI(title="Runpod AI Training Worker")

# Inisialisasi Manager
s3 = S3Manager()
local_storage = LocalStorageManager()

class TrainingRequest(BaseModel):
    user_id: str
    audio_path: str # Path file audio mentah di R2 (misal: "raw/user123/suara.wav")
    model_name: Optional[str] = "custom_voice"
    epochs: Optional[int] = 100

def run_training_pipeline(request: TrainingRequest):
    """Fungsi UTAMA: Pipeline Otomatis"""
    training_id = str(uuid.uuid4())[:8]
    # Gunakan path absolut untuk keamanan di RunPod
    base_work_dir = f"/workspace/voice-changer/ai-training-runpod/temp_training_{training_id}"
    raw_audio_dir = os.path.join(base_work_dir, "raw_audio")
    wavs_dir = os.path.join(base_work_dir, "wavs")
    output_dir = os.path.join(base_work_dir, "out")
    
    os.makedirs(raw_audio_dir, exist_ok=True)
    os.makedirs(wavs_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🛠️ [PIPELINE] Memulai Sesi {training_id} untuk User {request.user_id}")
    
    try:
        # 1. DOWNLOAD RAW AUDIO DARI R2
        is_s3 = os.getenv("AWS_ACCESS_KEY_ID") is not None
        local_raw_file = os.path.join(raw_audio_dir, os.path.basename(request.audio_path))
        
        if is_s3:
            print(f"📥 Downloading raw audio: {request.audio_path}")
            s3.s3.download_file(s3.bucket, request.audio_path, local_raw_file)
        else:
            print(f"📂 Menggunakan file lokal: {request.audio_path}")
            # Simulasi copy jika lokal
            shutil.copy(request.audio_path, local_raw_file)

        # 2. PREPROCESSING: SPLIT AUDIO
        print("✂️ [PIPELINE] Memotong audio panjang menjadi segmen...")
        # Kita perlu pindah directory sebentar karena script split_audio pakai path relatif
        old_cwd = os.getcwd()
        os.chdir(base_work_dir)
        split_long_audio() 
        
        # 3. PREPROCESSING: TRANSCRIBE
        print("🎤 [PIPELINE] Melakukan transkripsi otomatis (Google ID)...")
        transcribe_with_google()
        os.chdir(old_cwd)

        # 4. START TRAINING
        print("🚀 [PIPELINE] Menjalankan Mesin Training XTTS v2...")
        best_model_path = run_training(
            dataset_dir=base_work_dir,
            output_dir=output_dir,
            epochs=request.epochs,
            batch_size=2 # RTX 4090 amannya pakai 2
        )

        # 5. UPLOAD HASIL KE R2
        remote_model_dir = f"models/{request.user_id}/{request.model_name}_{training_id}"
        if is_s3:
            s3.upload_model(output_dir, remote_model_dir)
            print(f"✅ [PIPELINE] Training Selesai! Model di-upload ke: {remote_model_dir}")
        else:
            print(f"✅ [PIPELINE] Training Selesai! Hasil di folder: {output_dir}")

        # 6. CLEANUP (Opsional)
        # shutil.rmtree(base_work_dir)

    except Exception as e:
        print(f"❌ [PIPELINE] ERROR FATAL: {str(e)}")

@app.post("/train")
async def trigger_training(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Endpoint Trigger dari Laravel"""
    background_tasks.add_task(run_training_pipeline, request)
    return {
        "status": "processing",
        "message": "Pipeline training dimulai di background.",
        "user_id": request.user_id,
        "mode": "GPU RTX 4090 Ready"
    }

@app.get("/health")
async def health():
    return {"status": "online", "gpu": torch.cuda.is_available()}

if __name__ == "__main__":
    import uvicorn
    import torch
    uvicorn.run(app, host="0.0.0.0", port=8001)
