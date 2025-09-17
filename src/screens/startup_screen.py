"""
시작 화면
필박스 로고와 초기 메시지를 표시하는 화면
"""

import time
import lvgl as lv

class StartupScreen:
    """시작 화면 클래스 (간단한 버전)"""
    
    def __init__(self, screen_manager):
        """시작 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = 'startup'
        self.screen_obj = None
        self.start_time = time.ticks_ms()
        self.auto_advance_time = 5000  # 5초 후 자동 진행
        
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
        
        # 한글 폰트 로드 (안전하게)
        print(f"  📱 한글 폰트 로드...")
        korean_font = getattr(lv, "font_notosans_kr_regular", None)
        if korean_font:
            print(f"  ✅ 한글 폰트 로드 성공")
        else:
            print(f"  ⚠️ 한글 폰트 없음, 기본 폰트 사용")
        
        # 제목 라벨 생성 (화면 중앙에 배치)
        print(f"  📱 제목 라벨 생성...")
        title_label = lv.label(self.screen_obj)
        if korean_font:
            title_label.set_style_text_font(korean_font, 0)  # 폰트 먼저 설정
        title_label.set_text("필박스")  # 한글 텍스트
        title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)  # 흰색으로 변경
        title_label.align(lv.ALIGN.CENTER, 0, -10)  # 화면 중앙에서 약간 위로
        print(f"  ✅ 제목 라벨 생성 완료")
        
        # 부제목 라벨 생성
        print(f"  📱 부제목 라벨 생성...")
        subtitle_label = lv.label(self.screen_obj)
        if korean_font:
            subtitle_label.set_style_text_font(korean_font, 0)
        subtitle_label.set_text("스마트 알약 디스펜서")  # 부제목 텍스트
        subtitle_label.set_style_text_color(lv.color_hex(0x00C9A7), 0)  # 민트색으로 설정
        subtitle_label.align(lv.ALIGN.CENTER, 0, 10)  # 제목 아래에 배치
        print(f"  ✅ 부제목 라벨 생성 완료")
    
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
        current_time = time.ticks_ms()
        elapsed_time = time.ticks_diff(current_time, self.start_time)
        
        # 자동 진행 (5초 후)
        if elapsed_time >= self.auto_advance_time:
            print(f"⏰ {elapsed_time}ms 경과, Wi-Fi 설정 화면으로 자동 이동")
            self._go_to_wifi_setup()
    
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
        self.screen_manager.show_screen('wifi_scan')