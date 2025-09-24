# PillBox 소스코드

> **ESP32-C6 기반 스마트 알약 공급기 시스템**

## 📋 프로젝트 개요

PillBox는 ESP32-C6 마이크로컨트롤러를 기반으로 한 스마트 알약 공급기 시스템입니다. 사용자가 설정한 복용 스케줄에 따라 자동으로 알약을 공급하고, 복용 알림을 제공하는 IoT 기반 의료기기입니다.

### 🎯 주요 기능
- **스마트 복용 관리**: 사용자 맞춤 복용 스케줄 설정
- **자동 알약 공급**: 설정된 시간에 자동으로 알약 배출
- **Wi-Fi 연결**: 인터넷을 통한 시간 동기화 및 원격 모니터링
- **음성 안내**: 복용 알림 및 시스템 안내 음성 제공
- **직관적 UI**: LVGL 기반 터치스크린 인터페이스
- **한글 지원**: 완전한 한국어 인터페이스

### 🔧 하드웨어 구성
- **MCU**: ESP32-C6 (Wi-Fi 6, Bluetooth 5.0)
- **디스플레이**: ST7735S 1.8인치 RGB TFT (160x128)
- **입력**: 74HC165 기반 버튼 인터페이스 (A, B, C, D)
- **모터**: 74HC595 + ULN2003 기반 스테퍼 모터
- **오디오**: I2S 기반 WAV 파일 재생
- **저장**: 내장 플래시 메모리

## 🛠️ 개발환경

### 필수 소프트웨어
- **MicroPython**: ESP32-C6용 MicroPython 펌웨어
- **ampy**: Adafruit MicroPython Tool (파일 업로드)
- **Python 3.7+**: 개발 및 테스트 환경
- **Git**: 버전 관리

### 개발 도구
- **LVGL**: Light and Versatile Graphics Library (UI 프레임워크)
- **ESP-IDF**: ESP32 개발 프레임워크 (펌웨어 빌드)
- **VS Code**: 코드 편집기 (Python 확장 권장)


## 📚 가이드 문서

### 📁 문서 구조
```
src/docs/
├── 00_FIRMWARE_UPLOAD_GUIDE.md      # 펌웨어 업로드 가이드
├── 01_STARTUP_SCREEN_TEST_GUIDE.md  # 스타트업 화면 테스트
├── 02_WIFI_SCAN_SCREEN_TEST_GUIDE.md # Wi-Fi 스캔 화면 테스트
├── 03_WIFI_PASSWORD_SCREEN_TEST_GUIDE.md # Wi-Fi 비밀번호 화면 테스트
├── 04_DOSE_COUNT_SCREEN_TEST_GUIDE.md # 복용 횟수 설정 화면 테스트
├── 05_DOSE_TIME_SCREEN_TEST_GUIDE.md # 복용 시간 설정 화면 테스트
├── 06_PILL_LOADING_SCREEN_TEST_GUIDE.md # 알약 로딩 화면 테스트
├── 07_MAIN_SCREEN_TEST_GUIDE.md     # 메인 화면 테스트 (개발 중)
├── 08_NOTIFICATION_SCREEN_TEST_GUIDE.md # 알림 화면 테스트 (개발 중)
└── 09_SETTINGS_SCREEN_TEST_GUIDE.md # 설정 화면 테스트 (개발 중)
```

### 🚀 빠른 시작
1. **펌웨어 업로드**: [00_FIRMWARE_UPLOAD_GUIDE.md](docs/00_FIRMWARE_UPLOAD_GUIDE.md) 참조
2. **화면 테스트**: [01_STARTUP_SCREEN_TEST_GUIDE.md](docs/01_STARTUP_SCREEN_TEST_GUIDE.md)부터 시작
3. **개발 가이드**: 아래 개발 가이드 섹션 참조

> ✅ **현재 상태**: 화면 테스트 시스템으로 동작 중

## 📁 프로젝트 구조

```
src/
├── main.py                    # 화면 테스트 시스템 (메인 진입점)
├── pillbox_app.py            # 핵심 비즈니스 로직 및 상태 관리
├── screen_manager.py         # 화면 전환 및 관리
├── audio_system.py           # I2S 오디오 시스템
├── motor_control.py          # 스테퍼 모터 제어
├── button_interface.py       # 버튼 입력 처리
├── wifi_manager.py           # WiFi 연결 관리
├── lv_utils.py              # LVGL 유틸리티 함수
├── ui_style.py              # UI 스타일 정의
├── st77xx.py                # ST7735S 디스플레이 드라이버
├── audio_files_info.py      # 오디오 파일 정보 관리
├── screens/                 # UI 화면 모듈들
│   ├── __init__.py
│   ├── base_screen.py       # 기본 화면 클래스
│   ├── startup_screen.py    # 시작 화면
│   ├── main_screen.py       # 메인 화면
│   ├── settings_screen.py   # 설정 화면
│   ├── dose_time_screen.py  # 복용 시간 설정
│   ├── dose_count_screen.py # 복용 개수 설정
│   ├── pill_dispense_screen.py # 알약 공급 화면
│   ├── pill_loading_screen.py  # 알약 로딩 화면
│   ├── notification_screen.py  # 알림 화면
│   ├── wifi_scan_screen.py     # WiFi 스캔 화면
│   ├── wifi_password_screen.py # WiFi 비밀번호 입력
│   └── mock_screen.py       # 모의 화면 (테스트용)
└── wav/                     # 오디오 파일
    ├── refill_mode_selected_bomin.wav
    ├── refill_mode_selected_bomin_compressed.wav
    ├── wav_adjust.wav
    ├── wav_alarm.wav
    └── wav_select.wav
```

