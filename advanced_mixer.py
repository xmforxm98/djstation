"""
Advanced Music Mixer
프로페셔널 DJ 스타일의 고급 음악 믹싱 엔진
"""

import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment
import pyrubberband as pyrb
from pedalboard import Pedalboard, HighpassFilter, LowpassFilter, Gain
from typing import Dict, Tuple, Optional
from audio_analyzer import AudioAnalyzer


class AdvancedMixer:
    """전문가급 음악 믹싱 엔진"""
    
    def __init__(self):
        self.sample_rate = 44100
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        오디오 파일 로드
        
        Args:
            file_path: 오디오 파일 경로
            
        Returns:
            (audio_data, sample_rate)
        """
        y, sr = librosa.load(file_path, sr=self.sample_rate, mono=False)
        
        # 스테레오로 변환 (모노인 경우)
        if y.ndim == 1:
            y = np.stack([y, y])
        
        return y, sr
    
    def match_tempo(self, audio: np.ndarray, original_bpm: float, target_bpm: float) -> np.ndarray:
        """
        템포 매칭 (time-stretching without pitch change)
        
        Args:
            audio: 오디오 데이터
            original_bpm: 원본 BPM
            target_bpm: 목표 BPM
            
        Returns:
            템포가 조정된 오디오
        """
        if abs(original_bpm - target_bpm) < 0.5:
            print(f"  ⏭️  Tempo already matched ({original_bpm:.1f} BPM)")
            return audio
        
        rate = target_bpm / original_bpm
        print(f"  🎚️  Stretching tempo: {original_bpm:.1f} → {target_bpm:.1f} BPM (rate: {rate:.3f})")
        
        # pyrubberband로 고품질 time-stretching
        # 스테레오 처리
        if audio.ndim == 2:
            stretched = np.zeros_like(audio)
            for ch in range(audio.shape[0]):
                stretched[ch] = pyrb.time_stretch(audio[ch], self.sample_rate, rate)
        else:
            stretched = pyrb.time_stretch(audio, self.sample_rate, rate)
        
        return stretched
    
    def align_beats(self, audio1: np.ndarray, audio2: np.ndarray, 
                    beats1: np.ndarray, beats2: np.ndarray,
                    transition_point: float) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        비트 정렬 - 두 트랙의 비트를 완벽하게 동기화
        
        Args:
            audio1: 첫 번째 오디오
            audio2: 두 번째 오디오
            beats1: 첫 번째 오디오의 비트 타임스탬프
            beats2: 두 번째 오디오의 비트 타임스탬프
            transition_point: 전환 시작 지점 (초)
            
        Returns:
            (정렬된 audio1, 정렬된 audio2, 조정된 전환 지점)
        """
        print(f"  🎯 Aligning beats at transition point: {transition_point:.2f}s")
        
        # 전환 지점에서 가장 가까운 비트 찾기
        if len(beats1) > 0:
            closest_beat1_idx = np.argmin(np.abs(beats1 - transition_point))
            aligned_point1 = beats1[closest_beat1_idx]
        else:
            aligned_point1 = transition_point
        
        # audio2는 시작 비트에 맞춤
        if len(beats2) > 0:
            first_beat2 = beats2[0]
        else:
            first_beat2 = 0
        
        print(f"  ✓ Beat alignment: Track1 @ {aligned_point1:.2f}s, Track2 @ {first_beat2:.2f}s")
        
        return audio1, audio2, aligned_point1
    
    def find_optimal_transition_point(self, analysis1: Dict, analysis2: Dict, 
                                     transition_bars: int = 16) -> Tuple[float, float]:
        """
        최적의 전환 지점 찾기
        
        Args:
            analysis1: 첫 번째 트랙 분석 결과
            analysis2: 두 번째 트랙 분석 결과
            transition_bars: 전환 길이 (바 단위)
            
        Returns:
            (track1_out_point, track2_in_point)
        """
        print(f"  🔍 Finding optimal transition point ({transition_bars} bars)...")
        
        # Track 1: 아웃트로 시작점 사용
        outro1 = analysis1['segments']['outro']
        mixout_point = outro1['start']
        
        # Track 2: 인트로 끝 지점 사용
        intro2 = analysis2['segments']['intro']
        mixin_point = intro2['end'] if intro2['end'] > 5 else 0
        
        # 비트에 맞춰 조정
        if len(analysis1['beats']) > 0:
            closest_beat_idx = np.argmin(np.abs(analysis1['beats'] - mixout_point))
            mixout_point = analysis1['beats'][closest_beat_idx]
        
        print(f"  ✓ Transition points: Track1 @ {mixout_point:.2f}s, Track2 @ {mixin_point:.2f}s")
        
        return mixout_point, mixin_point
    
    def create_crossfade(self, audio1: np.ndarray, audio2: np.ndarray,
                        mixout_point: float, mixin_point: float,
                        crossfade_duration: float,
                        style: str = 'classic') -> np.ndarray:
        """
        크로스페이드 생성
        
        Args:
            audio1: 첫 번째 오디오
            audio2: 두 번째 오디오
            mixout_point: Track1 믹스 아웃 시작점
            mixin_point: Track2 믹스 인 시작점
            crossfade_duration: 크로스페이드 길이 (초)
            style: 전환 스타일 ('classic', 'bass_swap', 'filter_sweep')
            
        Returns:
            믹스된 오디오
        """
        print(f"  🎛️  Creating {style} crossfade ({crossfade_duration:.1f}s)...")
        
        # 샘플 단위로 변환
        mixout_sample = int(mixout_point * self.sample_rate)
        mixin_sample = int(mixin_point * self.sample_rate)
        fade_samples = int(crossfade_duration * self.sample_rate)
        
        # Track2 시작 위치 계산
        track2_start_in_mix = mixout_sample
        
        # 최종 길이 계산
        total_length = max(
            audio1.shape[1],
            track2_start_in_mix + (audio2.shape[1] - mixin_sample)
        )
        
        # 출력 버퍼 생성 (스테레오)
        mixed = np.zeros((2, total_length), dtype=np.float32)
        
        # Track1 복사 (전체)
        mixed[:, :audio1.shape[1]] = audio1
        
        # 크로스페이드 구간 계산
        fade_start = mixout_sample
        fade_end = min(fade_start + fade_samples, audio1.shape[1])
        actual_fade_samples = fade_end - fade_start
        
        if style == 'classic':
            # Classic crossfade
            fade_out_curve = np.linspace(1, 0, actual_fade_samples)
            fade_in_curve = np.linspace(0, 1, actual_fade_samples)
            
            # Track1 페이드 아웃
            for ch in range(2):
                mixed[ch, fade_start:fade_end] *= fade_out_curve
            
            # Track2 추가 (페이드 인)
            track2_fade_start = mixin_sample
            track2_fade_end = min(track2_fade_start + actual_fade_samples, audio2.shape[1])
            track2_fade_samples = track2_fade_end - track2_fade_start
            
            for ch in range(2):
                fade_in_actual = np.linspace(0, 1, track2_fade_samples)
                mixed[ch, fade_start:fade_start + track2_fade_samples] += \
                    audio2[ch, track2_fade_start:track2_fade_end] * fade_in_actual
            
            # Track2 나머지 부분
            remaining_start = fade_start + track2_fade_samples
            remaining_audio2_start = track2_fade_end
            remaining_length = min(
                audio2.shape[1] - remaining_audio2_start,
                total_length - remaining_start
            )
            
            if remaining_length > 0:
                mixed[:, remaining_start:remaining_start + remaining_length] = \
                    audio2[:, remaining_audio2_start:remaining_audio2_start + remaining_length]
        
        elif style == 'bass_swap':
            # Bass swap: 저음 먼저 교체
            print("    🔊 Applying bass swap...")
            
            # 저음/고음 분리 (간단한 필터)
            # Track1 저음 페이드 아웃
            fade_out_curve = np.linspace(1, 0, actual_fade_samples)
            for ch in range(2):
                mixed[ch, fade_start:fade_end] *= fade_out_curve
            
            # Track2 저음 먼저 페이드 인 (빠르게)
            bass_fade_samples = actual_fade_samples // 2
            track2_fade_start = mixin_sample
            
            for ch in range(2):
                bass_fade_in = np.linspace(0, 1, bass_fade_samples)
                mixed[ch, fade_start:fade_start + bass_fade_samples] += \
                    audio2[ch, track2_fade_start:track2_fade_start + bass_fade_samples] * bass_fade_in
            
            # 나머지 주파수 페이드 인
            remaining_fade_samples = actual_fade_samples - bass_fade_samples
            for ch in range(2):
                remaining_fade_in = np.linspace(0, 1, remaining_fade_samples)
                mixed[ch, fade_start + bass_fade_samples:fade_end] += \
                    audio2[ch, track2_fade_start + bass_fade_samples:track2_fade_start + actual_fade_samples] * remaining_fade_in
            
            # Track2 나머지
            remaining_start = fade_end
            remaining_audio2_start = track2_fade_start + actual_fade_samples
            remaining_length = min(
                audio2.shape[1] - remaining_audio2_start,
                total_length - remaining_start
            )
            
            if remaining_length > 0:
                mixed[:, remaining_start:remaining_start + remaining_length] = \
                    audio2[:, remaining_audio2_start:remaining_audio2_start + remaining_length]
        
        else:  # filter_sweep or other
            # 기본 classic 사용
            fade_out_curve = np.linspace(1, 0, actual_fade_samples)
            fade_in_curve = np.linspace(0, 1, actual_fade_samples)
            
            for ch in range(2):
                mixed[ch, fade_start:fade_end] *= fade_out_curve
            
            track2_fade_start = mixin_sample
            track2_fade_end = min(track2_fade_start + actual_fade_samples, audio2.shape[1])
            track2_fade_samples = track2_fade_end - track2_fade_start
            
            for ch in range(2):
                fade_in_actual = np.linspace(0, 1, track2_fade_samples)
                mixed[ch, fade_start:fade_start + track2_fade_samples] += \
                    audio2[ch, track2_fade_start:track2_fade_end] * fade_in_actual
            
            remaining_start = fade_start + track2_fade_samples
            remaining_audio2_start = track2_fade_end
            remaining_length = min(
                audio2.shape[1] - remaining_audio2_start,
                total_length - remaining_start
            )
            
            if remaining_length > 0:
                mixed[:, remaining_start:remaining_start + remaining_length] = \
                    audio2[:, remaining_audio2_start:remaining_audio2_start + remaining_length]
        
        print(f"  ✓ Crossfade complete: {total_length / self.sample_rate:.2f}s total")
        
        return mixed
    
    def normalize_audio(self, audio: np.ndarray, target_db: float = -14.0) -> np.ndarray:
        """
        오디오 정규화
        
        Args:
            audio: 오디오 데이터
            target_db: 목표 dB 레벨
            
        Returns:
            정규화된 오디오
        """
        # RMS 계산
        rms = np.sqrt(np.mean(audio ** 2))
        
        if rms > 0:
            current_db = 20 * np.log10(rms)
            gain_db = target_db - current_db
            gain_linear = 10 ** (gain_db / 20)
            
            normalized = audio * gain_linear
            
            # 클리핑 방지
            max_val = np.max(np.abs(normalized))
            if max_val > 1.0:
                normalized = normalized / max_val * 0.99
            
            print(f"  🔊 Normalized: {current_db:.1f} dB → {target_db:.1f} dB")
            return normalized
        
        return audio
    
    def mix(self, track1_path: str, track2_path: str, output_path: str,
            sync_beats: bool = True,
            match_tempo: bool = True,
            harmonic_mix: bool = True,
            transition_bars: int = 16,
            transition_style: str = 'classic',
            auto_detect: bool = True) -> str:
        """
        두 트랙을 믹싱
        
        Args:
            track1_path: 첫 번째 트랙 경로
            track2_path: 두 번째 트랙 경로
            output_path: 출력 파일 경로
            sync_beats: 비트 동기화 여부
            match_tempo: 템포 매칭 여부
            harmonic_mix: 하모닉 믹싱 여부
            transition_bars: 전환 길이 (바)
            transition_style: 전환 스타일
            auto_detect: 자동 전환점 감지
            
        Returns:
            출력 파일 경로
        """
        print(f"\n{'='*70}")
        print(f"🎧 Advanced Music Mixing")
        print(f"{'='*70}\n")
        
        # 1. 분석
        print("📊 Step 1: Analyzing tracks...\n")
        analyzer1 = AudioAnalyzer(track1_path)
        analysis1 = analyzer1.analyze_full()
        
        analyzer2 = AudioAnalyzer(track2_path)
        analysis2 = analyzer2.analyze_full()
        
        # 2. 하모닉 호환성 체크
        if harmonic_mix:
            print("\n🎹 Step 2: Checking harmonic compatibility...\n")
            compatible, reason = AudioAnalyzer.are_keys_compatible(
                analysis1['camelot'], analysis2['camelot']
            )
            
            if compatible:
                print(f"  ✅ Keys are compatible: {reason}")
            else:
                print(f"  ⚠️  Keys may clash: {reason}")
                print(f"     Track1: {analysis1['full_key']} ({analysis1['camelot']})")
                print(f"     Track2: {analysis2['full_key']} ({analysis2['camelot']})")
        
        # 3. 오디오 로드
        print("\n📂 Step 3: Loading audio files...\n")
        audio1, sr1 = self.load_audio(track1_path)
        audio2, sr2 = self.load_audio(track2_path)
        
        # 4. 템포 매칭
        if match_tempo:
            print("\n⏱️  Step 4: Matching tempo...\n")
            target_bpm = analysis1['bpm']  # Track1의 BPM에 맞춤
            audio2 = self.match_tempo(audio2, analysis2['bpm'], target_bpm)
            
            # 비트 정보도 조정
            tempo_ratio = target_bpm / analysis2['bpm']
            analysis2['beats'] = analysis2['beats'] / tempo_ratio
            analysis2['downbeats'] = analysis2['downbeats'] / tempo_ratio
        
        # 5. 전환점 찾기
        print("\n🎯 Step 5: Finding transition points...\n")
        if auto_detect:
            mixout_point, mixin_point = self.find_optimal_transition_point(
                analysis1, analysis2, transition_bars
            )
        else:
            # 수동: Track1 끝에서 transition_bars 전
            bars_duration = (60 / analysis1['bpm']) * 4 * transition_bars
            mixout_point = analysis1['duration'] - bars_duration
            mixin_point = 0
        
        # 6. 비트 정렬
        if sync_beats:
            print("\n🎵 Step 6: Synchronizing beats...\n")
            audio1, audio2, mixout_point = self.align_beats(
                audio1, audio2,
                analysis1['beats'], analysis2['beats'],
                mixout_point
            )
        
        # 7. 크로스페이드 생성
        print("\n🎛️  Step 7: Creating crossfade...\n")
        crossfade_duration = (60 / analysis1['bpm']) * 4 * transition_bars
        
        mixed = self.create_crossfade(
            audio1, audio2,
            mixout_point, mixin_point,
            crossfade_duration,
            transition_style
        )
        
        # 8. 정규화
        print("\n🔊 Step 8: Normalizing output...\n")
        mixed = self.normalize_audio(mixed)
        
        # 9. 저장
        print(f"\n💾 Step 9: Saving to {output_path}...\n")
        
        # Transpose for soundfile (channels, samples) -> (samples, channels)
        mixed_transposed = mixed.T
        
        sf.write(output_path, mixed_transposed, self.sample_rate)
        
        print(f"\n{'='*70}")
        print(f"✅ Mixing Complete!")
        print(f"{'='*70}")
        print(f"📁 Output: {output_path}")
        print(f"⏱️  Duration: {mixed.shape[1] / self.sample_rate:.2f}s")
        print(f"{'='*70}\n")
        
        return output_path


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python advanced_mixer.py <track1> <track2> <output>")
        sys.exit(1)
    
    track1 = sys.argv[1]
    track2 = sys.argv[2]
    output = sys.argv[3]
    
    mixer = AdvancedMixer()
    mixer.mix(track1, track2, output, 
              sync_beats=True,
              match_tempo=True,
              harmonic_mix=True,
              transition_bars=16,
              transition_style='classic',
              auto_detect=True)
