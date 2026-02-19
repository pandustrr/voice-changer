import os
import boto3
from dotenv import load_dotenv

# Load .env dari folder backend (naik satu level karena script di dalam folder scripts/)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

# Konfigurasi R2
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
ENDPOINT = os.getenv("AWS_ENDPOINT")
BUCKET = "suara-cloning"

if not ACCESS_KEY or not SECRET_KEY:
    print("❌ Error: Credentials R2 tidak ditemukan di .env")
    exit(1)

# Inisialisasi S3 Client (R2)
s3 = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    endpoint_url=ENDPOINT,
    region_name='auto'
)

DATASET_DIR = r"e:\Pandu-Projek\Freelance\Voice-Changer\backend\storage\app\public\dataset_training"

def upload_folder(local_folder):
    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            # Buat path remote (hapus bagian base path lokal)
            relative_path = os.path.relpath(local_path, DATASET_DIR)
            remote_path = f"datasets/my_voice/{relative_path.replace(os.path.sep, '/')}"
            
            print(f"📤 Uploading: {file} -> {remote_path}")
            s3.upload_file(local_path, BUCKET, remote_path)

print(f"🚀 Memulai upload dataset ke Cloudflare R2 (Bucket: {BUCKET})...")
try:
    upload_folder(DATASET_DIR)
    print("\n✅ Dataset berhasil di-upload ke Cloudflare R2!")
    print(f"🔗 Lokasi: {BUCKET}/datasets/my_voice/")
except Exception as e:
    print(f"❌ Error: {str(e)}")