## 🔧 주요 모듈 설명

### 📱 핵심 애플리케이션
- **`main.py`**: 시스템 초기화 및 메인 루프
- **`pillbox_app.py`**: 알약 공급기 핵심 로직, 상태 관리, 스케줄링

### 🖥️ UI 시스템
- **`screen_manager.py`**: 화면 전환 및 네비게이션 관리
- **`screens/`**: LVGL 기반 UI 화면들
  - 각 화면은 `base_screen.py`를 상속받아 구현
  - 독립적인 화면별 로직 및 이벤트 처리

### 🔊 오디오 시스템
- **`audio_system.py`**: I2S 인터페이스를 통한 WAV 파일 재생
- **`audio_files_info.py`**: 오디오 파일 메타데이터 관리

### 🔧 하드웨어 제어
- **`motor_control.py`**: 74HC595D를 통한 스테퍼 모터 제어
- **`button_interface.py`**: 74HC165D를 통한 버튼 입력 처리
- **`st77xx.py`**: ST7735S RGB 디스플레이 드라이버

### 🌐 네트워크
- **`wifi_manager.py`**: WiFi 연결, 스캔, 설정 관리

### 🎨 UI 유틸리티
- **`lv_utils.py`**: LVGL 관련 유틸리티 함수
- **`ui_style.py`**: UI 테마 및 스타일 정의

## 🚀 실행 방법

> ⚠️ **경고**: 아래 실행 방법은 참고용입니다. 현재 소스코드는 개발 중이므로 실행하지 마세요!

## 🧪 테스트

### 펌웨어 업로드
- **00_FIRMWARE_UPLOAD_GUIDE.md**: ESP32-C6 펌웨어 업로드 방법

### 화면별 테스트 가이드
- **01_STARTUP_SCREEN_TEST_GUIDE.md**: 스타트업 화면 테스트
- **02_WIFI_SCAN_SCREEN_TEST_GUIDE.md**: Wi-Fi 스캔 화면 테스트
- **03_WIFI_PASSWORD_SCREEN_TEST_GUIDE.md**: Wi-Fi 비밀번호 화면 테스트
- **04_DOSE_COUNT_SCREEN_TEST_GUIDE.md**: 복용 횟수 설정 화면 테스트
- **05_DOSE_TIME_SCREEN_TEST_GUIDE.md**: 복용 시간 설정 화면 테스트
- **06_PILL_LOADING_SCREEN_TEST_GUIDE.md**: 알약 로딩 화면 테스트
- **07_MAIN_SCREEN_TEST_GUIDE.md**: 메인 화면 테스트 (개발 중)
- **08_NOTIFICATION_SCREEN_TEST_GUIDE.md**: 알림 화면 테스트 (개발 중)
- **09_SETTINGS_SCREEN_TEST_GUIDE.md**: 설정 화면 테스트 (개발 중)

### 하드웨어 단위 테스트
각 하드웨어 컴포넌트별 단위 테스트는 `../tests/` 폴더에서 확인할 수 있습니다:

- **01_74HC165_TEST_GUIDE.md**: 버튼 입력 테스트
- **02_RGB_DISPLAY_TEST_GUIDE.md**: 디스플레이 테스트
- **03_WAV_PLAYER_TEST_GUIDE.md**: 오디오 테스트
- **04_74HC595_STEPPER_TEST_GUIDE.md**: 모터 제어 테스트
- **05_WIFI_TEST_GUIDE.md**: WiFi 연결 테스트
- **06_NTP_TEST_GUIDE.md**: 시간 동기화 테스트

## 📋 개발 가이드

### 새로운 화면 추가
1. `screens/` 폴더에 새 파일 생성
2. `base_screen.py`를 상속받아 구현
3. `screen_manager.py`에 화면 등록
4. `pillbox_app.py`에서 화면 전환 로직 추가

### 하드웨어 드라이버 추가
1. 해당 하드웨어 제어 모듈 생성
2. `pillbox_app.py`에서 초기화 및 사용
3. 필요시 `tests/` 폴더에 테스트 스크립트 추가