# 필박스 시스템 모터 위험성 종합 분석 보고서

## 📋 개요

이 문서는 src 폴더 내 모든 Python 파일들을 분석하여 모터가 의도치 않게 켜질 수 있는 위험 상황들을 종합적으로 정리한 보고서입니다.

## 🏗️ 시스템 아키텍처

### 1. 모터 제어 시스템 구조
```
PillBoxApp (메인 애플리케이션)
├── motor_system: PillBoxMotorSystem
│   └── motor_controller: StepperMotorController
│       ├── 74HC595D (출력 제어)
│       ├── ULN2003A (모터 드라이버)
│       └── 4개 스테퍼모터 (모터 0,1,2,3)
├── screen_manager: ScreenManager
│   ├── PillLoadingScreen (알약 충전)
│   ├── MainScreen (메인 UI)
│   └── 기타 화면들
└── button_interface: ButtonInterface
```

### 2. 모터 시스템 분포
- **motor_control.py**: 핵심 모터 제어 로직
- **pillbox_app.py**: 메인 애플리케이션에서 모터 시스템 초기화
- **screen_manager.py**: 화면 전환 관리
- **screens/**: 각 화면별 모터 제어 로직

## 🚨 의도치 않은 모터 활성화 위험 상황

### **1. 애플리케이션 레벨 위험성**

#### **위험 상황 1: PillBoxApp 초기화 실패 (매우 위험)**
**파일**: `pillbox_app.py`
```python
def __init__(self):
    self.motor_system = PillBoxMotorSystem()  # ⚠️ 예외 처리 없음
```

**위험성:**
- 모터 시스템 초기화 실패 시 전체 앱 크래시
- **부분적으로 초기화된 모터 시스템으로 인한 불안정 상태**
- 메모리 부족 시 예측 불가능한 모터 동작

#### **위험 상황 2: 메인 루프 예외 처리 부족 (높은 위험)**
**파일**: `pillbox_app.py`
```python
def _main_loop(self):
    while self.running:
        try:
            self.screen_manager.update()  # ⚠️ 화면에서 모터 제어 가능
        except Exception as e:
            print(f"메인 루프 오류: {e}")
            time.sleep_ms(100)  # ⚠️ 모터 상태 확인 없이 계속 진행
```

**위험성:**
- 메인 루프에서 예외 발생 시 모터 상태를 확인하지 않음
- **화면 전환 중 모터가 켜진 상태로 남을 수 있음**

#### **위험 상황 3: 앱 종료 시 모터 정리 부족 (중간 위험)**
**파일**: `pillbox_app.py`
```python
def stop(self):
    self.running = False  # ⚠️ 모터 정리 로직 없음
```

**위험성:**
- 앱 종료 시 모터 상태를 정리하지 않음
- **모터가 켜진 상태로 앱이 종료될 수 있음**

### **2. 화면 관리 시스템 위험성**

#### **위험 상황 4: 화면 전환 중 모터 상태 불일치 (높은 위험)**
**파일**: `screen_manager.py`
```python
def show_screen(self, screen_name, add_to_stack=True):
    if self.current_screen:
        self.current_screen.hide()  # ⚠️ 모터 상태 확인 없음
    self.current_screen = self.screens[screen_name]
    self.current_screen.show()  # ⚠️ 새 화면에서 모터 제어 가능
```

**위험성:**
- 화면 전환 시 이전 화면의 모터 상태를 확인하지 않음
- **여러 화면에서 동시에 모터 시스템에 접근 가능**
- 화면별 모터 상태 관리 불일치

#### **위험 상황 5: 버튼 입력 처리 중 모터 제어 (중간 위험)**
**파일**: `screen_manager.py`
```python
def handle_button_a(self):
    if self.current_screen and hasattr(self.current_screen, 'on_button_a'):
        self.current_screen.on_button_a()  # ⚠️ 모터 제어 가능한 버튼 처리
```

**위험성:**
- 버튼 입력으로 모터 제어 함수 호출 가능
- **예외 처리 없이 모터 제어 시도**
- 버튼 중복 입력으로 인한 모터 상태 혼란

### **3. 모터 제어 시스템 위험성**

#### **위험 상황 6: StepperMotorController 초기화 실패 (매우 위험)**
**파일**: `motor_control.py`
```python
def __init__(self, di_pin=2, sh_cp_pin=3, st_cp_pin=15, data_out_pin=10):
    self.di = Pin(di_pin, Pin.OUT)
    self.sh_cp = Pin(sh_cp_pin, Pin.OUT)
    self.st_cp = Pin(st_cp_pin, Pin.OUT)
    # ⚠️ 예외 처리 없이 GPIO 핀 설정
```

**위험성:**
- GPIO 핀 설정 실패 시 하드웨어 불안정
- **74HC595D 초기화 실패로 인한 출력 불안정**
- 전원 공급 불안정 시 모터가 의도치 않게 켜질 수 있음

#### **위험 상황 7: 74HC595D 타이밍 문제 (높은 위험)**
**파일**: `motor_control.py`
```python
def shift_out(self, data):
    for i in range(8):
        bit = (data >> (7 - i)) & 1
        self.di.value(bit)
        self.sh_cp.value(1)  # ⚠️ 딜레이 없음
        self.sh_cp.value(0)
```

**위험성:**
- 타이밍 딜레이 없이 연속 GPIO 전환
- **74HC595D 출력이 불안정한 상태로 고정될 수 있음**
- 모터가 의도하지 않은 전류를 받아 계속 켜진 상태 유지

#### **위험 상황 8: 비블로킹 모터 제어 변수 오염 (중간 위험)**
**파일**: `motor_control.py`
```python
def __init__(self):
    self.motor_running = [False, False, False, False]  # 비블로킹 제어 상태
    self.motor_direction = [1, 1, 1, 1]  # 각 모터별 방향
```

**위험성:**
- `motor_running` 상태가 예외적으로 `True`로 남을 수 있음
- **다른 화면에서 비블로킹 모터 제어 사용 시 상태 오염**

### **4. 화면별 모터 제어 위험성**

#### **위험 상황 9: PillLoadingScreen 모터 시스템 초기화 실패 (높은 위험)**
**파일**: `screens/pill_loading_screen.py`
```python
try:
    self.motor_system = PillBoxMotorSystem()
    print("✅ 모터 시스템 초기화 완료")
except Exception as e:
    print(f"⚠️ 모터 시스템 초기화 실패: {e}")
    self.motor_system = None  # ⚠️ 위험: None 상태
```

**위험성:**
- `self.motor_system = None` 상태에서 모터 제어 시도
- **`_real_loading()` 함수에서 `None` 참조로 인한 예외 발생**

#### **위험 상황 10: 모터 제어 중 예외 발생 (높은 위험)**
**파일**: `screens/pill_loading_screen.py`
```python
try:
    while self.current_disk_state.is_loading:
        self.motor_system.motor_controller.step_motor_continuous(disk_index, 1, 1)
except Exception as e:
    self.motor_system.motor_controller.stop_motor(disk_index)  # ⚠️ 부분적 정지만
    return False
```

**위험성:**
- 예외 발생 시 해당 모터만 정지
- **다른 모터들의 상태는 확인하지 않음**

#### **위험 상황 11: MainScreen 지연 초기화 충돌 (중간 위험)**
**파일**: `screens/main_screen_ui.py`
```python
def _init_motor_system(self):
    if self.motor_system is None:
        self.motor_system = PillBoxMotorSystem()  # ⚠️ 중복 초기화
```

**위험성:**
- PillBoxApp과 MainScreen에서 모터 시스템을 별도로 초기화
- **두 개의 모터 시스템 인스턴스로 인한 상태 불일치**

#### **위험 상황 12: DiskState와 실제 모터 상태 불일치 (중간 위험)**
**파일**: `screens/pill_loading_screen.py`
```python
def complete_loading(self):
    if self.current_loading_count >= 3:
        self.is_loading = False  # ⚠️ 소프트웨어 상태만 변경
        return True
```

**위험성:**
- `DiskState.is_loading = False`로 변경되지만
- **실제 하드웨어 모터 상태는 별도로 관리됨**

### **5. 하드웨어 레벨 위험성**

#### **위험 상황 13: 전원 공급 불안정 (매우 위험)**
**파일**: `motor_control.py`
```python
def turn_off_all_coils(self):
    for i in range(4):
        self.motor_states[i] = 0x00
    self.update_motor_output()
```

**위험성:**
- 전원 공급 불안정 시 74HC595D 출력이 예측 불가능한 상태
- **전원 복구 시 모터가 의도하지 않게 켜질 수 있음**

#### **위험 상황 14: 리미트 스위치 기반 제어 실패 (중간 위험)**
**파일**: `motor_control.py`
```python
def next_compartment(self, motor_index):
    while not self.is_limit_switch_pressed(motor_index):
        # 모터 회전 로직
        time.sleep_us(500)  # ⚠️ 무한 루프 가능성
```

**위험성:**
- 리미트 스위치 고장 시 무한 루프
- **모터가 계속 회전하여 과열 및 손상 가능**

## 📊 위험성 종합 평가

| 위험 상황 | 파일 | 발생 확률 | 영향도 | 우선순위 |
|-----------|------|-----------|--------|----------|
| PillBoxApp 초기화 실패 | pillbox_app.py | 높음 | 매우 높음 | 🔴 높음 |
| 메인 루프 예외 처리 부족 | pillbox_app.py | 높음 | 중간 | 🟡 중간 |
| 앱 종료 시 모터 정리 부족 | pillbox_app.py | 중간 | 높음 | 🟡 중간 |
| 화면 전환 중 모터 상태 불일치 | screen_manager.py | 높음 | 높음 | 🔴 높음 |
| 버튼 입력 처리 중 모터 제어 | screen_manager.py | 중간 | 중간 | 🟡 중간 |
| StepperMotorController 초기화 실패 | motor_control.py | 낮음 | 매우 높음 | 🔴 높음 |
| 74HC595D 타이밍 문제 | motor_control.py | 낮음 | 높음 | 🔴 높음 |
| 비블로킹 모터 제어 변수 오염 | motor_control.py | 낮음 | 높음 | 🟡 중간 |
| PillLoadingScreen 초기화 실패 | screens/pill_loading_screen.py | 중간 | 높음 | 🔴 높음 |
| 모터 제어 중 예외 발생 | screens/pill_loading_screen.py | 높음 | 중간 | 🟡 중간 |
| MainScreen 지연 초기화 충돌 | screens/main_screen_ui.py | 낮음 | 높음 | 🟡 중간 |
| DiskState와 모터 상태 불일치 | screens/pill_loading_screen.py | 중간 | 중간 | 🟡 중간 |
| 전원 공급 불안정 | motor_control.py | 낮음 | 매우 높음 | 🔴 높음 |
| 리미트 스위치 기반 제어 실패 | motor_control.py | 낮음 | 높음 | 🟡 중간 |

## 🛡️ 종합 위험성 완화 방안

### **1. 애플리케이션 레벨 안전장치**

#### **강화된 초기화 및 예외 처리**
```python
# pillbox_app.py
class PillBoxApp:
    def __init__(self):
        try:
            self.motor_system = self._safe_init_motor_system()
        except Exception as e:
            print(f"❌ PillBoxApp 초기화 실패: {e}")
            self._emergency_shutdown()
    
    def _safe_init_motor_system(self):
        """모터 시스템 안전 초기화"""
        try:
            motor_system = PillBoxMotorSystem()
            # 초기화 후 모터 상태 검증
            motor_system.motor_controller.stop_all_motors()
            return motor_system
        except Exception as e:
            print(f"⚠️ 모터 시스템 초기화 실패: {e}")
            return None
    
    def _emergency_shutdown(self):
        """비상 종료"""
        try:
            if hasattr(self, 'motor_system') and self.motor_system:
                self.motor_system.motor_controller.stop_all_motors()
        except:
            pass
```

#### **메인 루프 안전성 강화**
```python
def _main_loop(self):
    while self.running:
        try:
            lv.timer_handler()
            self.button_interface.update()
            self.screen_manager.update()
            
            # 주기적 모터 상태 검증
            self._periodic_motor_safety_check()
            
            time.sleep_ms(50)
        except Exception as e:
            print(f"메인 루프 오류: {e}")
            self._emergency_motor_stop()
            time.sleep_ms(100)
    
    def _periodic_motor_safety_check(self):
        """주기적 모터 안전 상태 검증"""
        try:
            if self.motor_system and self.motor_system.motor_controller:
                for i in range(4):
                    if self.motor_system.motor_controller.motor_states[i] != 0x00:
                        print(f"⚠️ 모터 {i}가 의도치 않게 켜짐 - 강제 정지")
                        self.motor_system.motor_controller.motor_states[i] = 0x00
                self.motor_system.motor_controller.update_motor_output()
        except Exception as e:
            print(f"모터 안전 검증 실패: {e}")
```

#### **안전한 앱 종료**
```python
def stop(self):
    print("⏹️ PillBoxApp 안전 종료 시작")
    try:
        # 모든 모터 강제 정지
        if self.motor_system and self.motor_system.motor_controller:
            self.motor_system.motor_controller.stop_all_motors()
        self.running = False
    except Exception as e:
        print(f"❌ 앱 종료 중 오류: {e}")
        self.running = False
```

### **2. 화면 관리 시스템 안전장치**

#### **화면 전환 시 모터 상태 검증**
```python
# screen_manager.py
def show_screen(self, screen_name, add_to_stack=True):
    try:
        # 현재 화면 모터 상태 정리
        if self.current_screen:
            self._cleanup_current_screen_motors()
            self.current_screen.hide()
        
        # 새 화면으로 전환
        self.current_screen_name = screen_name
        self.current_screen = self.screens[screen_name]
        self.current_screen.show()
        
        # 새 화면 모터 상태 검증
        self._verify_new_screen_motors()
        
    except Exception as e:
        print(f"❌ 화면 전환 실패: {e}")
        self._emergency_motor_stop()
    
    def _cleanup_current_screen_motors(self):
        """현재 화면의 모터 상태 정리"""
        try:
            if self.app and self.app.motor_system:
                self.app.motor_system.motor_controller.stop_all_motors()
        except:
            pass
    
    def _verify_new_screen_motors(self):
        """새 화면의 모터 상태 검증"""
        try:
            if self.app and self.app.motor_system:
                for i in range(4):
                    if self.app.motor_system.motor_controller.motor_states[i] != 0x00:
                        print(f"⚠️ 화면 전환 후 모터 {i} 상태 이상 - 정지")
                        self.app.motor_system.motor_controller.motor_states[i] = 0x00
                self.app.motor_system.motor_controller.update_motor_output()
        except:
            pass
```

### **3. 모터 제어 시스템 안전장치**

#### **하드웨어 안정성 강화**
```python
# motor_control.py
def shift_out(self, data):
    """74HC595D에 8비트 데이터 전송 (타이밍 개선)"""
    for i in range(8):
        bit = (data >> (7 - i)) & 1
        self.di.value(bit)
        time.sleep_us(1)  # ⚠️ 타이밍 딜레이 추가
        
        self.sh_cp.value(1)
        time.sleep_us(1)  # ⚠️ 타이밍 딜레이 추가
        self.sh_cp.value(0)
        time.sleep_us(1)  # ⚠️ 타이밍 딜레이 추가
    
    self.st_cp.value(1)
    time.sleep_us(1)  # ⚠️ 타이밍 딜레이 추가
    self.st_cp.value(0)
```

#### **리미트 스위치 안전장치**
```python
def next_compartment(self, motor_index):
    """다음 칸으로 이동 - 리미트 스위치 기반 (안전장치 추가)"""
    max_steps = 1000  # 최대 스텝 수 제한
    step_count = 0
    
    while not self.is_limit_switch_pressed(motor_index) and step_count < max_steps:
        # 모터 회전 로직
        step_count += 1
        
    if step_count >= max_steps:
        print(f"❌ 모터 {motor_index} 리미트 스위치 타임아웃")
        self.stop_motor(motor_index)
        return False
```

### **4. 화면별 안전장치**

#### **PillLoadingScreen 안전 초기화**
```python
# screens/pill_loading_screen.py
def __init__(self, screen_manager):
    # 모터 시스템 안전 초기화
    self.motor_system = self._safe_init_motor_system()
    
    def _safe_init_motor_system(self):
        try:
            motor_system = PillBoxMotorSystem()
            # 초기화 후 모든 모터 정지
            motor_system.motor_controller.stop_all_motors()
            return motor_system
        except Exception as e:
            print(f"⚠️ 모터 시스템 초기화 실패: {e}")
            return None
```

#### **강화된 예외 처리**
```python
def _real_loading(self, disk_index):
    try:
        # 모터 시스템 검증
        if not self.motor_system or not self.motor_system.motor_controller:
            print("❌ 모터 시스템이 초기화되지 않음")
            return False
        
        # 시작 전 모든 모터 강제 정지
        self.motor_system.motor_controller.stop_all_motors()
        
        # 모터 제어 로직...
        
    except Exception as e:
        print(f"❌ 모터 제어 중 오류: {e}")
        # 모든 모터 강제 정지
        try:
            self.motor_system.motor_controller.stop_all_motors()
        except:
            pass
        return False
    finally:
        # 항상 실행되는 정리 로직
        try:
            self.motor_system.motor_controller.stop_all_motors()
        except:
            pass
```

## 🎯 권장 조치사항

### **즉시 적용 (높은 우선순위)**
1. **PillBoxApp 초기화에 예외 처리 추가**
2. **메인 루프에 모터 상태 검증 로직 추가**
3. **화면 전환 시 모터 상태 정리 로직 추가**
4. **74HC595D 타이밍 딜레이 추가**
5. **모든 예외 처리에 `finally` 블록 추가**

### **단기 개선 (중간 우선순위)**
1. **주기적 모터 안전 상태 검증 시스템**
2. **모터 상태 모니터링 시스템 구축**
3. **비상 모터 정지 시스템**
4. **리미트 스위치 타임아웃 안전장치**

### **장기 개선 (낮은 우선순위)**
1. **전력 관리 시스템 개선**
2. **모터 상태 백업 및 복구 시스템**
3. **예측적 안전 모니터링**
4. **하드웨어 레벨 안전장치 추가**

## 📈 위험성 요약

### **가장 위험한 상황들:**
1. **PillBoxApp 초기화 실패** (높은 확률, 매우 높은 영향)
2. **StepperMotorController 초기화 실패** (낮은 확률, 매우 높은 영향)
3. **화면 전환 중 모터 상태 불일치** (높은 확률, 높은 영향)
4. **전원 공급 불안정** (낮은 확률, 매우 높은 영향)

### **즉시 개선 필요:**
- 예외 처리 부족으로 인한 모터 상태 불안정
- 화면 전환 시 모터 상태 관리 부족
- 하드웨어 타이밍 문제로 인한 출력 불안정
- 앱 종료 시 모터 정리 로직 부족

### **시스템 전체 위험도: 🔴 높음**
- **14가지 주요 위험 상황 식별**
- **6가지 높은 우선순위 위험 상황**
- **즉시 개선이 필요한 안전장치 부족**

---

*이 문서는 src 폴더 내 모든 Python 파일을 분석하여 모터가 의도치 않게 켜질 수 있는 위험 상황들을 종합적으로 정리한 결과입니다. 실제 구현은 각 해당 파일들을 참조하세요.*
