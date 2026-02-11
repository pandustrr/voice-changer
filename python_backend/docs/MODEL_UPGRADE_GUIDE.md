# Voice Changer - Model Installation Guide

## Current Status

✅ XTTS v2 (Working - Limited Indonesian support)
🔄 GPT-SoVITS (Recommended for Indonesian)

## Install GPT-SoVITS (Recommended)

### Step 1: Install Dependencies

```bash
pip install -r requirements_gptsovits.txt
```

### Step 2: Clone GPT-SoVITS Repository

```bash
cd python_backend
git clone https://github.com/RVC-Boss/GPT-SoVITS.git
cd GPT-SoVITS
```

### Step 3: Download Pre-trained Models

Download these models and place them in `GPT-SoVITS/pretrained_models/`:

1. **GPT Model** (Chinese/Multi-language base):
    - https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s1bert25.pth
    - https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s2G488k.pth
    - https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/s2D488k.pth

2. **BERT Models**:
    - https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-roberta-wwm-ext-large/pytorch_model.bin
    - Place in: `GPT-SoVITS/pretrained_models/chinese-roberta-wwm-ext-large/`

### Step 4: Test Installation

```bash
python test_gptsovits.py
```

## Alternative: Use OpenVoice v2

If GPT-SoVITS is too complex, we can use OpenVoice v2:

```bash
pip install git+https://github.com/myshell-ai/OpenVoice.git
```

OpenVoice advantages:

- ✅ Easier setup
- ✅ Better for cross-language cloning
- ✅ Faster inference
- ⚠️ Slightly lower quality than GPT-SoVITS

## Recommendation

For SaaS product with Indonesian focus:

1. **Best Quality**: GPT-SoVITS (setup time: 20 mins)
2. **Best Balance**: OpenVoice v2 (setup time: 5 mins)
3. **Current**: XTTS v2 (already working, limited ID support)

Choose based on your priority: Quality vs Setup Time
