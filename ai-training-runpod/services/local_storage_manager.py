import os
import shutil

class LocalStorageManager:
    """
    Simulasi S3 Manager tapi menggunakan Folder Lokal.
    Cocok untuk testing tanpa Cloudflare/S3.
    """
    def __init__(self, base_path=None):
        # Default ke folder storage Laravel jika tidak ditentukan
        if base_path is None:
            # Mengasumsikan folder ini ada di root project yang sama
            self.base_path = os.path.abspath(os.path.join(os.getcwd(), "..", "backend", "storage", "app", "public"))
        else:
            self.base_path = base_path
            
        print(f"🏠 [LOCAL STORAGE] Menggunakan path: {self.base_path}")

    def download_dataset(self, bucket, remote_path, local_dest):
        """Menyalin dataset dari folder 'public' Laravel ke folder kerja Training"""
        source = os.path.join(self.base_path, remote_path)
        os.makedirs(os.path.dirname(local_dest), exist_ok=True)
        
        if os.path.exists(source):
            print(f"📥 [LOCAL] Menyalin dataset: {source} -> {local_dest}")
            shutil.copy(source, local_dest)
            return True
        else:
            print(f"❌ [LOCAL] Dataset tidak ditemukan: {source}")
            return False

    def upload_model(self, local_path, bucket, remote_path):
        """Menyalin hasil training (.pth/.json) kembali ke folder 'public' Laravel"""
        destination = os.path.join(self.base_path, remote_path)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        if os.path.exists(local_path):
            print(f"📤 [LOCAL] Mengirim hasil training: {local_path} -> {destination}")
            shutil.copy(local_path, destination)
            return True
        else:
            print(f"❌ [LOCAL] File model tidak ditemukan untuk di-upload: {local_path}")
            return False
