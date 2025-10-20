# 필 디스펜서 메인 로직 설계안

## 1. 알약 배출 기능 설계안

### 1.1 개요
REQUIREMENTS.md의 3.2.4 약 배출 로직을 기반으로 한 종합적인 알약 배출 시스템 설계

### 1.2 배출 프로세스 (4단계)

#### 1.2.1 1단계: 알람 (Alarm Phase)
**목적**: 사용자에게 복약 시간임을 알림

**구현 요소**:
- **음성 알람**: "아침 약 드실 시간입니다." (한국어 음성 파일 재생)
- **LED 점멸**: 고휘도 LED를 1초 간격으로 점멸 (3회 반복)
- **부저음**: 1kHz 톤을 0.5초간 3회 울림
- **디스플레이**: "복용 시간입니다" 메시지 표시

**동작 순서**:
1. 설정된 복약 시간 도달 감지 (NTP 동기화된 시스템 시간)
2. 해당 디스크(아침/점심/저녁) 식별
3. 3가지 알람 동시 실행 (음성 + LED + 부저)
4. 사용자 확인 대기 (버튼 입력 또는 30초 타임아웃)

#### 1.2.2 2단계: 배출 준비 (Dispense Preparation)
**목적**: 선택된 디스크의 해당 칸을 배출 위치로 회전

**구현 요소**:
- **디스크 식별**: 복용 횟수에 따른 디스크 선택 (1회→모터1, 2회→모터2, 3회→모터3)
- **칸 위치 계산**: 원점 기준 + (칸 번호 × 273 스텝) 계산
- **모터 제어**: 해당 디스크를 배출 위치로 정밀 회전

**동작 순서**:
1. 복용 시간에 맞는 디스크 식별
2. 현재 칸 위치에서 배출 위치까지 스텝 계산
3. 모터 1,2,3 중 해당 모터를 배출 위치로 회전
4. 배출 준비 완료 신호

#### 1.2.3 3단계: 게이트 개폐 (Gate Control)
**목적**: 배출구 게이트를 열어 알약이 떨어지게 하고 자동으로 닫기

**구현 요소**:
- **게이트 모터 제어**: 모터 4를 이용한 배출구 슬라이드 제어
- **타이밍 제어**: 5초간 열린 상태 유지 후 자동 닫기
- **안전 장치**: 게이트 개방/폐쇄 상태 감지

**동작 순서**:
1. 모터 4를 이용해 배출구 게이트 열기
2. 5초 대기 (알약 떨어지는 시간)
3. 모터 4를 이용해 배출구 게이트 닫기
4. 게이트 상태 확인

#### 1.2.4 4단계: 기록 및 정리 (Recording & Cleanup)
**목적**: 배출 완료 기록 및 다음 배출 준비

**구현 요소**:
- **상태 기록**: 배출 완료 시간 및 칸 번호 기록
- **UI 업데이트**: 배출 완료 상태를 메인 화면에 표시
- **다음 배출 준비**: 다음 복용 시간까지 대기 상태로 전환
- **사용량 추적**: 해당 칸의 알약 개수 차감

**동작 순서**:
1. 배출 완료 시간 기록 (NTP 동기화 시간)
2. 해당 칸의 알약 개수 차감
3. 메인 화면에 배출 완료 상태 표시
4. 다음 복용 시간까지 대기 상태로 전환

### 1.3 배출 로직 상세 설계

#### 1.3.1 복용 시간 관리
```python
class MedicationScheduler:
    def __init__(self):
        self.dose_times = []  # 복용 시간 리스트
        self.current_dose_index = 0
        self.last_dispense_time = None
    
    def check_dispense_time(self):
        """복용 시간 확인 및 배출 트리거"""
        current_time = self.get_current_time()
        
        for i, dose_time in enumerate(self.dose_times):
            if self.is_time_to_dispense(current_time, dose_time):
                self.trigger_dispense(i)
                break
    
    def trigger_dispense(self, dose_index):
        """배출 프로세스 시작"""
        dose_info = self.dose_times[dose_index]
        dispense_manager.start_dispense_process(dose_info)
```

#### 1.3.2 디스크 및 칸 관리
```python
class DiskManager:
    def __init__(self):
        self.disks = {
            1: {'motor_id': 1, 'compartments': 15, 'current_compartment': 0},
            2: {'motor_id': 2, 'compartments': 15, 'current_compartment': 0},
            3: {'motor_id': 3, 'compartments': 15, 'current_compartment': 0}
        }
    
    def get_dispense_disk(self, dose_count):
        """복용 횟수에 따른 디스크 선택"""
        if dose_count == 1:
            return 1  # 모터 1 (아침)
        elif dose_count == 2:
            return 2  # 모터 2 (점심)
        elif dose_count == 3:
            return 3  # 모터 3 (저녁)
    
    def rotate_to_dispense_position(self, disk_id):
        """배출 위치로 디스크 회전"""
        motor_id = self.disks[disk_id]['motor_id']
        current_compartment = self.disks[disk_id]['current_compartment']
        
        # 배출 위치 계산 (원점 기준 + 칸 번호 × 273 스텝)
        target_steps = current_compartment * 273
        motor_controller.rotate_motor_to_position(motor_id, target_steps)
```

#### 1.3.3 게이트 제어
```python
class GateController:
    def __init__(self):
        self.gate_motor_id = 4  # 모터 4
        self.gate_open_steps = 200  # 게이트 열기 스텝 수
        self.gate_close_steps = 0   # 게이트 닫기 스텝 수
        self.is_open = False
    
    def open_gate(self):
        """게이트 열기"""
        motor_controller.rotate_motor_to_position(self.gate_motor_id, self.gate_open_steps)
        self.is_open = True
        print("게이트 열림")
    
    def close_gate(self):
        """게이트 닫기"""
        motor_controller.rotate_motor_to_position(self.gate_motor_id, self.gate_close_steps)
        self.is_open = False
        print("게이트 닫힘")
    
    def timed_gate_control(self, open_duration=5):
        """시간 제어 게이트 개폐"""
        self.open_gate()
        time.sleep(open_duration)
        self.close_gate()
```

### 1.4 알람 시스템 설계

#### 1.4.1 다중 감각 알람
```python
class MultiSensoryAlarm:
    def __init__(self):
        self.led_controller = LEDController()
        self.speaker_controller = SpeakerController()
        self.buzzer_controller = BuzzerController()
    
    def trigger_alarm(self, dose_type):
        """복용 타입에 따른 알람 실행"""
        # 음성 메시지
        voice_message = f"{dose_type} 약 드실 시간입니다."
        self.speaker_controller.play_voice(voice_message)
        
        # LED 점멸
        self.led_controller.blink_pattern(3, 1.0)  # 3회, 1초 간격
        
        # 부저음
        self.buzzer_controller.beep_pattern(3, 0.5)  # 3회, 0.5초 간격
        
        print(f"알람 실행: {dose_type} 복용 시간")
    
    def stop_alarm(self):
        """알람 중지"""
        self.led_controller.turn_off()
        self.buzzer_controller.stop()
        self.speaker_controller.stop()
```

#### 1.4.2 알람 타입별 메시지
- **아침 (1회)**: "아침 약 드실 시간입니다."
- **점심 (2회)**: "점심 약 드실 시간입니다."
- **저녁 (3회)**: "저녁 약 드실 시간입니다."

### 1.5 사용자 인터랙션

