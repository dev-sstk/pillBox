# 스테퍼 모터 동작 문제 디버깅

**문제 발생일**: 2025-10-10  
**증상**: 스테퍼 모터가 동작하지 않음  
**영향 범위**: 알약 배출 및 충전 기능 전체

---

## 📊 문제 개요

### ✅ 원인 확인됨: 하드웨어 문제!

**테스트 결과 (2025-10-10):**
```
❌ 문제 보드: 모터 동작 안 됨
✅ 정상 보드: test_74hc595_stepper.py로 모터 정상 회전

결론: 특정 보드의 하드웨어 결함!
```

### 증상
- 스테퍼 모터 제어 명령을 전송해도 모터가 회전하지 않음
- 같은 코드가 **다른 보드에서는 정상 동작**
- → 소프트웨어가 아닌 **하드웨어 문제 확정**

### ✅ 확정된 원인: 스테퍼 모터 커넥터 순서 반전

**문제:**
- 28BYJ-48 스테퍼 모터 5핀 커넥터의 핀 순서가 반대로 배치됨
- 정상: Orange(A) - Yellow(B) - Red(VCC) - Pink(C) - Blue(D)
- 반전: Blue(D) - Pink(C) - Red(VCC) - Yellow(B) - Orange(A)
- → 시퀀스가 역순으로 전달되어 모터가 정상 동작하지 않음

### ~~이전 추정 원인~~ (참고용)
1. ~~74HC595D 칩 불량~~ (아님)
2. ~~납땜 불량~~ (아님)
3. ~~GPIO 핀 손상~~ (아님)
4. ~~전원 문제~~ (아님)
5. ~~Daisy Chain 연결 문제~~ (아님)

### 권장 조치
1. **보드 교체** (가장 권장)
   - 커넥터 순서가 정상인 보드 사용
   
2. **하드웨어 수정**
   - 커넥터를 뜯어내고 올바른 순서로 재배치
   - 또는 점퍼선으로 순서 교정
   
3. **소프트웨어 워크어라운드** (비권장)
   - 해당 보드 전용 시퀀스 사용
   - 유지보수 복잡도 증가

### 재현 방법
1. `test_74hc595_stepper.py` 실행
2. 문제 보드: 모터 동작 안 됨
3. 정상 보드: 모터 정상 회전

---

## 🔍 초기화 로직 분석

### 1. 핀 초기화 (StepperMotorController.__init__)

```python
# GPIO 핀 설정
self.di = Pin(2, Pin.OUT)      # 74HC595 Data Input
self.sh_cp = Pin(3, Pin.OUT)   # 74HC595 Shift Clock (74HC165와 공유)
self.st_cp = Pin(15, Pin.OUT)  # 74HC595 Storage Clock (74HC165와 공유)

# 초기 상태 설정
self.di.value(0)      # Data Input: LOW
self.sh_cp.value(0)   # Shift Clock: LOW
self.st_cp.value(0)   # Storage Clock: LOW
```

**핀 상태 체크포인트:**
- ✅ GPIO 2, 3, 15가 OUTPUT 모드로 설정되었는가?
- ✅ 초기값이 모두 LOW인가?

### 2. 모터 상태 초기화

```python
# 4개 모터의 현재 상태 (각 모터당 8비트)
self.motor_states = [0, 0, 0, 0]

# 각 모터별 독립적인 스텝 상태
self.motor_steps = [0, 0, 0, 0]  # 현재 시퀀스 위치 (0~7)
self.motor_positions = [0, 0, 0, 0]  # 현재 칸 위치

# 속도 설정
self.step_delay_us = 1  # 스텝 간 지연 시간 (마이크로초) - 최고속
```

**문제점 1: 너무 빠른 속도**
- 현재: 1µs (1,000,000 Hz) - **너무 빠름**
- 권장: 200µs ~ 2000µs (500 ~ 5000 Hz)
- 이유: 하드웨어 응답 시간, 기계적 관성

### 3. ULN2003A 초기화 (중요!)

```python
def initialize_uln2003_high(self):
    """ULN2003A 출력 1C,2C,3C,4C HIGH 상태로 초기화"""
    print("⚡ ULN2003A 출력 초기화: 1C,2C,3C,4C HIGH 설정")
    
    # 모든 모터의 상태를 HIGH (0x0F)로 설정
    # 0x0F = 0b00001111 (1C,2C,3C,4C 모두 HIGH)
    for i in range(4):
        self.motor_states[i] = 0x0F
    
    # 74HC595D에 출력
    self.update_motor_output()
    print("✅ ULN2003A 출력 초기화 완료: 모든 출력 HIGH")
```

**문제점 2: HIGH 초기화의 의미**
- ULN2003A는 **Active LOW** 드라이버
- HIGH 입력 → ULN2003A 출력 OFF
- **0x0F로 초기화하면 모든 코일이 OFF 상태**
- 스텝 시퀀스가 HIGH/LOW를 반복해야 함

**대조: 테스트 파일에는 HIGH 초기화 없음**
```python
# test_74hc595_stepper.py에서는
self.motor_states = [0, 0, 0, 0]  # 모두 LOW로 시작
# initialize_uln2003_high() 함수 없음
```

---

## 🔧 동작 로직 분석

### 1. 스텝 시퀀스 (8 Half Step)

