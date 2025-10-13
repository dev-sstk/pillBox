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
        self.auto_advance_time = 1000  # 1초 후 자동 진행
        
        # UI 스타일 시스템 초기화
        self.ui_style = UIStyle()
        
        # WiFi 자동 연결 상태
        self.wifi_auto_connect_started = False
        self.wifi_auto_connect_done = False
        self.wifi_connected = False
        self.wifi_connected_time = 0  # WiFi 연결 성공 시각 기록
        
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
        self.logo_container.align(lv.ALIGN.CENTER, 0, 0)  # 완전히 중앙에 배치
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
        """로딩 영역 생성 - 제거됨"""
        # 로딩 텍스트와 프로그레스 바 제거
        pass
    
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
        
        # WiFi 연결 완료되면 즉시 전환
        if self.wifi_auto_connect_done:
            # WiFi 연결 시도 완료 (성공/실패 관계없이 즉시 전환)
            print(f"✅ WiFi 연결 시도 완료, Wi-Fi 스캔 화면으로 이동")
            self._go_to_wifi_setup()
    
    def _start_loading_animation(self):
        """로딩 애니메이션 시작"""
        print("🔄 로딩 애니메이션 시작 (텍스트/프로그레스 바 없음)")
    
    def _stop_loading_animation(self):
        """로딩 애니메이션 정지"""
        print("⏹️ 로딩 애니메이션 정지")
    
    def _try_wifi_auto_connect(self):
        """WiFi 자동 연결 시도"""
        if self.wifi_auto_connect_started:
            return
        
        self.wifi_auto_connect_started = True
        print("📡 WiFi 자동 연결 시도 시작...")
        
        try:
            # wifi_manager 전역 인스턴스 가져오기
            from wifi_manager import wifi_manager
            
            # 저장된 WiFi 설정으로 자동 연결 시도 (타임아웃 800ms로 단축)
            success = wifi_manager.try_auto_connect(timeout=800)
            
            if success:
                print("✅ WiFi 자동 연결 성공!")
                self.wifi_connected = True
                self.wifi_connected_time = time.ticks_ms()  # 연결 성공 시각 기록
            else:
                print("⚠️ WiFi 자동 연결 실패 (저장된 설정 없거나 연결 실패)")
                # 연결 실패해도 계속 진행
            
            self.wifi_auto_connect_done = True
            
        except Exception as e:
            print(f"❌ WiFi 자동 연결 오류: {e}")
            self.wifi_auto_connect_done = True
    
    def _update_loading_progress(self, elapsed_time):
        """로딩 진행률 업데이트"""
        # 즉시 WiFi 연결 시도 (WiFi 연결 자체가 딜레이가 되어 로고 표시 시간 확보)
        if not self.wifi_auto_connect_started:
            print(f"📱 WiFi 연결 시도 즉시 시작")
            self._try_wifi_auto_connect()
    
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
        # 짧은 대기 후 화면 전환
        time.sleep(0.2)
        
        # wifi_scan 화면이 등록되어 있는지 확인
        if 'wifi_scan' not in self.screen_manager.screens:
            print("📱 wifi_scan 화면이 등록되지 않음. 동적 생성 중...")
            try:
                from screens.wifi_scan_screen import WifiScanScreen
                wifi_scan_screen = WifiScanScreen(self.screen_manager)
                self.screen_manager.register_screen('wifi_scan', wifi_scan_screen)
                print("✅ wifi_scan 화면 생성 및 등록 완료")
            except Exception as e:
                print(f"❌ wifi_scan 화면 생성 실패: {e}")
                import sys
                sys.print_exception(e)
                return
        
        # 화면 전환
        print("📱 Wi-Fi 스캔 화면으로 전환")
        self.screen_manager.show_screen('wifi_scan')