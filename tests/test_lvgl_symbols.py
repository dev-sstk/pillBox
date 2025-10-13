#!/usr/bin/env python3
"""
LVGL 심볼 테스트 코드
대화형 선택지로 다양한 LVGL 심볼들을 확인할 수 있습니다.
실제 ESP32 환경에서 LVGL 심볼들을 화면에 표시하여 확인할 수 있습니다.
"""

import sys
import time
sys.path.append('/')

# LVGL 심볼 카테고리별 정의
SYMBOL_CATEGORIES = {
    "배터리 관련": [
        ("BATTERY_FULL", "lv.SYMBOL.BATTERY_FULL"),
        ("BATTERY_3", "lv.SYMBOL.BATTERY_3"),
        ("BATTERY_2", "lv.SYMBOL.BATTERY_2"),
        ("BATTERY_1", "lv.SYMBOL.BATTERY_1"),
        ("BATTERY_EMPTY", "lv.SYMBOL.BATTERY_EMPTY"),
        ("CHARGE", "lv.SYMBOL.CHARGE"),
    ],
    "상태 표시": [
        ("OK", "lv.SYMBOL.OK"),
        ("WARNING", "lv.SYMBOL.WARNING"),
        ("CLOSE", "lv.SYMBOL.CLOSE"),
        ("PLUS", "lv.SYMBOL.PLUS"),
        ("MINUS", "lv.SYMBOL.MINUS"),
    ],
    "알림/통신": [
        ("BELL", "lv.SYMBOL.BELL"),
        ("WIFI", "lv.SYMBOL.WIFI"),
        ("BLUETOOTH", "lv.SYMBOL.BLUETOOTH"),
        ("ENVELOPE", "lv.SYMBOL.ENVELOPE"),
        ("CALL", "lv.SYMBOL.CALL"),
    ],
    "방향/조작": [
        ("UP", "lv.SYMBOL.UP"),
        ("DOWN", "lv.SYMBOL.DOWN"),
        ("LEFT", "lv.SYMBOL.LEFT"),
        ("RIGHT", "lv.SYMBOL.RIGHT"),
        ("NEXT", "lv.SYMBOL.NEXT"),
        ("PREV", "lv.SYMBOL.PREV"),
    ],
    "미디어/재생": [
        ("PLAY", "lv.SYMBOL.PLAY"),
        ("PAUSE", "lv.SYMBOL.PAUSE"),
        ("STOP", "lv.SYMBOL.STOP"),
        ("AUDIO", "lv.SYMBOL.AUDIO"),
        ("VIDEO", "lv.SYMBOL.VIDEO"),
        ("VOLUME_MAX", "lv.SYMBOL.VOLUME_MAX"),
        ("VOLUME_MID", "lv.SYMBOL.VOLUME_MID"),
        ("MUTE", "lv.SYMBOL.MUTE"),
    ],
    "기능/도구": [
        ("SETTINGS", "lv.SYMBOL.SETTINGS"),
        ("HOME", "lv.SYMBOL.HOME"),
        ("SAVE", "lv.SYMBOL.SAVE"),
        ("EDIT", "lv.SYMBOL.EDIT"),
        ("COPY", "lv.SYMBOL.COPY"),
        ("CUT", "lv.SYMBOL.CUT"),
        ("PASTE", "lv.SYMBOL.PASTE"),
        ("TRASH", "lv.SYMBOL.TRASH"),
    ],
    "파일/시스템": [
        ("FILE", "lv.SYMBOL.FILE"),
        ("DIRECTORY", "lv.SYMBOL.DIRECTORY"),
        ("DRIVE", "lv.SYMBOL.DRIVE"),
        ("SD_CARD", "lv.SYMBOL.SD_CARD"),
        ("USB", "lv.SYMBOL.USB"),
        ("POWER", "lv.SYMBOL.POWER"),
    ],
    "기타": [
        ("REFRESH", "lv.SYMBOL.REFRESH"),
        ("GPS", "lv.SYMBOL.GPS"),
        ("IMAGE", "lv.SYMBOL.IMAGE"),
        ("KEYBOARD", "lv.SYMBOL.KEYBOARD"),
        ("LIST", "lv.SYMBOL.LIST"),
        ("BARS", "lv.SYMBOL.BARS"),
        ("BULLET", "lv.SYMBOL.BULLET"),
        ("EYE_OPEN", "lv.SYMBOL.EYE_OPEN"),
        ("EYE_CLOSE", "lv.SYMBOL.EYE_CLOSE"),
    ]
}

