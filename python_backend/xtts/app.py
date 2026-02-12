import os
from flask import Flask, request, send_file
from flask_cors import CORS
import torch
import uuid
import time
import librosa
import soundfile as sf
import traceback
from indo_cleaner import clean_indonesian_for_xtts

# Security Patch
orig_load = torch.load
def patched_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return orig_load(*args, **kwargs)
torch.load = patched_load

from TTS.api import TTS
os.environ["COQUI_TOS_AGREED"] = "1"

app = Flask(__name__)
CORS(app)

print("Starting XTTS Engine...")
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load Model
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'temp_xtts')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def handle_audio_duration(input_path, output_path):
    try:
        y, sr = librosa.load(input_path, sr=22050)
        duration = librosa.get_duration(y=y, sr=sr)
        if duration > 12:
            start_sample = int((duration / 2 - 5) * sr)
            end_sample = start_sample + int(10 * sr)
            y = y[max(0, start_sample):min(len(y), end_sample)]
        y = librosa.util.normalize(y) * 0.95
        sf.write(output_path, y, sr)
        return True
    except Exception as e:
        print(f"Audio error: {e}")
        return False

@app.route('/clone', methods=['POST'])
def clone_voice():
    if 'audio' not in request.files or 'text' not in request.form:
        return "Missing data", 400
    
    audio_file = request.files['audio']
    raw_text = request.form['text']
    speed = float(request.form.get('speed', 1.1))
    
    # Process text using indo_cleaner
    clean_text = clean_indonesian_for_xtts(raw_text)
    
    u_id = str(uuid.uuid4())
    raw_path = os.path.abspath(os.path.join(UPLOAD_FOLDER, f"raw_{u_id}.wav"))
    ref_path = os.path.abspath(os.path.join(UPLOAD_FOLDER, f"ref_{u_id}.wav"))
    out_path = os.path.abspath(os.path.join(UPLOAD_FOLDER, f"out_{u_id}.wav"))
    
    try:
        audio_file.save(raw_path)
        handle_audio_duration(raw_path, ref_path)
        
        # Gunakan 'pt' (Portuguese) - Vokal lebih mirip Indonesia daripada Spanish
        # Temperature rendah = lebih konsisten, Repetition penalty tinggi = hindari pola barat
        tts.tts_to_file(
            text=clean_text,
            speaker_wav=ref_path,
            language="pt",  # Portuguese memiliki vokal yang sangat dekat dengan Indonesia
            file_path=out_path,
            speed=speed,
            temperature=0.65,  # Lebih rendah = lebih stabil dan konsisten
            repetition_penalty=7.0  # Lebih tinggi = hindari pola bicara barat
        )
        
        return send_file(out_path, mimetype='audio/wav')
            
    except Exception as e:
        traceback.print_exc()
        return f"XTTS Engine Error: {str(e)}", 500
    finally:
        for p in [raw_path, ref_path]:
            if os.path.exists(p):
                try: os.remove(p)
                except: pass

@app.route('/health', methods=['GET'])
def health():
    return {"status": "ok", "engine": "XTTSv2-Pure-Indo", "device": device}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
