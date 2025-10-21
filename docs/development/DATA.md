# 데이터 파일 구조 및 기능 설명

## 📁 데이터 파일 개요

ESP32 필박스 시스템에서 사용되는 모든 JSON 데이터 파일들의 구조와 기능을 설명합니다.

---

## 📋 데이터 파일 목록

### 1. `global_data.json`
**전역 데이터 및 화면 상태 관리**

```json
{
  "unused_disks": [],
  "selected_meals": [
    {
      "key": "breakfast",
      "default_hour": 8,
      "name": "아침",
      "default_minute": 0
    }
  ],
  "dose_count": 3,
  "dose_times": [],
  "auto_assigned_disks": [
    {
      "disk_number": 1,
      "time": "08:00",
      "meal_name": "아침",
      "meal_key": "breakfast"
    }
  ],
  "screen_data_backup": {
    "meal_time": {
      "current_selection": 2,
      "selected_meals": {
        "lunch": true,
        "breakfast": true,
        "dinner": true
      }
    }
  }
}
```

**키-밸류 상세 설명:**
- `unused_disks`: 사용하지 않는 디스크 목록 (배열, 예: [])
- `selected_meals`: 선택된 복용 시간대 목록 (배열)
  - `key`: 시간대 키 (문자열, "breakfast", "lunch", "dinner")
  - `default_hour`: 기본 시간 (정수, 0-23)
  - `name`: 시간대 이름 (문자열, "아침", "점심", "저녁")
  - `default_minute`: 기본 분 (정수, 0-59)
- `dose_count`: 하루 복용 횟수 (정수, 1-3)
- `dose_times`: 설정된 복용 시간 목록 (배열)
- `auto_assigned_disks`: 자동 할당된 디스크 정보 (배열)
  - `disk_number`: 디스크 번호 (정수, 1-3)
  - `time`: 복용 시간 (문자열, "HH:MM" 형식)
  - `meal_name`: 시간대 이름 (문자열)
  - `meal_key`: 시간대 키 (문자열)
- `screen_data_backup`: 각 화면의 상태 백업 데이터 (객체)

**기능:**
- 시스템 전역 설정 및 상태 정보
- 복용 시간대 및 디스크 할당 관리
- 화면별 상태 백업 및 복원
- 자동 할당 로직 데이터

---

### 2. `dispense_log.json`
**복용 로그 관리**

```json
[
  {
    "success": true,
    "timestamp": "2025-10-21T13:29:52",
    "date": "2025-10-21",
    "dose_index": 0,
    "time": "13:29:52"
  }
]
```

**키-밸류 상세 설명:**
- `success`: 복용 성공 여부 (불린, true/false)
- `timestamp`: 복용 이벤트 발생 시간 (ISO 8601 형식)
- `date`: 복용 날짜 (문자열, "YYYY-MM-DD" 형식)
- `dose_index`: 복용 순서 인덱스 (정수, 0부터 시작)
- `time`: 복용 시간 (문자열, "HH:MM:SS" 형식)

**기능:**
- 모든 복용 이벤트 기록
- 복용 성공/실패 상태 추적
- 복용 순서 및 시간 기록
- 복용 이력 분석 및 통계

---

### 3. `boot_target.json`
**부팅 타겟 관리**

```json
{
  "boot_target": "meal_time"
}
```

**키-밸류 상세 설명:**
- `boot_target`: 재부팅 후 이동할 목표 화면 (문자열)

**가능한 값:**
- `"main"` - 메인 화면으로 부팅 (기본값)
- `"dose_time"` - 시간-분 설정 화면으로 부팅 (D버튼 조건부 재부팅)
- `"meal_time"` - 복용시간선택 화면으로 부팅 (D버튼 조건부 재부팅)
- `"wifi_scan"` - WiFi 스캔 화면으로 부팅 (초기 설정 또는 D버튼 조건부 재부팅)

**기능:**
- D버튼 조건부 재부팅 시 목표 화면 지정
- 시스템 재부팅 후 특정 화면으로 직접 이동
- 설정 완료 후 메인 화면 복귀

---

### 4. `disk_states.json`
**디스크 상태 관리**

