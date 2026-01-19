"""
Music Extender
한 곡을 자연스럽게 반복하여 길이를 확장하는 모듈
"""

import numpy as np
import librosa
import soundfile as sf
import os
import moviepy.editor as mp
from audio_analyzer import AudioAnalyzer
from advanced_mixer import AdvancedMixer


class MusicExtender:
    """음악 및 비디오 확장 클래스"""
    
    def __init__(self):
        self.mixer = AdvancedMixer()
    
    def parse_duration(self, duration_str: str) -> float:
        """
        시간 문자열을 초 단위로 변환
        예: '30m' -> 1800.0, '1h' -> 3600.0, '300s' -> 300.0
        """
        duration_str = duration_str.lower()
        if duration_str.endswith('m'):
            return float(duration_str[:-1]) * 60
        elif duration_str.endswith('h'):
            return float(duration_str[:-1]) * 3600
        elif duration_str.endswith('s'):
            return float(duration_str[:-1])
        else:
            return float(duration_str)
            
    def extend_track(self, input_path: str, output_path: str, 
                     target_duration_str: str, 
                     transition_bars: int = 16) -> str:
        """
        트랙(오디오, 비디오 또는 이미지)을 목표 시간까지 반복 확장
        """
        lower_path = input_path.lower()
        is_video = lower_path.endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm'))
        is_image = lower_path.endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp'))
        is_media = is_video or is_image
        
        video_temp_audio = "temp_video_audio.wav"
        
        # 미디어인 경우 오디오 추출 (이미지는 오디오 없음)
        actual_input = input_path
        if is_video:
            print("🎬 Video detected. Extracting audio for processing...")
            video = mp.VideoFileClip(input_path)
            video.audio.write_audiofile(video_temp_audio, logger=None)
            actual_input = video_temp_audio
        elif is_image:
            print("🖼️ Image detected. Processing as a static background...")
            # 이미지는 오디오가 없으므로 사용자가 이전에 업로드한 오디오가 필요하지만,
            # 현재 구조상 '이미지 + 오디오' 동시 업로드 기능이 아니므로 
            # 여기서는 분석할 오디오가 필요함. 
            # 만약 이미지만 넣었다면 에러가 날 것이므로 backend에서 방어해야함.
            pass

        target_duration = self.parse_duration(target_duration_str)
        
        print(f"\n{'='*70}")
        print(f"🔄 Media Extender: Extending to {target_duration_str}")
        print(f"{'='*70}\n")
        
        # 1. 분석 (이미지인 경우 오디오 분석 불가하므로 처리 필요)
        print("📊 Analyzing track...")
        analyzer = AudioAnalyzer(actual_input)
        analysis = analyzer.analyze_full()
        
        # 2. 오디오 로드
        print("\n📂 Loading audio...")
        audio, sr = self.mixer.load_audio(input_path)
        original_duration = analysis['duration']
        
        # 3. 반복 횟수 계산
        # 실제 루프되는 길이 = 전체 길이 - 믹스아웃 포인트 + 믹스인 포인트 (대략)
        # 정확히는 (Original Len - Transition Len) * N + Transition Len
        # 하지만 transition point가 유동적이므로 단순화해서 계산
        
        # Outro start -> Intro end 연결
        # 최적 전환 찾기 (자기 자신과 믹싱하므로 analysis1=analysis2)
        mixout_point, mixin_point = self.mixer.find_optimal_transition_point(
            analysis, analysis, transition_bars
        )
        
        # 비트 정렬 (Mixin 포인트를 비트에 맞춤)
        # 자기 자신과 믹싱하므로 BPM 매칭 불필요
        
        # 유효 루프 길이 (한 번 반복될 때 추가되는 시간)
        loop_length_seconds = mixout_point - mixin_point
        if loop_length_seconds <= 0:
             # 루프 길이가 0보다 작으면 전체 길이 사용 (fallback)
             loop_length_seconds = original_duration * 0.8 
             mixout_point = original_duration * 0.9
             mixin_point = original_duration * 0.1
             
        required_loops = int(np.ceil((target_duration - mixin_point) / loop_length_seconds))
        
        print(f"\nTarget: {target_duration:.1f}s")
        print(f"Loop Length: {loop_length_seconds:.2f}s (Mixout: {mixout_point:.1f}s → Mixin: {mixin_point:.1f}s)")
        print(f"Required loops: {required_loops}")
        
        if required_loops <= 1:
            print("⚠️  Target duration is shorter than original. Copying original.")
            sf.write(output_path, audio.T, sr)
            return output_path
            
        # 4. 루프 생성
        print(f"\n🔨 Building extended track ({required_loops} iterations)...")
        
        # 첫 번째 블록 (처음 ~ 믹스아웃)
        # 실제로는 크로스페이드를 위해 끝까지 필요할 수 있음
        # 메모리 효율을 위해 전체를 한 번에 빌드하지 않고, 점진적으로 추가
        
        current_audio = audio
        
        # 진행 상황 표시를 위해
        import sys
        
        for i in range(required_loops - 1):
            sys.stdout.write(f"\r  Progress: {i+1}/{required_loops-1} loops mixed")
            sys.stdout.flush()
            
            # current_audio의 끝부분(Outro)과 audio의 앞부분(Intro)을 믹싱
            
            # 비트 정렬 및 크로스페이드
            # align_beats 함수는 audio2를 이동시키거나 자르는데, 여기서는 audio2(원본)의 시작점을 맞춤
            
            # 믹스아웃 포인트는 current_audio 기준 (끝에서 loop_length 만큼 전이 아니라, 분석된 지점)
            # 하지만 current_audio는 계속 길어지므로, 매번 길이를 재계산해서 상대 위치를 찾아야 함
            # 첫 번째 루프: mixout_point
            # 두 번째 루프: mixout_point + loop_length
            # ...
            
            # 단순화를 위해:
            # 1. Base Audio 생성 (반복 횟수만큼)
            # 2. 각 접합부에서 Crossfade 적용
            pass
            
        # 메모리 문제 방지를 위해 전략 수정:
        # Crossfade부분만 계산하고, 나머지는 그대로 붙임
        
        # [Intro ... Body ... MixOutStart]  +  [MixInStart ... Body ... Outro]
        #                    \ Crossfade /
        
        # Part A: Start to MixOut
        part_a = audio[:, :int(mixout_point * sr)]
        
        # Part B: MixIn to End
        part_b = audio[:, int(mixin_point * sr):]
        
        # Crossfade Region Calculation
        # 두 오디오를 겹칠 길이
        crossfade_duration = (60 / analysis['bpm']) * 4 * transition_bars
        crossfade_samples = int(crossfade_duration * sr)
        
        # 실제 믹싱 로직
        # 1. 첫 번째 파트 준비
        final_audio_parts = [audio[:, :int(mixout_point * sr)]]
        current_length = final_audio_parts[0].shape[1]
        
        # 2. 루프 추가
        # 여기서 '정교한' 믹싱을 하려면 AdvancedMixer.create_crossfade를 써야 하는데
        # 구조상 약간 복잡함. 직접 구현:
        
        # 루프의 핵심은: [End of Prev]와 [Start of Next]를 겹치는 것
        # Prev: ... [FadeOut Region] ...
        # Next: [FadeIn Region] ...
        
        # 간단한 접근:
        # 1. Main Body: (Mixin Point + Crossfade/2) ~ (Mixout Point - Crossfade/2)
        # 2. Transition Block: (Mixout - Crossfade/2) + (Mixin - Crossfade/2) -> Mixed
        
        # 더 간단한 접근 (DJ 스타일):
        # Base Loop: audio[Mixin_Point : Mixout_Point] (중간 몸통)
        # 하지만 이렇게 하면 Intro/Outro가 사라짐.
        
        # Intro(0~Mixin) + [Body(Mixin~Mixout) * N] + Outro(Mixout~End)
        # 문제는 Body와 Body 사이, Intro-Body 사이의 연결이 매끄러워야 함.
        
        # 해결책:
        # Recursive approach using mixer.create_crossfade is memory intensive for long files.
        # But for MVP (30 mins), 300MB ~ 600MB RAM is okay.
        
        full_mix = audio
        
        for i in range(required_loops - 1):
            sys.stdout.write(f"\r  Progress: {i+1}/{required_loops-1}")
            sys.stdout.flush()
            
            # 현재 믹스의 끝부분과 원본의 앞부분을 믹싱
            # current_mixout = current_length - (original_duration - mixout_point)
            # 너무 복잡함.
            
            # "Append with Crossfade" 방식
            # Prev Track의 Mixout Point 지점부터 Next Track의 Mixin Point 지점을 겹침
            
            # 1. Prev Track의 믹스아웃 지점 계산 (마지막 섹션)
            # Prev Track의 길이는 계속 변함.
            # 하지만 믹싱 포인트는 항상 '끝에서 (Duration - MixoutPoint) 초 전'임.
            
            time_from_end = original_duration - mixout_point
            current_mixout_index = full_mix.shape[1] - int(time_from_end * sr)
            
            # 2. Next Track (Original)의 믹스인 지점
            next_mixin_index = int(mixin_point * sr)
            
            # 3. 겹치는 구간 (Crossfade length)
            # mixout_point부터 crossfade_duration 만큼
            
            # 비트 정렬 (이미 같은 곡이라 BPM 같음, 위상만 맞추면 됨)
            # align_beats 로직 재사용
            
            # 잘라내기 및 붙이기
            # Prev: [Start ............ Mixout] (Fade Out)
            # Next:           [Mixin ............ End] (Fade In)
            
            # A: Prev before fade
            # B: Mixed part
            # C: Next after fade
            
            fade_start_idx = current_mixout_index
            fade_end_idx = fade_start_idx + crossfade_samples
            
            # Next track starts at: fade_start_idx corresponds to mixin_point in Next Track
            # But we need to align beats.
            
            # Beat alignment logic simplified for same track:
            # Just ensure we cut exactly at beats?
            # Let's trust mixout/mixin points provided by find_optimal_transition_point which aligns to beats.
            
            # Prev Track을 fade_start_idx + crossfade_samples 까지만 유지 (나머지 버림)
            prev_keep = full_mix[:, :fade_end_idx]
            if prev_keep.shape[1] < fade_end_idx:
                # Pad if needed (shouldn't happen if mixout point is valid)
                pass
                
            # Next Track (Original) 준비
            # mixin_point부터 시작하되, crossfade_samples 만큼은 겹침
            next_start_idx = int(mixin_point * sr)
            next_audio = audio[:, next_start_idx:]
            
            # Crossfade 적용
            # 겹치는 부분: prev_keep[-crossfade_samples:] 과 next_audio[:crossfade_samples]
            
            # Create curves
            fade_out = np.linspace(1, 0, crossfade_samples)
            fade_in = np.linspace(0, 1, crossfade_samples)
            
            # Overlap Area
            overlap_prev = prev_keep[:, -crossfade_samples:]
            overlap_next = next_audio[:, :crossfade_samples]
            
            # Mix overlap
            overlap_mixed = (overlap_prev * fade_out) + (overlap_next * fade_in)
            
            # Concat: [Prev Body] + [Overlap Mixed] + [Next Body]
            prev_body = prev_keep[:, :-crossfade_samples]
            next_body = next_audio[:, crossfade_samples:]
            
            # Combine
            full_mix = np.concatenate([prev_body, overlap_mixed, next_body], axis=1)
            
            # Stop if duration reached
            if full_mix.shape[1] / sr >= target_duration:
                break
                
        print(f"\n✅ Extended logic complete. Final duration: {full_mix.shape[1]/sr:.1f}s")
        
        # Normalize
        full_mix = self.mixer.normalize_audio(full_mix)
        
        # Save Audio
        audio_output = output_path if not is_media else "temp_extended_audio.wav"
        sf.write(audio_output, full_mix.T, sr)
        print(f"💾 Saved audio to {audio_output}")
        
        # 6. 미디어 처리 (비디오 또는 이미지)
        if is_media:
            audio_clip = mp.AudioFileClip(audio_output)
            
            if is_video:
                print("\n🎬 Looping video to match audio duration (Lofi-style/Seamless)...")
                video_clip = mp.VideoFileClip(input_path)
                
                # 오디오 루프 포인트에 맞춰 비디오 조각(Clip) 생성
                clips = []
                part_a = video_clip.subclip(0, mixout_point)
                clips.append(part_a)
                
                body_segment = video_clip.subclip(mixin_point, mixout_point)
                for _ in range(required_loops - 1):
                    clips.append(body_segment)
                    
                part_c = video_clip.subclip(mixin_point, video_clip.duration)
                clips.append(part_c)
                
                final_video = mp.concatenate_videoclips(clips, method="compose")
                final_video = final_video.set_duration(audio_clip.duration)
                for c in clips: c.close()
                video_clip.close()
            
            elif is_image:
                print("\n🖼️ Creating static video from image...")
                final_video = mp.ImageClip(input_path).set_duration(audio_clip.duration)
            
            final_video = final_video.set_audio(audio_clip)
            
            print(f"📦 Writing final media: {output_path}")
            final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", bitrate="5000k", logger=None)
            
            # Cleanup
            audio_clip.close()
            if os.path.exists(video_temp_audio): os.path.unlink(video_temp_audio)
            if os.path.exists("temp_extended_audio.wav"): os.path.unlink("temp_extended_audio.wav")
            
        return output_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python music_extender.py <input> <output> <duration>")
        sys.exit(1)
        
    extender = MusicExtender()
    extender.extend_track(sys.argv[1], sys.argv[2], sys.argv[3])
