#!/usr/bin/env python3
"""
speech_to_text.py
Standalone Speech-to-Text module using Whisper
"""

import whisper
import torch
import warnings
warnings.filterwarnings('ignore')


class SpeechToText:
    """
    Standalone Speech-to-Text (STT) using Whisper
    """

    def __init__(self, model_name: str = "medium", device: str = None, language: str = "id"):
        print(f"🎙️ Initializing Speech-to-Text module")
        print(f"📦 Loading Whisper model: {model_name}")

        # Set device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        print(f"💻 Using device: {self.device}")

        # Load Whisper model
        try:
            self.model = whisper.load_model(model_name, device=self.device)
            print("✅ Whisper model loaded successfully!\n")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            print("⚙️ Falling back to 'base' model...")
            self.model = whisper.load_model("base", device=self.device)

        self.language = language

    def transcribe(self, audio_path: str, **kwargs):
        """
        Transcribe audio file to text.
        Returns dict: {'text': str, 'segments': list, 'language': str}
        """
        print(f"🎧 Transcribing: {audio_path}")
        result = self.model.transcribe(
            audio_path,
            language=self.language,
            task="transcribe",
            word_timestamps=True,
            condition_on_previous_text=False,
            **kwargs
        )
        print("✅ Transcription complete!\n")
        return result


# ========== DEMO ==========

if __name__ == "__main__":
    stt = SpeechToText(model_name="medium", device="cpu", language="id")

    # Path ke file audio
    audio_path = "./Datakom.m4a"
    # audio_path = "./bad.wav"

    result = stt.transcribe(audio_path)
    print("📝 Transcribed text:")
    print(result["text"])
