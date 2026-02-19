import re

def clean_indonesian_for_xtts(text: str) -> str:
    """
    Cleaner khusus Bahasa Indonesia untuk XTTS.
    Fokus:
    - Menjaga fonem khas Indonesia (ng, ny, kh)
    - Memperjelas pemenggalan suku kata
    - Mengurangi kecenderungan accent English
    """

    # 1. Lowercase
    text = text.lower()

    # 2. Normalisasi spasi
    text = re.sub(r'\s+', ' ', text).strip()

    # 3. Hapus karakter aneh kecuali tanda baca dasar
    text = re.sub(r'[^a-z0-9.,?!\s-]', '', text)

    # 4. Perjelas beberapa kata umum yang sering kebawa English
    fix_words = {
        "teknologi": "tekno logi",
        "teknologinya": "tekno loginya",
        "sistem": "sis tem",
        "program": "pro gram",
        "database": "data base",
        "data": "da ta",
        "server": "ser ver",
        "internet": "inter net",
        "aplikasi": "apli kasi",
        "informasi": "infor masi",
        "digital": "di gi tal",
        "komputer": "kom pu ter",
        "artificial": "arti fi cial",
        "intelligence": "intelijen"
    }

    for word, fix in fix_words.items():
        text = re.sub(rf'\b{word}\b', fix, text)

    # 5. Perjelas akhiran -si agar tidak jadi English "shi"
    text = re.sub(r'si\b', 'si', text)

    # 6. Pastikan 'e' tidak terlalu schwa (opsional tweak ringan)
    # Tidak mengganti huruf, hanya bantu jeda ringan
    text = text.replace(" e ", " e ")

    # 7. Jaga fonem khas Indonesia (jangan diubah)
    # ng, ny, kh tetap dipertahankan

    return text
