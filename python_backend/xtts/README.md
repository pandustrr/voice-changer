# XTTS Engine for Voice-Changer

Folder ini berisi sistem khusus untuk **XTTS v2** agar mendukung Bahasa Indonesia dengan logat murni.

## Struktur File

- `app.py`: Server utama (Flask) yang berjalan di port **5000**.
- `indo_cleaner.py`: Modul pembersih teks khusus Indonesia (Angka, Singkatan, Fonetik).
- `xtts_cleaner.py`: Modul pembersihan tambahan untuk optimasi XTTS.
- `check_languages.py`: Script untuk mengecek bahasa apa saja yang didukung XTTS lokal Anda.

## Cara Menjalankan

1. Buka terminal di folder ini (`python_backend/xtts`).
2. Jalankan perintah:
    ```powershell
    python app.py
    ```

## Fitur Unggulan

- **Pure Indonesian Accent**: Menggunakan jembatan fonetik Spanyol (`es`) agar vokal (A-I-U-E-O) terdengar murni Indonesia, bukan logat bule.
- **Auto-Slicing**: Anda bisa upload rekaman durasi lama. Sistem akan otomatis mengambil potongan 10 detik terbaik untuk cloning.
- **Speed Control**: Mendukung parameter kecepatan dari UI.
