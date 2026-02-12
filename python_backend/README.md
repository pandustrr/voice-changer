# Python Backend - Voice Cloning System

Sistem backend untuk Voice Cloning dengan dukungan **Bahasa Indonesia Native**.

## 📁 Struktur Folder

```
python_backend/
│
├── xtts/                           # XTTS v2 Engine (Port 5000)
│   ├── app.py                      # Server utama XTTS
│   ├── indo_cleaner.py             # Text processor Indonesia
│   ├── xtts_cleaner.py             # Optimasi fonetik
│   ├── check_languages.py          # Tool cek bahasa support
│   └── README.md                   # Dokumentasi XTTS
│
├── gptsovits_bridge/               # GPT-SoVITS Bridge (Port 5001)
│   ├── app.py                      # Server bridge
│   ├── requirements.txt            # Dependencies bridge
│   ├── README.md                   # Dokumentasi lengkap
│   └── QUICKSTART.md               # Panduan cepat
│
├── GPT-SoVITS/                     # GPT-SoVITS Core (Port 9880)
│   ├── api_v2.py                   # API server utama
│   ├── GPT_SoVITS/
│   │   └── text/
│   │       ├── indonesian.py       # ✨ Modul Indonesia Native
│   │       ├── cleaner.py          # Text cleaner (sudah diupdate)
│   │       ├── english.py
│   │       ├── japanese.py
│   │       └── ...
│   └── GPT_SoVITS/configs/
│       └── tts_infer.yaml          # Konfigurasi model
│
├── download_gptsovits_models.py    # Script download model GPT-SoVITS
├── download_openvoice_models.py    # Script download model OpenVoice
├── requirements.txt                # Dependencies umum
└── requirements_gptsovits.txt      # Dependencies GPT-SoVITS

```

## 🚀 Cara Menjalankan

### Opsi 1: XTTS (Cepat, Gratis, Kualitas Baik)

```powershell
cd xtts
python app.py
```

Server akan jalan di **http://localhost:5000**

### Opsi 2: GPT-SoVITS (Artikulasi Native Indonesia)

**Terminal 1 - Core Engine:**

```powershell
cd GPT-SoVITS
python api_v2.py -c GPT_SoVITS/configs/tts_infer.yaml
```

**Terminal 2 - Bridge:**

```powershell
cd gptsovits_bridge
python app.py
```

Server akan jalan di **http://localhost:5001**

## 🎯 Perbandingan Engine

| Fitur                  | XTTS                       | GPT-SoVITS                      |
| ---------------------- | -------------------------- | ------------------------------- |
| **Kecepatan**          | ⚡ Sangat Cepat            | 🐢 Agak Lambat                  |
| **Kualitas Indonesia** | ⭐⭐⭐ (Phonetic Bridge)   | ⭐⭐⭐⭐⭐ (Native)             |
| **Artikulasi**         | Kurang jelas, agak "lebay" | Sangat jelas dan natural        |
| **Setup**              | 1 Terminal                 | 2 Terminal                      |
| **Reference Text**     | Tidak perlu                | **Wajib** (untuk hasil terbaik) |
| **Rekomendasi**        | Testing cepat              | **Production**                  |

## 📝 Catatan Penting

### XTTS:

- Menggunakan Portuguese (`pt`) sebagai phonetic bridge
- Tidak perlu reference text
- Cocok untuk testing cepat

### GPT-SoVITS:

- **Modul `indonesian.py` sudah terintegrasi** di core engine
- **Wajib isi Reference Text** untuk hasil maksimal
- Parameter sudah dioptimasi untuk artikulasi jelas
- Hasil jauh lebih natural untuk bahasa Indonesia

## 🔧 Troubleshooting

### XTTS Offline

```powershell
# Cek apakah port 5000 sudah dipakai
netstat -ano | findstr :5000

# Jika ada, matikan prosesnya
taskkill /F /PID <PID_NUMBER>
```

### GPT-SoVITS Offline

```powershell
# Pastikan core engine (port 9880) running terlebih dahulu
cd GPT-SoVITS
python api_v2.py -c GPT_SoVITS/configs/tts_infer.yaml

# Baru jalankan bridge
cd ../gptsovits_bridge
python app.py
```

## 📦 Install Dependencies

### Untuk XTTS:

```powershell
cd xtts
pip install flask flask-cors torch TTS librosa soundfile
```

### Untuk GPT-SoVITS:

```powershell
# Install core dependencies
pip install -r requirements_gptsovits.txt

# Install bridge dependencies
cd gptsovits_bridge
pip install -r requirements.txt
```

## 🎓 Dokumentasi Lengkap

- **XTTS**: Lihat `xtts/README.md`
- **GPT-SoVITS**: Lihat `gptsovits_bridge/README.md` dan `QUICKSTART.md`

---

**Dibuat dengan ❤️ untuk Voice Cloning Indonesia Native**
