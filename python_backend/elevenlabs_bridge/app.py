"""
ElevenLabs Voice Cloning Bridge - Production Ready
Port: 5002
Kualitas: Production-grade (setara Filmora)
"""

import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
import uuid

app = Flask(__name__)
CORS(app)

# ElevenLabs Configuration
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', 'YOUR_API_KEY_HERE')
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

UPLOAD_FOLDER = 'C:\\Temp\\voice_changer_elevenlabs'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/clone', methods=['POST'])
def clone_voice():
    """
    Voice cloning endpoint menggunakan ElevenLabs API
    
    Parameters:
    - audio: File audio referensi (5-10 detik)
    - text: Teks yang ingin diucapkan
    - speed: Kecepatan bicara (0.5-2.0)
    - reference_text: Teks yang diucapkan di audio referensi (opsional)
    
    Returns:
    - Audio file (WAV/MP3)
    """
    
    if 'audio' not in request.files or 'text' not in request.form:
        return jsonify({"error": "Missing audio or text"}), 400
    
    audio_file = request.files['audio']
    text = request.form['text']
    speed = float(request.form.get('speed', 1.0))
    
    u_id = str(uuid.uuid4())
    audio_path = os.path.join(UPLOAD_FOLDER, f"ref_{u_id}.wav")
    output_path = os.path.join(UPLOAD_FOLDER, f"out_{u_id}.mp3")
    
    try:
        # Save reference audio
        audio_file.save(audio_path)
        
        # Step 1: Create voice clone (instant voice cloning)
        print("[ELEVENLABS] Creating instant voice clone...")
        
        with open(audio_path, 'rb') as f:
            files = {'file': f}
            headers = {'xi-api-key': ELEVENLABS_API_KEY}
            
            # ElevenLabs instant voice cloning endpoint
            clone_response = requests.post(
                f"{ELEVENLABS_API_URL}/voices/add",
                headers=headers,
                files=files,
                data={'name': f'clone_{u_id}'}
            )
        
        if clone_response.status_code != 200:
            return jsonify({
                "error": "ElevenLabs API error",
                "details": clone_response.text
            }), 500
        
        voice_id = clone_response.json()['voice_id']
        print(f"[ELEVENLABS] Voice cloned: {voice_id}")
        
        # Step 2: Generate speech with cloned voice
        print("[ELEVENLABS] Generating speech...")
        
        tts_payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",  # Supports Indonesian
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        tts_response = requests.post(
            f"{ELEVENLABS_API_URL}/text-to-speech/{voice_id}",
            headers={
                'xi-api-key': ELEVENLABS_API_KEY,
                'Content-Type': 'application/json'
            },
            json=tts_payload
        )
        
        if tts_response.status_code != 200:
            return jsonify({
                "error": "TTS generation failed",
                "details": tts_response.text
            }), 500
        
        # Save output
        with open(output_path, 'wb') as f:
            f.write(tts_response.content)
        
        print("[SUCCESS] ElevenLabs voice generated!")
        
        # Step 3: Delete temporary voice (cleanup)
        requests.delete(
            f"{ELEVENLABS_API_URL}/voices/{voice_id}",
            headers={'xi-api-key': ELEVENLABS_API_KEY}
        )
        
        return send_file(output_path, mimetype='audio/mpeg')
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({"error": str(e)}), 500
        
    finally:
        # Cleanup
        for p in [audio_path]:
            if os.path.exists(p):
                try: os.remove(p)
                except: pass

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    # Check if API key is configured
    api_key_status = "configured" if ELEVENLABS_API_KEY != 'YOUR_API_KEY_HERE' else "not_configured"
    
    return jsonify({
        "status": "online",
        "engine": "ElevenLabs-v2-Multilingual",
        "api_key": api_key_status,
        "supported_languages": ["id", "en", "es", "pt", "ja", "zh", "ko", "de", "fr", "it"]
    })

@app.route('/quota', methods=['GET'])
def check_quota():
    """Check remaining ElevenLabs quota"""
    try:
        response = requests.get(
            f"{ELEVENLABS_API_URL}/user",
            headers={'xi-api-key': ELEVENLABS_API_KEY}
        )
        
        if response.status_code == 200:
            user_data = response.json()
            return jsonify({
                "character_count": user_data.get('character_count', 0),
                "character_limit": user_data.get('character_limit', 0),
                "remaining": user_data.get('character_limit', 0) - user_data.get('character_count', 0)
            })
        else:
            return jsonify({"error": "Failed to fetch quota"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("ElevenLabs Voice Cloning Bridge")
    print("=" * 60)
    print(f"API Key Status: {'✅ Configured' if ELEVENLABS_API_KEY != 'YOUR_API_KEY_HERE' else '❌ Not Configured'}")
    print("Port: 5002")
    print("Endpoint: http://localhost:5002/clone")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5002, debug=True)
