import re

def clean_for_xtts(text):
    """
    Menyiapkan teks Indonesia agar dibaca dengan logat murni oleh XTTS.
    """
    text = text.lower()
    
    # 1. Normalisasi Angka Indonesia
    angka = {
        '0': 'nol', '1': 'satu', '2': 'dua', '3': 'tiga', '4': 'empat',
        '5': 'lima', '6': 'enam', '7': 'tujuh', '8': 'delapan', '9': 'sembilan'
    }
    for n, w in angka.items():
        text = text.replace(n, ' ' + w + ' ')

    # 2. Perbaiki fonetik agar vokal Indonesia (A-I-U-E-O) terdengar tajam
    # Trik: Kita arahkan ke pelafalan Spanyol ('es') karena vokal Spanyol 99% mirip Indonesia.
    # Spanyol jauh lebih stabil daripada Hindi di sistem Windows.
    text = text.replace('ny', 'ny')
    text = text.replace('ng', 'ng')
    text = text.replace('sy', 'sh')
    
    # Singkatan
    abbr = {'yg': 'yang', 'utk': 'untuk', 'dgn': 'dengan', 'sdh': 'sudah', 'gk': 'tidak'}
    for a, f in abbr.items():
        text = re.sub(rf'\b{a}\b', f, text)

    return text.strip()