def print_header():
    """헤더 출력"""
    print("=" * 60)
    print("🔍 LVGL 심볼 테스트 도구")
    print("=" * 60)
    print("다양한 LVGL 심볼들을 확인할 수 있습니다.")
    print("카테고리를 선택하면 해당 카테고리의 모든 심볼을 볼 수 있습니다.")
    print("=" * 60)

def print_categories():
    """카테고리 목록 출력"""
    print("\n📂 카테고리 목록:")
    categories = list(SYMBOL_CATEGORIES.keys())
    for i, category in enumerate(categories, 1):
        symbol_count = len(SYMBOL_CATEGORIES[category])
        print(f"  {i:2d}. {category} ({symbol_count}개)")
    print(f"  {len(categories)+1:2d}. 모든 심볼 보기")
    print(f"  {len(categories)+2:2d}. 종료")

def print_symbols(category_name):
    """특정 카테고리의 심볼들 출력"""
    symbols = SYMBOL_CATEGORIES[category_name]
    print(f"\n🔖 {category_name} 카테고리 심볼들:")
    print("-" * 50)
    
    for name, code in symbols:
        print(f"  {name:15} → {code}")
    print("-" * 50)
    print(f"총 {len(symbols)}개의 심볼")

def print_all_symbols():
    """모든 심볼 출력"""
    print("\n🌟 모든 LVGL 심볼들:")
    print("=" * 60)
    
    total_count = 0
    for category_name, symbols in SYMBOL_CATEGORIES.items():
        print(f"\n📂 {category_name}:")
        for name, code in symbols:
            print(f"  {name:15} → {code}")
        total_count += len(symbols)
    
    print("=" * 60)
    print(f"총 {total_count}개의 심볼")

def get_user_choice():
    """사용자 선택 입력 받기"""
    while True:
        try:
            choice = input("\n선택하세요 (번호 입력): ").strip()
            if choice.lower() in ['q', 'quit', 'exit', '종료']:
                return 'quit'
            return int(choice)
        except ValueError:
            print("❌ 올바른 번호를 입력해주세요.")
        except KeyboardInterrupt:
            print("\n\n👋 프로그램을 종료합니다.")
            return 'quit'

