#!/usr/bin/env python3
"""
Music Mixer Pro - Advanced DJ-Style Music Transition System
프로페셔널 음악 믹싱 CLI 애플리케이션
"""

import argparse
import sys
import json
from pathlib import Path
from audio_analyzer import AudioAnalyzer
from advanced_mixer import AdvancedMixer


def analyze_only(audio_path: str):
    """분석만 수행하고 결과 출력"""
    analyzer = AudioAnalyzer(audio_path)
    result = analyzer.analyze_full()
    
    print("\n" + "="*70)
    print("📋 ANALYSIS REPORT")
    print("="*70)
    print(f"\n📁 File: {result['file_path']}")
    print(f"⏱️  Duration: {result['duration']:.2f} seconds")
    print(f"\n🎵 TEMPO & RHYTHM")
    print(f"   BPM: {result['bpm']:.2f}")
    print(f"   Beats: {result['beat_count']}")
    print(f"   Downbeats: {len(result['downbeats'])}")
    print(f"\n🎹 KEY & HARMONY")
    print(f"   Key: {result['full_key']}")
    print(f"   Camelot: {result['camelot']}")
    print(f"\n⚡ ENERGY")
    print(f"   Average: {result['avg_energy']:.3f}")
    print(f"   Peak: {result['peak_energy']:.3f}")
    print(f"\n📊 SEGMENTS")
    for name, seg in result['segments'].items():
        duration = seg['end'] - seg['start']
        print(f"   {name.capitalize():10s}: {seg['start']:6.1f}s - {seg['end']:6.1f}s ({duration:5.1f}s)")
    print("="*70 + "\n")


def mix_tracks(args):
    """트랙 믹싱 수행"""
    mixer = AdvancedMixer()
    
    # 설정 로드 (config 파일이 있으면)
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        config = {}
    
    # CLI 인자가 config보다 우선
    sync_beats = args.sync_beats if args.sync_beats is not None else config.get('sync_beats', True)
    match_tempo = args.match_tempo if args.match_tempo is not None else config.get('match_tempo', True)
    harmonic_mix = args.harmonic_mix if args.harmonic_mix is not None else config.get('harmonic_mixing', True)
    transition_bars = args.transition_bars if args.transition_bars else config.get('transition_bars', 16)
    transition_style = args.style if args.style else config.get('transition_style', 'classic')
    auto_detect = args.auto if args.auto is not None else config.get('auto_detect_transition', True)
    
    # 확장 모드 확인
    if args.extend:
        from music_extender import MusicExtender
        extender = MusicExtender()
        output_path = extender.extend_track(
            args.track1, 
            args.output, 
            args.extend,
            transition_bars=transition_bars
        )
        return output_path
    
    # 믹싱 실행
    output_path = mixer.mix(
        args.track1,
        args.track2,
        args.output,
        sync_beats=sync_beats,
        match_tempo=match_tempo,
        harmonic_mix=harmonic_mix,
        transition_bars=transition_bars,
        transition_style=transition_style,
        auto_detect=auto_detect
    )
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='🎧 Music Mixer Pro - Advanced DJ-Style Music Transition System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 자동 모드 (모든 기능 활성화)
  python music_mixer_pro.py track1.mp3 track2.mp3 -o output.mp3 --auto
  
  # 비트 동기화 + 템포 매칭
  python music_mixer_pro.py track1.mp3 track2.mp3 -o output.mp3 --sync-beats --match-tempo
  
  # 하모닉 믹싱 (키 호환성 체크)
  python music_mixer_pro.py track1.mp3 track2.mp3 -o output.mp3 --harmonic-mix
  
  # 전환 스타일 지정
  python music_mixer_pro.py track1.mp3 track2.mp3 -o output.mp3 --style bass_swap
  
  # 분석만 수행
  python music_mixer_pro.py track1.mp3 --analyze-only
  
  # 설정 파일 사용
  python music_mixer_pro.py track1.mp3 track2.mp3 -o output.mp3 --config config.json

Transition Styles:
  - classic: 전통적인 크로스페이드
  - bass_swap: 저음을 먼저 교체
  - filter_sweep: 필터 스윕 효과 (개발 중)
        """
    )
    
    # 필수 인자
    parser.add_argument('track1', help='첫 번째 음악 파일')
    parser.add_argument('track2', nargs='?', help='두 번째 음악 파일 (분석 전용 모드에서는 불필요)')
    
    # 출력 옵션
    parser.add_argument('-o', '--output', help='출력 파일 경로')
    
    # 분석 전용 모드
    parser.add_argument('--analyze-only', action='store_true',
                       help='분석만 수행하고 믹싱하지 않음')
    
    # 믹싱 옵션
    parser.add_argument('--sync-beats', action='store_true', default=None,
                       help='비트 동기화 활성화')
    parser.add_argument('--match-tempo', action='store_true', default=None,
                       help='템포 매칭 활성화 (time-stretching)')
    parser.add_argument('--harmonic-mix', action='store_true', default=None,
                       help='하모닉 믹싱 활성화 (키 호환성 체크)')
    parser.add_argument('--auto', action='store_true', default=None,
                       help='자동 모드 (모든 기능 활성화)')
    
    # 전환 설정
    parser.add_argument('--transition-bars', type=int, default=None,
                       help='전환 길이 (바 단위, 기본: 16)')
    parser.add_argument('--style', choices=['classic', 'bass_swap', 'filter_sweep'],
                       help='전환 스타일 (기본: classic)')
                       
    # 확장 옵션
    parser.add_argument('--extend', help='트랙 확장 모드 (예: 30m, 1h)')
    
    # 설정 파일
    parser.add_argument('--config', help='JSON 설정 파일 경로')
    
    args = parser.parse_args()
    
    # 분석 전용 모드
    if args.analyze_only:
        analyze_only(args.track1)
        return
    
    # 믹싱 모드 - 필수 인자 체크
    if not args.track2 and not args.extend:
        parser.error("믹싱 모드에서는 track2가 필요합니다. 분석만 하려면 --analyze-only를 사용하세요.")
    
    if not args.output:
        parser.error("출력 파일 경로(-o/--output)가 필요합니다.")
    
    # 자동 모드
    if args.auto:
        args.sync_beats = True
        args.match_tempo = True
        args.harmonic_mix = True
    
    # 믹싱 실행
    try:
        output_path = mix_tracks(args)
        print(f"\n🎉 Success! Mixed track saved to: {output_path}\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
