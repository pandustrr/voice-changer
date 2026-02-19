"""
Analisis Struktur Public Speaking
Deteksi Opening, Content, Closing dari transkrip lengkap
dengan scoring otomatis untuk penilaian
"""

# import os
# os.environ['WANDB_DISABLED'] = 'true'

import pandas as pd
import torch
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import List, Dict, Tuple

# ============ 1. SENTENCE SPLITTER ============

def split_into_sentences(text: str) -> List[str]:
    """Split text menjadi kalimat-kalimat"""
    # Split berdasarkan tanda baca
    sentences = re.split(r'[.!?,;\n]+', text)
    # Bersihkan whitespace dan filter kalimat kosong
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

# ============ 2. BATCH PREDICTION ============

def predict_sentences(sentences: List[str], model_path='./best_model',
                      confidence_threshold: float = 0.7) -> List[Dict]:
    """Prediksi label untuk list kalimat"""

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.eval()

    label_map = {0: 'opening', 1: 'content', 2: 'closing'}
    results = []

    for idx, sentence in enumerate(sentences):
        inputs = tokenizer(
            sentence,
            add_special_tokens=True,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            predicted_class = torch.argmax(probs, dim=-1).item()
            confidence = probs[0][predicted_class].item()

        predicted_label = label_map[predicted_class]

        # 🔁 Jika opening / closing tapi confidence rendah → ubah jadi content
        if predicted_label in ['opening', 'closing'] and confidence < confidence_threshold:
            predicted_label = 'content'

        results.append({
            'sentence_idx': idx,
            'text': sentence,
            'predicted_label': predicted_label,
            'confidence': confidence,
            'probs': {
                'opening': probs[0][0].item(),
                'content': probs[0][1].item(),
                'closing': probs[0][2].item()
            }
        })

    return results


# ============ 3. POST-PROCESSING & HEURISTICS ============

def apply_structure_rules(predictions: List[Dict]) -> List[Dict]:
    """
    Terapkan rules untuk memperbaiki struktur:
    - Opening di awal
    - Closing di akhir
    - Content di tengah
    """

    if not predictions:
        return predictions

    n = len(predictions)

    # Rule 1: 2 kalimat pertama cenderung opening (jika confidence tinggi)
    for i in range(min(2, n)):
        if predictions[i]['probs']['opening'] > 0.8:  # Threshold
            predictions[i]['predicted_label'] = 'opening'
            predictions[i]['adjusted'] = True

    # Rule 2: 2 kalimat terakhir cenderung closing (jika confidence tinggi)
    for i in range(max(0, n-2), n):
        if predictions[i]['probs']['closing'] > 0.8:  # Threshold
            predictions[i]['predicted_label'] = 'closing'
            predictions[i]['adjusted'] = True

    # Rule 3: Detect transisi berdasarkan keyword
    closing_keywords = ['demikian', 'terima kasih', 'sekian', 'akhir kata',
                       'wassalam', 'selamat pagi dan', 'sampai jumpa']
    opening_keywords = ['selamat pagi', 'selamat siang', 'assalamualaikum',
                       'hadirin', 'pertama-tama', 'izinkan saya']

    for pred in predictions:
        text_lower = pred['text'].lower()

        # Check closing keywords
        if any(kw in text_lower for kw in closing_keywords):
            pred['predicted_label'] = 'closing'
            pred['keyword_match'] = True

        # Check opening keywords
        elif any(kw in text_lower for kw in opening_keywords):
            pred['predicted_label'] = 'opening'
            pred['keyword_match'] = True

    return predictions

# ============ 4. STRUCTURE SEGMENTATION ============

def segment_speech_structure(predictions: List[Dict]) -> Dict:
    """
    Grouping kalimat berdasarkan struktur yang terdeteksi
    """

    structure = {
        'opening': [],
        'content': [],
        'closing': []
    }

    for pred in predictions:
        label = pred['predicted_label']
        structure[label].append(pred)

    return structure

# ============ 5. SCORING SYSTEM ============

def calculate_structure_score(structure: Dict) -> Dict:
    """
    Hitung skor berdasarkan kriteria:
    - Poin 5: ada opening (1), content (1), closing (1)
    - Poin 4: ada opening (1), content (1), closing (0)
    - Poin 3: ada opening (1), content (0), closing (1)
    - Poin 2: ada opening (0), content (1), closing (1)
    - Poin 1: ada opening (1), content (0), closing (0)
    - Poin 0: tidak ada struktur yang lengkap
    """

    has_opening = len(structure['opening']) > 0
    has_content = len(structure['content']) > 0
    has_closing = len(structure['closing']) > 0

    # Hitung poin
    if has_opening and has_content and has_closing:
        score = 5
        description = "Sempurna! Struktur lengkap terdapat (Pembuka, Isi, Penutup)"
    elif has_opening and has_content and not has_closing:
        score = 4
        description = "Baik. Ada pembuka dan isi, tapi kurang penutup"
    elif has_opening and not has_content and has_closing:
        score = 3
        description = "Cukup. Ada pembuka dan penutup, tapi isi kurang jelas"
    elif not has_opening and has_content and has_closing:
        score = 2
        description = "Perlu perbaikan. Kurang pembuka yang jelas"
    elif has_opening and not has_content and not has_closing:
        score = 1
        description = "Kurang lengkap. Hanya ada pembuka"
    else:
        score = 0
        description = "Struktur tidak terdeteksi dengan baik"

    return {
        'score': score,
        'max_score': 5,
        'description': description,
        'has_opening': has_opening,
        'has_content': has_content,
        'has_closing': has_closing,
        'opening_count': len(structure['opening']),
        'content_count': len(structure['content']),
        'closing_count': len(structure['closing'])
    }

# ============ 6. MAIN ANALYSIS FUNCTION ============

def analyze_speech(transcript: str, model_path='./best_model',
                   apply_rules=True, verbose=True) -> Dict:
    """
    Fungsi utama untuk menganalisis struktur speech

    Args:
        transcript: Teks lengkap dari speech
        model_path: Path ke model yang sudah di-train
        apply_rules: Apakah menggunakan heuristic rules
        verbose: Tampilkan detail atau tidak

    Returns:
        Dict berisi hasil analisis lengkap
    """

    # 1. Split into sentences
    sentences = split_into_sentences(transcript)

    if verbose:
        print(f"📝 Jumlah kalimat terdeteksi: {len(sentences)}")

    # 2. Predict each sentence
    predictions = predict_sentences(sentences, model_path)

    # 3. Apply rules (optional)
    if apply_rules:
        predictions = apply_structure_rules(predictions)

    # 4. Segment structure
    structure = segment_speech_structure(predictions)

    # 5. Calculate score
    score_result = calculate_structure_score(structure)

    # 6. Generate report
    if verbose:
        print("\n" + "="*70)
        print("📊 HASIL ANALISIS STRUKTUR BERBICARA")
        print("="*70)

        print(f"\n🎯 SKOR: {score_result['score']}/{score_result['max_score']}")
        print(f"📝 {score_result['description']}")

        print(f"\n✅ Struktur terdeteksi:")
        print(f"   • Pembuka (Opening): {score_result['opening_count']} kalimat")
        print(f"   • Isi (Content): {score_result['content_count']} kalimat")
        print(f"   • Penutup (Closing): {score_result['closing_count']} kalimat")

        print(f"\n📄 Detail per bagian:")
        print(f"\n{'='*70}")

        for section in ['opening', 'content', 'closing']:
            if structure[section]:
                print(f"\n🔹 {section.upper()}:")
                for item in structure[section]:
                    print(f"   [{item['sentence_idx']+1}] {item['text'][:80]}...")
                    print(f"       Confidence: {item['confidence']:.2%}")

        print(f"\n{'='*70}")

    return {
        'sentences': sentences,
        'predictions': predictions,
        'structure': structure,
        'score': score_result,
        'transcript': transcript
    }


# ============ 8. CONTOH PENGGUNAAN ============

if __name__ == "__main__":

    # Contoh transkrip speech
    sample_transcript = """
    Assalamualaikum warahmatullahi wabarakatuh. Selamat pagi hadirin yang saya hormati
    Puji syukur kita panjatkan kehadirat Tuhan Yang Maha Esa

    Pada kesempatan ini saya akan membahas tentang pentingnya pendidikan karakter
    Menurut data dari Kemendikbud tahun 2023, tingkat literasi di Indonesia masih perlu ditingkatkan
    Berdasarkan penelitian menunjukkan bahwa pendidikan karakter sangat penting untuk generasi muda
    Contohnya seperti yang terjadi di negara-negara maju, mereka mengutamakan pendidikan karakter sejak dini

    Oleh karena itu kita perlu bergerak bersama untuk meningkatkan kualitas pendidikan
    Demikian yang dapat saya sampaikan
    Terima kasih atas perhatian Bapak dan Ibu sekalian
    Wassalamualaikum warahmatullahi wabarakatuh
    """

    print("🎤 ANALISIS STRUKTUR PUBLIC SPEAKING")
    print("="*70)

    # Jalankan analisis
    result = analyze_speech(
        transcript=sample_transcript,
        model_path='./best_model',
        apply_rules=True,
        verbose=True
    )