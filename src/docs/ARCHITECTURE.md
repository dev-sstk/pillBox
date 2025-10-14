# PillBox 소프트웨어 아키텍처

## 📋 목차
1. [개요](#개요)
2. [시스템 구조](#시스템-구조)
3. [계층 구조](#계층-구조)
4. [핵심 컴포넌트](#핵심-컴포넌트)
5. [데이터 흐름](#데이터-흐름)
6. [화면 흐름](#화면-흐름)
7. [하드웨어 인터페이스](#하드웨어-인터페이스)
8. [설계 원칙](#설계-원칙)

---

## 개요

PillBox는 ESP32-C6 기반의 스마트 알약 공급기 시스템으로, MicroPython과 LVGL을 활용한 임베디드 애플리케이션입니다.

### 기술 스택
- **플랫폼**: ESP32-C6 (Xtensa LX7, Wi-Fi 6, Bluetooth 5.0)
- **언어**: MicroPython 1.25.0
- **UI 프레임워크**: LVGL 8.x (Light and Versatile Graphics Library)
- **하드웨어 통신**: SPI, I2S, GPIO
- **네트워크**: Wi-Fi (802.11ax)

### 시스템 특징
- **이벤트 기반 아키텍처**: 버튼 입력, 타이머 이벤트를 통한 비동기 처리
- **계층형 구조**: 하드웨어 추상화, 비즈니스 로직, UI 계층 분리
- **화면 기반 네비게이션**: Screen Manager를 통한 중앙집중식 화면 관리
- **모듈화 설계**: 각 하드웨어 및 기능별 독립 모듈

---

## 시스템 구조

```
┌─────────────────────────────────────────────────────────────┐
│                       Application Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Main App    │  │ Screen Tests │  │  PillBox App │      │
│  │  (main.py)   │  │  (테스트)     │  │(pillbox_app) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                      Presentation Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Screen     │  │  UI Screens  │  │  UI Style    │      │
│  │   Manager    │  │  (14 screens)│  │  (ui_style)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                   │                  │             │
│         └───────────────────┴──────────────────┘             │
│                         LVGL                                 │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                       Business Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Motor     │  │    Audio     │  │    WiFi      │      │
│  │   Control    │  │    System    │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                  Hardware Abstraction Layer                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Button     │  │   Display    │  │     I2S      │      │
│  │  Interface   │  │   Driver     │  │   Driver     │      │
│  │  (74HC165)   │  │  (ST7735S)   │  │ (MAX98357A)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐                                           │
│  │   74HC595    │   (Shift Register for Motor Control)     │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                        Hardware Layer                        │
│  GPIO / SPI / I2S / UART / Timer / WiFi / Bluetooth          │
│              ESP32-C6 Microcontroller                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 계층 구조

### 1. Application Layer (애플리케이션 계층)
최상위 레벨로, 시스템의 진입점과 전체 실행 흐름을 관리합니다.

**주요 컴포넌트:**
- `main.py`: 화면 테스트 시스템 (개발/테스트용 진입점)
- `pillbox_app.py`: 실제 제품용 메인 애플리케이션 (통합 시스템)

**책임:**
- 시스템 초기화 (LVGL, 하드웨어, 네트워크)
- 메인 이벤트 루프 실행
- 최상위 예외 처리 및 시스템 종료

### 2. Presentation Layer (프레젠테이션 계층)
사용자 인터페이스와 화면 관리를 담당합니다.

**주요 컴포넌트:**
- `screen_manager.py`: 화면 전환 및 내비게이션
- `screens/`: 14개의 화면 모듈
  - `base_screen.py`: 모든 화면의 베이스 클래스
  - `startup_screen.py`: 시작 화면
  - `wifi_scan_screen.py`: Wi-Fi 스캔 화면
  - `wifi_password_screen.py`: Wi-Fi 비밀번호 입력
  - `dose_count_screen.py`: 복용 횟수 설정
  - `dose_time_screen.py`: 복용 시간 설정
  - `pill_loading_screen.py`: 알약 로딩
  - `main_screen_ui.py`: 메인 화면
  - `notification_screen.py`: 알림 화면
  - `settings_screen.py`: 설정 화면
  - 기타 화면들...
- `ui_style.py`: UI 스타일 정의 (색상, 폰트, 테마)
- `lv_utils.py`: LVGL 유틸리티 함수

**책임:**
- 화면 렌더링 및 업데이트
- 버튼 입력에 대한 UI 반응
- 화면 간 데이터 전달
- 사용자 피드백 표시

### 3. Business Layer (비즈니스 로직 계층)
핵심 기능과 비즈니스 로직을 구현합니다.

**주요 컴포넌트:**
- `motor_control.py`: 알약 배출 로직 (스테퍼 모터 제어)
- `audio_system.py`: 음성 안내 및 효과음 재생
- `wifi_manager.py`: Wi-Fi 연결 및 네트워크 관리
- `audio_files_info.py`: 오디오 파일 메타데이터

**책임:**
- 알약 배출 스케줄 관리
- 음성 안내 시스템 제어
- 네트워크 연결 상태 관리
- 시간 동기화 (NTP)

### 4. Hardware Abstraction Layer (하드웨어 추상화 계층)
하드웨어 장치를 추상화하여 상위 계층에 일관된 인터페이스를 제공합니다.

**주요 컴포넌트:**
- `button_interface.py`: 74HC165 기반 버튼 입력
- `st77xx.py`: ST7735S 디스플레이 드라이버
- I2S 드라이버 (MAX98357A 오디오)
- 74HC595 드라이버 (모터 제어용 시프트 레지스터)

**책임:**
- 하드웨어 레지스터 직접 제어
- 데이터 변환 (디지털 신호 <-> 논리 값)
- 하드웨어 초기화 및 설정
- 에러 처리 및 복구

---

## 핵심 컴포넌트

### 1. PillBoxApp (`pillbox_app.py`)
**역할**: 메인 애플리케이션 클래스

```python
class PillBoxApp:
    - button_interface: ButtonInterface
    - screen_manager: ScreenManager
    - audio_system: AudioSystem
    - motor_system: PillBoxMotorSystem
    - wifi_manager: WifiManager
    - ui_style: UIStyle
```

**주요 기능:**
- 모든 하위 시스템 초기화
- 메인 이벤트 루프 실행 (50ms 주기)
- 버튼 입력을 화면으로 라우팅
- 시스템 리소스 관리

**이벤트 루프:**
```python
while running:
    lv.timer_handler()           # LVGL 이벤트 처리
    button_interface.update()    # 버튼 입력 처리
    screen_manager.update()      # 화면 업데이트
    time.sleep_ms(50)            # 50ms 대기
```

### 2. ScreenManager (`screen_manager.py`)
**역할**: 화면 생명주기 관리 및 내비게이션

```python
class ScreenManager:
    - screens: Dict[str, BaseScreen]
    - current_screen: BaseScreen
    - current_screen_name: str
    - screen_stack: List[str]  # 뒤로가기용 스택
```

**주요 기능:**
- 화면 등록 및 제거
- 화면 전환 (`show_screen()`)
- 뒤로가기 기능 (`go_back()`)
- 버튼 이벤트를 현재 화면으로 전달

**화면 전환 흐름:**
```
current_screen.hide()
    ↓
screen_stack.push(current_screen_name)
    ↓
current_screen = new_screen
    ↓
current_screen.show()
```

### 3. BaseScreen (`screens/base_screen.py`)
**역할**: 모든 화면의 추상 베이스 클래스

```python
class BaseScreen:
    - screen_obj: lv.obj
    - title_label: lv.label
    - content_area: lv.obj
    - button_hints: lv.label
```

**생명주기 메서드:**
- `__init__()`: 화면 초기화
- `_create_content()`: 화면별 UI 생성 (추상 메서드)
- `show()`: 화면 표시
- `hide()`: 화면 숨김
- `update()`: 주기적 업데이트
- `on_button_a/b/c/d()`: 버튼 이벤트 처리

**표준 레이아웃:**
```
┌────────────────────┐
│  Title Label       │ ← title_label (상단 중앙)
│                    │
│  ┌──────────────┐  │
│  │ Content Area │  │ ← content_area (중앙)
│  │              │  │
│  └──────────────┘  │
│                    │
│  Button Hints      │ ← button_hints (하단 중앙)
└────────────────────┘
```

### 4. ButtonInterface (`button_interface.py`)
**역할**: 74HC165 시프트 레지스터 기반 버튼 입력 처리

**하드웨어 연결:**
- GPIO 15: PL (Parallel Load)
- GPIO 10: Q7 (Serial Data Out)
- GPIO 3: CLK (Clock)

**버튼 매핑:**
```
74HC165 핀 → 논리 버튼 → 역할
Pin 0 (SW1) → Button C → Menu/Back
Pin 1 (SW2) → Button D → Select/Next
Pin 2 (SW3) → Button A → Up
Pin 3 (SW4) → Button B → Down
Pin 4-7     → Limit Switches (리미트 스위치)
```

**동작 원리:**
1. 병렬 입력 래치 (PL LOW → HIGH)
2. 클럭 신호로 직렬 데이터 읽기 (8비트)
3. 버튼 상태 비교 (이전 상태 vs 현재 상태)
4. 눌림 감지 (HIGH → LOW) → 콜백 호출
5. 디바운싱 처리 (50ms)

### 5. AudioSystem (`audio_system.py`)
**역할**: I2S 기반 WAV 파일 재생 시스템

**하드웨어 설정 (MAX98357A):**
- GPIO 6: BCLK (Bit Clock)
- GPIO 7: LRCLK (Left/Right Clock)
- GPIO 5: DIN (Data Input)
- 샘플레이트: 16kHz, 16bit, Mono

**기능:**
- `play_voice()`: 안내 음성 재생 (블로킹/비블로킹)
- `play_effect()`: 효과음 재생
- `set_volume()`: 볼륨 조절
- 오디오 큐 관리

**오디오 파일 관리:**
- `audio_files_info.py`: 파일 메타데이터 (경로, 길이, 설명)
- WAV 파일 위치: `src/wav/`

### 6. PillBoxMotorSystem (`motor_control.py`)
**역할**: 알약 배출을 위한 스테퍼 모터 제어

**하드웨어 구성:**
- 74HC595D: 시프트 레지스터 (모터 신호 확장)
- ULN2003A: 다렐링턴 트랜지스터 어레이 (전류 증폭)
- 28BYJ-48: 스테퍼 모터 (5V, 1/64 기어비)

**제어 로직:**
- 4상 여자 방식 (Full Step / Half Step)
- 시프트 레지스터를 통한 4개 모터 독립 제어
- 위치 추적 및 리미트 스위치 감지

**주요 메서드:**
- `dispense_pill(slot_num)`: 특정 슬롯에서 알약 배출
- `rotate_motor(steps)`: 모터 회전
- `initialize_uln2003_high()`: ULN2003A 초기화

### 7. WifiManager (`wifi_manager.py`)
**역할**: Wi-Fi 연결 및 네트워크 관리

**기능:**
- AP 스캔 및 목록 반환
- 네트워크 연결 (SSID, Password)
- 연결 상태 모니터링
- NTP 시간 동기화

---

## 데이터 흐름

### 1. 버튼 입력 흐름
```
물리 버튼 누름
    ↓
74HC165 시프트 레지스터 (병렬 → 직렬)
    ↓
ButtonInterface.read_shift_regs() [GPIO 읽기]
    ↓
ButtonInterface.update() [상태 비교]
    ↓
ButtonInterface._handle_button_press() [디바운싱]
    ↓
Button Callback 호출
    ↓
PillBoxApp._on_button_x()
    ↓
ScreenManager.handle_button_x()
    ↓
CurrentScreen.on_button_x() [UI 업데이트]
    ↓
LVGL 렌더링
```

### 2. 화면 렌더링 흐름
```
Screen.show() 호출
    ↓
lv.screen_load(screen_obj)
    ↓
LVGL 드라이버 계층
    ↓
St7735.flush() [프레임버퍼 전송]
    ↓
SPI 통신 (GPIO 21, 22)
    ↓
ST7735S 디스플레이 컨트롤러
    ↓
160x128 RGB LCD 표시
```

### 3. 오디오 재생 흐름
```
AudioSystem.play_voice(file_name)
    ↓
audio_files_info.get_full_path()
    ↓
WAV 파일 읽기 (파일 시스템)
    ↓
I2S 버퍼에 PCM 데이터 쓰기
    ↓
I2S 드라이버 (GPIO 5, 6, 7)
    ↓
MAX98357A D-Class 앰프
    ↓
스피커 출력
```

### 4. 알약 배출 흐름
```
User: 버튼 D 누름 (메인 화면)
    ↓
MainScreen.on_button_d()
    ↓
motor_system.dispense_pill(slot_num)
    ↓
PillBoxMotorSystem.rotate_motor(steps)
    ↓
74HC595MotorController.set_motor_step()
    ↓
SPI 통신 (시프트 레지스터)
    ↓
74HC595D 출력 업데이트
    ↓
ULN2003A 전류 증폭
    ↓
28BYJ-48 스테퍼 모터 회전
    ↓
알약 배출
```

---

## 화면 흐름

### 초기 설정 플로우
```
[Startup Screen]
       ↓
[WiFi Scan Screen] ← (사용자: AP 선택)
       ↓
[WiFi Password Screen] ← (사용자: 비밀번호 입력)
       ↓
(WiFi 연결 시도)
       ↓
[Dose Count Screen] ← (사용자: 복용 횟수 선택, 1~4회)
       ↓
[Dose Time Screen] ← (사용자: 복용 시간 설정, n회 반복)
       ↓
[Pill Loading Screen] ← (사용자: 알약 로딩)
       ↓
[Main Screen] (메인 화면)
```

### 메인 화면 플로우
```
[Main Screen]
  ├─ 버튼 A: 이전 슬롯
  ├─ 버튼 B: 다음 슬롯
  ├─ 버튼 C: 설정 화면
  │    └─ [Settings Screen]
  │          ├─ WiFi 재설정
  │          ├─ 볼륨 조절
  │          └─ 시스템 리셋
  └─ 버튼 D: 알약 배출
       └─ [Pill Dispense Screen] (애니메이션)
            └─ (배출 완료 후) [Main Screen]
```

### 알림 플로우
```
(스케줄 시간 도달)
    ↓
[Notification Screen]
  ├─ 음성 안내 재생
  ├─ 화면 표시 (깜빡임)
  └─ 버튼 D: 확인
       └─ 알약 자동 배출
            └─ [Main Screen]
```

---

## 하드웨어 인터페이스

### 핀맵 요약

| 기능 | GPIO | 방향 | 프로토콜 | 장치 |
|------|------|------|----------|------|
| **디스플레이 (ST7735S)** |
| SPI MOSI | 21 | OUT | SPI | ST7735S |
| SPI SCK | 22 | OUT | SPI | ST7735S |
| DC (Data/Command) | 19 | OUT | GPIO | ST7735S |
| CS (Chip Select) | 23 | OUT | GPIO | ST7735S |
| RST (Reset) | 20 | OUT | GPIO | ST7735S |
| **버튼 입력 (74HC165)** |
| PL (Parallel Load) | 15 | OUT | GPIO | 74HC165 |
| Q7 (Serial Data) | 10 | IN | GPIO | 74HC165 |
| CLK (Clock) | 3 | OUT | GPIO | 74HC165 |
| **오디오 (MAX98357A)** |
| BCLK | 6 | OUT | I2S | MAX98357A |
| LRCLK | 7 | OUT | I2S | MAX98357A |
| DIN | 5 | OUT | I2S | MAX98357A |
| **모터 제어 (74HC595)** |
| SER (Serial Data) | 0 | OUT | GPIO | 74HC595 |
| SRCLK (Shift Clock) | 1 | OUT | GPIO | 74HC595 |
| RCLK (Latch Clock) | 2 | OUT | GPIO | 74HC595 |

### SPI 통신 설정

**디스플레이 (ST7735S):**
```python
SPI(
    1,                    # SPI Bus 1
    baudrate=40000000,    # 40 MHz
    polarity=0,           # CPOL=0
    phase=0,              # CPHA=0
    sck=Pin(22),          # Clock
    mosi=Pin(21)          # MOSI
)
```

**특징:**
- 8비트 전송 모드
- MSB First
- 더블 버퍼링 비활성화 (메모리 절약)
- 160x128 해상도, 16bit RGB565

### I2S 통신 설정

**오디오 (MAX98357A):**
```python
I2S(
    0,                    # I2S Bus 0
    sck=Pin(6),           # Bit Clock
    ws=Pin(7),            # Word Select (LRCLK)
    sd=Pin(5),            # Serial Data
    mode=I2S.TX,          # Transmit Only
    bits=16,              # 16bit PCM
    format=I2S.MONO,      # Mono Audio
    rate=16000,           # 16kHz Sample Rate
    ibuf=2048             # 2KB Internal Buffer
)
```

**특징:**
- 16kHz, 16bit, Mono WAV 파일 지원
- 블로킹/비블로킹 재생 모드
- 오디오 큐 관리

### GPIO 제어 (시프트 레지스터)

**버튼 입력 (74HC165):**
- 8비트 병렬 입력 → 직렬 출력
- Active LOW (버튼 눌림 = LOW)
- Pull-up 저항 내장

**모터 제어 (74HC595):**
- 8비트 직렬 입력 → 병렬 출력
- Daisy Chain으로 여러 칩 연결 가능
- ULN2003A를 통한 전류 증폭

---

## 설계 원칙

### 1. 계층화 (Layered Architecture)
- 하드웨어 종속성을 추상화 계층에 격리
- 상위 계층은 하위 계층의 인터페이스에만 의존
- 테스트 및 유지보수 용이성 향상

### 2. 관심사의 분리 (Separation of Concerns)
- UI 로직과 비즈니스 로직 분리
- 각 모듈은 단일 책임 원칙 준수
- 화면별 독립적인 상태 관리

### 3. 이벤트 기반 설계 (Event-Driven)
- 버튼 입력은 콜백 방식으로 처리
- LVGL 이벤트 루프와 통합
- 비동기 오디오 재생 지원

### 4. 리소스 효율성 (Resource Efficiency)
- 메모리 제약 고려 (ESP32-C6: 512KB SRAM)
- 가비지 컬렉션 명시적 호출
- 화면 캐싱 전략 (재사용)
- 오디오 버퍼 최적화 (2KB)

### 5. 확장성 (Extensibility)
- BaseScreen을 상속하여 새 화면 추가
- 플러그인 방식의 하드웨어 드라이버
- 설정 기반 동작 (하드코딩 최소화)

### 6. 테스트 가능성 (Testability)
- 각 화면 독립 테스트 가능 (`main.py` 테스트 시스템)
- 하드웨어 모의 객체 지원 (`mock_screen.py`)
- 단위 테스트 가이드 제공 (`tests/` 디렉토리)

### 7. 한글 지원 (Korean Language Support)
- Noto Sans KR 폰트 통합
- UTF-8 인코딩 사용
- 모든 UI 텍스트 및 음성 안내 한글화

---

## 디렉토리 구조

```
src/
├── main.py                      # 화면 테스트 시스템 (개발용)
├── pillbox_app.py               # 메인 애플리케이션 (통합)
├── screen_manager.py            # 화면 관리자
├── audio_system.py              # 오디오 시스템
├── motor_control.py             # 모터 제어
├── button_interface.py          # 버튼 인터페이스
├── wifi_manager.py              # WiFi 관리자
├── ui_style.py                  # UI 스타일 정의
├── lv_utils.py                  # LVGL 유틸리티
├── st77xx.py                    # ST7735S 드라이버
├── audio_files_info.py          # 오디오 메타데이터
│
├── screens/                     # UI 화면 모듈
│   ├── __init__.py
│   ├── base_screen.py           # 베이스 클래스
│   ├── startup_screen.py        # 시작 화면
│   ├── main_screen_ui.py        # 메인 화면
│   ├── wifi_scan_screen.py      # WiFi 스캔
│   ├── wifi_password_screen.py  # WiFi 비밀번호
│   ├── dose_count_screen.py     # 복용 횟수 설정
│   ├── dose_time_screen.py      # 복용 시간 설정
│   ├── pill_loading_screen.py   # 알약 로딩
│   ├── notification_screen.py   # 알림
│   ├── settings_screen.py       # 설정
│   └── ...
│
├── wav/                         # 오디오 파일
│   ├── wav_select.wav
│   ├── wav_adjust.wav
│   └── ...
│
├── docs/                        # 문서
│   ├── 00_FIRMWARE_UPLOAD_GUIDE.md
│   ├── 01_STARTUP_SCREEN_TEST_GUIDE.md
│   └── ...
│
└── ARCHITECTURE.md              # 이 문서
```

---

## 메모리 관리

### 메모리 제약
- ESP32-C6: 512KB SRAM
- MicroPython 런타임: ~200KB
- LVGL 프레임버퍼: ~40KB (160×128×2 bytes)
- 사용 가능 메모리: ~270KB

### 최적화 전략
1. **화면 캐싱**: 자주 사용하는 화면 객체 재사용
2. **명시적 GC**: 화면 전환 시 `gc.collect()` 호출
3. **버퍼 크기 최적화**: I2S 버퍼 2KB, SPI 더블버퍼링 비활성화
4. **폰트 최적화**: 필요한 글자만 포함 (서브셋팅)
5. **리소스 정리**: 화면 숨김 시 불필요한 객체 삭제

---

## 동시성 모델

PillBox는 **협력적 멀티태스킹 (Cooperative Multitasking)** 모델을 사용합니다.

### 이벤트 루프
```python
while running:
    # 1. LVGL 이벤트 처리 (~10ms)
    lv.timer_handler()
    
    # 2. 버튼 입력 처리 (~1ms)
    button_interface.update()
    
    # 3. 화면 업데이트 (~1ms)
    screen_manager.update()
    
    # 4. 대기 (50ms)
    time.sleep_ms(50)
```

### 주의사항
- 블로킹 작업 금지 (긴 오디오 재생 등)
- 콜백 함수는 빠르게 실행 완료
- 무거운 작업은 여러 프레임에 분산

---

## 에러 처리

### 계층별 에러 처리 전략

**애플리케이션 계층:**
- 최상위 try-except로 전체 시스템 보호
- 사용자 친화적 에러 메시지 표시
- 시스템 재시작 또는 안전 모드 진입

**비즈니스 계층:**
- 각 모듈별 예외 처리
- 에러 로그 출력 (디버그용)
- 기본값으로 복구 (Fallback)

**하드웨어 계층:**
- 하드웨어 통신 실패 시 재시도
- 초기화 실패 시 시뮬레이션 모드
- 타임아웃 설정

### 예시
```python
try:
    motor_system.dispense_pill(slot_num)
except MotorError as e:
    print(f"모터 오류: {e}")
    audio_system.play_voice("error_motor")
    screen_manager.show_screen("error_screen")
except Exception as e:
    print(f"알 수 없는 오류: {e}")
    system_reset()
```

---

## 향후 개선 방향

### 1. 데이터 영속성
- 설정 및 스케줄 저장 (JSON 파일)
- 복용 기록 로깅
- NVS (Non-Volatile Storage) 활용

### 2. 원격 모니터링
- MQTT 또는 HTTP 프로토콜
- 모바일 앱 연동 (PillBoxApp/)
- 복용 알림 푸시

### 3. 센서 통합
- 알약 재고 감지 (적외선 센서)
- 도어 개폐 감지 (홀 센서)
- 온습도 센서

### 4. 고급 스케줄링
- 주간/주말 스케줄 분리
- 특정 요일 반복 설정
- 임시 스케줄 추가/삭제

### 5. 음성 인식
- 음성 명령으로 배출 (Bluetooth 마이크)
- 음성 피드백 강화

---

## 참고 문서

- [README.md](README.md): 프로젝트 개요 및 시작 가이드
- [docs/](docs/): 화면별 테스트 가이드
- [tests/](../tests/): 하드웨어 단위 테스트 가이드
- [LVGL 공식 문서](https://docs.lvgl.io/)
- [ESP32-C6 데이터시트](../docs/esp32-c6_datasheet_en.pdf)

---

**작성일**: 2025-10-10  
**버전**: 1.0.0  
**작성자**: PillBox Development Team


