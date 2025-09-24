"""
설정 화면
다양한 설정 옵션을 제공하는 메뉴 화면
"""

import time
import lvgl as lv

class SettingsScreen:
    """설정 화면 클래스 (간단한 버전)"""
    
    def __init__(self, screen_manager):
        """설정 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = 'settings'
        self.screen_obj = None
        self.settings_options = [
            {"name": "Wi-Fi 설정", "icon": "📶", "action": "wifi"},
            {"name": "복용 설정", "icon": "💊", "action": "dose"},
            {"name": "알약 충전", "icon": "🔄", "action": "loading"},
            {"name": "알약 배출", "icon": "📤", "action": "dispense"},
            {"name": "시스템 정보", "icon": "ℹ️", "action": "info"}
        ]
        self.selected_index = 0
        
        # 간단한 화면 생성
        self._create_simple_screen()
        
        print(f"✅ {self.screen_name} 화면 초기화 완료")
    
    def _create_simple_screen(self):
        """간단한 화면 생성 (test_lvgl.py 방식)"""
        print(f"  📱 {self.screen_name} 간단한 화면 생성 시작...")
        
        # 메모리 정리
        import gc
        gc.collect()
        print(f"  ✅ 메모리 정리 완료")
        
        # 화면 생성
        print(f"  📱 화면 객체 생성...")
        self.screen_obj = lv.obj()
        self.screen_obj.set_style_bg_color(lv.color_hex(0x000000), 0)
        print(f"  ✅ 화면 객체 생성 완료")
        
        # 간단한 라벨 생성
        print(f"  📱 라벨 생성...")
        label = lv.label(self.screen_obj)
        label.set_text("설정")
        # 한국어 폰트 적용
        korean_font = getattr(lv, "font_notosans_kr_regular", None)
        if korean_font:
            label.set_style_text_font(korean_font, 0)
        label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        label.align(lv.ALIGN.CENTER, 0, 0)
        print(f"  ✅ 라벨 생성 완료")
    
    def get_title(self):
        """화면 제목"""
        return "설정"
    
    def get_button_hints(self):
        """버튼 힌트"""
        return "A:위  B:아래  C:뒤로  D:선택"
    
    def get_voice_file(self):
        """안내 음성 파일"""
        return "wav_settings_prompt.wav"
    
    def get_effect_file(self):
        """효과음 파일"""
        return "wav_select.wav"
    
    def show(self):
        """화면 표시"""
        if self.screen_obj:
            lv.screen_load(self.screen_obj)
            print(f"✅ {self.screen_name} 화면 표시됨")
            
            # LVGL 타이머 핸들러 강제 호출 (test_lvgl.py 방식)
            print(f"📱 {self.screen_name} 화면 강제 업데이트 시작...")
            for i in range(10):
                lv.timer_handler()
                time.sleep(0.1)  # test_lvgl.py와 동일한 대기 시간
            print(f"✅ {self.screen_name} 화면 강제 업데이트 완료")
    
    def hide(self):
        """화면 숨기기"""
        pass
    
    def update(self):
        """화면 업데이트"""
        pass
    
    def on_button_a(self):
        """버튼 A (Up) 처리"""
        print("설정 옵션 위로 이동")
        self.selected_index = (self.selected_index - 1) % len(self.settings_options)
        pass
    
    def on_button_b(self):
        """버튼 B (Down) 처리"""
        print("설정 옵션 아래로 이동")
        self.selected_index = (self.selected_index + 1) % len(self.settings_options)
        pass
    
    def on_button_c(self):
        """버튼 C (Back) 처리"""
        print("설정 화면 뒤로가기")
        self.screen_manager.show_screen('main')
    
    def on_button_d(self):
        """버튼 D (Select) 처리"""
        selected_option = self.settings_options[self.selected_index]
        print(f"설정 옵션 선택: {selected_option['name']}")
        
        # 선택된 옵션에 따라 화면 이동
        if selected_option['action'] == 'wifi':
            self.screen_manager.show_screen('wifi_scan')
        elif selected_option['action'] == 'dose':
            self.screen_manager.show_screen('dose_count')
        elif selected_option['action'] == 'loading':
            self.screen_manager.show_screen('pill_loading')
        elif selected_option['action'] == 'dispense':
            self.screen_manager.show_screen('pill_dispense')
        elif selected_option['action'] == 'info':
            print("시스템 정보 표시")
            pass