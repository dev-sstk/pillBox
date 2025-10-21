# 펌웨어 업로드 가이드

> **ESP32-C6 필박스 펌웨어 업로드 방법**

## 📋 개요

ESP32-C6 기반 필박스 시스템에 소스코드를 업로드하는 방법을 설명합니다. `mpremote` 도구를 사용하여 MicroPython 파일을 ESP32-C6에 전송합니다.

## 🔧 사전 준비

### 1. mpremote 설치
```bash
pip install mpremote
```

### 2. build_and_upload.py 사용 (권장)
```bash
python build_and_upload.py
```

### 3. ESP32-C6 연결 확인
- USB 케이블로 ESP32-C6을 PC에 연결
- 장치 관리자에서 COM 포트 확인 (예: COM4)
- ESP32-C6이 정상적으로 인식되는지 확인

### 4. MicroPython 펌웨어 확인
- ESP32-C6에 MicroPython 펌웨어가 설치되어 있는지 확인
- 터미널에서 ESP32-C6에 접속 가능한지 확인

## 🚀 업로드 방법

### 방법 1: build_and_upload.py 사용 (권장)

#### 자동 빌드 및 업로드
```bash
python build_and_upload.py
```

**메뉴 선택:**
- `1`: Python 파일을 mpy로 빌드 후 업로드 (권장)
- `2`: Python 파일을 그대로 업로드
- `4`: 개별 파일 빌드 후 업로드

### 방법 2: 수동 mpremote 사용

#### 메인 파일 업로드
```bash
mpremote connect COM4 cp src/main.py /main.py
```

#### 화면 파일 업로드
```bash
# 스타트업 화면
mpremote connect COM4 cp src/screens/startup_screen.py /screens/startup_screen.py

# Wi-Fi 스캔 화면
mpremote connect COM4 cp src/screens/wifi_scan_screen.py /screens/wifi_scan_screen.py

# Wi-Fi 비밀번호 화면
mpremote connect COM4 cp src/screens/wifi_password_screen.py /screens/wifi_password_screen.py

# 복용 시간 설정 화면
mpremote connect COM4 cp src/screens/dose_time_screen.py /screens/dose_time_screen.py

# 알약 로딩 화면
mpremote connect COM4 cp src/screens/pill_loading_screen.py /screens/pill_loading_screen.py

# 메인 화면
mpremote connect COM4 cp src/screens/main_screen.py /screens/main_screen.py

# 복용시간선택 화면
mpremote connect COM4 cp src/screens/meal_time_screen.py /screens/meal_time_screen.py

# 디스크 선택 화면
mpremote connect COM4 cp src/screens/disk_selection_screen.py /screens/disk_selection_screen.py
```

#### 핵심 모듈 업로드
```bash
# 화면 관리자
mpremote connect COM4 cp src/screen_manager.py /screen_manager.py

# UI 스타일
mpremote connect COM4 cp src/ui_style.py /ui_style.py

# LVGL 유틸리티
mpremote connect COM4 cp src/lv_utils.py /lv_utils.py

# 디스플레이 드라이버
mpremote connect COM4 cp src/st77xx.py /st77xx.py

# 버튼 인터페이스
mpremote connect COM4 cp src/button_interface.py /button_interface.py

# 모터 제어
mpremote connect COM4 cp src/motor_control.py /motor_control.py

# Wi-Fi 관리
mpremote connect COM4 cp src/wifi_manager.py /wifi_manager.py

# 오디오 시스템
mpremote connect COM4 cp src/audio_system.py /audio_system.py
mpremote connect COM4 cp src/audio_files_info.py /audio_files_info.py

# 데이터 관리
mpremote connect COM4 cp src/data_manager.py /data_manager.py
```

### 3. 오디오 파일 업로드

#### WAV 파일 업로드
```bash
# 오디오 파일 디렉토리 생성
mpremote connect COM4 fs mkdir /wav

# WAV 파일들 업로드
mpremote connect COM4 cp src/wav/wav_alarm.wav /wav/wav_alarm.wav
mpremote connect COM4 cp src/wav/wav_select.wav /wav/wav_select.wav
mpremote connect COM4 cp src/wav/wav_adjust.wav /wav/wav_adjust.wav
mpremote connect COM4 cp src/wav/refill_mode_selected_bomin.wav /wav/refill_mode_selected_bomin.wav
mpremote connect COM4 cp src/wav/refill_mode_selected_bomin_compressed.wav /wav/refill_mode_selected_bomin_compressed.wav
```

## 📁 디렉토리 구조

### ESP32-C6 내부 구조
```
/
├── main.py                    # 메인 실행 파일
├── screen_manager.py          # 화면 관리자
├── ui_style.py               # UI 스타일
├── lv_utils.py               # LVGL 유틸리티
├── st77xx.py                 # 디스플레이 드라이버
├── button_interface.py       # 버튼 인터페이스
├── motor_control.py          # 모터 제어
├── wifi_manager.py           # Wi-Fi 관리
├── audio_system.py           # 오디오 시스템
├── audio_files_info.py       # 오디오 파일 정보
├── screens/                  # 화면 모듈들
│   ├── startup_screen.py
│   ├── wifi_scan_screen.py
│   ├── wifi_password_screen.py
│   ├── dose_time_screen.py
│   ├── pill_loading_screen.py
│   ├── main_screen.py
│   ├── meal_time_screen.py
│   └── disk_selection_screen.py
└── wav/                      # 오디오 파일들
    ├── wav_alarm.wav
    ├── wav_select.wav
    ├── wav_adjust.wav
    └── refill_mode_selected_bomin.wav
```

## ⚠️ 주의사항

### 1. COM 포트 확인
- ESP32-C6 연결 시 COM 포트 번호가 변경될 수 있음
- 장치 관리자에서 정확한 포트 번호 확인 필요

### 2. 파일 크기 제한
- ESP32-C6의 플래시 메모리 용량 확인
- 큰 파일(오디오) 업로드 시 메모리 부족 주의

### 3. 업로드 순서
- 의존성이 있는 파일은 순서대로 업로드
- `main.py`는 마지막에 업로드하는 것을 권장

### 4. 오류 처리
- 업로드 실패 시 ESP32-C6 재부팅 후 재시도
- 파일이 손상된 경우 전체 재업로드

### 파일 목록 확인
```bash
ampy -p COM4 ls
ampy -p COM4 ls screens/
ampy -p COM4 ls wav/
```

### 파일 내용 확인
```bash
ampy -p COM4 get main.py
```

### ESP32-C6 실행
```bash
ampy -p COM4 run main.py
```

## 🔗 관련 문서

- **01_STARTUP_SCREEN_TEST_GUIDE.md**: 스타트업 화면 테스트
- **02_WIFI_SCAN_SCREEN_TEST_GUIDE.md**: Wi-Fi 스캔 화면 테스트
- **03_WIFI_PASSWORD_SCREEN_TEST_GUIDE.md**: Wi-Fi 비밀번호 화면 테스트
- **04_DOSE_COUNT_SCREEN_TEST_GUIDE.md**: 복용 횟수 설정 화면 테스트
- **05_DOSE_TIME_SCREEN_TEST_GUIDE.md**: 복용 시간 설정 화면 테스트
- **06_PILL_LOADING_SCREEN_TEST_GUIDE.md**: 알약 로딩 화면 테스트
