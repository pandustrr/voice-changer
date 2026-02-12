# GPT-SoVITS Bridge for Voice-Changer

Folder ini berisi sistem jembatan untuk **GPT-SoVITS** agar mendukung Bahasa Indonesia dengan artikulasi native.

## Struktur File

- `app.py`: Server bridge (Flask) yang berjalan di port **5001**.
- `requirements.txt`: Daftar dependencies Python yang dibutuhkan.

## Cara Menjalankan

### 1. Jalankan GPT-SoVITS Core Engine (Terminal 1)

```powershell
cd ../GPT-SoVITS
python api_v2.py -c GPT_SoVITS/configs/tts_infer.yaml
```

### 2. Jalankan Bridge Server (Terminal 2)

```powershell
cd gptsovits_bridge
python app.py
```

## Fitur Unggulan

- **Native Indonesian Support**: Menggunakan modul `indonesian.py` yang sudah terintegrasi di GPT-SoVITS core.
- **Clear Articulation**: Parameter sudah di-tune untuk artikulasi yang tajam dan jelas.
- **Reference Text System**: Mendukung input teks referensi untuk kemiripan suara maksimal.
- **No Auto-Split**: Teks dibaca persis seperti yang Anda ketik, tidak dipotong otomatis.
- **Long Audio Support**: Sistem otomatis memotong audio panjang ke segmen 7 detik terbaik.

## Parameter Optimasi

- `top_k`: 15 (artikulasi lebih jelas)
- `top_p`: 0.85 (variasi fonem natural)
- `temperature`: 0.75 (percaya diri, tidak mumbling)
- `repetition_penalty`: 1.2 (hindari suara nyangkut)
- `text_split_method`: cut0 (baca utuh tanpa split)

## Troubleshooting

- **Artikulasi kurang jelas**: Pastikan rekaman referensi Anda jelas dan tidak terlalu cepat
- **Suara tidak mirip**: Isi field "Reference Text" dengan persis apa yang Anda ucapkan di rekaman
- **Server offline**: Pastikan GPT-SoVITS core (port 9880) sudah running terlebih dahulu