#### 1.5.1 배출 확인 및 재알람 시스템
```python
class AdvancedDispenseConfirmation:
    """고급 배출 확인 및 재알람 시스템"""
    
    def __init__(self):
        self.alarm_interval = 300  # 5분 간격으로 재알람
        self.max_retry_count = 5  # 최대 5회까지 재알람
        self.manual_dispense_delay = 0  # 첫 번째 알람 후 즉시 수동 배출 가능
        self.waiting_for_confirmation = False
        self.current_retry_count = 0
        self.last_alarm_time = 0
        self.dispense_failed = False
        self.manual_dispense_available = False
        
    def wait_for_user_confirmation_with_retry(self, dose_info):
        """사용자 확인 대기 및 재알람 처리"""
        self.waiting_for_confirmation = True
        self.current_retry_count = 0
        self.dispense_failed = False
        self.manual_dispense_available = False
        
        # 첫 번째 알람 시작
        self.last_alarm_time = time.time()
        print(f"배출 알람 시작: {dose_info['type']}")
        
        # 첫 번째 알람 후 즉시 수동 배출 가능 상태로 설정
        self.schedule_immediate_manual_dispense(dose_info)
        
        while self.waiting_for_confirmation:
            current_time = time.time()
            
            # A 버튼 (Button A) 확인
            if button_interface.is_button_pressed('A'):  # A 버튼으로 배출 확인
                self.confirm_dispense(dose_info)
                return True
            
            # 5분 간격으로 재알람
            if current_time - self.last_alarm_time >= self.alarm_interval:
                self.current_retry_count += 1
                
                if self.current_retry_count <= self.max_retry_count:
                    # 재알람 실행
                    self.trigger_retry_alarm(dose_info)
                    self.last_alarm_time = current_time
                    print(f"재알람 {self.current_retry_count}/{self.max_retry_count}")
                else:
                    # 5회 재알람 후 배출 실패 처리
                    self.handle_dispense_failure(dose_info)
                    return False
            
            time.sleep(0.1)
        
        return False
    
    def trigger_retry_alarm(self, dose_info):
        """재알람 실행"""
        # 알람 시스템 재실행
        alarm_system.trigger_alarm(dose_info['type'])
        print(f"재알람 실행: {dose_info['type']} ({self.current_retry_count}회차)")
    
    def confirm_dispense(self, dose_info):
        """사용자 확인 시 배출 진행"""
        self.waiting_for_confirmation = False
        alarm_system.stop_alarm()
        print(f"배출 확인됨: {dose_info['type']} - 배출 진행")
        dispense_manager.proceed_with_dispense(dose_info)
    
    def handle_dispense_failure(self, dose_info):
        """배출 실패 처리"""
        self.waiting_for_confirmation = False
        self.dispense_failed = True
        alarm_system.stop_alarm()
        
        # 배출 실패 기록
        failure_log = {
            'timestamp': time.time(),
            'dose_type': dose_info['type'],
            'reason': 'user_not_responded',
            'retry_count': self.current_retry_count,
            'status': 'failed'
        }
        
        dispense_logger.log_dispense_failure(failure_log)
        print(f"배출 실패: {dose_info['type']} - 5회 재알람 후 미응답")
        
        # UI에 실패 상태 표시
        ui_manager.show_dispense_failure_message(dose_info['type'])
        
        # 수동 배출은 이미 첫 번째 알람 후부터 가능하므로 별도 처리 불필요
    
    def schedule_immediate_manual_dispense(self, dose_info):
        """첫 번째 알람 후 즉시 수동 배출 가능 상태로 설정"""
        def enable_manual_dispense_immediately():
            time.sleep(self.manual_dispense_delay)  # 0초 즉시
            self.enable_manual_dispense(dose_info)
        
        # 백그라운드에서 즉시 수동 배출 활성화
        import _thread
        _thread.start_new_thread(enable_manual_dispense_immediately, ())
    
    def enable_manual_dispense(self, dose_info):
        """수동 배출 가능 상태 활성화"""
        self.manual_dispense_available = True
        
        # UI에 수동 배출 가능 알림
        ui_manager.show_manual_dispense_available(dose_info['type'])
        print(f"수동 배출 가능: {dose_info['type']} - 나중에 드실 수 있습니다")
        
        # 배출 대기 목록에 추가
        manual_dispense_manager.add_to_pending_list(dose_info)
    
    def check_manual_dispense_request(self):
        """수동 배출 요청 확인"""
        if self.manual_dispense_available:
            # 메뉴에서 수동 배출 요청 확인
            if ui_manager.is_manual_dispense_requested():
                return manual_dispense_manager.get_next_pending_dose()
        return None
```

#### 1.5.2 수동 배출 관리 시스템
```python
class ManualDispenseManager:
    """수동 배출 관리 시스템"""
    
    def __init__(self):
        self.pending_doses = []  # 대기 중인 배출 목록
        self.max_pending_count = 10  # 최대 대기 개수
    
    def add_to_pending_list(self, dose_info):
        """배출 대기 목록에 추가"""
        if len(self.pending_doses) < self.max_pending_count:
            pending_dose = {
                'dose_info': dose_info,
                'timestamp': time.time(),
                'status': 'pending'
            }
            self.pending_doses.append(pending_dose)
            print(f"배출 대기 목록 추가: {dose_info['type']}")
        else:
            print("배출 대기 목록이 가득 참 - 오래된 항목 제거")
            self.pending_doses.pop(0)  # 오래된 항목 제거
            self.add_to_pending_list(dose_info)  # 재귀 호출
    
    def get_next_pending_dose(self):
        """다음 대기 중인 배출 반환"""
        if self.pending_doses:
            return self.pending_doses.pop(0)
        return None
    
    def execute_manual_dispense(self, dose_info):
        """수동 배출 실행 (A 버튼 확인 필요)"""
        print(f"수동 배출 대기: {dose_info['type']} - A 버튼을 눌러주세요")
        
        # A 버튼 대기
        while True:
            if button_interface.is_button_pressed('A'):
                print(f"수동 배출 확인: {dose_info['type']}")
                return True
            time.sleep(0.1)
    
    def get_pending_list(self):
        """대기 중인 배출 목록 반환"""
        return self.pending_doses
    
    def clear_pending_list(self):
        """대기 목록 초기화"""
        self.pending_doses.clear()
        print("배출 대기 목록 초기화")
    
    def remove_expired_doses(self):
        """만료된 배출 항목 제거 (24시간 후)"""
        current_time = time.time()
        expired_time = 24 * 3600  # 24시간
        
        self.pending_doses = [
            dose for dose in self.pending_doses
            if current_time - dose['timestamp'] < expired_time
        ]
```

#### 1.5.3 배출 실패 로깅 시스템
```python
class DispenseFailureLogger:
    """배출 실패 로깅 시스템"""
    
    def __init__(self):
        self.failure_logs = []
        self.max_log_entries = 50
    
    def log_dispense_failure(self, failure_info):
        """배출 실패 기록"""
        log_entry = {
            'timestamp': failure_info['timestamp'],
            'dose_type': failure_info['dose_type'],
            'reason': failure_info['reason'],
            'retry_count': failure_info['retry_count'],
            'status': failure_info['status'],
            'manual_dispense_available': True,
            'expires_at': failure_info['timestamp'] + 300  # 5분 후 만료
        }
        
        self.failure_logs.append(log_entry)
        
        # 로그 크기 제한
        if len(self.failure_logs) > self.max_log_entries:
            self.failure_logs.pop(0)
        
        # 영구 저장
        self.save_failure_logs()
        
        print(f"배출 실패 기록: {failure_info['dose_type']} - {failure_info['reason']}")
    
    def get_failure_stats(self, days=7):
        """배출 실패 통계 조회"""
        cutoff_time = time.time() - (days * 24 * 3600)
        recent_failures = [
            log for log in self.failure_logs
            if log['timestamp'] > cutoff_time
        ]
        
        failure_by_type = {}
        for failure in recent_failures:
            dose_type = failure['dose_type']
            if dose_type not in failure_by_type:
                failure_by_type[dose_type] = 0
            failure_by_type[dose_type] += 1
        
        return {
            'total_failures': len(recent_failures),
            'failures_by_type': failure_by_type,
            'compliance_rate': self.calculate_compliance_rate(recent_failures)
        }
    
    def calculate_compliance_rate(self, recent_failures):
        """복약 순응도 계산"""
        # 전체 배출 시도 수 (성공 + 실패)
        total_attempts = len(recent_failures) + len(dispense_logger.get_dispense_history(7))
        if total_attempts == 0:
            return 100.0
        
        success_count = total_attempts - len(recent_failures)
        return (success_count / total_attempts) * 100
    
    def save_failure_logs(self):
        """실패 로그 영구 저장"""
        # 영구 저장 시스템에 저장
        persistent_storage.save_data('dispense_failures', self.failure_logs)
```

