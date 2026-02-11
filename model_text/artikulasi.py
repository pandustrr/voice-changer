#!/usr/bin/env python3
"""
PRACTICAL PRONUNCIATION ASSESSMENT v2.2 - ARTICULATION ONLY
FOKUS PADA ARTIKULASI - MENERIMA TRANSCRIPT SEBAGAI VARIABEL

Author: AI Assistant
Date: 2025-11-05
"""

import torch
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re
import warnings
from difflib import SequenceMatcher
warnings.filterwarnings('ignore')


# ==================== DATA STRUCTURES ====================

@dataclass
class WordScore:
    """Score untuk satu kata"""
    index: int
    expected: str
    detected: str
    is_correct: bool
    similarity: float  # 0-1
    timestamp: Optional[float] = None
    confidence: Optional[float] = None
    is_filler: bool = False
    is_repetition: bool = False
    match_type: str = "match"  # "match", "substitution", "insertion", "deletion"


@dataclass
class PronunciationResult:
    """Hasil assessment"""
    reference_text: str
    transcribed_text: str
    word_scores: List[WordScore]

    # Metrics
    total_words: int
    correct_words: int
    accuracy_percentage: float

    # Scoring
    points: int
    category: str

    # Details
    filler_words_detected: List[str]
    repetitions_detected: List[Tuple[str, int]]
    unclear_words: List[str]

    # Feedback
    detailed_feedback: List[str]
    processing_time: float


# ==================== KATA PENGISI DETECTOR ====================

class FillerWordsDetector:
    """
    Deteksi kata pengisi dalam Bahasa Indonesia
    TIDAK difilter, tapi dicatat untuk analisis
    """

    FILLER_WORDS = {
        # Hesitation sounds
        'um', 'umm', 'ummm', 'em', 'emm', 'emmm',
        'eh', 'ehh', 'ehhh', 'ehm', 'ehmm', 'ehmmm',
        'ah', 'ahh', 'ahhh', 'ahm', 'ahmm', 'ahmmm',
        'hmm', 'hmmm', 'hmmmm',
        'uh', 'uhh', 'uhhh', 'uhm', 'uhmm',

        # Common fillers
        'anu', 'ano', 'gitu', 'gituloh', 'gitu loh',
        'kayak', 'kayaknya', 'kayak gini', 'kayak gitu',
        'apa', 'apa ya', 'apa namanya',
        'maksudnya', 'maksud saya', 'jadi', 'jadinya',
        'nah', 'terus', 'lalu', 'kemudian',
        'gini', 'begini', 'begitu',
        'semacam', 'semisal', 'ibaratnya',
        'ya kan', 'kan', 'ya', 'yah',
        'sepertinya', 'mungkin',

        # Regional variations
        'toh', 'sih', 'deh', 'dong', 'lah',
    }

    @classmethod
    def is_filler(cls, word: str) -> bool:
        """Check if word is a filler"""
        import string

        # Clean the word
        word_clean = word.lower().strip()

        # Remove trailing punctuation
        word_clean = word_clean.rstrip(string.punctuation)

        # Exact match
        if word_clean in cls.FILLER_WORDS:
            return True

        # Partial match for hesitations
        if re.match(r'^(um+|em+|eh+m*|ah+m*|uh+m*|hmm+)$', word_clean):
            return True

        return False

    @classmethod
    def count_fillers(cls, text: str) -> Tuple[int, List[str]]:
        """Count filler words in text"""
        words = text.lower().split()
        fillers = [w for w in words if cls.is_filler(w)]
        return len(fillers), fillers


# ==================== SEQUENCE ALIGNMENT ====================

