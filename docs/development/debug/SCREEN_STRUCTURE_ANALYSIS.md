# 화면 구조 분석 보고서

## 📱 DoseTimeScreen (복용 시간 설정 화면)

### **클래스 개요**
- **목적**: 각 복용 시간을 설정하는 화면 (롤러 UI 스타일)
- **파일**: `src/screens/dose_time_screen.py`
- **주요 기능**: 시간/분 설정, 복용 시간 저장, 다음 화면으로 전환

### **클래스 구조**

#### **초기화 (__init__)**
```python
def __init__(self, screen_manager, dose_count=1, selected_meals=None):
    # 기본 속성
    self.screen_manager = screen_manager
    self.screen_name = 'dose_time'
    self.screen_obj = None
    
    # 복용 시간 관련
    self.dose_count = dose_count
    self.selected_meals = selected_meals or []
    self.dose_times = []
    self.current_dose_index = 0
    self.current_hour = 8
    self.current_minute = 0
    self.editing_hour = True
    
    # UI 객체들
    self.hour_roller = None
    self.minute_roller = None
    self.ui_style = None  # 지연 초기화
```

#### **주요 메서드**

##### **1. UI 관리**
- `_ensure_ui_style()`: UI 스타일 지연 초기화
- `_create_simple_screen()`: 간단한 화면 생성
- `_update_title_text()`: 제목 텍스트 업데이트

##### **2. 시간 설정**
- `_set_default_time_from_meals()`: 선택된 식사 시간에 따라 기본 시간 설정
- `_next_time_setup()`: 다음 복용 시간 설정 또는 완료
- `_save_current_time()`: 현재 시간 저장

##### **3. 버튼 처리**
- `on_button_a()`: 버튼 A - 위/이전
- `on_button_b()`: 버튼 B - 아래/다음
- `on_button_c()`: 버튼 C - 뒤로가기
- `on_button_d()`: 버튼 D - 선택/확인

##### **4. 화면 전환**
- `show()`: 화면 표시
- `hide()`: 화면 숨김
- `_next_time_setup()`: 다음 화면으로 전환 (pill_loading)

### **메모리 최적화 특징**
- **지연 초기화**: `ui_style = None`으로 시작, 필요시에만 초기화
- **화면 정리**: 이전 화면들 정리로 메모리 절약
- **가비지 컬렉션**: 화면 전환 전 메모리 정리

---

## 💊 PillLoadingScreen (알약 충전 화면)

### **클래스 개요**
- **목적**: 알약을 디스크에 충전하는 화면
- **파일**: `src/screens/pill_loading_screen.py`
- **주요 기능**: 디스크 선택, 알약 충전, 순차적 충전, 모터 제어

### **클래스 구조**

#### **초기화 (__init__)**
```python
def __init__(self, screen_manager):
    # 기본 속성
    self.screen_manager = screen_manager
    self.screen_name = 'pill_loading'
    self.screen_obj = None
    
    # 디스크 관련
    self.selected_disk_index = 0
    self.is_loading = False
    self.loading_progress = 0
    self.current_mode = 'selection'
    self.current_disk_state = None
    
    # 식사 시간 매핑
    self.meal_to_disk_mapping = {
        'breakfast': 0,  # 아침 → 디스크 1
        'lunch': 1,      # 점심 → 디스크 2
        'dinner': 2      # 저녁 → 디스크 3
    }
    
    # 복용 시간 정보
    self.dose_times = []
    self.selected_meals = []
    self.available_disks = []
    
    # 순차적 충전
    self.sequential_mode = False
    self.current_sequential_index = 0
    self.sequential_disks = []
    
    # 지연 초기화 객체들
    self.disk_states = {}
    self._disk_states_loaded = False
    self.ui_style = None
    self.motor_system = None
```

#### **주요 메서드**

##### **1. 지연 초기화**
- `_ensure_ui_style()`: UI 스타일 지연 초기화
- `_ensure_motor_system()`: 모터 시스템 지연 초기화
- `_ensure_disk_states()`: 디스크 상태 지연 초기화

##### **2. 화면 생성**
- `_create_modern_screen()`: Modern 화면 생성
- `_create_loading_sub_screen()`: 충전 서브 화면 생성
- `_create_loading_screen_directly()`: 직접 충전 화면 생성

