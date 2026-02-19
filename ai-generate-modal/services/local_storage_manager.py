import os
import shutil

class LocalStorageManager:
    """
    Simulasi S3 Manager untuk Inference (Modal Local).
    Mengambil model dari folder 'public' Laravel.
    """
    def __init__(self, base_path=None):
        if base_path is None:
            self.base_path = os.path.abspath(os.path.join(os.getcwd(), "..", "backend", "storage", "app", "public"))
        else:
            self.base_path = base_path
            
        print(f"🏠 [LOCAL STORAGE] Menggunakan path: {self.base_path}")

    def download_model(self, bucket, remote_path, local_dest):
        """Mengambil model suara (.pth) dari folder Laravel ke cache lokal AI"""
        source = os.path.join(self.base_path, remote_path)
        os.makedirs(os.path.dirname(local_dest), exist_ok=True)
        
        if os.path.exists(source):
            print(f"📥 [LOCAL] Mengambil model: {source} -> {local_dest}")
            shutil.copy(source, local_dest)
            return True
        else:
            print(f"❌ [LOCAL] Model tidak ditemukan di storage: {source}")
            return False
