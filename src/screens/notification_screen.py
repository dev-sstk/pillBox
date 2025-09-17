"""
알림 화면
복용 시간 도착 시 표시되는 알림 화면
"""

import time
import lvgl as lv

class NotificationScreen:
    """알림 화면 클래스 (간단한 버전)"""
    
    def __init__(self, screen_manager, notification_data=None):
        """알림 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = 'notification'
        self.screen_obj = None
        self.notification_data = notification_data
        self.snooze_time = 0
        self.alert_start_time = time.ticks_ms()
        
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
        label.set_text("복용 시간입니다!")
        # 한국어 폰트 적용
        korean_font = getattr(lv, "font_notosans_kr_regular", None)
        if korean_font:
            label.set_style_text_font(korean_font, 0)
        label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        label.align(lv.ALIGN.CENTER, 0, 0)
        print(f"  ✅ 라벨 생성 완료")
    
    def get_title(self):
        """화면 제목"""
        return "알림"
    
    def get_button_hints(self):
        """버튼 힌트"""
        return "C:미루기  D:복용하기"
    
    def get_voice_file(self):
        """안내 음성 파일"""
        return "wav_take_pill_prompt.wav"
    
    def get_effect_file(self):
        """효과음 파일"""
        return "wav_alarm.wav"
    
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
    
    def set_notification_data(self, dose_info):
        """알림 데이터 설정"""
        self.notification_data = dose_info
        print(f"알림 데이터 설정: {dose_info}")
    
    def on_button_a(self):
        """버튼 A (None) 처리"""
        print("버튼 A - 사용 안함")
        pass
    
    def on_button_b(self):
        """버튼 B (None) 처리"""
        print("버튼 B - 사용 안함")
        pass
    
    def on_button_c(self):
        """버튼 C (Snooze) 처리"""
        print("알림 연기")
        self.snooze_time = 5 * 60 * 1000  # 5분 연기
        pass
    
    def on_button_d(self):
        """버튼 D (Take) 처리"""
        print("복용 완료")
        self.screen_manager.show_screen('main_screen')