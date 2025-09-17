"""
메인 화면
오늘의 알약 일정을 표시하는 대시보드 화면
"""

import time
import lvgl as lv

class MainScreen:
    """메인 화면 클래스 (간단한 버전)"""
    
    def __init__(self, screen_manager):
        """메인 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = 'main_screen'
        self.screen_obj = None
        self.current_dose_index = 0
        self.dose_schedule = []  # 복용 일정
        self.last_update_time = 0
        
        # 샘플 데이터 초기화
        self._init_sample_data()
        
        # 간단한 화면 생성
        self._create_simple_screen()
        
        print(f"✅ {self.screen_name} 화면 초기화 완료")
    
    def _init_sample_data(self):
        """샘플 데이터 초기화"""
        # 샘플 복용 일정 (오전 8시, 오후 2시, 오후 8시)
        self.dose_schedule = [
            {"time": "08:00", "taken": False, "medication": "비타민"},
            {"time": "14:00", "taken": False, "medication": "아스피린"},
            {"time": "20:00", "taken": False, "medication": "칼슘"}
        ]
    
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
        label.set_text("메인 화면")
        # 한국어 폰트 적용
        korean_font = getattr(lv, "font_notosans_kr_regular", None)
        if korean_font:
            label.set_style_text_font(korean_font, 0)
        label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        label.align(lv.ALIGN.CENTER, 0, 0)
        print(f"  ✅ 라벨 생성 완료")
    
    def get_title(self):
        """화면 제목"""
        return "메인 화면"
    
    def get_button_hints(self):
        """버튼 힌트"""
        return "A:이전  B:다음  C:설정  D:상세"
    
    def get_voice_file(self):
        """안내 음성 파일"""
        return "wav_main_screen.wav"
    
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
        """버튼 A (Prev) 처리"""
        print("이전 복용 정보")
        pass
    
    def on_button_b(self):
        """버튼 B (Next) 처리"""
        print("다음 복용 정보")
        pass
    
    def on_button_c(self):
        """버튼 C (Settings) 처리"""
        print("설정 화면으로 이동")
        self.screen_manager.show_screen('settings')
    
    def on_button_d(self):
        """버튼 D (Details) 처리"""
        print("복용 상세 정보")
        pass