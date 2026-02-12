# Setup ElevenLabs - Panduan Lengkap

## ✅ Yang Sudah Dikonfigurasi:

1. ✅ Folder `elevenlabs_bridge` sudah dibuat
2. ✅ Laravel `.env` sudah ditambahkan `AI_ELEVENLABS_URL`
3. ✅ Controller sudah support engine `elevenlabs`
4. ✅ Validation sudah update

---

## 🔑 Langkah Selanjutnya (Yang Perlu Anda Lakukan):

### **Step 1: Daftar ElevenLabs & Dapatkan API Key**

1. Buka: https://elevenlabs.io/
2. Klik **"Sign Up"** (pojok kanan atas)
3. Daftar dengan email atau Google account
4. Setelah login, klik **profile icon** → **"Profile + API Key"**
5. Atau langsung ke: https://elevenlabs.io/app/settings/api-keys
6. **Copy API Key** Anda (contoh: `sk_abc123def456...`)

---

### **Step 2: Set API Key**

**Pilih salah satu:**

#### **Cara A: Environment Variable** (Recommended)

```powershell
# Set untuk session saat ini
$env:ELEVENLABS_API_KEY="sk_your_api_key_here"

# Atau set permanent
[System.Environment]::SetEnvironmentVariable('ELEVENLABS_API_KEY', 'sk_your_api_key_here', 'User')
```

#### **Cara B: File .env**

Buat file `.env` di `python_backend/elevenlabs_bridge/`:

```env
ELEVENLABS_API_KEY=sk_your_api_key_here
```

Lalu update `app.py` line 6-8:

```python
from dotenv import load_dotenv
load_dotenv()

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
```

---

### **Step 3: Install Dependencies**

```powershell
cd python_backend/elevenlabs_bridge
pip install -r requirements.txt
```

---

### **Step 4: Jalankan Server**

```powershell
python app.py
```

**Tunggu hingga muncul:**

```
============================================================
ElevenLabs Voice Cloning Bridge
============================================================
API Key Status: ✅ Configured
Port: 5002
Endpoint: http://localhost:5002/clone
============================================================
 * Running on http://127.0.0.1:5002
```

---

### **Step 5: Test dari Website**

Karena UI belum ada selector engine, Anda bisa test dengan 2 cara:

#### **Cara A: Ubah Default Engine di Controller**

Edit `VoiceChangerController.php` line 31:

```php
// Sebelum:
$enginePreference = $request->input('engine', 'xtts');

// Sesudah (untuk test ElevenLabs):
$enginePreference = $request->input('engine', 'elevenlabs');
```

Lalu test dari website seperti biasa.

#### **Cara B: Test Langsung dengan cURL**

```powershell
curl -X POST http://localhost:5002/clone `
  -F "audio=@path/to/your/audio.wav" `
  -F "text=Halo, ini adalah test voice cloning dengan ElevenLabs" `
  -F "speed=1.0" `
  -o output.mp3
```

---

### **Step 6: Cek Quota**

```powershell
curl http://localhost:5002/quota
```

**Response:**

```json
{
    "character_count": 1500,
    "character_limit": 10000,
    "remaining": 8500
}
```

---

## 🎨 (Opsional) Tambah UI Selector Engine

Jika Anda ingin menambahkan selector di UI, tambahkan di `welcome.blade.php` setelah "Reference Text":

```html
<!-- Engine Selector -->
<div class="space-y-2">
    <label class="text-xs uppercase tracking-widest text-gray-500 font-bold">
        AI Engine
    </label>
    <select
        id="engineSelect"
        class="w-full bg-black/40 border border-yellow-500/30 rounded-xl p-3 text-white text-sm focus:outline-none focus:ring-2 focus:ring-yellow-500/50"
    >
        <option value="xtts">XTTS v2 (Free, Fast)</option>
        <option value="gptsovits">GPT-SoVITS (Free, Experimental)</option>
        <option value="elevenlabs">ElevenLabs (Premium, Best Quality)</option>
    </select>
    <p class="text-xs text-gray-600 italic">
        💡 ElevenLabs provides production-grade quality
    </p>
</div>
```

Lalu di JavaScript, tambahkan ke FormData:

```javascript
formData.append("engine", document.getElementById("engineSelect").value);
```

---

## 💰 Pricing ElevenLabs

| Tier        | Harga | Karakter/Bulan       | Cocok Untuk       |
| ----------- | ----- | -------------------- | ----------------- |
| **Free**    | $0    | 10,000 (~10 menit)   | Testing           |
| **Starter** | $5    | 30,000 (~30 menit)   | Personal          |
| **Creator** | $22   | 100,000 (~100 menit) | **Commercial** ✅ |
| **Pro**     | $99   | 500,000 (~500 menit) | High Volume       |

**Catatan:** Hanya tier **Creator** dan **Pro** yang boleh untuk komersial.

---

## 🎯 Perbandingan Engine

| Aspek               | XTTS     | GPT-SoVITS | **ElevenLabs**   |
| ------------------- | -------- | ---------- | ---------------- |
| **Logat Indonesia** | ⭐⭐⭐   | ⭐⭐       | ⭐⭐⭐⭐⭐       |
| **Artikulasi**      | ⭐⭐⭐   | ⭐⭐       | ⭐⭐⭐⭐⭐       |
| **Kemiripan Suara** | ⭐⭐⭐⭐ | ⭐⭐⭐     | ⭐⭐⭐⭐⭐       |
| **Setup**           | Mudah    | Rumit      | **Sangat Mudah** |
| **Biaya**           | Gratis   | Gratis     | $22-99/bulan     |
| **Kecepatan**       | Cepat    | Lambat     | **Sangat Cepat** |

---

## 🔧 Troubleshooting

### Error: "API key not configured"

- Pastikan API key sudah di-set di environment variable
- Atau buat file `.env` di folder `elevenlabs_bridge`

### Error: "Quota exceeded"

- Cek quota: `curl http://localhost:5002/quota`
- Upgrade tier di ElevenLabs
- Atau tunggu bulan berikutnya (reset otomatis)

### Error: "Voice cloning failed"

- Pastikan audio referensi jelas (tidak noise)
- Durasi audio minimal 5 detik
- Format audio: WAV/MP3

---

## 📊 Status Implementasi

- ✅ Backend server (Port 5002)
- ✅ Laravel integration
- ✅ Controller support
- ✅ .env configuration
- ⚠️ UI selector (opsional, bisa ditambahkan)
- 🔑 **Butuh API Key** untuk aktif

---

**Setelah dapat API key, langsung bisa dipakai!** 🚀