class LVGLSymbolTester:
    def __init__(self):
        self.screen = None
        self.current_category = None
        self.current_symbol_index = 0
        self.symbols = []
        self.labels = []
        self.is_display_mode = False
        
    def create_screen(self):
        """LVGL 화면 생성"""
        try:
            print("🔍 LVGL 모듈 임포트 시도 중...")
            import lvgl as lv
            print("✅ LVGL 모듈 임포트 성공")
            
            # LVGL 초기화 확인
            print("🔍 LVGL 초기화 상태 확인 중...")
            try:
                # LVGL 기본 함수들 확인
                print("  - lv.init() 상태 확인 중...")
                # lv.init()이 이미 호출되었는지 확인
                print("  - lv.obj() 호출 시도 중...")
                test_obj = lv.obj()
                print("✅ LVGL 초기화 상태 정상")
                print("  - 테스트 객체 삭제 중...")
                test_obj.delete()  # 테스트 객체 삭제
                print("✅ 테스트 객체 삭제 완료")
            except Exception as init_e:
                print(f"❌ LVGL 초기화 상태 이상: {init_e}")
                print(f"   오류 타입: {type(init_e).__name__}")
                import traceback
                traceback.print_exc()
                return False
            
            print("🔍 화면 생성 시도 중...")
            # 기존 활성 화면 확인
            print("  - lv.screen_active() 호출 중...")
            self.screen = lv.screen_active()
            print(f"  - screen_active() 결과: {self.screen}")
            
            if not self.screen:
                print("🔍 활성 화면이 없어서 새로 생성 중...")
                print("  - lv.obj() 호출 중...")
                self.screen = lv.obj()
                print(f"  - lv.obj() 결과: {self.screen}")
                print("  - lv.screen_load() 호출 중...")
                lv.screen_load(self.screen)
                print("✅ 새 화면 생성 및 로드 완료")
            else:
                print("✅ 기존 활성 화면 사용")
            
            print("🔍 화면 배경 설정 중...")
            # 화면 배경 설정
            self.screen.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
            print("✅ 화면 배경 설정 완료")
            
            print("✅ LVGL 화면 생성 완료")
            return True
            
        except ImportError as e:
            print(f"❌ LVGL 모듈 임포트 실패: {e}")
            return False
        except Exception as e:
            print(f"❌ LVGL 화면 생성 실패: {e}")
            print(f"   오류 타입: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False
    
    def show_symbols_directly(self):
        """심볼들을 직접 화면에 표시 (test_lvgl.py 방식)"""
        try:
            import lvgl as lv
            import lv_utils
            
            # 기존 디스플레이 정리
            print("  - 기존 디스플레이 정리 중...")
            
            # LVGL 초기화
            print("  - LVGL 초기화 중...")
            lv.init()
            
            # 이벤트 루프 시작 (화면 업데이트를 위해)
            if not lv_utils.event_loop.is_running():
                event_loop = lv_utils.event_loop()
                print("  - LVGL 이벤트 루프 시작")
            else:
                print("  - LVGL 이벤트 루프 이미 실행 중")
            
            # 화면 생성 (test_lvgl.py 방식)
            self.scr = lv.obj()
            self.scr.set_style_bg_color(lv.color_hex(0x000000), 0)  # 검은 배경
            
            # 화면 로드
            lv.screen_load(self.scr)
            print("  - 화면 로드 완료")
            
            print("✅ 디스플레이 준비 완료")
            return True
            
        except Exception as e:
            print(f"❌ 디스플레이 초기화 실패: {e}")
            print(f"   오류 타입: {type(e).__name__}")
            return False
    
    def display_symbol(self, symbol_name, symbol_code):
        """선택된 심볼을 디스플레이에 표시 - main_screen.py와 완전히 동일한 방식"""
        try:
            import lvgl as lv
            
            # main_screen.py와 동일한 방식으로 화면 생성
            self.scr.delete()
            self.scr = lv.obj()
            self.scr.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)  # 흰색 배경 명시적 설정
            lv.screen_load(self.scr)
            
            print(f"  - 화면 객체 재생성 완료 (흰색 배경)")
            
            # main_screen.py와 동일한 방식으로 심볼 직접 접근
            symbol_value = self._get_symbol_value(symbol_code)
            print(f"  - 심볼 값: '{symbol_value}'")
            
            # 심볼만 화면 정중앙에 표시
            symbol_label = lv.label(self.scr)
            symbol_label.set_text(symbol_value)
            symbol_label.align(lv.ALIGN.CENTER, 0, 0)  # 화면 정중앙 정렬
            symbol_label.set_style_text_color(lv.color_hex(0x1D1D1F), 0)  # main_screen.py와 동일한 색상
            symbol_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)  # 텍스트 중앙 정렬
            # main_screen.py처럼 폰트 설정하지 않음 (기본 폰트 자동 사용)
            print(f"  - 심볼 라벨 생성: '{symbol_value}' (화면 정중앙)")
            
            # 화면 강제 업데이트
            print(f"  - 화면 업데이트 시작...")
            for i in range(10):
                lv.timer_handler()
                time.sleep(0.1)
            print(f"  - 화면 업데이트 완료")
            
            print(f"✅ '{symbol_name}' 심볼이 디스플레이에 표시되었습니다")
            return True
            
        except Exception as e:
            print(f"❌ 심볼 표시 실패: {e}")
            import sys
            sys.print_exception(e)
            return False
    
    def _get_symbol_value(self, symbol_code):
        """심볼 코드에서 실제 심볼 값 추출 - main_screen.py 방식 하드코딩"""
        try:
            import lvgl as lv
            
            if symbol_code.startswith("lv.SYMBOL."):
                symbol_name = symbol_code.replace("lv.SYMBOL.", "")
                
                # main_screen.py에서 실제로 사용하는 심볼들만 하드코딩
                if symbol_name == "UP":
                    return lv.SYMBOL.UP
                elif symbol_name == "DOWN":
                    return lv.SYMBOL.DOWN
                elif symbol_name == "LEFT":
                    return lv.SYMBOL.LEFT
                elif symbol_name == "RIGHT":
                    return lv.SYMBOL.RIGHT
                elif symbol_name == "WIFI":
                    return lv.SYMBOL.WIFI
                elif symbol_name == "BATTERY_FULL":
                    return lv.SYMBOL.BATTERY_FULL
                elif symbol_name == "BATTERY_3":
                    return lv.SYMBOL.BATTERY_3
                elif symbol_name == "BATTERY_2":
                    return lv.SYMBOL.BATTERY_2
                elif symbol_name == "BATTERY_1":
                    return lv.SYMBOL.BATTERY_1
                elif symbol_name == "BATTERY_EMPTY":
                    return lv.SYMBOL.BATTERY_EMPTY
                elif symbol_name == "OK":
                    return lv.SYMBOL.OK
                elif symbol_name == "WARNING":
                    return lv.SYMBOL.WARNING
                elif symbol_name == "BELL":
                    return lv.SYMBOL.BELL
                elif symbol_name == "PLAY":
                    return lv.SYMBOL.PLAY
                elif symbol_name == "PAUSE":
                    return lv.SYMBOL.PAUSE
                elif symbol_name == "STOP":
                    return lv.SYMBOL.STOP
                elif symbol_name == "CHARGE":
                    return lv.SYMBOL.CHARGE
                elif symbol_name == "CLOSE":
                    return lv.SYMBOL.CLOSE
                elif symbol_name == "NEXT":
                    return lv.SYMBOL.NEXT
                elif symbol_name == "PREV":
                    return lv.SYMBOL.PREV
                else:
                    print(f"  - 지원하지 않는 심볼: {symbol_name}")
                    return "?"
            else:
                return symbol_code
                
        except Exception as e:
            print(f"  - 심볼 값 추출 실패: {e}")
            return "?"
    
    def interactive_symbol_test(self):
        """대화형 심볼 테스트"""
        try:
            print("\n" + "=" * 60)
            print("🔍 대화형 LVGL 심볼 테스트")
            print("=" * 60)
            print("터미널에서 심볼을 선택하면 디스플레이에 표시됩니다!")
            print("=" * 60)
            
            while True:
                print("\n📂 카테고리 선택:")
                categories = list(SYMBOL_CATEGORIES.keys())
                for i, category in enumerate(categories, 1):
                    symbol_count = len(SYMBOL_CATEGORIES[category])
                    print(f"  {i:2d}. {category} ({symbol_count}개)")
                print(f"  {len(categories)+1:2d}. 종료")
                
                try:
                    choice = input("\n카테고리 선택 (번호 입력): ").strip()
                    if choice.lower() in ['q', 'quit', 'exit', '종료']:
                        break
                    
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(categories):
                        category_name = categories[choice_num - 1]
                        self.show_category_symbols(category_name)
                    elif choice_num == len(categories) + 1:
                        break
                    else:
                        print("❌ 잘못된 선택입니다.")
                        
                except ValueError:
                    print("❌ 올바른 번호를 입력해주세요.")
                except KeyboardInterrupt:
                    print("\n\n👋 프로그램을 종료합니다.")
                    break
            
            return True
            
        except Exception as e:
            print(f"❌ 대화형 테스트 실패: {e}")
            return False
    
    def show_category_symbols(self, category_name):
        """특정 카테고리의 심볼들을 선택할 수 있게 표시"""
        try:
            symbols = SYMBOL_CATEGORIES[category_name]
            print(f"\n🔖 {category_name} 카테고리 심볼들:")
            print("-" * 50)
            
            for i, (name, code) in enumerate(symbols, 1):
                print(f"  {i:2d}. {name:15} → {code}")
            
            while True:
                try:
                    choice = input(f"\n{category_name} 심볼 선택 (1-{len(symbols)}) 또는 'b' (뒤로가기): ").strip()
                    
                    if choice.lower() in ['b', 'back', '뒤로', '뒤로가기']:
                        break
                    
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(symbols):
                        symbol_name, symbol_code = symbols[choice_num - 1]
                        print(f"\n📱 디스플레이에 '{symbol_name}' 심볼 표시 중...")
                        self.display_symbol(symbol_name, symbol_code)
                        
                        # 잠시 대기
                        input("⏎ Enter를 누르면 계속...")
                        break
                    else:
                        print("❌ 잘못된 선택입니다.")
                        
                except ValueError:
                    print("❌ 올바른 번호를 입력해주세요.")
                except KeyboardInterrupt:
                    print("\n\n👋 프로그램을 종료합니다.")
                    break
                    
        except Exception as e:
            print(f"❌ 카테고리 표시 실패: {e}")
    
    def show_symbols(self, category_name):
        """특정 카테고리의 심볼들 표시"""
        try:
            import lvgl as lv
            
            # 기존 화면 정리
            self.clear_screen()
            self.is_display_mode = True
            
            # 카테고리 정보 저장
            self.current_category = category_name
            self.symbols = SYMBOL_CATEGORIES[category_name]
            self.current_symbol_index = 0
            
            # 제목
            title = lv.label(self.screen)
            title.set_text(f"{category_name} 심볼들")
            title.align(lv.ALIGN.TOP_MID, 0, 5)
            title.set_style_text_color(lv.color_hex(0x000000), 0)
            
            # 현재 심볼 표시
            self.show_current_symbol()
            
            # 조작 안내
            hint = lv.label(self.screen)
            hint.set_text("A:이전 B:다음 C:메뉴로")
            hint.align(lv.ALIGN.BOTTOM_MID, 0, -10)
            hint.set_style_text_color(lv.color_hex(0x666666), 0)
            
            print(f"✅ {category_name} 심볼들 표시 완료")
            
        except Exception as e:
            print(f"❌ 심볼 표시 실패: {e}")
    
    def show_current_symbol(self):
        """현재 심볼 표시"""
        try:
            import lvgl as lv
            
            if not self.symbols or self.current_symbol_index >= len(self.symbols):
                return
            
            # 기존 심볼 라벨들 정리
            for label in self.labels:
                if label:
                    label.delete()
            self.labels = []
            
            current_symbol = self.symbols[self.current_symbol_index]
            symbol_name, symbol_code = current_symbol
            
            # 심볼 이름
            name_label = lv.label(self.screen)
            name_label.set_text(symbol_name)
            name_label.align(lv.ALIGN.TOP_MID, 0, 25)
            name_label.set_style_text_color(lv.color_hex(0x000000), 0)
            self.labels.append(name_label)
            
            # 심볼 코드
            code_label = lv.label(self.screen)
            code_label.set_text(symbol_code)
            code_label.align(lv.ALIGN.TOP_MID, 0, 40)
            code_label.set_style_text_color(lv.color_hex(0x666666), 0)
            self.labels.append(code_label)
            
            # 실제 심볼 표시 (큰 크기)
            symbol_label = lv.label(self.screen)
            symbol_label.set_text(eval(symbol_code))  # lv.SYMBOL.OK 등 실제 심볼
            symbol_label.align(lv.ALIGN.CENTER, 0, 0)
            symbol_label.set_style_text_color(lv.color_hex(0x000000), 0)
            symbol_label.set_style_text_font(lv.font_default(), 0)
            # 큰 폰트로 표시
            symbol_label.set_style_text_font_size(48, 0)
            self.labels.append(symbol_label)
            
            # 진행 상황
            progress_label = lv.label(self.screen)
            progress_label.set_text(f"{self.current_symbol_index + 1}/{len(self.symbols)}")
            progress_label.align(lv.ALIGN.BOTTOM_MID, 0, -30)
            progress_label.set_style_text_color(lv.color_hex(0x666666), 0)
            self.labels.append(progress_label)
            
        except Exception as e:
            print(f"❌ 현재 심볼 표시 실패: {e}")
    
    def next_symbol(self):
        """다음 심볼로 이동"""
        if self.current_symbol_index < len(self.symbols) - 1:
            self.current_symbol_index += 1
            self.show_current_symbol()
    
    def prev_symbol(self):
        """이전 심볼로 이동"""
        if self.current_symbol_index > 0:
            self.current_symbol_index -= 1
            self.show_current_symbol()
    
    def clear_screen(self):
        """화면 정리"""
        try:
            import lvgl as lv
            
            # 모든 자식 객체 삭제 - 안전한 방법
            try:
                # 방법 1: get_children() 사용
                if hasattr(self.screen, 'get_children'):
                    children = self.screen.get_children()
                    for child in children:
                        child.delete()
                # 방법 2: get_child_cnt() 사용
                elif hasattr(self.screen, 'get_child_cnt'):
                    child_cnt = self.screen.get_child_cnt()
                    for i in range(child_cnt):
                        child = self.screen.get_child(i)
                        if child:
                            child.delete()
                else:
                    # 방법 3: 화면 재생성
                    print("  - 화면 정리: 화면 재생성 방법 사용")
                    self.screen.delete()
                    self.screen = lv.obj()
                    lv.screen_load(self.screen)
                    
            except Exception as clear_e:
                print(f"  - 화면 정리 중 오류: {clear_e}")
                # 화면 재생성으로 폴백
                try:
                    self.screen.delete()
                    self.screen = lv.obj()
                    lv.screen_load(self.screen)
                except:
                    pass
                
        except Exception as e:
            print(f"❌ 화면 정리 실패: {e}")
            # 최후의 수단: 무시하고 계속 진행

