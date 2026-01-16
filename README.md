# 🎧 Music Mixer Pro

전문가 수준의 자동 음악 믹싱 시스템입니다. 두 음악 파일 간의 **비트(Beat)**, **템포(BPM)**, **키(Key)**, **에너지(Energy)**를 분석하여 DJ처럼 자연스럽게 연결해줍니다.

## ✨ 주요 기능

- **🎛️ Beat Synchronization**: 두 곡의 비트 그릴드를 완벽하게 정렬하여 박자가 어긋나지 않는 전환
- **⏱️ Tempo Matching**: BPM이 다른 곡들도 음정 변화 없이(Time-stretching) 자연스럽게 속도 매칭
- **🎹 Harmonic Mixing**: 곡의 키(Key)를 분석하고 Camelot Wheel 알고리즘으로 화성학적 호환성 체크
- **🤖 Intelligent Transition**: 곡의 빌드업, 드롭, 아웃트로를 감지하여 최적의 믹스 포인트 자동 결정
- **🔊 Smart Audio Processing**: 볼륨 정규화 및 다양한 크로스페이드 스타일 지원

## 🚀 설치 방법

### 1. 시스템 요구사항
이 프로그램은 고급 오디오 처리를 위해 `ffmpeg`과 `rubberband` 라이브러리가 필요합니다.

**macOS (Homebrew 사용):**
```bash
brew install ffmpeg rubberband
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg rubberband-cli
```

### 2. Python 패키지 설치
```bash
pip install -r requirements.txt
```

## 🎮 사용 방법

### 기본 사용법 (자동 모드)
가장 추천하는 방식입니다. 모든 분석 및 매칭 기능을 자동으로 수행합니다.
```bash
python music_mixer_pro.py track1.mp3 track2.mp3 -o output.mp3 --auto
```

### 상세 옵션 사용
원하는 기능만 선택하여 사용할 수 있습니다.
```bash
python music_mixer_pro.py track1.mp3 track2.mp3 -o output.mp3 \
    --sync-beats      # 비트 동기화
    --match-tempo     # 템포 매칭
    --harmonic-mix    # 키 호환성 체크 (경고 표시)
    --transition-bars 32  # 32마디 동안 전환 (길게)
    --style bass_swap # 베이스 스왑 스타일 사용
```

### 오디오 분석만 수행
믹싱하지 않고 음악 파일의 상세 정보를 분석합니다.
```bash
python music_mixer_pro.py track1.mp3 --analyze-only
```

### 설정 파일 사용
자주 사용하는 설정을 JSON 파일로 저장해두고 사용할 수 있습니다.
```bash
python music_mixer_pro.py track1.mp3 track2.mp3 -o output.mp3 --config mix_config.json
```

## 🧠 기술적 상세

### 지원되는 파일 형식
- MP3, WAV, FLAC, OGG, M4A 등 `ffmpeg`이 지원하는 대부분의 포맷

### 전환 스타일
1. **Classic**: 전통적인 볼륨 크로스페이드. 비트가 맞는 상태에서 부드럽게 전환됩니다.
2. **Bass Swap**: 저음역대 충돌을 방지하기 위해 베이스라인을 빠르게 교체하고 나머지를 천천히 블렌딩합니다. (EDM/House 믹싱에 적합)

### 하모닉 믹싱 가이드
프로그램은 **Camelot Wheel** 표기법(예: 8A, 9B)을 사용하여 키 호환성을 알려줍니다.
- **완벽 호환**: 같은 숫자 (예: 8A → 8A)
- **에너지 변화**: 숫자 ±1 (예: 8A → 9A, 8A → 7A)
- **무드 변화**: 같은 숫자, 다른 문자 (예: 8A → 8B)

## ⚠️ 주의사항
- **BPM 차이**: 두 곡의 BPM 차이가 너무 크면(예: 20% 이상) 템포 매칭 시 오디오 품질이 저하될 수 있습니다.
- **비트그리드**: 복잡한 박자나 비트가 불명확한 앰비언트 음악은 비트 감지가 부정확할 수 있습니다.
