# ElevenLabs Voice Cloning Bridge

Folder ini berisi bridge untuk **ElevenLabs API** - solusi voice cloning **production-grade** dengan kualitas setara Filmora.

## 🎯 Fitur

- ✅ **Instant Voice Cloning** - Upload audio 5-10 detik, langsung clone
- ✅ **Logat Indonesia Murni** - Model sudah dilatih dengan data Indonesia native
- ✅ **Artikulasi Sempurna** - Kualitas production-grade
- ✅ **Multi-bahasa** - Mendukung 10+ bahasa termasuk Indonesia
- ✅ **Quota Management** - Endpoint untuk cek sisa quota
- ✅ **Auto Cleanup** - Voice temporary otomatis dihapus

## 📋 Cara Setup

### 1. Daftar ElevenLabs

1. Buka: https://elevenlabs.io/
2. Sign up (gratis)
3. Dapatkan API Key di: https://elevenlabs.io/app/settings/api-keys

### 2. Set API Key

**Opsi A: Environment Variable (Recommended)**

```powershell
# Windows PowerShell
$env:ELEVENLABS_API_KEY="your_api_key_here"
```

**Opsi B: Edit app.py**

```python
ELEVENLABS_API_KEY = "your_api_key_here"  # Line 15
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Jalankan Server

```powershell
python app.py
```

Server akan jalan di **http://localhost:5002**

## 🎤 Cara Menggunakan

### Endpoint: `/clone`

**Request:**

```
POST http://localhost:5002/clone
Content-Type: multipart/form-data

- audio: File audio referensi (5-10 detik)
- text: Teks yang ingin diucapkan
- speed: Kecepatan (0.5-2.0, default 1.0)
```

**Response:**

```
Audio file (MP3)
```

### Endpoint: `/health`

**Request:**

```
GET http://localhost:5002/health
```

**Response:**

```json
{
  "status": "online",
  "engine": "ElevenLabs-v2-Multilingual",
  "api_key": "configured",
  "supported_languages": ["id", "en", "es", ...]
}
```

### Endpoint: `/quota`

**Request:**

```
GET http://localhost:5002/quota
```

**Response:**

```json
{
    "character_count": 5000,
    "character_limit": 10000,
    "remaining": 5000
}
```

## 💰 Pricing ElevenLabs

| Tier        | Harga | Karakter/Bulan       | Cocok Untuk       |
| ----------- | ----- | -------------------- | ----------------- |
| **Free**    | $0    | 10,000 (~10 menit)   | Testing           |
| **Starter** | $5    | 30,000 (~30 menit)   | Personal          |
| **Creator** | $22   | 100,000 (~100 menit) | **Commercial** ✅ |
| **Pro**     | $99   | 500,000 (~500 menit) | High Volume       |

**Catatan:** Hanya tier **Creator** dan **Pro** yang boleh untuk komersial.

## 🆚 Perbandingan dengan Engine Lain

| Aspek               | XTTS   | GPT-SoVITS | ElevenLabs       |
| ------------------- | ------ | ---------- | ---------------- |
| **Logat Indonesia** | ⭐⭐⭐ | ⭐⭐       | ⭐⭐⭐⭐⭐       |
| **Artikulasi**      | ⭐⭐⭐ | ⭐⭐       | ⭐⭐⭐⭐⭐       |
| **Setup**           | Mudah  | Rumit      | **Sangat Mudah** |
| **Biaya**           | Gratis | Gratis     | $22-99/bulan     |
| **Kualitas**        | Bagus  | Lumayan    | **Production**   |

## 🚀 Integrasi ke Website

Update Laravel controller untuk support ElevenLabs:

```php
// VoiceChangerController.php
$engine = $request->input('engine', 'xtts');

$url = match($engine) {
    'xtts' => env('AI_XTTS_URL'),
    'gptsovits' => env('AI_GPTSOVITS_URL'),
    'elevenlabs' => env('AI_ELEVENLABS_URL'),  // http://localhost:5002
};
```

Update `.env`:

```env
AI_ELEVENLABS_URL=http://localhost:5002
```

## 📊 Monitoring Quota

Untuk monitoring quota secara real-time:

```python
import requests

response = requests.get('http://localhost:5002/quota')
quota = response.json()

print(f"Used: {quota['character_count']}")
print(f"Limit: {quota['character_limit']}")
print(f"Remaining: {quota['remaining']}")
```

## ⚠️ Catatan Penting

1. **API Key Rahasia** - Jangan commit API key ke Git
2. **Quota Limit** - Monitor quota agar tidak over limit
3. **Commercial Use** - Pastikan pakai tier Creator/Pro jika untuk bisnis
4. **Cleanup** - Voice temporary otomatis dihapus setelah generate

## 🔧 Troubleshooting

### Error: "API key not configured"

- Set environment variable `ELEVENLABS_API_KEY`
- Atau edit `app.py` line 15

### Error: "Quota exceeded"

- Upgrade tier di ElevenLabs
- Atau tunggu bulan berikutnya (reset otomatis)

### Error: "Voice cloning failed"

- Pastikan audio referensi jelas (tidak noise)
- Durasi audio minimal 5 detik
- Format audio: WAV/MP3

## 📚 Resources

- **ElevenLabs Docs**: https://docs.elevenlabs.io/
- **API Reference**: https://docs.elevenlabs.io/api-reference
- **Pricing**: https://elevenlabs.io/pricing
- **Dashboard**: https://elevenlabs.io/app

---

**Status:** 🚧 **Siap Dikembangkan** (Butuh API Key untuk aktif)
