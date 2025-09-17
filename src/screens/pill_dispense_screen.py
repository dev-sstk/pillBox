"""
알약 배출 화면
알약을 배출하는 화면 (슬라이드 덮개 제어)
"""

import time
import lvgl as lv

class PillDispenseScreen:
    """알약 배출 화면 클래스 (간단한 버전)"""
    
    def __init__(self, screen_manager):
        """알약 배출 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = 'pill_dispense'
        self.screen_obj = None
        self.door_level = 0  # 0-3 단계 (0: 닫힘, 3: 모두 열림)
        self.is_dispensing = False
        
        # 모터 시스템은 나중에 초기화
        self.motor_system = None
        
        # 간단한 화면 생성
        self._create_simple_screen()
        
        print(f"✅ {self.screen_name} 화면 초기화 완료")
    
    def _create_simple_screen(self):
        """Modern/Xiaomi-like 슬라이드 덮개 카드 스타일 화면 생성"""
        print(f"  📱 {self.screen_name} 슬라이드 덮개 카드 스타일 화면 생성 시작...")
        
        # 메모리 정리
        import gc
        gc.collect()
        print(f"  ✅ 메모리 정리 완료")
        
        # 화면 생성 (흰색 배경)
        print(f"  📱 화면 객체 생성...")
        self.screen_obj = lv.obj()
        self.screen_obj.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)  # 화이트 배경
        print(f"  ✅ 화면 객체 생성 완료")
        
        # 제목 라벨 생성
        print(f"  📱 제목 라벨 생성...")
        title_label = lv.label(self.screen_obj)
        title_label.set_text("알약 배출")
        title_label.set_style_text_color(lv.color_hex(0x333333), 0)  # 다크 그레이
        # 한국어 폰트 적용
        korean_font = getattr(lv, "font_notosans_kr_regular", None)
        if korean_font:
            title_label.set_style_text_font(korean_font, 0)
        title_label.align(lv.ALIGN.TOP_MID, 0, 15)
        print(f"  ✅ 제목 라벨 생성 완료")
        
        # 슬라이드 덮개 단계 카드 컨테이너 생성
        print(f"  📱 슬라이드 덮개 카드 컨테이너 생성...")
        self.slide_container = lv.obj(self.screen_obj)
        self.slide_container.set_size(120, 80)
        self.slide_container.align(lv.ALIGN.CENTER, 0, 0)
        self.slide_container.set_style_bg_opa(0, 0)  # 투명 배경
        
        # 슬라이드 덮개 단계 카드들 생성 (0~3 단계)
        self.slide_cards = []
        self.selected_slide_stage = 0
        
        for i in range(4):  # 0~3 단계
            # 슬라이드 카드 생성
            slide_card = lv.obj(self.slide_container)
            slide_card.set_size(25, 25)
            slide_card.set_pos(10 + i * 30, 25)
            
            # 카드 스타일 (Modern/Xiaomi-like)
            slide_card.set_style_bg_color(lv.color_hex(0xF7F7F7), 0)  # 카드 배경
            slide_card.set_style_bg_opa(255, 0)
            slide_card.set_style_radius(10, 0)  # 둥근 모서리
            slide_card.set_style_border_width(1, 0)
            slide_card.set_style_border_color(lv.color_hex(0xE0E0E0), 0)  # 테두리
            slide_card.set_style_pad_all(3, 0)
            
            # 슬라이드 단계 라벨
            slide_label = lv.label(slide_card)
            slide_label.set_text(f"{i}")
            slide_label.set_style_text_color(lv.color_hex(0x333333), 0)
            if korean_font:
                slide_label.set_style_text_font(korean_font, 0)
            slide_label.align(lv.ALIGN.CENTER, 0, 0)
            
            self.slide_cards.append(slide_card)
        
        # 현재 선택된 카드 하이라이트
        self._update_slide_selection()
        
        # 상태 표시 라벨
        self.status_label = lv.label(self.screen_obj)
        self.status_label.set_text("배출 단계를 선택하고 D를 누르세요")
        self.status_label.set_style_text_color(lv.color_hex(0x666666), 0)
        if korean_font:
            self.status_label.set_style_text_font(korean_font, 0)
        self.status_label.align(lv.ALIGN.BOTTOM_MID, 0, -20)
        
        print(f"  ✅ 슬라이드 덮개 카드 화면 생성 완료")
    
    def _update_slide_selection(self):
        """선택된 슬라이드 단계 카드 하이라이트 업데이트"""
        for i, card in enumerate(self.slide_cards):
            if i == self.selected_slide_stage:
                # 선택된 카드 - 코발트 블루 색상
                card.set_style_bg_color(lv.color_hex(0x2196F3), 0)
                card.set_style_border_color(lv.color_hex(0x2196F3), 0)
                card.set_style_border_width(2, 0)
            else:
                # 일반 카드 - 회색
                card.set_style_bg_color(lv.color_hex(0xF7F7F7), 0)
                card.set_style_border_color(lv.color_hex(0xE0E0E0), 0)
                card.set_style_border_width(1, 0)
    
    def get_title(self):
        """화면 제목"""
        return "알약 배출"
    
    def get_button_hints(self):
        """버튼 힌트"""
        return "A:위  B:아래  C:뒤로  D:배출"
    
    def get_voice_file(self):
        """안내 음성 파일"""
        return "wav_pill_dispense_prompt.wav"
    
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
        print("배출 단계 증가")
        self.door_level = min(3, self.door_level + 1)
        pass
    
    def on_button_b(self):
        """버튼 B (Down) 처리"""
        print("배출 단계 감소")
        self.door_level = max(0, self.door_level - 1)
        pass
    
    def on_button_c(self):
        """버튼 C (Back) 처리"""
        print("알약 배출 화면 뒤로가기")
        self.screen_manager.show_screen('settings')
    
    def on_button_d(self):
        """버튼 D (Dispense) 처리"""
        print(f"알약 배출 실행 - 단계 {self.door_level}")
        if not self.is_dispensing:
            self.is_dispensing = True
            # 배출 로직 실행
            self._execute_dispense()
            self.is_dispensing = False
    
    def _execute_dispense(self):
        """알약 배출 실행"""
        print(f"배출 단계 {self.door_level}로 알약 배출 중...")
        # 실제 모터 제어 로직은 나중에 구현
        time.sleep(1)  # 시뮬레이션
        print("알약 배출 완료")