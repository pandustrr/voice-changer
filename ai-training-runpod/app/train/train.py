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
    # PINDAHKAN BASE MODEL KE FOLDER PERMANEN (Agar tidak download ulang 2GB terus)
    base_model_dir = "/workspace/base_xtts_v2"
    os.makedirs(base_model_dir, exist_ok=True)

    config_path = os.path.join(base_model_dir, "config.json")
    model_path = os.path.join(base_model_dir, "model.pth")
    vocab_path = os.path.join(base_model_dir, "vocab.json")
    speaker_path = os.path.join(base_model_dir, "speakers_xtts.pth")
    metadata_path = os.path.join(dataset_dir, "metadata.csv")
    
    # 1. DOWNLOAD BASE MODEL FILES (Jika belum ada)
    files_to_download = {
        "config.json": "https://huggingface.co/coqui/XTTS-v2/raw/main/config.json",
        "model.pth": "https://huggingface.co/coqui/XTTS-v2/resolve/main/model.pth",
        "vocab.json": "https://huggingface.co/coqui/XTTS-v2/resolve/main/vocab.json",
        "speakers_xtts.pth": "https://huggingface.co/coqui/XTTS-v2/resolve/main/speakers_xtts.pth"
    }

    for filename, url in files_to_download.items():
        path = os.path.join(base_model_dir, filename)
        if not os.path.exists(path):
            print(f"📥 Downloading {filename} to permanent storage...")
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
    cfg.use_speaker_embedding = True
    if hasattr(cfg, "model_args"):
        setattr(cfg.model_args, "use_speaker_embedding", True)
        # Compatibility Patch: Some XTTS versions expect these attributes in model_args (XttsArgs)
        patch_vars = {
            "use_d_vector_file": False,
            "use_gpt_eval": False,
            "use_language_embedding": True,
            "use_phonemes": False,
            "use_conditioning_latents": True
        }
        for var, val in patch_vars.items():
            if not hasattr(cfg.model_args, var):
                setattr(cfg.model_args, var, val)
                print(f"🔧 Patched model_args.{var} = {val}")
    
    cfg.use_d_vector_file = False
    cfg.use_phonemes = False
    
    # Tambahkan kalimat uji agar AI punya target bacaan saat evaluasi
    cfg.test_sentences = [
        "Halo, ini adalah suara buatan saya sendiri yang sedang dilatih.",
        "Semoga hasil training hari ini sangat bagus dan memuaskan.",
        "Teknologi kecerdasan buatan sekarang benar-benar luar biasa."
    ]
    
    # 2.5 AUTO-FIX METADATA (Hapus .wav di kolom index jika ada)
    if os.path.exists(metadata_path):
        print("🛠️ Checking metadata format...")
        with open(metadata_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        fixed_lines = []
        needs_fix = False
        for line in lines:
            parts = line.strip().split("|")
            if len(parts) >= 1 and parts[0].endswith(".wav"):
                parts[0] = os.path.splitext(parts[0])[0]
                fixed_lines.append("|".join(parts))
                needs_fix = True
            else:
                fixed_lines.append(line.strip())
        
        if needs_fix:
            print("🔧 Fixing metadata: Removing .wav from audio IDs...")
            with open(metadata_path, "w", encoding="utf-8") as f:
                for line in fixed_lines:
                    f.write(line + "\n")

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
    print("📋 Loading dataset samples...")
    samples = load_tts_samples(d_cfg)
    if isinstance(samples, tuple):
        samples = samples[0]
    print(f"✅ Data Terbaca: {len(samples)} file")

    # 4. INITIALIZE MODEL & LOAD CHECKPOINT
    print("🧠 Initializing XTTS v2 Model...")
    model = Xtts.init_from_config(cfg)
    model.load_checkpoint(cfg, checkpoint_path=model_path, vocab_path=vocab_path, speaker_file_path=speaker_path)
    model.to("cuda")
    
    # Ensure AudioProcessor is initialized (Fixed for 'NoneType has no attribute load_wav' & None / None division)
    from TTS.utils.audio import AudioProcessor
    if not hasattr(model, "ap") or model.ap is None:
        print("🔧 Initializing AudioProcessor (Hardened Mode)...")
        try:
            # Sediakan semua parameter krusial untuk mencegah pembagian None/None
            model.ap = AudioProcessor(
                sample_rate=22050,
                hop_length=256,
                win_length=1024,
                num_mels=80,
                preemphasis=0.0,
                ref_level_db=20,
                power=1.5,
                do_trim_silence=True
            )
        except Exception as ap_err:
            print(f"⚠️ AP Init Error: {ap_err}. Using Dummy Fallback...")
            class DummyAP:
                def __init__(self): self.sample_rate = 22050
                def load_wav(self, path):
                    import librosa
                    return librosa.load(path, sr=22050)[0]
            model.ap = DummyAP()

    # -- PATCH UNTUK KOMPATIBILITAS --
    if not hasattr(model, "get_criterion"):
        model.get_criterion = lambda: torch.nn.L1Loss()
    
    if not hasattr(model.tokenizer, "print_logs"):
        model.tokenizer.print_logs = lambda x: None
    
    model.tokenizer.use_phonemes = False

    if hasattr(model, "speaker_manager") and model.speaker_manager is not None:
        if not hasattr(model.speaker_manager, "save_ids_to_file"):
            model.speaker_manager.save_ids_to_file = lambda x: None

    if hasattr(model, "language_manager") and model.language_manager is not None:
        if not hasattr(model.language_manager, "save_ids_to_file"):
            model.language_manager.save_ids_to_file = lambda x: None
    # -- END PATCH --

    # 5. CONFIGURE TRAINER
    args = TrainerArgs()
    
    print(f"🚀 Memulai proses training {epochs} Epoch (Production Mode)...")
    
    trainer = Trainer(
        args, 
        cfg, 
        output_path=output_dir, 
        model=model, 
        train_samples=samples,
        eval_samples=samples # Gunakan data yang sama untuk validasi agar tidak error
    )
    
    # PATCH: Force Trainer to use the model's AudioProcessor
    # Ini krusial karena seringkali Trainer tidak otomatis mengambil AP dari XTTS model
    if hasattr(model, "ap"):
        trainer.ap = model.ap
        print("🔧 Trainer AP has been synchronized with Model AP")
    
    try:
        trainer.fit()
        print("✅ TRAINING SELESAI!")
        
        # Cari folder output terbaru (biasanya run-DATE...)
        import glob
        run_folders = glob.glob(os.path.join(output_dir, "run-*"))
        if run_folders:
            latest_run = max(run_folders, key=os.path.getmtime)
            best_model = os.path.join(latest_run, "best_model.pth")
            if os.path.exists(best_model):
                return best_model
                
    except BaseException as e:
        print(f"❌ ERROR SAAT FIT (FATAL): {str(e)}")
        import traceback
        traceback.print_exc()
        raise e
    
    return os.path.join(output_dir, "best_model.pth")

if __name__ == "__main__":
    # Test run
    D = "/workspace/voice-changer/ai-training-runpod"
    run_training(D, os.path.join(D, "out"))
