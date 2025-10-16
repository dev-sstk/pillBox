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
from wifi_manager import wifi_manager

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
        
        # 시간 모니터링 (자동 배출용)
        self.last_check_time = ""
        self.auto_dispense_enabled = True
        self.last_dispense_time = {}  # 각 일정별 마지막 배출 시간 기록
        
        # 샘플 데이터 초기화
        self._init_sample_data()
        
        # Modern 화면 생성
        self._create_modern_screen()
        
        print(f"✅ {self.screen_name} 화면 초기화 완료")
    
    def _init_sample_data(self):
        """샘플 데이터 초기화 - dose_time_screen에서 설정한 시간 가져오기"""
        # NTP 시간을 활용한 현재 날짜 가져오기 (RTC 백업 포함)
        try:
            # WiFi 매니저에서 한국 시간 가져오기
            if hasattr(self, 'wifi_manager') and self.wifi_manager and self.wifi_manager.is_connected and self.wifi_manager.time_synced:
                kst_time = self.wifi_manager.get_kst_time()
                year, month, day, hour, minute, second = kst_time[:6]
                print(f"  📅 NTP 시간으로 날짜 설정: {year}년 {month}월 {day}일 {hour}:{minute:02d}:{second:02d}")
                
                # NTP 시간을 RTC에 백업 저장 (외부 배터리 활용)
                from machine import RTC
                rtc = RTC()
                # RTC는 (year, month, day, weekday, hour, minute, second, microsecond) 형식
                weekday = (day - 1) % 7  # 간단한 요일 계산 (0=월요일)
                rtc.datetime((year, month, day, weekday, hour, minute, second, 0))
                print("  💾 NTP 시간을 RTC에 백업 저장 완료")
                
            else:
                # NTP가 없으면 RTC 백업 시간 사용 (외부 배터리로 유지됨)
                from machine import RTC
                rtc = RTC()
                year, month, day = rtc.datetime()[:3]
                print(f"  📅 RTC 백업 시간으로 날짜 설정: {year}년 {month}월 {day}일 (외부 배터리)")
                
        except Exception as e:
            # 오류 시 기본값 사용
            month, day = 12, 25
            print(f"  ⚠️ 날짜 설정 오류, 기본값 사용: {month}월 {day}일 ({e})")
        
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
                        print(f"  📱 dose_time_screen에서 설정한 시간 가져옴: {dose_times}")
                    else:
                        # 설정된 시간이 없으면 기본값 사용
                        self.dose_schedule = [
                            {"time": "08:00", "status": "pending"},
                            {"time": "12:00", "status": "pending"},
                            {"time": "18:00", "status": "pending"}
                        ]
                        print("  📱 설정된 시간 없음, 기본값 사용")
                else:
                    # get_dose_times 메서드가 없으면 기본값 사용
                    self.dose_schedule = [
                        {"time": "08:00", "status": "pending"},
                        {"time": "12:00", "status": "pending"},
                        {"time": "18:00", "status": "pending"}
                    ]
                    print("  📱 dose_time_screen 메서드 없음, 기본값 사용")
            else:
                # dose_time_screen이 없으면 기본값 사용
                self.dose_schedule = [
                    {"time": "08:00", "status": "pending"},
                    {"time": "12:00", "status": "pending"},
                    {"time": "18:00", "status": "pending"}
                ]
                print("  📱 dose_time_screen 없음, 기본값 사용")
        except Exception as e:
            # 오류 시 기본값 사용
            self.dose_schedule = [
                {"time": "08:00", "status": "pending"},
                {"time": "12:00", "status": "pending"},
                {"time": "18:00", "status": "pending"}
            ]
            print(f"  ⚠️ dose_time_screen에서 시간 가져오기 실패, 기본값 사용: {e}")
        
        self.current_date = f"{year}-{month:02d}-{day:02d}"
    
    def _create_modern_screen(self):
        """Modern 스타일 화면 생성"""
        print(f"  📱 {self.screen_name} Modern 화면 생성 시작...")
        
        try:
            # 메모리 정리
            import gc
            gc.collect()
            print("  ✅ 메모리 정리 완료")
            
            # 화면 생성
            print("  📱 화면 객체 생성...")
            self.screen_obj = lv.obj()
            print(f"  📱 화면 객체 생성됨: {self.screen_obj}")
            
            # 화면 배경 스타일 적용 (Modern 스타일)
            self.ui_style.apply_screen_style(self.screen_obj)
            
            # 스크롤바 완전 비활성화
            self.screen_obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.screen_obj.set_scroll_dir(lv.DIR.NONE)
            
            print("  ✅ 화면 배경 설정 완료")
            
            # 화면 크기 설정
            self.screen_obj.set_size(160, 128)
            print("  📱 화면 크기: 160x128")
            
            # 메인 컨테이너 생성
            print("  📱 메인 컨테이너 생성 시도...")
            self.main_container = lv.obj(self.screen_obj)
            self.main_container.set_size(160, 128)
            self.main_container.align(lv.ALIGN.CENTER, 0, 0)
            self.main_container.set_style_bg_opa(0, 0)  # 투명 배경
            self.main_container.set_style_border_width(0, 0)  # 테두리 없음
            
            # 스크롤바 완전 비활성화
            self.main_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.main_container.set_scroll_dir(lv.DIR.NONE)
            
            print("  📱 메인 컨테이너 생성 완료")
            
            # 제목 영역 생성
            print("  📱 제목 영역 생성 시도...")
            self._create_title_area()
            print("  📱 제목 영역 생성 완료")
            
            # 복용 일정 영역 생성
            print("  📱 복용 일정 영역 생성 시도...")
            self._create_schedule_area()
            print("  📱 복용 일정 영역 생성 완료")
            
            # 하단 버튼 힌트 영역 생성
            print("  📱 버튼 힌트 영역 생성 시도...")
            self._create_button_hints_area()
            print("  📱 버튼 힌트 영역 생성 완료")
            
            print("  ✅ Modern 화면 생성 완료")
            
        except Exception as e:
            print(f"  ❌ Modern 화면 생성 중 오류 발생: {e}")
            import sys
            sys.print_exception(e)
            # 기본 화면 생성 시도
            print(f"  📱 {self.screen_name} 기본 화면 생성 시도...")
            try:
                self._create_basic_screen()
                print(f"  ✅ {self.screen_name} 기본 화면 초기화 완료")
            except Exception as e2:
                print(f"  ❌ {self.screen_name} 기본 화면 초기화도 실패: {e2}")
                import sys
                sys.print_exception(e2)
    
    def _create_optimized_ui(self):
        """메모리 최적화된 UI 생성"""
        try:
            # 메모리 정리
            import gc
            gc.collect()
            print("  🧹 UI 생성 전 메모리 정리 완료")
            
            # 화면 생성
            self.screen_obj = lv.obj()
            self.screen_obj.set_size(160, 128)
            print("  📱 화면 객체 생성 완료")
            
            # 제목 제거됨
            
            # 상태 표시
            self.status_label = lv.label(self.screen_obj)
            self.status_label.set_text(self.status_text)
            self.status_label.align(lv.ALIGN.CENTER, 0, -10)
            self.status_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            print("  📱 상태 표시 생성 완료")
            
            # 복용 일정 표시
            self.schedule_label = lv.label(self.screen_obj)
            self._update_schedule_display()
            self.schedule_label.align(lv.ALIGN.CENTER, 0, 10)
            self.schedule_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            print("  📱 일정 표시 생성 완료")
            
            # 버튼 힌트
            self.hints_label = lv.label(self.screen_obj)
            self.hints_label.set_text("A:이전 B:다음 C:리셋 D:배출")
            self.hints_label.align(lv.ALIGN.BOTTOM_MID, 0, -5)
            self.hints_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            print("  📱 버튼 힌트 생성 완료")
            
            print("  ✅ 최적화된 UI 생성 완료")
            
        except Exception as e:
            print(f"  ❌ UI 생성 실패: {e}")
            # 최소한의 UI라도 생성
            self.screen_obj = lv.obj()
            self.screen_obj.set_size(160, 128)
            
            self.title_label = lv.label(self.screen_obj)
            self.title_label.set_text("필박스")
            self.title_label.align(lv.ALIGN.CENTER, 0, 0)
    
    def _update_schedule_display(self):
        """복용 일정 표시 업데이트"""
        try:
            if hasattr(self, 'schedule_label') and self.dose_schedule:
                current_schedule = self.dose_schedule[self.current_dose_index]
                status_icon = "⏰" if current_schedule["status"] == "pending" else "✅"
                schedule_text = f"{status_icon} {current_schedule['time']}"
                self.schedule_label.set_text(schedule_text)
        except Exception as e:
            print(f"  ❌ 일정 표시 업데이트 실패: {e}")
    
    def _update_status(self, status):
        """상태 업데이트"""
        try:
            self.status_text = status
            if hasattr(self, 'status_label'):
                self.status_label.set_text(status)
        except Exception as e:
            print(f"  ❌ 상태 업데이트 실패: {e}")
    
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
                print("  ✅ 실제 모터 시스템 초기화 완료")
                
            except Exception as e:
                print(f"  ⚠️ 실제 모터 시스템 초기화 실패, 재시도: {e}")
                try:
                    # 재시도
                    import gc
                    gc.collect()
                    from motor_control import PillBoxMotorSystem
                    self.motor_system = PillBoxMotorSystem()
                    print("  ✅ 실제 모터 시스템 재시도 초기화 완료")
                except Exception as e2:
                    print(f"  ❌ 실제 모터 시스템 초기화 최종 실패: {e2}")
                    # 모의 시스템 사용
                    self.motor_system = MockMotorSystem()
                    print("  ⚠️ 모의 모터 시스템 사용")
        
        return self.motor_system
    
    def show(self):
        """화면 표시"""
        print(f"📱 {self.screen_name} UI 통합 모드 표시")
        
        if hasattr(self, 'screen_obj') and self.screen_obj:
            lv.screen_load(self.screen_obj)
            print(f"✅ {self.screen_name} 화면 로드 완료")
            
            # 화면 강제 업데이트
            for i in range(3):
                lv.timer_handler()
                time.sleep(0.01)
            print(f"✅ {self.screen_name} 화면 업데이트 완료")
            
            # 자동 배출 모니터링 시작
            self._start_auto_dispense_monitoring()
        else:
            print(f"❌ {self.screen_name} 화면 객체가 없음")
    
    def hide(self):
        """화면 숨기기"""
        print(f"📱 {self.screen_name} 화면 숨기기")
        # 캐싱된 화면은 메모리에서 제거하지 않음
        pass
    
    def update(self):
        """화면 업데이트 (ScreenManager에서 주기적으로 호출)"""
        try:
            # 현재 시간 업데이트
            self._update_current_time()
            # 시간 표시 업데이트
            self._update_time_display()
            
        except Exception as e:
            print(f"❌ 메인 스크린 업데이트 실패: {e}")
    
    def _update_current_time(self):
        """현재 시간 업데이트 (WiFi 매니저 사용)"""
        try:
            # WiFi 매니저에서 한국 시간 가져오기
            if wifi_manager.is_connected and wifi_manager.time_synced:
                kst_time = wifi_manager.get_kst_time()
                hour = kst_time[3]
                minute = kst_time[4]
                self.current_time = f"{hour:02d}:{minute:02d}"
                self.wifi_status = {"connected": True, "ssid": wifi_manager.connected_ssid}
            else:
                # WiFi 연결이 없으면 RTC 사용
                current = self.rtc.datetime()
                hour = current[4]
                minute = current[5]
                self.current_time = f"{hour:02d}:{minute:02d}"
                self.wifi_status = {"connected": False, "ssid": None}
        except Exception as e:
            print(f"  ❌ 현재 시간 업데이트 실패: {e}")
            self.current_time = "00:00"
    
    def _update_time_display(self):
        """시간 표시 업데이트"""
        try:
            if hasattr(self, 'current_time_label'):
                self.current_time_label.set_text(self.current_time)
        except Exception as e:
            print(f"  ❌ 시간 표시 업데이트 실패: {e}")
    
    def on_button_a(self):
        """버튼 A - 이전 일정 (일정 3 -> 2 -> 1 순서)"""
        print("🔵 버튼 A: 이전 일정")
        
        if self.current_dose_index > 0:
            self.current_dose_index -= 1
            self._update_schedule_display()
            self._update_status(f"일정 {self.current_dose_index + 1} 선택")
            print(f"  📱 현재 일정: {self.current_dose_index + 1}")
        else:
            self._update_status("첫 번째 일정")
            print("  📱 이미 첫 번째 일정")
    
    def on_button_b(self):
        """버튼 B - 다음 일정 (일정 1 -> 2 -> 3 순서)"""
        print("🔴 버튼 B: 다음 일정")
        
        if self.current_dose_index < len(self.dose_schedule) - 1:
            self.current_dose_index += 1
            self._update_schedule_display()
            self._update_status(f"일정 {self.current_dose_index + 1} 선택")
            print(f"  📱 현재 일정: {self.current_dose_index + 1}")
        else:
            self._update_status("마지막 일정")
            print("  📱 이미 마지막 일정")
    
    def on_button_c(self):
        """버튼 C - 수동 알약 배출"""
        print("🟡 버튼 C: 수동 알약 배출")
        
        # D 버튼과 동일한 배출 로직 실행
        self._update_status("수동 배출 중...")
        
        try:
            # 모터 시스템 초기화
            motor_system = self._init_motor_system()
            
            # 배출 시퀀스 실행
            print(f"  🔄 수동 배출 시퀀스 시작: 일정 {self.current_dose_index + 1}")
            
            # 필요한 디스크 결정 (간단한 로직)
            required_disks = [1]  # 첫 번째 일정은 디스크 1만 사용
            
            print(f"  📋 필요한 디스크: {required_disks}")
            
            # 1. 디스크 1 회전 (리미트스위치 기반)
            print("  🔄 디스크 1 회전 (리미트스위치 기반)")
            self._update_status("디스크 회전 중...")
            disk_success = motor_system.rotate_disk(1, 1)  # 1칸만 회전
            
            if disk_success:
                print("  ✅ 디스크 1 회전 완료")
                self._update_status("디스크 회전 완료")
                
                # 2. 배출구 열림 (슬라이드 1단계) - 블로킹 모드
                print("  🔧 배출구 열림 (슬라이드 1단계) - 블로킹 모드")
                # UI 업데이트 제거 - 모터 동작 중에는 UI 업데이트 하지 않음
                open_success = motor_system.control_motor3_direct(1)  # 모터 3 배출구 1단계 (블로킹)
                
                if open_success:
                    print("  ✅ 배출구 열림 완료")
                    # 모터 동작 완료 후에만 UI 업데이트
                    self._update_status("배출구 열림 완료")
                    
                    # 약이 떨어질 시간 대기
                    import time
                    time.sleep(2)  # 2초 대기
                    
                    # 3. 배출구 닫힘은 자동으로 처리됨 (control_motor3_direct 내부에서)
                    print("  ✅ 배출구 닫힘 완료 (자동 처리)")
                    # 모터 동작 완료 후에만 UI 업데이트
                    self._update_status("수동 배출 완료")
                    
                    # 일정 상태 업데이트
                    self.dose_schedule[self.current_dose_index]["status"] = "completed"
                    self._update_schedule_display(self.current_dose_index)  # 특정 일정만 업데이트
                    
                    print(f"✅ 수동 배출 성공: 일정 {self.current_dose_index + 1}")
                else:
                    print("  ❌ 배출구 열림 실패")
                    self._update_status("배출구 열림 실패")
            else:
                print("  ❌ 디스크 1 회전 실패")
                self._update_status("디스크 회전 실패")
            
        except Exception as e:
            self._update_status("수동 배출 실패")
            print(f"❌ 수동 배출 실패: {e}")
    
    def on_button_d(self):
        """버튼 D - 배출 실행"""
        print("🟢 버튼 D: 배출 실행")
        self._update_status("배출 중...")
        
        try:
            # 모터 시스템 초기화
            motor_system = self._init_motor_system()
            
            # 배출 시퀀스 실행
            print(f"  🔄 배출 시퀀스 시작: 일정 {self.current_dose_index + 1}")
            
            # 필요한 디스크 결정 (간단한 로직)
            required_disks = [1]  # 첫 번째 일정은 디스크 1만 사용
            
            print(f"  📋 필요한 디스크: {required_disks}")
            
            # 1. 디스크 1 회전 (리미트스위치 기반)
            print("  🔄 디스크 1 회전 (리미트스위치 기반)")
            self._update_status("디스크 회전 중...")
            disk_success = motor_system.rotate_disk(1, 1)  # 1칸만 회전
            
            if disk_success:
                print("  ✅ 디스크 1 회전 완료")
                self._update_status("디스크 회전 완료")
                
                # 2. 배출구 열림 (슬라이드 1단계) - 블로킹 모드
                print("  🔧 배출구 열림 (슬라이드 1단계) - 블로킹 모드")
                # UI 업데이트 제거 - 모터 동작 중에는 UI 업데이트 하지 않음
                open_success = motor_system.control_motor3_direct(1)  # 모터 3 배출구 1단계 (블로킹)
                
                if open_success:
                    print("  ✅ 배출구 열림 완료")
                    # 모터 동작 완료 후에만 UI 업데이트
                    self._update_status("배출구 열림 완료")
                    
                    # 약이 떨어질 시간 대기
                    import time
                    time.sleep(2)  # 2초 대기
                    
                    # 3. 배출구 닫힘은 자동으로 처리됨 (control_motor3_direct 내부에서)
                    print("  ✅ 배출구 닫힘 완료 (자동 처리)")
                    # 모터 동작 완료 후에만 UI 업데이트
                    self._update_status("배출 완료")
                    
                    # 일정 상태 업데이트
                    self.dose_schedule[self.current_dose_index]["status"] = "completed"
                    self._update_schedule_display(self.current_dose_index)  # 특정 일정만 업데이트
                    
                    print(f"✅ 배출 성공: 일정 {self.current_dose_index + 1}")
                else:
                    print("  ❌ 배출구 열림 실패")
                    self._update_status("배출구 열림 실패")
            else:
                print("  ❌ 디스크 1 회전 실패")
                self._update_status("디스크 회전 실패")
            
        except Exception as e:
            self._update_status("배출 실패")
            print(f"❌ 배출 실패: {e}")
    
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
            if wifi_manager.is_connected and wifi_manager.time_synced:
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
            print(f"❌ 현재 시간 가져오기 실패: {e}")
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
                    # 중복 배출 방지 (같은 시간에 여러 번 배출되지 않도록)
                    schedule_key = f"{schedule['time']}_{i}"
                    if schedule_key in self.last_dispense_time:
                        last_dispense = self.last_dispense_time[schedule_key]
                        if current_time == last_dispense:
                            print(f"⏭️ 일정 {i+1} ({schedule['time']}) 이미 오늘 배출됨")
                            continue
                    
                    print(f"⏰ 자동 배출 트리거: 일정 {i+1} ({schedule['time']})")
                    self._execute_auto_dispense(i)
                    break
                    
        except Exception as e:
            print(f"❌ 자동 배출 확인 실패: {e}")
    
    def _execute_auto_dispense(self, dose_index):
        """자동 배출 실행"""
        try:
            print(f"🤖 자동 배출 시작: 일정 {dose_index + 1}")
            self._update_status("자동 배출 중...")
            
            # 현재 선택된 일정을 임시로 변경
            original_index = self.current_dose_index
            self.current_dose_index = dose_index
            
            # 배출 실행
            success = self.dispense_medication()
            
            # 원래 선택된 일정으로 복원
            self.current_dose_index = original_index
            
            if success:
                # 배출 성공 시 상태 업데이트
                self.dose_schedule[dose_index]["status"] = "completed"
                schedule_key = f"{self.dose_schedule[dose_index]['time']}_{dose_index}"
                self.last_dispense_time[schedule_key] = self._get_current_time()
                self._update_status("자동 배출 완료")
                print(f"✅ 자동 배출 성공: 일정 {dose_index + 1}")
            else:
                # 배출 실패 시 상태 업데이트
                self.dose_schedule[dose_index]["status"] = "failed"
                self._update_status("자동 배출 실패")
                print(f"❌ 자동 배출 실패: 일정 {dose_index + 1}")
            
            # UI 업데이트
            self._update_schedule_display()
            
        except Exception as e:
            print(f"❌ 자동 배출 실행 실패: {e}")
            self._update_status("자동 배출 오류")
    
    def update(self):
        """화면 업데이트 (ScreenManager에서 주기적으로 호출)"""
        try:
            # 자동 배출 시간 확인
            self._check_auto_dispense()
            
        except Exception as e:
            print(f"❌ 메인 스크린 업데이트 실패: {e}")
    
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
                        print(f"  📱 일정 {i+1} 업데이트: {schedule_text}")
        except Exception as e:
            print(f"  ❌ 일정 표시 업데이트 실패: {e}")