#### 1.5.4 통합 배출 확인 시스템
```python
class IntegratedDispenseConfirmation:
    """통합 배출 확인 시스템 (고급 재알람 + 수동 배출)"""
    
    def __init__(self):
        self.advanced_confirmation = AdvancedDispenseConfirmation()
        self.manual_manager = ManualDispenseManager()
        self.failure_logger = DispenseFailureLogger()
        self.medication_tracker = PersistentMedicationTracker()  # 약물 추적기 추가
    
    def start_dispense_process_with_confirmation(self, dose_info):
        """배출 프로세스 시작 (확인 시스템 포함)"""
        print(f"배출 프로세스 시작: {dose_info['type']}")
        
        # 1단계: 알람 실행
        alarm_system.trigger_alarm(dose_info['type'])
        
        # 2단계: 사용자 확인 대기 (재알람 포함)
        confirmed = self.advanced_confirmation.wait_for_user_confirmation_with_retry(dose_info)
        
        if confirmed:
            # 3단계: 배출 실행
            self.execute_dispense(dose_info)
            return True
        else:
            # 배출 실패 처리
            self.handle_dispense_failure(dose_info)
            return False
    
    def execute_dispense(self, dose_info):
        """실제 배출 실행"""
        try:
            # 디스크 회전
            disk_id = disk_manager.get_dispense_disk(dose_info['dose_count'])
            disk_manager.rotate_to_dispense_position(disk_id)
            
            # 게이트 개폐
            gate_controller.timed_gate_control(5)
            
            # 기록 및 정리
            self.medication_tracker.decrement_medication(disk_id, dose_info['compartment'])
            dispense_logger.log_dispense(dose_info, time.time(), True)
            
            print(f"배출 완료: {dose_info['type']}")
            
            # 약물 소진 확인
            self.check_medication_exhaustion(dose_info)
            
        except Exception as e:
            print(f"배출 실행 오류: {e}")
            self.handle_dispense_failure(dose_info)
    
    def check_medication_exhaustion(self, dose_info):
        """약물 소진 확인 및 알림"""
        try:
            # 배출된 디스크의 약물 상태 확인
            disk_id = disk_manager.get_dispense_disk(dose_info['dose_count'])
            remaining_count = self.medication_tracker.get_remaining_count(disk_id)
            
            print(f"디스크 {disk_id} 남은 약물: {remaining_count}개")
            
            # 약물이 소진되었는지 확인
            if remaining_count <= 0:
                print(f"⚠️ 디스크 {disk_id} 약물 소진!")
                self.trigger_medication_exhaustion_alarm(disk_id, dose_info['type'])
                
        except Exception as e:
            print(f"약물 소진 확인 중 오류: {e}")
    
    def trigger_medication_exhaustion_alarm(self, disk_id, dose_type):
        """약물 소진 알림 실행"""
        try:
            # LED 깜빡임 (빨간색으로 3초간)
            self.trigger_exhaustion_led_blink()
            
            # UI 메시지 표시
            self.ui_manager.show_medication_exhaustion_message(disk_id, dose_type)
            
            # 음성 알림 (선택사항)
            self.trigger_exhaustion_voice_alert(disk_id, dose_type)
            
            print(f"약물 소진 알림 실행: 디스크 {disk_id} ({dose_type})")
            
        except Exception as e:
            print(f"약물 소진 알림 실행 중 오류: {e}")
    
    def trigger_exhaustion_led_blink(self):
        """소진 알림용 LED 깜빡임"""
        try:
            # LED 제어 (빨간색으로 3초간 깜빡임)
            import _thread
            
            def led_blink_task():
                for i in range(6):  # 3초간 (0.5초 간격으로 6회)
                    # LED 켜기 (빨간색)
                    led_controller.set_color(255, 0, 0)  # Red
                    time.sleep(0.25)
                    # LED 끄기
                    led_controller.set_color(0, 0, 0)  # Off
                    time.sleep(0.25)
            
            _thread.start_new_thread(led_blink_task, ())
            
        except Exception as e:
            print(f"LED 깜빡임 실행 중 오류: {e}")
    
    def trigger_exhaustion_voice_alert(self, disk_id, dose_type):
        """소진 알림용 음성 출력"""
        try:
            # 음성 파일 재생 (선택사항)
            message = f"{dose_type} 약이 떨어졌습니다. 충전해주세요."
            audio_system.play_voice_message(message)
            
        except Exception as e:
            print(f"음성 알림 실행 중 오류: {e}")
    
    def handle_dispense_failure(self, dose_info):
        """배출 실패 처리"""
        failure_info = {
            'timestamp': time.time(),
            'dose_type': dose_info['type'],
            'reason': 'user_not_responded',
            'retry_count': self.advanced_confirmation.current_retry_count,
            'status': 'failed'
        }
        
        self.failure_logger.log_dispense_failure(failure_info)
        
        # 수동 배출 대기 목록에 추가
        self.manual_manager.add_to_pending_list(dose_info)
        
        print(f"배출 실패 처리 완료: {dose_info['type']}")
    
    def check_manual_dispense_requests(self):
        """수동 배출 요청 확인 (메인 루프에서 호출)"""
        # UI에서 수동 배출 요청 확인
        if ui_manager.is_manual_dispense_requested():
            pending_dose = self.manual_manager.get_next_pending_dose()
            if pending_dose:
                print(f"수동 배출 실행: {pending_dose['dose_info']['type']}")
                # A 버튼 확인 후 배출 실행
                if self.manual_manager.execute_manual_dispense(pending_dose['dose_info']):
                    self.execute_dispense(pending_dose['dose_info'])
                return True
        
        return False
    
    def get_pending_dispense_count(self):
        """대기 중인 배출 개수 반환"""
        return len(self.manual_manager.get_pending_list())
    
    def get_failure_statistics(self, days=7):
        """배출 실패 통계 반환"""
        return self.failure_logger.get_failure_stats(days)
```

#### 1.5.5 UI 통합 메시지 시스템
```python
class DispenseUIMessageManager:
    """배출 관련 UI 메시지 관리"""
    
    def __init__(self):
        self.current_message = None
        self.message_queue = []
    
    def show_dispense_failure_message(self, dose_type):
        """배출 실패 메시지 표시"""
        message = f"{dose_type} 배출 실패\n5회 알람 후 미응답\n메뉴에서 A 버튼으로 수동 배출 가능"
        self.display_message(message, duration=10)
    
    def show_manual_dispense_available(self, dose_type):
        """수동 배출 가능 알림"""
        message = f"{dose_type} 수동 배출 가능\n메뉴에서 A 버튼으로 배출하세요"
        self.display_message(message, duration=5)
    
    def show_pending_dispense_notification(self, count):
        """대기 중인 배출 알림"""
        if count > 0:
            message = f"대기 중인 배출: {count}개\n메뉴에서 A 버튼으로 확인하세요"
            self.display_notification(message)
    
    def show_medication_exhaustion_message(self, disk_id, dose_type):
        """약물 소진 메시지 표시"""
        message = f"⚠️ {dose_type} 약 소진!\n디스크 {disk_id} 충전하세요"
        self.display_message(message, duration=10)
        print(f"약물 소진 알림: 디스크 {disk_id} ({dose_type})")
    
    def display_message(self, message, duration=5):
        """메시지 표시"""
        self.current_message = message
        ui_manager.show_popup_message(message)
        
        # 지정된 시간 후 메시지 제거
        import _thread
        _thread.start_new_thread(self.clear_message_after_delay, (duration,))
    
    def display_notification(self, message):
        """알림 표시 (상단 바)"""
        ui_manager.show_top_notification(message)
    
    def clear_message_after_delay(self, delay):
        """지연 후 메시지 제거"""
        time.sleep(delay)
        self.current_message = None
        ui_manager.clear_popup_message()
```

### 1.6 복용 패턴별 로직 설계

#### 1.6.1 복용 패턴 정의
```python
class DosePattern:
    """복용 패턴 정의 클래스"""
    PATTERNS = {
        "ALL_THREE": {  # 아침, 점심, 저녁 모두
            "name": "하루 3회",
            "doses": ["morning", "lunch", "dinner"],
            "disk_mapping": {"morning": 1, "lunch": 2, "dinner": 3}
        },
        "MORNING_LUNCH": {  # 아침, 점심
            "name": "하루 2회 (아침, 점심)",
            "doses": ["morning", "lunch"],
            "disk_mapping": {"morning": 1, "lunch": 2}
        },
        "MORNING_DINNER": {  # 아침, 저녁
            "name": "하루 2회 (아침, 저녁)",
            "doses": ["morning", "dinner"],
            "disk_mapping": {"morning": 1, "dinner": 3}
        },
        "LUNCH_DINNER": {  # 점심, 저녁
            "name": "하루 2회 (점심, 저녁)",
            "doses": ["lunch", "dinner"],
            "disk_mapping": {"lunch": 2, "dinner": 3}
        },
        "MORNING_ONLY": {  # 아침만
            "name": "하루 1회 (아침)",
            "doses": ["morning"],
            "disk_mapping": {"morning": 1}
        },
        "LUNCH_ONLY": {  # 점심만
            "name": "하루 1회 (점심)",
            "doses": ["lunch"],
            "disk_mapping": {"lunch": 2}
        },
        "DINNER_ONLY": {  # 저녁만
            "name": "하루 1회 (저녁)",
            "doses": ["dinner"],
            "disk_mapping": {"dinner": 3}
        }
    }
```

#### 1.6.2 복용 패턴 매니저
```python
class DosePatternManager:
    """복용 패턴 관리 클래스"""
    
    def __init__(self):
        self.current_pattern = None
        self.dose_times = {}  # {dose_type: time}
        self.disk_usage = {1: False, 2: False, 3: False}  # 디스크 사용 여부
        
    def set_dose_pattern(self, pattern_name, dose_times):
        """복용 패턴 설정"""
        if pattern_name not in DosePattern.PATTERNS:
            raise ValueError(f"지원하지 않는 복용 패턴: {pattern_name}")
        
        self.current_pattern = DosePattern.PATTERNS[pattern_name]
        self.dose_times = dose_times
        
        # 사용할 디스크 설정
        self._configure_disk_usage()
        
        print(f"복용 패턴 설정: {self.current_pattern['name']}")
        print(f"복용 시간: {dose_times}")
        print(f"사용 디스크: {[k for k, v in self.disk_usage.items() if v]}")
    
    def _configure_disk_usage(self):
        """패턴에 따른 디스크 사용 설정"""
        # 모든 디스크 초기화
        self.disk_usage = {1: False, 2: False, 3: False}
        
        # 패턴에 따른 디스크 활성화
        for dose_type in self.current_pattern['doses']:
            disk_id = self.current_pattern['disk_mapping'][dose_type]
            self.disk_usage[disk_id] = True
    
    def get_next_dispense_time(self):
        """다음 배출 시간 계산"""
        current_time = self.get_current_time()
        next_times = []
        
        for dose_type, dose_time in self.dose_times.items():
            # 오늘의 배출 시간 계산
            today_dose_time = self._calculate_today_time(dose_time)
            
            # 이미 지난 시간이면 내일로 계산
            if today_dose_time <= current_time:
                tomorrow_dose_time = today_dose_time + 24 * 3600  # 24시간 후
                next_times.append((dose_type, tomorrow_dose_time))
            else:
                next_times.append((dose_type, today_dose_time))
        
        # 가장 가까운 시간 반환
        if next_times:
            return min(next_times, key=lambda x: x[1])
        return None
    
    def _calculate_today_time(self, time_str):
        """시간 문자열을 오늘의 타임스탬프로 변환"""
        # "08:00" 형식의 문자열을 파싱
        hour, minute = map(int, time_str.split(':'))
        
        # 오늘 날짜의 해당 시간 계산
        today = time.localtime()
        today_time = time.mktime((
            today.tm_year, today.tm_mon, today.tm_mday,
            hour, minute, 0, 0, 0, -1
        ))
        
        return today_time
    
    def get_dose_type_for_time(self, target_time):
        """특정 시간에 해당하는 복용 타입 반환"""
        for dose_type, dose_time_str in self.dose_times.items():
            today_dose_time = self._calculate_today_time(dose_time_str)
            
            # 시간 차이가 5분 이내면 해당 복용 타입
            if abs(today_dose_time - target_time) <= 300:  # 5분 = 300초
                return dose_type
        
        return None
```