```python
self.stepper_sequence = [
    0b00001000,  # 0x08 - A만 HIGH
    0b00001100,  # 0x0C - A,B HIGH
    0b00000100,  # 0x04 - B만 HIGH
    0b00000110,  # 0x06 - B,C HIGH
    0b00000010,  # 0x02 - C만 HIGH
    0b00000011,  # 0x03 - C,D HIGH
    0b00000001,  # 0x01 - D만 HIGH
    0b00001001   # 0x09 - D,A HIGH
]
```

**시퀀스 해석:**
- 28BYJ-48 유니폴라 스테퍼 모터용
- Half Step 방식 (부드러운 동작)
- 각 비트: `DCBA` (역순)

### 2. 모터 상태 업데이트 프로세스

```python
def set_motor_step(self, motor_index, step_value):
    """특정 모터의 스텝 설정"""
    if 0 <= motor_index <= 3:
        # 시퀀스에서 값 가져오기
        self.motor_states[motor_index] = self.stepper_sequence[step_value % 8]
        # 74HC595D로 출력
        self.update_motor_output()
```

### 3. 74HC595D 데이터 전송

```python
def shift_out(self, data):
    """74HC595D에 8비트 데이터 전송"""
    for i in range(8):
        # MSB first
        bit = (data >> (7 - i)) & 1
        self.di.value(bit)
        
        # Shift clock pulse
        self.sh_cp.value(1)
        self.sh_cp.value(0)
    
    # Storage clock pulse (latch)
    self.st_cp.value(1)
    self.st_cp.value(0)
```

**타이밍 분석:**
- Shift 클럭: HIGH → LOW (데이터 이동)
- Storage 클럭: HIGH → LOW (출력 래치)
- **딜레이 없음 → 매우 높은 문제 가능성!**

**74HC595D 데이터시트 요구사항:**
- Setup Time (tsu): 최소 10ns
- Hold Time (th): 최소 10ns  
- Pulse Width (tw): 최소 10ns
- **ESP32-C6 GPIO 전환 시간을 고려하면 충분하지 않을 수 있음**

### 4. 모터 출력 매핑

```python
def update_motor_output(self):
    """모든 모터 상태를 74HC595D에 출력"""
    combined_data = 0

    # 모터0 → 하위 4비트 (Q0~Q3 of 1번 칩)
    combined_data |= (self.motor_states[0] & 0x0F)

    # 모터1 → 상위 4비트 (Q4~Q7 of 1번 칩)
    combined_data |= ((self.motor_states[1] & 0x0F) << 4)

    # 모터2 → 하위 4비트 (Q0~Q3 of 2번 칩)
    combined_data |= ((self.motor_states[2] & 0x0F) << 8)

    # 모터3 → 상위 4비트 (Q4~Q7 of 2번 칩)
    combined_data |= ((self.motor_states[3] & 0x0F) << 12)

    # 전송 (상위 바이트 먼저)
    upper_byte = (combined_data >> 8) & 0xFF  # 2번 칩
    lower_byte = combined_data & 0xFF         # 1번 칩

    self.shift_out(upper_byte)  # 먼저 전송
    self.shift_out(lower_byte)  # 나중 전송
```

**데이터 흐름:**
```
ESP32 → 2번 74HC595 → 1번 74HC595
       (모터 2,3)     (모터 0,1)
```

### 5. 회전 로직

```python
def next_compartment(self, motor_index):
    """다음 칸으로 이동 - 리미트 스위치 기반"""
    step_count = 0
    
    # 리미트 스위치가 눌릴 때까지 회전
    while not self.is_limit_switch_pressed(motor_index):
        # 1스텝씩 이동 (역방향)
        self.motor_steps[motor_index] = (self.motor_steps[motor_index] - 1) % 8
        current_step = self.motor_steps[motor_index]
        self.motor_states[motor_index] = self.stepper_sequence[current_step]
        self.update_motor_output()
        
        # 속도 조절
        time.sleep_us(1000)  # 1ms 지연
        step_count += 1
    
    # 리미트 스위치가 떼질 때까지 계속 회전
    while self.is_limit_switch_pressed(motor_index):
        # (동일한 로직)
        time.sleep_us(1000)  # 1ms 지연
```

**문제점 3: 실제 속도는 1ms**
- `step_delay_us = 1` 설정은 무시됨
- 실제로는 `time.sleep_us(1000)` 사용 (1ms)
- 불일치로 인한 혼란

---

## 🐛 발견된 문제점

### ✅ ULN2003A HIGH 초기화 - 정상 동작
**현재 상태:**
```python
# 초기화 시
self.motor_states = [0x0F, 0x0F, 0x0F, 0x0F]  # 모두 HIGH
```

**확인 사항:**
- ✅ ULN2003A 입력 HIGH → 출력 LOW (스테퍼 구동)
- ✅ 미사용 시 HIGH 초기화 = 과전류 방지 (정상)
- ✅ 이 부분은 문제 없음!

**하드웨어 엔지니어 확인:**
> "ULN2003A는 출력이 LOW일 때 스테퍼 구동이라 구동 안 할 때는 HIGH로 초기화해줘야 됨.  
> 안 그러면 보드가 과전류 상태가 될 수 있어서 어떤 소자에 문제가 생길 수 있음."

---

### 🔴 높은 우선순위 - 진짜 문제들

