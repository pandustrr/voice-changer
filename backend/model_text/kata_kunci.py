import json
import re
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict

# Install dependencies:
# pip install sentence-transformers numpy scikit-learn

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("⚠️  Warning: sentence-transformers not installed. Using fallback mode.")
    print("   Install with: pip install sentence-transformers")


class AdvancedTopicRelevanceAnalyzer:
    """
    Advanced AI analyzer dengan BERT embeddings untuk semantic understanding
    Scoring berdasarkan jumlah keyword yang relevan
    """

    def __init__(self, dataset_path: str, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        """
        Initialize analyzer dengan BERT model

        Args:
            dataset_path: Path ke file JSON dataset (REQUIRED)
            model_name: Nama model Sentence Transformer (default: multilingual)
        """
        self.dataset_path = dataset_path
        self.topics = {}

        # Load dataset dari JSON
        self.load_dataset(dataset_path)

        # Load BERT model untuk embeddings
        if EMBEDDINGS_AVAILABLE:
            print(f"🔄 Loading BERT model: {model_name}...")
            self.model = SentenceTransformer(model_name)
            print("✅ Model loaded successfully!")
        else:
            self.model = None
            print("⚠️  Running in fallback mode (no embeddings)")

        # Precompute embeddings untuk efisiensi
        self.keyword_embeddings = {}
        if self.model:
            self._precompute_embeddings()

    def load_dataset(self, json_path: str):
        """Load dataset dari file JSON"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.topics = json.load(f)
            print(f"✅ Dataset loaded: {len(self.topics)} topics")
        except FileNotFoundError:
            raise FileNotFoundError(f"❌ Dataset file not found: {json_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ Invalid JSON format: {e}")

    def _precompute_embeddings(self):
        """Precompute embeddings untuk semua keywords dan context phrases"""
        if not self.model:
            return

        print("🔄 Precomputing embeddings...")

        for topic_id, topic_data in self.topics.items():
            self.keyword_embeddings[topic_id] = {}

            # Embed keywords
            keywords = topic_data['keywords']
            self.keyword_embeddings[topic_id]['keywords'] = self.model.encode(keywords)

            # Embed variants
            all_variants = []
            variant_mapping = []
            for keyword in keywords:
                variants = topic_data['variants'].get(keyword, [])
                for variant in variants:
                    all_variants.append(variant)
                    variant_mapping.append(keyword)

            if all_variants:
                self.keyword_embeddings[topic_id]['variants'] = {
                    'embeddings': self.model.encode(all_variants),
                    'mapping': variant_mapping,
                    'texts': all_variants
                }

            # Embed context phrases jika ada
            if 'context_phrases' in topic_data:
                context_phrases = topic_data['context_phrases']
                self.keyword_embeddings[topic_id]['context'] = self.model.encode(context_phrases)

        print("✅ Embeddings ready!")

    def preprocess_text(self, text: str) -> str:
        """Normalize text"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences dari text"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def semantic_keyword_detection(self, text: str, topic_id: str,
                                   threshold: float = 0.5) -> Dict:
        """
        Deteksi keyword menggunakan semantic similarity (BERT embeddings)

        Args:
            text: Teks speech
            topic_id: ID topik
            threshold: Threshold similarity (0-1)

        Returns:
            Dictionary berisi detected keywords dengan detail
        """
        if not self.model or topic_id not in self.keyword_embeddings:
            return self._fallback_detection(text, topic_id)

        sentences = self.extract_sentences(text)
        sentence_embeddings = self.model.encode(sentences)

        topic_data = self.topics[topic_id]
        keyword_embs = self.keyword_embeddings[topic_id]

        detected_keywords = defaultdict(list)

        # 1. Direct keyword matching dengan embeddings
        keyword_similarities = cosine_similarity(
            sentence_embeddings,
            keyword_embs['keywords']
        )

        for sent_idx, sentence in enumerate(sentences):
            for kw_idx, keyword in enumerate(topic_data['keywords']):
                similarity = keyword_similarities[sent_idx][kw_idx]

                if similarity >= threshold:
                    detected_keywords[keyword].append({
                        'type': 'semantic',
                        'sentence': sentence,
                        'similarity': float(similarity),
                        'confidence': 'high' if similarity >= 0.7 else 'medium'
                    })

        # 2. Variant matching dengan embeddings
        if 'variants' in keyword_embs:
            variant_similarities = cosine_similarity(
                sentence_embeddings,
                keyword_embs['variants']['embeddings']
            )

            for sent_idx, sentence in enumerate(sentences):
                for var_idx, (variant, mapped_kw) in enumerate(
                    zip(keyword_embs['variants']['texts'],
                        keyword_embs['variants']['mapping'])
                ):
                    similarity = variant_similarities[sent_idx][var_idx]

                    if similarity >= threshold:
                        if not any(d['type'] == 'variant' and d.get('variant') == variant
                                 for d in detected_keywords[mapped_kw]):
                            detected_keywords[mapped_kw].append({
                                'type': 'variant',
                                'variant': variant,
                                'sentence': sentence,
                                'similarity': float(similarity),
                                'confidence': 'high' if similarity >= 0.7 else 'medium'
                            })

        # 3. Exact string matching (untuk akurasi tinggi)
        text_lower = text.lower()
        for keyword in topic_data['keywords']:
            if keyword in text_lower:
                if not any(d['type'] == 'exact' for d in detected_keywords[keyword]):
                    detected_keywords[keyword].insert(0, {
                        'type': 'exact',
                        'keyword': keyword,
                        'similarity': 1.0,
                        'confidence': 'exact'
                    })

            # Check variants untuk exact match
            for variant in topic_data['variants'].get(keyword, []):
                if variant.lower() in text_lower:
                    if not any(d['type'] == 'exact_variant' and d.get('variant') == variant
                             for d in detected_keywords[keyword]):
                        detected_keywords[keyword].insert(0, {
                            'type': 'exact_variant',
                            'variant': variant,
                            'similarity': 1.0,
                            'confidence': 'exact'
                        })

        return dict(detected_keywords)

    def _fallback_detection(self, text: str, topic_id: str) -> Dict:
        """Fallback method tanpa embeddings"""
        text_lower = text.lower()
        topic_data = self.topics[topic_id]
        detected_keywords = {}

        for keyword in topic_data['keywords']:
            detections = []

            # Exact match
            if keyword in text_lower:
                detections.append({
                    'type': 'exact',
                    'keyword': keyword,
                    'similarity': 1.0,
                    'confidence': 'exact'
                })

            # Variant match
            for variant in topic_data['variants'].get(keyword, []):
                if variant.lower() in text_lower:
                    detections.append({
                        'type': 'variant',
                        'variant': variant,
                        'similarity': 0.9,
                        'confidence': 'high'
                    })

            if detections:
                detected_keywords[keyword] = detections

        return detected_keywords

    def calculate_relevance_score(self, detected_count: int, total_keywords: int) -> Dict:
        """
        Calculate skor berdasarkan jumlah keyword yang terdeteksi

        Args:
            detected_count: Jumlah keyword yang terdeteksi
            total_keywords: Total keyword dalam topik

        Returns:
            Dict dengan score, category, dan keterangan
        """
        if detected_count >= 9:
            return {
                'score': 5,
                'category': 'Sangat Baik',
                'description': 'Coverage keyword sangat lengkap',
                'emoji': '🌟'
            }
        elif detected_count >= 7:
            return {
                'score': 4,
                'category': 'Baik',
                'description': 'Coverage keyword baik, beberapa poin bisa ditambah',
                'emoji': '⭐'
            }
        elif detected_count >= 5:
            return {
                'score': 3,
                'category': 'Cukup',
                'description': 'Coverage keyword cukup, perlu penambahan pembahasan',
                'emoji': '✨'
            }
        elif detected_count >= 3:
            return {
                'score': 2,
                'category': 'Buruk',
                'description': 'Coverage keyword kurang, banyak poin yang belum dibahas',
                'emoji': '⚠️'
            }
        else:
            return {
                'score': 1,
                'category': 'Perlu Ditingkatkan',
                'description': 'Coverage keyword sangat rendah, perlu revisi menyeluruh',
                'emoji': '❌'
            }

    def calculate_depth_score(self, detections: List[Dict]) -> float:
        """Calculate kedalaman pembahasan suatu keyword"""
        if not detections:
            return 0.0

        # Faktor: jumlah kalimat, tipe deteksi, confidence
        depth = 0
        for d in detections:
            if d['confidence'] == 'exact':
                depth += 2.0
            elif d['confidence'] == 'high':
                depth += 1.5
            else:
                depth += 1.0

        # Normalize (max 5.0)
        return min(depth, 5.0)

    def analyze_relevance(self, speech_text: str, topic_id: str,
                         threshold: float = 0.5) -> Dict:
        """
        Analisis relevansi speech dengan topik menggunakan BERT embeddings

        Args:
            speech_text: Teks speech
            topic_id: ID topik
            threshold: Similarity threshold (0-1)

        Returns:
            Dictionary berisi hasil analisis lengkap
        """
        if topic_id not in self.topics:
            return {"error": f"Topik '{topic_id}' tidak ditemukan"}

        topic_data = self.topics[topic_id]

        # Deteksi keywords
        detected_keywords = self.semantic_keyword_detection(
            speech_text, topic_id, threshold
        )

        missing_keywords = [
            kw for kw in topic_data['keywords']
            if kw not in detected_keywords
        ]

        # Calculate scores
        total_keywords = len(topic_data['keywords'])
        detected_count = len(detected_keywords)

        # Coverage percentage
        coverage_percentage = (detected_count / total_keywords) * 100

        # Relevance score berdasarkan jumlah keyword
        relevance_scoring = self.calculate_relevance_score(detected_count, total_keywords)

        # Overall depth score
        depth_scores = {}
        for keyword, detections in detected_keywords.items():
            depth_scores[keyword] = self.calculate_depth_score(detections)

        avg_depth = (sum(depth_scores.values()) / len(depth_scores)) if depth_scores else 0

        # === Buat summary hasil analisis untuk backend ===
        summary_result = {
            "topic_id": topic_id,
            "topic_title": topic_data['title'],
            "threshold": threshold,
            "scores": {
                "relevance_score": relevance_scoring['score'],
                "relevance_category": relevance_scoring['category'],
                "coverage_percentage": round(coverage_percentage, 1),
                "depth_score": round(avg_depth, 2)
            },
            "keywords": {
                "detected": [
                    {
                        "keyword": kw,
                        "depth_score": round(depth_scores.get(kw, 0), 2),
                        "detections": detected_keywords.get(kw, [])
                    }
                    for kw in detected_keywords.keys()
                ],
                "missing": [
                    {"keyword": kw}
                    for kw in missing_keywords
                ]
            }
        }


        return {
            'topic_id': topic_id,
            'topic_title': topic_data['title'],
            'detected_count': detected_count,
            'total_keywords': total_keywords,
            'coverage_percentage': round(coverage_percentage, 1),
            'relevance_score': relevance_scoring['score'],
            'relevance_category': relevance_scoring['category'],
            'relevance_description': relevance_scoring['description'],
            'relevance_emoji': relevance_scoring['emoji'],
            'depth_score': round(avg_depth, 2),
            'detected_keywords': detected_keywords,
            'missing_keywords': missing_keywords,
            'depth_scores': depth_scores,
            'threshold_used': threshold,
            'summary_result': summary_result
        }

    def generate_report(self, analysis_result: Dict, show_details: bool = True) -> str:
        """Generate laporan analisis yang comprehensive"""
        if "error" in analysis_result:
            return f"❌ Error: {analysis_result['error']}"

        report = []
        report.append("=" * 90)
        report.append("📊 ADVANCED AI ANALYSIS - PUBLIC SPEAKING RELEVANCE")
        report.append("=" * 90)
        report.append(f"\n🎯 Topik: {analysis_result['topic_title']}")
        report.append(f"🆔 Topic ID: {analysis_result['topic_id']}")

        # Scores
        report.append(f"\n{'─' * 90}")
        report.append("📈 SKOR RELEVANSI:")
        report.append(f"{'─' * 90}")

        emoji = analysis_result['relevance_emoji']
        score = analysis_result['relevance_score']
        category = analysis_result['relevance_category']

        report.append(f"   {emoji} Relevance Score:  {score}/5")
        report.append(f"   📊 Category:         {category}")
        report.append(f"   📝 Keterangan:       {analysis_result['relevance_description']}")
        report.append(f"")
        report.append(f"   📊 Coverage:         {analysis_result['coverage_percentage']:.1f}% ({analysis_result['detected_count']}/{analysis_result['total_keywords']} keywords)")
        report.append(f"   📖 Depth Score:      {analysis_result['depth_score']:.1f}/5.0")

        # Detected keywords
        report.append(f"\n{'─' * 90}")
        report.append(f"✅ KEYWORD TERDETEKSI ({analysis_result['detected_count']}/{analysis_result['total_keywords']}):")
        report.append(f"{'─' * 90}")

        if analysis_result['detected_keywords']:
            for keyword, detections in sorted(analysis_result['detected_keywords'].items()):
                depth = analysis_result['depth_scores'].get(keyword, 0)
                depth_bar = "█" * int(depth) + "░" * (5 - int(depth))

                report.append(f"\n   🔹 {keyword.upper()}")
                report.append(f"      Depth: [{depth_bar}] {depth:.1f}/5.0")

                if show_details:
                    # Show top 2 detections
                    for i, det in enumerate(detections[:2], 1):
                        conf_emoji = "✓" if det['confidence'] == 'exact' else "≈"

                        if det['type'] == 'exact':
                            report.append(f"      {conf_emoji} Exact match (100%)")
                        elif det['type'] == 'exact_variant':
                            report.append(f"      {conf_emoji} Exact variant: '{det['variant']}' (100%)")
                        elif det['type'] == 'variant':
                            report.append(f"      {conf_emoji} Variant: '{det['variant']}' ({det['similarity']*100:.0f}%)")
                        elif det['type'] == 'semantic':
                            report.append(f"      {conf_emoji} Semantic: {det['similarity']*100:.0f}% confidence")
                            if 'sentence' in det and len(det['sentence']) < 100:
                                report.append(f"         → \"{det['sentence']}\"")
        else:
            report.append("   (Tidak ada keyword terdeteksi)")

        # Missing keywords
        if analysis_result['missing_keywords']:
            report.append(f"\n{'─' * 90}")
            report.append(f"❌ KEYWORD BELUM DISEBUTKAN ({len(analysis_result['missing_keywords'])}/{analysis_result['total_keywords']}):")
            report.append(f"{'─' * 90}")

            for keyword in analysis_result['missing_keywords']:
                report.append(f"   • {keyword}")


        return "\n".join(report)


# ===== CONTOH PENGGUNAAN =====
if __name__ == "__main__":
    print("🚀 Advanced Topic Relevance Analyzer with BERT\n")

    # Path ke dataset JSON
    dataset_path = './kata_kunci.json'

    # Initialize analyzer
    analyzer = AdvancedTopicRelevanceAnalyzer(dataset_path=dataset_path)

    # Sample speech
    sample_speech = """
    Selamat pagi teman-teman. Hari ini saya ingin membahas tentang Generasi Z
    dan bagaimana mereka bekerja di era digital.

    Generasi Z tumbuh di tengah digitalisasi yang sangat pesat. Mereka sangat
    mahir menggunakan media sosial seperti Instagram, TikTok, dan platform lainnya
    untuk berbagai keperluan. mereka dalam dunia digital sangat tinggi.

    Mereka pandai melakukan personal branding melalui konten-konten kreatif yang
    mereka buat. Self-branding menjadi keahlian penting di era ini. Namun, ada
    tantangan besar yaitu distraksi. Notifikasi yang tidak henti-hentinya membuat
    fokus terganggu. Banyak yang mencoba multitasking tapi hasilnya tidak maksimal.

    Kebiasaan online mereka sangat intens, kadang sampai lupa waktu. Yang penting
    adalah mencari keseimbangan. Kita tidak boleh melupakan realitas sosial dan
    interaksi di dunia nyata. Dunia digital memang memberikan banyak kemudahan,
    tapi kehidupan offline tetap penting untuk perkembangan karakter dan empati.

    Terima kasih atas perhatiannya.
    """

    print("=" * 90)
    print("ANALISIS CONTOH SPEECH")
    print("=" * 90)

    # Analyze
    result = analyzer.analyze_relevance(sample_speech, "1", threshold=0.7)
    print(analyzer.generate_report(result, show_details=True))