#### 1.6.3 패턴별 설정 예시
```python
# 사용 예시
pattern_manager = DosePatternManager()

# 예시 1: 하루 3회 (아침, 점심, 저녁)
pattern_manager.set_dose_pattern("ALL_THREE", {
    "morning": "08:00",
    "lunch": "12:00", 
    "dinner": "18:00"
})
# 결과: 디스크 1,2,3 모두 사용

# 예시 2: 하루 2회 (아침, 저녁)
pattern_manager.set_dose_pattern("MORNING_DINNER", {
    "morning": "08:00",
    "dinner": "19:00"
})
# 결과: 디스크 1,3 사용, 디스크 2 미사용

# 예시 3: 하루 1회 (아침만)
pattern_manager.set_dose_pattern("MORNING_ONLY", {
    "morning": "09:00"
})
# 결과: 디스크 1만 사용, 디스크 2,3 미사용
```

#### 1.6.4 복용 패턴별 디스크 관리
```python
class PatternBasedDiskManager:
    """패턴 기반 디스크 관리 클래스"""
    
    def __init__(self, pattern_manager):
        self.pattern_manager = pattern_manager
        self.disk_states = {
            1: {'active': False, 'current_compartment': 0, 'medication_count': [0] * 15},
            2: {'active': False, 'current_compartment': 0, 'medication_count': [0] * 15},
            3: {'active': False, 'current_compartment': 0, 'medication_count': [0] * 15}
        }
    
    def update_disk_states(self):
        """패턴 변경 시 디스크 상태 업데이트"""
        for disk_id in [1, 2, 3]:
            self.disk_states[disk_id]['active'] = self.pattern_manager.disk_usage[disk_id]
            
            if self.disk_states[disk_id]['active']:
                print(f"디스크 {disk_id} 활성화됨")
            else:
                print(f"디스크 {disk_id} 비활성화됨")
    
    def get_active_disks(self):
        """활성화된 디스크 목록 반환"""
        return [disk_id for disk_id, state in self.disk_states.items() if state['active']]
    
    def get_disk_for_dose_type(self, dose_type):
        """복용 타입에 해당하는 디스크 ID 반환"""
        if self.pattern_manager.current_pattern:
            return self.pattern_manager.current_pattern['disk_mapping'].get(dose_type)
        return None
    
    def check_medication_availability(self, dose_type):
        """해당 복용 타입의 알약 가용성 확인"""
        disk_id = self.get_disk_for_dose_type(dose_type)
        if disk_id and self.disk_states[disk_id]['active']:
            current_compartment = self.disk_states[disk_id]['current_compartment']
            medication_count = self.disk_states[disk_id]['medication_count'][current_compartment]
            return medication_count > 0
        return False
    
    def dispense_medication(self, dose_type):
        """복용 타입에 따른 알약 배출"""
        disk_id = self.get_disk_for_dose_type(dose_type)
        if disk_id and self.disk_states[disk_id]['active']:
            current_compartment = self.disk_states[disk_id]['current_compartment']
            
            # 알약 개수 차감
            if self.disk_states[disk_id]['medication_count'][current_compartment] > 0:
                self.disk_states[disk_id]['medication_count'][current_compartment] -= 1
                print(f"디스크 {disk_id}, 칸 {current_compartment}에서 알약 배출")
                
                # 다음 칸으로 이동
                self.disk_states[disk_id]['current_compartment'] = (
                    (current_compartment + 1) % 15
                )
                return True
        
        print(f"복용 타입 {dose_type}에 대한 알약 배출 실패")
        return False
```

#### 1.6.5 복용 패턴별 알람 시스템
```python
class PatternBasedAlarmSystem:
    """패턴 기반 알람 시스템"""
    
    def __init__(self, pattern_manager):
        self.pattern_manager = pattern_manager
        self.alarm_messages = {
            "morning": "아침 약 드실 시간입니다.",
            "lunch": "점심 약 드실 시간입니다.", 
            "dinner": "저녁 약 드실 시간입니다."
        }
    
    def get_alarm_message(self, dose_type):
        """복용 타입에 따른 알람 메시지 반환"""
        return self.alarm_messages.get(dose_type, "복용 시간입니다.")
    
    def trigger_pattern_alarm(self, dose_type):
        """패턴에 따른 알람 실행"""
        if dose_type in self.pattern_manager.current_pattern['doses']:
            message = self.get_alarm_message(dose_type)
            alarm_system.trigger_alarm(message)
            print(f"복용 패턴 알람 실행: {dose_type}")
        else:
            print(f"현재 패턴에 없는 복용 타입: {dose_type}")
```

#### 1.6.6 통합 복용 패턴 매니저
```python
class IntegratedDoseManager:
    """통합 복용 패턴 관리자"""
    
    def __init__(self):
        self.pattern_manager = DosePatternManager()
        self.disk_manager = PatternBasedDiskManager(self.pattern_manager)
        self.alarm_system = PatternBasedAlarmSystem(self.pattern_manager)
        self.dispense_manager = DispenseManager()
    
    def setup_medication_pattern(self, pattern_name, dose_times):
        """복용 패턴 설정 및 시스템 초기화"""
        # 패턴 설정
        self.pattern_manager.set_dose_pattern(pattern_name, dose_times)
        
        # 디스크 상태 업데이트
        self.disk_manager.update_disk_states()
        
        # 활성화된 디스크만 원점 보정
        active_disks = self.disk_manager.get_active_disks()
        self._calibrate_active_disks(active_disks)
        
        print(f"복용 패턴 '{pattern_name}' 설정 완료")
    
    def _calibrate_active_disks(self, active_disks):
        """활성화된 디스크만 원점 보정"""
        if active_disks:
            motor_indices = [disk_id for disk_id in active_disks]
            motor_controller.calibrate_multiple_motors(motor_indices)
            print(f"활성 디스크 원점 보정 완료: {active_disks}")
    
    def check_and_dispense(self):
        """복용 시간 확인 및 배출 실행"""
        next_dispense = self.pattern_manager.get_next_dispense_time()
        
        if next_dispense:
            dose_type, dispense_time = next_dispense
            current_time = time.time()
            
            # 복용 시간 도달 확인 (1분 허용 오차)
            if abs(current_time - dispense_time) <= 60:
                self._execute_dispense(dose_type)
    
    def _execute_dispense(self, dose_type):
        """실제 배출 실행"""
        # 알약 가용성 확인
        if not self.disk_manager.check_medication_availability(dose_type):
            print(f"⚠️ {dose_type} 알약 부족 - 배출 중단")
            return
        
        # 알람 실행
        self.alarm_system.trigger_pattern_alarm(dose_type)
        
        # 사용자 확인 대기
        if self._wait_for_user_confirmation():
            # 배출 실행
            success = self.disk_manager.dispense_medication(dose_type)
            if success:
                print(f"✅ {dose_type} 배출 완료")
            else:
                print(f"❌ {dose_type} 배출 실패")
    
    def _wait_for_user_confirmation(self):
        """사용자 확인 대기"""
        # 30초 타임아웃으로 사용자 확인 대기
        start_time = time.time()
        while time.time() - start_time < 30:
            if button_interface.is_button_pressed('D'):  # Select 버튼
                return True
            time.sleep(0.1)
        return False
```

#### 1.6.7 복용 패턴 설정 UI 통합
```python
class DosePatternSetupUI:
    """복용 패턴 설정 UI"""
    
    def __init__(self, dose_manager):
        self.dose_manager = dose_manager
        self.setup_patterns = [
            ("ALL_THREE", "하루 3회 (아침, 점심, 저녁)"),
            ("MORNING_LUNCH", "하루 2회 (아침, 점심)"),
            ("MORNING_DINNER", "하루 2회 (아침, 저녁)"),
            ("LUNCH_DINNER", "하루 2회 (점심, 저녁)"),
            ("MORNING_ONLY", "하루 1회 (아침)"),
            ("LUNCH_ONLY", "하루 1회 (점심)"),
            ("DINNER_ONLY", "하루 1회 (저녁)")
        ]
    
    def show_pattern_selection(self):
        """복용 패턴 선택 화면 표시"""
        print("복용 패턴을 선택하세요:")
        for i, (pattern_id, pattern_name) in enumerate(self.setup_patterns):
            print(f"{i+1}. {pattern_name}")
    
    def setup_pattern_times(self, pattern_id):
        """선택된 패턴의 시간 설정"""
        pattern = DosePattern.PATTERNS[pattern_id]
        dose_times = {}
        
        for dose_type in pattern['doses']:
            time_str = self._get_time_input(dose_type)
            dose_times[dose_type] = time_str
        
        return dose_times
    
    def _get_time_input(self, dose_type):
        """복용 타입별 시간 입력 받기"""
        dose_names = {
            "morning": "아침",
            "lunch": "점심", 
            "dinner": "저녁"
        }
        
        print(f"{dose_names[dose_type]} 복용 시간을 입력하세요 (예: 08:00):")
        # 실제 구현에서는 키보드 입력 또는 롤러 UI 사용
        return "08:00"  # 예시 값
```

