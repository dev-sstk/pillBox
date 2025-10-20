"""
시작 화면
필박스 로고와 초기 메시지를 표시하는 화면
Modern/Xiaomi-like 스타일 적용
"""

import time
import lvgl as lv
from ui_style import UIStyle

class StartupScreen:
    """시작 화면 클래스 - Modern UI 스타일"""
    
    def __init__(self, screen_manager):
        """시작 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = 'startup'
        self.screen_obj = None
        self.start_time = time.ticks_ms()
        self.auto_advance_time = 1000  # 1.5초 → 1초로 최적화 (화면 깜빡임 완전 방지)
        
        # UI 스타일 시스템 초기화
        self.ui_style = UIStyle()
        
        # WiFi 자동 연결 상태 제거됨
        
        # 디스크 원점 보정 상태
        self.calibration_started = False
        self.calibration_done = False
        self.calibration_progress = 0  # 0-100%
        self.current_disk = 0  # 0, 1, 2
        self.calibration_start_time = 0
        
        # 화면 생성
        self._create_modern_screen()
    
    def _create_modern_screen(self):
        """Modern 스타일 화면 생성"""
        
        # 메모리 정리
        import gc
        gc.collect()
        
        # 화면 생성
        self.screen_obj = lv.obj()
        
        # 화면 배경 스타일 적용
        self.ui_style.apply_screen_style(self.screen_obj)
        
        # 스크롤바 비활성화
        self.screen_obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.screen_obj.set_scroll_dir(lv.DIR.NONE)
        
        # 메인 컨테이너 생성
        self._create_main_container()
        
        # 로고 영역 생성
        self._create_logo_area()
    
    def _create_main_container(self):
        """메인 컨테이너 생성"""
        # 메인 컨테이너 (전체 화면)
        self.main_container = lv.obj(self.screen_obj)
        self.main_container.set_size(128, 160)
        self.main_container.align(lv.ALIGN.CENTER, 0, 0)
        self.main_container.set_style_bg_opa(0, 0)  # 투명 배경
        self.main_container.set_style_border_width(0, 0)
        
        # 스크롤바 비활성화
        self.main_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.main_container.set_scroll_dir(lv.DIR.NONE)
        self.main_container.set_style_pad_all(0, 0)
    
    def _create_logo_area(self):
        """로고 영역 생성 - 화면 정중앙에 배치"""
        # 로고 컨테이너 (화면 정중앙)
        self.logo_container = lv.obj(self.main_container)
        self.logo_container.set_size(120, 100)  # 원 크기에 맞게 높이 조정
        self.logo_container.align(lv.ALIGN.CENTER, 0, 0)  # 완전히 중앙에 배치
        self.logo_container.set_style_bg_opa(0, 0)
        self.logo_container.set_style_border_width(0, 0)
        self.logo_container.set_style_pad_all(0, 0)
        
        # 로고 컨테이너 스크롤바 비활성화
        self.logo_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.logo_container.set_scroll_dir(lv.DIR.NONE)
        
        # 필박스 아이콘 (원형 배경) - 사이즈 확대
        self.icon_bg = lv.obj(self.logo_container)
        self.icon_bg.set_size(80, 80)  # PILLMATE 텍스트에 맞게 80x80으로 확대
        self.icon_bg.align(lv.ALIGN.CENTER, 0, 0)  # 완전히 중앙에 배치
        
        # 아이콘 배경 스크롤바 비활성화
        self.icon_bg.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.icon_bg.set_scroll_dir(lv.DIR.NONE)
        self.icon_bg.set_style_bg_color(lv.color_hex(0xd2b13f), 0)  # 골드 색상
        self.icon_bg.set_style_bg_opa(255, 0)
        self.icon_bg.set_style_radius(40, 0)  # 반지름도 40으로 조정 (80/2)
        self.icon_bg.set_style_border_width(0, 0)
        
        # 필박스 아이콘 텍스트
        self.icon_text = lv.label(self.icon_bg)
        self.icon_text.set_text("PILLMATE")  # PILLMATE 텍스트
        self.icon_text.align(lv.ALIGN.CENTER, 0, 0)
        self.icon_text.set_style_text_color(lv.color_hex(0x000000), 0)  # 검정색
        self.icon_text.set_style_text_font(self.ui_style.get_font('title'), 0)
        
        # 아이콘 텍스트 스크롤바 비활성화
        self.icon_text.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.icon_text.set_scroll_dir(lv.DIR.NONE)
    
    def show(self):
        """화면 표시"""
        if self.screen_obj:
            lv.screen_load(self.screen_obj)
            
            # 원점 보정 시퀀스 시작
            self._start_calibration_sequence()
            
            # LVGL 타이머 핸들러 강제 호출
            for i in range(10):
                lv.timer_handler()
                time.sleep(0.1)
    
    def update(self):
        """화면 업데이트 - 로딩 진행 및 자동 전환"""
        current_time = time.ticks_ms()
        elapsed_time = time.ticks_diff(current_time, self.start_time)
        
        # 원점 보정 완료되면 즉시 전환
        if self.calibration_done:
            self._request_screen_transition()
        
        # 최대 대기 시간 초과 시 강제 전환 (2초)
        if elapsed_time > self.auto_advance_time:
            self._request_screen_transition()
    
    def _start_calibration_sequence(self):
        """원점 보정 시퀀스 시작"""
        # 원점 보정 시작
        self._start_calibration()
    
    def _start_calibration(self):
        """디스크 원점 보정 시작"""
        if self.calibration_started:
            return
        
        self.calibration_started = True
        self.calibration_start_time = time.ticks_ms()
        
        # 모터 시스템 직접 초기화
        try:
            from motor_control import PillBoxMotorSystem
            motor_system = PillBoxMotorSystem()
            
            # 비동기로 원점 보정 실행
            self._run_calibration_async(motor_system)
            
        except Exception as e:
            self.calibration_done = True
            self.calibration_progress = 100
    
    def _run_calibration_async(self, motor_system):
        """비동기 원점 보정 실행 (3개 모터 동시 보정)"""
        try:
            # 3개 디스크 동시 보정
            if motor_system.calibrate_all_disks_simultaneous():
                self.calibration_progress = 100
                self.calibration_done = True
            else:
                self.calibration_done = True
                pass
                
        except Exception as e:
            motor_system.motor_controller.stop_all_motors()
            self.calibration_done = True
    
    
    def _request_screen_transition(self):
        """화면 전환 요청 - ScreenManager에 위임"""
        # print("[INFO] 화면 전환 요청")
        
        # ScreenManager에 화면 전환 요청 (올바른 책임 분리)
        try:
            self.screen_manager.transition_to('wifi_scan')
            # print("[OK] 화면 전환 요청 완료")
        except Exception as e:
            # print(f"[ERROR] 화면 전환 요청 실패: {e}")
            import sys
            sys.print_exception(e)
        
        # 화면 전환 (올바른 책임 분리 - ScreenManager가 처리)
        # print("[INFO] 스타트업 화면 완료 - ScreenManager에 완료 신호 전송")
        
        # ScreenManager에 스타트업 완료 신호 전송 (올바른 책임 분리)
        try:
            self.screen_manager.startup_completed()
            # print("[OK] 스타트업 완료 신호 전송 완료")
        except Exception as e:
            # print(f"[ERROR] 스타트업 완료 신호 전송 실패: {e}")
            import sys
            sys.print_exception(e)
    
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
    
    def _cleanup_lvgl(self):
        """화면 전환 전 LVGL 객체 안전 정리 (ChatGPT 추천 방법)"""
        import lvgl as lv
        import gc
        import time
        
        # print("[INFO] StartupScreen LVGL 정리 시작")
        
        # 메모리 모니터링 (정리 전)
        self._monitor_memory("BEFORE CLEANUP")
        
        try:
            # 1️⃣ 현재 화면 객체가 존재하면 자식부터 모두 삭제
            if hasattr(self, 'screen_obj') and self.screen_obj:
                try:
                    # 모든 자식 객체 삭제
                    while self.screen_obj.get_child_count() > 0:
                        child = self.screen_obj.get_child(0)
                        if child:
                            child.delete()
                    # print("[OK] LVGL 자식 객체 삭제 완료")
                except Exception as e:
                    # print(f"[WARN] 자식 삭제 중 오류: {e}")
                    pass
                # 화면 자체 삭제
                try:
                    self.screen_obj.delete()
                    # print("[OK] 화면 객체 삭제 완료")
                except Exception as e:
                    # print(f"[WARN] 화면 객체 삭제 실패: {e}")
                    pass
                pass
                
                self.screen_obj = None  # Python 참조 제거
            
            # 2️⃣ 스타일 / 폰트 등 Python 객체 참조 해제
            if hasattr(self, 'ui_style'):
                self.ui_style = None
            
            # 3️⃣ LVGL 내부 타이머 및 큐 정리
            try:
                lv.timer_handler()
            except:
                pass
            
            # 4️⃣ 가비지 컬렉션 (여러 번 수행)
            for i in range(3):
                gc.collect()
                time.sleep_ms(10)
            
            # 메모리 모니터링 (정리 후)
            self._monitor_memory("AFTER CLEANUP")
            
            # print("[OK] StartupScreen LVGL 정리 완료")
            
        except Exception as e:
            # print(f"[ERROR] LVGL 정리 실패: {e}")
            pass