class SequenceAligner:
    """
    Proper sequence alignment untuk word matching
    Menggunakan Needleman-Wunsch algorithm (dynamic programming)
    """

    @staticmethod
    def calculate_similarity(word1: str, word2: str) -> float:
        """Calculate similarity between two words"""
        return SequenceMatcher(None, word1.lower(), word2.lower()).ratio()

    @staticmethod
    def align_sequences(
        reference: List[str],
        detected: List[str],
        match_threshold: float = 0.7
    ) -> List[Tuple[Optional[str], Optional[str], str]]:
        """
        Align two sequences dengan dynamic programming

        Returns:
            List of (ref_word, det_word, match_type)
            match_type: "match", "substitution", "insertion", "deletion"
        """
        m, n = len(reference), len(detected)

        # Initialize DP table
        # dp[i][j] = (score, traceback)
        dp = [[None for _ in range(n + 1)] for _ in range(m + 1)]

        # Scoring
        MATCH_SCORE = 2
        MISMATCH_PENALTY = -1
        GAP_PENALTY = -1

        # Initialize first row and column
        for i in range(m + 1):
            dp[i][0] = (i * GAP_PENALTY, 'up')
        for j in range(n + 1):
            dp[0][j] = (j * GAP_PENALTY, 'left')
        dp[0][0] = (0, 'done')

        # Fill DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                ref_word = reference[i-1]
                det_word = detected[j-1]

                # Calculate similarity
                similarity = SequenceAligner.calculate_similarity(ref_word, det_word)

                # Match/mismatch score
                if similarity >= match_threshold:
                    match_score = MATCH_SCORE
                else:
                    match_score = MISMATCH_PENALTY

                # Three possible moves
                diagonal = dp[i-1][j-1][0] + match_score
                up = dp[i-1][j][0] + GAP_PENALTY  # deletion
                left = dp[i][j-1][0] + GAP_PENALTY  # insertion

                # Choose best move
                max_score = max(diagonal, up, left)

                if max_score == diagonal:
                    dp[i][j] = (max_score, 'diagonal')
                elif max_score == up:
                    dp[i][j] = (max_score, 'up')
                else:
                    dp[i][j] = (max_score, 'left')

        # Traceback to get alignment
        alignment = []
        i, j = m, n

        while i > 0 or j > 0:
            if dp[i][j][1] == 'diagonal':
                ref_word = reference[i-1]
                det_word = detected[j-1]
                similarity = SequenceAligner.calculate_similarity(ref_word, det_word)

                if similarity >= match_threshold:
                    match_type = "match"
                else:
                    match_type = "substitution"

                alignment.append((ref_word, det_word, match_type))
                i -= 1
                j -= 1

            elif dp[i][j][1] == 'up':
                # Deletion (word in reference but not in detected)
                alignment.append((reference[i-1], None, "deletion"))
                i -= 1

            else:  # 'left'
                # Insertion (word in detected but not in reference)
                alignment.append((None, detected[j-1], "insertion"))
                j -= 1

        # Reverse to get correct order
        alignment.reverse()

        return alignment


# ==================== MAIN ASSESSMENT MODEL ====================