### 1.7 에러 처리 및 안전 장치

#### 1.6.1 배출 실패 처리
```python
class DispenseErrorHandler:
    def __init__(self):
        self.max_retry_count = 3
        self.retry_delay = 2  # 2초
    
    def handle_dispense_error(self, error_type, error_details):
        """배출 오류 처리"""
        if error_type == "MOTOR_STUCK":
            self.handle_motor_stuck_error()
        elif error_type == "GATE_FAILURE":
            self.handle_gate_failure_error()
        elif error_type == "DISK_MISALIGNMENT":
            self.handle_disk_misalignment_error()
        
        # 사용자에게 오류 알림
        self.notify_user_of_error(error_type)
    
    def retry_dispense(self, dose_info):
        """배출 재시도"""
        for attempt in range(self.max_retry_count):
            try:
                dispense_manager.start_dispense_process(dose_info)
                return True
            except Exception as e:
                print(f"배출 재시도 {attempt + 1}/{self.max_retry_count} 실패: {e}")
                time.sleep(self.retry_delay)
        
        return False
```

#### 1.6.2 안전 장치
- **모터 과부하 보호**: 전류 센서를 통한 모터 상태 모니터링
- **게이트 상태 확인**: 리미트 스위치를 통한 게이트 개방/폐쇄 상태 확인
- **디스크 위치 검증**: 원점 보정을 통한 정확한 위치 확인
- **배출 로그**: 모든 배출 활동 기록 및 추적

### 1.7 데이터 관리 및 영구 저장

#### 1.7.1 영구 저장 시스템
```python
import json
import os

class PersistentStorage:
    """영구 저장 시스템"""
    
    def __init__(self):
        self.storage_dir = "/flash/data"
        self.files = {
            'dose_patterns': '/flash/data/dose_patterns.json',
            'dispense_history': '/flash/data/dispense_history.json',
            'medication_tracking': '/flash/data/medication_tracking.json',
            'disk_positions': '/flash/data/disk_positions.json',
            'system_settings': '/flash/data/system_settings.json',
            'user_settings': '/flash/data/user_settings.json',
            'alarm_settings': '/flash/data/alarm_settings.json',
            'wifi_settings': '/flash/data/wifi_settings.json'
        }
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self):
        """저장 디렉토리 확인 및 생성"""
        try:
            os.mkdir(self.storage_dir)
            print("데이터 저장 디렉토리 생성됨")
        except OSError:
            pass  # 이미 존재함
    
    def save_data(self, data_type, data):
        """데이터 저장"""
        if data_type not in self.files:
            raise ValueError(f"지원하지 않는 데이터 타입: {data_type}")
        
        try:
            with open(self.files[data_type], 'w') as f:
                json.dump(data, f)
            print(f"✅ {data_type} 데이터 저장 완료")
            return True
        except Exception as e:
            print(f"❌ {data_type} 데이터 저장 실패: {e}")
            return False
    
    def load_data(self, data_type):
        """데이터 로드"""
        if data_type not in self.files:
            raise ValueError(f"지원하지 않는 데이터 타입: {data_type}")
        
        try:
            with open(self.files[data_type], 'r') as f:
                data = json.load(f)
            print(f"✅ {data_type} 데이터 로드 완료")
            return data
        except OSError:
            print(f"⚠️ {data_type} 파일이 존재하지 않음 - 기본값 반환")
            return self._get_default_data(data_type)
        except Exception as e:
            print(f"❌ {data_type} 데이터 로드 실패: {e}")
            return self._get_default_data(data_type)
    
    def _get_default_data(self, data_type):
        """기본 데이터 반환"""
        defaults = {
            'dose_patterns': {
                'current_pattern': None,
                'dose_times': {},
                'disk_usage': {1: False, 2: False, 3: False}
            },
            'dispense_history': [],
            'medication_tracking': {
                1: [10] * 15,  # 디스크 1, 15칸, 각각 10개
                2: [10] * 15,  # 디스크 2, 15칸, 각각 10개
                3: [10] * 15   # 디스크 3, 15칸, 각각 10개
            },
            'disk_positions': {
                1: {'current_compartment': 0, 'motor_steps': 0},
                2: {'current_compartment': 0, 'motor_steps': 0},
                3: {'current_compartment': 0, 'motor_steps': 0},
                4: {'current_position': 0}  # 게이트 모터
            },
            'system_settings': {
                'timezone': 'Asia/Seoul',
                'ntp_server': 'pool.ntp.org',
                'auto_save_interval': 300,  # 5분
                'max_log_entries': 100,
                'calibration_interval': 86400  # 24시간
            },
            'user_settings': {
                'language': 'ko',
                'volume_level': 70,
                'brightness_level': 80,
                'auto_dispense': True,
                'confirmation_timeout': 30
            },
            'alarm_settings': {
                'voice_enabled': True,
                'led_enabled': True,
                'buzzer_enabled': True,
                'alarm_duration': 30,
                'reminder_interval': 300  # 5분마다 리마인더
            },
            'wifi_settings': {
                'ssid': '',
                'password': '',
                'auto_connect': True,
                'last_connected': None
            }
        }
        return defaults.get(data_type, {})
    
    def clear_all_data(self):
        """모든 데이터 삭제 (초기화)"""
        for data_type in self.files:
            try:
                os.remove(self.files[data_type])
                print(f"✅ {data_type} 데이터 삭제 완료")
            except OSError:
                pass  # 파일이 존재하지 않음
```

#### 1.7.2 복용 패턴 영구 저장
```python
class PersistentDosePatternManager(DosePatternManager):
    """영구 저장 기능이 있는 복용 패턴 관리자"""
    
    def __init__(self):
        super().__init__()
        self.storage = PersistentStorage()
        self._load_saved_pattern()
    
    def _load_saved_pattern(self):
        """저장된 패턴 로드"""
        saved_data = self.storage.load_data('dose_patterns')
        
        if saved_data['current_pattern']:
            self.current_pattern = saved_data['current_pattern']
            self.dose_times = saved_data['dose_times']
            self.disk_usage = saved_data['disk_usage']
            print(f"저장된 복용 패턴 로드: {self.current_pattern['name']}")
    
    def set_dose_pattern(self, pattern_name, dose_times):
        """복용 패턴 설정 및 저장"""
        super().set_dose_pattern(pattern_name, dose_times)
        self._save_pattern()
    
    def _save_pattern(self):
        """현재 패턴 저장"""
        pattern_data = {
            'current_pattern': self.current_pattern,
            'dose_times': self.dose_times,
            'disk_usage': self.disk_usage
        }
        self.storage.save_data('dose_patterns', pattern_data)
    
    def update_dose_time(self, dose_type, new_time):
        """복용 시간 업데이트 및 저장"""
        if dose_type in self.dose_times:
            self.dose_times[dose_type] = new_time
            self._save_pattern()
            print(f"{dose_type} 복용 시간 업데이트: {new_time}")
```

#### 1.7.3 배출 기록 영구 저장
```python
class PersistentDispenseLogger:
    """영구 저장 기능이 있는 배출 기록 관리자"""
    
    def __init__(self):
        self.storage = PersistentStorage()
        self.dispense_log = self._load_dispense_history()
        self.max_log_entries = 100
        self.auto_save_enabled = True
    
    def _load_dispense_history(self):
        """저장된 배출 기록 로드"""
        return self.storage.load_data('dispense_history')
    
    def log_dispense(self, dose_info, timestamp, success):
        """배출 기록 저장 및 영구 저장"""
        log_entry = {
            'timestamp': timestamp,
            'dose_type': dose_info['type'],
            'disk_id': dose_info['disk_id'],
            'compartment': dose_info['compartment'],
            'success': success,
            'error_message': dose_info.get('error', None),
            'user_confirmed': dose_info.get('user_confirmed', False)
        }
        
        self.dispense_log.append(log_entry)
        
        # 로그 크기 제한
        if len(self.dispense_log) > self.max_log_entries:
            self.dispense_log.pop(0)
        
        # 즉시 영구 저장
        if self.auto_save_enabled:
            self._save_dispense_history()
    
    def _save_dispense_history(self):
        """배출 기록 영구 저장"""
        self.storage.save_data('dispense_history', self.dispense_log)
    
    def get_dispense_history(self, days=7):
        """지정된 기간의 배출 기록 조회"""
        cutoff_time = time.time() - (days * 24 * 3600)
        return [log for log in self.dispense_log if log['timestamp'] > cutoff_time]
    
    def get_compliance_rate(self, days=7):
        """복약 순응도 계산"""
        recent_logs = self.get_dispense_history(days)
        if not recent_logs:
            return 0.0
        
        successful_dispenses = len([log for log in recent_logs if log['success']])
        total_dispenses = len(recent_logs)
        
        return (successful_dispenses / total_dispenses) * 100 if total_dispenses > 0 else 0.0
    
    def export_history(self, filename=None):
        """배출 기록 내보내기 (JSON 형태)"""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"/flash/exports/dispense_history_{timestamp}.json"
        
        try:
            # 내보내기 디렉토리 생성
            os.makedirs("/flash/exports", exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(self.dispense_log, f, indent=2)
            
            print(f"배출 기록 내보내기 완료: {filename}")
            return filename
        except Exception as e:
            print(f"배출 기록 내보내기 실패: {e}")
            return None
```

