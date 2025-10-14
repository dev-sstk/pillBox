"""
설정 화면
다양한 설정 옵션을 제공하는 메뉴 화면
Modern UI 스타일 적용
"""

import time
import lvgl as lv
from ui_style import UIStyle
# from wifi_manager import wifi_manager  # 필요시 사용
from machine import RTC

class SettingsScreen:
    """설정 화면 클래스 - Modern UI 스타일"""
    
    def __init__(self, screen_manager):
        """설정 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = 'settings'
        self.screen_obj = None
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible_items = 4
        
        # 설정 카테고리 정의
        self.settings_categories = [
            {
                "name": "네트워크 설정",
                "icon": "📶",
                "items": [
                    {"name": "Wi-Fi 연결", "action": "wifi_scan", "status": "연결됨"},
                    {"name": "네트워크 상태", "action": "wifi_status", "status": "양호"},
                    {"name": "연결 품질", "action": "wifi_quality", "status": "강함"}
                ]
            },
            {
                "name": "복용 관리",
                "icon": "💊",
                "items": [
                    {"name": "복용 횟수", "action": "dose_count", "status": "2회"},
                    {"name": "복용 시간", "action": "dose_time", "status": "08:00, 20:00"},
                    {"name": "복용 일수", "action": "dose_days", "status": "30일"},
                    {"name": "알림 설정", "action": "notification", "status": "활성화"}
                ]
            },
            {
                "name": "알약 관리",
                "icon": "🔄",
                "items": [
                    {"name": "알약 충전", "action": "pill_loading", "status": "준비됨"},
                    {"name": "수동 배출", "action": "pill_dispense", "status": "가능"},
                    {"name": "디스크 상태", "action": "disk_status", "status": "정상"},
                    {"name": "리필 알림", "action": "refill_alert", "status": "활성화"}
                ]
            },
            {
                "name": "시스템 설정",
                "icon": "⚙️",
                "items": [
                    {"name": "시간 동기화", "action": "time_sync", "status": "동기화됨"},
                    {"name": "배터리 상태", "action": "battery", "status": "85%"},
                    {"name": "시스템 정보", "action": "system_info", "status": "v1.0.0"},
                    {"name": "화면 밝기", "action": "brightness", "status": "80%"},
                    {"name": "음성 안내", "action": "voice_guide", "status": "활성화"},
                    {"name": "자동 절전", "action": "sleep_mode", "status": "5분"}
                ]
            }
        ]
        
        # 현재 선택된 카테고리와 아이템
        self.current_category = 0
        self.current_item = 0
        self.view_mode = "category"  # "category" 또는 "item"
        
        # UI 스타일 시스템 초기화
        self.ui_style = UIStyle()
        
        # 시스템 정보
        self.rtc = RTC()
        self.wifi_status = {"connected": False, "ssid": None}
        self.battery_level = 85
        
        # Modern 화면 생성
        self._create_modern_screen()
        
        print(f"✅ {self.screen_name} 화면 초기화 완료")
    
    def _create_modern_screen(self):
        """Modern 스타일 화면 생성"""
        print(f"  📱 {self.screen_name} Modern 화면 생성 시작...")
        
        # 메모리 정리
        import gc
        gc.collect()
        print("  ✅ 메모리 정리 완료")
        
        # 화면 생성
        print("  📱 화면 객체 생성...")
        self.screen_obj = lv.obj()
        print(f"  📱 화면 객체 생성됨: {self.screen_obj}")
        
        # 화면 배경 스타일 적용
        self.ui_style.apply_screen_style(self.screen_obj)
        
        # 메인 컨테이너 생성
        self._create_main_container()
        
        # 헤더 영역 생성
        self._create_header_area()
        
        # 카테고리/아이템 리스트 영역 생성
        self._create_list_area()
        
        # 하단 정보 영역 생성
        self._create_footer_area()
        
        print(f"  ✅ {self.screen_name} Modern 화면 생성 완료")
    
    def _create_main_container(self):
        """메인 컨테이너 생성"""
        self.main_container = lv.obj(self.screen_obj)
        self.main_container.set_size(128, 160)
        self.main_container.align(lv.ALIGN.CENTER, 0, 0)
        self.main_container.set_style_bg_opa(0, 0)
        self.main_container.set_style_border_width(0, 0)
        self.main_container.set_style_pad_all(0, 0)
    
    def _create_header_area(self):
        """헤더 영역 생성"""
        # 헤더 컨테이너
        self.header_container = lv.obj(self.main_container)
        self.header_container.set_size(120, 30)
        self.header_container.align(lv.ALIGN.TOP_MID, 0, 5)
        self.header_container.set_style_bg_opa(0, 0)
        self.header_container.set_style_border_width(0, 0)
        self.header_container.set_style_pad_all(0, 0)
        
        # 제목 라벨
        self.title_label = self.ui_style.create_label(
            self.header_container,
            "설정",
            'text_title',
            self.ui_style.get_color('text')
        )
        self.title_label.align(lv.ALIGN.LEFT_MID, 0, 0)
        
        # 현재 시간 표시
        self.time_label = self.ui_style.create_label(
            self.header_container,
            self._get_current_time(),
            'text_caption',
            self.ui_style.get_color('text_secondary')
        )
        self.time_label.align(lv.ALIGN.RIGHT_MID, 0, 0)
    
    def _create_list_area(self):
        """리스트 영역 생성"""
        # 리스트 컨테이너
        self.list_container = lv.obj(self.main_container)
        self.list_container.set_size(120, 100)
        self.list_container.align(lv.ALIGN.CENTER, 0, 0)
        self.list_container.set_style_bg_opa(0, 0)
        self.list_container.set_style_border_width(0, 0)
        self.list_container.set_style_pad_all(0, 0)
        
        # 리스트 아이템들 생성
        self._create_list_items()
    
    def _create_list_items(self):
        """리스트 아이템들 생성"""
        if self.view_mode == "category":
            self._create_category_items()
        else:
            self._create_item_list()
    
    def _create_category_items(self):
        """카테고리 아이템들 생성"""
        # 기존 아이템들 정리
        self._clear_list_items()
        
        # 카테고리 아이템들 생성
        for i, category in enumerate(self.settings_categories):
            if i < self.max_visible_items:
                item = self._create_category_item(category, i)
                self.list_items.append(item)
    
    def _create_category_item(self, category, index):
        """카테고리 아이템 생성"""
        # 아이템 컨테이너
        item_container = lv.obj(self.list_container)
        item_container.set_size(115, 22)
        item_container.align(lv.ALIGN.TOP_MID, 0, index * 24)
        
        # 선택 상태에 따른 스타일
        if index == self.current_category:
            item_container.set_style_bg_color(lv.color_hex(self.ui_style.get_color('primary')), 0)
            item_container.set_style_bg_opa(50, 0)
            item_container.set_style_radius(8, 0)
        else:
            item_container.set_style_bg_opa(0, 0)
        
        item_container.set_style_border_width(0, 0)
        item_container.set_style_pad_all(2, 0)
        
        # 아이콘
        icon_label = self.ui_style.create_label(
            item_container,
            category["icon"],
            'text_body',
            self.ui_style.get_color('primary')
        )
        icon_label.align(lv.ALIGN.LEFT_MID, 0, 0)
        
        # 카테고리 이름
        name_label = self.ui_style.create_label(
            item_container,
            category["name"],
            'text_body',
            self.ui_style.get_color('text')
        )
        name_label.align(lv.ALIGN.LEFT_MID, 20, 0)
        
        # 화살표 아이콘
        arrow_label = self.ui_style.create_label(
            item_container,
            "▶",
            'text_caption',
            self.ui_style.get_color('text_secondary')
        )
        arrow_label.align(lv.ALIGN.RIGHT_MID, 0, 0)
        
        return item_container
    
    def _create_item_list(self):
        """아이템 리스트 생성"""
        # 기존 아이템들 정리
        self._clear_list_items()
        
        # 현재 카테고리의 아이템들 생성
        current_category = self.settings_categories[self.current_category]
        items = current_category["items"]
        
        for i, item in enumerate(items):
            if i < self.max_visible_items:
                item_widget = self._create_setting_item(item, i)
                self.list_items.append(item_widget)
    
    def _create_setting_item(self, item, index):
        """설정 아이템 생성"""
        # 아이템 컨테이너
        item_container = lv.obj(self.list_container)
        item_container.set_size(115, 22)
        item_container.align(lv.ALIGN.TOP_MID, 0, index * 24)
        
        # 선택 상태에 따른 스타일
        if index == self.current_item:
            item_container.set_style_bg_color(lv.color_hex(self.ui_style.get_color('primary')), 0)
            item_container.set_style_bg_opa(50, 0)
            item_container.set_style_radius(8, 0)
        else:
            item_container.set_style_bg_opa(0, 0)
        
        item_container.set_style_border_width(0, 0)
        item_container.set_style_pad_all(2, 0)
        
        # 설정 이름
        name_label = self.ui_style.create_label(
            item_container,
            item["name"],
            'text_body',
            self.ui_style.get_color('text')
        )
        name_label.align(lv.ALIGN.LEFT_MID, 0, 0)
        
        # 상태 표시
        status_label = self.ui_style.create_label(
            item_container,
            item["status"],
            'text_caption',
            self.ui_style.get_color('text_secondary')
        )
        status_label.align(lv.ALIGN.RIGHT_MID, 0, 0)
        
        return item_container
    
    def _clear_list_items(self):
        """리스트 아이템들 정리"""
        if hasattr(self, 'list_items'):
            for item in self.list_items:
                if item:
                    item.delete()
        self.list_items = []
    
    def _create_footer_area(self):
        """하단 정보 영역 생성"""
        # 푸터 컨테이너
        self.footer_container = lv.obj(self.main_container)
        self.footer_container.set_size(120, 25)
        self.footer_container.align(lv.ALIGN.BOTTOM_MID, 0, -5)
        self.footer_container.set_style_bg_opa(0, 0)
        self.footer_container.set_style_border_width(0, 0)
        self.footer_container.set_style_pad_all(0, 0)
        
        # 배터리 상태
        self.battery_label = self.ui_style.create_label(
            self.footer_container,
            f"🔋 {self.battery_level}%",
            'text_caption',
            self.ui_style.get_color('text_light')
        )
        self.battery_label.align(lv.ALIGN.LEFT_MID, 0, 0)
        
        # Wi-Fi 상태
        wifi_icon = "📶" if self.wifi_status["connected"] else "📵"
        self.wifi_label = self.ui_style.create_label(
            self.footer_container,
            wifi_icon,
            'text_caption',
            self.ui_style.get_color('text_light')
        )
        self.wifi_label.align(lv.ALIGN.RIGHT_MID, 0, 0)
        
        # 버튼 힌트
        self.hint_label = self.ui_style.create_label(
            self.footer_container,
            self._get_button_hints(),
            'text_caption',
            self.ui_style.get_color('text_light')
        )
        self.hint_label.align(lv.ALIGN.CENTER, 0, 0)
    
    def _get_current_time(self):
        """현재 시간 가져오기"""
        try:
            rtc = RTC()
            year, month, day, weekday, hour, minute, second, microsecond = rtc.datetime()
            return f"{hour:02d}:{minute:02d}"
        except:
            return "00:00"
    
    def _get_button_hints(self):
        """버튼 힌트 텍스트"""
        if self.view_mode == "category":
            return "A:위  B:아래  D:선택  C:뒤로"
        else:
            return "A:위  B:아래  D:설정  C:뒤로"
    
    def get_title(self):
        """화면 제목"""
        return "설정"
    
    def get_button_hints(self):
        """버튼 힌트"""
        return self._get_button_hints()
    
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
            
            # LVGL 타이머 핸들러 강제 호출
            print(f"📱 {self.screen_name} 화면 강제 업데이트 시작...")
            for i in range(10):
                lv.timer_handler()
                time.sleep(0.1)
            print(f"✅ {self.screen_name} 화면 강제 업데이트 완료")
    
    def hide(self):
        """화면 숨기기"""
        pass
    
    def update(self):
        """화면 업데이트"""
        # 시간 업데이트
        if hasattr(self, 'time_label'):
            self.time_label.set_text(self._get_current_time())
        
        # 배터리 상태 업데이트
        if hasattr(self, 'battery_label'):
            self.battery_label.set_text(f"🔋 {self.battery_level}%")
        
        # Wi-Fi 상태 업데이트
        if hasattr(self, 'wifi_label'):
            wifi_icon = "📶" if self.wifi_status["connected"] else "📵"
            self.wifi_label.set_text(wifi_icon)
    
    def on_button_a(self):
        """버튼 A (Up) 처리"""
        if self.view_mode == "category":
            self.current_category = (self.current_category - 1) % len(self.settings_categories)
            self._create_category_items()
            print(f"카테고리 위로 이동: {self.settings_categories[self.current_category]['name']}")
        else:
            current_items = self.settings_categories[self.current_category]["items"]
            self.current_item = (self.current_item - 1) % len(current_items)
            self._create_item_list()
            print(f"아이템 위로 이동: {current_items[self.current_item]['name']}")
    
    def on_button_b(self):
        """버튼 B (Down) 처리"""
        if self.view_mode == "category":
            self.current_category = (self.current_category + 1) % len(self.settings_categories)
            self._create_category_items()
            print(f"카테고리 아래로 이동: {self.settings_categories[self.current_category]['name']}")
        else:
            current_items = self.settings_categories[self.current_category]["items"]
            self.current_item = (self.current_item + 1) % len(current_items)
            self._create_item_list()
            print(f"아이템 아래로 이동: {current_items[self.current_item]['name']}")
    
    def on_button_c(self):
        """버튼 C (Back) 처리"""
        if self.view_mode == "item":
            # 아이템 뷰에서 카테고리 뷰로 돌아가기
            self.view_mode = "category"
            self.current_item = 0
            self._create_category_items()
            print("카테고리 뷰로 돌아가기")
        else:
            # 메인 화면으로 돌아가기
            print("설정 화면 뒤로가기")
            self.screen_manager.show_screen('main')
    
    def on_button_d(self):
        """버튼 D (Select) 처리"""
        if self.view_mode == "category":
            # 카테고리 선택 - 아이템 뷰로 이동
            self.view_mode = "item"
            self.current_item = 0
            self._create_item_list()
            category_name = self.settings_categories[self.current_category]['name']
            print(f"카테고리 선택: {category_name}")
        else:
            # 아이템 선택 - 해당 설정 실행
            current_items = self.settings_categories[self.current_category]["items"]
            selected_item = current_items[self.current_item]
            print(f"설정 아이템 선택: {selected_item['name']}")
            self._execute_setting_action(selected_item['action'])
    
    def _execute_setting_action(self, action):
        """설정 액션 실행"""
        print(f"설정 액션 실행: {action}")
        
        # 액션에 따른 화면 이동 또는 기능 실행
        if action == "wifi_scan":
            self.screen_manager.show_screen('wifi_scan')
        elif action == "dose_count":
            self.screen_manager.show_screen('dose_count')
        elif action == "dose_time":
            self.screen_manager.show_screen('dose_time')
        elif action == "pill_loading":
            self.screen_manager.show_screen('pill_loading')
        elif action == "pill_dispense":
            print("⚠️ 알약 배출 기능은 메인 화면에서 사용하세요")
            # self.screen_manager.show_screen('pill_dispense')  # 제거된 화면
        elif action == "wifi_status":
            self._show_wifi_status()
        elif action == "battery":
            self._show_battery_info()
        elif action == "system_info":
            self._show_system_info()
        elif action == "time_sync":
            self._sync_time()
        elif action == "brightness":
            self._adjust_brightness()
        elif action == "voice_guide":
            self._toggle_voice_guide()
        elif action == "sleep_mode":
            self._adjust_sleep_mode()
        elif action == "disk_status":
            self._show_disk_status()
        elif action == "refill_alert":
            self._toggle_refill_alert()
        elif action == "notification":
            self._toggle_notification()
        else:
            print(f"알 수 없는 액션: {action}")
    
    def _show_wifi_status(self):
        """Wi-Fi 상태 표시"""
        print("Wi-Fi 상태 정보 표시")
        # TODO: Wi-Fi 상태 상세 정보 표시 화면 구현
    
    def _show_battery_info(self):
        """배터리 정보 표시"""
        print("배터리 정보 표시")
        # TODO: 배터리 상세 정보 표시 화면 구현
    
    def _show_system_info(self):
        """시스템 정보 표시"""
        print("시스템 정보 표시")
        # TODO: 시스템 정보 표시 화면 구현
    
    def _sync_time(self):
        """시간 동기화"""
        print("시간 동기화 실행")
        # TODO: NTP 시간 동기화 구현
    
    def _adjust_brightness(self):
        """화면 밝기 조절"""
        print("화면 밝기 조절")
        # TODO: 화면 밝기 조절 기능 구현
    
    def _toggle_voice_guide(self):
        """음성 안내 토글"""
        print("음성 안내 토글")
        # TODO: 음성 안내 설정 토글 구현
    
    def _adjust_sleep_mode(self):
        """자동 절전 모드 조절"""
        print("자동 절전 모드 조절")
        # TODO: 자동 절전 모드 설정 구현
    
    def _show_disk_status(self):
        """디스크 상태 표시"""
        print("디스크 상태 표시")
        # TODO: 디스크별 알약 상태 표시 구현
    
    def _toggle_refill_alert(self):
        """리필 알림 토글"""
        print("리필 알림 토글")
        # TODO: 리필 알림 설정 토글 구현
    
    def _toggle_notification(self):
        """알림 설정 토글"""
        print("알림 설정 토글")
        # TODO: 알림 설정 토글 구현