class PracticalPronunciationAssessment:
    """
    Practical pronunciation assessment v2.2 - ARTICULATION ONLY

    IMPROVEMENTS:
    - Better sequence alignment
    - Accurate word matching
    - Proper filler detection
    - MENERIMA TRANSCRIPT SEBAGAI VARIABEL
    """

    def __init__(self, language: str = "id"):
        """Initialize model"""
        print(f"🚀 Initializing Practical Pronunciation Assessment v2.2 - ARTICULATION ONLY")
        print(f"📝 Transcript akan diterima sebagai variabel")
        
        self.language = language
        self.filler_detector = FillerWordsDetector()
        self.aligner = SequenceAligner()

        print(f"✅ Ready for articulation assessment!\n")

    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        text = text.lower()
        text = re.sub(r'[,\.!?;:]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def tokenize_words(self, text: str) -> List[str]:
        """Split text into words"""
        text = self.normalize_text(text)
        words = [w for w in text.split() if w]
        return words

    def assess_pronunciation(
        self,
        transcribed_text: str,
        reference_text: str
    ) -> PronunciationResult:
        """Main assessment function - menggunakan transcript sebagai variabel"""
        import time
        start_time = time.time()

        print(f"\n{'='*70}")
        print(f"🎯 PRONUNCIATION ASSESSMENT v2.2 - ARTICULATION ONLY")
        print(f"{'='*70}")
        print(f"📄 Reference Text:")
        print(f"{'─'*70}")
        print(f"{reference_text}")
        print(f"{'─'*70}")
        print(f"📝 Transcribed Text (dari variabel):")
        print(f"{'─'*70}")
        print(f"{transcribed_text}")
        print(f"{'─'*70}\n")

        # Step 1: Langsung gunakan transcribed_text dari parameter
        print(f"✅ Using provided transcript (length: {len(transcribed_text)} characters)")

        # Step 2: Tokenize
        print(f"🔤 Tokenizing words...")
        reference_words = self.tokenize_words(reference_text)
        detected_words_raw = self.tokenize_words(transcribed_text)
        print(f"✅ Reference words: {len(reference_words)}")
        print(f"✅ Detected words: {len(detected_words_raw)}")

        word_diff = len(reference_words) - len(detected_words_raw)
        if word_diff > 0:
            print(f"⚠️  Missing {word_diff} words in transcription")
        elif word_diff < 0:
            print(f"⚠️  Extra {abs(word_diff)} words in transcription")
        else:
            print(f"✅ Word count matches!")
        print()

        # Step 3: Detect fillers BEFORE alignment
        print(f"🔍 Analyzing speech patterns...")
        filler_count, filler_list = self.filler_detector.count_fillers(transcribed_text)
        print(f"✅ Filler words detected: {filler_count}")
        if filler_list:
            unique_fillers = list(set(filler_list))[:10]
            print(f"   Words: {', '.join(unique_fillers)}")
        print()

        # Step 4: IMPROVED ALIGNMENT with sequence matching
        print(f"📊 Aligning sequences with proper matching...")
        alignment = self.aligner.align_sequences(
            reference_words,
            detected_words_raw,
            match_threshold=0.7
        )
        print(f"✅ Aligned {len(alignment)} positions\n")

        # Step 5: Convert alignment to word scores
        word_scores = []
        correct_words = 0

        for idx, (ref_word, det_word, match_type) in enumerate(alignment):
            # Check if detected word is filler
            is_filler = False
            if det_word and self.filler_detector.is_filler(det_word):
                is_filler = True

            # Determine correctness
            if match_type == "match":
                is_correct = True
                similarity = self.aligner.calculate_similarity(ref_word or "", det_word or "")
                if not is_filler:  # Don't count fillers as correct
                    correct_words += 1
            elif match_type == "insertion" and is_filler:
                # Filler insertion is not an error
                is_correct = False
                similarity = 0.0
            else:
                is_correct = False
                similarity = self.aligner.calculate_similarity(ref_word or "", det_word or "") if ref_word and det_word else 0.0

            word_score = WordScore(
                index=idx,
                expected=ref_word or "[INSERTION]",
                detected=det_word or "[DELETION]",
                is_correct=is_correct,
                similarity=similarity,
                is_filler=is_filler,
                match_type=match_type
            )

            word_scores.append(word_score)

        # Step 6: Calculate metrics
        total_words = len(reference_words)
        accuracy_percentage = (correct_words / total_words * 100) if total_words > 0 else 0

        # Determine category
        if accuracy_percentage >= 81:
            category = "Sangat Baik"
            points = 5
        elif accuracy_percentage >= 61:
            category = "Baik"
            points = 4
        elif accuracy_percentage >= 41:
            category = "Cukup"
            points = 3
        elif accuracy_percentage >= 21:
            category = "Buruk"
            points = 2
        else:
            category = "Perlu Ditingkatkan"
            points = 1

        print(f"📊 Scoring complete!")
        print(f"✅ Correct: {correct_words}/{total_words} ({accuracy_percentage:.1f}%)\n")

        # Step 7: Generate feedback
        detailed_feedback = []

        detailed_feedback.append(
            f"✅ Akurasi Kata: {correct_words}/{total_words} kata benar ({accuracy_percentage:.1f}%)"
        )

        if filler_count > 0:
            detailed_feedback.append(
                f"\n💬 Kata Pengisi: {filler_count} terdeteksi ({', '.join(list(set(filler_list))[:5])})"
            )
            detailed_feedback.append(
                f"   📝 Ini NORMAL dalam berbicara natural. Tidak mengurangi nilai."
            )

        # Count errors by type
        deletions = sum(1 for ws in word_scores if ws.match_type == "deletion")
        substitutions = sum(1 for ws in word_scores if ws.match_type == "substitution")
        insertions = sum(1 for ws in word_scores if ws.match_type == "insertion" and not ws.is_filler)

        if deletions > 0 or substitutions > 0 or insertions > 0:
            detailed_feedback.append(f"\n⚠️  Analisis Kesalahan:")
            if deletions > 0:
                detailed_feedback.append(f"   • {deletions} kata tidak terucapkan/terdeteksi")
            if substitutions > 0:
                detailed_feedback.append(f"   • {substitutions} kata salah ucap")
            if insertions > 0:
                detailed_feedback.append(f"   • {insertions} kata tambahan (bukan filler)")

        # Show some examples
        unclear = [ws for ws in word_scores if not ws.is_correct and ws.match_type == "substitution"][:10]
        if unclear:
            detailed_feedback.append(f"\n❌ Contoh Kata Yang Salah:")
            for ws in unclear:
                detailed_feedback.append(f"   • '{ws.expected}' terdeteksi sebagai '{ws.detected}' (similarity: {ws.similarity:.0%})")

        # Recommendations
        detailed_feedback.append("\n💡 Rekomendasi:")
        if accuracy_percentage < 60:
            detailed_feedback.append("   • Perlambat tempo bicara untuk kejelasan")
            detailed_feedback.append("   • Perhatikan artikulasi setiap kata")
            detailed_feedback.append("   • Latih pelafalan kata yang sering salah")
        elif accuracy_percentage < 80:
            detailed_feedback.append("   • Sudah baik! Fokus pada kata-kata tertentu yang masih kurang jelas")
            detailed_feedback.append("   • Pertahankan tempo dan intonasi")
        else:
            detailed_feedback.append("   • Sangat baik! Pertahankan kualitas bicara")
            detailed_feedback.append("   • Fokus pada kelancaran dan variasi intonasi")

        processing_time = time.time() - start_time

        # Create result
        result = PronunciationResult(
            reference_text=reference_text,
            transcribed_text=transcribed_text,
            word_scores=word_scores,
            total_words=total_words,
            correct_words=correct_words,
            accuracy_percentage=accuracy_percentage,
            points=points,
            category=category,
            filler_words_detected=filler_list,
            repetitions_detected=[],  # TODO: Implement repetition detection
            unclear_words=[ws.expected for ws in word_scores if not ws.is_correct and ws.match_type != "insertion"][:20],
            detailed_feedback=detailed_feedback,
            processing_time=processing_time
        )

        return result

    def get_simple_result(self, result: PronunciationResult) -> Dict:
        """Return simplified result for API response"""
        return {
            "accuracy_percentage": round(result.accuracy_percentage, 1),
            "category": result.category,
            "points": result.points,
            "correct_words": result.correct_words,
            "total_words": result.total_words,
            "filler_count": len(result.filler_words_detected),
            "unclear_words": result.unclear_words[:10],  # Top 10 unclear words
            "processing_time": round(result.processing_time, 2)
        }

    def print_detailed_report(self, result: PronunciationResult):
        """Print detailed report"""
        print(f"\n{'='*70}")
        print(f"📊 DETAILED PRONUNCIATION REPORT")
        print(f"{'='*70}\n")

        # Overall
        print(f"🎯 OVERALL ASSESSMENT")
        print(f"{'─'*70}")
        print(f"Score:      {result.accuracy_percentage:.1f}%")
        print(f"Category:   {result.category}")
        print(f"Points:     {result.points}/5")
        print(f"Words:      {result.correct_words}/{result.total_words} correct")
        print(f"Time:       {result.processing_time:.2f}s\n")

        # Word-level details
        print(f"📝 WORD-BY-WORD ANALYSIS (First 30 words)")
        print(f"{'─'*70}")
        print(f"{'No':<4} {'Expected':<20} {'Detected':<20} {'Status':<15}")
        print(f"{'─'*70}")

        for i, ws in enumerate(result.word_scores[:30], 1):
            if ws.is_filler:
                status = "💬 Filler"
            elif ws.match_type == "match":
                status = "✅ Correct"
            elif ws.match_type == "deletion":
                status = "❌ Not spoken"
            elif ws.match_type == "insertion":
                status = "➕ Extra word"
            elif ws.match_type == "substitution":
                status = f"❌ Wrong ({ws.similarity:.0%})"
            else:
                status = "❓ Unknown"

            print(
                f"{i:<4} {ws.expected:<20} {ws.detected:<20} {status:<15}"
            )

        if len(result.word_scores) > 30:
            print(f"... and {len(result.word_scores) - 30} more words")

        print(f"{'─'*70}\n")

        # Feedback
        print(f"💬 DETAILED FEEDBACK")
        print(f"{'─'*70}")
        for feedback in result.detailed_feedback:
            print(feedback)

        print(f"\n{'='*70}\n")


# ==================== DEMO ====================

def demo():
    """Demo function"""
    # Initialize
    assessor = PracticalPronunciationAssessment(language="id")

    print("\n" + "="*70)
    print("📚 USAGE EXAMPLE")
    print("="*70)

    # Contoh penggunaan dengan transcript sebagai variabel
    transcribed_text = """
    assalamualaikum warahmatullahi wabarakatuh selamat pagi dan salam sejahtera bagi kita semua 
    hadirin yang saya hormati di era modern ini teknologi telah menjadi bagian penting dari 
    kehidupan manusia hampir setiap aspek kehidupan mulai dari pendidikan kesehatan hingga 
    komunikasi kini bergantung pada kemajuan teknologi dengan teknologi jarak bukan lagi 
    penghalang waktu bukan lagi batas dan informasi dapat diakses dalam hitungan detik 
    namun di balik kemudahan itu kita harus tetap bijak teknologi bukan hanya soal 
    kecanggihan tetapi juga tanggung jawab kita harus mampu menggunakannya untuk hal-hal 
    positif membangun kreativitas dan memperluas wawasan mari kita jadikan teknologi 
    sebagai alat untuk menciptakan perubahan bukan sekadar hiburan dengan semangat 
    inovasi dan etika digital kita dapat membangun masa depan yang lebih baik dan 
    bermanfaat bagi semua terima kasih wassalamualaikum warahmatullahi wabarakatuh
    """

    reference_text = """
    Assalamualaikum warahmatullahi wabarakatuh,
    Selamat pagi dan salam sejahtera bagi kita semua.
    Hadirin yang saya hormati,
    Di era modern ini, teknologi telah menjadi bagian penting dari kehidupan manusia.
    Hampir setiap aspek kehidupan, mulai dari pendidikan, kesehatan, hingga komunikasi,
    kini bergantung pada kemajuan teknologi.
    Dengan teknologi, jarak bukan lagi penghalang, waktu bukan lagi batas,
    dan informasi dapat diakses dalam hitungan detik.
    Namun, di balik kemudahan itu, kita harus tetap bijak.
    Teknologi bukan hanya soal kecanggihan, tetapi juga tanggung jawab.
    Kita harus mampu menggunakannya untuk hal-hal positif,
    membangun kreativitas, dan memperluas wawasan.
    Mari kita jadikan teknologi sebagai alat untuk menciptakan perubahan,
    bukan sekadar hiburan.
    Dengan semangat inovasi dan etika digital,
    kita dapat membangun masa depan yang lebih baik dan bermanfaat bagi semua.
    Terima kasih.
    Wassalamualaikum warahmatullahi wabarakatuh.
    """

    result = assessor.assess_pronunciation(
        transcribed_text=transcribed_text,
        reference_text=reference_text
    )

    # View report
    assessor.print_detailed_report(result)

    # Get simple result for API
    simple_result = assessor.get_simple_result(result)
    print(f"🎯 SIMPLE RESULT FOR API:")
    print(simple_result)


if __name__ == "__main__":
    demo()