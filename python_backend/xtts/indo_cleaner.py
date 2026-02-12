import re

def clean_indonesian_for_xtts(text):
    """
    Pemroses teks khusus Indonesia untuk XTTS v2.
    Menghilangkan aksen 'bule' dengan normalisasi fonetik agresif.
    """
    text = text.lower()
    
    # 1. Normalisasi Angka
    numbers = {
        '0': 'nol', '1': 'satu', '2': 'dua', '3': 'tiga', '4': 'empat',
        '5': 'lima', '6': 'enam', '7': 'tujuh', '8': 'delapan', '9': 'sembilan'
    }
    for num, word in numbers.items():
        text = text.replace(num, ' ' + word + ' ')

    # 2. PERBAIKAN FONETIK INDONESIA
    # Ganti huruf yang sering salah dibaca dengan ejaan fonetik yang benar
    
    # C → CH (cinta = chinta, agar tidak dibaca "kinta")
    text = re.sub(r'\bc', 'ch', text)  # c di awal kata
    text = re.sub(r'c', 'ch', text)     # c di tengah/akhir kata
    
    # E → EH (agar tidak jadi schwa ə)
    text = text.replace(' e ', ' eh ')
    
    # Konsonan ganda Indonesia
    text = text.replace('ng', 'ng')  # tetap ng
    text = text.replace('ny', 'ny')  # tetap ny
    
    # 3. Handle abbreviations
    abbreviations = {
        'yg': 'yang', 'utk': 'untuk', 'dgn': 'dengan', 
        'sdh': 'sudah', 'tks': 'terima kasih', 'gk': 'tidak',
        'tdk': 'tidak', 'dll': 'dan lain lain', 'dsb': 'dan sebagainya'
    }
    for abbr, full in abbreviations.items():
        text = re.sub(rf'\b{abbr}\b', full, text)

    # 4. Bersihkan karakter sisa
    text = re.sub(r'[^a-z.?!, ]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