#### 1.7.4 복용량 추적 영구 저장
```python
class PersistentMedicationTracker:
    """영구 저장 기능이 있는 복용량 추적 관리자"""
    
    def __init__(self):
        self.storage = PersistentStorage()
        self.medication_count = self._load_medication_tracking()
        self.auto_save_enabled = True
    
    def _load_medication_tracking(self):
        """저장된 복용량 추적 데이터 로드"""
        return self.storage.load_data('medication_tracking')
    
    def decrement_medication(self, disk_id, compartment):
        """배출 후 해당 칸의 알약 개수 차감 및 저장"""
        if self.medication_count[disk_id][compartment] > 0:
            self.medication_count[disk_id][compartment] -= 1
            print(f"디스크 {disk_id}, 칸 {compartment}: {self.medication_count[disk_id][compartment]}개 남음")
            
            # 즉시 영구 저장
            if self.auto_save_enabled:
                self._save_medication_tracking()
            
            # 알약 부족 경고
            if self.medication_count[disk_id][compartment] <= 2:
                self.notify_low_medication(disk_id, compartment)
    
    def refill_medication(self, disk_id, compartment, count):
        """알약 리필 및 저장"""
        if 1 <= disk_id <= 3 and 0 <= compartment <= 14:
            self.medication_count[disk_id][compartment] += count
            print(f"디스크 {disk_id}, 칸 {compartment}: {count}개 리필 완료")
            
            # 즉시 영구 저장
            if self.auto_save_enabled:
                self._save_medication_tracking()
    
    def _save_medication_tracking(self):
        """복용량 추적 데이터 영구 저장"""
        self.storage.save_data('medication_tracking', self.medication_count)
    
    def get_medication_status(self):
        """전체 알약 상태 조회"""
        total_medications = 0
        low_medication_warnings = []
        
        for disk_id in [1, 2, 3]:
            for compartment in range(15):
                count = self.medication_count[disk_id][compartment]
                total_medications += count
                
                if count <= 2:
                    low_medication_warnings.append({
                        'disk_id': disk_id,
                        'compartment': compartment,
                        'count': count
                    })
        
        return {
            'total_medications': total_medications,
            'low_medication_warnings': low_medication_warnings,
            'disk_summary': {
                disk_id: sum(self.medication_count[disk_id])
                for disk_id in [1, 2, 3]
            }
        }
    
    def notify_low_medication(self, disk_id, compartment):
        """알약 부족 알림"""
        print(f"⚠️ 알약 부족 경고: 디스크 {disk_id}, 칸 {compartment}")
        # UI에 알약 부족 표시
        ui_manager.show_low_medication_warning(disk_id, compartment)
```

#### 1.7.5 디스크 위치 영구 저장
```python
class PersistentDiskPositionManager:
    """영구 저장 기능이 있는 디스크 위치 관리자"""
    
    def __init__(self):
        self.storage = PersistentStorage()
        self.disk_positions = self._load_disk_positions()
        self.auto_save_enabled = True
    
    def _load_disk_positions(self):
        """저장된 디스크 위치 데이터 로드"""
        return self.storage.load_data('disk_positions')
    
    def update_disk_position(self, disk_id, compartment, motor_steps):
        """디스크 위치 업데이트 및 저장"""
        if 1 <= disk_id <= 4:
            self.disk_positions[disk_id] = {
                'current_compartment': compartment,
                'motor_steps': motor_steps,
                'last_updated': time.time()
            }
            
            # 즉시 영구 저장
            if self.auto_save_enabled:
                self._save_disk_positions()
            
            print(f"디스크 {disk_id} 위치 업데이트: 칸 {compartment}, 스텝 {motor_steps}")
    
    def get_disk_position(self, disk_id):
        """디스크 위치 조회"""
        return self.disk_positions.get(disk_id, {
            'current_compartment': 0,
            'motor_steps': 0,
            'last_updated': 0
        })
    
    def _save_disk_positions(self):
        """디스크 위치 데이터 영구 저장"""
        self.storage.save_data('disk_positions', self.disk_positions)
    
    def reset_disk_positions(self):
        """디스크 위치 초기화 (원점 보정 후)"""
        for disk_id in [1, 2, 3, 4]:
            self.disk_positions[disk_id] = {
                'current_compartment': 0,
                'motor_steps': 0,
                'last_updated': time.time()
            }
        
        self._save_disk_positions()
        print("모든 디스크 위치 초기화 완료")
```

#### 1.7.6 시스템 설정 영구 저장
```python
class PersistentSystemSettings:
    """영구 저장 기능이 있는 시스템 설정 관리자"""
    
    def __init__(self):
        self.storage = PersistentStorage()
        self.system_settings = self._load_system_settings()
        self.user_settings = self._load_user_settings()
        self.alarm_settings = self._load_alarm_settings()
        self.wifi_settings = self._load_wifi_settings()
    
    def _load_system_settings(self):
        """시스템 설정 로드"""
        return self.storage.load_data('system_settings')
    
    def _load_user_settings(self):
        """사용자 설정 로드"""
        return self.storage.load_data('user_settings')
    
    def _load_alarm_settings(self):
        """알람 설정 로드"""
        return self.storage.load_data('alarm_settings')
    
    def _load_wifi_settings(self):
        """Wi-Fi 설정 로드"""
        return self.storage.load_data('wifi_settings')
    
    def update_system_setting(self, key, value):
        """시스템 설정 업데이트"""
        self.system_settings[key] = value
        self.storage.save_data('system_settings', self.system_settings)
        print(f"시스템 설정 업데이트: {key} = {value}")
    
    def update_user_setting(self, key, value):
        """사용자 설정 업데이트"""
        self.user_settings[key] = value
        self.storage.save_data('user_settings', self.user_settings)
        print(f"사용자 설정 업데이트: {key} = {value}")
    
    def update_alarm_setting(self, key, value):
        """알람 설정 업데이트"""
        self.alarm_settings[key] = value
        self.storage.save_data('alarm_settings', self.alarm_settings)
        print(f"알람 설정 업데이트: {key} = {value}")
    
    def update_wifi_setting(self, key, value):
        """Wi-Fi 설정 업데이트"""
        self.wifi_settings[key] = value
        self.storage.save_data('wifi_settings', self.wifi_settings)
        print(f"Wi-Fi 설정 업데이트: {key} = {value}")
    
    def get_setting(self, category, key):
        """설정 값 조회"""
        settings_map = {
            'system': self.system_settings,
            'user': self.user_settings,
            'alarm': self.alarm_settings,
            'wifi': self.wifi_settings
        }
        return settings_map.get(category, {}).get(key)
    
    def backup_all_settings(self):
        """모든 설정 백업"""
        backup_data = {
            'system_settings': self.system_settings,
            'user_settings': self.user_settings,
            'alarm_settings': self.alarm_settings,
            'wifi_settings': self.wifi_settings,
            'backup_timestamp': time.time()
        }
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_filename = f"/flash/backups/settings_backup_{timestamp}.json"
        
        try:
            # 백업 디렉토리 생성
            os.makedirs("/flash/backups", exist_ok=True)
            
            with open(backup_filename, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            print(f"설정 백업 완료: {backup_filename}")
            return backup_filename
        except Exception as e:
            print(f"설정 백업 실패: {e}")
            return None
    
    def restore_settings_from_backup(self, backup_filename):
        """백업 파일에서 설정 복원"""
        try:
            with open(backup_filename, 'r') as f:
                backup_data = json.load(f)
            
            # 각 설정 카테고리별로 복원
            for category in ['system_settings', 'user_settings', 'alarm_settings', 'wifi_settings']:
                if category in backup_data:
                    self.storage.save_data(category.replace('_settings', '_settings'), backup_data[category])
            
            # 메모리에도 로드
            self.system_settings = self._load_system_settings()
            self.user_settings = self._load_user_settings()
            self.alarm_settings = self._load_alarm_settings()
            self.wifi_settings = self._load_wifi_settings()
            
            print(f"설정 복원 완료: {backup_filename}")
            return True
        except Exception as e:
            print(f"설정 복원 실패: {e}")
            return False
```

