# GPT-SoVITS Model Download Guide

## Required Models

GPT-SoVITS membutuhkan beberapa pre-trained models (~2.5 GB total).

### Cara Download Otomatis (Recommended)

Jalankan script download otomatis:

```bash
cd python_backend
python download_gptsovits_models.py
```

### Cara Download Manual

Jika download otomatis gagal, download manual dari link berikut:

#### 1. GPT Model (s1bert25.pth)

- **Size**: ~500 MB
- **Link**: https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s1bert25.pth
- **Save to**: `python_backend/GPT-SoVITS/pretrained_models/s1bert25.pth`

#### 2. SoVITS Generator (s2G488k.pth)

- **Size**: ~600 MB
- **Link**: https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s2G488k.pth
- **Save to**: `python_backend/GPT-SoVITS/pretrained_models/s2G488k.pth`

#### 3. SoVITS Discriminator (s2D488k.pth)

- **Size**: ~300 MB
- **Link**: https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s2D488k.pth
- **Save to**: `python_backend/GPT-SoVITS/pretrained_models/s2D488k.pth`

#### 4. BERT Model (chinese-roberta-wwm-ext-large)

- **Size**: ~1.2 GB
- **Link**: https://huggingface.co/hfl/chinese-roberta-wwm-ext-large/resolve/main/pytorch_model.bin
- **Save to**: `python_backend/GPT-SoVITS/pretrained_models/chinese-roberta-wwm-ext-large/pytorch_model.bin`

**IMPORTANT**: Buat folder `chinese-roberta-wwm-ext-large` terlebih dahulu!

```bash
mkdir -p GPT-SoVITS/pretrained_models/chinese-roberta-wwm-ext-large
```

### Struktur Folder yang Benar

Setelah download, struktur folder harus seperti ini:

```
python_backend/
└── GPT-SoVITS/
    └── pretrained_models/
        ├── s1bert25.pth
        ├── s2G488k.pth
        ├── s2D488k.pth
        └── chinese-roberta-wwm-ext-large/
            └── pytorch_model.bin
```

### Verifikasi Download

Jalankan script verifikasi:

```bash
python verify_models.py
```

Script akan mengecek apakah semua model sudah ter-download dengan benar.

## Troubleshooting

### Download Lambat?

Gunakan download manager seperti:

- **IDM** (Internet Download Manager) - Windows
- **wget** - Linux/Mac
- **aria2c** - Cross-platform

Contoh dengan wget:

```bash
wget -O GPT-SoVITS/pretrained_models/s1bert25.pth https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s1bert25.pth
```

### Koneksi Terputus?

File besar bisa di-resume. Gunakan download manager yang support resume.

### Alternatif Mirror

Jika HuggingFace lambat, coba mirror China:

- https://hf-mirror.com/lj1995/GPT-SoVITS

## Next Steps

Setelah semua model ter-download:

1. Jalankan server GPT-SoVITS:

    ```bash
    python app_gptsovits.py
    ```

2. Test dengan curl:

    ```bash
    curl http://localhost:5001/health
    ```

3. Jika berhasil, update Laravel controller untuk menggunakan port 5001
