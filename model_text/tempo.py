"""
Tempo Analysis - Analisis jeda bicara dengan Silero VAD
Fixed version dengan error handling dan return value yang proper
"""

import torch
import torchaudio
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')


class TempoAnalyzer:
    """Analyzer untuk tempo dan jeda bicara"""
    
    def __init__(self):
        """Initialize Silero VAD model"""
        print("🔄 Loading Silero VAD model...")
        
        torch.set_num_threads(1)
        self.model, self.utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            verbose=False
        )
        
        (self.get_speech_timestamps,
         self.save_audio,
         self.read_audio,
         self.VADIterator,
         self.collect_chunks) = self.utils
        
        print("✅ Silero VAD model loaded!")
    
    def skor_jeda(self, pause: float) -> int:
        """
        Beri nilai berdasarkan durasi jeda
        Jeda <= 3 detik → 1 (baik)
        Jeda > 3 detik → 0 (terlalu lama)
        """
        return 1 if pause <= 3.0 else 0
    
    def analyze(self, audio_path: str, sampling_rate: int = 16000) -> Dict:
        """
        Analisis tempo dan jeda bicara
        
        Args:
            audio_path: Path ke file audio
            sampling_rate: Sample rate audio (default: 16000)
        
        Returns:
            Dictionary berisi hasil analisis
        """
        try:
            # Read audio
            wav = self.read_audio(audio_path, sampling_rate=sampling_rate)
            
            # Detect speech segments
            speech_timestamps = self.get_speech_timestamps(
                wav,
                self.model,
                sampling_rate=sampling_rate,
                threshold=0.5,
                min_speech_duration_ms=250,
                min_silence_duration_ms=100
            )
            
            if not speech_timestamps:
                return {
                    "error": "No speech detected in audio",
                    "segments": [],
                    "total_segments": 0
                }
            
            # Analyze segments
            segments_data = []
            total_pause = 0
            total_score = 0
            num_pauses = 0
            
            for i, seg in enumerate(speech_timestamps):
                start_time = seg['start'] / sampling_rate
                end_time = seg['end'] / sampling_rate
                duration = end_time - start_time
                
                if i == 0:
                    pause_before = start_time
                else:
                    pause_before = start_time - (speech_timestamps[i - 1]['end'] / sampling_rate)
                
                # Calculate score
                skor = self.skor_jeda(pause_before)
                
                total_pause += pause_before
                total_score += skor
                num_pauses += 1
                
                segments_data.append({
                    'segment': i + 1,
                    'start_sec': round(start_time, 2),
                    'end_sec': round(end_time, 2),
                    'duration_sec': round(duration, 2),
                    'pause_before_sec': round(pause_before, 2),
                    'pause_score': skor
                })
            
            # Calculate averages
            avg_pause = total_pause / num_pauses if num_pauses > 0 else 0
            avg_score = total_score / num_pauses if num_pauses > 0 else 0
            
            # Determine category
            if avg_score >= 0.9:
                category = "Sangat Baik"
                points = 5
                description = "Tempo bicara sangat baik, jeda-jeda natural dan tidak terlalu lama"
            elif avg_score >= 0.7:
                category = "Baik"
                points = 4
                description = "Tempo bicara baik, beberapa jeda sedikit panjang"
            elif avg_score >= 0.5:
                category = "Cukup"
                points = 3
                description = "Tempo bicara cukup, ada beberapa jeda yang terlalu lama"
            elif avg_score >= 0.3:
                category = "Buruk"
                points = 2
                description = "Tempo bicara buruk, banyak jeda yang terlalu lama"
            else:
                category = "Perlu Ditingkatkan"
                points = 1
                description = "Tempo bicara perlu ditingkatkan, jeda terlalu sering dan terlalu lama"
            
            return {
                "status": "success",
                "total_segments": len(speech_timestamps),
                "segments": segments_data[:10],  # Return first 10 segments
                "summary": {
                    "avg_pause_sec": round(avg_pause, 2),
                    "avg_score": round(avg_score, 2),
                    "points": points,
                    "category": category,
                    "description": description
                },
                "recommendations": self._get_recommendations(avg_pause, avg_score)
            }
            
        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "status": "failed"
            }
    
    def _get_recommendations(self, avg_pause: float, avg_score: float) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if avg_pause > 3.0:
            recommendations.append("Kurangi jeda yang terlalu lama antar kalimat")
            recommendations.append("Latih kelancaran berbicara dengan membaca naskah berulang kali")
        
        if avg_pause < 0.5:
            recommendations.append("Tambahkan jeda natural untuk memberi penekanan")
            recommendations.append("Jangan terburu-buru, berikan waktu untuk pendengar mencerna informasi")
        
        if avg_score >= 0.8:
            recommendations.append("Tempo bicara sudah sangat baik! Pertahankan konsistensi")
        elif avg_score >= 0.6:
            recommendations.append("Perhatikan jeda di beberapa bagian untuk meningkatkan kualitas")
        else:
            recommendations.append("Fokus pada latihan tempo dan jeda bicara")
            recommendations.append("Rekam dan dengarkan kembali untuk evaluasi")
        
        return recommendations


# ==================== DEMO ====================

if __name__ == "__main__":
    print("🎤 TEMPO ANALYZER DEMO\n")
    
    # Initialize
    analyzer = TempoAnalyzer()
    
    # Analyze
    audio_path = "./bad.wav"
    result = analyzer.analyze(audio_path)
    
    # Print results
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("="*70)
        print("📊 ANALISIS TEMPO BICARA")
        print("="*70)
        print(f"\n🎯 HASIL:")
        print(f"   Total Segmen: {result['total_segments']}")
        print(f"   Rata-rata Jeda: {result['summary']['avg_pause_sec']} detik")
        print(f"   Skor Rata-rata: {result['summary']['avg_score']:.2f}/1.0")
        print(f"   Poin: {result['summary']['points']}/5")
        print(f"   Kategori: {result['summary']['category']}")
        print(f"\n📝 {result['summary']['description']}")
        
        print(f"\n💡 REKOMENDASI:")
        for rec in result['recommendations']:
            print(f"   • {rec}")
        
        print(f"\n📄 Detail Segmen (10 pertama):")
        print(f"{'─'*70}")
        print(f"{'No':<4} {'Mulai':<8} {'Selesai':<8} {'Durasi':<8} {'Jeda':<8} {'Skor':<6}")
        print(f"{'─'*70}")
        
        for seg in result['segments']:
            print(
                f"{seg['segment']:<4} "
                f"{seg['start_sec']:<8} "
                f"{seg['end_sec']:<8} "
                f"{seg['duration_sec']:<8} "
                f"{seg['pause_before_sec']:<8} "
                f"{seg['pause_score']:<6}"
            )
        
        print(f"{'─'*70}\n")