#### 1. 74HC595D 타이밍 문제 (가장 유력!)
**현재 상태:**
```python
self.sh_cp.value(1)  # 딜레이 없음
self.sh_cp.value(0)
```

**문제 분석:**
```
ESP32-C6 GPIO 전환 속도: 수십 MHz 가능
하지만 실제로는:
1. 명령 실행 시간
2. 함수 호출 오버헤드
3. MicroPython 인터프리터 지연
4. 74HC595D 응답 시간

딜레이 없이 연속 GPIO 전환 시:
→ 데이터 비트가 제대로 시프트되지 않음
→ 74HC595D 출력이 잘못된 값
→ 모터가 엉뚱한 신호를 받음
→ 회전하지 않거나 떨림
```

**증거:**
- test_74hc595_stepper.py에서는 딜레이 없이도 동작함
- 하지만 실제 시스템에서는 2개 칩을 연속으로 제어
- 더 복잡한 로직으로 인한 타이밍 마진 부족

**해결 방안 (필수!):**
```python
def shift_out(self, data):
    """74HC595D에 8비트 데이터 전송 (타이밍 개선)"""
    for i in range(8):
        bit = (data >> (7 - i)) & 1
        self.di.value(bit)
        time.sleep_us(1)  # 1µs 대기
        
        self.sh_cp.value(1)
        time.sleep_us(1)  # 1µs 대기
        self.sh_cp.value(0)
        time.sleep_us(1)  # 1µs 대기
    
    self.st_cp.value(1)
    time.sleep_us(1)  # 1µs 대기
    self.st_cp.value(0)
```

#### 2. 스텝 시퀀스가 실제로 전송되지 않음 (매우 유력!)

**현재 로직:**
```python
# 초기화: 모든 모터 0x0F (HIGH)
self.motor_states = [0x0F, 0x0F, 0x0F, 0x0F]

# 첫 스텝 시퀀스 실행
self.motor_steps[0] = 0  # 시퀀스 인덱스 0
self.motor_states[0] = self.stepper_sequence[0]  # 0x08
self.update_motor_output()  # 전송!
```

**문제 가능성:**
```
초기: [0x0F, 0x0F, 0x0F, 0x0F]
첫 스텝: [0x08, 0x0F, 0x0F, 0x0F]

Combined data:
Lower byte = 0x0F | (0x0F << 4) = 0xFF (모터 0,1)
Upper byte = 0x0F | (0x0F << 4) = 0xFF (모터 2,3)

아니다... 0x08 | (0x0F << 4) = 0xF8

그런데 문제는:
1. 74HC595D 타이밍 문제로 0xF8이 제대로 전송 안됨
2. 또는 시프트 순서 문제
```

**디버깅 필요:**
- 실제로 74HC595D 출력 핀에서 전압 측정
- 오실로스코프로 클럭 신호 확인
- 데이터가 올바르게 시프트되는지 확인

#### 3. 리미트 스위치 비트 순서 불일치
**motor_control.py:**
```python
self.limit_switches = [
    LimitSwitch(self.input_shift_register, 6),  # 모터 0 (역순)
    LimitSwitch(self.input_shift_register, 5),  # 모터 1
    LimitSwitch(self.input_shift_register, 4),  # 모터 2 (역순)
    LimitSwitch(self.input_shift_register, 7),  # 모터 3
]
```

**test_74hc595_stepper.py:**
```python
self.limit_switches = [
    LimitSwitch(self.input_shift_register, 4),  # 모터 0
    LimitSwitch(self.input_shift_register, 5),  # 모터 1
    LimitSwitch(self.input_shift_register, 6),  # 모터 2
    LimitSwitch(self.input_shift_register, 7),  # 모터 3
]
```

**해결 방안:**
```python
# 하드웨어 연결에 맞춰 통일
self.limit_switches = [
    LimitSwitch(self.input_shift_register, 4),  # 모터 0: LIMIT SW1
    LimitSwitch(self.input_shift_register, 5),  # 모터 1: LIMIT SW2
    LimitSwitch(self.input_shift_register, 6),  # 모터 2: LIMIT SW3
    LimitSwitch(self.input_shift_register, 7),  # 모터 3: LIMIT SW4
]
```

#### 4. 74HC165/74HC595 클럭 공유로 인한 간섭 (매우 유력!)

**현재 상태:**
```python
# 동일한 GPIO 핀을 공유
sh_cp_pin = 3   # 74HC595 Shift Clock
clock_pin = 3   # 74HC165 Clock (동일!)

st_cp_pin = 15  # 74HC595 Storage Clock
pload_pin = 15  # 74HC165 Parallel Load (동일!)
```

**문제 시나리오:**
```
1. next_compartment() 함수 실행
2. 루프 시작:
   - is_limit_switch_pressed() 호출
   - → input_shift_register.read_byte()
   - → GPIO 3 (CLK) 펄스 8번 발생
   - → 74HC595도 같은 클럭 받음!
   - → 74HC595 데이터가 엉뚱하게 시프트됨!
3. motor_states 업데이트
   - → update_motor_output()
   - → GPIO 3 (SH_CP) 펄스 16번 발생
   - → 74HC165도 같은 클럭 받음!
   - → 리미트 스위치 읽기 오류!
```

