import os
import requests
from tqdm import tqdm

def download_file(url, destination):
    print(f"[DOWNLOADING] {os.path.basename(destination)}")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    
    with open(destination, 'wb') as file, tqdm(
        desc=os.path.basename(destination),
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

# List model GPT-SoVITS yang wajib ada
models = {
    "chinese-roberta-wwm-ext-large/pytorch_model.bin": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-roberta-wwm-ext-large/pytorch_model.bin",
    "chinese-roberta-wwm-ext-large/config.json": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-roberta-wwm-ext-large/config.json",
    "chinese-roberta-wwm-ext-large/tokenizer.json": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-roberta-wwm-ext-large/tokenizer.json",
    "s2G488k.pth": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s2G488k.pth",
    "s2D488k.pth": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s2D488k.pth",
    "gsv-v2final-pretrained/s1v2.ckpt": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/gsv-v2final-pretrained/s1v2.ckpt",
    "gsv-v2final-pretrained/s2G488k.pth": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/gsv-v2final-pretrained/s2G488k.pth",
    "gsv-v2final-pretrained/s2D488k.pth": "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/gsv-v2final-pretrained/s2D488k.pth",
}

base_dir = "GPT-SoVITS/pretrained_models"

print("="*60)
print("GPT-SoVITS Offline Model Downloader (v2)")
print("="*60)

for path, url in models.items():
    full_path = os.path.join(base_dir, path)
    if not os.path.exists(full_path):
        try:
            download_file(url, full_path)
        except Exception as e:
            print(f"[ERROR] Failed to download {path}: {e}")
    else:
        print(f"[EXISTS] {path} already downloaded.")

print("\n[SUCCESS] Semua model GPT-SoVITS sudah siap!")
