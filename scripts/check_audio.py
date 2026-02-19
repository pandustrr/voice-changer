import wave
import contextlib
import os

file_path = r"e:\Pandu-Projek\Freelance\Voice-Changer\WhatsApp-Video-2026-02-09-at-20.37.31.wav"

if os.path.exists(file_path):
    try:
        with contextlib.closing(wave.open(file_path,'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            channels = f.getnchannels()
            print(f"File: {os.path.basename(file_path)}")
            print(f"Duration: {duration/60:.2f} minutes")
            print(f"Sample Rate: {rate} Hz")
            print(f"Channels: {channels}")
    except Exception as e:
        print(f"Error reading wave file: {e}")
        # Maybe it's not a standard PCM WAV, check size vs duration
        file_size = os.path.getsize(file_path)
        print(f"File Size: {file_size / (1024*1024):.2f} MB")
else:
    print("File not found.")
