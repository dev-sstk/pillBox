# WAV 파일 재생 테스트 가이드

> **⚠️ 중요**: 이 가이드는 작업자가 단계별로 따라할 수 있도록 작성되었습니다. 각 단계를 순서대로 진행하세요.

## 📋 목차
1. [준비사항 확인](#준비사항-확인)
2. [하드웨어 연결](#하드웨어-연결)
3. [테스트 파일 업로드](#테스트-파일-업로드)
4. [테스트 실행](#테스트-실행)
5. [문제 해결](#문제-해결)
6. [완료 체크리스트](#완료-체크리스트)

---

## 🎯 준비사항 확인

### ✅ 필요한 하드웨어
- [ ] ESP32-C6 기반 PCB
- [ ] MAX98357A 오디오 앰프 연결된 PCB
- [ ] 스피커 (8Ω, 1W 이상 권장)
- [ ] USB 케이블
- [ ] 컴퓨터 (Windows 10/11)

### ✅ 필요한 소프트웨어
- [ ] Python 3.8 이상
- [ ] esptool, ampy 설치 완료
- [ ] PuTTY 설치 완료
- [ ] 최신 펌웨어 업로드 완료

### 📦 테스트 대상
- **MAX98357A** I2S 오디오 앰프
- **ESP32-C6** I2S 인터페이스
- **WAV 파일** (실제 음성 메시지)
- **스피커** (8Ω, 1W 이상 권장)

### 🎵 지원 WAV 파일
- **refill_mode_selected_bomin.wav**: 리필모드 선택 안내
- **refill_mode_selected_bomin_compressed.wav**: 압축된 버전

### 📊 WAV 파일 사양
- **포맷**: WAV (RIFF)
- **채널**: 모노 (1채널)
- **비트 깊이**: 16비트
- **샘플레이트**: 16kHz (자동 감지)
- **인코딩**: PCM

---

## 🔌 하드웨어 연결

### MAX98357A I2S 연결
```
ESP32-C6          MAX98357A
GPIO6 (BCLK)  →   BCLK (Bit Clock)
GPIO5 (DIN)   →   DIN (Data Input)
GPIO7 (LRCLK) →   LRCLK (Left/Right Clock)
3.3V          →   VDD
GND           →   GND

MAX98357A     →   스피커
OUT+          →   스피커 +
OUT-          →   스피커 -
```

### I2S 설정
- **모드**: I2S.TX (송신)
- **비트 깊이**: 16비트
- **포맷**: I2S.MONO (모노)
- **샘플레이트**: 16kHz (WAV 파일에서 자동 감지)
- **버퍼 크기**: 8192바이트 (큰 버퍼 우선)

## 📁 테스트 스크립트

### `test_wav_player_mono.py`
- **기능**: 모노 WAV 파일 재생
- **특징**: I2S 인터페이스 사용, 자동 파일 정보 감지
- **사용법**: 대화형 파일 선택 메뉴

### 주요 기능
1. **파일 선택**: 대화형 메뉴에서 WAV 파일 선택
2. **자동 감지**: WAV 파일 헤더에서 샘플레이트, 채널, 비트 깊이 자동 감지
3. **연속 재생**: 파일 끝에 도달하면 자동으로 다시 시작
4. **오류 처리**: I2S 초기화 실패 시 다양한 버퍼 크기로 재시도

---

## 📤 테스트 파일 업로드

### 1단계: 테스트 파일 업로드

1. **명령 프롬프트 열기**
   - Windows 키 + R → `cmd` 입력 → Enter

2. **프로젝트 폴더로 이동**
   ```cmd
   cd C:\Users\outrobot\OneDrive\사업\아웃로봇\신성테크\소스코드_전달\pillBox
   ```

3. **테스트 파일 업로드**
   ```cmd
   ampy -p COM3 put .\tests\test_wav_player_mono.py
   ampy -p COM3 put .\src\wav\refill_mode_selected_bomin.wav
   ampy -p COM3 put .\src\wav\refill_mode_selected_bomin_compressed.wav
   ```

   **⚠️ 중요**: `COM3`을 실제 COM 포트 번호로 변경하세요!

---

## 🧪 테스트 실행

### 1단계: PuTTY 연결

1. **PuTTY 실행**
   - PuTTY 실행 → Load → Open

2. **연결 확인**
   - MicroPython 프롬프트(`>>>`)가 나타나면 성공

### 2단계: 테스트 실행

1. **테스트 모듈 임포트 및 실행**
   ```python
   from test_wav_player_mono import main
   main()
   ```

### 3. 테스트 메뉴
```
🎵 재생할 WAV 파일을 선택하세요:
   1. refill_mode_selected_bomin.wav
   2. refill_mode_selected_bomin_compressed.wav

선택 (1-2): 
```

### 4. 테스트 결과 예시

#### 성공적인 재생
```
✅ 선택된 파일: refill_mode_selected_bomin.wav
📁 WAV 파일 정보:
   샘플레이트: 16000Hz
   채널: 1 (모노)
   비트: 16bit
✅ I2S 초기화 성공 (큰 버퍼, 16000Hz, 16bit)
🎵 모노 WAV 파일 재생 시작: refill_mode_selected_bomin.wav
🎵 재생 시작... (프레임 크기: 2바이트)
🎵 재생 루프 시작...
🔄 파일 재생 완료, 다시 시작...
```

#### I2S 초기화 실패 시
```
❌ I2S 초기화 실패 (큰 버퍼): [오류 메시지]
✅ I2S 초기화 성공 (중간 버퍼, 16000Hz, 16bit)
```

이 가이드를 따라 WAV 파일 재생 기능을 정확히 테스트할 수 있습니다.
