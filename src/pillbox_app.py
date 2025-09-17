"""
필박스 메인 애플리케이션
버튼 인터페이스와 화면 관리 시스템을 통합한 메인 앱
"""

import time
import lvgl as lv
import lv_utils
from machine import Pin
from button_interface import ButtonInterface
from screen_manager import ScreenManager
from ui_style import UIStyle
from audio_system import AudioSystem
from motor_control import PillBoxMotorSystem
from wifi_manager import wifi_manager

class PillBoxApp:
    """필박스 메인 애플리케이션 클래스"""
    
    def __init__(self):
        """앱 초기화"""
        # 메모리 정리 (test_lvgl.py 방식)
        import gc
        gc.collect()
        print("✅ 메모리 정리 완료")
        
        self.ui_style = UIStyle()
        self.audio_system = AudioSystem()
        self.button_interface = ButtonInterface()
        self.motor_system = PillBoxMotorSystem()  # 모터 시스템 추가
        self.wifi_manager = wifi_manager  # WiFi 시스템 추가
        self.screen_manager = ScreenManager(self)  # 자신을 전달
        self.running = False
        
        # 버튼 콜백 설정
        self._setup_button_callbacks()
        
        print("✅ PillBoxApp 초기화 완료")
    
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
        print("🚀 PillBoxApp 시작")
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
