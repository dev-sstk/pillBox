"""
기본 화면 클래스
모든 화면의 공통 기능을 정의하는 베이스 클래스
"""

import sys
import os
import lvgl as lv
import time

# 현재 파일 기준 상위 폴더
sys.path.append("..")

from ui_style import UIStyle
from audio_system import AudioSystem

class BaseScreen:
    """기본 화면 클래스"""
    
    def __init__(self, screen_manager, screen_name):
        """기본 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = screen_name
        self.screen_obj = None
        self.title_label = None
        self.content_area = None
        self.button_hints = None
        
        # PillBoxApp에서 UI 스타일과 오디오 시스템 가져오기
        app = screen_manager.app if hasattr(screen_manager, 'app') else None
        if app:
            self.ui_style = app.get_ui_style()
            self.audio_system = app.get_audio_system()
        else:
            # fallback: 직접 생성 (비효율적이지만 안전)
            self.ui_style = UIStyle()
            self.audio_system = AudioSystem()
        
        # 화면 생성
        self._create_screen()
        
        print(f"[OK] {screen_name} 화면 초기화 완료")
    
    def _create_screen(self):
        """화면 UI 생성"""
        print(f"  [INFO] {self.screen_name} 화면 UI 생성 시작...")
        
        # 메모리 정리 (test_lvgl.py 방식)
        print(f"  [INFO] 메모리 정리...")
        import gc
        gc.collect()
        print(f"  [OK] 메모리 정리 완료")
        
        # 메인 화면 객체 생성 (test_lvgl.py 방식)
        print(f"  [INFO] 메인 화면 객체 생성...")
        try:
            # LVGL 상태 확인 및 재초기화
            print(f"  [INFO] LVGL 상태 확인...")
            if not lv.is_initialized():
                print(f"  [INFO] LVGL 재초기화...")
                lv.init()
                print(f"  [OK] LVGL 재초기화 완료")
            else:
                print(f"  [OK] LVGL 이미 초기화됨")
            
            # 더 안전한 방법으로 화면 객체 생성
            print(f"  [INFO] 화면 객체 생성 시도...")
            self.screen_obj = lv.obj()
            print(f"  [INFO] 배경색 설정...")
            self.screen_obj.set_style_bg_color(lv.color_hex(0x000000), 0)
            print(f"  [OK] 메인 화면 객체 생성 완료")
        except Exception as e:
            print(f"  [ERROR] 메인 화면 객체 생성 실패: {e}")
            import sys
            sys.print_exception(e)
            # 대안: 기본 화면 사용
            print(f"  [INFO] 기본 화면 사용 시도...")
            try:
                self.screen_obj = lv.screen_active()
                print(f"  [OK] 기본 화면 사용 성공")
            except Exception as e2:
                print(f"  [ERROR] 기본 화면 사용도 실패: {e2}")
                raise
        
        # 제목 라벨 생성 (test_lvgl.py 방식)
        print(f"  [INFO] 제목 라벨 생성...")
        self.title_label = lv.label(self.screen_obj)
        self.title_label.set_text(self.get_title())
        self.title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        # 한글 폰트 적용
        korean_font = getattr(lv, "font_notosans_kr_regular", None)
        if korean_font:
            self.title_label.set_style_text_font(korean_font, 0)
        self.title_label.align(lv.ALIGN.TOP_MID, 0, 15)
        print(f"  [OK] 제목 라벨 생성 완료")
        
        # 콘텐츠 영역 생성
        print(f"  [INFO] 콘텐츠 영역 생성...")
        self.content_area = lv.obj(self.screen_obj)
        self.content_area.set_size(120, 100)
        self.content_area.align(lv.ALIGN.CENTER, 0, 0)
        self.content_area.set_style_bg_opa(0, 0)  # 투명 배경
        print(f"  [OK] 콘텐츠 영역 생성 완료")
        
        # 버튼 힌트 생성 (test_lvgl.py 방식)
        print(f"  [INFO] 버튼 힌트 생성...")
        self.button_hints = lv.label(self.screen_obj)
        self.button_hints.set_text(self.get_button_hints())
        self.button_hints.set_style_text_color(lv.color_hex(0x888888), 0)
        if korean_font:
            self.button_hints.set_style_text_font(korean_font, 0)
        self.button_hints.align(lv.ALIGN.BOTTOM_MID, 0, -15)
        print(f"  [OK] 버튼 힌트 생성 완료")
        
        # 화면별 콘텐츠 생성
        print(f"  [INFO] 화면별 콘텐츠 생성...")
        self._create_content()
        print(f"  [OK] 화면별 콘텐츠 생성 완료")
    
    
    def _create_content(self):
        """화면별 콘텐츠 생성 (하위 클래스에서 구현)"""
        pass
    
    def get_title(self):
        """화면 제목 반환 (하위 클래스에서 구현)"""
        return "기본 화면"
    
    def get_button_hints(self):
        """버튼 힌트 텍스트 반환 (하위 클래스에서 구현)"""
        return "A:Up B:Down C:Back D:Next"
    
    def get_voice_file(self):
        """안내 음성 파일명 반환 (하위 클래스에서 구현)"""
        return None
    
    def get_effect_file(self):
        """효과음 파일명 반환 (하위 클래스에서 구현)"""
        return None
    
    def show(self):
        """화면 표시"""
        if self.screen_obj:
            lv.screen_load(self.screen_obj)
            self.on_show()
    
    def hide(self):
        """화면 숨기기"""
        self.on_hide()
    
    def update(self):
        """화면 업데이트 (하위 클래스에서 구현)"""
        pass
    
    def on_show(self):
        """화면이 표시될 때 호출 (하위 클래스에서 구현)"""
        # 안내 음성 재생
        voice_file = self.get_voice_file()
        if voice_file:
            self.audio_system.play_voice(voice_file)
        
        # 효과음 재생
        effect_file = self.get_effect_file()
        if effect_file:
            self.audio_system.play_effect(effect_file)
    
    def on_hide(self):
        """화면이 숨겨질 때 호출 (하위 클래스에서 구현)"""
        pass
    
    def on_button_a(self):
        """버튼 A 처리 (하위 클래스에서 구현)"""
        self._play_button_sound()
    
    def on_button_b(self):
        """버튼 B 처리 (하위 클래스에서 구현)"""
        self._play_button_sound()
    
    def on_button_c(self):
        """버튼 C 처리 (하위 클래스에서 구현)"""
        self._play_button_sound()
    
    def on_button_d(self):
        """버튼 D 처리 (하위 클래스에서 구현)"""
        self._play_button_sound()
    
    def _play_button_sound(self):
        """버튼 클릭음 재생"""
        # 버튼 클릭음 제거됨
        pass
    
    def create_label(self, text, x=0, y=0, style_name='text_body', color=None):
        """라벨 생성 헬퍼"""
        print(f"      [INFO] 라벨 생성: '{text}' (스타일: {style_name})")
        label = self.ui_style.create_label(self.content_area, text, style_name, color)
        label.align(lv.ALIGN.CENTER, x, y)
        print(f"      [OK] 라벨 생성 완료: '{text}'")
        return label
    
    def create_button(self, text, x=0, y=0, width=80, height=40):
        """버튼 생성 헬퍼"""
        btn = self.ui_style.create_button(self.content_area, text, width, height)
        btn.align(lv.ALIGN.CENTER, x, y)
        return btn
    
    def create_card(self, width=120, height=80, selected=False):
        """카드 생성 헬퍼"""
        return self.ui_style.create_card(self.content_area, width, height, selected)