#### 1.7.7 자동 저장 스케줄러
```python
class AutoSaveScheduler:
    """자동 저장 스케줄러"""
    
    def __init__(self):
        self.save_interval = 300  # 5분
        self.last_save_time = time.time()
        self.storage = PersistentStorage()
        self.managers = {}  # 등록된 매니저들
    
    def register_manager(self, name, manager):
        """매니저 등록"""
        self.managers[name] = manager
        print(f"자동 저장 매니저 등록: {name}")
    
    def check_and_save(self):
        """주기적 저장 확인"""
        current_time = time.time()
        
        if current_time - self.last_save_time >= self.save_interval:
            self._perform_auto_save()
            self.last_save_time = current_time
    
    def _perform_auto_save(self):
        """자동 저장 실행"""
        print("자동 저장 시작...")
        
        for name, manager in self.managers.items():
            try:
                if hasattr(manager, 'auto_save'):
                    manager.auto_save()
                print(f"✅ {name} 자동 저장 완료")
            except Exception as e:
                print(f"❌ {name} 자동 저장 실패: {e}")
        
        print("자동 저장 완료")
    
    def force_save_all(self):
        """모든 데이터 강제 저장"""
        print("강제 저장 시작...")
        self._perform_auto_save()
        print("강제 저장 완료")
```

#### 1.7.8 통합 영구 저장 매니저
```python
class IntegratedPersistentManager:
    """통합 영구 저장 매니저"""
    
    def __init__(self):
        self.storage = PersistentStorage()
        self.pattern_manager = PersistentDosePatternManager()
        self.dispense_logger = PersistentDispenseLogger()
        self.medication_tracker = PersistentMedicationTracker()
        self.disk_position_manager = PersistentDiskPositionManager()
        self.system_settings = PersistentSystemSettings()
        self.auto_save_scheduler = AutoSaveScheduler()
        
        # 자동 저장 스케줄러에 매니저들 등록
        self._register_managers()
    
    def _register_managers(self):
        """자동 저장 스케줄러에 매니저들 등록"""
        self.auto_save_scheduler.register_manager("pattern_manager", self.pattern_manager)
        self.auto_save_scheduler.register_manager("dispense_logger", self.dispense_logger)
        self.auto_save_scheduler.register_manager("medication_tracker", self.medication_tracker)
        self.auto_save_scheduler.register_manager("disk_position_manager", self.disk_position_manager)
    
    def initialize_from_storage(self):
        """저장된 데이터로 시스템 초기화"""
        print("영구 저장 데이터로 시스템 초기화 중...")
        
        # 각 매니저의 데이터 로드 (이미 생성자에서 자동 로드됨)
        print("✅ 복용 패턴 로드 완료")
        print("✅ 배출 기록 로드 완료")
        print("✅ 복용량 추적 데이터 로드 완료")
        print("✅ 디스크 위치 데이터 로드 완료")
        print("✅ 시스템 설정 로드 완료")
        
        print("시스템 초기화 완료")
    
    def perform_maintenance(self):
        """데이터 유지보수 작업"""
        print("데이터 유지보수 작업 시작...")
        
        # 자동 저장 실행
        self.auto_save_scheduler.check_and_save()
        
        # 로그 정리 (오래된 로그 삭제)
        self._cleanup_old_logs()
        
        # 백업 생성 (일주일마다)
        self._create_weekly_backup()
        
        print("데이터 유지보수 작업 완료")
    
    def _cleanup_old_logs(self):
        """오래된 로그 정리"""
        # 30일 이상 된 로그 삭제
        cutoff_time = time.time() - (30 * 24 * 3600)
        original_count = len(self.dispense_logger.dispense_log)
        
        self.dispense_logger.dispense_log = [
            log for log in self.dispense_logger.dispense_log 
            if log['timestamp'] > cutoff_time
        ]
        
        removed_count = original_count - len(self.dispense_logger.dispense_log)
        if removed_count > 0:
            print(f"오래된 로그 {removed_count}개 정리 완료")
            self.dispense_logger._save_dispense_history()
    
    def _create_weekly_backup(self):
        """주간 백업 생성"""
        # 매주 월요일에 백업 생성
        current_time = time.localtime()
        if current_time.tm_wday == 0:  # 월요일
            self.system_settings.backup_all_settings()
    
    def get_system_status(self):
        """전체 시스템 상태 조회"""
        return {
            'pattern_info': {
                'current_pattern': self.pattern_manager.current_pattern,
                'dose_times': self.pattern_manager.dose_times,
                'active_disks': [k for k, v in self.pattern_manager.disk_usage.items() if v]
            },
            'medication_status': self.medication_tracker.get_medication_status(),
            'dispense_stats': {
                'total_dispenses': len(self.dispense_logger.dispense_log),
                'compliance_rate': self.dispense_logger.get_compliance_rate(7),
                'recent_dispenses': len(self.dispense_logger.get_dispense_history(1))
            },
            'disk_positions': {
                disk_id: self.disk_position_manager.get_disk_position(disk_id)
                for disk_id in [1, 2, 3, 4]
            },
            'storage_info': {
                'auto_save_enabled': True,
                'last_auto_save': self.auto_save_scheduler.last_save_time,
                'storage_directory': self.storage.storage_dir
            }
        }
    
    def emergency_backup(self):
        """긴급 백업 (전원 차단 전)"""
        print("긴급 백업 시작...")
        
        # 모든 데이터 강제 저장
        self.auto_save_scheduler.force_save_all()
        
        # 설정 백업
        backup_file = self.system_settings.backup_all_settings()
        
        print(f"긴급 백업 완료: {backup_file}")
        return backup_file
    
    def factory_reset(self):
        """공장 초기화 (모든 데이터 삭제)"""
        print("⚠️ 공장 초기화 시작 - 모든 데이터가 삭제됩니다!")
        
        # 모든 데이터 파일 삭제
        self.storage.clear_all_data()
        
        # 메모리 데이터 초기화
        self.pattern_manager = PersistentDosePatternManager()
        self.dispense_logger = PersistentDispenseLogger()
        self.medication_tracker = PersistentMedicationTracker()
        self.disk_position_manager = PersistentDiskPositionManager()
        self.system_settings = PersistentSystemSettings()
        
        print("공장 초기화 완료 - 시스템을 재시작하세요")
```

### 1.8 메인 배출 매니저

#### 1.8.1 통합 배출 관리 (영구 저장 + 고급 알람 통합)
```python
class AdvancedPersistentDispenseManager:
    """영구 저장 + 고급 알람 기능이 통합된 배출 관리자"""
    
    def __init__(self):
        # 영구 저장 매니저 초기화
        self.persistent_manager = IntegratedPersistentManager()
        
        # 기존 매니저들 (영구 저장 기능 통합)
        self.medication_scheduler = MedicationScheduler()
        self.disk_manager = DiskManager()
        self.gate_controller = GateController()
        self.alarm_system = MultiSensoryAlarm()
        self.error_handler = DispenseErrorHandler()
        
        # 영구 저장 기능이 있는 매니저들로 교체
        self.logger = self.persistent_manager.dispense_logger
        self.tracker = self.persistent_manager.medication_tracker
        self.pattern_manager = self.persistent_manager.pattern_manager
        self.disk_position_manager = self.persistent_manager.disk_position_manager
        self.system_settings = self.persistent_manager.system_settings
        
        # 고급 배출 확인 시스템 통합
        self.integrated_confirmation = IntegratedDispenseConfirmation()
        self.ui_message_manager = DispenseUIMessageManager()
        
        # 시스템 초기화
        self.persistent_manager.initialize_from_storage()
    
    def start_dispense_process(self, dose_info):
        """전체 배출 프로세스 시작 (고급 알람 + 영구 저장 통합)"""
        try:
            print(f"배출 프로세스 시작: {dose_info}")
            
            # 고급 배출 확인 시스템으로 처리 (재알람 + 수동 배출 포함)
            success = self.integrated_confirmation.start_dispense_process_with_confirmation(dose_info)
            
            if success:
                print("배출 프로세스 완료")
            else:
                print("배출 프로세스 실패 - 수동 배출 대기 목록에 추가됨")
            
            return success
            
        except Exception as e:
            print(f"배출 프로세스 오류: {e}")
            self.error_handler.handle_dispense_error("DISPENSE_FAILURE", str(e))
            self.logger.log_dispense(dose_info, time.time(), False)
            return False
    
    def check_scheduled_dispenses(self):
        """예약된 배출 확인 (메인 루프에서 호출)"""
        self.medication_scheduler.check_dispense_time()
        
        # 수동 배출 요청 확인
        self.integrated_confirmation.check_manual_dispense_requests()
        
        # 대기 중인 배출 알림 표시
        pending_count = self.integrated_confirmation.get_pending_dispense_count()
        if pending_count > 0:
            self.ui_message_manager.show_pending_dispense_notification(pending_count)
    
    def setup_medication_pattern(self, pattern_name, dose_times):
        """복용 패턴 설정 (영구 저장 통합)"""
        self.pattern_manager.set_dose_pattern(pattern_name, dose_times)
        print(f"복용 패턴 설정 완료: {pattern_name}")
    
    def refill_medication(self, disk_id, compartment, count):
        """알약 리필 (영구 저장 통합)"""
        self.tracker.refill_medication(disk_id, compartment, count)
        print(f"디스크 {disk_id}, 칸 {compartment}: {count}개 리필 완료")
    
    def get_system_status(self):
        """전체 시스템 상태 조회"""
        base_status = self.persistent_manager.get_system_status()
        
        # 배출 관련 상태 추가
        base_status['dispense_status'] = {
            'pending_dispenses': self.integrated_confirmation.get_pending_dispense_count(),
            'failure_statistics': self.integrated_confirmation.get_failure_statistics(7),
            'current_alarm_active': self.integrated_confirmation.advanced_confirmation.waiting_for_confirmation
        }
        
        return base_status
    
    def perform_maintenance(self):
        """데이터 유지보수 작업"""
        self.persistent_manager.perform_maintenance()
        
        # 만료된 수동 배출 항목 정리
        self.integrated_confirmation.manual_manager.remove_expired_doses()
    
    def emergency_backup(self):
        """긴급 백업"""
        return self.persistent_manager.emergency_backup()
    
    def get_pending_dispense_list(self):
        """대기 중인 배출 목록 반환"""
        return self.integrated_confirmation.manual_manager.get_pending_list()
    
    def clear_pending_dispenses(self):
        """대기 중인 배출 목록 초기화"""
        self.integrated_confirmation.manual_manager.clear_pending_list()
        print("대기 중인 배출 목록 초기화 완료")
```

