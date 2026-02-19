import os
import sys
import uuid
from flask import Flask, request, send_file
from flask_cors import CORS

# Menambahkan path ke folder AI agar bisa import script-nya
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))

app = Flask(__name__)
CORS(app)

# Path storage Laravel
STORAGE_BASE = os.path.abspath(os.path.join(os.getcwd(), "storage/app/public"))
MODEL_DIR = os.path.join(STORAGE_BASE, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

@app.route('/health', methods=['GET'])
def health():
    return {"status": "ok", "engine": "XTTS v2 Local Hybrid"}

@app.route('/extract_speaker', methods=['POST'])
def extract_speaker():
    # Menangani request dari VoiceChangerController::initializeVoice
    print("🎙️ [FRONTEND] Menerima request extract_speaker")
    return {
        "success": True, 
        "speaker_id": "local_test_speaker_" + str(uuid.uuid4())[:8],
        "message": "Speaker profile created locally"
    }

@app.route('/clone', methods=['POST'])
def clone():
    # Menangani request dari VoiceChangerController::clone
    print("🎤 [FRONTEND] Menerima request clone voice")
    # Biarkan frontend mendapat respons sukses
    return "Dummy audio content" 

@app.route('/train', methods=['POST'])
def train():
    user_id = request.form.get('user_id')
    audio_path = request.form.get('audio_path')
    
    print(f"🛠️ [SaaS] Memulai Training untuk User: {user_id}")
    return {"status": "success", "message": "Training lokal dimulai (Simulasi)"}

@app.route('/generate', methods=['POST'])
def generate():
    text = request.form.get('text')
    print(f"🎤 [SaaS] Menghasilkan suara: {text}")
    return "Dummy audio content"

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Local AI Server Running on http://127.0.0.1:5000")
    print("Mode: Hybrid (Support Frontend & SaaS Flow)")
    print("="*50 + "\n")
    app.run(port=5000, debug=True)

