import os
import requests
from tqdm import tqdm

def download_file(url, destination):
    if os.path.exists(destination):
        print(f"[EXISTS] {os.path.basename(destination)}")
        return
    
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

# Model OpenVoice v2 (Lite & High Quality)
models = {
    "openvoice_v2/checkpoint.pth": "https://huggingface.co/myshell-ai/OpenVoiceV2/resolve/main/checkpoints_v2/240504/checkpoint.pth",
    "openvoice_v2/config.json": "https://huggingface.co/myshell-ai/OpenVoiceV2/resolve/main/checkpoints_v2/240504/config.json",
}

base_dir = "models"

print("="*60)
print("OpenVoice v2 Model Downloader")
print("="*60)

for path, url in models.items():
    download_file(url, os.path.join(base_dir, path))

print("\n[SUCCESS] OpenVoice v2 Models Ready!")
