import os
import torch
import requests
from pathlib import Path

# ─── Patch torch.load untuk keamanan PyTorch 2.6+ ───────────────────────────
orig_load = torch.load
def patched_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return orig_load(*args, **kwargs)
torch.load = patched_load

from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts, XttsAudioConfig, XttsArgs
from TTS.tts.configs.shared_configs import BaseDatasetConfig

# Allowlist untuk PyTorch serialization safety
if hasattr(torch.serialization, 'add_safe_globals'):
    torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, XttsArgs, BaseDatasetConfig])

try:
    from trainer import Trainer, TrainerArgs
except ImportError:
    os.system("pip install trainer")
    from trainer import Trainer, TrainerArgs


def run_training(dataset_dir, output_dir, epochs=100, batch_size=2):
    """
    Fine-tuning XTTS v2 — Pendekatan bersih ala kode teman (train_samples=None).
    Trainer handle dataset loading sendiri → menghindari semua collate_fn TypeError.
    """

    # ── 1. DOWNLOAD BASE MODEL (Disimpan permanen agar tidak redownload) ──────
    base_model_dir = "/workspace/base_xtts_v2"
    os.makedirs(base_model_dir, exist_ok=True)

    files_to_download = {
        "config.json":       "https://huggingface.co/coqui/XTTS-v2/raw/main/config.json",
        "model.pth":         "https://huggingface.co/coqui/XTTS-v2/resolve/main/model.pth",
        "vocab.json":        "https://huggingface.co/coqui/XTTS-v2/resolve/main/vocab.json",
        "speakers_xtts.pth": "https://huggingface.co/coqui/XTTS-v2/resolve/main/speakers_xtts.pth",
    }
    for filename, url in files_to_download.items():
        dest = os.path.join(base_model_dir, filename)
        if not os.path.exists(dest):
            print(f"📥 Downloading {filename} to permanent storage...")
            r = requests.get(url, stream=True)
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

    # ── 2. SIAPKAN STRUKTUR DATASET (dataset_dir/wavs/) ───────────────────────
    # LJSpeech formatter mengharapkan: path/wavs/*.wav + metadata.csv di root path
    metadata_path = os.path.join(dataset_dir, "metadata.csv")
    wavs_dir = os.path.join(dataset_dir, "wavs")

    # Pindahkan audio ke subfolder wavs/ jika belum ada
    os.makedirs(wavs_dir, exist_ok=True)
    if os.path.exists(metadata_path):
        # Cek apakah ada .wav di root yang perlu dipindah ke wavs/
        wav_files_in_root = [f for f in os.listdir(dataset_dir) if f.endswith(".wav")]
        if wav_files_in_root:
            print(f"� Memindahkan {len(wav_files_in_root)} file .wav ke subfolder wavs/...")
            for wav_file in wav_files_in_root:
                src = os.path.join(dataset_dir, wav_file)
                dst = os.path.join(wavs_dir, wav_file)
                if not os.path.exists(dst):
                    os.rename(src, dst)

    # ── 2.5 AUTO-FIX METADATA (Hapus .wav di kolom ID jika ada) ──────────────
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
                f.write("\n".join(fixed_lines) + "\n")

    # Log jumlah sample
    if os.path.exists(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            num_samples = len([l for l in f.readlines() if l.strip()])
        print(f"✅ Dataset siap: {num_samples} file")

    # ── 3. KONFIGURASI XTTS ───────────────────────────────────────────────────
    config_path = os.path.join(base_model_dir, "config.json")
    cfg = XttsConfig()
    cfg.load_json(config_path)

    # Dataset config — path ke PARENT dir, formatter ljspeech cari wavs/ sendiri
    d_cfg = BaseDatasetConfig(
        formatter="ljspeech",
        meta_file_train="metadata.csv",  # relatif terhadap path
        path=dataset_dir,                # parent dir (berisi wavs/ dan metadata.csv)
        language="en",                   # 'id' tidak tersedia di tokenizer XTTS v2
    )
    cfg.datasets = [d_cfg]

    # Parameter training
    cfg.epochs = epochs
    cfg.batch_size = batch_size
    cfg.eval_batch_size = max(1, batch_size // 2)
    cfg.num_loader_workers = 4
    cfg.grad_acumm_steps = 4           # Effective batch = batch_size * 4
    cfg.lr = 5e-6                       # Learning rate konservatif
    cfg.save_step = 1000
    cfg.print_step = 50
    cfg.mixed_precision = False

    # Matikan fitur yang tidak diperlukan (mencegah mapping TypeError)
    cfg.use_d_vector_file = False
    cfg.use_phonemes = False
    cfg.use_language_embedding = False

    # Uji kalimat saat evaluasi
    cfg.test_sentences = [
        "Halo, ini adalah suara buatan saya sendiri yang sedang dilatih.",
        "Semoga hasil training hari ini sangat bagus dan memuaskan.",
        "Teknologi kecerdasan buatan sekarang benar-benar luar biasa.",
    ]

    # Patch model_args untuk kompatibilitas berbagai versi TTS
    if hasattr(cfg, "model_args") and cfg.model_args is not None:
        compat_patch = {
            "use_speaker_embedding":    True,
            "use_d_vector_file":        False,
            "use_gpt_eval":             False,
            "use_language_embedding":   False,
            "use_phonemes":             False,
            "use_conditioning_latents": True,
        }
        for var, val in compat_patch.items():
            if not hasattr(cfg.model_args, var):
                setattr(cfg.model_args, var, val)
                print(f"🔧 Patched model_args.{var} = {val}")

    # ── 4. INISIALISASI MODEL & LOAD CHECKPOINT ───────────────────────────────
    print("🧠 Initializing XTTS v2 Model...")
    model = Xtts.init_from_config(cfg)

    # Gunakan checkpoint_dir (sama dengan pendekatan teman yang berhasil)
    model.load_checkpoint(
        cfg,
        checkpoint_dir=base_model_dir,   # ← checkpoint_dir bukan checkpoint_path
        eval=False,
        strict=False,
    )
    model.to("cuda")

    # Patch: get_criterion — diperlukan Trainer tapi tidak ada di Xtts versi ini
    if not hasattr(model, "get_criterion"):
        print("🔧 Patching model.get_criterion...")
        model.get_criterion = lambda: torch.nn.L1Loss()

    # Patch tokenizer jika versi baru tidak punya text_to_ids
    if hasattr(model, "tokenizer") and not hasattr(model.tokenizer, "text_to_ids"):
        print("🔧 Patching tokenizer.text_to_ids (lang=en)...")
        model.tokenizer.text_to_ids = lambda x: model.tokenizer.encode(x, lang="en")

    # ── 5. TRAINER — train_samples=None agar Trainer load sendiri ────────────
    print(f"🚀 Memulai proses training {epochs} Epoch...")
    trainer_args = TrainerArgs(
        restore_path=None,
        skip_train_epoch=False,
    )

    trainer = Trainer(
        trainer_args,
        cfg,
        output_path=output_dir,
        model=model,
        train_samples=None,   # ← Trainer handle dataset loading sendiri
        eval_samples=None,    # ← Menghindari collate_fn speaker/language TypeError
    )

    # ── 6. FIT ────────────────────────────────────────────────────────────────
    try:
        trainer.fit()
        print("✅ TRAINING SELESAI!")

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
    D = "/workspace/voice-changer/ai-training-runpod"
    run_training(D, os.path.join(D, "out"))
