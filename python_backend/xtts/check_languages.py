import torch
# Patch torch.load
orig_load = torch.load
def patched_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return orig_load(*args, **kwargs)
torch.load = patched_load

from TTS.api import TTS
import os

os.environ["COQUI_TOS_AGREED"] = "1"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
print(f"Supported languages: {tts.languages}")
