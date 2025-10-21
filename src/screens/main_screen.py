"""
메인 화면
오늘의 알약 일정을 표시하는 대시보드 화면
Modern UI 스타일 적용 + 자동 배출 기능
"""

import sys
sys.path.append("/")

import time
import lvgl as lv
from machine import RTC

class MainScreen:
    """메인 화면 클래스 - Modern UI 스타일 + 자동 배출 기능"""
    
    def __init__(self, screen_manager):
        """메인 화면 초기화 - 메모리 최적화"""
        self.screen_manager = screen_manager
        self.screen_name = 'main'
        self.screen_obj = None
        self.current_dose_index = 0
        self.dose_schedule = []  # 복용 일정
        self.last_update_time = 0
        
        # 실시간 정보 (최소한만 초기화)
        self.current_time = "00:00"  # 기본값으로 설정
        self.next_dose_time = ""
        self.time_until_next = ""
        
        # 필박스 상태 (최소한만 초기화)
        self.wifi_connected = True  # WiFi 연결 상태 (시뮬레이션)
        
        # UI 업데이트 타이머
        self.ui_update_counter = 0
        
        # 지연 초기화를 위한 플래그들 (모든 무거운 객체들을 지연 로딩)
        self._ui_style = None
        self._data_manager = None
        self._medication_tracker = None
        self._alarm_system = None
        self._wifi_manager = None
        self._motor_system = None
        self._rtc = None  # RTC도 지연 로딩
        self._disk_states = None  # 디스크 상태도 지연 로딩
        self._wifi_status = None  # WiFi 상태도 지연 로딩
        self._current_date = None  # 현재 날짜도 지연 로딩
        
        # 시간 모니터링 (자동 배출용) - 최소한만 초기화
        self.last_check_time = ""
        self.auto_dispense_enabled = True
        self.last_dispense_time = {}
        
        # NTP 동기화 관련 속성
        self._ntp_sync_enabled = False
        self._last_ntp_sync_time = 0
        
        # 약물 상태 모니터링용 - 지연 로딩
        self._last_medication_check = None
        self._medication_alerts = None
        
        # 알람 상태 모니터링 - 지연 로딩
        self._last_alarm_check = None
        
        # 시간 초기화를 지연 초기화 플래그들 설정 후 실행
        self._initialize_time()
        
        # print("[DEBUG] 메인 화면 초기화 - 메모리 최적화 지연 로딩 방식")
        
        # 샘플 데이터 초기화
        self._init_sample_data()
    
    @property
    def rtc(self):
        """RTC 지연 로딩"""
        if self._rtc is None:
            self._rtc = RTC()
        return self._rtc
    
    @property
    def disk_states(self):
        """디스크 상태 지연 로딩"""
        if self._disk_states is None:
            self._disk_states = {"disk_1": 0, "disk_2": 0, "disk_3": 0}
        return self._disk_states
    
    @property
    def wifi_status(self):
        """WiFi 상태 지연 로딩"""
        if self._wifi_status is None:
            self._wifi_status = {"connected": False, "ssid": None}
        return self._wifi_status
    
    @property
    def current_date(self):
        """현재 날짜 지연 로딩"""
        if self._current_date is None:
            self._current_date = "2025-10-17"
        return self._current_date
    
    @property
    def last_medication_check(self):
        """약물 체크 시간 지연 로딩"""
        if self._last_medication_check is None:
            self._last_medication_check = ""
        return self._last_medication_check
    
    @property
    def medication_alerts(self):
        """약물 알림 지연 로딩"""
        if self._medication_alerts is None:
            self._medication_alerts = []
        return self._medication_alerts
    
    @property
    def last_alarm_check(self):
        """알람 체크 시간 지연 로딩"""
        if self._last_alarm_check is None:
            self._last_alarm_check = ""
        return self._last_alarm_check
    
    def _initialize_time(self):
        """시간 초기화 (가장 먼저 실행) - WiFi 자동 연결 및 NTP 설정 포함"""
        try:
            # print("[DEBUG] 시간 초기화 시작 - WiFi 자동 연결 및 NTP 설정")
            
            # WiFi 매니저 지연 로딩
            wifi_manager = self.wifi_manager
            
            # 1단계: 저장된 WiFi 설정으로 자동 연결 시도 (재시도 포함)
            try:
                if wifi_manager:
                    # print("[INFO] 저장된 WiFi 설정으로 자동 연결 시도...")
                    success = self._try_wifi_connection_with_retry(wifi_manager)
                    if success:
                        # print(f"[OK] WiFi 자동 연결 성공: {wifi_manager.connected_ssid}")
                        
                        # 2단계: NTP 시간 동기화 시도
                        # print("[INFO] NTP 시간 동기화 시도...")
                        ntp_success = wifi_manager.sync_ntp_time()
                        if ntp_success:
                            # print("[OK] NTP 시간 동기화 성공")
                            kst_time = wifi_manager.get_kst_time()
                            hour = kst_time[3]
                            minute = kst_time[4]
                            self.current_time = f"{hour:02d}:{minute:02d}"
                            self._wifi_status = {"connected": True, "ssid": wifi_manager.connected_ssid}
                            self.wifi_connected = True
                            self._current_date = f"{kst_time[0]}-{kst_time[1]:02d}-{kst_time[2]:02d}"
                            # print(f"[OK] NTP 시간으로 초기화: {self.current_time}")
                            return
                        else:
                            # print("[WARN] NTP 시간 동기화 실패")
                            pass
                    else:
                        # print("[WARN] WiFi 자동 연결 최종 실패 (모든 재시도 완료)")
                        pass
                else:
                    # print("[WARN] WiFi 매니저 사용 불가")
                    pass
            except Exception as e:
                # print(f"[WARN] WiFi 자동 연결 중 오류: {e}")
                pass
            
            # 3단계: WiFi 연결 실패 시 RTC 시간 사용
            # print("[INFO] WiFi 연결 실패 - RTC 시간 사용")
            current = self.rtc.datetime()
            hour = current[4]
            minute = current[5]
            self.current_time = f"{hour:02d}:{minute:02d}"
            self._wifi_status = {"connected": False, "ssid": None}
            self.wifi_connected = False
            self._current_date = f"{current[0]}-{current[1]:02d}-{current[2]:02d}"
            # print(f"[OK] RTC 시간으로 초기화: {self.current_time}")
        except Exception as e:
            # print(f"[ERROR] 시간 초기화 실패: {e}")
            self.current_time = "00:00"
            self._wifi_status = {"connected": False, "ssid": None}
            self.wifi_connected = False  # WiFi 연결 상태 설정
            self._current_date = "2025-10-17"
        
        # 복용 일정 데이터 초기화
        self._init_sample_data()
        
        # Modern 화면 생성
        self._create_modern_screen()
        
        # 시간 초기화 (WiFi 자동 연결 및 NTP 설정)
        # print("[INFO] MainScreen 시간 초기화 시작...")
        self._initialize_time()
        # print("[INFO] MainScreen 시간 초기화 완료")
        
        # print(f"[OK] {self.screen_name} 화면 초기화 완료")
    
    # 지연 로딩 메서드들
    @property
    def ui_style(self):
        """UI 스타일 지연 로딩"""
        if self._ui_style is None:
            from ui_style import UIStyle
            self._ui_style = UIStyle()
            # print("[DEBUG] UI 스타일 지연 로딩 완료")
        return self._ui_style
    
    @property
    def data_manager(self):
        """데이터 관리자 지연 로딩"""
        if self._data_manager is None:
            from data_manager import DataManager
            self._data_manager = DataManager()
            # print("[DEBUG] 데이터 관리자 지연 로딩 완료")
        return self._data_manager
    
    @property
    def medication_tracker(self):
        """약물 추적 시스템 지연 로딩"""
        if self._medication_tracker is None:
            from medication_tracker import MedicationTracker
            self._medication_tracker = MedicationTracker(self.data_manager)
            # print("[DEBUG] 약물 추적 시스템 지연 로딩 완료")
        return self._medication_tracker
    
    @property
    def alarm_system(self):
        """알람 시스템 지연 로딩"""
        if self._alarm_system is None:
            import gc
            gc.collect()
            
            try:
                from alarm_system import AlarmSystem
                self._alarm_system = AlarmSystem(self.data_manager, self)  # 메인 화면 참조 전달
                # print("[DEBUG] 알람 시스템 지연 로딩 완료")
            except Exception as e:
                # print(f"[ERROR] 알람 시스템 지연 로딩 실패: {e}")
                self._alarm_system = None
        return self._alarm_system
    
    @property
    def wifi_manager(self):
        """WiFi 관리자 지연 로딩"""
        if self._wifi_manager is None:
            from wifi_manager import get_wifi_manager
            self._wifi_manager = get_wifi_manager()
            # print("[DEBUG] WiFi 관리자 지연 로딩 완료")
        return self._wifi_manager
    
    @property
    def motor_system(self):
        """모터 시스템 지연 로딩"""
        if self._motor_system is None:
            from motor_control import PillBoxMotorSystem
            self._motor_system = PillBoxMotorSystem()
            # print("[DEBUG] 모터 시스템 지연 로딩 완료")
        return self._motor_system
    
    
    def _init_sample_data(self):
        """샘플 데이터 초기화 - dose_time_screen에서 설정한 시간 가져오기"""
        # NTP 시간을 활용한 현재 날짜 가져오기 (RTC 백업 포함)
        try:
            # WiFi 매니저에서 한국 시간 가져오기 (지연 로딩)
            wifi_manager = self.wifi_manager
            if wifi_manager and wifi_manager.is_connected and wifi_manager.time_synced:
                kst_time = wifi_manager.get_kst_time()
                year, month, day, hour, minute, second = kst_time[:6]
                # print(f"  📅 NTP 시간으로 날짜 설정: {year}년 {month}월 {day}일 {hour}:{minute:02d}:{second:02d}")
                
                # NTP 시간을 RTC에 백업 저장 (외부 배터리 활용)
                from machine import RTC
                rtc = RTC()
                # RTC는 (year, month, day, weekday, hour, minute, second, microsecond) 형식
                weekday = (day - 1) % 7  # 간단한 요일 계산 (0=월요일)
                rtc.datetime((year, month, day, weekday, hour, minute, second, 0))
                # print("  [SAVE] NTP 시간을 RTC에 백업 저장 완료")
                
            else:
                # NTP가 없으면 RTC 백업 시간 사용 (외부 배터리로 유지됨)
                from machine import RTC
                rtc = RTC()
                year, month, day = rtc.datetime()[:3]
                # print(f"  📅 RTC 백업 시간으로 날짜 설정: {year}년 {month}월 {day}일 (외부 배터리)")
                
        except Exception as e:
            # 오류 시 기본값 사용
            month, day = 12, 25
            # print(f"  [WARN] 날짜 설정 오류, 기본값 사용: {month}월 {day}일 ({e})")
        
        # 자동 할당된 디스크 정보에서 시간 가져오기 (우선)
        try:
            from data_manager import DataManager
            data_manager = DataManager()
            auto_assigned_disks = data_manager.get_auto_assigned_disks()
            
            if auto_assigned_disks:
                # 자동 할당된 디스크만 표시
                self.dose_schedule = []
                for disk_info in auto_assigned_disks:
                    self.dose_schedule.append({
                        "time": disk_info['time'],
                        "status": "pending",
                        "meal_name": disk_info['meal_name'],
                        "disk_number": disk_info['disk_number']
                    })
                # print(f"  [INFO] 자동 할당된 디스크에서 시간 가져옴: {len(auto_assigned_disks)}개")
                for disk_info in auto_assigned_disks:
                    # print(f"    - {disk_info['meal_name']}: {disk_info['time']} (디스크 {disk_info['disk_number']})")
                    pass
            else:
                # 자동 할당 정보가 없으면 DataManager에서 설정한 시간 가져오기
                pass
                from data_manager import DataManager
                data_manager = DataManager()
                dose_times = data_manager.get_dose_times()
                
                if dose_times:
                    self.dose_schedule = []
                    for dose_time in dose_times:
                        # dose_time이 딕셔너리인 경우 'time' 키 사용, 문자열인 경우 그대로 사용
                        if isinstance(dose_time, dict):
                            time_str = dose_time.get('time', '08:00')
                            meal_name = dose_time.get('meal_name', '알 수 없음')
                            selected_disks = dose_time.get('selected_disks', [])
                        else:
                            time_str = dose_time
                            meal_name = '알 수 없음'
                            selected_disks = []
                        
                        self.dose_schedule.append({
                            "time": time_str,
                            "status": "pending",
                            "meal_name": meal_name,
                            "selected_disks": selected_disks
                        })
                    # print(f"  [INFO] DataManager에서 설정한 시간 가져옴: {len(dose_times)}개")
                    for dose_time in dose_times:
                        if isinstance(dose_time, dict):
                            # print(f"    - {dose_time.get('meal_name', '알 수 없음')}: {dose_time.get('time', '알 수 없음')}")
                            pass
                else:
                    # 설정된 시간이 없으면 기본값 사용
                    self.dose_schedule = [
                        {"time": "08:00", "status": "pending"},
                        {"time": "12:00", "status": "pending"},
                        {"time": "18:00", "status": "pending"}
                    ]
                    # print("  [INFO] 설정된 시간 없음, 기본값 사용")
        except Exception as e:
            # 오류 시 기본값 사용
            self.dose_schedule = [
                {"time": "08:00", "status": "pending"},
                {"time": "12:00", "status": "pending"},
                {"time": "18:00", "status": "pending"}
            ]
            # print(f"  [WARN] 복용 시간 가져오기 실패, 기본값 사용: {e}")
        
        self._current_date = f"{year}-{month:02d}-{day:02d}"
    
    def _create_modern_screen(self):
        """Modern 스타일 화면 생성"""
        # print(f"  [INFO] {self.screen_name} Modern 화면 생성 시작...")
        
        try:
            # 메모리 정리
            import gc
            gc.collect()
            # print("  [OK] 메모리 정리 완료")
            
            # 화면 생성
            # print("  [INFO] 화면 객체 생성...")
            self.screen_obj = lv.obj()
            # print(f"  [INFO] 화면 객체 생성됨: {self.screen_obj}")
            
            # 간단한 배경 설정 (스타일 시스템 사용 안함 - 메모리 절약)
            self.screen_obj.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
            self.screen_obj.set_style_bg_opa(255, 0)
            
            # 스크롤바 완전 비활성화
            self.screen_obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.screen_obj.set_scroll_dir(lv.DIR.NONE)
            
            # print("  [OK] 화면 배경 설정 완료")
            
            # 화면 크기 설정
            self.screen_obj.set_size(160, 128)
            # print("  [INFO] 화면 크기: 160x128")
            
            # 메인 컨테이너 생성
            # print("  [INFO] 메인 컨테이너 생성 시도...")
            self.main_container = lv.obj(self.screen_obj)
            self.main_container.set_size(160, 128)
            self.main_container.align(lv.ALIGN.CENTER, 0, 0)
            self.main_container.set_style_bg_opa(0, 0)  # 투명 배경
            self.main_container.set_style_border_width(0, 0)  # 테두리 없음
            
            # 스크롤바 완전 비활성화
            self.main_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.main_container.set_scroll_dir(lv.DIR.NONE)
            
            # print("  [INFO] 메인 컨테이너 생성 완료")
            
            # 제목 영역 생성
            # print("  [INFO] 제목 영역 생성 시도...")
            self._create_title_area()
            # print("  [INFO] 제목 영역 생성 완료")
            
            # 복용 일정 영역 생성
            # print("  [INFO] 복용 일정 영역 생성 시도...")
            self._create_schedule_area()
            # print("  [INFO] 복용 일정 영역 생성 완료")
            
            # 하단 버튼 힌트 영역 생성
            # print("  [INFO] 버튼 힌트 영역 생성 시도...")
            self._create_button_hints_area()
            # print("  [INFO] 버튼 힌트 영역 생성 완료")
            
            # print("  [OK] Modern 화면 생성 완료")
            
        except Exception as e:
            # print(f"  [ERROR] Modern 화면 생성 중 오류 발생: {e}")
            # 메모리 부족 시 더 간단한 UI 생성
            try:
                self._create_minimal_ui()
            except Exception as e2:
                # print(f"  [ERROR] 최소 UI 생성도 실패: {e2}")
                pass
    def _create_minimal_ui(self):
        """최소한의 UI 생성 (메모리 절약)"""
        try:
            # print("  [INFO] 최소 UI 생성 시작...")
            
            # 제목 라벨만 생성
            title_label = lv.label(self.screen_obj)
            title_label.set_text("복용 알림")
            title_label.align(lv.ALIGN.TOP_MID, 0, 10)
            title_label.set_style_text_color(lv.color_hex(0x333333), 0)
            
            # 시간 표시 라벨
            time_label = lv.label(self.screen_obj)
            time_label.set_text("11:35")
            time_label.align(lv.ALIGN.CENTER, 0, -20)
            time_label.set_style_text_color(lv.color_hex(0x666666), 0)
            
            # 상태 라벨
            status_label = lv.label(self.screen_obj)
            status_label.set_text("정상")
            status_label.align(lv.ALIGN.BOTTOM_MID, 0, -10)
            status_label.set_style_text_color(lv.color_hex(0x4CAF50), 0)
            
            # print("  [OK] 최소 UI 생성 완료")
            
        except Exception as e:
            # print(f"  [ERROR] 최소 UI 생성 실패: {e}")
            raise e
    
    def _create_title_area(self):
        """제목 영역 생성"""
        try:
            # 제목 영역 완전 제거됨
            
            # 현재 시간과 상태 표시기를 독립적으로 생성
            self._create_current_time_and_status()
            
        except Exception as e:
            # print(f"  [ERROR] 제목 영역 생성 실패: {e}")
            pass

    def _create_current_time_and_status(self):
        """현재 시간과 상태 표시기를 독립적으로 생성"""
        try:
            # 현재 시간 표시 (좌측 상단)
            self.current_time_label = lv.label(self.main_container)
            self.current_time_label.set_text(self.current_time)
            self.current_time_label.align(lv.ALIGN.TOP_LEFT, 5, -10)
            self.current_time_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
            self.current_time_label.set_style_text_color(lv.color_hex(0x007AFF), 0)
            
            # 알약 개수는 복용 일정 영역에서 표시
        
            # WiFi 심볼을 상단 중앙에 독립적으로 배치
            self._create_wifi_indicator()
        
            # 배터리 상태 표시기 삭제됨
        
        except Exception as e:
            # print(f"  [ERROR] 현재 시간과 상태 표시기 생성 실패: {e}")
            pass
    def _create_wifi_indicator(self):
        """WiFi 심볼을 상단 중앙에 독립적으로 생성"""
        try:
            # WiFi 연결 상태 확인 (속성이 없으면 기본값 사용)
            wifi_connected = getattr(self, 'wifi_connected', False)
            
            # WiFi 표시 (화면 상단 중앙) - 완전히 독립적으로 배치
            wifi_icon = lv.SYMBOL.WIFI if wifi_connected else lv.SYMBOL.CLOSE
            self.wifi_label = lv.label(self.main_container)
            self.wifi_label.set_text(wifi_icon)
            self.wifi_label.align(lv.ALIGN.TOP_MID, 0, -10)  # 상단 중앙 위치
            self.wifi_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            self.wifi_label.set_style_text_color(lv.color_hex(0x007AFF) if wifi_connected else lv.color_hex(0xFF3B30), 0)
            # print("  [OK] WiFi 심볼을 상단 중앙에 배치 완료")
        except Exception as e:
            # print(f"  [ERROR] WiFi 심볼 생성 실패: {e}")
            pass

    def _create_schedule_area(self):
        """복용 일정 영역 생성"""
        try:
            # 일정 컨테이너
            self.schedule_container = lv.obj(self.main_container)
            self.schedule_container.set_size(160, 90)
            self.schedule_container.align(lv.ALIGN.TOP_MID, 0, 1)  # 8픽셀 위로 이동 (9 → 1)
            self.schedule_container.set_style_bg_opa(0, 0)
            self.schedule_container.set_style_border_width(0, 0)
            
            # 스크롤바 완전 비활성화
            self.schedule_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.schedule_container.set_scroll_dir(lv.DIR.NONE)
            
            # 날짜 표시
            date_label = lv.label(self.schedule_container)
            date_label.set_text(self.current_date)
            date_label.align(lv.ALIGN.TOP_MID, 0, 5)
            date_label.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
            
            # 복용 일정 표시
            self.schedule_labels = []
            self.pill_count_labels = []  # 모든 일정의 알약 개수 라벨 저장
            
            # dose_schedule이 비어있으면 기본값 사용
            if not hasattr(self, 'dose_schedule') or not self.dose_schedule:
                # print("  [WARN] dose_schedule이 비어있음, 기본값 사용")
                self.dose_schedule = [{"time": "08:00", "status": "pending"}]
            
            for i, schedule in enumerate(self.dose_schedule):
                # 상태에 따른 아이콘 (LVGL 심볼 사용)
                if schedule["status"] == "completed":
                    status_icon = lv.SYMBOL.OK
                elif schedule["status"] == "failed":
                    status_icon = lv.SYMBOL.CLOSE
                else:  # pending
                    status_icon = lv.SYMBOL.BELL
                
                # 일정 아이템 컨테이너
                schedule_item = lv.obj(self.schedule_container)
                schedule_item.set_size(145, 22)
                schedule_item.align(lv.ALIGN.TOP_MID, -8, 20 + i * 18)
                schedule_item.set_style_bg_opa(0, 0)
                schedule_item.set_style_border_width(0, 0)
                
                # 선택 표시 완전 비활성화 (네모박스 제거)
                schedule_item.set_style_bg_opa(0, lv.STATE.PRESSED)
                schedule_item.set_style_border_width(0, lv.STATE.PRESSED)
                schedule_item.set_style_bg_opa(0, lv.STATE.FOCUSED)
                schedule_item.set_style_border_width(0, lv.STATE.FOCUSED)
                schedule_item.set_style_bg_opa(0, lv.STATE.FOCUS_KEY)
                schedule_item.set_style_border_width(0, lv.STATE.FOCUS_KEY)
                
                # 스크롤바 완전 비활성화
                schedule_item.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
                schedule_item.set_scroll_dir(lv.DIR.NONE)
                
                # 시간과 아이콘을 하나의 라벨로 합쳐서 중앙 정렬
                combined_text = f"{schedule['time']} {status_icon}"
                combined_label = lv.label(schedule_item)
                combined_label.set_text(combined_text)
                combined_label.align(lv.ALIGN.CENTER, 0, 0)
                combined_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
                
                # 알약 개수 표시 (모든 일정에 표시)
                pill_count_label = lv.label(schedule_item)
                
                # 실제 수량으로 초기화
                try:
                    # 복용 횟수 확인
                    dose_count = len(self.dose_schedule)
                    
                    if dose_count == 1:
                        # 1일 1회: 선택된 디스크들의 총합 표시
                        selected_disks = self._get_selected_disks_from_dose_time()
                        
                        total_count = 0
                        total_capacity = 0
                        
                        for disk_num in selected_disks:
                            data_manager = self.data_manager
                            if data_manager:
                                current_count = data_manager.get_disk_count(disk_num)
                            else:
                                current_count = 15  # 기본값
                            total_count += current_count
                            total_capacity += 15
                        
                        count_text = f"{total_count}/{total_capacity}"
                        # print(f"  [DEBUG] 1일 1회 초기 선택된 디스크 총합 표시: {total_count}/{total_capacity} (디스크: {selected_disks})")
                    else:
                        # 1일 2회 이상: 기존 방식 (디스크별 개별 표시)
                        if i < len(self.dose_schedule):
                            current_dose = self.dose_schedule[i]
                            selected_disks = current_dose.get('selected_disks', [i + 1])
                            if selected_disks:
                                disk_num = selected_disks[0]
                            else:
                                disk_num = i + 1
                            
                            # DataManager에서 실제 수량 가져오기
                            data_manager = self.data_manager
                            if data_manager:
                                current_count = data_manager.get_disk_count(disk_num)
                            else:
                                current_count = 15  # 기본값
                            
                            max_capacity = 15
                            count_text = f"{current_count}/{max_capacity}"
                        else:
                            count_text = "15/15"  # 기본값
                except:
                    count_text = "15/15"  # 오류 시 기본값
                
                pill_count_label.set_text(count_text)
                pill_count_label.align(lv.ALIGN.CENTER, 50, 0)  # 복용 일정 오른쪽
                pill_count_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
                pill_count_label.set_style_text_color(lv.color_hex(0x000000), 0)  # 검정색
                
                # 첫 번째 일정의 알약 개수 라벨을 메인 참조로 저장 (하위 호환성)
                if i == 0:
                    self.pill_count_label = pill_count_label
                
                # 알약 개수 라벨을 리스트에 추가
                self.pill_count_labels.append(pill_count_label)
                
                combined_label.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
                
                self.schedule_labels.append(combined_label)
            
        except Exception as e:
            # print(f"  [ERROR] 복용 일정 영역 생성 실패: {e}")
            pass
    def _create_button_hints_area(self):
        """하단 버튼 힌트 영역 생성 - Modern 스타일"""
        # 버튼 힌트 컨테이너
        self.hints_container = lv.obj(self.main_container)
        self.hints_container.set_size(140, 18)
        self.hints_container.align(lv.ALIGN.BOTTOM_MID, 0, 12)
        # 투명 배경 (Modern 스타일)
        self.hints_container.set_style_bg_opa(0, 0)
        self.hints_container.set_style_border_width(0, 0)
        self.hints_container.set_style_pad_all(0, 0)
        
        # 버튼 힌트 텍스트 (일정 이동 + 배출 + 고급 설정) - 기본 폰트 사용
        self.hints_text = lv.label(self.hints_container)
        self.hints_text.set_text(f"A:{lv.SYMBOL.DOWNLOAD} B:{lv.SYMBOL.UP} C:{lv.SYMBOL.DOWN} D:{lv.SYMBOL.SETTINGS}")
        self.hints_text.align(lv.ALIGN.CENTER, 0, 0)  # 컨테이너 중앙에 배치
        self.hints_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.hints_text.set_style_text_color(lv.color_hex(0x8E8E93), 0)  # 모던 라이트 그레이
        # 기본 폰트는 자동으로 사용됨 (한글 폰트 적용 안함)

    def _create_basic_screen(self):
        """기본 화면 생성 (오류 시 대안)"""
        # print(f"  [INFO] {self.screen_name} 기본 화면 생성 시작...")
        
        try:
            # 기본 화면 객체 생성
            self.screen_obj = lv.obj()
            self.screen_obj.set_size(160, 128)
            
            # 기본 라벨 생성
            self.title_label = lv.label(self.screen_obj)
            self.title_label.set_text("메인 화면")
            self.title_label.align(lv.ALIGN.CENTER, 0, 0)
            
            # print("  [OK] 기본 화면 생성 완료")
            
        except Exception as e:
            # print(f"  [ERROR] 기본 화면 생성 실패: {e}")
            # 최소한의 화면이라도 생성
            self.screen_obj = lv.obj()
            self.screen_obj.set_size(160, 128)


    def get_memory_info(self):
        """메모리 사용 정보 반환"""
        try:
            if hasattr(self.screen_manager, 'get_memory_info'):
                return self.screen_manager.get_memory_info()
            else:
                return {"error": "ScreenManager에 get_memory_info 메서드가 없음"}
        except Exception as e:
            return {"error": f"메모리 정보 조회 실패: {e}"}
    
    def _update_schedule_display(self):
        """복용 일정 표시 업데이트"""
        try:
            if hasattr(self, 'schedule_label') and self.dose_schedule:
                current_schedule = self.dose_schedule[self.current_dose_index]
                status_icon = "⏰" if current_schedule["status"] == "pending" else "[OK]"
                schedule_text = f"{status_icon} {current_schedule['time']}"
                self.schedule_label.set_text(schedule_text)
        except Exception as e:
            # print(f"  [ERROR] 일정 표시 업데이트 실패: {e}")
            pass
    def _update_status(self, status):
        """상태 업데이트"""
        try:
            self.status_text = status
            if hasattr(self, 'status_label'):
                self.status_label.set_text(status)
        except Exception as e:
            # print(f"  [ERROR] 상태 업데이트 실패: {e}")
            pass
    
    def _init_motor_system(self):
        """모터 시스템 지연 초기화"""
        if self.motor_system is None:
            try:
                # 메모리 정리
                import gc
                gc.collect()
                # print("  🧹 모터 시스템 초기화 전 메모리 정리 완료")
                
                # 실제 모터 시스템 초기화
                from motor_control import PillBoxMotorSystem
                self.motor_system = PillBoxMotorSystem()
                # print("  [OK] 실제 모터 시스템 초기화 완료")
                
            except Exception as e:
                # print(f"  [WARN] 실제 모터 시스템 초기화 실패, 재시도: {e}")
                try:
                    # 재시도
                    import gc
                    gc.collect()
                    from motor_control import PillBoxMotorSystem
                    self.motor_system = PillBoxMotorSystem()
                    # print("  [OK] 실제 모터 시스템 재시도 초기화 완료")
                except Exception as e2:
                    # print(f"  [ERROR] 실제 모터 시스템 초기화 최종 실패: {e2}")
                    # 모의 시스템 사용
                    self.motor_system = MockMotorSystem()
                    # print("  [WARN] 모의 모터 시스템 사용")
        
        return self.motor_system
    
    def show(self):
        """화면 표시 - 메모리 최적화"""
        from memory_monitor import log_memory, cleanup_memory
        
        # print(f"[INFO] {self.screen_name} UI 통합 모드 표시")
        log_memory("MainScreen show() 시작")
        
        if hasattr(self, 'screen_obj') and self.screen_obj:
            lv.screen_load(self.screen_obj)
            # print(f"[OK] {self.screen_name} 화면 로드 완료")
            
            # 화면 강제 업데이트
            for i in range(3):
                lv.timer_handler()
                time.sleep(0.01)
            # print(f"[OK] {self.screen_name} 화면 업데이트 완료")
            
            # 자동 배출 모니터링 시작 (메모리 사용량 고려)
            self._start_auto_dispense_monitoring()
            
            # 주기적 NTP 시간 동기화 시작
            self._start_periodic_ntp_sync()
            
            # 자동 배출 모니터링 후 메모리 정리
            import gc
            gc.collect()
            # print("[INFO] MainScreen 자동 배출 모니터링 후 메모리 정리 완료")
            
            # ST7735 디스플레이 PWM 정리 (메모리 누수 방지)
            self._cleanup_display_pwm()
            
            # 화면 표시 완료 후 메모리 상태 모니터링
            memory_info = log_memory("MainScreen show() 완료")
            
            # 메모리 사용률이 높으면 추가 정리
            if memory_info and memory_info['usage_percent'] > 85:
                # print("[WARN] MainScreen 메모리 사용률이 높음, 추가 정리 수행")
                cleanup_memory("MainScreen show() 후 정리")
                log_memory("MainScreen show() 후 정리 완료")
        else:
            # print(f"[WARN] {self.screen_name} 화면 객체가 없음 - 화면 생성 시도")
            # 화면이 없으면 생성
            self._create_modern_screen()
            if hasattr(self, 'screen_obj') and self.screen_obj:
                lv.screen_load(self.screen_obj)
                # print(f"[OK] {self.screen_name} 화면 재생성 및 로드 완료")
                
                # 화면 강제 업데이트
                for i in range(3):
                    lv.timer_handler()
                    time.sleep(0.01)
                # print(f"[OK] {self.screen_name} 화면 업데이트 완료")
                
                # 자동 배출 모니터링 시작
                self._start_auto_dispense_monitoring()
                
                # 주기적 NTP 시간 동기화 시작
                self._start_periodic_ntp_sync()
                
                # 메모리 정리
                import gc
                gc.collect()
                # print("[INFO] MainScreen 자동 배출 모니터링 후 메모리 정리 완료")
                
                # ST7735 디스플레이 PWM 정리
                self._cleanup_display_pwm()
                
                # print(f"[OK] {self.screen_name} 화면 실행됨")
            else:
                # print(f"[ERROR] {self.screen_name} 화면 생성 실패")
                pass
        
        # 캐싱된 화면은 메모리에서 제거하지 않음
        pass
    
    def _cleanup_references(self):
        """참조 정리 - 메모리 최적화"""
        try:
            # print("[INFO] MainScreen 참조 정리 시작")
            
            # 지연 로딩된 객체들 정리
            self._ui_style = None
            self._data_manager = None
            self._medication_tracker = None
            self._alarm_system = None
            self._wifi_manager = None
            self._motor_system = None
            self._rtc = None
            self._disk_states = None
            self._wifi_status = None
            self._current_date = None
            self._last_medication_check = None
            self._medication_alerts = None
            self._last_alarm_check = None
            
            # print("[OK] MainScreen 참조 정리 완료")
            
        except Exception as e:
            # print(f"[ERROR] MainScreen 참조 정리 실패: {e}")
            pass
        
    def _force_garbage_collection(self):
        """강제 가비지 컬렉션 - 메모리 최적화"""
        try:
            from memory_utils import standard_garbage_collection
            
            # print("[INFO] MainScreen 강제 가비지 컬렉션 시작")
            
            # 참조 정리 먼저 수행
            self._cleanup_references()
            
            # 표준 가비지 컬렉션 수행
            standard_garbage_collection("MainScreen")
            
            # print("[OK] MainScreen 강제 가비지 컬렉션 완료")
            
        except Exception as e:
            # print(f"[ERROR] MainScreen 가비지 컬렉션 실패: {e}")
            pass
        
    def _cleanup_display_pwm(self):
        """ST7735 디스플레이 PWM 정리 - 메모리 누수 방지"""
        try:
            # print("[INFO] ST7735 디스플레이 PWM 정리 시작")
            
            # 디스플레이 객체가 있으면 PWM 정리
            if hasattr(self, 'screen_manager') and self.screen_manager:
                if hasattr(self.screen_manager, 'app') and self.screen_manager.app:
                    app = self.screen_manager.app
                    if hasattr(app, 'display') and app.display:
                        try:
                            # ST7735 cleanup 메서드 호출
                            if hasattr(app.display, 'cleanup'):
                                app.display.cleanup()
                                # print("[OK] ST7735 디스플레이 PWM 정리 완료")
                            else:
                                # cleanup 메서드가 없으면 off() 메서드 호출
                                app.display.off()
                                # print("[OK] ST7735 디스플레이 백라이트 끄기 완료")
                        except Exception as e:
                            # print(f"[WARN] ST7735 디스플레이 정리 실패: {e}")
                            pass
            # print("[OK] ST7735 디스플레이 PWM 정리 완료")
            
        except Exception as e:
            # print(f"[ERROR] ST7735 디스플레이 PWM 정리 실패: {e}")
            pass
        
    def _monitor_memory(self, label):
        """메모리 사용량 모니터링 (MicroPython만)"""
        try:
            import micropython
            
            # MicroPython 메모리 정보만 확인
            mem_info = micropython.mem_info()
            # print(f"[{label}] MicroPython 메모리:")
            # print(f"  {mem_info}")
                    
        except Exception as e:
            # print(f"[WARN] 메모리 모니터 실패: {e}")
            pass
    
        
    def update(self):
        """화면 업데이트 (ScreenManager에서 주기적으로 호출) - 메모리 최적화"""
        try:
            # 업데이트 빈도 제한 (1초마다)
            current_time_ms = time.ticks_ms()
            if hasattr(self, 'last_update_time') and time.ticks_diff(current_time_ms, self.last_update_time) < 1000:
                return
            
            self.last_update_time = current_time_ms
            
            # 현재 시간 업데이트 (1초마다)
            self._update_current_time()
            self._update_time_display()
            
            # 알약 개수 업데이트 (5초마다)
            if not hasattr(self, 'last_pill_count_update') or time.ticks_diff(current_time_ms, self.last_pill_count_update) >= 5000:
                self._update_pill_count_display()
                self.last_pill_count_update = current_time_ms
            
            # 자동 배출 시간 확인 (1초마다)
            self._check_auto_dispense()
            
            # 약물 상태 모니터링 (30초마다)
            if not hasattr(self, 'last_medication_update') or time.ticks_diff(current_time_ms, self.last_medication_update) >= 30000:
                self._check_medication_status()
                self.last_medication_update = current_time_ms
            
            # 재알람 확인 (1초마다)
            self._check_reminder_alarms()
            
            # 알람 시스템 모니터링 (5초마다)
            if not hasattr(self, 'last_alarm_update') or time.ticks_diff(current_time_ms, self.last_alarm_update) >= 5000:
                self._check_alarm_system()
                self.last_alarm_update = current_time_ms
            
            # WiFi 연결 상태 모니터링 및 재연결 시도 (30초마다)
            if not hasattr(self, 'last_wifi_check') or time.ticks_diff(current_time_ms, self.last_wifi_check) >= 30000:
                self._check_and_reconnect_wifi()
                self.last_wifi_check = current_time_ms
            
            # NTP 시간 동기화 (1시간마다)
            if not hasattr(self, 'last_ntp_sync') or time.ticks_diff(current_time_ms, self.last_ntp_sync) >= 3600000:  # 1시간 = 3600000ms
                self._sync_ntp_time()
                self.last_ntp_sync = current_time_ms
            
        except Exception as e:
            # print(f"[ERROR] 메인 스크린 업데이트 실패: {e}")
            pass
        
    def _sync_ntp_time(self):
        """NTP 시간 동기화 (1시간마다 실행)"""
        try:
            # print("[INFO] 주기적 NTP 시간 동기화 시작...")
            
            # WiFi 매니저 지연 로딩
            wifi_manager = self.wifi_manager
            if wifi_manager and wifi_manager.is_connected:
                # WiFi 매니저의 NTP 동기화 함수 호출
                if hasattr(wifi_manager, 'sync_ntp_time'):
                    success = wifi_manager.sync_ntp_time()
                    if success:
                        # print("[OK] 주기적 NTP 시간 동기화 성공")
                        
                        # 동기화 후 시간 업데이트
                        self._update_current_time()
                        self._update_time_display()
                    else:
                        # print("[WARN] 주기적 NTP 시간 동기화 실패")
                        pass
                else:
                    # print("[WARN] WiFi 매니저에 NTP 동기화 함수가 없음")
                    pass
            else:
                # print("[WARN] WiFi 연결되지 않음 - NTP 동기화 건너뜀")
                pass
        except Exception as e:
            # print(f"[ERROR] 주기적 NTP 시간 동기화 실패: {e}")
            pass
    def save_current_settings(self):
        """현재 설정을 데이터 매니저에 저장"""
        try:
            settings = {
                "dose_schedule": self.dose_schedule,
                "auto_dispense_enabled": self.auto_dispense_enabled,
                "system_settings": {
                    "auto_dispense": self.auto_dispense_enabled,
                    "sound_enabled": True,
                    "display_brightness": 100
                }
            }
            
            success = self.data_manager.save_settings(settings)
            if success:
                # print("[OK] 현재 설정 저장 완료")
                pass
            else:
                # print("[ERROR] 현재 설정 저장 실패")
                pass
            return success
            
        except Exception as e:
            # print(f"[ERROR] 설정 저장 실패: {e}")
            return False
    
    def get_medication_summary(self):
        """약물 상태 요약 정보 반환 (자동 할당된 디스크만)"""
        try:
            # 자동 할당된 디스크 정보 가져오기
            auto_assigned_disks = self.data_manager.get_auto_assigned_disks()
            
            if auto_assigned_disks:
                # 자동 할당된 디스크만 표시
                disk_counts = {}
                for disk_info in auto_assigned_disks:
                    disk_number = disk_info['disk_number']
                    disk_counts[str(disk_number)] = self.data_manager.get_disk_count(disk_number)
                    # print(f"[DEBUG] 자동 할당 디스크 {disk_number} ({disk_info['meal_name']}): {disk_counts[str(disk_number)]}개")
            else:
                # 자동 할당 정보가 없으면 모든 디스크 표시
                disk_counts = {
                    "1": self.data_manager.get_disk_count(1),
                    "2": self.data_manager.get_disk_count(2),
                    "3": self.data_manager.get_disk_count(3)
                }
            
            summary = {
                "disk_counts": disk_counts,
                "low_stock_disks": [],
                "today_dispense_count": len(self.data_manager.get_today_dispense_logs())
            }
            
            # 부족한 디스크 확인
            for disk_num in [1, 2, 3]:
                if self.data_manager.is_disk_low_stock(disk_num):
                    summary["low_stock_disks"].append(disk_num)
            
            return summary
            
        except Exception as e:
            # print(f"[ERROR] 약물 상태 요약 생성 실패: {e}")
            return None
    
    def _check_medication_status(self):
        """약물 상태 모니터링 (메모리 최적화)"""
        try:
            # 약물 추적 시스템이 로드되지 않았으면 스킵
            if not hasattr(self, '_medication_tracker') or self._medication_tracker is None:
                return
            
            current_time = self._get_current_time()
            
            # 5분마다 약물 상태 확인
            if current_time == self.last_medication_check:
                return
            
            self.last_medication_check = current_time
            
            # 약물 상태 확인 (지연 로딩)
            medication_tracker = self.medication_tracker
            if medication_tracker:
                alerts = medication_tracker.check_low_stock_alerts()
                
                if alerts:
                    self.medication_alerts = alerts
                    self._handle_medication_alerts(alerts)
                else:
                    self.medication_alerts = []
                
        except Exception as e:
            # print(f"[ERROR] 약물 상태 모니터링 실패: {e}")
            pass
    
    def _handle_medication_alerts(self, alerts):
        """약물 알림 처리"""
        try:
            for alert in alerts:
                alert_type = alert.get("type", "unknown")
                disk_num = alert.get("disk", 0)
                message = alert.get("message", "")
                priority = alert.get("priority", "medium")
                
                if alert_type == "empty":
                    # print(f"🚨 [CRITICAL] {message}")
                    self._update_status(f"디스크 {disk_num} 소진 - 즉시 충전!")
                elif alert_type == "critical":
                    # print(f"⚠️ [HIGH] {message}")
                    self._update_status(f"디스크 {disk_num} 위험 수준!")
                elif alert_type == "low_stock":
                    # print(f"📢 [MEDIUM] {message}")
                    self._update_status(f"디스크 {disk_num} 부족")
                
        except Exception as e:
            # print(f"[ERROR] 약물 알림 처리 실패: {e}")
            pass
    
    def get_medication_status_display(self):
        """약물 상태 표시용 정보 반환"""
        try:
            summary = self.medication_tracker.get_medication_summary()
            if not summary:
                return "약물 상태 확인 중..."
            
            # 상태별 디스크 수
            normal = summary["normal_disks"]
            low_stock = summary["low_stock_disks"]
            critical = summary["critical_disks"]
            empty = summary["empty_disks"]
            
            if empty > 0:
                return f"🚨 {empty}개 디스크 소진"
            elif critical > 0:
                return f"⚠️ {critical}개 디스크 위험"
            elif low_stock > 0:
                return f"📢 {low_stock}개 디스크 부족"
            else:
                return f"✅ 모든 디스크 정상 ({normal}/3)"
                
        except Exception as e:
            # print(f"[ERROR] 약물 상태 표시 정보 생성 실패: {e}")
            return "상태 확인 오류"
    
    def get_disk_count_display(self, disk_num):
        """디스크 수량 표시용 정보 반환"""
        try:
            count = self.data_manager.get_disk_count(disk_num)
            disk_info = self.medication_tracker.get_disk_medication_info(disk_num)
            disk_name = disk_info.get("name", f"디스크 {disk_num}") if disk_info else f"디스크 {disk_num}"
            
            return f"{disk_name}: {count}개"
            
        except Exception as e:
            # print(f"[ERROR] 디스크 {disk_num} 수량 표시 정보 생성 실패: {e}")
            return f"디스크 {disk_num}: 확인 불가"
    
    def _check_alarm_system(self):
        """알람 시스템 모니터링 (메모리 최적화)"""
        try:
            # 알람 시스템이 로드되지 않았으면 스킵
            if not hasattr(self, '_alarm_system') or self._alarm_system is None:
                return
            
            # 지연 로딩으로 알람 시스템 가져오기
            alarm_system = self.alarm_system
            if not alarm_system:
                return
            
            # 재알람 확인 (매번 호출)
            alarm_system.check_reminder_alarms()
            
            # 활성 알람 상태 확인
            active_alarms = alarm_system.get_active_alarms()
            if active_alarms:
                self._handle_active_alarms(active_alarms)
            
            # 알람 실패 확인 및 일정 상태 업데이트
            self._check_alarm_failures()
                
        except Exception as e:
            # print(f"[ERROR] 알람 시스템 모니터링 실패: {e}")
            pass
    
    def _check_alarm_failures(self):
        """알람 실패 확인 및 일정 상태 업데이트 (메모리 최적화)"""
        try:
            # 알람 시스템이 로드되지 않았으면 스킵
            if not hasattr(self, '_alarm_system') or self._alarm_system is None:
                return
            
            alarm_system = self.alarm_system
            if not alarm_system:
                return
            
            # 알람 히스토리에서 최근 실패 기록 확인
            alarm_history = alarm_system.get_alarm_history()
            
            for record in alarm_history[-10:]:  # 최근 10개 기록만 확인
                if record.get("action") == "dispense_failed":
                    dose_index = record.get("dose_index")
                    meal_name = record.get("meal_name", f"일정 {dose_index + 1}")
                    
                    # 해당 일정의 상태를 "failed"로 업데이트
                    if dose_index < len(self.dose_schedule):
                        if self.dose_schedule[dose_index]["status"] != "failed":
                            self.dose_schedule[dose_index]["status"] = "failed"
                            # print(f"❌ 일정 상태 업데이트: {meal_name} → 실패")
                            
                            # UI 업데이트
                            self._update_schedule_display()
                            
        except Exception as e:
            # print(f"[ERROR] 알람 실패 확인 실패: {e}")
            pass
    
    def _handle_active_alarms(self, active_alarms):
        """활성 알람 처리"""
        try:
            for dose_index, alarm_info in active_alarms.items():
                meal_name = alarm_info.get("meal_name", f"일정 {dose_index + 1}")
                dose_time = alarm_info.get("dose_time", "")
                reminder_count = alarm_info.get("reminder_count", 0)
                max_reminders = alarm_info.get("max_reminders", 5)
                
                if reminder_count == 0:
                    # 첫 알람
                    self._update_status(f"🔔 {meal_name} 복용 시간 ({dose_time})")
                else:
                    # 재알람
                    self._update_status(f"🔔 {meal_name} 재알람 {reminder_count}/{max_reminders}")
                
        except Exception as e:
            # print(f"[ERROR] 활성 알람 처리 실패: {e}")
            pass
    
    def get_alarm_status_display(self):
        """알람 상태 표시용 정보 반환"""
        try:
            active_alarms = self.alarm_system.get_active_alarms()
            alarm_summary = self.alarm_system.get_alarm_summary()
            
            if not active_alarms:
                return "🔕 알람 없음"
            
            active_count = len(active_alarms)
            if active_count == 1:
                dose_index = list(active_alarms.keys())[0]
                alarm_info = active_alarms[dose_index]
                meal_name = alarm_info.get("meal_name", f"일정 {dose_index + 1}")
                return f"🔔 {meal_name} 알람 활성"
            else:
                return f"🔔 {active_count}개 알람 활성"
                
        except Exception as e:
            # print(f"[ERROR] 알람 상태 표시 정보 생성 실패: {e}")
            return "알람 상태 확인 오류"
    
    def _update_current_time(self):
        """현재 시간 업데이트 (WiFi 매니저 사용)"""
        try:
            # WiFi 매니저에서 한국 시간 가져오기 (지연 로딩)
            wifi_manager = self.wifi_manager
            if wifi_manager and wifi_manager.is_connected and wifi_manager.time_synced:
                kst_time = wifi_manager.get_kst_time()
                hour = kst_time[3]
                minute = kst_time[4]
                self.current_time = f"{hour:02d}:{minute:02d}"
                self._wifi_status = {"connected": True, "ssid": wifi_manager.connected_ssid}
            else:
                # WiFi 연결이 없으면 RTC 사용
                current = self.rtc.datetime()
                hour = current[4]
                minute = current[5]
                self.current_time = f"{hour:02d}:{minute:02d}"
                self._wifi_status = {"connected": False, "ssid": None}
        except Exception as e:
            # print(f"  [ERROR] 현재 시간 업데이트 실패: {e}")
            self.current_time = "00:00"
    
    def _update_time_display(self):
        """시간 표시 업데이트"""
        try:
            if hasattr(self, 'current_time_label'):
                self.current_time_label.set_text(self.current_time)
        except Exception as e:
            # print(f"  [ERROR] 시간 표시 업데이트 실패: {e}")
            pass
    
    def _update_pill_count_display(self):
        """알약 개수 표시 업데이트 (모든 일정)"""
        try:
            if hasattr(self, 'pill_count_labels') and self.pill_count_labels:
                # 복용 횟수 확인
                dose_count = len(self.dose_schedule)
                
                if dose_count == 1:
                    # 1일 1회: 모든 디스크의 총합 표시
                    self._update_total_pill_count_display()
                else:
                    # 1일 2회 이상: 기존 방식 (디스크별 개별 표시)
                    self._update_individual_pill_count_display()
                        
        except Exception as e:
            # print(f"  [ERROR] 알약 개수 표시 업데이트 실패: {e}")
            pass
    
    def _get_selected_disks_from_dose_time(self):
        """복용 시간 정보에서 선택된 디스크들 가져오기 (DataManager 사용)"""
        try:
            # print(f"[DEBUG] _get_selected_disks_from_dose_time 호출됨")
            
            # DataManager에서 복용 시간 정보 가져오기
            from data_manager import DataManager
            data_manager = DataManager()
            dose_times = data_manager.get_dose_times()
            
            # print(f"[DEBUG] dose_times 전체 데이터: {dose_times}")
            
            if dose_times and len(dose_times) > 0:
                first_dose_info = dose_times[0]
                # print(f"[DEBUG] 첫 번째 복용 정보: {first_dose_info}")
                # print(f"[DEBUG] first_dose_info 타입: {type(first_dose_info)}")
                
                if isinstance(first_dose_info, dict):
                    # print(f"[DEBUG] first_dose_info 키들: {list(first_dose_info.keys())}")
                    if 'selected_disks' in first_dose_info:
                        selected_disks = first_dose_info['selected_disks']
                        # print(f"[DEBUG] DataManager에서 선택된 디스크 불러오기: {selected_disks}")
                        return selected_disks
                    else:
                        # print("[DEBUG] selected_disks 키가 없음 - 실제 알약이 있는 디스크 자동 감지")
                        # selected_disks가 없으면 실제 알약이 있는 디스크를 자동으로 감지
                        disks_with_pills = []
                        for disk_num in [1, 2, 3]:
                            count = self.data_manager.get_disk_count(disk_num)
                            print(f"[DEBUG] 디스크 {disk_num}: {count}개 알약")
                            if count > 0:
                                disks_with_pills.append(disk_num)
                        print(f"[DEBUG] 실제 알약이 있는 디스크 자동 감지: {disks_with_pills}")
                        return disks_with_pills
                else:
                    # print(f"[DEBUG] first_dose_info가 딕셔너리가 아님: {type(first_dose_info)}")
                    pass
            
            # print("[WARN] 선택된 디스크 정보 없음, 기본값 사용")
            return [1]  # 기본값
        except Exception as e:
            # print(f"[ERROR] 선택된 디스크 불러오기 실패: {e}")
            import sys
            sys.print_exception(e)
            return [1]  # 기본값
    
    def _get_selected_disks_for_dose(self, dose_index):
        """특정 복용 시간에 대한 선택된 디스크들 가져오기 (global_data 직접 사용)"""
        try:
            # data_manager에서 직접 복용 시간 정보 가져오기
            from data_manager import DataManager
            data_manager = DataManager()
            dose_times = data_manager.get_dose_times()
            
            if dose_times and len(dose_times) > dose_index:
                dose_info = dose_times[dose_index]
                if isinstance(dose_info, dict) and 'selected_disks' in dose_info:
                    selected_disks = dose_info['selected_disks']
                    # print(f"[DEBUG] 일정 {dose_index + 1} 선택된 디스크: {selected_disks}")
                    return selected_disks
            
            # 기본값: 모든 복용 시간에 동일한 디스크 사용
            selected_disks = self._get_selected_disks_from_dose_time()
            # print(f"[DEBUG] 일정 {dose_index + 1} 기본 디스크 사용: {selected_disks}")
            return selected_disks
            
        except Exception as e:
            # print(f"[ERROR] 일정 {dose_index + 1} 디스크 정보 불러오기 실패: {e}")
            return [1]  # 기본값
    
    
    def _update_total_pill_count_display(self):
        """1일 1회일 때 선택된 디스크들의 총합 알약 개수 표시"""
        try:
            # print(f"[DEBUG] _update_total_pill_count_display 호출됨")
            
            # 선택된 디스크들 가져오기
            selected_disks = self._get_selected_disks_from_dose_time()
            # print(f"[DEBUG] 선택된 디스크 목록: {selected_disks}")
            
            # 선택된 디스크들의 총합 계산
            total_count = 0
            total_capacity = 0
            
            for disk_num in selected_disks:
                current_count = self.data_manager.get_disk_count(disk_num)
                # print(f"[DEBUG] 디스크 {disk_num}: {current_count}개")
                total_count += current_count
                total_capacity += 15  # 디스크당 최대 15칸
            
            # print(f"[DEBUG] 총합 계산: {total_count}/{total_capacity}")
            
            # 모든 일정에 동일한 총합 표시
            for i, pill_count_label in enumerate(self.pill_count_labels):
                if i < len(self.dose_schedule):
                    count_text = f"{total_count}/{total_capacity}"
                    pill_count_label.set_text(count_text)
                    pill_count_label.set_style_text_color(lv.color_hex(0x000000), 0)
                    
            # print(f"  [DEBUG] 1일 1회 선택된 디스크 총합 표시: {total_count}/{total_capacity} (디스크: {selected_disks})")
                    
        except Exception as e:
            # print(f"  [ERROR] 총합 알약 개수 표시 실패: {e}")
            pass
    
    def _update_individual_pill_count_display(self):
        """1일 2회 이상일 때 개별 디스크 알약 개수 표시 (자동 할당된 디스크 정보 우선 사용)"""
        try:
            # 자동 할당된 디스크 정보 우선 확인
            auto_assigned_disks = self.data_manager.get_auto_assigned_disks()
            
            if auto_assigned_disks and len(auto_assigned_disks) > 0:
                # 자동 할당된 디스크 정보 사용
                # print(f"[DEBUG] 자동 할당된 디스크 정보로 개별 수량 표시: {len(auto_assigned_disks)}개")
                
                for i, pill_count_label in enumerate(self.pill_count_labels):
                    if i < len(auto_assigned_disks):
                        disk_info = auto_assigned_disks[i]
                        disk_number = disk_info['disk_number']
                        meal_name = disk_info['meal_name']
                        
                        # 디스크의 현재 개수와 최대 용량 가져오기
                        current_count = self.data_manager.get_disk_count(disk_number)
                        max_capacity = 15  # 디스크당 최대 15칸
                        
                        # 표시 텍스트 업데이트
                        count_text = f"{current_count}/{max_capacity}"
                        pill_count_label.set_text(count_text)
                        
                        # 개수에 따른 색상 변경
                        pill_count_label.set_style_text_color(lv.color_hex(0x000000), 0)
                        
                        # print(f"[DEBUG] 자동 할당 디스크 {disk_number} ({meal_name}): {current_count}/{max_capacity}")
                        
            else:
                # 자동 할당 정보가 없으면 기존 방식 사용
                # print("[DEBUG] 자동 할당 정보 없음 - 기존 방식으로 개별 수량 표시")
                
                for i, pill_count_label in enumerate(self.pill_count_labels):
                    if i < len(self.dose_schedule):
                        current_dose = self.dose_schedule[i]
                        
                        # dose_time_screen에서 설정한 selected_disks 정보 사용
                        selected_disks = current_dose.get('selected_disks', [i + 1])
                        if selected_disks:
                            disk_num = selected_disks[0]  # 첫 번째 선택된 디스크 사용
                        else:
                            disk_num = i + 1  # 기본값
                        
                        # 디스크의 현재 개수와 최대 용량 가져오기
                        data_manager = self.data_manager
                        if data_manager:
                            current_count = data_manager.get_disk_count(disk_num)
                        else:
                            current_count = 15  # 기본값
                        
                        max_capacity = 15  # 디스크당 최대 15칸
                        
                        # 표시 텍스트 업데이트
                        count_text = f"{current_count}/{max_capacity}"
                        pill_count_label.set_text(count_text)
                        
                        # 개수에 따른 색상 변경
                        # 알약 개수는 항상 검정색으로 표시
                        pill_count_label.set_style_text_color(lv.color_hex(0x000000), 0)
                        
        except Exception as e:
            # print(f"  [ERROR] 개별 알약 개수 표시 실패: {e}")
            pass
    
    def on_button_a(self):
        """버튼 A - 배출"""
        # print("🔵 버튼 A: 배출")
        
        try:
            # 활성 알람이 있는지 확인
            active_alarms = self.alarm_system.get_active_alarms()
            
            if active_alarms:
                # 활성 알람이 있으면 배출 트리거
                # print("🔔 활성 알람 감지 - 배출 트리거")
                self._trigger_dispense_from_alarm()
            else:
                # 활성 알람이 없으면 수동 배출 실행
                # print("🔵 수동 배출 실행")
                self._update_status("수동 배출 중...")
                
                try:
                    # 1단계: 먼저 알람 실행 (메모리 절약)
                    # print(f"  [DEBUG] 알람 실행 시작...")
                    self._play_dispense_voice()
                    # print(f"  [DEBUG] 알람 실행 완료")
                    
                    # 2단계: 알람 실행 후 모터 시스템 초기화 (필요할 때만)
                    # print(f"  [DEBUG] 모터 시스템 초기화 시작...")
                    motor_system = self._init_motor_system()
                    # print(f"  [DEBUG] 모터 시스템 초기화 완료")
                    
                    # print(f"  [RETRY] 수동 배출 시퀀스 시작: 일정 {self.current_dose_index + 1}")
                    
                    # print(f"  [DEBUG] 선택된 디스크 확인 시작...")
                    required_disks = self._get_selected_disks_for_dose(self.current_dose_index)
                    # print(f"  [INFO] 선택된 디스크들: {required_disks}")
                    
                    # print(f"  📋 필요한 디스크: {required_disks}")
                    
                    # print(f"  [DEBUG] 배출 함수 호출 시작...")
                    success = self._dispense_from_selected_disks_no_alarm(motor_system, required_disks)
                    # print(f"  [DEBUG] 배출 함수 호출 완료, 결과: {success}")
                    
                    if success:
                        # print(f"  [OK] 모든 디스크 배출 완료")
                        self._update_status("배출 완료")
                        
                        # 배출 성공 (안내는 배출 전에 이미 재생됨)
                        
                        self.dose_schedule[self.current_dose_index]["status"] = "completed"
                        
                        self.data_manager.log_dispense(self.current_dose_index, True)
                        
                        self.alarm_system.confirm_dispense(self.current_dose_index)
                        
                        # 디스크 수량 감소는 _dispense_from_selected_disks()에서 처리됨
                        # self._decrease_selected_disks_count(self.current_dose_index)  # 중복 제거
                        
                        self._update_schedule_display()
                        
                        # print(f"[OK] 수동 배출 성공: 일정 {self.current_dose_index + 1}")
                    else:
                        # print(f"  [ERROR] 배출 실패")
                        self._update_status("배출 실패")
                    
                except Exception as e:
                    self._update_status("수동 배출 실패")
                    # print(f"[ERROR] 수동 배출 실패: {e}")
                
        except Exception as e:
            # print(f"[ERROR] 버튼 A 처리 실패: {e}")
            self._update_status("버튼 A 처리 실패")
    
    def _trigger_dispense_from_alarm(self):
        """알람에서 배출 트리거 - 수동 배출 알림 후 배출"""
        try:
            active_alarms = self.alarm_system.get_active_alarms()
            
            if not active_alarms:
                # print("[WARN] 활성 알람이 없습니다")
                return
            
            # 첫 번째 활성 알람의 일정 인덱스 사용
            dose_index = list(active_alarms.keys())[0]
            alarm_info = active_alarms[dose_index]
            
            # print(f"🔔 알람 배출 트리거: {alarm_info['meal_name']} (일정 {dose_index + 1})")
            
            # 1단계: 수동 배출 알림 재생 (버저 → LED → 음성)
            # print("🔊 수동 배출 알림 시작 (버저 → LED → 음성)")
            self._play_dispense_voice()
            
            # 2단계: 알람 확인 처리
            self.alarm_system.confirm_dispense(dose_index)
            
            # 3단계: 배출 시퀀스 실행
            self._update_status("알람 배출 중...")
            success = self._execute_dispense_sequence(dose_index)
            
            if success:
                # print(f"[OK] 알람 배출 성공: {alarm_info['meal_name']}")
                self._update_status("알람 배출 완료")
                
                # 알람 배출 성공 (안내는 배출 전에 이미 재생됨)
            else:
                # print(f"[ERROR] 알람 배출 실패: {alarm_info['meal_name']}")
                self._update_status("알람 배출 실패")
                
        except Exception as e:
            # print(f"[ERROR] 알람 배출 트리거 실패: {e}")
            self._update_status("알람 배출 실패")
    
    def _execute_dispense_sequence(self, dose_index):
        """배출 시퀀스 실행 - 실제 알약 배출 수행"""
        try:
            # print(f"🔔 알람 배출 시퀀스 시작: 일정 {dose_index + 1}")
            
            # 1단계: 선택된 디스크 확인
            required_disks = self._get_selected_disks_for_dose(dose_index)
            # print(f"  [INFO] 선택된 디스크들: {required_disks}")
            
            if not required_disks:
                # print(f"  [ERROR] 선택된 디스크가 없음: 일정 {dose_index + 1}")
                return False
            
            # 2단계: 모터 시스템 초기화
            motor_system = self._init_motor_system()
            if not motor_system:
                # print(f"  [ERROR] 모터 시스템 초기화 실패")
                return False
            
            # 3단계: 실제 배출 실행
            # print(f"  [DEBUG] 배출 함수 호출 시작...")
            success = self._dispense_from_selected_disks_no_alarm(motor_system, required_disks)
            # print(f"  [DEBUG] 배출 함수 호출 완료, 결과: {success}")
            
            # 4단계: 배출 결과 처리
            if success:
                # 배출 성공 시 일정 상태 업데이트
                if dose_index < len(self.dose_schedule):
                    self.dose_schedule[dose_index]["status"] = "completed"
                    
                    # 데이터 매니저에 배출 성공 기록 저장
                    self.data_manager.log_dispense(dose_index, True)
                    
                    # UI 업데이트
                    self._update_schedule_display()
                    
                    # print(f"[OK] 알람 배출 성공: 일정 {dose_index + 1}")
                    return True
                else:
                    # print(f"[ERROR] 잘못된 일정 인덱스: {dose_index}")
                    return False
            else:
                # 배출 실패 시 상태 업데이트
                if dose_index < len(self.dose_schedule):
                    self.dose_schedule[dose_index]["status"] = "failed"
                    
                    # 데이터 매니저에 배출 실패 기록 저장
                    self.data_manager.log_dispense(dose_index, False)
                    
                    # print(f"[ERROR] 알람 배출 실패: 일정 {dose_index + 1}")
                    return False
                else:
                    # print(f"[ERROR] 잘못된 일정 인덱스: {dose_index}")
                    return False
                
        except Exception as e:
            # print(f"[ERROR] 알람 배출 시퀀스 실행 실패: {e}")
            return False
    
    def on_button_b(self):
        """버튼 B - 위로 (이전 일정으로 이동)"""
        # print("🔴 버튼 B: 위로")
        
        try:
            # 이전 일정으로 이동
            self.current_dose_index = (self.current_dose_index - 1) % len(self.dose_schedule)
            self._update_schedule_display()
            self._update_status(f"일정 {self.current_dose_index + 1} 선택")
            # print(f"[OK] 이전 일정으로 이동: {self.current_dose_index + 1}")
        except Exception as e:
            # print(f"[ERROR] 일정 이동 실패: {e}")
            self._update_status("일정 이동 실패")
    
    def on_button_c(self):
        """버튼 C - 아래 (다음 일정으로 이동)"""
        # print("🟡 버튼 C: 아래")
        
        try:
            # 다음 일정으로 이동
            self.current_dose_index = (self.current_dose_index + 1) % len(self.dose_schedule)
            self._update_schedule_display()
            self._update_status(f"일정 {self.current_dose_index + 1} 선택")
            # print(f"[OK] 다음 일정으로 이동: {self.current_dose_index + 1}")
        except Exception as e:
            # print(f"[ERROR] 일정 이동 실패: {e}")
            self._update_status("일정 이동 실패")
    
    def on_button_d(self):
        """버튼 D - 네트워크 연결 상태와 디스크 알약 상태에 따른 조건부 재부팅"""
        # print("🟢 버튼 D: 조건부 재부팅 시작")
        self._update_status("상태 확인 중...")
        
        # 네트워크 연결 상태 확인
        is_network_connected = self._check_network_connection()
        
        # 디스크 알약 상태 확인
        has_pills_in_disk = self._check_disk_pill_status()
        
        print(f"[DEBUG] 네트워크 연결: {is_network_connected}, 디스크 알약: {has_pills_in_disk}")
        
        # 조건에 따른 분기 처리
        if is_network_connected and has_pills_in_disk:
            # 케이스 1: 네트워크 연결됨 + 알약 있음
            # print("[INFO] 케이스 1: 네트워크 연결됨 + 알약 있음 - 시간-분 설정으로 재부팅")
            self._update_status("시간-분 설정으로 재부팅...")
            self._make_screen_white()
            self._restart_to_dose_time()
        elif is_network_connected and not has_pills_in_disk:
            # 케이스 2: 네트워크 연결됨 + 알약 없음
            # print("[INFO] 케이스 2: 네트워크 연결됨 + 알약 없음 - 복용시간선택으로 재부팅")
            self._update_status("복용시간선택으로 재부팅...")
            self._make_screen_white()
            self._restart_to_meal_time()
        else:
            # 케이스 3: 네트워크 연결 안됨 + 알약 없음 (현재 로직)
            # print("[INFO] 케이스 3: 네트워크 연결 안됨 + 알약 없음 - 네트워크 선택으로 재부팅")
            self._update_status("네트워크 선택으로 재부팅...")
            self._make_screen_white()
            self._restart_to_wifi_scan()
    
    def _check_network_connection(self):
        """네트워크 연결 상태 확인"""
        try:
            import network
            import time
            
            # WiFi 인터페이스 직접 체크
            wlan = network.WLAN(network.STA_IF)
            is_active = wlan.active()
            is_connected = wlan.isconnected()
            
            print(f"[DEBUG] WiFi active: {is_active}, connected: {is_connected}")
            
            # WiFiManager도 체크
            try:
                from wifi_manager import WiFiManager
                wifi_manager = WiFiManager()
                wifi_manager_connected = wifi_manager.is_connected
                print(f"[DEBUG] WiFiManager.is_connected: {wifi_manager_connected}")
            except Exception as e:
                print(f"[DEBUG] WiFiManager 체크 실패: {e}")
                wifi_manager_connected = False
            
            # 둘 중 하나라도 연결되어 있으면 True
            result = is_connected or wifi_manager_connected
            print(f"[DEBUG] 최종 네트워크 연결 상태: {result}")
            return result
            
        except Exception as e:
            print(f"[ERROR] 네트워크 연결 상태 확인 실패: {e}")
            return False
    
    def _check_disk_pill_status(self):
        """디스크 알약 상태 확인 (하나라도 알약이 있으면 True)"""
        try:
            from data_manager import DataManager
            data_manager = DataManager()
            
            # 모든 디스크 확인 (1, 2, 3)
            for disk_num in [1, 2, 3]:
                count = data_manager.get_disk_count(disk_num)
                print(f"[DEBUG] 디스크 {disk_num}: {count}개 알약")
                if count > 0:
                    print(f"[DEBUG] 디스크 {disk_num}: {count}개 알약 있음")
                    return True
            
            print("[DEBUG] 모든 디스크에 알약 없음")
            return False
        except Exception as e:
            # print(f"[ERROR] 디스크 알약 상태 확인 실패: {e}")
            return False
    
    def _restart_to_dose_time(self):
        """시간-분 설정 화면으로 재부팅 (Pill 로딩 방식 응용)"""
        try:
            # print("[INFO] 시간-분 설정으로 재부팅 시작")
            
            # 시간-분 설정으로 부팅하도록 플래그 설정
            self._set_boot_to_dose_time()
            
            # 흰색 화면 만들기
            self._make_screen_white()
            
            # 잠시 대기 후 재부팅
            import time
            time.sleep(0.1)
            
            # print("[INFO] ESP 리셋 시작...")
            import machine
            machine.reset()
            
        except Exception as e:
            # print(f"[ERROR] 시간 설정 재부팅 실패: {e}")
            self._restart_to_wifi_scan()
    
    def _restart_to_meal_time(self):
        """복용시간선택 화면으로 재부팅 (Pill 로딩 방식 응용)"""
        try:
            # print("[INFO] 복용시간선택으로 재부팅 시작")
            
            # 복용시간선택으로 부팅하도록 플래그 설정
            self._set_boot_to_meal_time()
            
            # 흰색 화면 만들기
            self._make_screen_white()
            
            # 잠시 대기 후 재부팅
            import time
            time.sleep(0.1)
            
            # print("[INFO] ESP 리셋 시작...")
            import machine
            machine.reset()
            
        except Exception as e:
            # print(f"[ERROR] 복용시간선택 재부팅 실패: {e}")
            self._restart_to_wifi_scan()
    
    def _set_boot_to_dose_time(self):
        """시간-분 설정으로 부팅하도록 플래그 설정"""
        try:
            import json
            import os
            
            # /data 디렉토리 존재 확인 및 생성
            data_dir = "/data"
            try:
                if data_dir not in os.listdir("/"):
                    os.mkdir(data_dir)
            except OSError as e:
                if e.errno == 17:  # EEXIST - 디렉토리가 이미 존재
                    pass
                else:
                    raise
            
            boot_data = {"boot_target": "dose_time"}
            boot_file = "/data/boot_target.json"
            
            # 부팅 타겟 파일 생성/업데이트
            with open(boot_file, 'w') as f:
                json.dump(boot_data, f)
            
        except Exception as e:
            # print(f"[ERROR] 시간 설정 부팅 플래그 설정 실패: {e}")
            pass
    
    def _set_boot_to_meal_time(self):
        """복용시간선택으로 부팅하도록 플래그 설정"""
        try:
            import json
            import os
            
            # /data 디렉토리 존재 확인 및 생성
            data_dir = "/data"
            try:
                if data_dir not in os.listdir("/"):
                    os.mkdir(data_dir)
            except OSError as e:
                if e.errno == 17:  # EEXIST - 디렉토리가 이미 존재
                    pass
                else:
                    raise
            
            boot_data = {"boot_target": "meal_time"}
            boot_file = "/data/boot_target.json"
            
            # 부팅 타겟 파일 생성/업데이트
            with open(boot_file, 'w') as f:
                json.dump(boot_data, f)
            
        except Exception as e:
            # print(f"[ERROR] 복용시간선택 부팅 플래그 설정 실패: {e}")
            pass
    
    def _make_screen_white(self):
        """화면을 흰색으로 만들기 (디스플레이 테스트용)"""
        try:
            # print("[INFO] 화면을 흰색으로 변경 시작...")
            
            # 현재 화면 객체가 있는지 확인
            if hasattr(self, 'screen_obj') and self.screen_obj:
                # 화면 배경을 흰색으로 설정
                self.screen_obj.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)  # 흰색
                # print("[OK] 화면 배경을 흰색으로 변경 완료")
                
                # 모든 자식 객체 숨기기 (깔끔한 흰색 화면을 위해)
                if hasattr(self, 'main_container') and self.main_container:
                    self.main_container.delete()  # 메인 컨테이너 삭제
                    # print("[OK] 기존 UI 요소 제거 완료")
                
                # 새로운 빈 컨테이너 생성 (흰색 배경만)
                self.main_container = lv.obj(self.screen_obj)
                self.main_container.set_size(lv.pct(100), lv.pct(100))
                self.main_container.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)  # 흰색
                self.main_container.set_style_border_width(0, 0)  # 테두리 없음
                self.main_container.center()
                
                # print("[OK] 흰색 화면 설정 완료")
                self._update_status("화면이 흰색으로 변경됨")
                
            else:
                # print("[ERROR] 화면 객체가 없음")
                self._update_status("화면 변경 실패")
                
        except Exception as e:
            # print(f"[ERROR] 화면을 흰색으로 변경 실패: {e}")
            self._update_status("화면 변경 실패")
    
    def _restart_to_wifi_scan(self):
        """재부팅 후 WiFi 스캔 사용을 위한 처리"""
        try:
            # print("[INFO] 재부팅 후 WiFi 스캔 사용 준비 중...")
            
            # 설정 완료 플래그를 false로 변경 (WiFi 스캔 사용 가능하게)
            self._reset_setup_flag()
            
            # print("[INFO] 즉시 재부팅합니다...")
            
            # print("[INFO] ESP 재부팅 시작...")
            import machine
            machine.reset()
            
        except Exception as e:
            # print(f"[ERROR] 재부팅 처리 실패: {e}")
            self._update_status("재부팅 실패")
    
    def _reset_setup_flag(self):
        """설정 완료 플래그를 false로 리셋 (스타트업 메뉴 사용 가능하게) - boot_target.json 공통 사용"""
        try:
            import json
            import os
            
            # /data 디렉토리 존재 확인 및 생성
            data_dir = "/data"
            try:
                if data_dir not in os.listdir("/"):
                    os.mkdir(data_dir)
                    # print(f"[INFO] /data 디렉토리 생성됨")
            except OSError as e:
                if e.errno == 17:  # EEXIST - 디렉토리가 이미 존재
                    # print(f"[INFO] /data 디렉토리가 이미 존재함")
                    pass
                else:
                    raise
            
            # boot_target.json을 사용하여 WiFi 스캔으로 부팅하도록 설정
            boot_data = {"boot_target": "wifi_scan"}
            boot_file = "/data/boot_target.json"
            
            # 부팅 타겟 파일 생성/업데이트
            with open(boot_file, 'w') as f:
                json.dump(boot_data, f)
            
            # print("[OK] 설정 완료 플래그를 false로 리셋 - 스타트업으로 부팅 설정됨")
            
        except Exception as e:
            # print(f"[WARN] 설정 완료 플래그 리셋 실패: {e}")
            pass
            
    
    def on_show(self):
        """화면이 표시될 때 호출"""
        pass
    
    def on_hide(self):
        """화면이 숨겨질 때 호출"""
        pass
    
    
    def _start_auto_dispense_monitoring(self):
        """자동 배출 모니터링 시작"""
        # print("🕐 자동 배출 모니터링 시작")
        self._update_status("자동 배출 모니터링 중...")
    
    def _try_wifi_connection_with_retry(self, wifi_manager, max_retries=3, retry_delay=2):
        """WiFi 연결 재시도 로직"""
        # print(f"[INFO] WiFi 자동 연결 시작 (최대 {max_retries}회 재시도)")
        
        for attempt in range(max_retries):
            try:
                # print(f"[INFO] WiFi 연결 시도 {attempt + 1}/{max_retries}...")
                success = wifi_manager.try_auto_connect()
                
                if success:
                    # print(f"[OK] WiFi 연결 성공 (시도 {attempt + 1})")
                    return True
                else:
                    # print(f"[WARN] WiFi 연결 실패 (시도 {attempt + 1})")
                    
                    # 마지막 시도가 아니면 대기 후 재시도
                    if attempt < max_retries - 1:
                        # print(f"[INFO] {retry_delay}초 후 재시도...")
                        import time
                        time.sleep(retry_delay)
                        
                        # 재시도 전에 WiFi 재초기화
                        try:
                            wifi_manager.disconnect()
                            time.sleep(1)
                            # print("[INFO] WiFi 재초기화 완료")
                        except Exception as e:
                            # print(f"[WARN] WiFi 재초기화 실패: {e}")
                            pass
                    
            except Exception as e:
                # print(f"[ERROR] WiFi 연결 시도 {attempt + 1} 중 오류: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
        
        # print(f"[ERROR] WiFi 연결 최종 실패 ({max_retries}회 시도 완료)")
        return False
    
    def _check_and_reconnect_wifi(self):
        """WiFi 연결 상태 확인 및 재연결 시도"""
        try:
            wifi_manager = self.wifi_manager
            if not wifi_manager:
                # print("[DEBUG] WiFi 매니저 없음 - 재연결 시도 건너뜀")
                return
            
            # 현재 연결 상태 확인
            is_connected = wifi_manager.is_connected
            # print(f"[DEBUG] WiFi 연결 상태 확인: {is_connected}")
            
            if not is_connected:
                # print("[INFO] WiFi 연결 끊어짐 - 재연결 시도 시작")
                self._update_status("WiFi 재연결 중...")
                
                # 재연결 시도
                success = self._try_wifi_connection_with_retry(wifi_manager, max_retries=2, retry_delay=3)
                
                if success:
                    # print("[OK] WiFi 재연결 성공")
                    self.wifi_connected = True
                    self._wifi_status = {"connected": True, "ssid": wifi_manager.connected_ssid}
                    
                    # NTP 시간 동기화도 다시 시도
                    try:
                        ntp_success = wifi_manager.sync_ntp_time()
                        if ntp_success:
                            # print("[OK] WiFi 재연결 후 NTP 동기화 성공")
                            pass
                        else:
                            # print("[WARN] WiFi 재연결 후 NTP 동기화 실패")
                            pass
                    except Exception as e:
                        # print(f"[WARN] WiFi 재연결 후 NTP 동기화 오류: {e}")
                        pass
                    
                    self._update_status("WiFi 재연결 완료")
                else:
                    # print("[WARN] WiFi 재연결 실패")
                    self.wifi_connected = False
                    self._wifi_status = {"connected": False, "ssid": None}
                    self._update_status("WiFi 연결 안됨")
            else:
                # 연결되어 있으면 상태 업데이트
                if not self.wifi_connected:
                    # print("[INFO] WiFi 연결 상태 복구됨")
                    self.wifi_connected = True
                    self._wifi_status = {"connected": True, "ssid": wifi_manager.connected_ssid}
                
        except Exception as e:
            # print(f"[WARN] WiFi 연결 상태 확인 중 오류: {e}")
            pass
    
    def _start_periodic_ntp_sync(self):
        """주기적 NTP 시간 동기화 시작"""
        # print("🕐 주기적 NTP 시간 동기화 시작...")
        
        try:
            # WiFi 매니저가 연결되어 있으면 주기적 동기화 시작
            wifi_manager = self.wifi_manager
            if wifi_manager and wifi_manager.is_connected:
                # print("[INFO] WiFi 연결됨 - 주기적 NTP 동기화 활성화")
                # 5분마다 NTP 동기화 (실제로는 update() 메서드에서 처리)
                self._ntp_sync_enabled = True
                self._last_ntp_sync_time = 0
            else:
                # print("[INFO] WiFi 연결 안됨 - NTP 동기화 비활성화")
                self._ntp_sync_enabled = False
                
        except Exception as e:
            # print(f"[WARN] 주기적 NTP 동기화 설정 실패: {e}")
            self._ntp_sync_enabled = False
    
    def _get_current_time(self):
        """현재 시간 가져오기 (WiFi 우선, RTC 백업)"""
        try:
            # WiFi 매니저에서 한국 시간 가져오기 (지연 로딩)
            wifi_manager = self.wifi_manager
            if wifi_manager and wifi_manager.is_connected and wifi_manager.time_synced:
                kst_time = wifi_manager.get_kst_time()
                hour = kst_time[3]
                minute = kst_time[4]
                return f"{hour:02d}:{minute:02d}"
            else:
                # WiFi 연결이 없으면 RTC 사용
                current = self.rtc.datetime()
                hour = current[4]
                minute = current[5]
                return f"{hour:02d}:{minute:02d}"
        except Exception as e:
            # print(f"[ERROR] 현재 시간 가져오기 실패: {e}")
            return "00:00"
    
    
    def _check_auto_dispense(self):
        """자동 배출 시간 확인 (메모리 최적화)"""
        if not self.auto_dispense_enabled:
            return
        
        try:
            current_time = self._get_current_time()
            
            # 시간이 변경되었을 때만 확인 (메모리 절약)
            if current_time == self.last_check_time:
                return
            
            self.last_check_time = current_time
            
            # 각 일정 확인 (간소화)
            for i, schedule in enumerate(self.dose_schedule):
                if schedule["status"] == "pending" and schedule["time"] == current_time:
                    # 데이터 매니저를 사용하여 같은 시간에 배출 여부 확인
                    data_manager = self.data_manager
                    if data_manager and data_manager.was_dispensed_today(i, schedule['time']):
                        continue
                    
                    # print(f"⏰ 알람 트리거: 일정 {i+1} ({schedule['time']})")
                    
                    # 알람 시스템이 로드되어 있으면 알람 트리거
                    alarm_system = self.alarm_system
                    if alarm_system:
                        meal_name = schedule.get('meal_name', f'일정 {i+1}')
                        alarm_system.trigger_dose_alarm(i, schedule['time'], meal_name)
                        # print(f"🔔 알람 발생: A버튼을 눌러 복용하세요")
                    else:
                        # print(f"🔔 알람 시스템 없음: 수동 배출 필요")
                        pass
                    break
                    
        except Exception as e:
            # print(f"[ERROR] 자동 배출 확인 실패: {e}")
            pass
    
    def _check_reminder_alarms(self):
        """재알람 확인 - 5분 간격으로 최대 5회"""
        try:
            # 알람 시스템이 로드되어 있으면 재알람 확인
            alarm_system = self.alarm_system
            if alarm_system:
                alarm_system.check_reminder_alarms()
        except Exception as e:
            # print(f"[ERROR] 재알람 확인 실패: {e}")
            pass
            
    
    def _execute_auto_dispense(self, dose_index):
        """자동 배출 실행"""
        try:
            # print(f"🤖 자동 배출 시작: 일정 {dose_index + 1}")
            self._update_status("자동 배출 중...")
            
            # 현재 선택된 일정을 임시로 변경
            original_index = self.current_dose_index
            self.current_dose_index = dose_index
            
            # 배출 실행 (C 버튼과 동일한 로직)
            self.on_button_c()
            success = True  # on_button_c에서 이미 배출 처리됨
            
            # 원래 선택된 일정으로 복원
            self.current_dose_index = original_index
            
            if success:
                # 배출 성공 시 상태 업데이트
                self.dose_schedule[dose_index]["status"] = "completed"
                schedule_key = f"{self.dose_schedule[dose_index]['time']}_{dose_index}"
                self.last_dispense_time[schedule_key] = self._get_current_time()
                
                # 데이터 매니저에 배출 기록 저장
                self.data_manager.log_dispense(dose_index, True)
                
                # 알람 시스템에 배출 확인
                self.alarm_system.confirm_dispense(dose_index)
                
                # 디스크 수량 감소는 _dispense_from_selected_disks()에서 처리됨
                # self._decrease_selected_disks_count(dose_index)  # 중복 제거
                
                self._update_status("자동 배출 완료")
                # print(f"[OK] 자동 배출 성공: 일정 {dose_index + 1}")
            else:
                # 배출 실패 시 상태 업데이트
                self.dose_schedule[dose_index]["status"] = "failed"
                
                # 데이터 매니저에 배출 실패 기록 저장
                self.data_manager.log_dispense(dose_index, False)
                
                self._update_status("자동 배출 실패")
                # print(f"[ERROR] 자동 배출 실패: 일정 {dose_index + 1}")
            
            # UI 업데이트
            self._update_schedule_display()
            
        except Exception as e:
            # print(f"[ERROR] 자동 배출 실행 실패: {e}")
            self._update_status("자동 배출 오류")
    
    # def _decrease_selected_disks_count(self, dose_index):
    #     """선택된 디스크들의 약물 수량 감소 (중복 제거됨)"""
    #     # 이 함수는 _dispense_from_selected_disks()에서 _decrease_disk_count()로 대체됨
    #     # 중복으로 디스크 수량을 감소시키는 문제를 해결하기 위해 비활성화
    #     pass
    
    def _get_selected_disks_for_dose(self, dose_index):
        """복용 일정에 대한 선택된 디스크들 반환 (순차 소진 방식)"""
        try:
            # 복용 횟수 확인
            dose_count = len(self.dose_schedule)
            
            if dose_count == 1:
                # 1일 1회: 디스크1 → 디스크2 → 디스크3 순으로 배출
                result = self._get_sequential_dispense_order()
                # print(f"[DEBUG] _get_sequential_dispense_order() 결과: {result}")
                return result
            else:
                # 1일 2회 이상: 기존 방식 (일정별 개별 디스크)
                return self._get_individual_disk_for_dose(dose_index)
                
        except Exception as e:
            # print(f"[ERROR] 선택된 디스크 결정 실패: {e}")
            return [1]  # 기본값
    
    def _get_sequential_dispense_order(self):
        """1일 1회일 때 순차 배출 순서 반환 (선택된 디스크들 중에서 순차적으로)"""
        try:
            # dose_time_screen에서 선택된 디스크들 가져오기
            selected_disks = self._get_selected_disks_from_dose_time()
            
            if not selected_disks:
                # print("[WARN] 선택된 디스크 정보 없음, 기본값 사용")
                return [1]  # 기본값
            
            # 선택된 디스크들을 정렬해서 1, 2, 3 순서로 배출
            sorted_disks = sorted(selected_disks)
            # print(f"[INFO] 선택된 디스크 정렬: {selected_disks} → {sorted_disks}")
            
            # 정렬된 디스크들 중에서 사용 가능한 첫 번째 디스크 찾기
            for disk_num in sorted_disks:
                current_count = self.data_manager.get_disk_count(disk_num)
                if current_count > 0:
                    # print(f"[INFO] 1일 1회 순차 배출: 디스크 {disk_num}에서 1알 배출 ({current_count}개 남음)")
                    return [disk_num]  # 한 번에 하나의 디스크만 반환
                else:
                    # print(f"[INFO] 디스크 {disk_num}: {current_count}개 → 비어있음, 다음 디스크 확인")
                    pass
            # 선택된 모든 디스크가 비어있음
            # print("[WARN] 선택된 모든 디스크가 비어있음")
            return [selected_disks[0]] if selected_disks else [1]  # 첫 번째 선택된 디스크에서 시도
            
        except Exception as e:
            # print(f"[ERROR] 순차 배출 순서 결정 실패: {e}")
            return [1]  # 기본값
    
    
    def _get_individual_disk_for_dose(self, dose_index):
        """1일 2회 이상일 때 개별 디스크 반환 (자동 할당된 디스크 정보 사용)"""
        try:
            # 자동 할당된 디스크 정보에서 찾기
            from data_manager import DataManager
            data_manager = DataManager()
            auto_assigned_disks = data_manager.get_auto_assigned_disks()
            
            if auto_assigned_disks and dose_index < len(auto_assigned_disks):
                disk_info = auto_assigned_disks[dose_index]
                disk_number = disk_info['disk_number']
                meal_name = disk_info['meal_name']
                # print(f"[INFO] 복용 일정 {dose_index + 1} ({meal_name})의 자동 할당된 디스크: {disk_number}")
                return [disk_number]
            else:
                # 자동 할당 정보가 없으면 dose_times에서 찾기
                dose_times = []
                if hasattr(self.screen_manager, 'screens') and 'dose_time' in self.screen_manager.screens:
                    dose_time_screen = self.screen_manager.screens['dose_time']
                    if hasattr(dose_time_screen, 'get_dose_times'):
                        dose_times = dose_time_screen.get_dose_times()
                
                if dose_times and dose_index < len(dose_times):
                    dose_info = dose_times[dose_index]
                    selected_disks = dose_info.get('selected_disks', None)
                    
                    # selected_disks가 설정되어 있으면 사용
                    if selected_disks:
                        # print(f"[INFO] 복용 일정 {dose_index + 1}의 선택된 디스크: {selected_disks}")
                        return selected_disks
                    else:
                        # selected_disks가 없으면 일정 인덱스에 따라 해당 디스크 사용
                        disk_num = dose_index + 1  # 일정 0 → 디스크 1, 일정 1 → 디스크 2, 일정 2 → 디스크 3
                        # print(f"[INFO] 복용 일정 {dose_index + 1}에 selected_disks 정보 없음, 일정 인덱스 기반으로 디스크 {disk_num} 사용")
                        return [disk_num]
                else:
                    # dose_times 정보가 없으면 일정 인덱스에 따라 해당 디스크 사용
                    disk_num = dose_index + 1  # 일정 0 → 디스크 1, 일정 1 → 디스크 2, 일정 2 → 디스크 3
                    # print(f"[INFO] 복용 일정 {dose_index + 1}에 dose_times 정보 없음, 일정 인덱스 기반으로 디스크 {disk_num} 사용")
                    return [disk_num]
                
        except Exception as e:
            # print(f"[ERROR] 선택된 디스크 가져오기 실패: {e}")
            # 오류 시 일정 인덱스에 따라 해당 디스크 사용
            disk_num = dose_index + 1  # 일정 0 → 디스크 1, 일정 1 → 디스크 2, 일정 2 → 디스크 3
            # print(f"[INFO] 오류 발생으로 일정 인덱스 기반으로 디스크 {disk_num} 사용")
            return [disk_num]
    
    def _get_next_available_disk(self):
        """순차 소진 방식으로 다음 사용 가능한 디스크 반환 (최적화)"""
        try:
            # 디스크 1, 2, 3 순서로 확인하여 약물이 있는 첫 번째 디스크 반환
            for disk_num in [1, 2, 3]:
                current_count = self.data_manager.get_disk_count(disk_num)
                
                if current_count > 0:
                    # print(f"[INFO] 순차 소진: 디스크 {disk_num} 사용 가능 ({current_count}개 남음)")
                    return disk_num
            
            # 모든 디스크가 비어있으면 None 반환
            # print(f"[WARN] 순차 소진: 모든 디스크가 비어있음")
            return None
            
        except Exception as e:
            # print(f"[ERROR] 다음 사용 가능한 디스크 확인 실패: {e}")
            return None
    
    def _play_dispense_voice(self):
        """배출 완료 시 버저 → LED → 음성 순서로 안내 (메모리 최적화)"""
        try:
            # print("🔊 배출 완료 안내 시작 (버저 → LED → 음성)")
            
            # 1단계: 버저 소리 재생
            # print("🔔 1단계: 버저 소리 재생")
            self._play_buzzer_sound()
            
            # 버저 사용 후 참조 정리 및 가비지 컬렉션
            # print("[INFO] 버저 사용 후 참조 정리 및 메모리 정리")
            self._cleanup_audio_system()
            self._force_garbage_collection()
            
            # 2단계: LED 켜기
            # print("💡 2단계: LED 켜기")
            self._turn_on_led()
            
            # LED 사용 후 참조 정리 및 가비지 컬렉션
            # print("[INFO] LED 사용 후 참조 정리 및 메모리 정리")
            self._cleanup_led_controller()
            self._force_garbage_collection()
            
            # 3단계: 음성 재생 (메모리 정리 후)
            # print("🔊 3단계: 음성 재생 (메모리 정리 완료 후)")
            self._play_voice_audio_after_cleanup()
                
        except Exception as e:
            # print(f"[ERROR] 배출 완료 안내 실패: {e}")
            pass
        finally:
            # 최종 가비지 컬렉션
            self._force_garbage_collection()
            # print("[DEBUG] 배출 완료 안내 후 최종 가비지 컬렉션 완료")
    
    def _play_voice_audio_after_cleanup(self):
        """메모리 정리 후 음성 재생 (I2S 초기화 포함)"""
        try:
            # print("🔊 메모리 정리 완료 후 음성 재생 시작")
            
            # 오디오 시스템 새로 로딩 (메모리 정리 후)
            # audio_system이 없으면 새로 생성
            if not hasattr(self, 'audio_system') or self.audio_system is None:
                from audio_system import AudioSystem
                self.audio_system = AudioSystem()
            
            if self.audio_system:
                # print("🔊 dispense_medicine.wav 음성 파일 재생 (I2S 초기화 포함)")
                self.audio_system.play_voice("dispense_medicine.wav", blocking=True)
                
                # 음성 재생 후 참조 정리
                self._cleanup_audio_system()
            else:
                # print("🔊 배출 완료 음성 재생 (시뮬레이션)")
                pass                
        except Exception as e:
            # print(f"[ERROR] 음성 재생 실패: {e}")
            pass
    
    def _cleanup_audio_system(self):
        """오디오 시스템 참조 정리"""
        try:
            if hasattr(self, 'audio_system') and self.audio_system:
                # print("[INFO] 오디오 시스템 참조 정리 시작...")
                self.audio_system = None
                # print("[OK] 오디오 시스템 참조 정리 완료")
        except Exception as e:
            # print(f"[WARN] 오디오 시스템 참조 정리 실패: {e}")
            pass
    
    def _cleanup_led_controller(self):
        """LED 컨트롤러 참조 정리"""
        try:
            if hasattr(self, '_led_controller') and self._led_controller:
                # print("[INFO] LED 컨트롤러 참조 정리 시작...")
                self._led_controller = None
                # print("[OK] LED 컨트롤러 참조 정리 완료")
        except Exception as e:
            # print(f"[WARN] LED 컨트롤러 참조 정리 실패: {e}")
            pass
    
    def _force_garbage_collection(self):
        """강제 가비지 컬렉션 수행 - 표준화된 시스템 사용"""
        try:
            from memory_utils import aggressive_garbage_collection
            
            # print("[INFO] MainScreen 강제 가비지 컬렉션 시작")
            
            # 표준화된 적극적인 가비지 컬렉션 사용
            result = aggressive_garbage_collection("MainScreen")
            
            if result and result['usage_percent'] > 94:
                # print("[WARN] 메모리 사용률이 높음, 추가 정리 수행")
                # 모든 캐시 정리
                self._cleanup_all_caches()
                
                # 추가 가비지 컬렉션
                from memory_utils import standard_garbage_collection
                standard_garbage_collection(10, 100, "MainScreen_추가정리")
            
            # print("[OK] MainScreen 강제 가비지 컬렉션 완료")
            
        except Exception as e:
            # print(f"[ERROR] 가비지 컬렉션 실패: {e}")
            pass
    
    def _cleanup_all_caches(self):
        """모든 캐시 정리"""
        try:
            # print("[INFO] 모든 캐시 정리 시작")
            
            # DataManager 캐시 정리
            if hasattr(self, 'data_manager') and self.data_manager:
                self.data_manager._medication_cache = None
                self.data_manager._dose_times = None
                self.data_manager._selected_meals = None
            
            # AudioSystem 캐시 정리
            if hasattr(self, 'audio_system') and self.audio_system:
                self.audio_system._clear_all_caches()
            
            # print("[OK] 모든 캐시 정리 완료")
            
        except Exception as e:
            # print(f"[ERROR] 캐시 정리 실패: {e}")
            pass
    
    def _play_buzzer_sound(self):
        """버저 소리 재생 (PWM으로 실제 재생)"""
        try:
            # print("🔔 버저 소리 재생 시작 (PWM)")
            
            # PWM으로 실제 버저 소리 재생
            from machine import Pin, PWM
            import time
            
            # 버저 핀 설정 (GPIO 18 - HARDWARE.md 참조)
            buzzer_pin = Pin(18, Pin.OUT)
            buzzer = PWM(buzzer_pin)
            
            # 1000Hz 톤으로 0.5초 재생
            buzzer.freq(1000)
            buzzer.duty(512)  # 50% 듀티 사이클
            time.sleep(0.5)
            
            # 버저 끄기
            buzzer.deinit()
            buzzer_pin.value(0)
            
            # print("🔔 버저 소리 재생 완료 (PWM)")
                
        except Exception as e:
            # print(f"[ERROR] 버저 소리 재생 실패: {e}")
            pass
    
    def _turn_on_led(self):
        """LED 켜기"""
        try:
            # print("💡 LED 켜기 시작")
            
            # 알람 시스템을 통해 LED 켜기
            if self.alarm_system:
                # 알람 시스템의 LED 컨트롤러 가져오기
                led_controller = self.alarm_system._get_led_controller()
                if led_controller:
                    # 성공 표시용 LED 켜기
                    led_controller.show_alarm_led()
                    # print("💡 LED 켜기 완료")
                    
                    # 1초 후 LED 끄기
                    import time
                    time.sleep(1)
                    led_controller.hide_alarm_led()
                    # print("💡 LED 끄기 완료")
                else:
                    # print("💡 LED 컨트롤러 없음, LED 시뮬레이션")
                    import time
                    time.sleep(1)  # 시뮬레이션
            else:
                # print("💡 알람 시스템 없음, LED 시뮬레이션")
                import time
                time.sleep(1)  # 시뮬레이션
                
        except Exception as e:
            # print(f"[ERROR] LED 제어 실패: {e}")
            pass
    
    def _play_voice_audio(self):
        """음성 재생 (수동 배출 시 dispense_medicine.wav 사용)"""
        try:
            # print("🔊 음성 재생 시작")
            
            # 음성 재생 직전 메모리 정리 강화
            import gc
            gc.collect()
            gc.collect()  # 두 번 정리
            import time
            time.sleep_ms(100)  # 100ms 대기
            
            # DataManager 캐시 비활성화 (메모리 절약)
            if hasattr(self, 'data_manager') and self.data_manager:
                try:
                    # 캐시된 데이터 정리
                    if hasattr(self.data_manager, 'clear_cache'):
                        self.data_manager.clear_cache()
                    # print("[INFO] DataManager 캐시 정리 완료")
                except Exception as cache_error:
                    # print(f"[WARN] 캐시 정리 실패: {cache_error}")
                    pass
            
            # 직접 오디오 시스템을 통해 음성 재생 (블로킹 모드로 실제 재생)
            try:
                from audio_system import AudioSystem
                audio_system = AudioSystem()
                audio_system.play_voice("dispense_medicine.wav", blocking=True)
                # print("🔊 dispense_medicine.wav 음성 재생 완료")
            except Exception as audio_error:
                # print(f"[WARN] 직접 오디오 시스템 재생 실패: {audio_error}")
                
                # 알람 시스템의 오디오 시스템을 통해 음성 재생 (백업)
                if hasattr(self.alarm_system, 'audio_system') and self.alarm_system.audio_system:
                    self.alarm_system.audio_system.play_voice("dispense_medicine.wav", blocking=True)
                    # print("🔊 알람 시스템을 통한 dispense_medicine.wav 음성 재생 완료")
                else:
                    # print("🔊 오디오 시스템 없음, 음성 재생 시뮬레이션")
                    import time
                    time.sleep(1)  # 시뮬레이션
                
        except Exception as e:
            # print(f"[ERROR] 음성 재생 실패: {e}")
            pass
    
    def _dispense_from_selected_disks(self, motor_system, selected_disks):
        """선택된 디스크들에서 순차적으로 배출 (알람 포함)"""
        try:
            # print(f"[INFO] 선택된 디스크들 순차 배출 시작: {selected_disks}")
            # print(f"[DEBUG] motor_system 타입: {type(motor_system)}")
            # print(f"[DEBUG] selected_disks 타입: {type(selected_disks)}, 값: {selected_disks}")
            
            # 선택된 디스크가 없으면 실패
            if not selected_disks:
                # print(f"[ERROR] 배출할 디스크가 없음")
                self._update_status("배출할 디스크 없음")
                return False
            
            # 배출 시작 전 안내 (버저 → LED → 음성)
            self._play_dispense_voice()
            
            for i, disk_num in enumerate(selected_disks):
                # print(f"[INFO] 디스크 {disk_num} 배출 중... ({i+1}/{len(selected_disks)})")
                self._update_status(f"디스크 {disk_num} 배출 중...")
                
                # 배출 전 디스크 수량 재확인 (순차 소진 방식)
                current_count = self.data_manager.get_disk_count(disk_num)
                if current_count <= 0:
                    # print(f"[WARN] 디스크 {disk_num}가 비어있음, 다음 디스크로 넘어감")
                    continue
                
                # 1. 디스크 회전
                disk_success = motor_system.rotate_disk(disk_num, 1)  # 1칸만 회전
                if not disk_success:
                    # print(f"[ERROR] 디스크 {disk_num} 회전 실패")
                    return False
                
                # 2. 배출구 열림 (디스크별 단계)
                open_success = motor_system.control_motor3_direct(disk_num)  # 디스크 번호 = 단계
                if not open_success:
                    # print(f"[ERROR] 디스크 {disk_num} 배출구 열림 실패")
                    return False
                
                # 3. 약이 떨어질 시간 대기
                import time
                time.sleep(2)  # 2초 대기
                
                # print(f"[OK] 디스크 {disk_num} 배출 완료")
                
                # 배출된 디스크의 수량 감소
                self._decrease_disk_count(disk_num)
                
                # 마지막 디스크가 아니면 잠시 대기
                if i < len(selected_disks) - 1:
                    time.sleep(1)  # 1초 간격
            
            # print(f"[OK] 모든 디스크 배출 완료: {selected_disks}")
            return True
            
        except Exception as e:
            # print(f"[ERROR] 선택된 디스크 배출 실패: {e}")
            import sys
            sys.print_exception(e)
            return False
    
    def _dispense_from_selected_disks_no_alarm(self, motor_system, selected_disks):
        """선택된 디스크들에서 순차적으로 배출 (알람 없음)"""
        try:
            # print(f"[INFO] 선택된 디스크들 순차 배출 시작: {selected_disks}")
            # print(f"[DEBUG] motor_system 타입: {type(motor_system)}")
            # print(f"[DEBUG] selected_disks 타입: {type(selected_disks)}, 값: {selected_disks}")
            
            # 선택된 디스크가 없으면 실패
            if not selected_disks:
                # print(f"[ERROR] 배출할 디스크가 없음")
                self._update_status("배출할 디스크 없음")
                return False
            
            # 알람 없이 바로 배출 시작
            
            for i, disk_num in enumerate(selected_disks):
                # print(f"[INFO] 디스크 {disk_num} 배출 중... ({i+1}/{len(selected_disks)})")
                self._update_status(f"디스크 {disk_num} 배출 중...")
                
                # 배출 전 디스크 수량 재확인 (순차 소진 방식)
                current_count = self.data_manager.get_disk_count(disk_num)
                if current_count <= 0:
                    # print(f"[WARN] 디스크 {disk_num}가 비어있음, 다음 디스크로 넘어감")
                    continue
                
                # 1. 디스크 회전
                disk_success = motor_system.rotate_disk(disk_num, 1)  # 1칸만 회전
                if not disk_success:
                    # print(f"[ERROR] 디스크 {disk_num} 회전 실패")
                    return False
                
                # 2. 배출구 열림 (디스크별 단계)
                open_success = motor_system.control_motor3_direct(disk_num)  # 디스크 번호 = 단계
                if not open_success:
                    # print(f"[ERROR] 디스크 {disk_num} 배출구 열림 실패")
                    return False
                
                # 3. 약이 떨어질 시간 대기
                import time
                time.sleep(2)  # 2초 대기
                
                # print(f"[OK] 디스크 {disk_num} 배출 완료")
                
                # 배출된 디스크의 수량 감소
                self._decrease_disk_count(disk_num)
                
                # 마지막 디스크가 아니면 잠시 대기
                if i < len(selected_disks) - 1:
                    time.sleep(1)  # 1초 간격
            
            # print(f"[OK] 모든 디스크 배출 완료: {selected_disks}")
            return True
            
        except Exception as e:
            # print(f"[ERROR] 선택된 디스크 배출 실패: {e}")
            import sys
            sys.print_exception(e)
            return False
    
    def _decrease_disk_count(self, disk_num):
        """배출된 디스크의 수량 감소"""
        try:
            # print(f"[DEBUG] _decrease_disk_count 호출됨: 디스크 {disk_num}")
            current_count = self.data_manager.get_disk_count(disk_num)
            # print(f"[DEBUG] 현재 수량: {current_count}")
            if current_count > 0:
                new_count = current_count - 1
                # print(f"[DEBUG] 새 수량: {new_count}")
                success = self.data_manager.update_disk_count(disk_num, new_count)
                if success:
                    # print(f"[INFO] 디스크 {disk_num} 약물 수량: {current_count} → {new_count}")
                    pass                    
                else:
                    # print(f"[ERROR] 디스크 {disk_num} 수량 업데이트 실패")
                    pass
            else:
                # print(f"[WARN] 디스크 {disk_num}가 이미 비어있음")
                pass
        except Exception as e:
            # print(f"[ERROR] 디스크 {disk_num} 수량 감소 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _update_schedule_display(self, specific_index=None):
        """복용 일정 표시 업데이트 (특정 일정만 또는 전체)"""
        try:
            if hasattr(self, 'schedule_labels') and self.schedule_labels:
                # 업데이트할 일정 인덱스 범위 결정
                if specific_index is not None:
                    # 특정 일정만 업데이트
                    update_range = [specific_index]
                else:
                    # 모든 일정 업데이트
                    update_range = range(len(self.schedule_labels))
                
                for i in update_range:
                    if i < len(self.schedule_labels) and i < len(self.dose_schedule):
                        schedule_label = self.schedule_labels[i]
                        schedule = self.dose_schedule[i]
                        
                        # 상태에 따른 아이콘 (LVGL 심볼 사용)
                        if schedule["status"] == "completed":
                            status_icon = lv.SYMBOL.OK
                        elif schedule["status"] == "failed":
                            status_icon = lv.SYMBOL.CLOSE
                        else:  # pending
                            status_icon = lv.SYMBOL.BELL
                        
                        # 현재 선택된 일정은 강조 표시 (▶ 심볼 제거)
                        schedule_text = f"{schedule['time']} {status_icon}"
                        
                        schedule_label.set_text(schedule_text)
                        
                        # 현재 선택된 일정은 다른 색상으로 표시
                        if i == self.current_dose_index:
                            schedule_label.set_style_text_color(lv.color_hex(0x007AFF), 0)  # 파란색
                        else:
                            schedule_label.set_style_text_color(lv.color_hex(0x1D1D1F), 0)  # 검정색
                            
        except Exception as e:
            # print(f"  [ERROR] 일정 표시 업데이트 실패: {e}")
            pass