### 1.9 통합 메인 루프 (영구 저장 통합)

#### 1.9.1 메인 실행 로직
```python
def main_dispense_loop():
    """메인 배출 관리 루프 (고급 알람 + 영구 저장 통합)"""
    dispense_manager = AdvancedPersistentDispenseManager()
    
    # 메인 루프 카운터 (유지보수 작업용)
    main_loop_counter = 0
    maintenance_interval = 3600  # 1시간마다 유지보수
    
    while True:
        try:
            # 예약된 배출 확인
            dispense_manager.check_scheduled_dispenses()
            
            # 버튼 입력 처리
            button_interface.process_button_inputs()
            
            # UI 업데이트
            ui_manager.update_display()
            
            # 시스템 상태 확인
            system_monitor.check_system_health()
            
            # 주기적 유지보수 작업 (1시간마다)
            main_loop_counter += 1
            if main_loop_counter >= maintenance_interval:
                dispense_manager.perform_maintenance()
                main_loop_counter = 0
            
            time.sleep(0.1)  # 100ms 간격으로 실행
            
        except KeyboardInterrupt:
            print("배출 시스템 종료 - 긴급 백업 실행")
            dispense_manager.emergency_backup()
            break
        except Exception as e:
            print(f"메인 루프 오류: {e}")
            error_handler.handle_system_error(e)
            # 오류 발생 시에도 긴급 백업 시도
            try:
                dispense_manager.emergency_backup()
            except:
                pass
```

#### 1.9.2 시스템 시작 시 영구 저장 데이터 로드
```python
def initialize_system():
    """시스템 초기화 (영구 저장 데이터 로드)"""
    print("시스템 초기화 시작...")
    
    # 영구 저장 매니저 초기화
    persistent_manager = IntegratedPersistentManager()
    
    # 저장된 데이터로 시스템 초기화
    persistent_manager.initialize_from_storage()
    
    # 시스템 상태 출력
    system_status = persistent_manager.get_system_status()
    print("=== 시스템 상태 ===")
    print(f"복용 패턴: {system_status['pattern_info']['current_pattern']}")
    print(f"활성 디스크: {system_status['pattern_info']['active_disks']}")
    print(f"총 알약 수: {system_status['medication_status']['total_medications']}")
    print(f"복약 순응도: {system_status['dispense_stats']['compliance_rate']:.1f}%")
    
    print("시스템 초기화 완료")
    return persistent_manager
```

#### 1.9.3 전원 차단 감지 및 긴급 백업
```python
import machine

class PowerManager:
    """전원 관리 및 긴급 백업"""
    
    def __init__(self, persistent_manager):
        self.persistent_manager = persistent_manager
        self.low_power_threshold = 3.3  # V
        self.last_backup_time = 0
        self.backup_interval = 300  # 5분마다 백업
    
    def check_power_status(self):
        """전원 상태 확인"""
        # ADC를 통한 전원 전압 측정 (실제 하드웨어에 따라 구현)
        # voltage = adc.read_voltage()
        
        # 임시로 시간 기반 백업 (실제로는 전압 센서 사용)
        current_time = time.time()
        if current_time - self.last_backup_time >= self.backup_interval:
            self.perform_periodic_backup()
            self.last_backup_time = current_time
    
    def perform_periodic_backup(self):
        """주기적 백업"""
        try:
            print("주기적 백업 실행...")
            self.persistent_manager.auto_save_scheduler.check_and_save()
            print("주기적 백업 완료")
        except Exception as e:
            print(f"주기적 백업 실패: {e}")
    
    def emergency_shutdown(self):
        """긴급 종료 처리"""
        print("⚠️ 전원 부족 감지 - 긴급 종료 시작")
        
        # 모든 데이터 즉시 저장
        backup_file = self.persistent_manager.emergency_backup()
        
        # 시스템 종료
        print("시스템 종료")
        machine.deepsleep()  # 딥 슬립 모드
```

### 1.10 영구 저장 시스템 요약

#### 1.10.1 저장되는 데이터
- **복용 패턴**: 현재 패턴, 복용 시간, 디스크 사용 상태
- **배출 기록**: 모든 배출 활동의 상세 로그
- **복용량 추적**: 각 디스크/칸별 알약 개수
- **디스크 위치**: 각 모터의 현재 위치 및 스텝 수
- **시스템 설정**: 타임존, NTP 서버, 자동 저장 간격 등
- **사용자 설정**: 언어, 볼륨, 밝기, 자동 배출 여부 등
- **알람 설정**: 음성, LED, 부저 활성화 상태
- **Wi-Fi 설정**: SSID, 비밀번호, 자동 연결 설정

#### 1.10.2 자동 저장 기능
- **즉시 저장**: 중요한 데이터 변경 시 즉시 저장
- **주기적 저장**: 5분마다 자동 백업
- **긴급 백업**: 전원 차단 전 모든 데이터 저장
- **로그 정리**: 30일 이상 된 로그 자동 삭제
- **주간 백업**: 매주 설정 백업 파일 생성

#### 1.10.3 복구 기능
- **기본값 복원**: 파일 손상 시 기본 설정으로 복원
- **백업 복원**: 백업 파일에서 설정 복원
- **공장 초기화**: 모든 데이터 삭제 후 초기 상태로 복원

### 1.11 고급 배출 프로세스 요약

#### 1.11.1 배출 프로세스 플로우
```
1. 복용 시간 도달
   ↓
2. 알람 실행 (음성 + LED + 부저)
   ↓
3. 수동 배출 즉시 가능 (첫 번째 알람 후)
   ↓
4. A 버튼 대기 (5분간)
   ↓
5. A 버튼 미응답 시 재알람 (5분 간격으로 최대 5회)
   ↓
6. 5회 재알람 후 미응답 시 배출 실패 처리
   ↓
7. 메뉴에서 수동 배출 요청 시 A 버튼으로 배출 실행
   ↓
8. 배출 완료 후 약물 소진 확인
   ↓
9. 약물 소진 시 LED 깜빡임 + "충전하세요" 알림
```

#### 1.11.2 주요 특징
- **A 버튼 확인**: 사용자가 A 버튼을 눌러야 배출 진행
- **즉시 수동 배출**: 첫 번째 알람 후 즉시 메뉴에서 배출 가능
- **5분 간격 재알람**: 미응답 시 5분마다 최대 5회까지 재알람
- **배출 실패 처리**: 5회 재알람 후 미응답 시 배출 실패로 기록
- **약물 소진 알림**: 배출 후 약물 소진 시 LED 깜빡임 + "충전하세요" 메시지
- **영구 저장**: 모든 배출 기록과 실패 로그 영구 저장
- **복약 순응도 추적**: 성공/실패 비율로 순응도 계산

#### 1.11.3 사용자 경험
1. **정시 복용**: A 버튼으로 즉시 배출
2. **즉시 수동 배출**: 첫 번째 알람 후 바로 메뉴에서 A 버튼으로 배출 가능
3. **지연 복용**: 언제든지 메뉴에서 A 버튼으로 수동 배출 가능
4. **실패 방지**: 5분 간격 5회 재알람으로 놓치기 방지 (총 25분간)
5. **최대 유연성**: 첫 번째 알람부터 수동 배출 가능으로 사용자 편의성 극대화
6. **일관된 조작**: 모든 배출은 A 버튼으로 통일된 조작
7. **약물 소진 알림**: 배출 후 약물이 떨어지면 LED 깜빡임과 "충전하세요" 메시지로 즉시 알림
8. **추적**: 모든 복용 기록 자동 관리

이 설계안은 REQUIREMENTS.md의 3.2.4 약 배출 로직을 완전히 구현하면서, 실제 하드웨어 구성(모터 1,2,3,4, 리미트 스위치, LED, 부저, 스피커)과 현재 구현된 시스템 구조를 고려하여 작성되었습니다. 특히 영구 저장 기능과 고급 알람 시스템을 통해 전원 차단이나 시스템 재시작 후에도 모든 설정과 데이터가 보존되어 연속적인 서비스가 가능하며, 사용자가 놓친 복용도 나중에 처리할 수 있는 완전한 복약 관리 시스템을 제공합니다.
