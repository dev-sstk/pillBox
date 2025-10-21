# PillBox 하드웨어 사양 및 핀맵

## 📋 목차
1. [개요](#개요)
2. [ESP32-C6 핀맵](#esp32-c6-핀맵)
3. [하드웨어 모듈](#하드웨어-모듈)
4. [통신 프로토콜](#통신-프로토콜)
5. [전원 관리](#전원-관리)
6. [회로 연결도](#회로-연결도)
7. [하드웨어 테스트](#하드웨어-테스트)
8. [문제 해결](#문제-해결)

---

## 개요

PillBox는 ESP32-C6 마이크로컨트롤러 기반의 스마트 알약 공급기로, 다음과 같은 하드웨어 구성을 가지고 있습니다.

### 주요 사양 (최종 구현)
- **MCU**: ESP32-C6 (RISC-V, 160MHz, 512KB SRAM, 4MB Flash)
- **무선 통신**: Wi-Fi 6 (802.11ax), Bluetooth 5.0 LE
- **디스플레이**: ST7735S 1.8" TFT LCD (160×128, RGB565) ✅ 완전 구현
- **입력**: 74HC165 시프트 레지스터 (4개 버튼 + 4개 리미트 스위치) ✅ 완전 구현
- **출력**: 74HC595 시프트 레지스터 (모터 제어) ✅ 완전 구현
- **모터**: 28BYJ-48 스테퍼 모터 3개 + 24BYJ-48 스테퍼 모터 1개 (ULN2003A 드라이버) ✅ 완전 구현
- **오디오**: MAX98357A I2S 앰프 ✅ 완전 구현
- **전원**: USB Type-C / Li-ion 배터리 (MCP73831 충전 관리)
- **데이터 저장**: SPIFFS 파일 시스템 (/data 디렉토리) ✅ 완전 구현

---

## ESP32-C6 핀맵

### 전체 핀 할당표

| GPIO | 기능 | 방향 | 연결 대상 | 프로토콜 | 설명 |
|------|------|------|-----------|----------|------|
| **입출력 제어** |
| IO1 | LED_PWR/B | OUT | Power LED / RGB Blue | PWM | 전원 표시 LED / RGB LED Blue |
| IO2 | SER (DI) | OUT | 74HC595D Serial Data | GPIO | 시프트 레지스터 데이터 |
| IO3 | SH_CP / CLK | OUT | 74HC595/74HC165 공용 | GPIO | 시프트 클럭 (공유) |
| **오디오 (I2S)** |
| IO5 | DIN | OUT | MAX98357A Data In | I2S | I2S 오디오 데이터 |
| IO6 | BCLK | OUT | MAX98357A Bit Clock | I2S | I2S 비트 클럭 |
| IO7 | LRCLK | OUT | MAX98357A L/R Clock | I2S | I2S 워드 셀렉트 |
| **입력** |
| IO10 | DATA_OUT | IN | 74HC165 Q7 Output | GPIO | 버튼/센서 데이터 입력 |
| **시프트 레지스터** |
| IO15 | ST_CP / PL | OUT | 74HC595/74HC165 공용 | GPIO | 스토리지 클럭/병렬 로드 |
| **기타** |
| IO11 | NC | - | Not Connected | - | 미사용 (NC) |
| IO18 | SOUND | OUT | Buzzer | PWM | 부저 출력 |
| **디스플레이 (SPI)** |
| IO19 | LCD_DC | OUT | ST7735S D/C | GPIO | 데이터/커맨드 선택 |
| IO20 | LCD_RES | OUT | ST7735S Reset | GPIO | 디스플레이 리셋 |
| IO21 | LCD_SDA (MOSI) | OUT | ST7735S SPI Data | SPI | SPI MOSI |
| IO22 | LCD_SCL (SCK) | OUT | ST7735S SPI Clock | SPI | SPI Clock |
| IO23 | LCD_CS | OUT | ST7735S Chip Select | GPIO | SPI 칩 선택 |
| 3V3 | LCD_BLK | - | ST7735S Backlight | - | 백라이트 전원 (직결) |
| **전원 및 접지** |
| 3V3 | Power | - | 3.3V Power Supply | - | 시스템 전원 |
| GND | Ground | - | Ground (Pin 1, 28, 29) | - | 접지 |
| EN | Enable | IN | Reset Control | - | 리셋/인에이블 핀 |

### 핀 배치도

```
ESP32-C6 DevKit C-1 (30 Pin)

     USB Type-C
         ||
  ┌──────────────┐
  │              │
1 │ GND      GND │ 30
2 │ 3V3      GND │ 29
3 │ EN       GND │ 28
4 │ IO4      IO7 │ 27  ← LRCLK
5 │ IO5      IO6 │ 26  ← BCLK
6 │ NC       IO5 │ 25  ← DIN
7 │ NC       IO4 │ 24  ← BAT_AD
8 │ NC       IO3 │ 23  ← SH_CP/CLK
9 │ NC       IO2 │ 22  ← DI
10│ NC       IO1 │ 21  ← LED_PWR/B
11│ IO8      IO0 │ 20  ← DI
12│ IO9      IO15│ 19  ← ST_CP/PL
13│ IO10     IO18│ 18  ← SOUND
14│ IO11     NC  │ 17
15│ IO12     IO23│ 16  ← LCD_CS
  │              │
  └──────────────┘

추가 핀 (오른쪽 하단부):
IO13, IO14, IO19, IO20, IO21, IO22
```

### 개발 시 주의사항

1. **부트모드**: IO0을 LOW로 하고 리셋하면 다운로드 모드
2. **I2S 오디오**: BCLK, DIN, LRCLK 핀 사용
3. **SPI 통신**: LCD 제어용 SPI 인터페이스
4. **시리얼 통신**: TX(IO1), RX(IO3) 기본 UART
5. **전원**: 3.3V 동작, USB 또는 배터리 전원 지원
6. **모터 제어**: ULN2003A 드라이버를 통한 스테퍼 모터 제어

---

## 하드웨어 모듈

### 1. 디스플레이 (ST7735S)

**사양:**
- 크기: 1.8인치 TFT LCD
- 해상도: 160×128 픽셀
- 색상: 65K (RGB565)
- 인터페이스: SPI
- 모델: MSP1804 (blacktab)

**핀 연결:**
```
ST7735S        ESP32-C6      설명
────────────────────────────────────
VCC            3.3V          전원
GND            GND           접지
CS             IO23          칩 선택 (Active LOW)
RST            IO20          리셋 (Active LOW)
DC             IO19          데이터/커맨드 (HIGH=Data, LOW=Command)
SDA (MOSI)     IO21          SPI 데이터
SCL (SCK)      IO22          SPI 클럭
LED            3.3V          백라이트 (PWM 가능)
```

**SPI 설정:**
- 버스: SPI1
- 속도: 40MHz
- 모드: CPOL=0, CPHA=0 (Mode 0)
- 비트 순서: MSB First
- 회전: 3 (180도)
- 오프셋: X=1, Y=2

**소프트웨어 드라이버:**
- 파일: `st77xx.py`
- 클래스: `St7735`
- LVGL 통합: 자동 플러시 콜백

### 2. 버튼 입력 (74HC165)

**사양:**
- IC: SN74HC165 (8비트 병렬 → 직렬 시프트 레지스터)
- 입력: 8개 디지털 입력 (Active LOW)
- 출력: 직렬 데이터 (Q7)
- Pull-up: 내부 10kΩ

**핀 연결:**
```
74HC165        ESP32-C6      설명
────────────────────────────────────
VCC            3.3V          전원
GND            GND           접지
CLK            IO3           시프트 클럭 (74HC595와 공유)
PL (SH/LD)     IO15          병렬 로드 (Active LOW)
Q7             IO10          직렬 데이터 출력
```

**입력 매핑:**
```
74HC165 핀    입력 장치           논리 버튼    역할
──────────────────────────────────────────────────────
D0 (Pin 11)   SW1 (Menu)          Button C     메뉴/뒤로가기
D1 (Pin 12)   SW2 (Select)        Button D     선택/다음
D2 (Pin 13)   SW3 (Up)            Button A     위/증가
D3 (Pin 14)   SW4 (Down)          Button B     아래/감소
D4 (Pin 3)    LIMIT SW3           -            모터 2 원점 (역순)
D5 (Pin 4)    LIMIT SW2           -            모터 1 원점
D6 (Pin 5)    LIMIT SW1           -            모터 0 원점 (역순)
D7 (Pin 6)    LIMIT SW4           -            모터 3 원점
```

**동작 원리:**
1. PL을 LOW로 설정 → 8개 병렬 입력 래치
2. PL을 HIGH로 복구
3. CLK 상승 엣지마다 1비트씩 Q7으로 출력
4. 8번 클럭 → 8비트 데이터 완전 읽기

**소프트웨어 드라이버:**
- 파일: `button_interface.py`
- 클래스: `ButtonInterface`
- 폴링 주기: 10ms
- 디바운싱: 50ms

### 3. 모터 제어 (74HC595 + ULN2003A)

**구성:**
- 시프트 레지스터: SN74HC595D × 2개 (직렬 → 병렬)
- 모터 드라이버: ULN2003A × 4개
- 스테퍼 모터: 28BYJ-48 × 3개 + 24BYJ-48 × 1개

**74HC595D 핀 연결:**
```
74HC595 #1     ESP32-C6      설명
────────────────────────────────────
VCC            3.3V          전원
GND            GND           접지
SER (DS)       IO2           직렬 데이터 입력
SRCLK (SHCP)   IO3           시프트 레지스터 클럭 (74HC165와 공유)
RCLK (STCP)    IO15          스토리지 레지스터 클럭 (래치)
OE             GND           출력 인에이블 (Always ON)
SRCLR          3.3V          시프트 레지스터 클리어 (Always HIGH)
Q7'            SER of #2     다음 칩으로 캐스케이드
Q0-Q3          Motor 0       모터 0 제어 신호 (1B,2B,3B,4B)
Q4-Q7          Motor 1       모터 1 제어 신호 (1B,2B,3B,4B)

74HC595 #2     연결
────────────────────────────────────
SER (DS)       Q7' of #1     이전 칩에서 캐스케이드
SRCLK (SHCP)   IO3           공유
RCLK (STCP)    IO15          공유
Q0-Q3          Motor 2       모터 2 제어 신호 (1B,2B,3B,4B)
Q4-Q7          Motor 3       모터 3 제어 신호 (1B,2B,3B,4B)
```

**ULN2003A 연결:**
```
각 모터당 1개의 ULN2003A 사용

74HC595 → ULN2003A → 28BYJ-48
────────────────────────────────────
Qx (Bit 0)  → 1B → 1C → Coil A (Orange)
Qx (Bit 1)  → 2B → 2C → Coil B (Yellow)
Qx (Bit 2)  → 3B → 3C → Coil C (Pink)
Qx (Bit 3)  → 4B → 4C → Coil D (Blue)

28BYJ-48 5핀 커넥터:
Pin 1: Coil A (Orange)
Pin 2: Coil B (Yellow)
Pin 3: VCC (Red) - 5V
Pin 4: Coil C (Pink)
Pin 5: Coil D (Blue)
```

**28BYJ-48 스테퍼 모터 사양 (모터 0, 1, 2):**
- 타입: 유니폴라 스테퍼 모터
- 전압: 5V DC
- 스텝 각도: 5.625° (기어비 전)
- 기어비: 1:64
- 실제 스텝 각도: 0.087890625° (5.625° ÷ 64)
- 한 바퀴 스텝 수: 4096 스텝 (정확: 4095.9)
- 스텝 모드: 8스텝 Half Step (더 부드러운 동작)
- 토크: ~300 gf·cm
- RPM: ~15 (최대 속도)

**24BYJ-48 스테퍼 모터 사양 (모터 3):**
- 타입: 유니폴라 스테퍼 모터
- 전압: 5V DC
- 스텝 각도: 5.625° (기어비 전)
- 기어비: 1:64
- 실제 스텝 각도: 0.087890625° (5.625° ÷ 64)
- 한 바퀴 스텝 수: 4096 스텝 (정확: 4095.9)
- 스텝 모드: 8스텝 Half Step (더 부드러운 동작)
- 토크: ~300 gf·cm
- RPM: ~15 (최대 속도)
- 용도: 배출구 슬라이드 제어

**스텝 시퀀스 (8 Half Step):**
```
Step  |  A  B  C  D  | Hex  | Binary
──────────────────────────────────────
  0   |  1  0  0  0  | 0x08 | 00001000
  1   |  1  1  0  0  | 0x0C | 00001100
  2   |  0  1  0  0  | 0x04 | 00000100
  3   |  0  1  1  0  | 0x06 | 00000110
  4   |  0  0  1  0  | 0x02 | 00000010
  5   |  0  0  1  1  | 0x03 | 00000011
  6   |  0  0  0  1  | 0x01 | 00000001
  7   |  1  0  0  1  | 0x09 | 00001001
```

**모터 할당:**
- **모터 0, 1, 2**: 알약 디스크 회전 (28BYJ-48, 15칸, 리미트 스위치 기반)
- **모터 3**: 배출구 슬라이드 제어 (24BYJ-48, 0°~360°)

**소프트웨어 드라이버:**
- 파일: `motor_control.py`
- 클래스: `StepperMotorController`, `PillBoxMotorSystem`
- 속도: 1ms/step (최고속)
- 제어 방식: 리미트 스위치 기반 위치 추적

### 4. 스위치 및 센서 (74HC165)

**사양:**
- IC: 74HC165D (8비트 병렬-직렬 변환기)
- 입력: 8개 디지털 입력
- 출력: 직렬 데이터 (Q7)
- 클럭: 공유 클럭 (74HC595와 동일)

**핀 연결:**
```
74HC165D       ESP32-C6      설명
────────────────────────────────────
VCC            3.3V          전원
GND            GND           접지
SH/LD (SH_CP)  IO3           시프트/로드 클럭 (74HC595와 공유)
CLK (ST_CP)    IO15          스토리지 클럭 (74HC595와 공유)
Q7             IO10          직렬 데이터 출력
D0             SW1           메뉴 버튼
D1             SW2           선택 버튼
D2             SW3           위 버튼
D3             SW4           아래 버튼
D4             LIMIT SW1     스테퍼 모터 1 원점
D5             LIMIT SW2     스테퍼 모터 2 원점
D6             LIMIT SW3     스테퍼 모터 3 원점
D7             LIMIT SW4     스테퍼 모터 4 원점
```

**스위치 사양:**
- **SW1-SW4**: EST-1102VB 택트 스위치 (4개 버튼)
- **LIMIT SW**: 리미트 스위치 (4개, J8 커넥터)
- **PHOTO**: 포토 센서 (NPN 트랜지스터 Q6 사용, J5 커넥터)

### 5. 오디오 출력 (MAX98357A)

**사양:**
- IC: MAX98357A (I2S D-Class 앰프)
- 출력: 3.2W @ 4Ω, 1.8W @ 8Ω
- 인터페이스: I2S
- 샘플레이트: 8kHz ~ 96kHz
- 비트 수: 16bit, 24bit, 32bit
- 채널: Mono / Stereo (Left 또는 Right 선택 가능)

**핀 연결:**
```
MAX98357A      ESP32-C6      설명
────────────────────────────────────
VCC            5V            전원 (충전 시 USB 5V)
GND            GND           접지
DIN            IO5           I2S 데이터 입력
BCLK           IO6           I2S 비트 클럭
LRCLK (LRC)    IO7           I2S L/R 클럭 (Word Select)
SD             GND           셧다운 (GND=활성화)
GAIN           GND           게인 설정 (GND=9dB)
OUT+           Speaker+      스피커 출력 +
OUT-           Speaker-      스피커 출력 -
```

**I2S 설정:**
- 버스: I2S0
- 모드: TX (송신 전용)
- 포맷: Mono
- 비트: 16bit
- 샘플레이트: 16kHz
- 버퍼 크기: 2048 bytes

**게인 설정 (GAIN 핀):**
- GND: 9dB
- VCC: 15dB
- 100kΩ to GND: 12dB

**소프트웨어 드라이버:**
- 파일: `audio_system.py`
- 클래스: `AudioSystem`
- 포맷: WAV 파일 (16kHz, 16bit, Mono)
- 재생 모드: 블로킹/비블로킹

### 5. 전원 관리

**USB-UART 브리지:**
- IC: CP2102N-A01
- 인터페이스: USB Type-C
- 속도: 최대 921600 baud
- 기능: 프로그래밍 + 시리얼 통신 + 자동 리셋

**배터리 충전기:**
- IC: MCP73831T-2ACI/OT
- 입력: USB 5V
- 배터리: Li-ion 1S (3.7V ~ 4.2V)
- 충전 전류: 500mA
- 충전 종료 전압: 4.2V
- 상태 표시: RGB LED 연결
  - STAT 핀 → RGB LED Red/Green
  - 충전 중: Red LED 점등
  - 충전 완료: Green LED 점등
  - 대기 상태: LED 꺼짐

**전압 레귤레이터:**
- IC: AP2112K-3.3TRG1 (LDO)
- 입력: 5V (USB) 또는 3.7V (Battery)
- 출력: 3.3V
- 최대 전류: 600mA
- 효율: ~80%

**배터리 모니터링:**
- GPIO: IO4 (BAT_AD)
- 배터리: 3.7V Li-ion 배터리 (실제 범위: 3.0V ~ 4.2V)
- 회로: 전압 분배기 (배터리 측 R1=100kΩ, 그라운드 측 R2=100kΩ)
- 분배 비율: 1:2 (배터리 전압의 1/2이 ADC로 입력)
- ADC 범위: 0V ~ 3.3V (실제 배터리 전압: 0V ~ 6.6V)
- 실용 범위: 1.5V ~ 2.1V ADC (배터리 3.0V ~ 4.2V에 해당)
- 분해능: 12bit (0 ~ 4095)
- 배터리 전압 계산: `V_battery = ADC_value * 3.3 / 4095 * 2`
- 배터리 상태 판단: 3.0V 이하 (저전압), 4.2V (충전 완료)

**전력 소비 (추정):**
- ESP32-C6: ~100mA (Wi-Fi 활성)
- ST7735S: ~30mA (백라이트 포함)
- MAX98357A: ~20mA (대기), ~500mA (최대 출력)
- 스테퍼 모터 (×4): ~200mA (1개 동작 시)
- **총 소비**: ~350mA (일반), ~850mA (모터 동작 시)

### 6. USB 및 시리얼 통신

**CP2102N-A01 USB-UART 브리지:**
- IC: CP2102N-A01 (Silicon Labs)
- 기능: USB Type-C ↔ UART 변환
- 전압: 3.3V (ESP32-C6 호환)
- 속도: 최대 2Mbps
- 자동 프로그래밍: DTR/RTS 신호 지원

**USB Type-C 커넥터 (J1):**
- 전원: 5V USB 전원 공급
- 데이터: USB 2.0 Full Speed
- 프로그래밍: 자동 다운로드 모드 지원
- 충전: 배터리 충전 시 5V 공급

### 7. 기타 하드웨어

**부저 (BMX-3203/BUZZER):**
- 모델: BMX-3203
- 타입: 패시브 부저 (Passive Buzzer)
- 전압: 3.3V
- 주파수: 2kHz ~ 5kHz (PWM 제어)
- GPIO: IO18 (SOUND)
- 제어 방식: PWM 신호로 주파수 및 볼륨 제어
- 용도: 알람 신호, 사용자 알림음

**서보 모터 (SERVO1, SERVO2):**
- 타입: SG90 호환 서보 모터
- 전압: 5V
- 각도: 0° ~ 180°
- PWM: 50Hz, 1ms~2ms 펄스 폭
- GPIO: IO12, IO13

**포토 센서 (PHOTO):**
- 타입: 포토트랜지스터 (NPN)
- 전압: 3.3V
- 출력: 디지털 (HIGH=빛 감지)
- GPIO: IO11

**RGB LED (LMRGB5050-B4):**
- 모델: LMRGB5050-B4
- 타입: Common Anode RGB LED
- 전압: 3.3V
- 제어: PWM (3채널)
- GPIO 연결:
  - B (Blue) 핀: IO1 (LED_PWR와 공용)
  - R (Red) 핀: MCP73831 STAT (충전 상태 표시)
  - G (Green) 핀: MCP73831 STAT (충전 상태 표시)
  - Anode (VCC): 3.3V
- 용도: 
  - Blue (IO1): 상태 표시, 알람 신호, 사용자 피드백
  - Red/Green (MCP73831): 배터리 충전 상태 표시
    - Red: 충전 중
    - Green: 충전 완료
    - Off: 대기 상태

---

## 통신 프로토콜

### SPI (디스플레이)

**하드웨어 설정:**
```python
SPI(
    1,                    # SPI Bus 1
    baudrate=40000000,    # 40 MHz
    polarity=0,           # CPOL=0 (클럭 기본 LOW)
    phase=0,              # CPHA=0 (첫 엣지에서 샘플링)
    sck=Pin(22),          # Clock
    mosi=Pin(21),         # Master Out Slave In
    miso=None             # 사용 안 함 (디스플레이는 단방향)
)
```

**타이밍:**
- 클럭 주파수: 40MHz
- 비트 전송 시간: 25ns/bit
- 프레임 전송 시간: ~10ms (160×128×16bit @ 40MHz)

### I2S (오디오)

**하드웨어 설정:**
```python
I2S(
    0,                    # I2S Bus 0
    sck=Pin(6),           # Bit Clock (BCLK)
    ws=Pin(7),            # Word Select (LRCLK)
    sd=Pin(5),            # Serial Data (DIN)
    mode=I2S.TX,          # Transmit Only
    bits=16,              # 16bit 샘플
    format=I2S.MONO,      # Mono Audio
    rate=16000,           # 16kHz 샘플레이트
    ibuf=2048             # 2KB 내부 버퍼
)
```

**타이밍:**
- 샘플레이트: 16kHz
- 비트 클럭: 512kHz (16kHz × 16bit × 2채널)
- 워드 클럭: 16kHz
- 버퍼 지속 시간: 64ms (2048 bytes ÷ 16kHz ÷ 2 bytes)

### GPIO (시프트 레지스터)

**74HC165 읽기 타이밍:**
```
      ┌──┐ ┌──┐ ┌──┐ ┌──┐
CLK:  │  └─┘  └─┘  └─┘  └─
      
PL:   ──┐             ┌───
        └─────────────┘
        ↑ 5µs
        
Q7:   ──X──D0─X──D1─X──D2─
```

- PL 펄스 폭: 5µs (병렬 로드)
- CLK 펄스 폭: 5µs (시프트)
- 총 읽기 시간: ~80µs (8비트)

**74HC595 쓰기 타이밍:**
```
         ┌──┐ ┌──┐ ┌──┐ ┌──┐
SH_CP:   │  └─┘  └─┘  └─┘  └─
         
SER:  ──X──D0─X──D1─X──D2─X
      
ST_CP: ──────────────┐  ┌───
                     └──┘
                     ↑ 래치
```

- SH_CP 펄스 폭: 1µs (시프트)
- ST_CP 펄스 폭: 1µs (래치)
- 총 쓰기 시간: ~20µs (16비트, 2개 칩)

---

## 회로 연결도

### 시스템 블록 다이어그램

```
                    ┌─────────────────┐
                    │   ESP32-C6      │
                    │   DevKit C-1    │
                    └─────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
   │ Display │         │ Audio   │        │ Motor   │
   │ ST7735S │         │MAX98357A│        │ Control │
   └─────────┘         └─────────┘        └─────────┘
   │                   │                   │
   │ SPI               │ I2S               │ GPIO
   │ 40MHz             │ 16kHz             │ Shift Register
   └───────────────────┴───────────────────┘
                       │
              ┌────────┴────────┐
              │                 │
         ┌────▼────┐       ┌────▼────┐
         │ Buttons │       │ WiFi    │
         │ 74HC165 │       │ 2.4GHz  │
         └─────────┘       └─────────┘
```

### 전원 분배도

```
USB Type-C (5V)
    │
    ├─→ MCP73831 ──→ Li-ion Battery (3.7V~4.2V)
    │      │           │
    │      │           ├─→ 100kΩ ──→ IO4 (BAT_AD) ──→ ESP32-C6 ADC
    │      │           │
    │      │           └─→ 100kΩ ──→ GND
    │      │
    │      └─→ STAT ──→ RGB LED (Red/Green)
    │
    ├─→ AP2112K ──→ 3.3V Rail
    │      │           │
    │      │           ├─→ ESP32-C6
    │      │           ├─→ ST7735S
    │      │           ├─→ 74HC165
    │      │           ├─→ 74HC595
    │      │           └─→ Sensors
    │
    └─→ 5V Rail
           │
           ├─→ MAX98357A
           ├─→ ULN2003A (×4)
           └─→ Servo Motors
```

### 배터리 모니터링 회로

```
Li-ion Battery (3.7V~4.2V)
    │
    ├─→ 100kΩ (R1)
    │       │
    │       ├─→ IO4 (BAT_AD) ──→ ESP32-C6 ADC
    │       │
    │       ├─→ 100kΩ (R2)
    │       │
    │       └─→ GND
    │
    └─→ MCP73831 (충전 관리)
```

**전압 분배 계산:**
- R1 = 100kΩ (배터리 측)
- R2 = 100kΩ (그라운드 측)
- 분배 비율 = R2/(R1+R2) = 100k/(100k+100k) = 0.5
- ADC 입력 전압 = 배터리 전압 × 0.5

**배터리 전압 계산 예시:**
- ADC 값 2048 (중간값) → ADC 전압 = 2048×3.3/4095 = 1.65V
- 실제 배터리 전압 = 1.65V × 2 = 3.3V
- ADC 값 2488 (4.2V) → ADC 전압 = 2488×3.3/4095 = 2.0V
- 실제 배터리 전압 = 2.0V × 2 = 4.0V

### 모터 제어 회로

```
ESP32-C6 GPIO2 (DI) ────┐
ESP32-C6 GPIO3 (SH_CP) ─┼─┐
ESP32-C6 GPIO15 (ST_CP) ┼─┼─┐
                        │ │ │
                     ┌──▼─▼─▼───┐
                     │ 74HC595#1│
                     │ Q0-Q3    │──→ ULN2003A#1 ──→ Motor 0
                     │ Q4-Q7    │──→ ULN2003A#2 ──→ Motor 1
                     │ Q7'      │──┐
                     └──────────┘  │
                                   │
                     ┌─────────────┘
                     │
                     │ ┌──────────┐
                     └─┤74HC595#2│
                       │ Q0-Q3   │──→ ULN2003A#3 ──→ Motor 2
                       │ Q4-Q7   │──→ ULN2003A#4 ──→ Motor 3
                       └─────────┘
```

---

## 하드웨어 테스트

### 테스트 순서

1. **전원 테스트**: LED 점등 확인
2. **디스플레이 테스트**: `tests/02_RGB_DISPLAY_TEST_GUIDE.md`
3. **버튼 테스트**: `tests/01_74HC165_TEST_GUIDE.md`
4. **오디오 테스트**: `tests/03_WAV_PLAYER_TEST_GUIDE.md`
5. **모터 테스트**: `tests/04_74HC595_STEPPER_TEST_GUIDE.md`
6. **WiFi 테스트**: `tests/05_WIFI_TEST_GUIDE.md`

### 기본 하드웨어 체크리스트

```python
# ESP32-C6 기본 확인
import machine
import time

# 1. GPIO 테스트 (Power LED / RGB Blue)
led = machine.Pin(1, machine.Pin.OUT)
led.value(1)  # LED 켜기
time.sleep(1)
led.value(0)  # LED 끄기

# 1-1. RGB LED Blue 채널 테스트 (PWM)
import machine
pwm_blue = machine.PWM(machine.Pin(1))
pwm_blue.freq(1000)  # 1kHz PWM
pwm_blue.duty(512)   # 50% 듀티 (밝기 중간)
time.sleep(1)
pwm_blue.duty(0)     # 끄기
pwm_blue.deinit()    # PWM 해제

# 2. SPI 테스트
spi = machine.SPI(1, baudrate=40000000, sck=machine.Pin(22), mosi=machine.Pin(21))
print(spi)

# 3. I2S 테스트
i2s = machine.I2S(0, sck=machine.Pin(6), ws=machine.Pin(7), sd=machine.Pin(5), 
                  mode=machine.I2S.TX, bits=16, format=machine.I2S.MONO, rate=16000)
print(i2s)

# 4. WiFi 테스트
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print(wlan.scan())

# 5. 배터리 전압 측정
import machine
adc = machine.ADC(machine.Pin(4))
adc.atten(machine.ADC.ATTN_11DB)  # 0-3.3V 범위
adc_value = adc.read()
battery_voltage = adc_value * 3.3 / 4095 * 2  # 전압 분배기 보정
print(f"ADC 값: {adc_value}, 배터리 전압: {battery_voltage:.2f}V")

# 6. 메모리 확인
import gc
gc.collect()
print(f"Free memory: {gc.mem_free()} bytes")
```

---

## 문제 해결

### 일반적인 문제

**1. 디스플레이가 작동하지 않음**
- SPI 연결 확인 (MOSI, SCK, CS, DC, RST)
- 전원 전압 확인 (3.3V)
- 오프셋 설정 확인 (X=1, Y=2)
- 백라이트 연결 확인

**2. 오디오가 재생되지 않음**
- I2S 핀 연결 확인 (BCLK, LRCLK, DIN)
- MAX98357A 전원 확인 (5V)
- SD 핀이 GND인지 확인 (셧다운 방지)
- 샘플레이트 및 포맷 확인 (16kHz, 16bit, Mono)

**3. 버튼 입력이 반응하지 않음**
- 74HC165 연결 확인 (CLK, PL, Q7)
- Pull-up 저항 확인 (10kΩ)
- 버튼이 GND로 연결되는지 확인 (Active LOW)

**4. 모터가 회전하지 않음**
- 74HC595 연결 확인 (DI, SH_CP, ST_CP)
- ULN2003A 전원 확인 (5V)
- 모터 연결 순서 확인 (A, B, C, D)
- 스텝 시퀀스 확인

**5. WiFi 연결 실패**
- 안테나 연결 확인
- 2.4GHz 대역 확인 (5GHz 지원 안 함)
- SSID 및 비밀번호 확인
- 신호 세기 확인 (RSSI > -70dBm)

### 디버깅 도구

**시리얼 모니터:**
```bash
# Windows (esptool 사용)
python -m esptool --port COM3 read_flash 0 0x400000 flash_dump.bin

# Linux/Mac (screen 사용)
screen /dev/ttyUSB0 115200

# PuTTY (Windows)
# COM 포트, 115200 baud, 8N1
```

**전압 측정:**
- 3.3V 레일: 3.2V ~ 3.4V
- 5V 레일: 4.8V ~ 5.2V
- 배터리: 3.0V ~ 4.2V

**전류 측정:**
- USB 입력: 100mA ~ 1A (동작 상태에 따라)
- 배터리 충전: ~500mA (충전 중)

---

## 참고 자료

### 데이터시트
- [ESP32-C6 Datasheet](../docs/esp32-c6_datasheet_en.pdf)
- [ST7735S Datasheet](../docs/ST7735S.pdf)
- [SN74HC165 Datasheet](../docs/sn54hc165-sn74hc165.pdf)
- [SN74HC595 Datasheet](../docs/sn74hc595n.pdf)
- [ESP32-C6 DevKit C-1 Schematics](../docs/esp32-c6-devkitc-1-schematics_v1.4.pdf)

### 관련 문서
- [ARCHITECTURE.md](ARCHITECTURE.md): 소프트웨어 아키텍처
- [README.md](README.md): 프로젝트 개요
- [tests/](../tests/): 하드웨어 단위 테스트 가이드

### 외부 링크
- [ESP32-C6 공식 문서](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c6/)
- [MicroPython 공식 문서](https://docs.micropython.org/)
- [LVGL 공식 문서](https://docs.lvgl.io/)

---

**작성일**: 2025-10-10  
**버전**: 1.0.0  
**작성자**: PillBox Development Team