def test_lvgl_availability():
    """LVGL 사용 가능 여부 테스트"""
    try:
        import lvgl as lv
        print("✅ LVGL 모듈 임포트 성공")
        
        # 디스플레이 드라이버 초기화 시도
        print("🔍 디스플레이 드라이버 초기화 시도 중...")
        try:
            from st77xx import St7735
            from machine import Pin, SPI
            print("✅ ST7735 드라이버 임포트 성공")
            
            # ST7735 디스플레이 초기화 (160x128 해상도)
            print("  - ST7735 디스플레이 초기화 시도 중...")
            
            # SPI 및 핀 설정
            spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19))
            dc = Pin(21, Pin.OUT)
            cs = Pin(23, Pin.OUT)
            rst = Pin(20, Pin.OUT)
            
            display = St7735(
                res=(128, 160),  # 올바른 해상도로 수정
                model='blacktab',
                cs=cs,
                dc=dc,
                rst=rst,
                spi=spi,
                rot=3,  # 180도 회전
                doublebuffer=False
            )
            
            # 디스플레이 백라이트 설정
            display.set_backlight(100)
            print("✅ ST7735 디스플레이 초기화 완료")
            
        except Exception as display_e:
            print(f"❌ 디스플레이 드라이버 초기화 실패: {display_e}")
            print("  - LVGL만으로 테스트 시도 중...")
            
            # LVGL 초기화 상태 확인
            print("🔍 LVGL 초기화 상태 확인 중...")
            
            # lv.init()이 이미 호출되었는지 확인
            try:
                print("  - lv.init() 호출 시도 중...")
                lv.init()
                print("  - lv.init() 호출 완료")
            except Exception as init_e:
                print(f"  - lv.init() 호출 실패: {init_e}")
                # 이미 초기화되었을 수도 있음
            
            # 간단한 테스트 (타임아웃 추가)
            print("  - lv.obj() 호출 시도 중...")
            try:
                test_obj = lv.obj()
                print("  - lv.obj() 호출 성공")
                print("  - 테스트 객체 삭제 시도 중...")
                test_obj.delete()
                print("  - 테스트 객체 삭제 완료")
            except Exception as obj_e:
                print(f"  - lv.obj() 호출 실패: {obj_e}")
                print("  - 디스플레이 드라이버 없이는 LVGL 객체 생성 불가")
                return False
        
        print("✅ LVGL 기본 기능 테스트 성공")
        return True
    except Exception as e:
        print(f"❌ LVGL 사용 불가: {e}")
        print(f"   오류 타입: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 함수"""
    print_header()
    
    print("🔍 LVGL 사용 가능 여부 테스트 중...")
    if test_lvgl_availability():
        print("📱 LVGL 화면 모드로 실행합니다.")
        print("🔍 LVGL 화면 테스터 생성 중...")
        
        # LVGL 화면 테스터 생성
        tester = LVGLSymbolTester()
        
        print("🔍 LVGL 화면 생성 시도 중...")
        # LVGL 화면 생성 시도
        if tester.create_screen():
            print("디스플레이 초기화 완료.")
            
            # 디스플레이 준비
            if tester.show_symbols_directly():
                print("📱 디스플레이가 준비되었습니다!")
                
                # 대화형 심볼 테스트 시작
                tester.interactive_symbol_test()
            else:
                print("❌ 디스플레이 준비에 실패했습니다.")
            
            return
        else:
            print("❌ LVGL 화면 생성 실패, 콘솔 모드로 전환합니다.")
    
    # LVGL 화면 생성 실패 시 콘솔 모드로 실행
    print("📱 콘솔 모드로 실행합니다.")
    print("콘솔에서 카테고리를 선택할 수 있습니다.")
    
    while True:
        print_categories()
        choice = get_user_choice()
        
        if choice == 'quit':
            break
            
        categories = list(SYMBOL_CATEGORIES.keys())
        
        if 1 <= choice <= len(categories):
            # 특정 카테고리 선택
            category_name = categories[choice - 1]
            print_symbols(category_name)
            
        elif choice == len(categories) + 1:
            # 모든 심볼 보기
            print_all_symbols()
            
        elif choice == len(categories) + 2:
            # 종료
            print("\n👋 프로그램을 종료합니다.")
            break
            
        else:
            print("❌ 잘못된 선택입니다. 다시 선택해주세요.")
        
        input("\n⏎ 계속하려면 Enter를 누르세요...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 프로그램을 종료합니다.")
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")
