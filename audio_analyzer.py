"""
Advanced Audio Analyzer
고급 오디오 분석 엔진: BPM, 비트 그리드, 키, 에너지 레벨, 구간 감지
"""

import librosa
import numpy as np
from scipy import signal
from typing import Dict, Tuple, List


class AudioAnalyzer:
    """전문가급 오디오 분석 클래스"""
    
    # Camelot Wheel for harmonic mixing
    CAMELOT_WHEEL = {
        'C major': '8B', 'A minor': '8A',
        'G major': '9B', 'E minor': '9A',
        'D major': '10B', 'B minor': '10A',
        'A major': '11B', 'F# minor': '11A',
        'E major': '12B', 'C# minor': '12A',
        'B major': '1B', 'G# minor': '1A',
        'F# major': '2B', 'D# minor': '2A',
        'Db major': '3B', 'Bb minor': '3A',
        'Ab major': '4B', 'F minor': '4A',
        'Eb major': '5B', 'C minor': '5A',
        'Bb major': '6B', 'G minor': '6A',
        'F major': '7B', 'D minor': '7A',
    }
    
    KEY_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    def __init__(self, audio_path: str):
        """
        오디오 파일 로드
        
        Args:
            audio_path: 분석할 오디오 파일 경로
        """
        print(f"🎵 Loading audio: {audio_path}")
        self.audio_path = audio_path
        self.y, self.sr = librosa.load(audio_path, sr=44100, mono=True)
        self.duration = librosa.get_duration(y=self.y, sr=self.sr)
        print(f"✓ Loaded {self.duration:.2f} seconds at {self.sr} Hz")
    
    def analyze_tempo_and_beats(self) -> Dict:
        """
        BPM과 비트 그리드 분석
        
        Returns:
            dict: bpm, beats, downbeats, beat_frames
        """
        print("🎼 Analyzing tempo and beats...")
        
        # Tempo 추정
        tempo, beat_frames = librosa.beat.beat_track(y=self.y, sr=self.sr, units='frames')
        beat_times = librosa.frames_to_time(beat_frames, sr=self.sr)
        
        # Downbeat 감지 (강박)
        # 더 정확한 분석을 위해 onset strength 사용
        onset_env = librosa.onset.onset_strength(y=self.y, sr=self.sr)
        
        # 4/4 박자 가정하여 downbeat 추정
        if len(beat_times) >= 4:
            # 비트 간격 분석
            beat_intervals = np.diff(beat_times)
            avg_interval = np.median(beat_intervals)
            
            # 4비트마다 downbeat
            downbeat_indices = np.arange(0, len(beat_times), 4)
            downbeat_times = beat_times[downbeat_indices]
        else:
            downbeat_times = beat_times[:1] if len(beat_times) > 0 else np.array([])
        
        print(f"✓ BPM: {float(tempo):.2f}, Beats: {len(beat_times)}, Downbeats: {len(downbeat_times)}")
        
        return {
            'bpm': float(tempo),
            'beats': beat_times,
            'downbeats': downbeat_times,
            'beat_frames': beat_frames,
            'beat_count': len(beat_times)
        }
    
    def analyze_key(self) -> Dict:
        """
        음악의 키(조성) 분석
        
        Returns:
            dict: key, scale, camelot
        """
        print("🎹 Analyzing key and scale...")
        
        # Chromagram 계산
        chroma = librosa.feature.chroma_cqt(y=self.y, sr=self.sr)
        
        # 평균 chroma 벡터
        chroma_mean = np.mean(chroma, axis=1)
        
        # 가장 강한 음 찾기
        key_index = np.argmax(chroma_mean)
        key_name = self.KEY_NAMES[key_index]
        
        # Major/Minor 판단 (간단한 휴리스틱)
        # Major: 1-3-5 (root, major third, fifth)
        # Minor: 1-b3-5 (root, minor third, fifth)
        major_third = (key_index + 4) % 12
        minor_third = (key_index + 3) % 12
        
        major_strength = chroma_mean[major_third]
        minor_strength = chroma_mean[minor_third]
        
        if major_strength > minor_strength:
            scale = 'major'
            full_key = f"{key_name} major"
        else:
            scale = 'minor'
            full_key = f"{key_name} minor"
        
        # Camelot 코드
        camelot = self.CAMELOT_WHEEL.get(full_key, 'Unknown')
        
        print(f"✓ Key: {full_key}, Camelot: {camelot}")
        
        return {
            'key': key_name,
            'scale': scale,
            'full_key': full_key,
            'camelot': camelot
        }
    
    def analyze_energy(self) -> Dict:
        """
        에너지 레벨 분석
        
        Returns:
            dict: energy_curve, avg_energy, peak_energy
        """
        print("⚡ Analyzing energy levels...")
        
        # RMS 에너지
        rms = librosa.feature.rms(y=self.y)[0]
        
        # Spectral centroid (밝기/에너지 지표)
        spectral_centroid = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)[0]
        
        # 정규화된 에너지 커브
        energy_curve = rms / np.max(rms) if np.max(rms) > 0 else rms
        
        # 시간 축
        times = librosa.frames_to_time(np.arange(len(energy_curve)), sr=self.sr)
        
        avg_energy = float(np.mean(energy_curve))
        peak_energy = float(np.max(energy_curve))
        
        print(f"✓ Avg Energy: {avg_energy:.3f}, Peak: {peak_energy:.3f}")
        
        return {
            'energy_curve': energy_curve,
            'energy_times': times,
            'avg_energy': avg_energy,
            'peak_energy': peak_energy,
            'spectral_centroid': spectral_centroid
        }
    
    def detect_segments(self, beat_info: Dict, energy_info: Dict) -> Dict:
        """
        곡의 구간 감지 (인트로, 빌드업, 드롭, 아웃트로)
        
        Args:
            beat_info: 비트 정보
            energy_info: 에너지 정보
            
        Returns:
            dict: intro, buildup, drop, outro 구간
        """
        print("📊 Detecting song segments...")
        
        energy_curve = energy_info['energy_curve']
        duration = self.duration
        
        # 간단한 휴리스틱으로 구간 감지
        # 인트로: 처음 10-20% (낮은 에너지)
        intro_end = min(duration * 0.15, 30)  # 최대 30초
        
        # 아웃트로: 마지막 10-20% (에너지 감소)
        outro_start = max(duration * 0.85, duration - 30)
        
        # 에너지 피크로 드롭 찾기
        if len(energy_curve) > 0:
            # 에너지가 평균보다 높은 구간
            high_energy_threshold = energy_info['avg_energy'] * 1.2
            high_energy_frames = np.where(energy_curve > high_energy_threshold)[0]
            
            if len(high_energy_frames) > 0:
                drop_frame = high_energy_frames[0]
                drop_time = librosa.frames_to_time(drop_frame, sr=self.sr)
                
                # 빌드업은 드롭 직전
                buildup_start = max(0, drop_time - 16)  # 드롭 16초 전
                buildup_end = drop_time
            else:
                # 에너지 피크가 명확하지 않으면 중간 지점
                drop_time = duration * 0.4
                buildup_start = duration * 0.3
                buildup_end = drop_time
        else:
            drop_time = duration * 0.4
            buildup_start = duration * 0.3
            buildup_end = drop_time
        
        segments = {
            'intro': {'start': 0, 'end': intro_end},
            'buildup': {'start': buildup_start, 'end': buildup_end},
            'drop': {'start': drop_time, 'end': min(drop_time + 30, outro_start)},
            'outro': {'start': outro_start, 'end': duration}
        }
        
        print(f"✓ Segments detected:")
        for name, seg in segments.items():
            print(f"  - {name.capitalize()}: {seg['start']:.1f}s - {seg['end']:.1f}s")
        
        return segments
    
    def analyze_full(self) -> Dict:
        """
        전체 분석 수행
        
        Returns:
            dict: 모든 분석 결과
        """
        print(f"\n{'='*60}")
        print(f"🎧 Full Audio Analysis: {self.audio_path}")
        print(f"{'='*60}\n")
        
        # 각 분석 수행
        tempo_info = self.analyze_tempo_and_beats()
        key_info = self.analyze_key()
        energy_info = self.analyze_energy()
        segments = self.detect_segments(tempo_info, energy_info)
        
        # 결과 통합
        result = {
            'file_path': self.audio_path,
            'duration': self.duration,
            'sample_rate': self.sr,
            **tempo_info,
            **key_info,
            **energy_info,
            'segments': segments
        }
        
        print(f"\n{'='*60}")
        print("✅ Analysis Complete!")
        print(f"{'='*60}\n")
        
        return result
    
    @staticmethod
    def are_keys_compatible(camelot1: str, camelot2: str) -> Tuple[bool, str]:
        """
        두 키가 하모닉 믹싱에 호환되는지 확인
        
        Args:
            camelot1: 첫 번째 곡의 Camelot 코드
            camelot2: 두 번째 곡의 Camelot 코드
            
        Returns:
            (호환 여부, 설명)
        """
        if camelot1 == 'Unknown' or camelot2 == 'Unknown':
            return False, "Unknown key"
        
        # 같은 키
        if camelot1 == camelot2:
            return True, "Perfect match (same key)"
        
        # 숫자와 문자 분리
        num1, letter1 = int(camelot1[:-1]), camelot1[-1]
        num2, letter2 = int(camelot2[:-1]), camelot2[-1]
        
        # 같은 숫자, 다른 문자 (relative major/minor)
        if num1 == num2 and letter1 != letter2:
            return True, "Relative major/minor"
        
        # ±1 숫자 (같은 문자)
        if letter1 == letter2:
            if (num1 + 1) % 12 == num2 % 12 or (num1 - 1) % 12 == num2 % 12:
                return True, "Adjacent key (±1 semitone)"
        
        return False, "Incompatible keys"


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python audio_analyzer.py <audio_file>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    analyzer = AudioAnalyzer(audio_file)
    result = analyzer.analyze_full()
    
    # 결과 출력
    print("\n📋 Analysis Summary:")
    print(f"Duration: {result['duration']:.2f}s")
    print(f"BPM: {result['bpm']:.2f}")
    print(f"Key: {result['full_key']} ({result['camelot']})")
    print(f"Beats: {result['beat_count']}")
    print(f"Energy: {result['avg_energy']:.3f}")
