"""
font_notosans_kr_regular 한글 폰트로 "필박스" 출력 테스트
"""

import sys
import time
import lvgl as lv
import lv_utils
from machine import Pin, SPI
from st77xx import St7735

# 전역 변수
current_display = None
current_offset_x = 0
current_offset_y = 0

def set_st7735_offset(offset_x=0, offset_y=0):
    """ST7735 오프셋 설정"""
    global current_offset_x, current_offset_y
    current_offset_x = offset_x
    current_offset_y = offset_y
    
    print(f"ST7735 오프셋 설정: X={offset_x}, Y={offset_y}")
    
    # ST7735 드라이버의 오프셋 맵 수정
    from st77xx import ST77XX_COL_ROW_MODEL_START_ROTMAP
    
    # blacktab 모델의 오프셋을 조정
    new_offset = [(offset_x, offset_y), (offset_x, offset_y), (offset_x, offset_y), (offset_x, offset_y)]
    ST77XX_COL_ROW_MODEL_START_ROTMAP[(128, 160, 'blacktab')] = new_offset
    
    print(f"오프셋 설정 완료: {new_offset}")

def init_display():
    """ST7735 디스플레이 초기화"""
    global current_display
    
    try:
        # 디스플레이 설정
        DISPLAY_WIDTH = 128
        DISPLAY_HEIGHT = 160
        
        # SPI 설정
        spi = SPI(1, baudrate=40000000, polarity=0, phase=0, sck=Pin(22), mosi=Pin(21))
        
        # 제어 핀 설정
        dc = Pin(19, Pin.OUT)
        cs = Pin(23, Pin.OUT)
        rst = Pin(20, Pin.OUT)
        
        # 오프셋 설정 (초기화 전에 설정)
        set_st7735_offset(offset_x=1, offset_y=2)  # X축 1픽셀, Y축 2픽셀 오프셋
        
        # ST7735 디스플레이 초기화
        current_display = St7735(
            res=(DISPLAY_WIDTH, DISPLAY_HEIGHT),
            model='blacktab',
            cs=cs,
            dc=dc,
            rst=rst,
            spi=spi,
            rot=3,  # 180도 회전
            doublebuffer=False
        )
        
        print("✅ ST7735 디스플레이 초기화 완료")
        return True
        
    except Exception as e:
        print(f"❌ 디스플레이 초기화 실패: {e}")
        return False

def setup_lvgl_environment():
    """LVGL 환경 설정 (초기화, 디스플레이, 이벤트 루프)"""
    try:
        # LVGL 초기화
        lv.init()
        print("✅ LVGL 초기화 완료")
        
        # 디스플레이 초기화
        if not init_display():
            return False
        
        # 디스플레이 백라이트 설정
        if current_display:
            current_display.set_backlight(100)
            print("✅ 디스플레이 백라이트 설정 완료")
        
        # 이벤트 루프 시작
        if not lv_utils.event_loop.is_running():
            event_loop = lv_utils.event_loop()
            print("✅ LVGL 이벤트 루프 시작")
        
        return True
        
    except Exception as e:
        print(f"❌ LVGL 환경 설정 실패: {e}")
        return False

def load_korean_font():
    """한글 폰트 로드"""
    font = getattr(lv, "font_notosans_kr_regular", None)
    if font:
        print("✅ font_notosans_kr_regular 폰트 로드 성공")
    else:
        print("❌ font_notosans_kr_regular 폰트 없음, 기본 폰트 사용")
    return font

def create_screen():
    """기본 화면 생성"""
    scr = lv.obj()
    scr.set_style_bg_color(lv.color_hex(0x000000), 0)  # 검은 배경
    print("✅ 화면 생성 완료")
    return scr

def create_label(parent, text, font=None, color=0xFFFFFF, align=lv.ALIGN.CENTER, x=0, y=0):
    """라벨 생성 헬퍼 함수"""
    label = lv.label(parent)
    if font:
        label.set_style_text_font(font, 0)
    label.set_text(text)
    label.align(align, x, y)
    label.set_style_text_color(lv.color_hex(color), 0)
    return label

def test_pillbox_display():
    """필박스 출력 테스트"""
    print("=" * 60)
    print("필박스 출력 테스트")
    print("=" * 60)
    
    try:
        # LVGL 환경 설정
        if not setup_lvgl_environment():
            return False
        
        # 화면 생성
        scr = create_screen()
        
        # 한글 폰트 로드
        font = load_korean_font()
        
        # "필박스" 라벨 생성
        print("필박스 라벨 생성 중...")
        label = create_label(scr, "필박스", font, align=lv.ALIGN.CENTER, y=0)
        print("✅ 필박스 라벨 생성 완료")
        
        # 화면 로드
        lv.screen_load(scr)
        print("✅ 화면 로드 완료")
        
        # 5초 대기
        print("5초간 표시 중...")
        time.sleep(5)
        
        print("✅ 필박스 출력 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ 필박스 출력 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def main():
    """메인 함수"""
    print("=" * 60)
    print("필박스 출력 테스트 프로그램")
    print("=" * 60)
    print("1. 필박스 출력 테스트")
    print("2. 종료")
    
    while True:
        try:
            choice = input("\n테스트 선택 (1-2): ").strip()
            
            if choice == '1':
                test_pillbox_display()
            elif choice == '2':
                print("테스트 종료")
                break
            else:
                print("잘못된 선택입니다. 1-2 중 선택하세요.")
                
        except KeyboardInterrupt:
            print("\n테스트 중단됨")
            break
        except Exception as e:
            print(f"오류 발생: {e}")
            import sys
            sys.print_exception(e)

if __name__ == "__main__":
    main()