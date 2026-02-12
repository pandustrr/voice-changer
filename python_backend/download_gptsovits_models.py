import os
import requests
from tqdm import tqdm

def download_file(url, destination):
    print(f"[DOWNLOADING] {os.path.basename(destination)}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        with open(destination, 'wb') as file, tqdm(
            desc=os.path.basename(destination),
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=8192):
                size = file.write(data)
                bar.update(size)
    except Exception as e:
        print(f"[ERROR] Gagal download {url}: {e}")

# Folder penyimpanan model
base_dir = "GPT-SoVITS/GPT_SoVITS/pretrained_models"

models = {
    # BERT
    "chinese-roberta-wwm-ext-large/pytorch_model.bin": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-roberta-wwm-ext-large/pytorch_model.bin",
    "chinese-roberta-wwm-ext-large/config.json": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-roberta-wwm-ext-large/config.json",
    "chinese-roberta-wwm-ext-large/tokenizer.json": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-roberta-wwm-ext-large/tokenizer.json",
    
    # Hubert (Ini yang tadi kurang file preprocessor)
    "chinese-hubert-base/pytorch_model.bin": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-hubert-base/pytorch_model.bin",
    "chinese-hubert-base/config.json": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-hubert-base/config.json",
    "chinese-hubert-base/preprocessor_config.json": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-hubert-base/preprocessor_config.json",
    
    # Model Weights (V2)
    "gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt",
    "gsv-v2final-pretrained/s2G2333k.pth": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/gsv-v2final-pretrained/s2G2333k.pth",
}

print("="*60)
print("GPT-SoVITS Model Auto-Installer (Fixing Missing Files)")
print("="*60)

for path, url in models.items():
    full_path = os.path.join(base_dir, path)
    if not os.path.exists(full_path):
        download_file(url, full_path)
    else:
        print(f"[OK] {path} sudah ada.")

print("\n[FINISH] Semua model sudah lengkap!")
