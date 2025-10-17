"""
설정 화면
시스템 설정 변경 및 관리
"""

import sys
sys.path.append("/")

import time
import lvgl as lv
from ui_style import UIStyle
from data_manager import DataManager

class SettingsScreen:
    """설정 화면 클래스"""
    
    def __init__(self, screen_manager):
        """설정 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = "settings"
        
        # 데이터 관리자 초기화
        self.data_manager = DataManager()
        
        # UI 스타일 시스템 초기화
        self.ui_style = UIStyle()
        
        # 화면 객체
        self.screen = None
        self.main_container = None
        self.title_label = None
        self.settings_list = None
        self.back_button = None
        
        # 설정 항목들
        self.setting_items = []
        
        print(f"[INFO] {self.screen_name} 화면 초기화")
    
    def create_screen(self):
        """설정 화면 생성"""
        try:
            print(f"[INFO] {self.screen_name} 화면 생성 시작...")
            
            # 화면 객체 생성
            self.screen = lv.obj()
            self.screen.set_size(160, 128)
            self.screen.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
            
            # 메인 컨테이너 생성
            self._create_main_container()
            
            # 제목 영역 생성
            self._create_title_area()
            
            # 설정 목록 생성
            self._create_settings_list()
            
            # 하단 버튼 영역 생성
            self._create_button_area()
            
            print(f"[OK] {self.screen_name} 화면 생성 완료")
            return True
            
        except Exception as e:
            print(f"[ERROR] {self.screen_name} 화면 생성 실패: {e}")
            return False
    
    def _create_main_container(self):
        """메인 컨테이너 생성"""
        try:
            self.main_container = lv.obj(self.screen)
            self.main_container.set_size(160, 128)
            self.main_container.set_pos(0, 0)
            self.main_container.set_style_bg_opa(0, 0)
            self.main_container.set_style_border_width(0, 0)
            self.main_container.set_style_pad_all(0, 0)
            
            print("[OK] 메인 컨테이너 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] 메인 컨테이너 생성 실패: {e}")
    
    def _create_title_area(self):
        """제목 영역 생성"""
        try:
        # 제목 라벨
            self.title_label = lv.label(self.main_container)
            self.title_label.set_text("설정")
            self.title_label.set_style_text_font(self.ui_style.font_large, 0)
            self.title_label.set_style_text_color(lv.color_hex(0x333333), 0)
            self.title_label.align(lv.ALIGN.TOP_MID, 0, 5)
            
            print("[OK] 제목 영역 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] 제목 영역 생성 실패: {e}")
    
    def _create_settings_list(self):
        """설정 목록 생성"""
        try:
            # 설정 목록 컨테이너
            self.settings_list = lv.obj(self.main_container)
            self.settings_list.set_size(150, 80)
            self.settings_list.set_pos(5, 25)
            self.settings_list.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
            self.settings_list.set_style_border_width(1, 0)
            self.settings_list.set_style_border_color(lv.color_hex(0xCCCCCC), 0)
            self.settings_list.set_style_radius(5, 0)
            self.settings_list.set_style_pad_all(3, 0)
            
            # 설정 항목들 생성
            self._create_setting_items()
            
            print("[OK] 설정 목록 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] 설정 목록 생성 실패: {e}")
    
    def _create_setting_items(self):
        """설정 항목들 생성"""
        try:
            # 설정 데이터 로드
            settings = self.data_manager.load_settings()
            
            # 설정 항목들 정의
            setting_configs = [
                {
                    "key": "auto_dispense",
                    "name": "자동 배출",
                    "type": "toggle",
                    "value": settings.get("system_settings", {}).get("auto_dispense", True)
                },
                {
                    "key": "sound_enabled",
                    "name": "소리 알림",
                    "type": "toggle",
                    "value": settings.get("system_settings", {}).get("sound_enabled", True)
                },
                {
                    "key": "reminder_interval",
                    "name": "재알람 간격",
                    "type": "number",
                    "value": settings.get("alarm_settings", {}).get("reminder_interval", 5)
                },
                {
                    "key": "max_reminders",
                    "name": "최대 재알람",
                    "type": "number",
                    "value": settings.get("alarm_settings", {}).get("max_reminders", 3)
                }
            ]
            
            # 설정 항목들 생성
            for i, config in enumerate(setting_configs):
                self._create_setting_item(config, i * 18)
            
        except Exception as e:
            print(f"[ERROR] 설정 항목 생성 실패: {e}")
    
    def _create_setting_item(self, config, y_offset):
        """설정 항목 생성"""
        try:
            # 설정 항목 컨테이너
            item_container = lv.obj(self.settings_list)
            item_container.set_size(140, 15)
            item_container.set_pos(5, y_offset)
            item_container.set_style_bg_opa(0, 0)
            item_container.set_style_border_width(0, 0)
            item_container.set_style_pad_all(0, 0)
            
            # 설정 이름
            name_label = lv.label(item_container)
            name_label.set_text(config["name"])
            name_label.set_style_text_font(self.ui_style.font_small, 0)
            name_label.set_style_text_color(lv.color_hex(0x333333), 0)
            name_label.set_pos(0, 0)
            
            # 설정 값 표시
            if config["type"] == "toggle":
                value_text = "켜짐" if config["value"] else "꺼짐"
                value_color = lv.color_hex(0x44AA44) if config["value"] else lv.color_hex(0x999999)
            else:  # number
                value_text = str(config["value"])
                value_color = lv.color_hex(0x333333)
            
            value_label = lv.label(item_container)
            value_label.set_text(value_text)
            value_label.set_style_text_font(self.ui_style.font_small, 0)
            value_label.set_style_text_color(value_color, 0)
            value_label.set_pos(100, 0)
            
            # 설정 항목 저장
            self.setting_items.append({
                "container": item_container,
                "config": config,
                "name_label": name_label,
                "value_label": value_label
            })
            
        except Exception as e:
            print(f"[ERROR] 설정 항목 생성 실패: {e}")
    
    def _create_button_area(self):
        """하단 버튼 영역 생성"""
        try:
            # 뒤로가기 버튼
            self.back_button = lv.btn(self.main_container)
            self.back_button.set_size(60, 20)
            self.back_button.set_pos(50, 100)
            self.back_button.set_style_bg_color(lv.color_hex(0x007AFF), 0)
            self.back_button.set_style_radius(10, 0)
            
            # 버튼 라벨
            back_label = lv.label(self.back_button)
            back_label.set_text("뒤로")
            back_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
            back_label.center()
            
            # 버튼 이벤트
            self.back_button.add_event_cb(self._on_back_button, lv.EVENT.CLICKED, None)
            
            print("[OK] 하단 버튼 영역 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] 하단 버튼 영역 생성 실패: {e}")
    
    def _on_back_button(self, event):
        """뒤로가기 버튼 이벤트"""
        try:
            if event == lv.EVENT.CLICKED:
                print("[BTN] 뒤로가기 버튼 눌림")
                self.screen_manager.show_screen("main")
                
        except Exception as e:
            print(f"[ERROR] 뒤로가기 버튼 이벤트 실패: {e}")
    
    def show(self):
        """화면 표시"""
        try:
            if self.screen:
                lv.scr_load(self.screen)
                print(f"[OK] {self.screen_name} 화면 표시")
            else:
                print(f"[ERROR] {self.screen_name} 화면 객체 없음")
                
        except Exception as e:
            print(f"[ERROR] {self.screen_name} 화면 표시 실패: {e}")
    
    def hide(self):
        """화면 숨기기"""
        try:
            print(f"[INFO] {self.screen_name} 화면 숨기기")
            # 화면 숨김 처리
            
        except Exception as e:
            print(f"[ERROR] {self.screen_name} 화면 숨기기 실패: {e}")
    
    def update(self):
        """화면 업데이트"""
        try:
            # 설정 항목들 업데이트
            for item in self.setting_items:
                self._update_setting_item(item)
            
        except Exception as e:
            print(f"[ERROR] {self.screen_name} 화면 업데이트 실패: {e}")
    
    def _update_setting_item(self, item):
        """설정 항목 업데이트"""
        try:
            config = item["config"]
            value_label = item["value_label"]
            
            # 현재 설정 값 가져오기
            settings = self.data_manager.load_settings()
            current_value = self._get_setting_value(settings, config["key"])
            
            # 값 표시 업데이트
            if config["type"] == "toggle":
                value_text = "켜짐" if current_value else "꺼짐"
                value_color = lv.color_hex(0x44AA44) if current_value else lv.color_hex(0x999999)
            else:  # number
                value_text = str(current_value)
                value_color = lv.color_hex(0x333333)
            
            value_label.set_text(value_text)
            value_label.set_style_text_color(value_color, 0)
            
        except Exception as e:
            print(f"[ERROR] 설정 항목 업데이트 실패: {e}")
    
    def _get_setting_value(self, settings, key):
        """설정 값 가져오기"""
        try:
            if key == "auto_dispense":
                return settings.get("system_settings", {}).get("auto_dispense", True)
            elif key == "sound_enabled":
                return settings.get("system_settings", {}).get("sound_enabled", True)
            elif key == "reminder_interval":
                return settings.get("alarm_settings", {}).get("reminder_interval", 5)
            elif key == "max_reminders":
                return settings.get("alarm_settings", {}).get("max_reminders", 3)
            else:
                return None
                
        except Exception as e:
            print(f"[ERROR] 설정 값 가져오기 실패: {e}")
            return None
    
    def cleanup(self):
        """화면 정리"""
        try:
            if self.screen:
                self.screen.delete()
                self.screen = None
            print(f"[OK] {self.screen_name} 화면 정리 완료")
            
        except Exception as e:
            print(f"[ERROR] {self.screen_name} 화면 정리 실패: {e}")