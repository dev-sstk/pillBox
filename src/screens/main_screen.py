"""
메인 화면
오늘의 알약 일정을 표시하는 대시보드 화면
Modern UI 스타일 적용 + 자동 배출 기능
"""

import sys
sys.path.append("/")

import time
import lvgl as lv
from ui_style import UIStyle
from machine import RTC
from wifi_manager import get_wifi_manager
from data_manager import DataManager
from medication_tracker import MedicationTracker
from alarm_system import AlarmSystem

class MainScreen:
    """메인 화면 클래스 - Modern UI 스타일 + 자동 배출 기능"""
    
    def __init__(self, screen_manager):
        """메인 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = 'main'
        self.screen_obj = None
        self.current_dose_index = 0
        self.dose_schedule = []  # 복용 일정
        self.last_update_time = 0
        
        # 실시간 정보
        self.rtc = RTC()
        self.current_time = self._get_current_time()  # 초기화 시 현재 시간 설정
        self.next_dose_time = ""
        self.time_until_next = ""
        self.wifi_status = {"connected": False, "ssid": None}
        
        # 필박스 상태
        self.disk_states = {"disk_1": 0, "disk_2": 0, "disk_3": 0}  # 각 디스크의 충전된 칸 수
        self.battery_level = 85  # 배터리 레벨 (시뮬레이션)
        self.wifi_connected = True  # WiFi 연결 상태 (시뮬레이션)
        
        # UI 업데이트 타이머
        self.ui_update_counter = 0
        self.battery_simulation_step = 0  # 배터리 시뮬레이션 단계 (0: 완충, 1: 3단계, 2: 2단계, 3: 1단계, 4: 방전)
        self.is_charging = False  # 충전 상태 (고정값)
        
        # UI 스타일 시스템 초기화
        self.ui_style = UIStyle()
        
        # 모터 시스템 (지연 초기화)
        self.motor_system = None
        
        # 데이터 관리자 초기화
        self.data_manager = DataManager()
        
        # 약물 추적 시스템 초기화
        self.medication_tracker = MedicationTracker(self.data_manager)
        
        # 알람 시스템 초기화 (오디오 시스템과 LED 컨트롤러 전달)
        print("[DEBUG] 알람 시스템 초기화 시작")
        
        # 직접 오디오 시스템과 LED 컨트롤러 생성
        try:
            from audio_system import AudioSystem
            from led_controller import LEDController
            audio_system = AudioSystem()
            led_controller = LEDController()
            print("[DEBUG] 오디오 시스템과 LED 컨트롤러 직접 생성 완료")
        except Exception as e:
            print(f"[ERROR] 오디오 시스템/LED 컨트롤러 생성 실패: {e}")
            audio_system = None
            led_controller = None
        
        self.alarm_system = AlarmSystem(self.data_manager, audio_system, led_controller)
        print("[DEBUG] 알람 시스템 초기화 완료")
        
        # 시간 모니터링 (자동 배출용)
        self.last_check_time = ""
        self.auto_dispense_enabled = True
        self.last_dispense_time = {}  # 각 일정별 마지막 배출 시간 기록
        
        # 약물 상태 모니터링
        self.last_medication_check = ""
        self.medication_alerts = []
        
        # 알람 상태 모니터링
        self.last_alarm_check = ""
        
        # 샘플 데이터 초기화
        self._init_sample_data()
        
        # Modern 화면 생성
        self._create_modern_screen()
        
        print(f"[OK] {self.screen_name} 화면 초기화 완료")
    
    def _init_sample_data(self):
        """샘플 데이터 초기화 - dose_time_screen에서 설정한 시간 가져오기"""
        # NTP 시간을 활용한 현재 날짜 가져오기 (RTC 백업 포함)
        try:
            # WiFi 매니저에서 한국 시간 가져오기
            wifi_manager = get_wifi_manager()
            if wifi_manager and wifi_manager.is_connected and wifi_manager.time_synced:
                kst_time = wifi_manager.get_kst_time()
                year, month, day, hour, minute, second = kst_time[:6]
                print(f"  📅 NTP 시간으로 날짜 설정: {year}년 {month}월 {day}일 {hour}:{minute:02d}:{second:02d}")
                
                # NTP 시간을 RTC에 백업 저장 (외부 배터리 활용)
                from machine import RTC
                rtc = RTC()
                # RTC는 (year, month, day, weekday, hour, minute, second, microsecond) 형식
                weekday = (day - 1) % 7  # 간단한 요일 계산 (0=월요일)
                rtc.datetime((year, month, day, weekday, hour, minute, second, 0))
                print("  [SAVE] NTP 시간을 RTC에 백업 저장 완료")
                
            else:
                # NTP가 없으면 RTC 백업 시간 사용 (외부 배터리로 유지됨)
                from machine import RTC
                rtc = RTC()
                year, month, day = rtc.datetime()[:3]
                print(f"  📅 RTC 백업 시간으로 날짜 설정: {year}년 {month}월 {day}일 (외부 배터리)")
                
        except Exception as e:
            # 오류 시 기본값 사용
            month, day = 12, 25
            print(f"  [WARN] 날짜 설정 오류, 기본값 사용: {month}월 {day}일 ({e})")
        
        # dose_time_screen에서 설정한 시간 가져오기
        try:
            if hasattr(self.screen_manager, 'screens') and 'dose_time' in self.screen_manager.screens:
                dose_time_screen = self.screen_manager.screens['dose_time']
                if hasattr(dose_time_screen, 'get_dose_times'):
                    dose_times = dose_time_screen.get_dose_times()
                    if dose_times:
                        self.dose_schedule = []
                        for dose_time in dose_times:
                            # dose_time이 딕셔너리인 경우 'time' 키 사용, 문자열인 경우 그대로 사용
                            if isinstance(dose_time, dict):
                                time_str = dose_time.get('time', '08:00')
                            else:
                                time_str = dose_time
                            
                            self.dose_schedule.append({
                                "time": time_str,
                                "status": "pending"
                            })
                        print(f"  [INFO] dose_time_screen에서 설정한 시간 가져옴: {dose_times}")
                    else:
                        # 설정된 시간이 없으면 기본값 사용
                        self.dose_schedule = [
                            {"time": "08:00", "status": "pending"},
                            {"time": "12:00", "status": "pending"},
                            {"time": "18:00", "status": "pending"}
                        ]
                        print("  [INFO] 설정된 시간 없음, 기본값 사용")
                else:
                    # get_dose_times 메서드가 없으면 기본값 사용
                    self.dose_schedule = [
                        {"time": "08:00", "status": "pending"},
                        {"time": "12:00", "status": "pending"},
                        {"time": "18:00", "status": "pending"}
                    ]
                    print("  [INFO] dose_time_screen 메서드 없음, 기본값 사용")
            else:
                # dose_time_screen이 없으면 기본값 사용
                self.dose_schedule = [
                    {"time": "08:00", "status": "pending"},
                    {"time": "12:00", "status": "pending"},
                    {"time": "18:00", "status": "pending"}
                ]
                print("  [INFO] dose_time_screen 없음, 기본값 사용")
        except Exception as e:
            # 오류 시 기본값 사용
            self.dose_schedule = [
                {"time": "08:00", "status": "pending"},
                {"time": "12:00", "status": "pending"},
                {"time": "18:00", "status": "pending"}
            ]
            print(f"  [WARN] dose_time_screen에서 시간 가져오기 실패, 기본값 사용: {e}")
        
        self.current_date = f"{year}-{month:02d}-{day:02d}"
    
    def _create_modern_screen(self):
        """Modern 스타일 화면 생성"""
        print(f"  [INFO] {self.screen_name} Modern 화면 생성 시작...")
        
        try:
            # 메모리 정리
            import gc
            gc.collect()
            print("  [OK] 메모리 정리 완료")
            
            # 화면 생성
            print("  [INFO] 화면 객체 생성...")
            self.screen_obj = lv.obj()
            print(f"  [INFO] 화면 객체 생성됨: {self.screen_obj}")
            
            # 화면 배경 스타일 적용 (Modern 스타일)
            self.ui_style.apply_screen_style(self.screen_obj)
            
            # 스크롤바 완전 비활성화
            self.screen_obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.screen_obj.set_scroll_dir(lv.DIR.NONE)
            
            print("  [OK] 화면 배경 설정 완료")
            
            # 화면 크기 설정
            self.screen_obj.set_size(160, 128)
            print("  [INFO] 화면 크기: 160x128")
            
            # 메인 컨테이너 생성
            print("  [INFO] 메인 컨테이너 생성 시도...")
            self.main_container = lv.obj(self.screen_obj)
            self.main_container.set_size(160, 128)
            self.main_container.align(lv.ALIGN.CENTER, 0, 0)
            self.main_container.set_style_bg_opa(0, 0)  # 투명 배경
            self.main_container.set_style_border_width(0, 0)  # 테두리 없음
            
            # 스크롤바 완전 비활성화
            self.main_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.main_container.set_scroll_dir(lv.DIR.NONE)
            
            print("  [INFO] 메인 컨테이너 생성 완료")
            
            # 제목 영역 생성
            print("  [INFO] 제목 영역 생성 시도...")
            self._create_title_area()
            print("  [INFO] 제목 영역 생성 완료")
            
            # 복용 일정 영역 생성
            print("  [INFO] 복용 일정 영역 생성 시도...")
            self._create_schedule_area()
            print("  [INFO] 복용 일정 영역 생성 완료")
            
            # 하단 버튼 힌트 영역 생성
            print("  [INFO] 버튼 힌트 영역 생성 시도...")
            self._create_button_hints_area()
            print("  [INFO] 버튼 힌트 영역 생성 완료")
            
            print("  [OK] Modern 화면 생성 완료")
            
        except Exception as e:
            print(f"  [ERROR] Modern 화면 생성 중 오류 발생: {e}")
            import sys
            sys.print_exception(e)
            # 기본 화면 생성 시도
            print(f"  [INFO] {self.screen_name} 기본 화면 생성 시도...")
            try:
                self._create_basic_screen()
                print(f"  [OK] {self.screen_name} 기본 화면 초기화 완료")
            except Exception as e2:
                print(f"  [ERROR] {self.screen_name} 기본 화면 초기화도 실패: {e2}")
                import sys
                sys.print_exception(e2)
    
    def _create_title_area(self):
        """제목 영역 생성"""
        try:
            # 제목 영역 완전 제거됨
            
            # 현재 시간과 상태 표시기를 독립적으로 생성
            self._create_current_time_and_status()
            
        except Exception as e:
            print(f"  [ERROR] 제목 영역 생성 실패: {e}")

    def _create_current_time_and_status(self):
        """현재 시간과 상태 표시기를 독립적으로 생성"""
        try:
            # 현재 시간 표시 (좌측 상단)
            self.current_time_label = lv.label(self.main_container)
            self.current_time_label.set_text(self.current_time)
            self.current_time_label.align(lv.ALIGN.TOP_LEFT, 5, -10)  # 배터리와 같은 y축 위치
            self.current_time_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
            self.current_time_label.set_style_text_color(lv.color_hex(0x007AFF), 0)
            
            # 알약 개수 표시 (시간 오른편)
            self.pill_count_label = lv.label(self.main_container)
            self.pill_count_label.set_text("10/15")  # 기본값
            self.pill_count_label.align(lv.ALIGN.TOP_LEFT, 80, -10)  # 시간 오른편
            self.pill_count_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
            self.pill_count_label.set_style_text_color(lv.color_hex(0x34C759), 0)  # 초록색
        
            # WiFi 심볼을 상단 중앙에 독립적으로 배치
            self._create_wifi_indicator()
        
            # 배터리 상태 표시기 (오른쪽만)
            self._create_battery_indicators()
        
        except Exception as e:
            print(f"  [ERROR] 현재 시간과 상태 표시기 생성 실패: {e}")

    def _create_wifi_indicator(self):
        """WiFi 심볼을 상단 중앙에 독립적으로 생성"""
        try:
            # WiFi 표시 (화면 상단 중앙) - 완전히 독립적으로 배치
            wifi_icon = lv.SYMBOL.WIFI if self.wifi_connected else lv.SYMBOL.CLOSE
            self.wifi_label = lv.label(self.main_container)
            self.wifi_label.set_text(wifi_icon)
            self.wifi_label.align(lv.ALIGN.TOP_MID, 0, -10)  # 배터리와 같은 y축 위치
            self.wifi_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            self.wifi_label.set_style_text_color(lv.color_hex(0x007AFF) if self.wifi_connected else lv.color_hex(0xFF3B30), 0)
            print("  [OK] WiFi 심볼을 상단 중앙에 배치 완료")
        except Exception as e:
            print(f"  [ERROR] WiFi 심볼 생성 실패: {e}")

    def _create_battery_indicators(self):
        """배터리 상태 표시기 생성 (오른쪽만)"""
        try:
            # 배터리 아이콘 (오른쪽 상단)
            if self.is_charging:
                battery_icon = lv.SYMBOL.CHARGE
            elif self.battery_level > 75:
                battery_icon = lv.SYMBOL.BATTERY_FULL
            elif self.battery_level > 50:
                battery_icon = lv.SYMBOL.BATTERY_3
            elif self.battery_level > 25:
                battery_icon = lv.SYMBOL.BATTERY_2
            elif self.battery_level > 0:
                battery_icon = lv.SYMBOL.BATTERY_1
            else:
                battery_icon = lv.SYMBOL.BATTERY_EMPTY
        
            self.battery_icon_label = lv.label(self.main_container)
            self.battery_icon_label.set_text(battery_icon)
            self.battery_icon_label.align(lv.ALIGN.TOP_RIGHT, -30, -10)  # 원래 위치로 되돌림
            self.battery_icon_label.set_style_text_color(lv.color_hex(0x34C759), 0)
        
            # 배터리 텍스트 (오른쪽 상단, 아이콘 옆)
            self.battery_text_label = lv.label(self.main_container)
            self.battery_text_label.set_text("100%")  # 고정값으로 변경
            self.battery_text_label.align(lv.ALIGN.TOP_RIGHT, 11, -10)  # 오른쪽으로 16픽셀 이동 (-5 + 16 = 11)
            self.battery_text_label.set_style_text_align(lv.TEXT_ALIGN.RIGHT, 0)
            self.battery_text_label.set_style_text_color(lv.color_hex(0x34C759), 0)
            print("  [OK] 배터리 상태 표시기 생성 완료")
        except Exception as e:
            print(f"  [ERROR] 배터리 상태 표시기 생성 실패: {e}")

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
                schedule_item.align(lv.ALIGN.TOP_MID, 0, 20 + i * 18)
                schedule_item.set_style_bg_opa(0, 0)
                schedule_item.set_style_border_width(0, 0)
                
                # 스크롤바 완전 비활성화
                schedule_item.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
                schedule_item.set_scroll_dir(lv.DIR.NONE)
                
                # 시간과 아이콘을 하나의 라벨로 합쳐서 중앙 정렬
                combined_text = f"{schedule['time']} {status_icon}"
                combined_label = lv.label(schedule_item)
                combined_label.set_text(combined_text)
                combined_label.align(lv.ALIGN.CENTER, 0, 0)
                combined_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
                combined_label.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
                
                self.schedule_labels.append(combined_label)
            
        except Exception as e:
            print(f"  [ERROR] 복용 일정 영역 생성 실패: {e}")

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
        self.hints_text.set_text(f"A:{lv.SYMBOL.DOWNLOAD} B:{lv.SYMBOL.UP} C:{lv.SYMBOL.DOWN}")
        self.hints_text.align(lv.ALIGN.CENTER, 0, 0)  # 컨테이너 중앙에 배치
        self.hints_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.hints_text.set_style_text_color(lv.color_hex(0x8E8E93), 0)  # 모던 라이트 그레이
        # 기본 폰트는 자동으로 사용됨 (한글 폰트 적용 안함)

    def _create_basic_screen(self):
        """기본 화면 생성 (오류 시 대안)"""
        print(f"  [INFO] {self.screen_name} 기본 화면 생성 시작...")
        
        try:
            # 기본 화면 객체 생성
            self.screen_obj = lv.obj()
            self.screen_obj.set_size(160, 128)
            
            # 기본 라벨 생성
            self.title_label = lv.label(self.screen_obj)
            self.title_label.set_text("메인 화면")
            self.title_label.align(lv.ALIGN.CENTER, 0, 0)
            
            print("  [OK] 기본 화면 생성 완료")
            
        except Exception as e:
            print(f"  [ERROR] 기본 화면 생성 실패: {e}")
            # 최소한의 화면이라도 생성
            self.screen_obj = lv.obj()
            self.screen_obj.set_size(160, 128)

    def cleanup_unused_screens(self):
        """사용하지 않는 화면들 정리 (메모리 절약)"""
        try:
            if hasattr(self.screen_manager, 'cleanup_unused_screens'):
                deleted_count = self.screen_manager.cleanup_unused_screens()
                print(f"[INFO] 메인 화면에서 {deleted_count}개 화면 정리 완료")
                return deleted_count
            else:
                print("[WARN] ScreenManager에 cleanup_unused_screens 메서드가 없음")
            return 0
        except Exception as e:
            print(f"[ERROR] 화면 정리 실패: {e}")
            return 0

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
            print(f"  [ERROR] 일정 표시 업데이트 실패: {e}")
    
    def _update_status(self, status):
        """상태 업데이트"""
        try:
            self.status_text = status
            if hasattr(self, 'status_label'):
                self.status_label.set_text(status)
        except Exception as e:
            print(f"  [ERROR] 상태 업데이트 실패: {e}")
    
    
    def _init_motor_system(self):
        """모터 시스템 지연 초기화"""
        if self.motor_system is None:
            try:
                # 메모리 정리
                import gc
                gc.collect()
                print("  🧹 모터 시스템 초기화 전 메모리 정리 완료")
                
                # 실제 모터 시스템 초기화
                from motor_control import PillBoxMotorSystem
                self.motor_system = PillBoxMotorSystem()
                print("  [OK] 실제 모터 시스템 초기화 완료")
                
            except Exception as e:
                print(f"  [WARN] 실제 모터 시스템 초기화 실패, 재시도: {e}")
                try:
                    # 재시도
                    import gc
                    gc.collect()
                    from motor_control import PillBoxMotorSystem
                    self.motor_system = PillBoxMotorSystem()
                    print("  [OK] 실제 모터 시스템 재시도 초기화 완료")
                except Exception as e2:
                    print(f"  [ERROR] 실제 모터 시스템 초기화 최종 실패: {e2}")
                    # 모의 시스템 사용
                    self.motor_system = MockMotorSystem()
                    print("  [WARN] 모의 모터 시스템 사용")
        
        return self.motor_system
    
    def show(self):
        """화면 표시"""
        print(f"[INFO] {self.screen_name} UI 통합 모드 표시")
        
        if hasattr(self, 'screen_obj') and self.screen_obj:
            lv.screen_load(self.screen_obj)
            print(f"[OK] {self.screen_name} 화면 로드 완료")
            
            # 화면 강제 업데이트
            for i in range(3):
                lv.timer_handler()
                time.sleep(0.01)
            print(f"[OK] {self.screen_name} 화면 업데이트 완료")
            
            # 자동 배출 모니터링 시작
            self._start_auto_dispense_monitoring()
        else:
            print(f"[ERROR] {self.screen_name} 화면 객체가 없음")
    
    def hide(self):
        """화면 숨기기"""
        print(f"[INFO] {self.screen_name} 화면 숨기기")
        # 캐싱된 화면은 메모리에서 제거하지 않음
        pass
    
    def update(self):
        """화면 업데이트 (ScreenManager에서 주기적으로 호출)"""
        try:
            # 현재 시간 업데이트
            self._update_current_time()
            # 시간 표시 업데이트
            self._update_time_display()
            
            # 알약 개수 업데이트
            self._update_pill_count_display()
            
            # 자동 배출 시간 확인
            self._check_auto_dispense()
            
            # 약물 상태 모니터링
            self._check_medication_status()
            
            # 알람 시스템 모니터링
            self._check_alarm_system()
            
        except Exception as e:
            print(f"[ERROR] 메인 스크린 업데이트 실패: {e}")
    
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
                print("[OK] 현재 설정 저장 완료")
            else:
                print("[ERROR] 현재 설정 저장 실패")
            return success
            
        except Exception as e:
            print(f"[ERROR] 설정 저장 실패: {e}")
            return False
    
    def get_medication_summary(self):
        """약물 상태 요약 정보 반환"""
        try:
            summary = {
                "disk_counts": {
                    "1": self.data_manager.get_disk_count(1),
                    "2": self.data_manager.get_disk_count(2),
                    "3": self.data_manager.get_disk_count(3)
                },
                "low_stock_disks": [],
                "today_dispense_count": len(self.data_manager.get_today_dispense_logs())
            }
            
            # 부족한 디스크 확인
            for disk_num in [1, 2, 3]:
                if self.data_manager.is_disk_low_stock(disk_num):
                    summary["low_stock_disks"].append(disk_num)
            
            return summary
            
        except Exception as e:
            print(f"[ERROR] 약물 상태 요약 생성 실패: {e}")
            return None
    
    def _check_medication_status(self):
        """약물 상태 모니터링"""
        try:
            current_time = self._get_current_time()
            
            # 5분마다 약물 상태 확인
            if current_time == self.last_medication_check:
                return
            
            self.last_medication_check = current_time
            
            # 약물 상태 확인
            alerts = self.medication_tracker.check_low_stock_alerts()
            
            if alerts:
                self.medication_alerts = alerts
                self._handle_medication_alerts(alerts)
            else:
                self.medication_alerts = []
                
        except Exception as e:
            print(f"[ERROR] 약물 상태 모니터링 실패: {e}")
    
    def _handle_medication_alerts(self, alerts):
        """약물 알림 처리"""
        try:
            for alert in alerts:
                alert_type = alert.get("type", "unknown")
                disk_num = alert.get("disk", 0)
                message = alert.get("message", "")
                priority = alert.get("priority", "medium")
                
                if alert_type == "empty":
                    print(f"🚨 [CRITICAL] {message}")
                    self._update_status(f"디스크 {disk_num} 소진 - 즉시 충전!")
                elif alert_type == "critical":
                    print(f"⚠️ [HIGH] {message}")
                    self._update_status(f"디스크 {disk_num} 위험 수준!")
                elif alert_type == "low_stock":
                    print(f"📢 [MEDIUM] {message}")
                    self._update_status(f"디스크 {disk_num} 부족")
                
        except Exception as e:
            print(f"[ERROR] 약물 알림 처리 실패: {e}")
    
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
            print(f"[ERROR] 약물 상태 표시 정보 생성 실패: {e}")
            return "상태 확인 오류"
    
    def get_disk_count_display(self, disk_num):
        """디스크 수량 표시용 정보 반환"""
        try:
            count = self.data_manager.get_disk_count(disk_num)
            disk_info = self.medication_tracker.get_disk_medication_info(disk_num)
            disk_name = disk_info.get("name", f"디스크 {disk_num}") if disk_info else f"디스크 {disk_num}"
            
            return f"{disk_name}: {count}개"
            
        except Exception as e:
            print(f"[ERROR] 디스크 {disk_num} 수량 표시 정보 생성 실패: {e}")
            return f"디스크 {disk_num}: 확인 불가"
    
    def _check_alarm_system(self):
        """알람 시스템 모니터링"""
        try:
            # 재알람 확인 (매번 호출)
            self.alarm_system.check_reminder_alarms()
            
            # 활성 알람 상태 확인
            active_alarms = self.alarm_system.get_active_alarms()
            if active_alarms:
                self._handle_active_alarms(active_alarms)
            
            # 알람 실패 확인 및 일정 상태 업데이트
            self._check_alarm_failures()
                
        except Exception as e:
            print(f"[ERROR] 알람 시스템 모니터링 실패: {e}")
    
    def _check_alarm_failures(self):
        """알람 실패 확인 및 일정 상태 업데이트"""
        try:
            # 알람 히스토리에서 최근 실패 기록 확인
            alarm_history = self.alarm_system.get_alarm_history()
            
            for record in alarm_history[-10:]:  # 최근 10개 기록만 확인
                if record.get("action") == "dispense_failed":
                    dose_index = record.get("dose_index")
                    meal_name = record.get("meal_name", f"일정 {dose_index + 1}")
                    
                    # 해당 일정의 상태를 "failed"로 업데이트
                    if dose_index < len(self.dose_schedule):
                        if self.dose_schedule[dose_index]["status"] != "failed":
                            self.dose_schedule[dose_index]["status"] = "failed"
                            print(f"❌ 일정 상태 업데이트: {meal_name} → 실패")
                            
                            # UI 업데이트
                            self._update_schedule_display()
                            
        except Exception as e:
            print(f"[ERROR] 알람 실패 확인 실패: {e}")
    
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
            print(f"[ERROR] 활성 알람 처리 실패: {e}")
    
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
            print(f"[ERROR] 알람 상태 표시 정보 생성 실패: {e}")
            return "알람 상태 확인 오류"
    
    def _update_current_time(self):
        """현재 시간 업데이트 (WiFi 매니저 사용)"""
        try:
            # WiFi 매니저에서 한국 시간 가져오기
            if get_wifi_manager().is_connected and get_wifi_manager().time_synced:
                kst_time = get_wifi_manager().get_kst_time()
                hour = kst_time[3]
                minute = kst_time[4]
                self.current_time = f"{hour:02d}:{minute:02d}"
                self.wifi_status = {"connected": True, "ssid": get_wifi_manager().connected_ssid}
            else:
                # WiFi 연결이 없으면 RTC 사용
                current = self.rtc.datetime()
                hour = current[4]
                minute = current[5]
                self.current_time = f"{hour:02d}:{minute:02d}"
                self.wifi_status = {"connected": False, "ssid": None}
        except Exception as e:
            print(f"  [ERROR] 현재 시간 업데이트 실패: {e}")
            self.current_time = "00:00"
    
    def _update_time_display(self):
        """시간 표시 업데이트"""
        try:
            if hasattr(self, 'current_time_label'):
                self.current_time_label.set_text(self.current_time)
        except Exception as e:
            print(f"  [ERROR] 시간 표시 업데이트 실패: {e}")
    
    def _update_pill_count_display(self):
        """알약 개수 표시 업데이트"""
        try:
            if hasattr(self, 'pill_count_label') and self.pill_count_label:
                # 현재 선택된 복용 일정의 디스크에서 알약 개수 가져오기
                if self.current_dose_index < len(self.dose_schedule):
                    current_dose = self.dose_schedule[self.current_dose_index]
                    disk_num = current_dose.get('disk', self.current_dose_index + 1)
                    
                    # 디스크의 현재 개수와 최대 용량 가져오기
                    current_count = self.data_manager.get_disk_count(disk_num)
                    max_capacity = 15  # 디스크당 최대 15칸
                    
                    # 표시 텍스트 업데이트
                    count_text = f"{current_count}/{max_capacity}"
                    self.pill_count_label.set_text(count_text)
                    
                    # 개수에 따른 색상 변경
                    if current_count <= 1:
                        # 위험 (빨간색)
                        self.pill_count_label.set_style_text_color(lv.color_hex(0xFF3B30), 0)
                    elif current_count <= 3:
                        # 부족 (주황색)
                        self.pill_count_label.set_style_text_color(lv.color_hex(0xFF9500), 0)
                    else:
                        # 충분 (초록색)
                        self.pill_count_label.set_style_text_color(lv.color_hex(0x34C759), 0)
                        
        except Exception as e:
            print(f"  [ERROR] 알약 개수 표시 업데이트 실패: {e}")
    
    def on_button_a(self):
        """버튼 A - 배출"""
        print("🔵 버튼 A: 배출")
        
        try:
            # 활성 알람이 있는지 확인
            active_alarms = self.alarm_system.get_active_alarms()
            
            if active_alarms:
                # 활성 알람이 있으면 배출 트리거
                print("🔔 활성 알람 감지 - 배출 트리거")
                self._trigger_dispense_from_alarm()
            else:
                # 활성 알람이 없으면 수동 배출 실행
                print("🔵 수동 배출 실행")
                self._update_status("수동 배출 중...")
                
                try:
                    motor_system = self._init_motor_system()
                    
                    print(f"  [RETRY] 수동 배출 시퀀스 시작: 일정 {self.current_dose_index + 1}")
                    
                    required_disks = self._get_selected_disks_for_dose(self.current_dose_index)
                    print(f"  [INFO] 선택된 디스크들: {required_disks}")
                    
                    print(f"  📋 필요한 디스크: {required_disks}")
                    
                    success = self._dispense_from_selected_disks(motor_system, required_disks)
                    
                    if success:
                        print(f"  [OK] 모든 디스크 배출 완료")
                        self._update_status("배출 완료")
                        
                        self.dose_schedule[self.current_dose_index]["status"] = "completed"
                        
                        self.data_manager.log_dispense(self.current_dose_index, True)
                        
                        self.alarm_system.confirm_dispense(self.current_dose_index)
                        
                        self._decrease_selected_disks_count(self.current_dose_index)
                        
                        self._update_schedule_display()
                        
                        print(f"[OK] 수동 배출 성공: 일정 {self.current_dose_index + 1}")
                    else:
                        print(f"  [ERROR] 배출 실패")
                        self._update_status("배출 실패")
                    
                except Exception as e:
                    self._update_status("수동 배출 실패")
                    print(f"[ERROR] 수동 배출 실패: {e}")
                
        except Exception as e:
            print(f"[ERROR] 버튼 A 처리 실패: {e}")
            self._update_status("버튼 A 처리 실패")
    
    def _trigger_dispense_from_alarm(self):
        """알람에서 배출 트리거"""
        try:
            active_alarms = self.alarm_system.get_active_alarms()
            
            if not active_alarms:
                print("[WARN] 활성 알람이 없습니다")
                return
            
            # 첫 번째 활성 알람의 일정 인덱스 사용
            dose_index = list(active_alarms.keys())[0]
            alarm_info = active_alarms[dose_index]
            
            print(f"🔔 알람 배출 트리거: {alarm_info['meal_name']} (일정 {dose_index + 1})")
            
            # 알람 확인 처리
            self.alarm_system.confirm_dispense(dose_index)
            
            # 배출 시퀀스 실행
            self._update_status("알람 배출 중...")
            success = self._execute_dispense_sequence(dose_index)
            
            if success:
                print(f"[OK] 알람 배출 성공: {alarm_info['meal_name']}")
                self._update_status("알람 배출 완료")
            else:
                print(f"[ERROR] 알람 배출 실패: {alarm_info['meal_name']}")
                self._update_status("알람 배출 실패")
                
        except Exception as e:
            print(f"[ERROR] 알람 배출 트리거 실패: {e}")
            self._update_status("알람 배출 실패")
    
    def _execute_dispense_sequence(self, dose_index):
        """배출 시퀀스 실행 (기존 자동 배출 로직 재사용)"""
        try:
            print(f"🔔 알람 배출 시퀀스 시작: 일정 {dose_index + 1}")
            
            # 기존 자동 배출 메서드 재사용
            self._execute_auto_dispense(dose_index)
            
            # 배출 성공 여부 확인 (일정 상태로 판단)
            if dose_index < len(self.dose_schedule):
                if self.dose_schedule[dose_index]["status"] == "completed":
                    print(f"[OK] 알람 배출 성공: 일정 {dose_index + 1}")
                    return True
                else:
                    print(f"[ERROR] 알람 배출 실패: 일정 {dose_index + 1}")
                    return False
            else:
                print(f"[ERROR] 잘못된 일정 인덱스: {dose_index}")
                return False
                
        except Exception as e:
            print(f"[ERROR] 알람 배출 시퀀스 실행 실패: {e}")
            return False
    
    def on_button_b(self):
        """버튼 B - 위로 (이전 일정으로 이동)"""
        print("🔴 버튼 B: 위로")
        
        try:
            # 이전 일정으로 이동
            self.current_dose_index = (self.current_dose_index - 1) % len(self.dose_schedule)
            self._update_schedule_display()
            self._update_status(f"일정 {self.current_dose_index + 1} 선택")
            print(f"[OK] 이전 일정으로 이동: {self.current_dose_index + 1}")
        except Exception as e:
            print(f"[ERROR] 일정 이동 실패: {e}")
            self._update_status("일정 이동 실패")
    
    def on_button_c(self):
        """버튼 C - 아래 (다음 일정으로 이동)"""
        print("🟡 버튼 C: 아래")
        
        try:
            # 다음 일정으로 이동
            self.current_dose_index = (self.current_dose_index + 1) % len(self.dose_schedule)
            self._update_schedule_display()
            self._update_status(f"일정 {self.current_dose_index + 1} 선택")
            print(f"[OK] 다음 일정으로 이동: {self.current_dose_index + 1}")
        except Exception as e:
            print(f"[ERROR] 일정 이동 실패: {e}")
            self._update_status("일정 이동 실패")
    
    def on_button_d(self):
        """버튼 D - 고급 설정 화면으로 전환"""
        print("🟢 버튼 D: 고급 설정 화면으로 전환")
        
        try:
            self.screen_manager.show_screen("advanced_settings")
            print("[OK] 고급 설정 화면으로 전환")
        except Exception as e:
            print(f"[ERROR] 고급 설정 화면 전환 실패: {e}")
            self._update_status("고급 설정 화면 전환 실패")
            
    
    def on_show(self):
        """화면이 표시될 때 호출"""
        pass
    
    def on_hide(self):
        """화면이 숨겨질 때 호출"""
        pass
    
    def get_title(self):
        """화면 제목"""
        return "메인 화면"
    
    def get_button_hints(self):
        """버튼 힌트"""
        return "A:UP  B:DOWN  C:DOWNLOAD  D:SETTINGS"
    
    def get_voice_file(self):
        """안내 음성 파일"""
        return "wav_main_screen.wav"
    
    def get_effect_file(self):
        """효과음 파일"""
        return "wav_select.wav"
    
    def _start_auto_dispense_monitoring(self):
        """자동 배출 모니터링 시작"""
        print("🕐 자동 배출 모니터링 시작")
        self._update_status("자동 배출 모니터링 중...")
    
    def _get_current_time(self):
        """현재 시간 가져오기 (WiFi 우선, RTC 백업)"""
        try:
            # WiFi 매니저에서 한국 시간 가져오기
            if get_wifi_manager().is_connected and get_wifi_manager().time_synced:
                kst_time = get_wifi_manager().get_kst_time()
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
            print(f"[ERROR] 현재 시간 가져오기 실패: {e}")
            return "00:00"
    
    
    def _check_auto_dispense(self):
        """자동 배출 시간 확인"""
        if not self.auto_dispense_enabled:
            return
        
        try:
            current_time = self._get_current_time()
            
            # 시간이 변경되었을 때만 확인
            if current_time == self.last_check_time:
                return
            
            self.last_check_time = current_time
            print(f"🕐 시간 확인: {current_time}")
            
            # 각 일정 확인
            for i, schedule in enumerate(self.dose_schedule):
                if schedule["status"] == "pending" and schedule["time"] == current_time:
                    # 데이터 매니저를 사용하여 같은 시간에 배출 여부 확인
                    if self.data_manager.was_dispensed_today(i, schedule['time']):
                        print(f"⏭️ 일정 {i+1} ({schedule['time']}) 이미 같은 시간에 배출됨")
                        continue
                    
                    print(f"⏰ 알람 트리거: 일정 {i+1} ({schedule['time']})")
                    
                    # 알람만 트리거 (A버튼을 기다림)
                    meal_name = schedule.get('meal_name', f'일정 {i+1}')
                    self.alarm_system.trigger_dose_alarm(i, schedule['time'], meal_name)
                    
                    # 자동 배출은 하지 않고 알람만 발생
                    print(f"🔔 알람 발생: A버튼을 눌러 복용하세요")
                    break
                    
        except Exception as e:
            print(f"[ERROR] 자동 배출 확인 실패: {e}")
    
    def _execute_auto_dispense(self, dose_index):
        """자동 배출 실행"""
        try:
            print(f"🤖 자동 배출 시작: 일정 {dose_index + 1}")
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
                
                # 선택된 디스크들의 약물 수량 감소
                self._decrease_selected_disks_count(dose_index)
                
                self._update_status("자동 배출 완료")
                print(f"[OK] 자동 배출 성공: 일정 {dose_index + 1}")
            else:
                # 배출 실패 시 상태 업데이트
                self.dose_schedule[dose_index]["status"] = "failed"
                
                # 데이터 매니저에 배출 실패 기록 저장
                self.data_manager.log_dispense(dose_index, False)
                
                self._update_status("자동 배출 실패")
                print(f"[ERROR] 자동 배출 실패: 일정 {dose_index + 1}")
            
            # UI 업데이트
            self._update_schedule_display()
            
        except Exception as e:
            print(f"[ERROR] 자동 배출 실행 실패: {e}")
            self._update_status("자동 배출 오류")
    
    def _decrease_selected_disks_count(self, dose_index):
        """선택된 디스크들의 약물 수량 감소"""
        try:
            # dose_time_screen에서 복용 시간 정보 가져오기
            dose_times = []
            if hasattr(self.screen_manager, 'screens') and 'dose_time' in self.screen_manager.screens:
                dose_time_screen = self.screen_manager.screens['dose_time']
                if hasattr(dose_time_screen, 'get_dose_times'):
                    dose_times = dose_time_screen.get_dose_times()
            
            if dose_times and dose_index < len(dose_times):
                dose_info = dose_times[dose_index]
                selected_disks = dose_info.get('selected_disks', [dose_index + 1])  # 기본값: 해당 일정의 디스크
                
                print(f"[INFO] 선택된 디스크들: {selected_disks}")
                
                # 각 디스크의 약물 수량 감소
                for disk_num in selected_disks:
                    current_count = self.data_manager.get_disk_count(disk_num)
                    if current_count > 0:
                        new_count = current_count - 1
                        self.data_manager.update_disk_count(disk_num, new_count)
                        print(f"[INFO] 디스크 {disk_num} 약물 수량: {current_count} → {new_count}")
                    else:
                        print(f"[WARN] 디스크 {disk_num} 약물 수량이 0입니다")
            else:
                # 기본 로직: 해당 일정의 디스크만 감소
                disk_num = dose_index + 1
                current_count = self.data_manager.get_disk_count(disk_num)
                if current_count > 0:
                    new_count = current_count - 1
                    self.data_manager.update_disk_count(disk_num, new_count)
                    print(f"[INFO] 디스크 {disk_num} 약물 수량: {current_count} → {new_count}")
                
        except Exception as e:
            print(f"[ERROR] 선택된 디스크 수량 감소 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _get_selected_disks_for_dose(self, dose_index):
        """복용 일정에 대한 선택된 디스크들 반환"""
        try:
            # dose_time_screen에서 복용 시간 정보 가져오기
            dose_times = []
            if hasattr(self.screen_manager, 'screens') and 'dose_time' in self.screen_manager.screens:
                dose_time_screen = self.screen_manager.screens['dose_time']
                if hasattr(dose_time_screen, 'get_dose_times'):
                    dose_times = dose_time_screen.get_dose_times()
            
            if dose_times and dose_index < len(dose_times):
                dose_info = dose_times[dose_index]
                selected_disks = dose_info.get('selected_disks', [dose_index + 1])  # 기본값: 해당 일정의 디스크
                return selected_disks
            else:
                # 기본 로직: 해당 일정의 디스크만 반환
                return [dose_index + 1]
                
        except Exception as e:
            print(f"[ERROR] 선택된 디스크 가져오기 실패: {e}")
            # 오류 시 기본값 반환
            return [dose_index + 1]
    
    def _dispense_from_selected_disks(self, motor_system, selected_disks):
        """선택된 디스크들에서 순차적으로 배출"""
        try:
            print(f"[INFO] 선택된 디스크들 순차 배출 시작: {selected_disks}")
            
            for i, disk_num in enumerate(selected_disks):
                print(f"[INFO] 디스크 {disk_num} 배출 중... ({i+1}/{len(selected_disks)})")
                self._update_status(f"디스크 {disk_num} 배출 중...")
                
                # 1. 디스크 회전
                disk_success = motor_system.rotate_disk(disk_num, 1)  # 1칸만 회전
                if not disk_success:
                    print(f"[ERROR] 디스크 {disk_num} 회전 실패")
                    return False
                
                # 2. 배출구 열림 (디스크별 단계)
                open_success = motor_system.control_motor3_direct(disk_num)  # 디스크 번호 = 단계
                if not open_success:
                    print(f"[ERROR] 디스크 {disk_num} 배출구 열림 실패")
                    return False
                
                # 3. 약이 떨어질 시간 대기
                import time
                time.sleep(2)  # 2초 대기
                
                print(f"[OK] 디스크 {disk_num} 배출 완료")
                
                # 마지막 디스크가 아니면 잠시 대기
                if i < len(selected_disks) - 1:
                    time.sleep(1)  # 1초 간격
            
            print(f"[OK] 모든 디스크 배출 완료: {selected_disks}")
            return True
            
        except Exception as e:
            print(f"[ERROR] 선택된 디스크 배출 실패: {e}")
            import sys
            sys.print_exception(e)
            return False
    
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
                        
                        schedule_text = f"{schedule['time']} {status_icon}"
                        schedule_label.set_text(schedule_text)
                        print(f"  [INFO] 일정 {i+1} 업데이트: {schedule_text}")
        except Exception as e:
            print(f"  [ERROR] 일정 표시 업데이트 실패: {e}")


class MockMotorSystem:
    """모의 모터 시스템"""
    
    def __init__(self):
        self.motor_controller = MockMotorController()
        print("[OK] MockMotorSystem 초기화 완료")
    
    def control_dispense_slide(self, level):
        """모의 배출구 슬라이드 제어"""
        print(f"🚪 모의 배출구 슬라이드 {level}단 (120도)")
        return True
    
    def rotate_disk(self, disk_num, steps):
        """모의 디스크 회전"""
        print(f"[RETRY] 모의 디스크 {disk_num} 회전: {steps} 스텝")
        return True


class MockMotorController:
    """모의 모터 컨트롤러"""
    
    def __init__(self):
        self.motor_states = [0, 0, 0, 0]
        self.motor_steps = [0, 0, 0, 0]
        self.motor_positions = [0, 0, 0, 0]
        print("[OK] MockMotorController 초기화 완료")
    
    def test_motor_simple(self, motor_index, steps):
        """모의 모터 간단 테스트"""
        print(f"🧪 모의 모터 {motor_index} 간단 테스트 시작 ({steps}스텝)")
        print(f"[OK] 모의 모터 {motor_index} 테스트 성공")
        return True
    
    def test_motor3_only(self, steps=50):
        """모터 3 전용 테스트 (모의)"""
        print(f"🧪 모의 모터 3 전용 테스트 시작 ({steps}스텝)")
        print("[OK] 모의 모터 3 테스트 성공")
        return True
