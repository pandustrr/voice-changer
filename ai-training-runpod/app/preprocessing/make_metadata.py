import os
import speech_recognition as sr

def transcribe_with_google():
    """
    Auto transcribe audio files menggunakan Google Speech Recognition.
    
    Input: wavs/ (segmen audio hasil split)
    Output: metadata.csv (mapping audio -> teks)
    """
    wavs_dir = "wavs"
    metadata_path = "metadata.csv"
    
    if not os.path.exists(wavs_dir):
        print(f"❌ ERROR: Folder '{wavs_dir}' tidak ditemukan!")
        print("\nJalankan dulu: python split_audio.py")
        return

    print("=" * 60)
    print("AUTO TRANSCRIBE DENGAN GOOGLE SPEECH RECOGNITION")
    print("=" * 60)
    print(f"Input folder: {wavs_dir}/")
    print(f"Output file: {metadata_path}")
    print()
    print("⚠️  CATATAN:")
    print("   - Hasil auto transcribe PASTI ada error")
    print("   - HARUS review manual setelah selesai")
    print("   - Akurasi ~70-80%")
    print()
    
    r = sr.Recognizer()
    
    files = [f for f in os.listdir(wavs_dir) if f.endswith(".wav")]
    files.sort()
    
    if not files:
        print(f"❌ Folder '{wavs_dir}' kosong!")
        return
    
    print(f"📊 Ditemukan {len(files)} file audio")
    print("🎤 Mulai transcribe...\n")
    
    results = []
    success_count = 0
    error_count = 0
    
    for i, filename in enumerate(files):
        path = os.path.join(wavs_dir, filename)
        print(f"[{i+1}/{len(files)}] {filename}... ", end="", flush=True)
        
        try:
            with sr.AudioFile(path) as source:
                audio = r.record(source)
                # Gunakan Google Recognition (Indonesia)
                text = r.recognize_google(audio, language="id-ID")
                
                # Bersihkan teks
                text = text.replace("|", "")
                # ID untuk LJSpeech format adalah nama file TANPA .wav
                file_id = os.path.splitext(filename)[0]
                
                # Format LJSpeech butuh 3 kolom: ID|teks|teks_normal
                results.append(f"{file_id}|{text}|{text}")
                success_count += 1
                print(f"✓ {text[:50]}...")
        except sr.UnknownValueError:
            file_id = os.path.splitext(filename)[0]
            results.append(f"{file_id}|[TIDAK_TERDETEKSI]|[TIDAK_TERDETEKSI]")
            error_count += 1
            print("✗ Tidak terdeteksi")
        except Exception as e:
            file_id = os.path.splitext(filename)[0]
            results.append(f"{file_id}|[ERROR]|[ERROR]")
            error_count += 1
            print(f"✗ Error: {e}")

    # Tulis ke metadata.csv
    with open(metadata_path, "w", encoding="utf-8") as f:
        for line in results:
            f.write(line + "\n")
            
    print()
    print("=" * 60)
    print("✅ SELESAI!")
    print(f"   Total file: {len(files)}")
    print(f"   Berhasil: {success_count}")
    print(f"   Error: {error_count}")
    print(f"   File output: {metadata_path}")
    print()
    print("⚠️  PENTING:")
    print("   1. Buka metadata.csv")
    print("   2. Review SEMUA transkrip")
    print("   3. Perbaiki yang salah/error")
    print("   4. Pastikan 100% akurat sebelum training")
    print("=" * 60)

if __name__ == "__main__":
    transcribe_with_google()
