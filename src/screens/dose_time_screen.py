"""
복용 시간 설정 화면
각 복용 시간을 설정하는 화면 (spinner_card layout)
"""

import time
import lvgl as lv

class DoseTimeScreen:
    """복용 시간 설정 화면 클래스 (간단한 버전)"""
    
    def __init__(self, screen_manager, dose_count=1):
        """복용 시간 설정 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = 'dose_time'
        self.screen_obj = None
        self.dose_count = dose_count
        self.dose_times = []  # 설정된 복용 시간들
        self.current_dose_index = 0  # 현재 설정 중인 복용 시간 인덱스
        self.current_hour = 8  # 기본값: 오전 8시
        self.current_minute = 0  # 기본값: 0분
        self.editing_hour = True  # True: 시간 편집, False: 분 편집
        
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
        label.set_text("복용 시간 설정")
        # 한국어 폰트 적용
        korean_font = getattr(lv, "font_notosans_kr_regular", None)
        if korean_font:
            label.set_style_text_font(korean_font, 0)
        label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        label.align(lv.ALIGN.CENTER, 0, 0)
        print(f"  ✅ 라벨 생성 완료")
    
    def get_title(self):
        """화면 제목"""
        return "복용 시간"
    
    def get_button_hints(self):
        """버튼 힌트"""
        return "A:증가  B:감소  C:뒤로  D:선택"
    
    def get_voice_file(self):
        """안내 음성 파일"""
        return "wav_dose_time_prompt.wav"
    
    def get_effect_file(self):
        """효과음 파일"""
        return "wav_adjust.wav"
    
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
        print("복용 시간 증가")
        pass
    
    def on_button_b(self):
        """버튼 B (Down) 처리"""
        print("복용 시간 감소")
        pass
    
    def on_button_c(self):
        """버튼 C (Back) 처리"""
        print("복용 시간 화면 뒤로가기")
        self.screen_manager.show_screen('dose_count')
    
    def on_button_d(self):
        """버튼 D (Select) 처리"""
        print("복용 시간 선택 완료")
        self.screen_manager.show_screen('main_screen')