class MockMotorSystem:
    """모의 모터 시스템"""
    
    def __init__(self):
        self.motor_controller = MockMotorController()
        print("✅ MockMotorSystem 초기화 완료")
    
    def control_dispense_slide(self, level):
        """모의 배출구 슬라이드 제어"""
        print(f"🚪 모의 배출구 슬라이드 {level}단 (120도)")
        return True
    
    def rotate_disk(self, disk_num, steps):
        """모의 디스크 회전"""
        print(f"🔄 모의 디스크 {disk_num} 회전: {steps} 스텝")
        return True


class MockMotorController:
    """모의 모터 컨트롤러"""
    
    def __init__(self):
        self.motor_states = [0, 0, 0, 0]
        self.motor_steps = [0, 0, 0, 0]
        self.motor_positions = [0, 0, 0, 0]
        print("✅ MockMotorController 초기화 완료")
    
    def test_motor_simple(self, motor_index, steps):
        """모의 모터 간단 테스트"""
        print(f"🧪 모의 모터 {motor_index} 간단 테스트 시작 ({steps}스텝)")
        print(f"✅ 모의 모터 {motor_index} 테스트 성공")
        return True
    
    def test_motor3_only(self, steps=50):
        """모터 3 전용 테스트 (모의)"""
        print(f"🧪 모의 모터 3 전용 테스트 시작 ({steps}스텝)")
        print("✅ 모의 모터 3 테스트 성공")
        return True


