"""
GPT-SoVITS Bridge Server v2.5 - ULTRA-ROBUST
Indonesian Native + Fallback (No FFmpeg required)
"""

import os
import requests
from flask import Flask, request, send_file
from flask_cors import CORS
import uuid
import time
import traceback
import librosa
import soundfile as sf
import numpy as np

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'temp_audio')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

GSV_API_URL = "http://127.0.0.1:9880/tts"

# Lazy load whisper untuk menghindari error saat startup jika ffmpeg tidak ada
_stt_model = None

def get_stt_model():
    global _stt_model
    if _stt_model is None:
        try:
            import whisper
            device = "cuda" if os.environ.get("USE_GPU") == "1" else "cpu"
            print(f"📦 Loading Whisper model...")
            _stt_model = whisper.load_model("base")
        except:
            print("⚠️ Whisper failed to load. Using empty prompt fallback.")
            _stt_model = False
    return _stt_model

def python_trim_audio(input_path, output_path):
    """Memotong audio menggunakan Librosa (7 detik dari tengah)"""
    try:
        y, sr = librosa.load(input_path, sr=32000)
        duration = librosa.get_duration(y=y, sr=sr)
        start_sec = max(0, (duration / 2) - 3.5)
        end_sec = start_sec + 7
        start_sample = int(start_sec * sr)
        end_sample = int(end_sec * sr)
        y_trimmed = y[start_sample:end_sample]
        sf.write(output_path, y_trimmed, sr)
        return True
    except Exception as e:
        print(f"[PY-TRIM-ERROR] {e}")
        return False

@app.route('/clone', methods=['POST'])
def clone_voice():
    if 'audio' not in request.files or 'text' not in request.form:
        return "Missing audio or text", 400
    
    audio_file = request.files['audio']
    text = request.form['text']
    u_id = str(uuid.uuid4())
    
    raw_path = os.path.abspath(os.path.join(UPLOAD_FOLDER, f"raw_{u_id}.wav"))
    ref_path = os.path.abspath(os.path.join(UPLOAD_FOLDER, f"ref_{u_id}.wav"))
    out_path = os.path.abspath(os.path.join(UPLOAD_FOLDER, f"out_{u_id}.wav"))
    
    try:
        audio_file.save(raw_path)
        
        # Potong audio
        print(f"[GSV-OPTIMIZE] Trimming audio...")
        success = python_trim_audio(raw_path, ref_path)
        final_ref = ref_path if success and os.path.exists(ref_path) else raw_path
        
        # Auto-Transcribe dengan error handling ([WinError 2] fix)
        prompt_text = ""
        try:
            model = get_stt_model()
            if model:
                print(f"[WHISPER] Transcribing...")
                # Whisper butuh ffmpeg. Jika tdk ada, bagian ini akan error.
                # Kita tangkap errornya agar tidak mematikan seluruh server.
                result = model.transcribe(final_ref, language="id")
                prompt_text = result.get("text", "").strip()
                print(f"[WHISPER] Prompt: \"{prompt_text}\"")
        except Exception as stt_err:
            print(f"⚠️ STT Skip: {stt_err} (Mungkin FFmpeg tidak ada)")
            prompt_text = ""

        # Generate Voice
        print(f"[GSV-BRIDGE] Generating Native Indo Voice...")
        payload = {
            "text": text,
            "text_lang": "id", 
            "ref_audio_path": final_ref,
            "prompt_lang": "id",
            "prompt_text": prompt_text,
            "media_type": "wav"
        }
        
        time.sleep(0.3)
        response = requests.get(GSV_API_URL, params=payload, timeout=300)
        
        if response.status_code == 200:
            with open(out_path, "wb") as f:
                f.write(response.content)
            return send_file(out_path, mimetype='audio/wav')
        else:
            return f"API Error: {response.text}", 500
            
    except Exception as e:
        traceback.print_exc()
        return f"Bridge failure: {str(e)}", 500
    finally:
        for p in [raw_path, ref_path]:
            if os.path.exists(p):
                try: os.remove(p)
                except: pass

@app.route('/health', methods=['GET'])
def health():
    return {"status": "online", "engine": "GPT-SoVITS-Robust-V2.5"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
