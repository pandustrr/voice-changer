# Fine-Tuning XTTS untuk Bahasa Indonesia - Panduan Lengkap

## 📋 Daftar Isi

1. [Persiapan Data](#persiapan-data)
2. [Setup Environment](#setup-environment)
3. [Fine-Tuning Process](#fine-tuning-process)
4. [Deployment](#deployment)
5. [Estimasi Biaya & Waktu](#estimasi-biaya--waktu)

---

## 1. Persiapan Data

### Data yang Dibutuhkan:

- **Audio**: 10-60 menit rekaman Bahasa Indonesia
- **Transkrip**: Teks dari audio tersebut (harus akurat 100%)
- **Format**: WAV, 22050 Hz, Mono

### Struktur Folder:

```
dataset/
├── wavs/
│   ├── audio_001.wav
│   ├── audio_002.wav
│   └── ...
└── metadata.csv
```

### Format `metadata.csv`:

```csv
wavs/audio_001.wav|Selamat pagi, nama saya Pandu.
wavs/audio_002.wav|Hari ini cuaca sangat cerah.
wavs/audio_003.wav|Saya sedang belajar voice cloning.
```

### Cara Mendapatkan Data:

**Opsi A: Rekam Sendiri** (Paling Direkomendasikan)

- Baca 100-200 kalimat Bahasa Indonesia
- Durasi total: 20-30 menit
- Rekam di ruangan tenang
- Gunakan mic yang bagus

**Opsi B: Dataset Publik**

- Common Voice Indonesia: https://commonvoice.mozilla.org/id
- Download gratis, sudah ada transkrip
- Pilih speaker yang suaranya mirip target Anda

**Opsi C: Hire Voice Actor**

- Upwork/Fiverr: $20-50 untuk 30 menit
- Minta baca script yang Anda siapkan

---

## 2. Setup Environment

### Hardware Requirements:

| GPU              | VRAM | Batch Size | Training Time | Biaya                     |
| ---------------- | ---- | ---------- | ------------- | ------------------------- |
| GTX 1060         | 6GB  | 2-4        | 12-24 jam     | Gratis (pakai sendiri)    |
| RTX 3060         | 12GB | 8-16       | 6-8 jam       | Gratis (pakai sendiri)    |
| Cloud GPU (T4)   | 16GB | 16-32      | 4-6 jam       | $0.5/jam = **Rp 30k-50k** |
| Cloud GPU (A100) | 40GB | 32-64      | 2-3 jam       | $1.5/jam = **Rp 50k-75k** |

### Software Requirements:

```bash
# Python 3.10
# CUDA 11.8 atau 12.1
# PyTorch 2.0+
# Coqui TTS (fork untuk fine-tuning)
```

---

## 3. Fine-Tuning Process

### Step 1: Install Dependencies

```bash
# Clone XTTS fine-tuning repo
git clone https://github.com/coqui-ai/TTS
cd TTS

# Install dependencies
pip install -e .
pip install trainer
pip install deepspeed  # Untuk training lebih cepat
```

### Step 2: Prepare Config

File: `config_finetune.json`

```json
{
    "run_name": "xtts_indonesian",
    "model_name": "xtts",
    "language": "id",
    "dataset_path": "./dataset",
    "output_path": "./output",

    "batch_size": 8, // Sesuaikan dengan VRAM
    "epochs": 100,
    "learning_rate": 5e-6,
    "mixed_precision": true, // Hemat VRAM

    "num_loader_workers": 4,
    "save_step": 1000,
    "eval_step": 500
}
```

### Step 3: Run Training

```bash
# Training command
python TTS/bin/train_xtts.py \
    --config_path config_finetune.json \
    --restore_path pretrained_models/xtts_v2.pth \
    --use_cuda true
```

### Step 4: Monitor Progress

Training akan menampilkan:

```
Epoch: 1/100 | Loss: 2.345 | Time: 00:15:23
Epoch: 2/100 | Loss: 2.123 | Time: 00:30:45
...
Epoch: 100/100 | Loss: 0.456 | Time: 08:45:12
```

**Target Loss:** < 0.5 untuk hasil bagus

---

## 4. Deployment

### Step 1: Export Model

Setelah training selesai, Anda akan punya:

```
output/
├── best_model.pth  ← Model fine-tuned
├── config.json
└── vocab.json
```

### Step 2: Integrate ke Aplikasi Anda

Update `python_backend/xtts/app.py`:

```python
# Ganti model loading
# SEBELUM (model default):
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# SESUDAH (model fine-tuned):
tts = TTS(model_path="./output/best_model.pth",
          config_path="./output/config.json").to(device)
```

### Step 3: Test

```python
# Test dengan teks Indonesia
tts.tts_to_file(
    text="Halo, ini adalah tes voice cloning Indonesia.",
    speaker_wav="reference.wav",
    language="id",
    file_path="output.wav"
)
```

---

## 5. Estimasi Biaya & Waktu

### Skenario A: GTX 1060 (Gratis)

**Biaya:**

- Hardware: **Rp 0** (pakai GPU sendiri)
- Data: **Rp 0** (rekam sendiri) atau **Rp 300k-500k** (hire voice actor)
- Total: **Rp 0 - 500k** (sekali saja)

**Waktu:**

- Persiapan data: 2-4 jam
- Training: 12-24 jam
- Testing & deployment: 2-3 jam
- **Total: 1-2 hari**

**Hasil:**

- Logat Indonesia: ⭐⭐⭐⭐ (80-90% murni)
- Artikulasi: ⭐⭐⭐⭐
- Kemiripan suara: ⭐⭐⭐⭐⭐

---

### Skenario B: Cloud GPU (Bayar Sekali)

**Biaya:**

- GPU rental (6 jam): **Rp 30k-50k**
- Data: **Rp 0** (rekam sendiri) atau **Rp 300k-500k** (hire voice actor)
- Total: **Rp 30k - 550k** (sekali saja)

**Waktu:**

- Persiapan data: 2-4 jam
- Training: 4-6 jam
- Testing & deployment: 2-3 jam
- **Total: 8-13 jam (1 hari)**

**Hasil:**

- Logat Indonesia: ⭐⭐⭐⭐⭐ (95-100% murni)
- Artikulasi: ⭐⭐⭐⭐⭐
- Kemiripan suara: ⭐⭐⭐⭐⭐

---

### Skenario C: Tetap Pakai XTTS Default (Gratis)

**Biaya:**

- **Rp 0**

**Waktu:**

- **0 jam** (sudah jalan)

**Hasil:**

- Logat Indonesia: ⭐⭐⭐ (60-70% murni, masih ada aksen Inggris)
- Artikulasi: ⭐⭐⭐
- Kemiripan suara: ⭐⭐⭐⭐

---

## 🎯 Kesimpulan

### Kapan Fine-Tune?

**YA, jika:**

- ✅ Anda punya waktu 1-2 hari
- ✅ Budget ada (Rp 30k-500k sekali saja)
- ✅ Butuh kualitas production-grade
- ✅ Klien strict soal aksen Indonesia

**TIDAK, jika:**

- ❌ Butuh solusi instant
- ❌ Budget 0 rupiah
- ❌ Klien tidak terlalu strict soal aksen
- ❌ Tidak ada waktu untuk setup

---

## 📚 Resources

- **Coqui TTS Docs**: https://docs.coqui.ai/
- **Fine-tuning Guide**: https://github.com/coqui-ai/TTS/wiki/Fine-Tuning
- **Common Voice ID**: https://commonvoice.mozilla.org/id
- **GPU Rental**:
    - Google Colab Pro: https://colab.research.google.com/
    - Vast.ai: https://vast.ai/
    - RunPod: https://runpod.io/

---

## 🤝 Bantuan Lebih Lanjut

Jika Anda memutuskan untuk fine-tune, saya bisa:

1. Buatkan script automation lengkap
2. Guide step-by-step via chat
3. Troubleshoot jika ada error
4. Optimize config untuk GPU Anda

**Siap membantu kapan saja!** 🚀