# Modern UI 함수들을 MainScreen 클래스에 추가
def _create_title_area(self):
    """제목 영역 생성"""
    try:
        # 제목 영역 완전 제거됨
        
        # 현재 시간과 상태 표시기를 독립적으로 생성
        self._create_current_time_and_status()
        
    except Exception as e:
        print(f"  ❌ 제목 영역 생성 실패: {e}")

def _create_current_time_and_status(self):
    """현재 시간과 상태 표시기를 독립적으로 생성"""
    try:
        # 현재 시간 표시 (좌측 상단)
        self.current_time_label = lv.label(self.main_container)
        self.current_time_label.set_text(self.current_time)
        self.current_time_label.align(lv.ALIGN.TOP_LEFT, 5, -10)  # 배터리와 같은 y축 위치
        self.current_time_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
        self.current_time_label.set_style_text_color(lv.color_hex(0x007AFF), 0)
        
        # WiFi 심볼을 상단 중앙에 독립적으로 배치
        self._create_wifi_indicator()
        
        # 배터리 상태 표시기 (오른쪽만)
        self._create_battery_indicators()
        
    except Exception as e:
        print(f"  ❌ 현재 시간과 상태 표시기 생성 실패: {e}")

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
        print("  ✅ WiFi 심볼을 상단 중앙에 배치 완료")
    except Exception as e:
        print(f"  ❌ WiFi 심볼 생성 실패: {e}")

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
        print("  ✅ 배터리 상태 표시기 생성 완료")
    except Exception as e:
        print(f"  ❌ 배터리 상태 표시기 생성 실패: {e}")

