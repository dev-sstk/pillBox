# PCB 펌웨어 테스트 메뉴얼

> **⚠️ 중요**: 이 메뉴얼은 작업자가 단계별로 따라할 수 있도록 작성되었습니다. 각 단계를 순서대로 진행하세요.

## 📋 목차
1. [프로젝트 구조 개요](#프로젝트-구조-개요)
2. [준비사항 확인](#준비사항-확인)
3. [개발환경 설치](#개발환경-설치)
4. [PCB 연결 및 확인](#pcb-연결-및-확인)
5. [펌웨어 업로드](#펌웨어-업로드)
6. [기본 기능 테스트](#기본-기능-테스트)
7. [고급 기능 테스트](#고급-기능-테스트)
8. [문제해결](#문제해결)
9. [완료 체크리스트](#완료-체크리스트)

---

## 📁 프로젝트 구조 개요

### 🗂️ 폴더 구조
```
pillBox/
├── firmware/           # ESP32-C6 펌웨어 바이너리 파일
├── fonts/             # 한국어 폰트 파일
├── src/               # 메인 소스코드
│   ├── screens/       # UI 화면 모듈들
│   └── wav/          # 오디오 파일
├── tests/             # 단위 테스트 스크립트
└── PCB_테스트_메뉴얼.md  # 이 메뉴얼
```

### 🔧 주요 컴포넌트
- **`src/main.py`**: 메인 애플리케이션 진입점
- **`src/pillbox_app.py`**: 핵심 비즈니스 로직
- **`src/screens/`**: LVGL 기반 UI 화면들
- **`src/audio_system.py`**: I2S 오디오 시스템
- **`src/motor_control.py`**: 스테퍼 모터 제어
- **`src/button_interface.py`**: 버튼 입력 처리
- **`tests/`**: 하드웨어별 단위 테스트

### 🎯 테스트 전략
1. **단위 테스트**: 각 하드웨어 컴포넌트별 개별 테스트
2. **통합 테스트**: 전체 시스템 동작 확인
3. **기능 테스트**: 실제 사용 시나리오 검증

---

## 🎯 준비사항 확인

### ✅ 필요한 하드웨어
- [ ] ESP32-C6 기반 PCB
- [ ] USB 케이블 (데이터 전송 가능한 케이블)
- [ ] 컴퓨터 (Windows 10/11)
- [ ] 인터넷 연결

### ✅ 필요한 소프트웨어
- [ ] Python 3.8 이상
- [ ] 시리얼 모니터 프로그램 (PuTTY 권장)
- [ ] 텍스트 에디터 (메모장 또는 VS Code)

### 📦 테스트 대상 하드웨어
- **ESP32-C6** 마이크로컨트롤러
- **ST7735S** RGB 디스플레이 (128x160)
- **MAX98357A** I2S 오디오 앰프
- **74HC165D** 시프트 레지스터 (버튼 입력)
- **74HC595** 시프트 레지스터 (스테퍼 모터 제어)
- **스테퍼 모터** (알약 공급용)

### 🎵 테스트 기능
- 디스플레이 RGB 컬러 테스트
- 오디오 출력 테스트 (I2S/PWM)
- 버튼 입력 테스트
- WiFi 연결 테스트
- NTP 시간 동기화 테스트
- 통합 시스템 테스트

---

## 🔧 개발환경 설치

### 1단계: Python 설치

1. **Python 다운로드**
   - 웹브라우저에서 https://www.python.org/downloads/ 접속
   - "Download Python 3.x.x" 버튼 클릭
   - 다운로드된 파일 실행

2. **Python 설치**
   - ✅ **중요**: "Add Python to PATH" 체크박스 반드시 선택
   - "Install Now" 클릭
   - 설치 완료 후 명령 프롬프트에서 확인:
   ```cmd
   python --version
   ```
   - 결과: `Python 3.x.x` 표시되면 성공

### 2단계: 필수 패키지 설치

1. **명령 프롬프트 열기**
   - Windows 키 + R → `cmd` 입력 → Enter

2. **패키지 설치**
   ```cmd
   pip install esptool
   pip install adafruit-ampy
   ```

3. **설치 확인**
   ```cmd
   esptool.py version
   ampy --help
   ```

### 3단계: PuTTY 설치

1. **PuTTY 다운로드**
   - https://www.putty.org/ 접속
   - "Download PuTTY" 클릭
   - Windows 64-bit 버전 다운로드

2. **PuTTY 설치**
   - 다운로드된 파일 실행
   - 기본 설정으로 설치 진행

### 4단계: USB 드라이버 설치 (필요시)

**COM 포트가 인식되지 않는 경우에만 진행**

1. **장치 관리자 확인**
   - Windows 키 + X → "장치 관리자" 선택
   - "포트(COM & LPT)" 항목 확인
   - "알 수 없는 장치" 또는 "!" 표시가 있으면 드라이버 필요

2. **드라이버 다운로드**
   - CP210x 드라이버: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
   - 또는 CH340 드라이버: https://sparks.gogo.co.nz/ch340.html

3. **드라이버 설치**
   - 다운로드된 파일 실행
   - 설치 완료 후 USB 케이블 재연결

---

## 🔌 PCB 연결 및 확인

### 1단계: PCB 연결

1. **USB 케이블 연결**
   - PCB의 USB 포트에 케이블 연결
   - 컴퓨터의 USB 포트에 연결

2. **전원 확인**
   - PCB의 전원 LED가 켜지는지 확인
   - 디스플레이가 켜지는지 확인

### 2단계: COM 포트 확인

1. **장치 관리자에서 포트 확인**
   - Windows 키 + X → "장치 관리자" 선택
   - "포트(COM & LPT)" 확장
   - "USB Serial Port (COMx)" 확인 (x는 숫자)
   - **기록**: COM 포트 번호 (예: COM3, COM4, COM5)

2. **PuTTY 설정**
   - PuTTY 실행
   - Connection type: **Serial** 선택
   - Serial line: **COMx** 입력 (확인한 포트 번호)
   - Speed: **115200** 입력
   - Saved Sessions: **micropython** 입력
   - **Save** 버튼 클릭 (나중에 Load로 재사용 가능)

### 3단계: 연결 테스트

1. **PuTTY로 연결 테스트**
   - PuTTY에서 **Load** 버튼 클릭
   - **Open** 버튼 클릭
   - 검은 화면이 나타나면 성공

2. **연결 확인**
   - PCB의 리셋 버튼을 한 번 누르기
   - PuTTY 화면에 다음과 같은 메시지가 나타나면 성공:
   ```
   MicroPython v1.25.0 on 2024-04-15; ESP32C6 module with ESP32C6
   Type "help()" for more information.
   >>>
   ```

3. **연결 실패 시**
   - COM 포트 번호 다시 확인
   - USB 케이블 재연결
   - 다른 USB 포트 시도

---

## 📤 펌웨어 업로드

### 1단계: 펌웨어 파일 준비

1. **펌웨어 파일 확인**
   - `firmware/` 폴더에 다음 파일들이 있는지 확인:
     - `ESP32_GENERIC_C6-20250415-v1.25.0.bin` (기본 버전)
     - `ESP32_GENERIC_C6-20250911_I2S+LVGL+KrFont.bin` (최신 버전)

2. **사용할 펌웨어**
   - `ESP32_GENERIC_C6-20250911_I2S+LVGL+KrFont.bin` (최신 버전, 모든 기능 포함)

### 2단계: 펌웨어 업로드

1. **명령 프롬프트 열기**
   - Windows 키 + R → `cmd` 입력 → Enter

2. **프로젝트 폴더로 이동**
   ```cmd
   cd C:\Users\outrobot\OneDrive\사업\아웃로봇\신성테크\소스코드_전달\pillBox
   ```

3. **펌웨어 업로드 명령 실행**
   ```cmd
    esptool --chip esp32c6 --port COMx erase_flash 
    esptool --chip esp32c6 --port COMx write_flash 0 .\firmware\ESP32_GENERIC_C6-20250911_I2S+LVGL+KrFont.bin
   ```

   **⚠️ 중요**: `COM3`을 실제 COM 포트 번호로 변경하세요!

4. **업로드 진행 상황 확인**
   - 진행률이 100%까지 표시되면 성공
   - 오류 메시지가 나타나면 COM 포트 번호 확인

### 3단계: 업로드 확인

1. **PuTTY로 연결**
   - PuTTY 실행 → Load → Open

2. **PCB 리셋**
   - PCB의 리셋 버튼을 한 번 누르기

3. **성공 확인**
   - 다음과 같은 메시지가 나타나면 성공:
   ```
   MicroPython v1.25.0 on 2024-04-15; ESP32C6 module with ESP32C6
   Type "help()" for more information.
   >>>
   ```

---

## 📁 Tests 폴더 개요

### 📋 단위 테스트 가이드 목록

각 하드웨어 컴포넌트별로 상세한 테스트 가이드가 준비되어 있습니다:

| 번호 | 테스트 가이드 | 대상 하드웨어 | 주요 기능 |
|------|--------------|--------------|----------|
| **1** | **74HC165_TEST_GUIDE.md** | 74HC165D 시프트 레지스터 | 버튼 입력 테스트 |
| **2** | **RGB_DISPLAY_TEST_GUIDE.md** | ST7735S 디스플레이 | RGB 컬러 표시 테스트 |
| **3** | **WAV_PLAYER_TEST_GUIDE.md** | 오디오 시스템 | WAV 파일 재생 테스트 |
| **4** | **74HC595_STEPPER_TEST_GUIDE.md** | 74HC595D + 스테퍼 모터 | 모터 제어 테스트 |
| **5** | **WIFI_TEST_GUIDE.md** | WiFi 모듈 | 네트워크 연결 테스트 |
| **6** | **NTP_TEST_GUIDE.md** | NTP 클라이언트 | 시간 동기화 테스트 |

### 🎯 테스트 순서 권장사항

1. **기본 하드웨어 테스트** (순서대로 진행)
   - **1번**: 74HC165D 버튼 입력 테스트
   - **2번**: ST7735S 디스플레이 테스트
   - **3번**: WAV 파일 재생 테스트

2. **고급 기능 테스트**
   - **4번**: 74HC595D 스테퍼 모터 테스트
   - **5번**: WiFi 연결 테스트
   - **6번**: NTP 시간 동기화 테스트

### 📖 각 가이드 사용법

각 테스트 가이드는 다음 구조로 되어 있습니다:
- **준비사항 확인**: 필요한 하드웨어/소프트웨어 체크리스트
- **하드웨어 연결**: 연결 방법 및 다이어그램
- **테스트 파일 업로드**: ampy를 사용한 파일 전송
- **테스트 실행**: 단계별 실행 방법
- **문제 해결**: 일반적인 문제와 해결방법
- **완료 체크리스트**: 테스트 완료 확인 항목

---

이 메뉴얼을 따라 단계별로 진행하면 PCB의 모든 기능을 정확히 테스트할 수 있습니다.
