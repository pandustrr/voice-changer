"""
ElevenLabs Voice Cloning Backend - Secure Version
"""

import os
from flask import Flask, request, send_file
from flask_cors import CORS
import uuid
import time
import requests
import traceback
from dotenv import load_dotenv

# Load environmental variables dari root directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'temp_audio'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ElevenLabs API Key (Diambil dari file .env)
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

# Voice ID Manual (Optional)
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', '')

def get_fallback_voice_id(api_key):
    """Mencari suara yang tersedia di akun jika ID default gagal"""
    try:
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {"xi-api-key": api_key}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            voices = res.json().get('voices', [])
            if voices:
                return voices[0].get('voice_id')
    except:
        pass
    return "21m00Tcm4TlvDq8ikWAM" # ID Rachel (Global Default)

@app.route('/clone', methods=['POST'])
def clone_voice():
    if not ELEVENLABS_API_KEY:
        return "ERROR: ELEVENLABS_API_KEY tidak ditemukan di file .env", 500

    if 'audio' not in request.files or 'text' not in request.form:
        return "Missing audio or text", 400
    
    text = request.form['text']
    u_id = str(uuid.uuid4())
    out_path = os.path.join(UPLOAD_FOLDER, f"out_{u_id}.mp3")
    
    try:
        headers = {"xi-api-key": ELEVENLABS_API_KEY}
        voice_id = ELEVENLABS_VOICE_ID

        if not voice_id:
            print("[INFO] No Manual Voice ID. Fetching first available voice from account...")
            voice_id = get_fallback_voice_id(ELEVENLABS_API_KEY)
        
        print(f"[ELEVENLABS] Synthesizing with Voice ID: {voice_id}")
        
        # Text to Speech
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8
            }
        }
        
        res = requests.post(tts_url, headers=headers, json=payload)
        
        if res.status_code == 200:
            with open(out_path, 'wb') as f:
                f.write(res.content)
            return send_file(out_path, mimetype='audio/mpeg')
        else:
            if "voice_not_found" in res.text:
                new_id = get_fallback_voice_id(ELEVENLABS_API_KEY)
                print(f"[RETRY] Voice not found. Retrying with ID: {new_id}")
                res = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{new_id}", headers=headers, json=payload)
                if res.status_code == 200:
                    with open(out_path, 'wb') as f:
                        f.write(res.content)
                    return send_file(out_path, mimetype='audio/mpeg')

            return f"ElevenLabs API Error: {res.text}", res.status_code
            
    except Exception as e:
        traceback.print_exc()
        return str(e), 500

@app.route('/health', methods=['GET'])
def health():
    return {
        "status": "ok", 
        "engine": "ElevenLabs-Secure",
        "key_loaded": bool(ELEVENLABS_API_KEY)
    }

if __name__ == '__main__':
    print("="*60)
    print("ElevenLabs Secure Server (Port 5002)")
    print("="*60)
    app.run(host='0.0.0.0', port=5002, debug=True)