# 기존 _create_status_indicators 함수는 제거됨 (WiFi와 배터리를 분리)

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
            print(f"  ❌ 복용 일정 영역 생성 실패: {e}")

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
        
        # 버튼 힌트 텍스트 (LVGL 심볼 사용) - 기본 폰트 사용
        self.hints_text = lv.label(self.hints_container)
        self.hints_text.set_text(f"A:{lv.SYMBOL.UP} B:{lv.SYMBOL.DOWN} C:{lv.SYMBOL.DOWNLOAD} D:{lv.SYMBOL.SETTINGS}")
        self.hints_text.align(lv.ALIGN.CENTER, 0, 0)  # 컨테이너 중앙에 배치
        self.hints_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.hints_text.set_style_text_color(lv.color_hex(0x8E8E93), 0)  # 모던 라이트 그레이
        # 기본 폰트는 자동으로 사용됨 (한글 폰트 적용 안함)

def _create_basic_screen(self):
    """기본 화면 생성 (오류 시 대안)"""
    print(f"  📱 {self.screen_name} 기본 화면 생성 시작...")
    
    # 기본 화면 객체 생성
    self.screen_obj = lv.obj()
    self.screen_obj.set_size(160, 128)
    
    # 기본 라벨 생성
    self.title_label = lv.label(self.screen_obj)
    self.title_label.set_text("메인 화면")
    self.title_label.align(lv.ALIGN.CENTER, 0, 0)
    
    print("  ✅ 기본 화면 생성 완료")

# MainScreen 클래스에 함수들을 바인딩
MainScreen._create_title_area = _create_title_area
MainScreen._create_current_time_and_status = _create_current_time_and_status
MainScreen._create_wifi_indicator = _create_wifi_indicator
MainScreen._create_battery_indicators = _create_battery_indicators
MainScreen._create_schedule_area = _create_schedule_area
MainScreen._create_button_hints_area = _create_button_hints_area
MainScreen._create_basic_screen = _create_basic_screen