**결과:**
- 모터 출력이 계속 변경됨
- 정상적인 스텝 시퀀스가 전달되지 않음
- 모터가 떨리거나 아예 회전하지 않음

**해결 방안 (필수!):**
```python
# 방법 1: 리미트 스위치 읽기를 별도 시점에만
def next_compartment(self, motor_index):
    # 먼저 한 번만 체크
    if self.is_limit_switch_pressed(motor_index):
        return  # 이미 눌려있으면 종료
    
    # 이후로는 체크하지 않고 고정 스텝만 회전
    for _ in range(136):  # 1칸 = 136 스텝
        self.motor_steps[motor_index] = (self.motor_steps[motor_index] - 1) % 8
        current_step = self.motor_steps[motor_index]
        self.motor_states[motor_index] = self.stepper_sequence[current_step]
        self.update_motor_output()
        time.sleep_us(1000)

# 방법 2: 클럭 공유 시 충분한 대기
def is_limit_switch_pressed(self, motor_index):
    # 모터 출력 완전히 완료 대기
    time.sleep_us(100)  # 100µs 대기
    return self.limit_switches[motor_index].is_pressed()
```

### 🟡 중간 우선순위

#### 5. 속도 설정 불일치
**문제:**
```python
# 설정값
self.step_delay_us = 1  # 1µs

# 실제 사용
time.sleep_us(1000)  # 1000µs = 1ms
```

**해결 방안:**
```python
# next_compartment() 함수 수정
time.sleep_us(self.step_delay_us)  # 설정값 사용

# 또는 적절한 기본값 설정
self.step_delay_us = 1000  # 1ms (1000 Hz)
```

#### 6. 데이터 전송 순서 문제

**현재:**
```python
# 상위 바이트 먼저 (모터 2,3)
self.shift_out(upper_byte)
# 하위 바이트 나중 (모터 0,1)
self.shift_out(lower_byte)
```

**문제 가능성:**
- Daisy Chain 연결: ESP32 → 2번 칩 → 1번 칩
- 상위 바이트가 2번 칩으로 가야 하는데 1번 칩에 들어갈 수 있음
- 또는 반대

**확인 필요:**
- 하드웨어 연결 확인
- 어떤 칩이 먼저 연결되어 있는지

---

## ✅ 권장 수정 사항 (우선순위별)

### 🔴 최우선: 74HC595D 타이밍 개선

**이것이 가장 유력한 원인!**

```python
def shift_out(self, data):
    """74HC595D에 8비트 데이터 전송 (타이밍 개선 - 필수!)"""
    for i in range(8):
        bit = (data >> (7 - i)) & 1
        self.di.value(bit)
        time.sleep_us(1)  # ← 필수! Setup time 보장
        
        self.sh_cp.value(1)
        time.sleep_us(1)  # ← 필수! Pulse width 보장
        self.sh_cp.value(0)
        time.sleep_us(1)  # ← 필수! Hold time 보장
    
    self.st_cp.value(1)
    time.sleep_us(1)  # ← 필수!
    self.st_cp.value(0)
    time.sleep_us(1)  # ← 필수!

print("✅ 타이밍 개선으로 안정적인 데이터 전송 보장")
```

**예상 효과:**
- 74HC595D가 모든 비트를 정확하게 받음
- 출력이 안정적으로 변경됨
- 모터가 정상 회전

### 🔴 2순위: 클럭 공유 문제 해결

**74HC165 읽기 시 74HC595 간섭 방지:**

```python
def is_limit_switch_pressed(self, motor_index):
    """리미트 스위치 상태 확인 (간섭 방지)"""
    if 0 <= motor_index <= 3:
        # 모터 출력 완전 완료 대기 (중요!)
        time.sleep_us(100)  # 100µs 대기
        
        # 리미트 스위치 읽기
        is_pressed = self.limit_switches[motor_index].is_pressed()
        
        # 읽기 후 다시 대기 (안정화)
        time.sleep_us(50)
        
        return is_pressed
    return False
```

**또는 더 간단한 방법:**
```python
def next_compartment(self, motor_index):
    """다음 칸으로 이동 (리미트 스위치 최소 사용)"""
    
    # 고정 스텝 수로 회전 (리미트 스위치 의존도 낮춤)
    for _ in range(136):  # 1칸 = 136 스텝 (2048/15)
        self.motor_steps[motor_index] = (self.motor_steps[motor_index] - 1) % 8
        current_step = self.motor_steps[motor_index]
        self.motor_states[motor_index] = self.stepper_sequence[current_step]
        self.update_motor_output()
        time.sleep_us(1000)  # 1ms
    
    print(f"모터 {motor_index} 1칸 이동 완료")
```

### 🟡 3순위: 리미트 스위치 비트 순서

```python
# 하드웨어 연결에 맞춰 수정
self.limit_switches = [
    LimitSwitch(self.input_shift_register, 4),  # 모터 0
    LimitSwitch(self.input_shift_register, 5),  # 모터 1
    LimitSwitch(self.input_shift_register, 6),  # 모터 2
    LimitSwitch(self.input_shift_register, 7),  # 모터 3
]
```

### 🟡 4순위: 속도 설정 통일

```python
def next_compartment(self, motor_index):
    # ... (기존 코드)
    
    # ❌ 기존: 하드코딩된 딜레이
    # time.sleep_us(1000)
    
    # ✅ 새로운: 설정값 사용
    time.sleep_us(self.step_delay_us)
```

