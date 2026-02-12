"""
Indonesian G2P for GPT-SoVITS - Simplified Version
Minimal processing untuk hasil yang akurat
"""

import re

def text_normalize(text):
    """Normalisasi teks minimal"""
    # Lowercase
    text = text.lower()
    
    # Hapus karakter yang tidak perlu
    text = re.sub(r'[^\w\s.,!?]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def g2p(text):
    """
    Simple Indonesian G2P
    Kembalikan teks yang sudah dinormalisasi sebagai list karakter
    """
    text = text_normalize(text)
    
    # Split menjadi karakter individual
    phones = []
    for char in text:
        if char == ' ':
            phones.append('_')  # Word separator
        else:
            phones.append(char)
    
    # Pastikan minimal 4 karakter
    if len(phones) < 4:
        phones = [','] + phones
    
    return phones

if __name__ == "__main__":
    test = "Halo nama saya Pandu"
    print(f"Input: {test}")
    print(f"Output: {g2p(test)}")
