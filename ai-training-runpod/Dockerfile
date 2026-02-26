# GUNAKAN IMAGE CUDA UNTUK RTX 4090
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# 1. SETUP LINGKUNGAN
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2. SETUP WORKDIR
WORKDIR /workspace/ai-training-worker

# 3. INSTALL DEPENDENCIES
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 4. COPY SEMUA KODINGAN
COPY . .

# 5. EXPOSE PORT FASTAPI (8001) DAN JELASKAN CARA JALANNYA
EXPOSE 8001

# Jalankan server
CMD ["python3", "api/server.py"]
