import os
import sys
import uuid
import shutil
import threading
import torch
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# Menambahkan directory parent dari script ini (ai-training-runpod) ke path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables
load_dotenv()

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

# Progress tracking
training_progress = {
    "status": "idle",
    "current_step": "none",
    "progress_percent": 0,
    "current_epoch": 0,
    "total_epochs": 0,
    "message": "Waiting for command..."
}

def run_training_pipeline(request: TrainingRequest):
    """Fungsi UTAMA: Pipeline Otomatis"""
    global training_progress
    training_id = str(uuid.uuid4())[:8]
    
    training_progress.update({
        "status": "running",
        "current_step": "initializing",
        "progress_percent": 5,
        "total_epochs": request.epochs,
        "message": f"Initializing session {training_id}"
    })

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
        training_progress.update({
            "current_step": "downloading",
            "progress_percent": 15,
            "message": "Downloading dataset from Cloud..."
        })
        
        is_s3 = os.getenv("AWS_ACCESS_KEY_ID") is not None
        local_raw_file = os.path.join(raw_audio_dir, os.path.basename(request.audio_path))
        
        if is_s3:
            s3.s3.download_file(s3.bucket, request.audio_path, local_raw_file)
        else:
            shutil.copy(request.audio_path, local_raw_file)

        # 2. PREPROCESSING: SPLIT AUDIO
        training_progress.update({
            "current_step": "preprocessing",
            "progress_percent": 30,
            "message": "Splitting audio into segments..."
        })
        old_cwd = os.getcwd()
        os.chdir(base_work_dir)
        split_long_audio() 
        
        # 3. PREPROCESSING: TRANSCRIBE
        training_progress.update({
            "progress_percent": 45,
            "message": "Transcribing audio segments..."
        })
        transcribe_with_google()
        os.chdir(old_cwd)

        # 4. START TRAINING
        training_progress.update({
            "current_step": "training",
            "progress_percent": 50,
            "message": "Starting XTTS v2 Training Engine..."
        })
        
        # Note: In a real scenario, you'd want to hook into the run_training loop to update current_epoch
        # For now, we simulate the start
        best_model_path = run_training(
            dataset_dir=base_work_dir,
            output_dir=output_dir,
            epochs=request.epochs,
            batch_size=2 
        )

        # 5. UPLOAD HASIL KE R2
        training_progress.update({
            "current_step": "uploading",
            "progress_percent": 90,
            "message": "Uploading trained model to Cloud..."
        })
        remote_model_dir = f"models/{request.user_id}/{request.model_name}_{training_id}"
        if is_s3:
            s3.upload_model(output_dir, remote_model_dir)

        training_progress.update({
            "status": "completed",
            "current_step": "done",
            "progress_percent": 100,
            "message": "Training finished successfully!"
        })

    except Exception as e:
        training_progress.update({
            "status": "error",
            "message": f"Pipeline Error: {str(e)}"
        })
        print(f"❌ [PIPELINE] ERROR FATAL: {str(e)}")

@app.post("/train")
async def trigger_training(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Endpoint Trigger dari Laravel"""
    background_tasks.add_task(run_training_pipeline, request)
    return {
        "status": "processing",
        "message": "Pipeline training dimulai di background.",
        "user_id": request.user_id
    }

@app.get("/status")
async def get_status():
    """Endpoint Monitoring Real-time"""
    return training_progress

@app.get("/health")
async def health():
    return {"status": "online", "gpu": torch.cuda.is_available()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