---

## 🎯 최종 결론

### 가장 유력한 원인 (우선순위순)

#### 1️⃣ 74HC595D 타이밍 문제 (90% 확률)
**증상과 일치:**
- 딜레이 없이 고속 GPIO 전환
- 2개 칩 연속 제어로 더 복잡
- 데이터가 제대로 시프트되지 않을 가능성 높음

**해결책:**
- 각 GPIO 전환마다 1µs 딜레이 추가
- 총 전송 시간: 약 50µs (충분히 빠름)

#### 2️⃣ 74HC165/74HC595 클럭 공유 간섭 (70% 확률)
**증상과 일치:**
- 리미트 스위치 체크할 때마다 모터 출력 교란
- 연속 회전 중 읽기 → 스텝 시퀀스 깨짐

**해결책:**
- 리미트 스위치 읽기 전후 대기
- 또는 고정 스텝 수 사용

#### 3️⃣ 리미트 스위치 비트 순서 (30% 확률)
**증상과 일치:**
- 원점 보정이 안 될 수 있음
- 하지만 회전 자체는 가능해야 함

**해결책:**
- 하드웨어 연결 확인 후 수정

### 권장 조치 순서

1. **먼저 시도**: 74HC595D 타이밍 개선 (`shift_out` 함수에 딜레이 추가)
2. **두 번째**: 리미트 스위치 읽기 시 대기 추가
3. **세 번째**: 리미트 스위치 비트 순서 확인

---

## 🧪 테스트 계획

### 단계별 테스트

#### 1. 74HC595D 출력 테스트
```python
# 간단한 출력 테스트
controller = StepperMotorController()

# 모든 비트 HIGH
controller.motor_states[0] = 0x0F
controller.update_motor_output()
time.sleep(1)

# 모든 비트 LOW
controller.motor_states[0] = 0x00
controller.update_motor_output()
time.sleep(1)

# 멀티미터로 출력 전압 측정
```

#### 2. 단일 코일 테스트
```python
# 코일 A만 활성화
controller.motor_states[0] = 0b00001000  # A만 HIGH
controller.update_motor_output()
time.sleep(1)

# 코일 B만 활성화
controller.motor_states[0] = 0b00000100  # B만 HIGH
controller.update_motor_output()
time.sleep(1)

# (C, D 반복)
```

#### 3. 시퀀스 패턴 테스트
```python
# 8스텝 시퀀스를 천천히 실행
for step in range(8):
    print(f"Step {step}: 0x{controller.stepper_sequence[step]:02X}")
    controller.set_motor_step(0, step)
    time.sleep(500)  # 0.5초 대기
```

#### 4. 저속 회전 테스트
```python
# 매우 느린 속도로 회전
controller.set_speed(10)  # 10ms = 100Hz
controller.rotate_motor(0, 1, 0.1)  # 0.1회전
```

#### 5. 리미트 스위치 테스트
```python
# 리미트 스위치 상태 확인
while True:
    states = controller.check_limit_switches()
    print(f"Limit Switches: {states}")
    time.sleep(100)
```

---

## 📊 디버깅 체크리스트