```json
{
  "disk_1_loaded": 3,
  "disk_2_loaded": 3,
  "disk_3_loaded": 3,
  "saved_at": 814369218
}
```

**키-밸류 상세 설명:**
- `disk_1_loaded`: 디스크 1에 충전된 알약 개수 (정수, 0 이상)
- `disk_2_loaded`: 디스크 2에 충전된 알약 개수 (정수, 0 이상)
- `disk_3_loaded`: 디스크 3에 충전된 알약 개수 (정수, 0 이상)
- `saved_at`: 설정 저장 시간 (Unix 타임스탬프, 정수)

**기능:**
- 각 디스크의 알약 개수 관리
- 디스크별 충전 상태 추적
- 마지막 저장 시간 기록
- 디스크별 상태 모니터링

---

### 5. `medication.json`
**약물 정보 및 리필 이력 관리**

```json
{
  "refill_history": [
    {
      "disk": 1,
      "count": 3,
      "timestamp": "2025-10-21T13:29:27"
    }
  ],
  "low_stock_threshold": 3,
  "disks": {
    "1": {
      "total_capacity": 15,
      "name": "아침약",
      "medication_type": "morning",
      "current_count": 0,
      "last_refill": "2025-10-21T13:41:18"
    }
  }
}
```

**키-밸류 상세 설명:**
- `refill_history`: 리필 이력 목록 (배열)
  - `disk`: 디스크 번호 (정수, 1-3)
  - `count`: 리필된 알약 개수 (정수)
  - `timestamp`: 리필 시간 (ISO 8601 형식)
- `low_stock_threshold`: 재고 부족 알림 임계값 (정수, 기본값: 3)
- `disks`: 각 디스크별 상세 정보 (객체)
  - `total_capacity`: 디스크 최대 용량 (정수)
  - `name`: 디스크 이름 (문자열, 예: "아침약", "점심약", "저녁약")
  - `medication_type`: 약물 타입 (문자열, "morning", "lunch", "dinner")
  - `current_count`: 현재 알약 개수 (정수)
  - `last_refill`: 마지막 리필 시간 (ISO 8601 형식)

**기능:**
- 디스크별 약물 정보 관리
- 리필 이력 추적 및 분석
- 재고 부족 알림 관리
- 디스크별 용량 및 타입 관리

---

### 6. `settings.json`
**시스템 설정 관리**

```json
{
  "dose_days": 30,
  "dose_times": [
    {
      "meal_key": "breakfast",
      "minute": 0,
      "meal_name": "아침",
      "selected_disks": [3],
      "time": "08:00",
      "hour": 8
    }
  ],
  "dose_schedule": [
    {
      "time": "08:00",
      "meal_name": "아침",
      "meal_key": "breakfast",
      "enabled": true
    }
  ],
  "system_settings": {
    "sound_enabled": true,
    "display_brightness": 100,
    "auto_dispense": true
  },
  "wifi": {
    "ssid": "",
    "connected": false,
    "password": ""
  },
  "dose_count": 3,
  "alarm_settings": {
    "enabled": true,
    "max_reminders": 3,
    "reminder_interval": 5
  }
}
```

**키-밸류 상세 설명:**
- `dose_days`: 복용 일수 (정수, 예: 30일)
- `dose_times`: 설정된 복용 시간 목록 (배열)
  - `meal_key`: 시간대 키 (문자열)
  - `minute`: 분 (정수, 0-59)
  - `meal_name`: 시간대 이름 (문자열)
  - `selected_disks`: 선택된 디스크 목록 (배열)
  - `time`: 복용 시간 (문자열, "HH:MM" 형식)
  - `hour`: 시간 (정수, 0-23)
- `dose_schedule`: 복용 스케줄 (배열)
  - `time`: 복용 시간 (문자열)
  - `meal_name`: 시간대 이름 (문자열)
  - `meal_key`: 시간대 키 (문자열)
  - `enabled`: 활성화 여부 (불린)
- `system_settings`: 시스템 설정 (객체)
  - `sound_enabled`: 소리 활성화 (불린)
  - `display_brightness`: 화면 밝기 (정수, 0-100)
  - `auto_dispense`: 자동 복용 활성화 (불린)
