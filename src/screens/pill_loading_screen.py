"""
알약 충전 화면
알약을 디스크에 충전하는 화면
"""

import time
import lvgl as lv

class PillLoadingScreen:
    """알약 충전 화면 클래스 (간단한 버전)"""
    
    def __init__(self, screen_manager):
        """알약 충전 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = 'pill_loading'
        self.screen_obj = None
        self.selected_disk = 1  # 1, 2, 3 디스크
        self.loading_step = 0  # 0-4 (한 번에 3칸씩, 총 5단계)
        self.is_loading = False
        
        # 모터 시스템은 나중에 초기화
        self.motor_system = None
        
        # 간단한 화면 생성
        self._create_simple_screen()
        
        print(f"✅ {self.screen_name} 화면 초기화 완료")
    
    def _create_simple_screen(self):
        """Modern/Xiaomi-like 디스크 카드 스타일 화면 생성"""
        print(f"  📱 {self.screen_name} 디스크 카드 스타일 화면 생성 시작...")
        
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
        title_label.set_text("알약 충전")
        title_label.set_style_text_color(lv.color_hex(0x333333), 0)  # 다크 그레이
        # 한국어 폰트 적용
        korean_font = getattr(lv, "font_notosans_kr_regular", None)
        if korean_font:
            title_label.set_style_text_font(korean_font, 0)
        title_label.align(lv.ALIGN.TOP_MID, 0, 15)
        print(f"  ✅ 제목 라벨 생성 완료")
        
        # 디스크 카드 컨테이너 생성
        print(f"  📱 디스크 카드 컨테이너 생성...")
        self.disk_container = lv.obj(self.screen_obj)
        self.disk_container.set_size(120, 80)
        self.disk_container.align(lv.ALIGN.CENTER, 0, 0)
        self.disk_container.set_style_bg_opa(0, 0)  # 투명 배경
        
        # 디스크 카드들 생성 (3개 디스크)
        self.disk_cards = []
        self.selected_disk_index = 0
        
        for i in range(3):  # 3개 디스크
            # 디스크 카드 생성
            disk_card = lv.obj(self.disk_container)
            disk_card.set_size(35, 35)
            disk_card.set_pos(5 + i * 40, 20)
            
            # 카드 스타일 (Modern/Xiaomi-like)
            disk_card.set_style_bg_color(lv.color_hex(0xF7F7F7), 0)  # 카드 배경
            disk_card.set_style_bg_opa(255, 0)
            disk_card.set_style_radius(10, 0)  # 둥근 모서리
            disk_card.set_style_border_width(1, 0)
            disk_card.set_style_border_color(lv.color_hex(0xE0E0E0), 0)  # 테두리
            disk_card.set_style_pad_all(5, 0)
            
            # 디스크 번호 라벨
            disk_label = lv.label(disk_card)
            disk_label.set_text(f"디스크\n{i+1}")
            disk_label.set_style_text_color(lv.color_hex(0x333333), 0)
            if korean_font:
                disk_label.set_style_text_font(korean_font, 0)
            disk_label.align(lv.ALIGN.CENTER, 0, 0)
            
            self.disk_cards.append(disk_card)
        
        # 현재 선택된 카드 하이라이트
        self._update_disk_selection()
        
        # 상태 표시 라벨
        self.status_label = lv.label(self.screen_obj)
        self.status_label.set_text("디스크를 선택하고 D를 누르세요")
        self.status_label.set_style_text_color(lv.color_hex(0x666666), 0)
        if korean_font:
            self.status_label.set_style_text_font(korean_font, 0)
        self.status_label.align(lv.ALIGN.BOTTOM_MID, 0, -20)
        
        print(f"  ✅ 디스크 카드 화면 생성 완료")
    
    def _update_disk_selection(self):
        """선택된 디스크 카드 하이라이트 업데이트"""
        for i, card in enumerate(self.disk_cards):
            if i == self.selected_disk_index:
                # 선택된 카드 - 민트 색상
                card.set_style_bg_color(lv.color_hex(0x00C9A7), 0)
                card.set_style_border_color(lv.color_hex(0x00C9A7), 0)
                card.set_style_border_width(2, 0)
            else:
                # 일반 카드 - 회색
                card.set_style_bg_color(lv.color_hex(0xF7F7F7), 0)
                card.set_style_border_color(lv.color_hex(0xE0E0E0), 0)
                card.set_style_border_width(1, 0)
    
    def get_title(self):
        """화면 제목"""
        return "알약 충전"
    
    def get_button_hints(self):
        """버튼 힌트"""
        return "A:위  B:아래  C:뒤로  D:충전"
    
    def get_voice_file(self):
        """안내 음성 파일"""
        return "wav_pill_loading_prompt.wav"
    
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
        """버튼 A (위) 처리 - 디스크 선택 위로"""
        if self.selected_disk_index > 0:
            self.selected_disk_index -= 1
            self._update_disk_selection()
            print(f"디스크 {self.selected_disk_index + 1} 선택")
    
    def on_button_b(self):
        """버튼 B (아래) 처리 - 디스크 선택 아래로"""
        if self.selected_disk_index < 2:  # 3개 디스크 (0,1,2)
            self.selected_disk_index += 1
            self._update_disk_selection()
            print(f"디스크 {self.selected_disk_index + 1} 선택")
    
    def on_button_c(self):
        """버튼 C (뒤로) 처리"""
        print("알약 충전 화면 뒤로가기")
        self.screen_manager.show_screen('settings')
    
    def on_button_d(self):
        """버튼 D (충전) 처리"""
        selected_disk = self.selected_disk_index
        print(f"디스크 {selected_disk + 1} 알약 충전 시작")
        
        # 상태 업데이트
        if hasattr(self, 'status_label'):
            self.status_label.set_text(f"디스크 {selected_disk + 1} 충전 중...")
        
        # TODO: 실제 모터 제어 연동
        # motor_system = self.screen_manager.app.get_motor_system()
        # motor_system.load_pills(selected_disk, compartments=3)
        
        # 시뮬레이션
        print(f"디스크 {selected_disk + 1}에서 3칸 회전하여 알약 충전 완료")
        
        # 상태 업데이트
        if hasattr(self, 'status_label'):
            self.status_label.set_text("알약 충전 완료!")
        
        # 잠시 후 메인 화면으로 이동
        import time
        time.sleep(2)
        self.screen_manager.show_screen('main_screen')