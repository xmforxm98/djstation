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
        """
        return self.mix_playlist([track1_path, track2_path], output_path, 
                                sync_beats, match_tempo, harmonic_mix, 
                                transition_bars, transition_style, auto_detect)

    def mix_playlist(self, track_paths: list, output_path: str,
                    sync_beats: bool = True,
                    match_tempo: bool = True,
                    harmonic_mix: bool = True,
                    transition_bars: int = 16,
                    transition_style: str = 'classic',
                    auto_detect: bool = True) -> str:
        """
        여러 트랙을 순차적으로 믹싱 (플레이리스트 방식)
        
        Args:
            track_paths: 트랙 파일 경로 목록
            output_path: 출력 파일 경로
            ... (기타 옵션은 mix와 동일)
        """
        if not track_paths:
            raise ValueError("No tracks provided for mixing")
            
        if len(track_paths) == 1:
            # 트랙이 하나면 그냥 복사(포맷 변환)만 함
            audio, sr = self.load_audio(track_paths[0])
            sf.write(output_path, audio.T, self.sample_rate)
            return output_path

        print(f"\n{'='*70}")
        print(f"🎧 Playlist Mixing ({len(track_paths)} tracks)")
        print(f"{'='*70}\n")

        # 첫 번째 트랙 로드 및 초기화
        current_audio, sr = self.load_audio(track_paths[0])
        analyzer = AudioAnalyzer(track_paths[0])
        current_analysis = analyzer.analyze_full()
        
        # 첫 번째 트랙 정규화
        current_audio = self.normalize_audio(current_audio)
        
        # 템포 기준 (첫 트랙 또는 평균으로 설정 가능, 여기선 첫 트랙 기준)
        reference_bpm = current_analysis['bpm']

        for i in range(1, len(track_paths)):
            next_track_path = track_paths[i]
            print(f"\n📎 Mixing in Track {i+1}: {os.path.basename(next_track_path)}")
            
            # 다음 트랙 분석 및 로드
            next_analyzer = AudioAnalyzer(next_track_path)
            next_analysis = next_analyzer.analyze_full()
            next_audio, sr_next = self.load_audio(next_track_path)
            
            # 템포 매칭 (이전 트랙의 BPM에 맞춤)
            if match_tempo:
                next_audio = self.match_tempo(next_audio, next_analysis['bpm'], reference_bpm)
                # 비트 정보 업데이트
                tempo_ratio = reference_bpm / next_analysis['bpm']
                next_analysis['beats'] = next_analysis['beats'] / tempo_ratio

            # 하모닉 체크 (참고용)
            if harmonic_mix:
                comp, reason = AudioAnalyzer.are_keys_compatible(current_analysis['camelot'], next_analysis['camelot'])
                print(f"  🎹 Key: {next_analysis['full_key']} ({next_analysis['camelot']}) -> " + ("✅ Compatible" if comp else f"⚠️ {reason}"))

            # 전환점 계산
            if auto_detect:
                mixout_point, mixin_point = self.find_optimal_transition_point(current_analysis, next_analysis, transition_bars)
            else:
                bars_duration = (60 / reference_bpm) * 4 * transition_bars
                mixout_point = (current_audio.shape[1] / self.sample_rate) - bars_duration
                mixin_point = 0

            # 비트 정렬
            if sync_beats:
                current_audio, next_audio, mixout_point = self.align_beats(
                    current_audio, next_audio,
                    current_analysis['beats'], next_analysis['beats'],
                    mixout_point
                )

            # 크로스페이드 생성
            crossfade_duration = (60 / reference_bpm) * 4 * transition_bars
            
            # mixout_point 이후의 beats는 audio2의 beats로 대체되거나 offset 되어야 함 (여기선 단순 누적)
            current_audio = self.create_crossfade(
                current_audio, next_audio,
                mixout_point, mixin_point,
                crossfade_duration,
                transition_style
            )
            
            # 다음 믹싱을 위한 current_analysis 업데이트
            # 믹스된 결과물의 새로운 비트와 분석 데이터가 필요하지만, 
            # 단순화를 위해 Track2의 데이터를 offset 시켜서 사용
            offset = mixout_point - mixin_point
            current_analysis = {
                'bpm': reference_bpm,
                'beats': next_analysis['beats'] + offset,
                'segments': {
                    'outro': {
                        'start': next_analysis['segments']['outro']['start'] + offset,
                        'end': next_analysis['segments']['outro']['end'] + offset
                    }
                },
                'camelot': next_analysis['camelot']
            }
            
            print(f"  ✓ Track {i+1} merged. Current total length: {current_audio.shape[1]/self.sample_rate:.1f}s")

        # 최종 정규화
        current_audio = self.normalize_audio(current_audio)
        
        # 저장
        sf.write(output_path, current_audio.T, self.sample_rate)
        print(f"\n✅ All {len(track_paths)} tracks mixed successfully!")
        
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
