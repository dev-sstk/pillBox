"""
UI 스타일 시스템
Modern/Xiaomi-like 테마를 적용한 UI 스타일 관리
"""

import lvgl as lv

class UIStyle:
    """UI 스타일 관리 클래스"""
    
    def __init__(self):
        """UI 스타일 초기화"""
        # Modern/Xiaomi-like 색상 정의
        self.colors = {
            'background': 0xFFFFFF,      # 화이트 배경
            'primary': 0xd2b13f,         # 로고 색상 (#d2b13f)
            'secondary': 0x2196F3,       # 코발트 블루 포인트 (#2196F3)
            'text': 0x333333,            # 다크 그레이 텍스트 (#333333)
            'text_secondary': 0x666666,  # 세컨더리 텍스트
            'text_light': 0x888888,      # 라이트 텍스트
            'card': 0xF7F7F7,            # 카드 배경 (#F7F7F7)
            'selected': 0xd2b13f,        # 선택된 항목 (로고 색상)
            'alert': 0xD32F2F,           # 알림 색상 (#D32F2F)
            'success': 0x4CAF50,         # 성공 색상
            'warning': 0xFF9800,         # 경고 색상
            'error': 0xF44336,           # 오류 색상
            'border': 0xE0E0E0,          # 테두리 색상
            'shadow': 0x000000,          # 그림자 색상
            'highlight': 0xd2b13f,       # 하이라이트 색상
            'disk_color': 0xd2b13f,      # 디스크 색상
            'slide_color': 0x2196F3      # 슬라이드 색상
        }
        
        # 폰트 정의
        self.fonts = {
            'title': None,      # 한글 폰트로 설정
            'subtitle': None,   # 한글 폰트로 설정
            'body': None,       # 한글 폰트로 설정
            'caption': None,    # 한글 폰트로 설정
            'korean': None      # font_notosans_kr_regular로 설정
        }
        
        # 한글 폰트 로드 시도
        self._load_korean_font()
        
        # 스타일 객체들 생성
        self._create_styles()
        
        print("[OK] UIStyle 초기화 완료")
    
    def _load_korean_font(self):
        """한글 폰트 로드"""
        try:
            # font_notosans_kr_regular 폰트 로드
            korean_font = getattr(lv, "font_notosans_kr_regular", None)
            
            if korean_font:
                # 모든 폰트를 한글 폰트로 설정
                self.fonts['title'] = korean_font
                self.fonts['subtitle'] = korean_font
                self.fonts['body'] = korean_font
                self.fonts['caption'] = korean_font
                self.fonts['korean'] = korean_font
                print("[OK] font_notosans_kr_regular 폰트 로드 성공")
            else:
                # 한글 폰트가 없으면 기본 폰트 사용
                self.fonts['title'] = lv.font_default
                self.fonts['subtitle'] = lv.font_default
                self.fonts['body'] = lv.font_default
                self.fonts['caption'] = lv.font_default
                self.fonts['korean'] = lv.font_default
                print("[WARN] font_notosans_kr_regular 폰트 없음, 기본 폰트 사용")
                
        except Exception as e:
            print(f"[ERROR] 폰트 로드 실패: {e}")
            # 오류 시 기본 폰트 사용
            self.fonts['title'] = lv.font_default
            self.fonts['subtitle'] = lv.font_default
            self.fonts['body'] = lv.font_default
            self.fonts['caption'] = lv.font_default
            self.fonts['korean'] = lv.font_default
    
    def _create_styles(self):
        """스타일 객체들 생성"""
        self.styles = {}
        
        # 화면 배경 스타일
        self.styles['screen_bg'] = lv.style_t()
        self.styles['screen_bg'].set_bg_color(lv.color_hex(self.colors['background']))
        self.styles['screen_bg'].set_bg_opa(255)
        
        # 카드 스타일
        self.styles['card'] = lv.style_t()
        self.styles['card'].set_bg_color(lv.color_hex(self.colors['card']))
        self.styles['card'].set_bg_opa(255)
        self.styles['card'].set_radius(12)
        self.styles['card'].set_border_width(1)
        self.styles['card'].set_border_color(lv.color_hex(self.colors['border']))
        self.styles['card'].set_pad_all(8)
        # ESP32 LVGL에서는 그림자 설정이 다를 수 있음
        try:
            self.styles['card'].set_shadow_width(4)
            self.styles['card'].set_shadow_color(lv.color_hex(self.colors['shadow']))
            self.styles['card'].set_shadow_ofs_x(2)
            self.styles['card'].set_shadow_ofs_y(2)
        except AttributeError:
            # 그림자 메서드가 없으면 건너뛰기
            print("[WARN] 그림자 스타일 메서드 지원 안됨, 건너뛰기")
        
        # 선택된 카드 스타일
        self.styles['card_selected'] = lv.style_t()
        self.styles['card_selected'].set_bg_color(lv.color_hex(self.colors['selected']))
        self.styles['card_selected'].set_bg_opa(255)
        self.styles['card_selected'].set_radius(12)
        self.styles['card_selected'].set_border_width(2)
        self.styles['card_selected'].set_border_color(lv.color_hex(self.colors['primary']))
        self.styles['card_selected'].set_pad_all(8)
        try:
            self.styles['card_selected'].set_shadow_width(6)
            self.styles['card_selected'].set_shadow_color(lv.color_hex(self.colors['primary']))
            self.styles['card_selected'].set_shadow_ofs_x(3)
            self.styles['card_selected'].set_shadow_ofs_y(3)
        except AttributeError:
            pass
        
        # 버튼 스타일
        self.styles['button'] = lv.style_t()
        self.styles['button'].set_bg_color(lv.color_hex(self.colors['primary']))
        self.styles['button'].set_bg_opa(255)
        self.styles['button'].set_radius(12)
        self.styles['button'].set_border_width(0)
        self.styles['button'].set_pad_all(12)
        try:
            self.styles['button'].set_shadow_width(4)
            self.styles['button'].set_shadow_color(lv.color_hex(self.colors['shadow']))
            self.styles['button'].set_shadow_ofs_x(2)
            self.styles['button'].set_shadow_ofs_y(2)
        except AttributeError:
            pass
        
        # 버튼 눌림 스타일
        self.styles['button_pressed'] = lv.style_t()
        self.styles['button_pressed'].set_bg_color(lv.color_hex(self.colors['secondary']))
        self.styles['button_pressed'].set_bg_opa(255)
        self.styles['button_pressed'].set_radius(12)
        self.styles['button_pressed'].set_border_width(0)
        self.styles['button_pressed'].set_pad_all(12)
        try:
            self.styles['button_pressed'].set_shadow_width(2)
            self.styles['button_pressed'].set_shadow_color(lv.color_hex(self.colors['shadow']))
            self.styles['button_pressed'].set_shadow_ofs_x(1)
            self.styles['button_pressed'].set_shadow_ofs_y(1)
        except AttributeError:
            pass
        
        # 텍스트 스타일들
        self.styles['text_title'] = lv.style_t()
        self.styles['text_title'].set_text_color(lv.color_hex(self.colors['text']))
        self.styles['text_title'].set_text_font(self.fonts['title'])
        
        self.styles['text_subtitle'] = lv.style_t()
        self.styles['text_subtitle'].set_text_color(lv.color_hex(self.colors['text']))
        self.styles['text_subtitle'].set_text_font(self.fonts['subtitle'])
        
        self.styles['text_body'] = lv.style_t()
        self.styles['text_body'].set_text_color(lv.color_hex(self.colors['text']))
        self.styles['text_body'].set_text_font(self.fonts['body'])
        
        self.styles['text_caption'] = lv.style_t()
        self.styles['text_caption'].set_text_color(lv.color_hex(self.colors['text_light']))
        self.styles['text_caption'].set_text_font(self.fonts['caption'])
        
        # 한글 텍스트 스타일
        if self.fonts['korean']:
            self.styles['text_korean'] = lv.style_t()
            self.styles['text_korean'].set_text_color(lv.color_hex(self.colors['text']))
            self.styles['text_korean'].set_text_font(self.fonts['korean'])
        
        # 알림 스타일
        self.styles['alert'] = lv.style_t()
        self.styles['alert'].set_bg_color(lv.color_hex(self.colors['alert']))
        self.styles['alert'].set_bg_opa(255)
        self.styles['alert'].set_radius(12)
        self.styles['alert'].set_border_width(0)
        self.styles['alert'].set_pad_all(16)
        try:
            self.styles['alert'].set_shadow_width(8)
            self.styles['alert'].set_shadow_color(lv.color_hex(self.colors['alert']))
            self.styles['alert'].set_shadow_ofs_x(4)
            self.styles['alert'].set_shadow_ofs_y(4)
        except AttributeError:
            pass
        
        print("[OK] UI 스타일 객체들 생성 완료")
    
    def get_color(self, color_name):
        """색상 값 반환"""
        return self.colors.get(color_name, 0x000000)
    
    def get_font(self, font_name):
        """폰트 객체 반환"""
        return self.fonts.get(font_name, self.fonts['body'])
    
    def get_style(self, style_name):
        """스타일 객체 반환"""
        return self.styles.get(style_name, None)
    
    def apply_screen_style(self, screen_obj):
        """화면에 기본 스타일 적용"""
        if self.styles['screen_bg']:
            screen_obj.add_style(self.styles['screen_bg'], 0)
    
    def create_card(self, parent, width=120, height=80, selected=False):
        """카드 생성 헬퍼"""
        card = lv.obj(parent)
        card.set_size(width, height)
        
        if selected and self.styles['card_selected']:
            card.add_style(self.styles['card_selected'], 0)
        elif self.styles['card']:
            card.add_style(self.styles['card'], 0)
        
        return card
    
    def create_button(self, parent, text, width=80, height=40):
        """버튼 생성 헬퍼"""
        btn = lv.btn(parent)
        btn.set_size(width, height)
        
        if self.styles['button']:
            btn.add_style(self.styles['button'], 0)
        
        btn_label = lv.label(btn)
        btn_label.set_text(text)
        btn_label.center()
        
        if self.styles['text_body']:
            btn_label.add_style(self.styles['text_body'], 0)
        
        return btn
    
    def create_label(self, parent, text, style_name='text_body', color=None):
        """라벨 생성 헬퍼"""
        label = lv.label(parent)
        label.set_text(text)
        
        # 스타일 적용
        if style_name in self.styles:
            label.add_style(self.styles[style_name], 0)
        
        # 색상 오버라이드
        if color:
            label.set_style_text_color(lv.color_hex(color), 0)
        
        return label
    
    def cleanup(self):
        """스타일 리소스 정리 (메모리 누수 방지)"""
        try:
            # 스타일 객체들 정리
            for style_name, style_obj in self.styles.items():
                if style_obj:
                    try:
                        # LVGL 스타일 객체 정리
                        if hasattr(style_obj, 'reset'):
                            style_obj.reset()
                    except:
                        pass
            
            # 폰트 객체들 정리
            for font_name, font_obj in self.fonts.items():
                if font_obj:
                    try:
                        # 폰트 객체는 일반적으로 정적이므로 특별한 정리 불필요
                        pass
                    except:
                        pass
            
            # 딕셔너리 초기화
            self.styles.clear()
            self.fonts.clear()
            self.colors.clear()
            
        except Exception as e:
            # 정리 실패해도 계속 진행
            pass