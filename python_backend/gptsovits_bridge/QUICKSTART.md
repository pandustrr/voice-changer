# Cara Menjalankan GPT-SoVITS Bridge

## Langkah 1: Install Dependencies (Sekali Saja)

```powershell
pip install -r requirements.txt
```

## Langkah 2: Jalankan GPT-SoVITS Core Engine

Buka terminal baru, lalu:

```powershell
cd ../GPT-SoVITS
python api_v2.py -c GPT_SoVITS/configs/tts_infer.yaml
```

Tunggu hingga muncul:

```
 > Running on http://127.0.0.1:9880
```

## Langkah 3: Jalankan Bridge Server

Di terminal lain (atau terminal ini), jalankan:

```powershell
python app.py
```

Tunggu hingga muncul:

```
 * Running on http://127.0.0.1:5001
```

## Selesai!

Server GPT-SoVITS sudah siap digunakan dari website Anda.

## Catatan Penting

- GPT-SoVITS Core (port 9880) HARUS running terlebih dahulu
- Bridge (port 5001) baru bisa jalan setelah core aktif
- Jangan tutup kedua terminal selama menggunakan sistem
