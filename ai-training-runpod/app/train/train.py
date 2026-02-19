"""
XTTS v2 Fine-Tuning Script untuk Bahasa Indonesia
===================================================

Script ini akan fine-tune model XTTS v2 dengan dataset Bahasa Indonesia
untuk menghasilkan suara yang lebih native dan natural.

PERSIAPAN:
1. Siapkan folder training/ dengan struktur:
   training/
   ├── wavs/           # File audio WAV (22050Hz, mono)
   └── metadata.csv    # Format: filename.wav|teks transkrip

2. Install dependencies:
   pip install TTS trainer

3. Jalankan script ini:
   python finetune_xtts_indo.py

CATATAN:
- Minimum 10 menit audio untuk hasil bagus
- Semakin banyak data, semakin baik hasilnya
- Training membutuhkan GPU (CUDA) untuk kecepatan optimal
- Tanpa GPU, training akan sangat lambat (gunakan Colab)
"""

import os
import torch
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from trainer import Trainer, TrainerArgs

# Patch torch.load untuk kompatibilitas
orig_load = torch.load
def patched_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return orig_load(*args, **kwargs)
torch.load = patched_load

# ============================================
# KONFIGURASI
# ============================================

# Path dataset
DATASET_PATH = "./training"
WAVS_PATH = os.path.join(DATASET_PATH, "wavs")
METADATA_FILE = os.path.join(DATASET_PATH, "metadata.csv")

# Path output model
OUTPUT_PATH = "./xtts_indonesian_finetuned"
os.makedirs(OUTPUT_PATH, exist_ok=True)

# Cek GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🖥️  Device: {device}")
if device == "cpu":
    print("⚠️  WARNING: Training tanpa GPU akan SANGAT lambat!")
    print("   Rekomendasi: Gunakan Google Colab dengan GPU gratis")
    print("   https://colab.research.google.com/")

# ============================================
# LOAD BASE MODEL
# ============================================

print("\n📦 Loading XTTS v2 base model...")
config = XttsConfig()
config.load_json("https://coqui.gateway.scarf.sh/v0.14.3/tts_models--multilingual--multi-dataset--xtts_v2/config.json")

model = Xtts.init_from_config(config)
model.load_checkpoint(
    config,
    checkpoint_dir="https://coqui.gateway.scarf.sh/v0.14.3/tts_models--multilingual--multi-dataset--xtts_v2/",
    eval=False,
    use_deepspeed=False
)

print("✅ Base model loaded!")

# ============================================
# PREPARE DATASET
# ============================================

print("\n📊 Preparing Indonesian dataset...")

# Cek apakah dataset ada
if not os.path.exists(METADATA_FILE):
    print(f"❌ ERROR: File {METADATA_FILE} tidak ditemukan!")
    print("\nBuat file metadata.csv dengan format:")
    print("audio_001.wav|Teks transkrip dalam Bahasa Indonesia")
    print("audio_002.wav|Contoh kalimat kedua")
    exit(1)

if not os.path.exists(WAVS_PATH):
    print(f"❌ ERROR: Folder {WAVS_PATH} tidak ditemukan!")
    exit(1)

# Hitung jumlah data
with open(METADATA_FILE, 'r', encoding='utf-8') as f:
    num_samples = len(f.readlines())

print(f"✅ Dataset found: {num_samples} samples")

# ============================================
# TRAINING CONFIGURATION
# ============================================

# Training arguments
training_args = TrainerArgs(
    # Epochs (iterasi training)
    epochs=10,  # Bisa dinaikkan untuk hasil lebih baik (20-50)
    
    # Batch size (OPTIMIZED untuk GTX 1650 4GB VRAM)
    batch_size=1,  # KECIL untuk GPU 4GB (jangan naikkan!)
    grad_accum_steps=4,  # Akumulasi gradient untuk kompensasi batch kecil
    
    # Learning rate
    lr=5e-6,  # Learning rate rendah untuk fine-tuning
    
    # Checkpoint
    save_step=100,
    save_n_checkpoints=3,
    save_best_after=100,
    
    # Output
    output_path=OUTPUT_PATH,
    
    # Logging
    print_step=10,
    plot_step=100,
    
    # Mixed precision (PENTING untuk hemat VRAM)
    mixed_precision=True,  # FP16 untuk hemat memory
    
    # Memory optimization
    use_grad_scaler=True,  # Gradient scaling untuk stability
)

# Update config untuk Indonesian
config.languages = ["id"]  # Fokus ke Bahasa Indonesia
config.dataset_config = {
    "formatter": "ljspeech",
    "meta_file_train": METADATA_FILE,
    "path": DATASET_PATH,
    "language": "id"
}

# ============================================
# START TRAINING
# ============================================

print("\n🚀 Starting fine-tuning...")
print(f"   Epochs: {training_args.epochs}")
print(f"   Batch size: {training_args.batch_size}")
print(f"   Device: {device}")
print(f"   Output: {OUTPUT_PATH}")
print("\n" + "="*50)

try:
    trainer = Trainer(
        training_args,
        config,
        output_path=OUTPUT_PATH,
        model=model,
        train_samples=None,  # Will load from metadata
        eval_samples=None
    )
    
    trainer.fit()
    
    print("\n" + "="*50)
    print("✅ Fine-tuning selesai!")
    print(f"📁 Model tersimpan di: {OUTPUT_PATH}")
    print("\nCara menggunakan model:")
    print("1. Copy folder model ke python_backend/xtts/")
    print("2. Update app.py untuk load model custom")
    
except Exception as e:
    print(f"\n❌ Error during training: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Pastikan format metadata.csv benar")
    print("2. Pastikan semua file audio ada di wavs/")
    print("3. Cek VRAM GPU (turunkan batch_size jika perlu)")
    print("4. Gunakan Google Colab jika tidak punya GPU")
