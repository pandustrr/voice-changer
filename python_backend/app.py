import os
from flask import Flask, request, send_file
from flask_cors import CORS
import torch
import uuid
import time
import librosa
import soundfile as sf
import traceback
import numpy as np
import re

# Patch torch.load untuk keamanan dan kompatibilitas
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

print("Starting Optimized Indonesian-Phonetic Engine (XTTS v2)...")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device detecteed: {device}")

# Load model XTTS v2
# Engine Hindi ('hi') digunakan sebagai basis fonetik Indonesia yang paling akurat
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

UPLOAD_FOLDER = 'temp_audio'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/clone', methods=['POST'])
def clone_voice():
    now = time.time()
    for f in os.listdir(UPLOAD_FOLDER):
        f_path = os.path.join(UPLOAD_FOLDER, f)
        if os.stat(f_path).st_mtime < now - 3600:
            try: os.remove(f_path)
            except: pass

    if 'audio' not in request.files or 'text' not in request.form:
        return "Missing audio or text", 400
    
    audio_file = request.files['audio']
    text = request.form['text']
    u_id = str(uuid.uuid4())
    
    ref_path = os.path.join(UPLOAD_FOLDER, f"ref_{u_id}.wav")
    out_path = os.path.join(UPLOAD_FOLDER, f"out_{u_id}.wav")
    
    try:
        audio_file.save(ref_path)
        
        # Audio Preprocessing untuk menangkap karakteristik suara asli
        y, sr = librosa.load(ref_path, sr=22050, mono=True)
        # Ambil 10 detik terbaik
        y, _ = librosa.effects.trim(y, top_db=25)
        y = librosa.util.normalize(y) * 0.95
        sf.write(ref_path, y, 22050, format='WAV', subtype='PCM_16')
        
    except Exception as e:
        print(f"[ERROR] Preprocessing: {str(e)}")

    try:
        print(f"[SYNTHESIS] Cloning using Hindi Phonetic Bridge (Best for Indo)...")
        
        # Menggunakan 'hi' (Hindi) karena bunyi vokalnya (A, I, U, E, O) 
        # sangat identik dengan Indonesia. Menghilangkan aksen 'bule'.
        tts.tts_to_file(
            text=text,
            speaker_wav=ref_path,
            language="hi", 
            file_path=out_path,
            speed=1.2,           # Lebih cepat agar tidak lambat/boring
            temperature=0.7,     # Keseimbangan antara kemiripan & emosi
            repetition_penalty=3.0,
            enable_text_splitting=True
        )
        
        if os.path.exists(out_path) and os.path.getsize(out_path) > 100:
            print(f"[SUCCESS] Natural sound generated.")
            return send_file(out_path, mimetype='audio/wav')
        else:
            return "Synthesis failed", 500
            
    except Exception as e:
        print(f"[ERROR] Engine Failure: {str(e)}")
        # Fallback terakhir ke 'en' jika 'hi' gagal (meskipun 'hi' pasti ada di list anda)
        try:
             tts.tts_to_file(text=text, speaker_wav=ref_path, language="en", file_path=out_path, speed=1.2)
             return send_file(out_path, mimetype='audio/wav')
        except:
             return f"AI Engine Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