- `wifi`: WiFi 설정 (객체)
  - `ssid`: WiFi 네트워크 이름 (문자열)
  - `connected`: 연결 상태 (불린)
  - `password`: WiFi 비밀번호 (문자열)
- `dose_count`: 하루 복용 횟수 (정수, 1-3)
- `alarm_settings`: 알림 설정 (객체)
  - `enabled`: 알림 활성화 (불린)
  - `max_reminders`: 최대 리마인더 횟수 (정수)
  - `reminder_interval`: 리마인더 간격 (정수, 분 단위)

**기능:**
- 복용 스케줄 및 시간 관리
- 시스템 설정 (소리, 밝기, 자동 복용)
- WiFi 연결 정보
- 알림 및 리마인더 설정

---

### 7. `wifi_config.json`
**WiFi 연결용 임시 설정**

```json
{
  "saved_at": 814369532,
  "password": "",
  "ssid": ""
}
```

**키-밸류 상세 설명:**
- `saved_at`: 설정 저장 시간 (Unix 타임스탬프, 정수)
- `password`: WiFi 비밀번호 (평문 문자열)
- `ssid`: WiFi 네트워크 이름 (문자열)

**기능:**
- WiFi 연결 시 임시 저장용 설정
- `WiFiManager`에서 연결 정보 저장/불러오기
- 연결 성공 후 자동 삭제 가능

**`settings.json`과의 차이점:**
- **용도**: `wifi_config.json`은 연결용, `settings.json`은 시스템 설정용
- **암호화**: `wifi_config.json`은 평문, `settings.json`은 암호화
- **지속성**: `wifi_config.json`은 임시, `settings.json`은 영구

---

## 🔄 데이터 파일 간 관계

### 복용 플로우
```
settings.json → dose_times 설정 → global_data.json → auto_assigned_disks
```

### 디스크 관리 플로우
```
disk_states.json → medication.json → refill_history 업데이트
```

### 로그 플로우
```
복용 이벤트 → dispense_log.json → 복용 이력 기록
```

### 부팅 플로우
```
boot_target.json → main.py → 특정 화면으로 부팅
```

---

## 🛠️ 데이터 관리 기능

### 자동 생성
- 시스템 최초 부팅 시 기본값으로 생성
- 각 화면에서 필요한 데이터 자동 생성

### 백업 및 복원
- `build_and_upload.py`의 데이터 파일 삭제 기능
- 개별 파일별 백업 및 복원 가능

### 데이터 무결성
- JSON 형식 검증
- 필수 필드 존재 확인
- 데이터 타입 검증

---

## 📊 데이터 사용 예시

### 메인 화면에서 알약 개수 표시
```python
# disk_states.json에서 디스크별 알약 개수 읽기
disk_1_pills = data_manager.get_disk_count(1)
disk_2_pills = data_manager.get_disk_count(2)
disk_3_pills = data_manager.get_disk_count(3)
```

### D버튼 조건부 재부팅
```python
# boot_target.json에 목표 화면 설정
boot_target = {
    "boot_target": "dose_time"  # 시간-분 설정으로 부팅
}
```

### 복용 로그 기록
```python
# dispense_log.json에 복용 이벤트 추가
log_entry = {
    "success": True,
    "timestamp": "2025-10-21T13:29:52",
    "date": "2025-10-21",
    "dose_index": 0,
    "time": "13:29:52"
}
```

---

## ⚠️ 주의사항

1. **데이터 백업**: 중요한 설정 변경 전 백업 권장
2. **파일 크기**: 로그 파일이 계속 증가하므로 주기적 정리 필요
3. **동시 접근**: 여러 프로세스에서 동시 수정 시 데이터 손실 가능
4. **JSON 형식**: 잘못된 JSON 형식으로 인한 파싱 오류 주의

---

## 🔧 유지보수

### 정기 작업
- 로그 파일 크기 모니터링
- 불필요한 데이터 정리
- 백업 파일 생성

### 문제 해결
- JSON 파싱 오류 시 파일 재생성
- 데이터 불일치 시 초기화
- 백업에서 복원

---

*최종 업데이트: 2024-01-01*
*문서 버전: 2.0.0 (실제 데이터 구조 반영)*