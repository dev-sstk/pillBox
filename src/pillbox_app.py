"""
필박스 메인 애플리케이션
버튼 인터페이스와 화면 관리 시스템을 통합한 메인 앱
"""

import time
import lvgl as lv

class PillBoxApp:
    """필박스 메인 애플리케이션 클래스"""
    
    def __init__(self):
        """앱 초기화"""
        # 메모리 정리 (test_lvgl.py 방식)
        import gc
        gc.collect()
        print("[OK] 메모리 정리 완료")
        
        # 지연 초기화를 위한 플래그들
        self._ui_style = None
        self._audio_system = None
        self._led_controller = None
        self._button_interface = None
        self._motor_system = None
        self._wifi_manager = None
        self._screen_manager = None
        self.running = False
        
        # 버튼 콜백 설정
        self._setup_button_callbacks()
        
        print("[OK] PillBoxApp 초기화 완료")
    
    # 지연 로딩 메서드들
    @property
    def ui_style(self):
        """UI 스타일 지연 로딩"""
        if self._ui_style is None:
            from ui_style import UIStyle
            self._ui_style = UIStyle()
            print("[DEBUG] UI 스타일 지연 로딩 완료")
        return self._ui_style
    
    @property
    def audio_system(self):
        """오디오 시스템 지연 로딩"""
        if self._audio_system is None:
            from audio_system import AudioSystem
            self._audio_system = AudioSystem()
            print("[DEBUG] 오디오 시스템 지연 로딩 완료")
        return self._audio_system
    
    @property
    def led_controller(self):
        """LED 컨트롤러 지연 로딩"""
        if self._led_controller is None:
            from led_controller import LEDController
            self._led_controller = LEDController()
            print("[DEBUG] LED 컨트롤러 지연 로딩 완료")
        return self._led_controller
    
    @property
    def button_interface(self):
        """버튼 인터페이스 지연 로딩"""
        if self._button_interface is None:
            from button_interface import ButtonInterface
            self._button_interface = ButtonInterface()
            print("[DEBUG] 버튼 인터페이스 지연 로딩 완료")
        return self._button_interface
    
    @property
    def motor_system(self):
        """모터 시스템 지연 로딩"""
        if self._motor_system is None:
            from motor_control import PillBoxMotorSystem
            self._motor_system = PillBoxMotorSystem()
            print("[DEBUG] 모터 시스템 지연 로딩 완료")
        return self._motor_system
    
    @property
    def wifi_manager(self):
        """WiFi 관리자 지연 로딩"""
        if self._wifi_manager is None:
            from wifi_manager import get_wifi_manager
            self._wifi_manager = get_wifi_manager()
            print("[DEBUG] WiFi 관리자 지연 로딩 완료")
        return self._wifi_manager
    
    @property
    def screen_manager(self):
        """화면 관리자 지연 로딩"""
        if self._screen_manager is None:
            from screen_manager import ScreenManager
            self._screen_manager = ScreenManager(self)
            print("[DEBUG] 화면 관리자 지연 로딩 완료")
        return self._screen_manager
    
    def cleanup_unused_modules(self):
        """사용하지 않는 모듈들 정리"""
        import gc
        
        # 사용하지 않는 모듈들 해제
        if hasattr(self, '_audio_system') and self._audio_system:
            self._audio_system = None
            print("[DEBUG] 오디오 시스템 메모리 해제")
        
        if hasattr(self, '_motor_system') and self._motor_system:
            self._motor_system = None
            print("[DEBUG] 모터 시스템 메모리 해제")
        
        if hasattr(self, '_led_controller') and self._led_controller:
            self._led_controller = None
            print("[DEBUG] LED 컨트롤러 메모리 해제")
        
        # 가비지 컬렉션 실행
        gc.collect()
        print("[DEBUG] 메모리 정리 완료")
    
    def _setup_button_callbacks(self):
        """버튼 콜백 함수들 설정"""
        self.button_interface.set_callback('A', self._on_button_a)
        self.button_interface.set_callback('B', self._on_button_b)
        self.button_interface.set_callback('C', self._on_button_c)
        self.button_interface.set_callback('D', self._on_button_d)
    
    def _on_button_a(self):
        """버튼 A (Up / Value +) 처리"""
        current_screen = self.screen_manager.get_current_screen()
        if current_screen:
            current_screen.on_button_a()
    
    def _on_button_b(self):
        """버튼 B (Down / Value -) 처리"""
        current_screen = self.screen_manager.get_current_screen()
        if current_screen:
            current_screen.on_button_b()
    
    def _on_button_c(self):
        """버튼 C (Back / Cancel) 처리"""
        current_screen = self.screen_manager.get_current_screen()
        if current_screen:
            current_screen.on_button_c()
    
    def _on_button_d(self):
        """버튼 D (Next / Select / Confirm) 처리"""
        current_screen = self.screen_manager.get_current_screen()
        if current_screen:
            current_screen.on_button_d()
    
    def start(self):
        """앱 시작"""
        print("[ROCKET] PillBoxApp 시작")
        self.running = True
        
        # 시작 화면으로 이동
        self.screen_manager.show_screen('startup')
        
        # 메인 루프
        self._main_loop()
    
    def stop(self):
        """앱 중지"""
        print("⏹️ PillBoxApp 중지")
        self.running = False
    
    def _main_loop(self):
        """메인 애플리케이션 루프"""
        while self.running:
            try:
                # LVGL 타이머 핸들러 호출 (화면 업데이트)
                lv.timer_handler()
                
                # 버튼 입력 처리
                self.button_interface.update()
                
                # 화면 업데이트
                self.screen_manager.update()
                
                # 짧은 대기
                time.sleep_ms(50)
                
            except KeyboardInterrupt:
                print("사용자에 의해 중단됨")
                self.stop()
                break
            except Exception as e:
                print(f"메인 루프 오류: {e}")
                time.sleep_ms(100)
    
    def get_ui_style(self):
        """UI 스타일 객체 반환"""
        return self.ui_style
    
    def get_audio_system(self):
        """오디오 시스템 객체 반환"""
        return self.audio_system
    
    def get_screen_manager(self):
        """화면 관리자 반환"""
        return self.screen_manager
    
    def get_motor_system(self):
        """모터 시스템 반환"""
        return self.motor_system
    
    def get_wifi_manager(self):
        """WiFi 시스템 반환"""
        return self.wifi_manager
    
    def create_and_register_screen(self, screen_name, **kwargs):
        """화면 동적 생성 및 등록"""
        try:
            if screen_name == "advanced_settings":
                from screens.advanced_settings_screen import AdvancedSettingsScreen
                screen_instance = AdvancedSettingsScreen(self.screen_manager)
                self.screen_manager.register_screen(screen_name, screen_instance)
                print(f"[OK] {screen_name} 화면 생성 및 등록 완료")
                return True
            elif screen_name == "data_management":
                from screens.data_management_screen import DataManagementScreen
                screen_instance = DataManagementScreen(self.screen_manager)
                self.screen_manager.register_screen(screen_name, screen_instance)
                print(f"[OK] {screen_name} 화면 생성 및 등록 완료")
                return True
            elif screen_name == "disk_selection":
                from screens.disk_selection_screen import DiskSelectionScreen
                dose_info = kwargs.get('dose_info', None)
                screen_instance = DiskSelectionScreen(self.screen_manager, dose_info=dose_info)
                self.screen_manager.register_screen(screen_name, screen_instance)
                print(f"[OK] {screen_name} 화면 생성 및 등록 완료")
                return True
            else:
                print(f"[ERROR] 지원하지 않는 화면: {screen_name}")
                return False
        except Exception as e:
            print(f"[ERROR] 화면 생성 실패: {screen_name}, 오류: {e}")
            return False