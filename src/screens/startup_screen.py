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
        self.auto_advance_time = 5000  # 5초 후 자동 진행
        
        # UI 스타일 시스템 초기화
        self.ui_style = UIStyle()
        
        # 로딩 상태 관리
        self.loading_progress = 0
        self.loading_steps = [
            "시스템 초기화 중...",
            "디스플레이 설정 중...",
            "오디오 준비 중...",
            "Wi-Fi 연결 준비 중...",
            "준비 완료!"
        ]
        self.current_step = 0
        
        # 화면 생성
        self._create_modern_screen()
        
        print(f"✅ {self.screen_name} 화면 초기화 완료")
    
    def _create_modern_screen(self):
        """Modern 스타일 화면 생성"""
        print(f"  📱 {self.screen_name} Modern 화면 생성 시작...")
        
        # 메모리 정리
        import gc
        gc.collect()
        print(f"  ✅ 메모리 정리 완료")
        
        # 화면 생성
        print(f"  📱 화면 객체 생성...")
        self.screen_obj = lv.obj()
        
        # 화면 배경 스타일 적용
        self.ui_style.apply_screen_style(self.screen_obj)
        
        # 스크롤바 비활성화
        self.screen_obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.screen_obj.set_scroll_dir(lv.DIR.NONE)
        
        print(f"  ✅ 화면 객체 생성 완료")
        
        # 메인 컨테이너 생성
        self._create_main_container()
        
        # 로고 영역 생성
        self._create_logo_area()
        
        # 로딩 영역 생성
        self._create_loading_area()
        
        # 하단 정보 영역 생성
        self._create_info_area()
        
        print(f"  ✅ Modern 화면 생성 완료")
    
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
        self.logo_container.set_size(120, 80)
        self.logo_container.align(lv.ALIGN.CENTER, 0, -10)  # 화면 정중앙으로 이동
        self.logo_container.set_style_bg_opa(0, 0)
        self.logo_container.set_style_border_width(0, 0)
        self.logo_container.set_style_pad_all(0, 0)
        
        # 로고 컨테이너 스크롤바 비활성화
        self.logo_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.logo_container.set_scroll_dir(lv.DIR.NONE)
        
        # 필박스 아이콘 (원형 배경) - 사이즈 확대
        self.icon_bg = lv.obj(self.logo_container)
        self.icon_bg.set_size(68, 68)  # 64x64에서 68x68로 확대
        self.icon_bg.align(lv.ALIGN.CENTER, 0, 0)  # 완전히 중앙에 배치
        
        # 아이콘 배경 스크롤바 비활성화
        self.icon_bg.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.icon_bg.set_scroll_dir(lv.DIR.NONE)
        self.icon_bg.set_style_bg_color(lv.color_hex(self.ui_style.get_color('primary')), 0)
        self.icon_bg.set_style_bg_opa(255, 0)
        self.icon_bg.set_style_radius(34, 0)  # 반지름도 34로 조정
        self.icon_bg.set_style_border_width(0, 0)
        
        # 필박스 아이콘 텍스트
        self.icon_text = lv.label(self.icon_bg)
        self.icon_text.set_text("PILLBOX")  # PILLBOX 텍스트
        self.icon_text.align(lv.ALIGN.CENTER, 0, 0)
        self.icon_text.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        self.icon_text.set_style_text_font(self.ui_style.get_font('title'), 0)
        
        # 아이콘 텍스트 스크롤바 비활성화
        self.icon_text.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.icon_text.set_scroll_dir(lv.DIR.NONE)
        
        # 제목 제거됨
        
        # 부제목 제거됨
    
    def _create_loading_area(self):
        """로딩 영역 생성 - 버전 텍스트 바로 위에 배치"""
        # 로딩 컨테이너 (하단으로 이동)
        self.loading_container = lv.obj(self.main_container)
        self.loading_container.set_size(120, 40)
        self.loading_container.align(lv.ALIGN.BOTTOM_MID, 0, -10)  # 하단에서 10px 위
        self.loading_container.set_style_bg_opa(0, 0)
        self.loading_container.set_style_border_width(0, 0)
        self.loading_container.set_style_pad_all(0, 0)
        
        # 로딩 컨테이너 스크롤바 비활성화
        self.loading_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.loading_container.set_scroll_dir(lv.DIR.NONE)
        
        # 로딩 상태 텍스트 (작은 사이즈)
        self.loading_text = self.ui_style.create_label(
            self.loading_container,
            self.loading_steps[0],
            'text_caption',  # 작은 폰트 (12px 효과)
            self.ui_style.get_color('text_secondary')
        )
        self.loading_text.align(lv.ALIGN.CENTER, 0, -8)
        
        # 로딩 텍스트 스크롤바 비활성화
        self.loading_text.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.loading_text.set_scroll_dir(lv.DIR.NONE)
        
        # 작은 사이즈 효과 적용
        try:
            self.loading_text.set_style_text_color(lv.color_hex(0x666666), 0)  # 작은 텍스트 톤
            self.loading_text.set_style_text_letter_space(-2, 0)  # 더 좁은 간격
            # 폰트 크기 직접 조정
            self.loading_text.set_style_text_font(self.ui_style.get_font('text_small'), 0)
        except:
            pass
        
        # 프로그레스 바
        self.progress_bar = lv.bar(self.loading_container)
        self.progress_bar.set_size(100, 6)  # 높이를 더 작게
        self.progress_bar.align(lv.ALIGN.CENTER, 0, 5)
        self.progress_bar.set_range(0, 100)
        self.progress_bar.set_value(0, 0)  # 애니메이션 없이 설정
        self.progress_bar.set_style_bg_color(lv.color_hex(self.ui_style.get_color('card')), 0)
        self.progress_bar.set_style_bg_opa(255, 0)
        self.progress_bar.set_style_radius(3, 0)
        
        # 프로그레스 바 스크롤바 비활성화
        self.progress_bar.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.progress_bar.set_scroll_dir(lv.DIR.NONE)
        
        # 애니메이션 시간 설정 (ESP32 LVGL 호환)
        try:
            self.progress_bar.set_style_anim_time(500, 0)
        except AttributeError:
            print("⚠️ set_style_anim_time 지원 안됨, 건너뛰기")
        
        # 프로그레스 바 색상 설정 (ESP32 LVGL 호환)
        try:
            self.progress_bar.set_style_bg_color(lv.color_hex(self.ui_style.get_color('primary')), lv.PART.INDICATOR)
            self.progress_bar.set_style_radius(3, lv.PART.INDICATOR)
        except AttributeError:
            # ESP32 LVGL에서는 다른 방식으로 설정
            print("⚠️ lv.PART.INDICATOR 지원 안됨, 기본 스타일 사용")
    
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
            print(f"✅ {self.screen_name} 화면 표시됨")
            
            # 로딩 애니메이션 시작
            self._start_loading_animation()
            
            # LVGL 타이머 핸들러 강제 호출
            print(f"📱 {self.screen_name} 화면 강제 업데이트 시작...")
            for i in range(10):
                lv.timer_handler()
                time.sleep(0.1)
            print(f"✅ {self.screen_name} 화면 강제 업데이트 완료")
    
    def hide(self):
        """화면 숨기기"""
        # 로딩 애니메이션 정지
        self._stop_loading_animation()
    
    def update(self):
        """화면 업데이트 - 로딩 진행 및 자동 전환"""
        current_time = time.ticks_ms()
        elapsed_time = time.ticks_diff(current_time, self.start_time)
        
        # 로딩 진행 업데이트
        self._update_loading_progress(elapsed_time)
        
        # 자동 진행 (5초 후)
        if elapsed_time >= self.auto_advance_time:
            print(f"⏰ {elapsed_time}ms 경과, Wi-Fi 설정 화면으로 자동 이동")
            self._go_to_wifi_setup()
    
    def _start_loading_animation(self):
        """로딩 애니메이션 시작"""
        self.loading_progress = 0
        self.current_step = 0
        self.progress_bar.set_value(0, 0)  # 애니메이션 없이 설정
        self.loading_text.set_text(self.loading_steps[0])
        print("🔄 로딩 애니메이션 시작")
    
    def _stop_loading_animation(self):
        """로딩 애니메이션 정지"""
        print("⏹️ 로딩 애니메이션 정지")
    
    def _update_loading_progress(self, elapsed_time):
        """로딩 진행률 업데이트"""
        # 5초 동안 100% 완료
        progress = min(100, (elapsed_time / self.auto_advance_time) * 100)
        
        # 프로그레스 바 업데이트
        if hasattr(self, 'progress_bar'):
            self.progress_bar.set_value(int(progress), 1)  # 애니메이션과 함께 설정
        
        # 단계별 텍스트 업데이트
        step_progress = progress / 20  # 5단계로 나누기
        new_step = min(4, int(step_progress))
        
        if new_step != self.current_step and new_step < len(self.loading_steps):
            self.current_step = new_step
            if hasattr(self, 'loading_text'):
                self.loading_text.set_text(self.loading_steps[self.current_step])
                print(f"📱 로딩 단계: {self.loading_steps[self.current_step]}")
    
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
        # 로딩 완료 표시
        if hasattr(self, 'loading_text'):
            self.loading_text.set_text("준비 완료!")
        if hasattr(self, 'progress_bar'):
            self.progress_bar.set_value(100, 1)  # 애니메이션과 함께 설정
        
        # 잠시 대기 후 화면 전환
        time.sleep(0.5)
        self.screen_manager.show_screen('wifi_scan')