##### **3. 충전 관리**
- `start_sequential_loading()`: 순차적 충전 시작
- `_real_loading()`: 실제 모터 제어를 통한 알약 충전
- `_save_disk_states()`: 디스크 충전 상태 저장

##### **4. 버튼 처리**
- `on_button_a()`: 버튼 A - 디스크 회전 (비활성화)
- `on_button_b()`: 버튼 B - 다음 화면으로 (메인 화면)
- `on_button_c()`: 버튼 C - 충전 완료
- `on_button_d()`: 버튼 D - 디스크 선택/충전 실행

##### **5. 데이터 관리**
- `update_dose_times()`: 복용 시간 정보 업데이트
- `_load_disk_states()`: 저장된 디스크 충전 상태 불러오기
- `_save_disk_states()`: 디스크 충전 상태 저장

### **DiskState 클래스**
```python
class DiskState:
    def __init__(self, disk_id):
        self.disk_id = disk_id
        self.total_compartments = 15  # 총 15칸
        self.compartments_per_loading = 3  # 한 번에 3칸씩 충전
        self.loaded_count = 0  # 충전된 칸 수
        self.is_loading = False  # 현재 충전 중인지 여부
        self.current_loading_count = 0  # 현재 충전 중인 칸 수
```

### **메모리 최적화 특징**
- **지연 초기화**: UI 스타일, 모터 시스템, 디스크 상태 모두 지연 초기화
- **파일 I/O 최소화**: 디스크 상태 로딩을 필요시에만 수행
- **메모리 정리**: 각 초기화 전 가비지 컬렉션 수행

---

## 🔄 화면 전환 플로우

### **DoseTimeScreen → PillLoadingScreen**
1. **시간 설정 완료**: `_next_time_setup()` 호출
2. **이전 화면 정리**: startup, wifi_scan, meal_time 화면 정리
3. **메모리 정리**: 5회 가비지 컬렉션
4. **PillLoadingScreen 생성**: 임포트 → 인스턴스 생성 → 등록
5. **화면 전환**: `show_screen('pill_loading')`

### **메모리 사용 패턴**
- **DoseTimeScreen**: ~50KB
- **화면 정리 후**: ~100KB
- **PillLoadingScreen 생성 시**: ~162KB (문제 지점)

---

## 🚨 메모리 문제 분석

### **문제 지점**
1. **PillLoadingScreen 임포트**: 클래스 로딩 시 메모리 사용
2. **인스턴스 생성**: `__init__` 메서드 실행 시 메모리 할당
3. **UI 객체 생성**: LVGL 객체들 생성 시 메모리 사용

### **해결 방안**
1. **지연 초기화**: 모든 무거운 객체들을 필요시에만 초기화
2. **화면 정리**: 이전 화면들의 LVGL 객체 완전 삭제
3. **메모리 정리**: 가비지 컬렉션 강화
4. **대체 경로**: 실패 시 메인 화면으로 이동

---

## 📊 성능 비교

| 항목 | DoseTimeScreen | PillLoadingScreen |
|------|----------------|-------------------|
| **초기화 속도** | 빠름 | 느림 (지연 초기화) |
| **메모리 사용량** | 낮음 (~50KB) | 높음 (~162KB) |
| **UI 복잡도** | 단순 (롤러 2개) | 복잡 (아크, 진행률, 버튼) |
| **기능 복잡도** | 단순 (시간 설정) | 복잡 (모터 제어, 충전) |
| **메모리 최적화** | 기본 | 고급 (지연 초기화) |

---

## 🎯 권장 사항

### **DoseTimeScreen**
- 현재 구조가 적절함
- 메모리 사용량이 낮아 추가 최적화 불필요

### **PillLoadingScreen**
- 지연 초기화 패턴 유지
- 메모리 모니터링 강화
- 실패 시 대체 경로 제공

### **전체 시스템**
- 화면 전환 시 메모리 정리 강화
- 메모리 사용량 모니터링 추가
- 예외 처리 강화

**두 화면 모두 메모리 최적화가 잘 적용되어 있으며, PillLoadingScreen의 지연 초기화 패턴이 핵심 해결책입니다.** 🚀💾
