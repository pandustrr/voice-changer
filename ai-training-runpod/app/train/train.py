import os
import torch
import requests
from TTS.tts.configs.xtts_config import XttsConfig
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
    dataset_dir: Folder yang berisi wavs/ dan metadata.csv
    output_dir: Folder hasil training
    """
    
    config_path = os.path.join(dataset_dir, "config.json")
    metadata_path = os.path.join(dataset_dir, "metadata.csv")
    
    # 1. DOWNLOAD BASE CONFIG IF NOT EXISTS
    if not os.path.exists(config_path):
        print("📥 Download base config from HuggingFace...")
        r = requests.get("https://huggingface.co/coqui/XTTS-v2/raw/main/config.json")
        with open(config_path, "wb") as f:
            f.write(r.content)

    # 2. XTTS CONFIGURATION
    cfg = XttsConfig()
    cfg.load_json(config_path)
    cfg.languages = ["id"]
    cfg.epochs = epochs
    cfg.batch_size = batch_size
    cfg.use_d_vector_file = False
    cfg.use_speaker_embedding = True
    cfg.use_phonemes = False
    cfg.ignored_speakers = []
    
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

    # 4. INITIALIZE MODEL
    model = Xtts.init_from_config(cfg)
    
    # Patch tokenizer (untuk hindari error print_logs/use_phonemes)
    model.tokenizer.use_phonemes = False
    if not hasattr(model.tokenizer, "print_logs"):
        model.tokenizer.print_logs = lambda x: None
        
    model.to("cuda")
    
    # Patch criterion (untuk versi trainer tertentu)
    if not hasattr(model, "get_criterion"):
        model.get_criterion = lambda: torch.nn.L1Loss()

    # 5. START TRAINING
    args = TrainerArgs()
    print(f"🚀 Memulai proses training selama {epochs} Epoch...")
    
    trainer = Trainer(
        args, 
        cfg, 
        output_path=output_dir, 
        model=model, 
        train_samples=samples
    )
    trainer.fit()
    
    return os.path.join(output_dir, "best_model.pth")

if __name__ == "__main__":
    # Test run
    D = "/workspace/voice-changer/ai-training-runpod"
    run_training(D, os.path.join(D, "out"))
