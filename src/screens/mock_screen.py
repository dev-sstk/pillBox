"""
Mock 화면 클래스
아직 구현되지 않은 화면들의 기본 템플릿
"""

import time
import lvgl as lv
from ui_style import UIStyle

class MockScreen:
    """Mock 화면 클래스 - 기본 템플릿"""
    
    def __init__(self, screen_manager, screen_name, title="Mock Screen"):
        """Mock 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = screen_name
        self.title = title
        self.screen_obj = None
        
        # UI 스타일 시스템 초기화
        self.ui_style = UIStyle()
        
        # 화면 생성
        self._create_mock_screen()
        
        print(f"✅ {self.screen_name} Mock 화면 초기화 완료")
    
    def _create_mock_screen(self):
        """Mock 화면 생성"""
        print(f"  📱 {self.screen_name} Mock 화면 생성 시작...")
        
        # 메모리 정리
        import gc
        gc.collect()
        
        # 화면 생성
        self.screen_obj = lv.obj()
        
        # 화면 배경 스타일 적용
        self.ui_style.apply_screen_style(self.screen_obj)
        
        # 메인 컨테이너 생성
        self._create_main_container()
        
        # 제목 영역 생성
        self._create_title_area()
        
        # 내용 영역 생성
        self._create_content_area()
        
        # 하단 정보 영역 생성
        self._create_info_area()
        
        print(f"  ✅ {self.screen_name} Mock 화면 생성 완료")
    
    def _create_main_container(self):
        """메인 컨테이너 생성"""
        self.main_container = lv.obj(self.screen_obj)
        self.main_container.set_size(128, 160)
        self.main_container.align(lv.ALIGN.CENTER, 0, 0)
        self.main_container.set_style_bg_opa(0, 0)
        self.main_container.set_style_border_width(0, 0)
        self.main_container.set_style_pad_all(0, 0)
    
    def _create_title_area(self):
        """제목 영역 생성"""
        # 제목 컨테이너
        self.title_container = lv.obj(self.main_container)
        self.title_container.set_size(120, 40)
        self.title_container.align(lv.ALIGN.TOP_MID, 0, 10)
        self.title_container.set_style_bg_opa(0, 0)
        self.title_container.set_style_border_width(0, 0)
        self.title_container.set_style_pad_all(0, 0)
        
        # 제목 라벨
        self.title_label = self.ui_style.create_label(
            self.title_container,
            self.title,
            'text_title',
            self.ui_style.get_color('text')
        )
        self.title_label.align(lv.ALIGN.CENTER, 0, 0)
        
        # 부제목 라벨
        self.subtitle_label = self.ui_style.create_label(
            self.title_container,
            f"{self.screen_name} 화면",
            'text_caption',
            self.ui_style.get_color('text_secondary')
        )
        self.subtitle_label.align(lv.ALIGN.CENTER, 0, 15)
    
    def _create_content_area(self):
        """내용 영역 생성"""
        # 내용 컨테이너
        self.content_container = lv.obj(self.main_container)
        self.content_container.set_size(120, 80)
        self.content_container.align(lv.ALIGN.CENTER, 0, 0)
        self.content_container.set_style_bg_opa(0, 0)
        self.content_container.set_style_border_width(0, 0)
        self.content_container.set_style_pad_all(0, 0)
        
        # 상태 메시지
        self.status_label = self.ui_style.create_label(
            self.content_container,
            "이 화면은 아직 구현 중입니다.",
            'text_body',
            self.ui_style.get_color('text_secondary')
        )
        self.status_label.align(lv.ALIGN.CENTER, 0, -10)
        
        # 기능 설명
        self.desc_label = self.ui_style.create_label(
            self.content_container,
            "Mock 화면으로 테스트 중",
            'text_caption',
            self.ui_style.get_color('text_light')
        )
        self.desc_label.align(lv.ALIGN.CENTER, 0, 10)
        
        # 진행률 표시 (선택적)
        if hasattr(self, '_create_progress_indicator'):
            self._create_progress_indicator()
    
    def _create_info_area(self):
        """하단 정보 영역 생성"""
        # 정보 컨테이너
        self.info_container = lv.obj(self.main_container)
        self.info_container.set_size(120, 30)
        self.info_container.align(lv.ALIGN.BOTTOM_MID, 0, -10)
        self.info_container.set_style_bg_opa(0, 0)
        self.info_container.set_style_border_width(0, 0)
        self.info_container.set_style_pad_all(0, 0)
        
        # 버튼 힌트
        self.hint_label = self.ui_style.create_label(
            self.info_container,
            "C:뒤로가기  D:다음",
            'text_caption',
            self.ui_style.get_color('text_light')
        )
        self.hint_label.align(lv.ALIGN.CENTER, 0, 0)
    
    def get_title(self):
        """화면 제목"""
        return self.title
    
    def get_button_hints(self):
        """버튼 힌트"""
        return "C:뒤로가기  D:다음"
    
    def get_voice_file(self):
        """안내 음성 파일"""
        return f"wav_{self.screen_name}_prompt.wav"
    
    def get_effect_file(self):
        """효과음 파일"""
        return "wav_select.wav"
    
    def show(self):
        """화면 표시"""
        if self.screen_obj:
            lv.screen_load(self.screen_obj)
            print(f"✅ {self.screen_name} 화면 표시됨")
            
            # LVGL 타이머 핸들러 강제 호출
            for i in range(10):
                lv.timer_handler()
                time.sleep(0.1)
    
    def hide(self):
        """화면 숨기기"""
        pass
    
    def update(self):
        """화면 업데이트"""
        pass
    
    def on_button_a(self):
        """버튼 A 처리"""
        pass
    
    def on_button_b(self):
        """버튼 B 처리"""
        pass
    
    def on_button_c(self):
        """버튼 C (뒤로가기) 처리"""
        print(f"{self.screen_name} 화면 뒤로가기")
        # 이전 화면으로 돌아가기 (스택이 있으면)
        if hasattr(self.screen_manager, 'go_back'):
            self.screen_manager.go_back()
    
    def on_button_d(self):
        """버튼 D (다음) 처리"""
        print(f"{self.screen_name} 화면 다음으로")
        # 다음 화면으로 이동 (기본적으로 메인 화면)
        self.screen_manager.show_screen('main')

# 특화된 Mock 화면들
class WifiScanMockScreen(MockScreen):
    """Wi-Fi 스캔 Mock 화면"""
    
    def __init__(self, screen_manager):
        super().__init__(screen_manager, "wifi_scan", "Wi-Fi 스캔")
        self._create_wifi_list()
    
    def _create_wifi_list(self):
        """Wi-Fi 목록 생성"""
        # Wi-Fi 목록 컨테이너
        self.wifi_container = lv.obj(self.content_container)
        self.wifi_container.set_size(100, 60)
        self.wifi_container.align(lv.ALIGN.CENTER, 0, 0)
        self.wifi_container.set_style_bg_opa(0, 0)
        self.wifi_container.set_style_border_width(0, 0)
        
        # Wi-Fi 목록
        wifi_networks = ["Home_WiFi", "Office_Network", "Guest_WiFi"]
        for i, network in enumerate(wifi_networks):
            wifi_label = self.ui_style.create_label(
                self.wifi_container,
                f"📶 {network}",
                'text_body',
                self.ui_style.get_color('text')
            )
            wifi_label.align(lv.ALIGN.TOP_MID, 0, i * 15)

class WifiPasswordMockScreen(MockScreen):
    """Wi-Fi 비밀번호 Mock 화면"""
    
    def __init__(self, screen_manager, ssid="Example_SSID"):
        super().__init__(screen_manager, "wifi_password", "Wi-Fi 비밀번호")
        self.ssid = ssid
        self._create_password_input()
    
    def _create_password_input(self):
        """비밀번호 입력 영역 생성"""
        # SSID 표시
        ssid_label = self.ui_style.create_label(
            self.content_container,
            f"네트워크: {self.ssid}",
            'text_body',
            self.ui_style.get_color('text')
        )
        ssid_label.align(lv.ALIGN.CENTER, 0, -20)
        
        # 비밀번호 입력 필드 (시뮬레이션)
        password_label = self.ui_style.create_label(
            self.content_container,
            "비밀번호: ********",
            'text_body',
            self.ui_style.get_color('text_secondary')
        )
        password_label.align(lv.ALIGN.CENTER, 0, 0)

class DoseCountMockScreen(MockScreen):
    """복용량 설정 Mock 화면"""
    
    def __init__(self, screen_manager):
        super().__init__(screen_manager, "dose_count", "복용량 설정")
        self.dose_count = 1
        self._create_dose_selector()
    
    def _create_dose_selector(self):
        """복용량 선택기 생성"""
        # 현재 복용량 표시
        count_label = self.ui_style.create_label(
            self.content_container,
            f"복용량: {self.dose_count}개",
            'text_title',
            self.ui_style.get_color('primary')
        )
        count_label.align(lv.ALIGN.CENTER, 0, -10)
        
        # 조정 안내
        adjust_label = self.ui_style.create_label(
            self.content_container,
            "A: 감소  B: 증가",
            'text_caption',
            self.ui_style.get_color('text_light')
        )
        adjust_label.align(lv.ALIGN.CENTER, 0, 10)

class DoseTimeMockScreen(MockScreen):
    """복용 시간 설정 Mock 화면"""
    
    def __init__(self, screen_manager, dose_count=2):
        super().__init__(screen_manager, "dose_time", "복용 시간 설정")
        self.dose_count = dose_count
        self._create_time_selector()
    
    def _create_time_selector(self):
        """시간 선택기 생성"""
        # 복용 횟수 표시
        count_label = self.ui_style.create_label(
            self.content_container,
            f"복용 횟수: {self.dose_count}회",
            'text_body',
            self.ui_style.get_color('text')
        )
        count_label.align(lv.ALIGN.CENTER, 0, -20)
        
        # 시간 설정 안내
        time_label = self.ui_style.create_label(
            self.content_container,
            "복용 시간 설정",
            'text_body',
            self.ui_style.get_color('text_secondary')
        )
        time_label.align(lv.ALIGN.CENTER, 0, 0)

class MainMockScreen(MockScreen):
    """메인 Mock 화면"""
    
    def __init__(self, screen_manager):
        super().__init__(screen_manager, "main", "메인 화면")
        self._create_main_dashboard()
    
    def _create_main_dashboard(self):
        """메인 대시보드 생성"""
        # 상태 카드들
        status_cards = [
            ("다음 복용", "10:00"),
            ("남은 알약", "15개"),
            ("연결 상태", "Wi-Fi 연결됨")
        ]
        
        for i, (title, value) in enumerate(status_cards):
            card = lv.obj(self.content_container)
            card.set_size(35, 25)
            card.align(lv.ALIGN.TOP_LEFT, 5 + i * 40, 0)
            card.set_style_bg_color(lv.color_hex(self.ui_style.get_color('card')), 0)
            card.set_style_bg_opa(255, 0)
            card.set_style_radius(8, 0)
            
            # 카드 제목
            card_title = self.ui_style.create_label(
                card,
                title,
                'text_caption',
                self.ui_style.get_color('text_secondary')
            )
            card_title.align(lv.ALIGN.TOP_MID, 0, 2)
            
            # 카드 값
            card_value = self.ui_style.create_label(
                card,
                value,
                'text_body',
                self.ui_style.get_color('text')
            )
            card_value.align(lv.ALIGN.BOTTOM_MID, 0, -2)

class NotificationMockScreen(MockScreen):
    """알림 Mock 화면"""
    
    def __init__(self, screen_manager, notification_data):
        super().__init__(screen_manager, "notification", "알림")
        self.notification_data = notification_data
        self._create_notification_content()
    
    def _create_notification_content(self):
        """알림 내용 생성"""
        # 알림 아이콘
        icon_label = self.ui_style.create_label(
            self.content_container,
            "🔔",
            'text_title',
            self.ui_style.get_color('alert')
        )
        icon_label.align(lv.ALIGN.CENTER, 0, -20)
        
        # 알림 메시지
        message_label = self.ui_style.create_label(
            self.content_container,
            "알약 복용 시간입니다!",
            'text_body',
            self.ui_style.get_color('text')
        )
        message_label.align(lv.ALIGN.CENTER, 0, 0)
        
        # 시간 정보
        time_label = self.ui_style.create_label(
            self.content_container,
            f"시간: {self.notification_data.get('time', '10:00')}",
            'text_caption',
            self.ui_style.get_color('text_secondary')
        )
        time_label.align(lv.ALIGN.CENTER, 0, 15)

class SettingsMockScreen(MockScreen):
    """설정 Mock 화면"""
    
    def __init__(self, screen_manager):
        super().__init__(screen_manager, "settings", "설정")
        self._create_settings_menu()
    
    def _create_settings_menu(self):
        """설정 메뉴 생성"""
        settings_items = [
            "Wi-Fi 설정",
            "복용량 조정",
            "시간 설정",
            "알림 설정"
        ]
        
        for i, item in enumerate(settings_items):
            item_label = self.ui_style.create_label(
                self.content_container,
                f"⚙️ {item}",
                'text_body',
                self.ui_style.get_color('text')
            )
            item_label.align(lv.ALIGN.TOP_MID, 0, -20 + i * 12)

class PillLoadingMockScreen(MockScreen):
    """알약 로딩 Mock 화면"""
    
    def __init__(self, screen_manager):
        super().__init__(screen_manager, "pill_loading", "알약 로딩")
        self._create_loading_interface()
    
    def _create_loading_interface(self):
        """로딩 인터페이스 생성"""
        # 로딩 아이콘
        loading_label = self.ui_style.create_label(
            self.content_container,
            "💊",
            'text_title',
            self.ui_style.get_color('primary')
        )
        loading_label.align(lv.ALIGN.CENTER, 0, -10)
        
        # 로딩 메시지
        message_label = self.ui_style.create_label(
            self.content_container,
            "알약을 넣어주세요",
            'text_body',
            self.ui_style.get_color('text')
        )
        message_label.align(lv.ALIGN.CENTER, 0, 10)

class PillDispenseMockScreen(MockScreen):
    """알약 배출 Mock 화면"""
    
    def __init__(self, screen_manager):
        super().__init__(screen_manager, "pill_dispense", "알약 배출")
        self._create_dispense_interface()
    
    def _create_dispense_interface(self):
        """배출 인터페이스 생성"""
        # 배출 아이콘
        dispense_label = self.ui_style.create_label(
            self.content_container,
            "💊",
            'text_title',
            self.ui_style.get_color('success')
        )
        dispense_label.align(lv.ALIGN.CENTER, 0, -10)
        
        # 배출 메시지
        message_label = self.ui_style.create_label(
            self.content_container,
            "알약을 배출합니다",
            'text_body',
            self.ui_style.get_color('text')
        )
        message_label.align(lv.ALIGN.CENTER, 0, 10)