### 하드웨어 확인
- [ ] ESP32-C6 GPIO 2, 3, 15 출력 확인
- [ ] 74HC595D 전원 (VCC = 3.3V, GND)
- [ ] 74HC595D 칩 간 연결 (Q7' → SER)
- [ ] ULN2003A 전원 (VCC = 5V, GND)
- [ ] 28BYJ-48 전원 (5V)
- [ ] 모터 코일 저항 측정 (약 50Ω)

### 소프트웨어 확인
- [ ] 초기화 시 HIGH → LOW 변경
- [ ] 타이밍 딜레이 추가 (1µs)
- [ ] 리미트 스위치 비트 순서 수정
- [ ] 속도 설정 통일 (1ms)
- [ ] 시퀀스 방향 확인 (+ 또는 -)

### 신호 측정
- [ ] GPIO 2 (DI) 출력 확인 (오실로스코프)
- [ ] GPIO 3 (SH_CP) 클럭 확인
- [ ] GPIO 15 (ST_CP) 래치 확인
- [ ] 74HC595D 출력 (Q0~Q7) 확인
- [ ] ULN2003A 출력 (1C~4C) 확인
- [ ] 모터 코일 전압 측정

---

## 📝 추가 참고 사항

### ULN2003A 동작 원리 (확인됨 ✅)
```
입력 (1B)    ULN2003A    출력 (1C)    모터 코일      설명
─────────────────────────────────────────────────────────────
LOW          OFF         5V (HIGH)    비여자 (OFF)   대기 상태
HIGH         ON          0V (LOW)     여자 (ON)      전류 흐름
```

**중요:**
- 출력이 LOW일 때 스테퍼 구동 (코일에 전류 흐름)
- 미사용 시 HIGH 초기화 필수 (과전류 방지)
- 0x0F (모두 HIGH) 초기화는 정상 동작!

### 28BYJ-48 권장 구동 속도
- 최소: 1 step/100ms (10 Hz) - 매우 느림
- 권장: 1 step/2ms (500 Hz) - 부드러움
- 최대: 1 step/0.5ms (2000 Hz) - 빠름
- **현재 1µs는 너무 빠름!**

### 전류 소모
- 28BYJ-48 단일 코일: ~200mA
- 4코일 동시: ~200mA (공통 전원)
- ULN2003A 최대: 500mA
- 4개 모터 동시 동작: ~800mA

---

## 🔗 관련 파일

- `src/motor_control.py`: 모터 제어 로직
- `tests/test_74hc595_stepper.py`: 테스트 코드
- `src/HARDWARE.md`: 하드웨어 핀맵
- `tests/04_74HC595_STEPPER_TEST_GUIDE.md`: 테스트 가이드

---

**작성일**: 2025-10-10  
**작성자**: PillBox Debug Team  
**최종 업데이트**: 2025-10-10 (원인 확정: 커넥터 반전)  
**해결 상태**: ✅ 원인 확정 - 보드 제조 오류 (스테퍼 모터 커넥터 핀 순서 반전)

---

## 🔴 긴급 업데이트 - 하드웨어 문제 확인됨!

### 테스트 결과 (2025-10-10)

**테스트 환경:**
- 테스트 파일: `test_74hc595_stepper.py`
- 결과: **다른 보드에서는 정상 동작 확인!**

**결론:**
```
❌ 문제 보드: 모터 동작 안 됨
✅ 정상 보드: test_74hc595_stepper.py로 모터 정상 회전

→ 소프트웨어 문제 아님!
→ 특정 보드의 하드웨어 문제!
```

### 🔍 하드웨어 문제 가능성 (우선순위순)

#### 1️⃣ 74HC595D 칩 불량 (가장 유력!)
**증상:**
- 같은 코드가 다른 보드에서는 동작
- 데이터 전송은 되지만 출력이 안 나옴

**확인 방법:**
```
1. 74HC595D 전원 확인
   - VCC = 3.3V
   - GND 연결 확인
   
2. 클럭 신호 확인 (오실로스코프)
   - SH_CP (GPIO 3) 신호 확인
   - ST_CP (GPIO 15) 신호 확인
   
3. 출력 핀 전압 측정
   - Q0~Q7 출력 확인
   - 멀티미터로 측정
   
4. 칩 교체 시도
```

#### 2️⃣ 납땜 불량 (매우 가능!)
**문제 가능성:**
- 74HC595D 핀 접촉 불량
- Cold Joint (불완전한 납땜)
- 브리지 (인접 핀 단락)

**확인 방법:**
```
1. 육안 검사
   - 74HC595D 핀 납땜 상태
   - 광택 나는 부분 vs 무광택 부분
   
2. 멀티미터 연속성 테스트
   - ESP32 GPIO → 74HC595D 핀
   - 74HC595D → ULN2003A 연결
   - 74HC595D 칩 간 Q7' → SER 연결
   
3. 재납땜 시도
   - 플럭스 추가
   - 적절한 온도 (350°C)
```

#### 3️⃣ GPIO 핀 손상
**문제 가능성:**
- ESP32-C6 GPIO 2, 3, 15 손상
- 과전압/과전류로 인한 핀 손상

**확인 방법:**
```python
# GPIO 테스트 코드
from machine import Pin
import time

# GPIO 2 테스트
p2 = Pin(2, Pin.OUT)
for _ in range(10):
    p2.value(1)
    print(f"GPIO 2: HIGH = {p2.value()}")
    time.sleep(0.1)
    p2.value(0)
    print(f"GPIO 2: LOW = {p2.value()}")
    time.sleep(0.1)

# GPIO 3, 15도 동일하게 테스트
```

#### 4️⃣ 전원 문제
**문제 가능성:**
- 3.3V 레귤레이터 출력 부족
- 전압 강하 (Voltage Drop)
- 노이즈

**확인 방법:**
```
1. 3.3V 레일 전압 측정
   - 무부하: 3.3V
   - 부하 시: 3.2V 이상 유지되어야 함
   
2. 전류 소모 측정
   - 74HC595D × 2: ~20mA
   - 정상 범위 확인
   
3. 바이패스 커패시터 확인
   - 74HC595D VCC 근처 0.1µF
```

#### 5️⃣ Daisy Chain 연결 문제
**문제 가능성:**
- 1번 칩 Q7' → 2번 칩 SER 연결 끊김
- 잘못된 연결

**확인 방법:**
```
1. 멀티미터로 연속성 확인
   - 1번 칩 Pin 9 (Q7') → 2번 칩 Pin 14 (SER)
   
2. 단일 칩만 테스트
   - 2번 칩 연결 해제
   - 1번 칩만으로 모터 0, 1 테스트
```

### 📋 권장 조치 순서

#### 1단계: 기본 확인
```
□ 전원 전압 측정 (3.3V)
□ 74HC595D 발열 확인 (과열 시 불량)
□ 육안 검사 (납땜, 브리지)
```

#### 2단계: 간단한 테스트
```python
# 단순 출력 테스트
from machine import Pin
import time

di = Pin(2, Pin.OUT)
sh_cp = Pin(3, Pin.OUT)
st_cp = Pin(15, Pin.OUT)

# 모든 비트 HIGH 출력
for i in range(8):
    di.value(1)
    sh_cp.value(1)
    sh_cp.value(0)

st_cp.value(1)
st_cp.value(0)

# 멀티미터로 74HC595D 출력 확인
time.sleep(5)
```

#### 3단계: 시그널 측정
```
오실로스코프 확인:
□ GPIO 2 (DI) - 데이터 신호 있는가?
□ GPIO 3 (SH_CP) - 클럭 신호 있는가?
□ GPIO 15 (ST_CP) - 래치 신호 있는가?
□ 74HC595D Q0~Q7 - 출력 나오는가?
```

#### 4단계: 부품 교체
```
□ 74HC595D #1 교체
□ 74HC595D #2 교체
□ ESP32-C6 보드 교체 (이미 확인됨 - 다른 보드는 OK)
```

### 🎯 최종 결론

**✅ 원인 확정: 스테퍼 모터 커넥터 순서 반전!**

**문제:**
- 스테퍼 모터 커넥터(5핀)의 핀 순서가 반대로 설계/제조됨
- 28BYJ-48 모터의 코일 A, B, C, D 순서가 반전됨
- → 올바른 시퀀스를 보내도 모터가 정상 동작하지 않음

**증상:**
- 소프트웨어: 정상 ✅
- 다른 보드: 정상 동작 ✅
- 문제 보드: 커넥터 반전으로 동작 안 됨 ❌

**해결 방안:**
1. **하드웨어 수정** (권장)
   - 커넥터 재배치
   - 점퍼선으로 올바른 순서로 연결
   
2. **소프트웨어 워크어라운드**
   - 시퀀스 배열을 반전시킴
   ```python
   # 정상 시퀀스
   self.stepper_sequence = [0x08, 0x0C, 0x04, 0x06, 0x02, 0x03, 0x01, 0x09]
   
   # 반전 커넥터용 시퀀스 (비트 순서 역전)
   self.stepper_sequence_reversed = [0x01, 0x09, 0x08, 0x0C, 0x04, 0x06, 0x02, 0x03]
   ```

**보드 불량 확인:**
- 제조 오류: 커넥터 핀 순서 반전
- 다른 보드는 정상이므로 제조 공정 중 일부 보드에서만 발생
- 권장: 해당 보드 교체 또는 하드웨어 수정

---

---

# WiFi 스캔 동작 문제 디버깅

**문제 발생일**: 2025-10-13  
**증상**: WiFi 네트워크 스캔 시 0개 결과 반환  
**영향 범위**: WiFi 초기 설정 기능 전체

---

## 📊 문제 개요

### 증상
- WiFi 스캔 실행은 되지만 원시 스캔 결과가 0개
- 실제로 주변에 WiFi 네트워크가 존재함에도 불구하고 감지 안 됨
- WiFi 활성화 상태는 True로 정상

### 로그 분석
```
📡 WiFi 네트워크 스캔 시작...
  📡 WiFi 활성 상태: True
  📡 스캔 실행 중...
  📡 원시 스캔 결과: 0개
  ⚠️ 스캔 결과가 비어있음
✅ 0개 네트워크 스캔 완료
```

### 재시도 로직 실행
```
  📡 스캔 결과 없음, 2초 대기 후 재시도...
  📡 2차 스캔 시도...
📡 WiFi 네트워크 스캔 시작...
  📡 WiFi 활성 상태: True
  📡 스캔 실행 중...
  📡 원시 스캔 결과: 0개
  ⚠️ 스캔 결과가 비어있음
✅ 0개 네트워크 스캔 완료
⚠️ WiFi 스캔 결과가 없습니다
  💡 ESP32-C6 WiFi가 제대로 초기화되지 않았을 수 있습니다
```

---

## 🔍 원인 분석

### 1️⃣ ESP32-C6 WiFi 초기화 문제 (가장 유력!)

**가능한 원인:**
- WiFi 모듈이 활성화는 되었으나 실제로 RF가 동작하지 않음
- WiFi 펌웨어 초기화 실패
- 안테나 문제

**확인 사항:**
```python
# wifi_manager.py 초기화
self.wifi = network.WLAN(network.STA_IF)
self.wifi.active(True)  # ← 이것만으로는 부족할 수 있음
```

**ESP32-C6 특이사항:**
- ESP32-C6는 WiFi 6 (802.11ax) 지원
- 일부 펌웨어에서 WiFi 초기화 지연 필요
- 스캔 전 충분한 대기 시간 필요

### 2️⃣ MicroPython 펌웨어 문제

**현재 펌웨어:**
```
ESP32_GENERIC_C6-20250911_I2S+LVGL+KrFont.bin
```

**가능한 문제:**
- 커스텀 펌웨어에 WiFi 드라이버 이슈
- WiFi 스캔 함수 버그
- ESP-IDF 버전 문제

**확인 방법:**
```python
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print(wlan.config('mac'))  # MAC 주소 출력되는지 확인
print(wlan.status())  # 상태 코드 확인
```

### 3️⃣ 하드웨어 문제

**가능성:**
- WiFi 안테나 연결 불량
- RF 회로 문제
- 보드 제조 결함

**증거:**
- 같은 펌웨어를 다른 보드에서 테스트 필요
- 만약 다른 보드에서는 작동한다면 하드웨어 문제 확정

### 4️⃣ 스캔 타이밍 문제

**현재 로직:**
```python
# WiFi 활성화 후 즉시 스캔
if not self.wifi.active():
    self.wifi.active(True)
    time.sleep_ms(500)  # 500ms 대기

scan_results = self.wifi.scan()  # 바로 스캔
```

**문제:**
- ESP32-C6는 WiFi 초기화에 더 많은 시간 필요 가능
- 500ms로는 부족할 수 있음

---

## 🔧 해결 방안

### 1단계: 대기 시간 증가

```python
def scan_networks(self, force=False):
    # WiFi 활성화 확인
    if not self.wifi.active():
        print("  📡 WiFi 비활성 상태 감지, 활성화 중...")
        self.wifi.active(True)
        time.sleep_ms(2000)  # 500ms → 2000ms로 증가
    
    # 스캔 전 추가 대기
    time.sleep_ms(500)
    
    # WiFi 스캔 실행
    scan_results = self.wifi.scan()
```

### 2단계: WiFi 재초기화

```python
def scan_networks(self, force=False):
    # WiFi 재초기화 시도
    print("  📡 WiFi 재초기화 시도...")
    self.wifi.active(False)
    time.sleep_ms(500)
    self.wifi.active(True)
    time.sleep_ms(2000)
    
    # 스캔 실행
    scan_results = self.wifi.scan()
```

### 3단계: 명시적 스캔 옵션

```python
def scan_networks(self, force=False):
    # 스캔 옵션 명시
    print("  📡 WiFi 스캔 (모든 채널)...")
    scan_results = self.wifi.scan(
        # show_hidden=True,  # 숨겨진 네트워크도 표시
    )
```

### 4단계: 디버깅 정보 추가

```python
def scan_networks(self, force=False):
    # WiFi 상태 상세 확인
    print(f"  📡 WiFi MAC: {':'.join(['%02x' % b for b in self.wifi.config('mac')])}")
    print(f"  📡 WiFi Status: {self.wifi.status()}")
    print(f"  📡 WiFi Channel: {self.wifi.config('channel')}")
    
    # 스캔 실행
    scan_results = self.wifi.scan()
```

### 5단계: 펌웨어 문제 확인

```python
# REPL에서 직접 테스트
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
import time
time.sleep(2)
scan_results = wlan.scan()
print(f"스캔 결과: {len(scan_results)}개")
for result in scan_results:
    print(result)
```

---

## 🧪 테스트 계획

### 1. REPL 직접 테스트
```python
# Thonny나 mpremote로 직접 실행
>>> import network
>>> wlan = network.WLAN(network.STA_IF)
>>> wlan.active(True)
>>> import time
>>> time.sleep(2)
>>> results = wlan.scan()
>>> print(len(results))
>>> for r in results:
...     print(r[0].decode('utf-8'), r[3])
```

**예상 결과:**
- 정상: 주변 WiFi 네트워크 목록 출력
- 문제: 0개 또는 에러 발생

### 2. 다른 보드에서 테스트
- 동일한 펌웨어를 다른 ESP32-C6 보드에 업로드
- 같은 코드 실행
- 결과 비교

### 3. 표준 펌웨어 테스트
- MicroPython 공식 ESP32-C6 펌웨어 설치
- WiFi 스캔 테스트
- 정상 동작 확인 시 커스텀 펌웨어 문제

---

## 📋 권장 조치 순서

### 즉시 조치:
1. **REPL 직접 테스트** (5분)
   - WiFi 스캔이 REPL에서는 되는지 확인

2. **대기 시간 증가** (10분)
   - 500ms → 2000ms
   - 스캔 전 추가 대기 500ms

3. **WiFi 재초기화** (10분)
   - active(False) → active(True)

### 추가 확인:
4. **다른 보드 테스트** (30분)
   - 하드웨어 문제 여부 확인

5. **공식 펌웨어 테스트** (1시간)
   - 커스텀 펌웨어 문제 여부 확인

6. **안테나 확인** (10분)
   - 물리적 연결 상태 확인

---

## 🎯 결론

### 가장 유력한 원인 (우선순위순)

#### 1️⃣ ESP32-C6 WiFi 초기화 타이밍 문제 (70%)
**증상:**
- WiFi active는 True이지만 스캔 결과 0개
- 하드웨어는 정상이지만 RF가 준비 안됨

**해결책:**
- 대기 시간 증가 (500ms → 2000ms)
- WiFi 재초기화 시도

#### 2️⃣ 커스텀 펌웨어 WiFi 드라이버 버그 (60%)
**증상:**
- LVGL + I2S + 한글폰트 통합 펌웨어
- WiFi 기능 테스트 부족 가능성

**해결책:**
- 공식 MicroPython 펌웨어로 테스트
- WiFi 동작 확인 후 커스텀 펌웨어 재빌드

#### 3️⃣ 하드웨어 문제 (30%)
**증상:**
- 안테나 연결 불량
- RF 회로 문제

**해결책:**
- 다른 보드에서 테스트
- 안테나 재연결

---

## 📝 관련 파일

- `src/wifi_manager.py`: WiFi 관리 시스템
- `src/screens/wifi_scan_screen.py`: WiFi 스캔 화면
- `firmware/ESP32_GENERIC_C6-20250911_I2S+LVGL+KrFont.bin`: 현재 펌웨어

---

**작성일**: 2025-10-13  
**작성자**: PillBox Debug Team  
**상태**: 🔍 조사 중 - REPL 직접 테스트 필요

---

## 📊 이전 분석 (참고용)

