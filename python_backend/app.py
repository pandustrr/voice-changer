import os
from flask import Flask, request, send_file
from flask_cors import CORS
import torch
import uuid

# Patch torch.load to support older models in newer PyTorch versions
orig_load = torch.load
def patched_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return orig_load(*args, **kwargs)
torch.load = patched_load

from TTS.api import TTS

# Automatically accept Coqui TTS license
os.environ["COQUI_TOS_AGREED"] = "1"


app = Flask(__name__)
CORS(app)

# Load model (XTTS v2 is great for cloning)
# It will download automatically on first run
print("Loading TTS model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
# Note: XTTS requires accepting license for commercial use
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)


UPLOAD_FOLDER = 'temp_audio'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/clone', methods=['POST'])
def clone_voice():
    if 'audio' not in request.files or 'text' not in request.form:
        return "Missing audio or text", 400
    
    audio_file = request.files['audio']
    text = request.form['text']
    
    # Save the reference audio (might be webm from browser)
    temp_ref_path = os.path.join(UPLOAD_FOLDER, f"temp_{uuid.uuid4()}.blob")
    audio_file.save(temp_ref_path)
    
    # Convert to proper WAV for TTS (browser sends webm/ogg even if called .wav)
    ref_filename = f"{uuid.uuid4()}_ref.wav"
    ref_path = os.path.join(UPLOAD_FOLDER, ref_filename)
    
    try:
        import librosa
        import soundfile as sf
        # Load any audio format and save as standard WAV PCM 16
        y, sr = librosa.load(temp_ref_path, sr=22050)
        sf.write(ref_path, y, sr, format='WAV', subtype='PCM_16')
        os.remove(temp_ref_path) # Clean up blob
    except Exception as e:
        print(f"Conversion error: {str(e)}")
        # Fallback: if librosa fails, just rename (might still fail in TTS)
        os.rename(temp_ref_path, ref_path)
    
    # Output path
    out_filename = f"{uuid.uuid4()}_out.wav"
    out_path = os.path.join(UPLOAD_FOLDER, out_filename)
    
    print(f"Generating voice for text: {text}")
    
    try:
        # Generate cloned voice
        # speaker_wav is the reference audio
        # language is 'en' or 'id' (XTTS supports many, but not 'id' in base models apparently)
        tts.tts_to_file(
            text=text,
            speaker_wav=ref_path,
            language="en", # Changed to 'en' as request failed with 'id'
            file_path=out_path
        )
        
        return send_file(out_path, mimetype='audio/wav')
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return str(e), 500
    
    finally:
        # Clean up files if you want, or keep them for cache
        # os.remove(ref_path)
        pass

if __name__ == '__main__':
    app.run(port=5000, debug=True)
