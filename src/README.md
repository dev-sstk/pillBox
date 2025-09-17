# PillBox 소스코드 구조

> **ESP32-C6 기반 알약 공급기 메인 소스코드**

> ⚠️ **중요**: 이 소스코드는 현재 개발 중입니다. 실행하지 마세요!

## 📁 프로젝트 구조

```
src/
├── main.py                    # 메인 애플리케이션 진입점
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
│   └── wifi_password_screen.py # WiFi 비밀번호 입력
└── wav/                     # 오디오 파일
    ├── refill_mode_selected_bomin.wav
    └── refill_mode_selected_bomin_compressed.wav
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

> ⚠️ **중요**: 소스코드 실행 대신 `../tests/` 폴더의 단위 테스트를 사용하세요!

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