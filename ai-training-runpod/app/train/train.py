import os
import torch
import requests
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.tts.configs.shared_configs import BaseDatasetConfig

# Fix untuk PyTorch 2.6+ security restriction
if hasattr(torch.serialization, 'add_safe_globals'):
    torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, XttsArgs, BaseDatasetConfig])

from TTS.tts.models.xtts import Xtts
try:
    from trainer import Trainer, TrainerArgs
except ImportError:
    os.system("pip install trainer")
    from trainer import Trainer, TrainerArgs
from TTS.tts.configs.shared_configs import BaseDatasetConfig
from TTS.tts.datasets import load_tts_samples

def run_training(dataset_dir, output_dir, epochs=100, batch_size=2):
    """
    Fungsi utama untuk menjalankan fine-tuning XTTS v2.
    """
    config_path = os.path.join(dataset_dir, "config.json")
    model_path = os.path.join(dataset_dir, "model.pth")
    vocab_path = os.path.join(dataset_dir, "vocab.json")
    speaker_path = os.path.join(dataset_dir, "speakers_xtts.pth")
    metadata_path = os.path.join(dataset_dir, "metadata.csv")
    
    # 1. DOWNLOAD BASE MODEL FILES (Penting untuk Fine-tuning)
    files_to_download = {
        "config.json": "https://huggingface.co/coqui/XTTS-v2/raw/main/config.json",
        "model.pth": "https://huggingface.co/coqui/XTTS-v2/resolve/main/model.pth",
        "vocab.json": "https://huggingface.co/coqui/XTTS-v2/resolve/main/vocab.json",
        "speakers_xtts.pth": "https://huggingface.co/coqui/XTTS-v2/resolve/main/speakers_xtts.pth"
    }

    for filename, url in files_to_download.items():
        path = os.path.join(dataset_dir, filename)
        if not os.path.exists(path):
            print(f"📥 Downloading {filename}...")
            r = requests.get(url, stream=True)
            with open(path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

    # 2. XTTS CONFIGURATION
    cfg = XttsConfig()
    cfg.load_json(config_path)
    cfg.languages = ["id"]
    cfg.epochs = epochs
    cfg.batch_size = batch_size
    cfg.use_d_vector_file = False
    cfg.use_speaker_embedding = True
    cfg.use_phonemes = False # Matikan phonemes untuk hindari error espeak
    
    d_cfg = BaseDatasetConfig(
        dataset_name="custom_dataset",
        meta_file_train=metadata_path,
        meta_file_val=metadata_path,
        path=dataset_dir,
        formatter="ljspeech",
        language="id"
    )
    cfg.dataset_config = [d_cfg]

    # 3. LOAD SAMPLES
    samples = load_tts_samples(d_cfg)
    if isinstance(samples, tuple):
        samples = samples[0]
    print(f"✅ Data Terbaca: {len(samples)} file")

    # 4. INITIALIZE MODEL & LOAD CHECKPOINT
    print("🧠 Initializing XTTS v2 Model...")
    model = Xtts.init_from_config(cfg)
    model.load_checkpoint(cfg, checkpoint_path=model_path, vocab_path=vocab_path, speaker_file_path=speaker_path)
    model.to("cuda")

    # 5. CONFIGURE TRAINER
    args = TrainerArgs()
    
    print(f"🚀 Memulai proses training selama {epochs} Epoch (RTX 4090 Mode)...")
    
    trainer = Trainer(
        args, 
        cfg, 
        output_path=output_dir, 
        model=model, 
        train_samples=samples
    )
    
    try:
        trainer.fit()
    except Exception as e:
        print(f"❌ ERROR SAAT FIT: {str(e)}")
        raise e
    
    return os.path.join(output_dir, "best_model.pth")

if __name__ == "__main__":
    # Test run
    D = "/workspace/voice-changer/ai-training-runpod"
    run_training(D, os.path.join(D, "out"))
