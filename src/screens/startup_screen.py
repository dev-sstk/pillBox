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
        self.auto_advance_time = 2000  # 2초 후 자동 진행 (원점 보정 시간 확보)
        
        # UI 스타일 시스템 초기화
        self.ui_style = UIStyle()
        
        # WiFi 자동 연결 상태
        self.wifi_auto_connect_started = False
        self.wifi_auto_connect_done = False
        self.wifi_connected = False
        self.wifi_connected_time = 0  # WiFi 연결 성공 시각 기록
        
        # 디스크 원점 보정 상태
        self.calibration_started = False
        self.calibration_done = False
        self.calibration_progress = 0  # 0-100%
        self.current_disk = 0  # 0, 1, 2
        self.calibration_start_time = 0
        
        # 화면 생성
        self._create_modern_screen()
        
        print(f"[OK] {self.screen_name} 화면 초기화 완료")
    
    def _create_modern_screen(self):
        """Modern 스타일 화면 생성"""
        print(f"  [INFO] {self.screen_name} Modern 화면 생성 시작...")
        
        # 메모리 정리
        import gc
        gc.collect()
        print(f"  [OK] 메모리 정리 완료")
        
        # 화면 생성
        print(f"  [INFO] 화면 객체 생성...")
        self.screen_obj = lv.obj()
        
        # 화면 배경 스타일 적용
        self.ui_style.apply_screen_style(self.screen_obj)
        
        # 스크롤바 비활성화
        self.screen_obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.screen_obj.set_scroll_dir(lv.DIR.NONE)
        
        print(f"  [OK] 화면 객체 생성 완료")
        
        # 메인 컨테이너 생성
        self._create_main_container()
        
        # 로고 영역 생성
        self._create_logo_area()
        
        # 하단 정보 영역 생성
        self._create_info_area()
        
        print(f"  [OK] Modern 화면 생성 완료")
    
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
        
        # 제목 제거됨
        
        # 부제목 제거됨
    
    
    def _create_info_area(self):
        """하단 정보 영역 생성 - 버전 텍스트 제거로 간소화"""
        # 정보 컨테이너 제거 (버전 텍스트가 없으므로 불필요)
        pass
    
    def get_title(self):
        """화면 제목"""
        return "필박스"
    
    def get_button_hints(self):
        """버튼 힌트"""
        return "C:건너뛰기  D:다음"
    
    def get_voice_file(self):
        """안내 음성 파일"""
        return "wav_startup_hello.wav"
    
    def get_effect_file(self):
        """효과음 파일"""
        return "wav_select.wav"
    
    def show(self):
        """화면 표시"""
        if self.screen_obj:
            lv.screen_load(self.screen_obj)
            print(f"[OK] {self.screen_name} 화면 표시됨")
            
            # 로딩 애니메이션 시작
            self._start_loading_animation()
            
            # LVGL 타이머 핸들러 강제 호출
            print(f"[INFO] {self.screen_name} 화면 강제 업데이트 시작...")
            for i in range(10):
                lv.timer_handler()
                time.sleep(0.1)
            print(f"[OK] {self.screen_name} 화면 강제 업데이트 완료")
    
    def hide(self):
        """화면 숨기기"""
        try:
            print("[INFO] startup 화면 숨김 시작...")
            # 로딩 애니메이션 정지
            self._stop_loading_animation()
            print("[INFO] startup 화면 숨김 완료")
        except Exception as e:
            print(f"[WARN] startup 화면 숨김 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def update(self):
        """화면 업데이트 - 로딩 진행 및 자동 전환"""
        current_time = time.ticks_ms()
        elapsed_time = time.ticks_diff(current_time, self.start_time)
        
        # 원점 보정 완료 후 WiFi 연결 시도
        if self.calibration_done and not self.wifi_auto_connect_started:
            print("[TOOL] 원점 보정 완료, WiFi 연결 시도 시작")
            self._try_wifi_auto_connect()
        
        # WiFi 연결 완료되면 즉시 전환
        if self.wifi_auto_connect_done:
            # WiFi 연결 시도 완료 (성공/실패 관계없이 즉시 전환)
            print(f"[OK] WiFi 연결 시도 완료, Wi-Fi 스캔 화면으로 이동")
            self._go_to_wifi_setup()
        
        # 최대 대기 시간 초과 시 강제 전환 (2초)
        if elapsed_time > self.auto_advance_time:
            print("⏰ 최대 대기 시간 초과, Wi-Fi 스캔 화면으로 강제 전환")
            self._go_to_wifi_setup()
    
    def _start_loading_animation(self):
        """로딩 애니메이션 시작"""
        print("[RETRY] 백그라운드 원점 보정 시작")
        # 원점 보정 시작
        self._start_calibration()
    
    def _stop_loading_animation(self):
        """로딩 애니메이션 정지"""
        try:
            print("⏹️ 백그라운드 원점 보정 정지")
            # 추가적인 정리 작업이 필요하면 여기에 추가
        except Exception as e:
            print(f"[WARN] 로딩 애니메이션 정지 실패: {e}")
    
    def cleanup(self):
        """리소스 정리"""
        try:
            print(f"🧹 {self.screen_name} 리소스 정리 시작...")
            
            # 로딩 애니메이션 정지
            self._stop_loading_animation()
            
            # 화면 객체 정리
            if hasattr(self, 'screen_obj') and self.screen_obj:
                try:
                    print(f"🧹 {self.screen_name} LVGL 객체 정리...")
                    # LVGL 객체는 ScreenManager에서 삭제하므로 여기서는 참조만 정리
                    pass
                except Exception as e:
                    print(f"[WARN] {self.screen_name} LVGL 객체 정리 실패: {e}")
            
            print(f"[OK] {self.screen_name} 리소스 정리 완료")
            
        except Exception as e:
            print(f"[ERROR] {self.screen_name} 리소스 정리 실패: {e}")
    
    def _start_calibration(self):
        """디스크 원점 보정 시작"""
        if self.calibration_started:
            return
        
        self.calibration_started = True
        self.calibration_start_time = time.ticks_ms()
        print("[TOOL] 디스크 원점 보정 시작...")
        
        # 모터 시스템 직접 초기화
        try:
            from motor_control import PillBoxMotorSystem
            motor_system = PillBoxMotorSystem()
            print("[OK] 모터 시스템 직접 초기화 완료")
            
            # 비동기로 원점 보정 실행
            self._run_calibration_async(motor_system)
            
        except Exception as e:
            print(f"[ERROR] 모터 시스템 초기화 실패: {e}")
            print("[WARN] 원점 보정 건너뛰기")
            self.calibration_done = True
            self.calibration_progress = 100
    
    def _run_calibration_async(self, motor_system):
        """비동기 원점 보정 실행 (3개 모터 동시 보정)"""
        try:
            print("[TOOL] 3개 디스크 동시 원점 보정 중...")
            
            # 3개 디스크 동시 보정
            if motor_system.calibrate_all_disks_simultaneous():
                print("[OK] 모든 디스크 동시 원점 보정 완료!")
                self.calibration_progress = 100
                self.calibration_done = True
            else:
                print("[ERROR] 디스크 동시 보정 실패")
                self.calibration_done = True
                
        except Exception as e:
            print(f"[ERROR] 원점 보정 중 오류: {e}")
            motor_system.motor_controller.stop_all_motors()
            print("🔌 전체 모터 끄기")
            self.calibration_done = True
    
    def _try_wifi_auto_connect(self):
        """WiFi 자동 연결 시도"""
        if self.wifi_auto_connect_started:
            return
        
        self.wifi_auto_connect_started = True
        print("📡 WiFi 자동 연결 시도 시작...")
        
        try:
            # wifi_manager 전역 인스턴스 가져오기
            from wifi_manager import get_wifi_manager
            
            # 저장된 WiFi 설정으로 자동 연결 시도 (타임아웃 800ms로 단축)
            wifi_mgr = get_wifi_manager()
            success = wifi_mgr.try_auto_connect(timeout=800)
            
            if success:
                print("[OK] WiFi 자동 연결 성공!")
                self.wifi_connected = True
                self.wifi_connected_time = time.ticks_ms()  # 연결 성공 시각 기록
            else:
                print("[WARN] WiFi 자동 연결 실패 (저장된 설정 없거나 연결 실패)")
                # 연결 실패해도 계속 진행
            
            self.wifi_auto_connect_done = True
            
        except Exception as e:
            print(f"[ERROR] WiFi 자동 연결 오류: {e}")
            self.wifi_auto_connect_done = True
    
    def _update_loading_progress(self, elapsed_time):
        """로딩 진행률 업데이트 - 제거됨 (원점 보정으로 대체)"""
        pass
    
    def on_button_a(self):
        """버튼 A 처리"""
        pass
    
    def on_button_b(self):
        """버튼 B 처리"""
        pass
    
    def on_button_c(self):
        """버튼 C (Skip) 처리"""
        print("시작 화면 건너뛰기")
        self._go_to_wifi_setup()
    
    def on_button_d(self):
        """버튼 D (Next) 처리"""
        print("시작 화면 다음으로")
        self._go_to_wifi_setup()
    
    def _go_to_wifi_setup(self):
        """Wi-Fi 설정 화면으로 이동"""
        # 짧은 대기 후 화면 전환
        time.sleep(0.2)
        
        # [FAST] 메모리 부족 해결: startup 화면 종료 시 메모리 정리
        import gc
        print("🧹 startup 화면 종료 시 메모리 정리 시작...")
        for i in range(5):  # 5회 가비지 컬렉션
            gc.collect()
            time.sleep(0.02)  # 0.02초 대기
        print("[OK] startup 화면 종료 시 메모리 정리 완료")
        
        # wifi_scan 화면이 등록되어 있는지 확인
        if 'wifi_scan' not in self.screen_manager.screens:
            print("[INFO] wifi_scan 화면이 등록되지 않음. 동적 생성 중...")
            
            # [FAST] 메모리 부족 해결: wifi_scan 화면 생성 전 메모리 정리
            print("🧹 wifi_scan 화면 생성 전 메모리 정리 시작...")
            for i in range(5):  # 5회 가비지 컬렉션
                gc.collect()
                time.sleep(0.02)  # 0.02초 대기
            print("[OK] wifi_scan 화면 생성 전 메모리 정리 완료")
            
            try:
                from screens.wifi_scan_screen import WifiScanScreen
                wifi_scan_screen = WifiScanScreen(self.screen_manager)
                self.screen_manager.register_screen('wifi_scan', wifi_scan_screen)
                print("[OK] wifi_scan 화면 생성 및 등록 완료")
            except Exception as e:
                print(f"[ERROR] wifi_scan 화면 생성 실패: {e}")
                # [FAST] 메모리 할당 실패 시 추가 메모리 정리
                print("🧹 wifi_scan 화면 생성 실패 후 추가 메모리 정리...")
                for i in range(3):
                    gc.collect()
                    time.sleep(0.01)
                print("[OK] 추가 메모리 정리 완료")
                import sys
                sys.print_exception(e)
                return
        
        # 화면 전환 (ScreenManager가 자동으로 처리)
        print("[INFO] Wi-Fi 스캔 화면으로 전환")
        # startup 화면은 ScreenManager.show_screen에서 자동으로 삭제됨
        self.screen_manager.show_screen('wifi_scan')