class MockMotorSystem:
    """모의 모터 시스템"""
    
    def __init__(self):
        self.motor_controller = MockMotorController()
        # print("[OK] MockMotorSystem 초기화 완료")
    
    def control_dispense_slide(self, level):
        """모의 배출구 슬라이드 제어"""
        # print(f"🚪 모의 배출구 슬라이드 {level}단 (120도)")
        return True
    
    def rotate_disk(self, disk_num, steps):
        """모의 디스크 회전"""
        # print(f"[RETRY] 모의 디스크 {disk_num} 회전: {steps} 스텝")
        return True


class MockMotorController:
    """모의 모터 컨트롤러"""
    
    def __init__(self):
        self.motor_states = [0, 0, 0, 0]
        self.motor_steps = [0, 0, 0, 0]
        self.motor_positions = [0, 0, 0, 0]
        # print("[OK] MockMotorController 초기화 완료")
    
    def test_motor_simple(self, motor_index, steps):
        """모의 모터 간단 테스트"""
        # print(f"🧪 모의 모터 {motor_index} 간단 테스트 시작 ({steps}스텝)")
        # print(f"[OK] 모의 모터 {motor_index} 테스트 성공")
        return True
    
    def test_motor3_only(self, steps=50):
        """모터 3 전용 테스트 (모의)"""
        # print(f"🧪 모의 모터 3 전용 테스트 시작 ({steps}스텝)")
        # print("[OK] 모의 모터 3 테스트 성공")
        return True
