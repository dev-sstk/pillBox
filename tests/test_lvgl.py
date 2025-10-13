"""
LVGL 테스트 코드 - 통합 버전
pill_box 스마트 알약 공급기
"""

import sys
import time
import lvgl as lv
import lv_utils
from machine import Pin, SPI
from st77xx import St7735
import fs_driver

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
    """디스플레이 초기화"""
    global current_display
    
    # 디스플레이 설정
    DISPLAY_WIDTH = 128
    DISPLAY_HEIGHT = 160
    
    # SPI 설정
    spi = SPI(1, baudrate=40000000, polarity=0, phase=0, sck=Pin(22), mosi=Pin(21))
    
    # 제어 핀 설정
    dc = Pin(19, Pin.OUT)
    cs = Pin(23, Pin.OUT)
    rst = Pin(20, Pin.OUT)
    
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
    
    print("✅ 디스플레이 초기화 완료")


def show_test_pattern():
    """테스트 패턴 표시"""
    if current_display is None:
        print("❌ 디스플레이가 초기화되지 않았습니다.")
        return
    
    # 화면 지우기
    current_display.clear(0x0000)  # 검은색
    
    # 테두리 그리기 (빨간색)
    # 상단
    current_display.blit(0, 0, 160, 2, b'\xF8\x00' * 160)
    # 하단
    current_display.blit(0, 158, 160, 2, b'\xF8\x00' * 160)
    # 좌측
    current_display.blit(0, 0, 2, 160, b'\xF8\x00' * 2 * 160)
    # 우측
    current_display.blit(158, 0, 2, 160, b'\xF8\x00' * 2 * 160)
    
    # 중앙 십자가 (흰색)
    # 수직선
    current_display.blit(79, 0, 2, 160, b'\xFF\xFF' * 2 * 160)
    # 수평선
    current_display.blit(0, 79, 160, 2, b'\xFF\xFF' * 160)
    
    # 중앙 원 (파란색)
    current_display.blit(70, 70, 20, 20, b'\x00\x1F' * 20 * 20)
    
    print(f"테스트 패턴 표시 완료 (현재 오프셋: X={current_offset_x}, Y={current_offset_y})")

def adjust_offset(delta_x, delta_y):
    """오프셋 조정"""
    global current_offset_x, current_offset_y
    
    new_x = current_offset_x + delta_x
    new_y = current_offset_y + delta_y
    
    print(f"오프셋 조정: ({current_offset_x}, {current_offset_y}) -> ({new_x}, {new_y})")
    
    # 오프셋 설정
    set_st7735_offset(new_x, new_y)
    
    # 디스플레이 재초기화
    init_display()
    
    # 테스트 패턴 표시
    show_test_pattern()

def test_simple_display():
    """간단한 디스플레이 테스트"""
    print("=" * 50)
    print("간단한 디스플레이 테스트 시작")
    print("=" * 50)
    
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
        
        print("✅ 핀 설정 완료")
        
        # 오프셋 설정 (초기화 전에 설정)
        set_st7735_offset(offset_x=-1, offset_y=-2)  # 위로 2픽셀, 왼쪽으로 1픽셀
        
        # ST7735 디스플레이 초기화 (LVGL 없이)
        display = St7735(
            res=(DISPLAY_WIDTH, DISPLAY_HEIGHT),
            model='blacktab',
            cs=cs,
            dc=dc,
            rst=rst,
            spi=spi,
            rot=1,  # Landscape 모드
            doublebuffer=False,  # LVGL 사용 안함
            factor=1
        )
        
        print("✅ ST7735 디스플레이 초기화 완료")
        
        # 간단한 색상 테스트
        print("색상 테스트 중...")
        display.clear(0x0000)  # 검은색
        time.sleep_ms(1000)
        
        display.clear(0xFFFF)  # 흰색
        time.sleep_ms(1000)
        
        display.clear(0xF800)  # 빨간색
        time.sleep_ms(1000)
        
        display.clear(0x07E0)  # 초록색
        time.sleep_ms(1000)
        
        display.clear(0x001F)  # 파란색
        time.sleep_ms(1000)
        
        print("✅ 간단한 디스플레이 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ 간단한 디스플레이 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_st7735_lvgl():
    """ST7735 드라이버를 사용한 LVGL 테스트"""
    print("=" * 50)
    print("ST7735 LVGL 테스트 시작")
    print("=" * 50)
    
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
        
        print("✅ 핀 설정 완료")
        
        # 오프셋 설정 (초기화 전에 설정)
        set_st7735_offset(offset_x=-1, offset_y=-2)  # 위로 2픽셀, 왼쪽으로 1픽셀
        
        # ST7735 디스플레이 초기화
        display = St7735(
            res=(DISPLAY_WIDTH, DISPLAY_HEIGHT),
            model='blacktab',  # ST7735S는 blacktab 모델
            cs=cs,
            dc=dc,
            rst=rst,
            spi=spi,
            rot=1,  # Landscape 모드
            doublebuffer=True,
            factor=4
        )
        
        print("✅ ST7735 디스플레이 초기화 완료")
        
        # 디스플레이 백라이트 설정
        display.set_backlight(100)
        
        print("✅ 디스플레이 백라이트 설정 완료")
        
        # 이벤트 루프 시작
        if not lv_utils.event_loop.is_running():
            event_loop = lv_utils.event_loop()
            print("✅ LVGL 이벤트 루프 시작")
        
        # 화면 생성
        screen = lv.screen_active()
        
        # 배경색 설정 (검은색)
        screen.set_style_bg_color(lv.color_hex(0x000000), 0)
        
        # 제목 라벨
        title_label = lv.label(screen)
        title_label.set_text("pill_box")
        title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        title_label.set_style_text_font(lv.font_montserrat_16, 0)
        title_label.align(lv.ALIGN.TOP_MID, 0, 10)
        
        # 상태 라벨
        status_label = lv.label(screen)
        status_label.set_text("LVGL 테스트 중...")
        status_label.set_style_text_color(lv.color_hex(0x00FF00), 0)
        status_label.set_style_text_font(lv.font_montserrat_12, 0)
        status_label.align(lv.ALIGN.CENTER, 0, 0)
        
        # 테스트 버튼
        test_btn = lv.button(screen)
        test_btn.set_size(80, 30)
        test_btn.align(lv.ALIGN.BOTTOM_MID, 0, -20)
        
        btn_label = lv.label(test_btn)
        btn_label.set_text("테스트")
        btn_label.center()
        
        # 버튼 클릭 이벤트
        def btn_click_cb(e):
            status_label.set_text("버튼 클릭됨!")
            status_label.set_style_text_color(lv.color_hex(0xFF0000), 0)
        
        test_btn.add_event_cb(btn_click_cb, lv.EVENT.CLICKED, None)
        
        print("✅ 테스트 화면 생성 완료")
        print("화면에 'pill_box' 제목과 '테스트' 버튼이 표시됩니다.")
        
        # 5초간 화면 표시
        print("5초간 테스트 화면 표시 중...")
        for i in range(50):
            lv.task_handler()
            time.sleep_ms(100)
        
        print("✅ ST7735 LVGL 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ ST7735 LVGL 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_offset_adjustment():
    """오프셋 조정 테스트"""
    print("=" * 50)
    print("오프셋 조정 테스트 시작")
    print("=" * 50)
    
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
        
        # ST7735 디스플레이 초기화
        display = St7735(
            res=(DISPLAY_WIDTH, DISPLAY_HEIGHT),
            model='blacktab',
            cs=cs,
            dc=dc,
            rst=rst,
            spi=spi,
            rot=1,
            doublebuffer=False
        )
        
        print("✅ ST7735 디스플레이 초기화 완료")
        
        # 오프셋 테스트
        offsets = [(0, 0), (2, 1), (1, 2), (-1, -1), (3, 2)]
        
        for i, (offset_x, offset_y) in enumerate(offsets):
            print(f"\n--- 오프셋 테스트 {i+1}: ({offset_x}, {offset_y}) ---")
            
            # 화면 지우기
            display.clear(0x0000)  # 검은색
            
            # 테두리 그리기 (빨간색)
            # 상단
            display.blit(0, 0, 160, 2, b'\xF8\x00' * 160)
            # 하단  
            display.blit(0, 158, 160, 2, b'\xF8\x00' * 160)
            # 좌측
            display.blit(0, 0, 2, 160, b'\xF8\x00' * 2 * 160)
            # 우측
            display.blit(158, 0, 2, 160, b'\xF8\x00' * 2 * 160)
            
            # 중앙 십자가 (흰색)
            # 수직선
            display.blit(79, 0, 2, 160, b'\xFF\xFF' * 2 * 160)
            # 수평선
            display.blit(0, 79, 160, 2, b'\xFF\xFF' * 160)
            
            print(f"오프셋 ({offset_x}, {offset_y}) 적용됨")
            print("화면을 확인하고 3초 후 다음 테스트로 진행합니다...")
            time.sleep_ms(3000)
        
        print("✅ 오프셋 조정 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ 오프셋 조정 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

class ST7735OffsetTest:
    """ST7735 오프셋 테스트 클래스"""
    
    def __init__(self):
        """초기화"""
        # 디스플레이 핀 설정 (config.py에서 가져온 값)
        self.DISPLAY_CS_PIN = 23
        self.DISPLAY_SCL_PIN = 22
        self.DISPLAY_SDA_PIN = 21
        self.DISPLAY_RES_PIN = 20
        self.DISPLAY_DC_PIN = 19
        self.DISPLAY_BLK_PIN = 11
        self.DISPLAY_SPI_ID = 1
        self.DISPLAY_WIDTH = 160
        self.DISPLAY_HEIGHT = 128
        
        # 오프셋 설정 (기본값)
        self.column_offset = 0
        self.row_offset = 2
        
        # 디스플레이 핀 설정
        self.cs = Pin(self.DISPLAY_CS_PIN, Pin.OUT)
        self.dc = Pin(self.DISPLAY_DC_PIN, Pin.OUT)
        self.res = Pin(self.DISPLAY_RES_PIN, Pin.OUT)
        self.blk = Pin(self.DISPLAY_BLK_PIN, Pin.OUT)
        
        # SPI 설정
        self.spi = SPI(
            self.DISPLAY_SPI_ID,
            baudrate=40000000,
            polarity=0,
            phase=0,
            sck=Pin(self.DISPLAY_SCL_PIN),
            mosi=Pin(self.DISPLAY_SDA_PIN)
        )
        
        # BLK 핀을 HIGH로 설정 (항상 켜짐)
        self.blk.value(1)
        
        # 디스플레이 초기화
        self.init_display()
        
        print("ST7735 오프셋 테스트 초기화 완료")
        
    def init_display(self):
        """ST7735S 디스플레이 초기화"""
        # 리셋
        self.res.value(0)
        time.sleep_ms(100)
        self.res.value(1)
        time.sleep_ms(100)
        
        # Sleep out
        self.write_cmd(0x11)
        time.sleep_ms(120)
        
        # Memory access control (RGB 순서, 가로 방향)
        self.write_cmd(0x36)
        self.write_data(bytearray([0xA0]))
        
        # Color mode (RGB565)
        self.write_cmd(0x3A)
        self.write_data(bytearray([0x05]))
        
        # Column address set
        self.write_cmd(0x2A)
        self.write_data(bytearray([0x00, self.column_offset, 0x00, self.column_offset + 159]))
        
        # Row address set
        self.write_cmd(0x2B)
        self.write_data(bytearray([0x00, self.row_offset, 0x00, self.row_offset + 127]))
        
        # Display inversion off
        self.write_cmd(0x20)
        
        # Display on
        self.write_cmd(0x29)
        
        print("디스플레이 초기화 완료")
        
    def write_cmd(self, cmd):
        """명령어 쓰기"""
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)
        
    def write_data(self, data):
        """데이터 쓰기"""
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(data)
        self.cs.value(1)
        
    def rgb_to_565(self, r, g, b):
        """RGB888을 RGB565로 변환"""
        r = (r >> 3) & 0x1F
        g = (g >> 2) & 0x3F
        b = (b >> 3) & 0x1F
        return (r << 11) | (g << 5) | b
        
    def fill_rect(self, x, y, width, height, color):
        """사각형 채우기 (오프셋 적용)"""
        # 오프셋을 적용한 실제 좌표 계산
        actual_x = x + self.column_offset
        actual_y = y + self.row_offset
        
        # 컬럼 주소 설정
        self.write_cmd(0x2A)
        self.write_data(bytearray([0x00, actual_x, 0x00, actual_x + width - 1]))
        
        # 로우 주소 설정
        self.write_cmd(0x2B)
        self.write_data(bytearray([0x00, actual_y, 0x00, actual_y + height - 1]))
        
        # 메모리 쓰기
        self.write_cmd(0x2C)
        
        # RGB565 컬러로 변환
        color_565 = self.rgb_to_565(*color)
        color_bytes = bytearray([color_565 >> 8, color_565 & 0xFF])
        
        # 픽셀 데이터 전송
        self.dc.value(1)
        self.cs.value(0)
        for _ in range(width * height):
            self.spi.write(color_bytes)
        self.cs.value(1)
        
    def clear_screen(self):
        """화면 지우기 (검정색) - 전체 영역 채우기"""
        # 오프셋을 고려한 전체 화면 지우기
        # 컬럼 주소 설정 (전체 영역)
        self.write_cmd(0x2A)
        self.write_data(bytearray([0x00, self.column_offset, 0x00, self.column_offset + 159]))
        
        # 로우 주소 설정 (전체 영역)
        self.write_cmd(0x2B)
        self.write_data(bytearray([0x00, self.row_offset, 0x00, self.row_offset + 127]))
        
        # 메모리 쓰기
        self.write_cmd(0x2C)
        
        # 검정색 RGB565
        black_color = bytearray([0x00, 0x00])
        
        # 전체 픽셀 데이터 전송 (160 * 128 = 20480 픽셀)
        self.dc.value(1)
        self.cs.value(0)
        for _ in range(160 * 128):
            self.spi.write(black_color)
        self.cs.value(1)
        
    def fill_screen_white(self):
        """화면을 흰색으로 완전히 채우기"""
        # 컬럼 주소 설정 (전체 영역)
        self.write_cmd(0x2A)
        self.write_data(bytearray([0x00, self.column_offset, 0x00, self.column_offset + 159]))
        
        # 로우 주소 설정 (전체 영역)
        self.write_cmd(0x2B)
        self.write_data(bytearray([0x00, self.row_offset, 0x00, self.row_offset + 127]))
        
        # 메모리 쓰기
        self.write_cmd(0x2C)
        
        # 흰색 RGB565
        white_color = bytearray([0xFF, 0xFF])
        
        # 전체 픽셀 데이터 전송 (160 * 128 = 20480 픽셀)
        self.dc.value(1)
        self.cs.value(0)
        for _ in range(160 * 128):
            self.spi.write(white_color)
        self.cs.value(1)
        
    def show_test_pattern(self):
        """테스트 패턴 표시"""
        # 화면을 흰색으로 완전히 채우기
        self.fill_screen_white()
        
        # 가장자리에 빨간색 테두리 그리기
        border_color = (255, 0, 0)
        
        # 상단 테두리
        self.fill_rect(0, 0, self.DISPLAY_WIDTH, 2, border_color)
        # 하단 테두리
        self.fill_rect(0, self.DISPLAY_HEIGHT-2, self.DISPLAY_WIDTH, 2, border_color)
        # 좌측 테두리
        self.fill_rect(0, 0, 2, self.DISPLAY_HEIGHT, border_color)
        # 우측 테두리
        self.fill_rect(self.DISPLAY_WIDTH-2, 0, 2, self.DISPLAY_HEIGHT, border_color)
        
        # 중앙 십자가 (검은색)
        # 수직선
        self.fill_rect(79, 0, 2, self.DISPLAY_HEIGHT, (0, 0, 0))
        # 수평선
        self.fill_rect(0, 63, self.DISPLAY_WIDTH, 2, (0, 0, 0))
        
        # 중앙 원 (파란색)
        self.fill_rect(70, 54, 20, 20, (0, 0, 255))
        
        print(f"테스트 패턴 표시 완료 (현재 오프셋: X={self.column_offset}, Y={self.row_offset})")
        
    def set_offset_interactive(self):
        """대화형으로 오프셋 설정"""
        print("\n=== 오프셋 설정 ===")
        print(f"현재 컬럼 오프셋: {self.column_offset}")
        print(f"현재 로우 오프셋: {self.row_offset}")
        print("오프셋 범위: 0-20 (권장: 0-10)")
        
        try:
            # 컬럼 오프셋 입력
            while True:
                try:
                    col_offset = int(input("새로운 컬럼 오프셋 (0-20): "))
                    if 0 <= col_offset <= 20:
                        self.column_offset = col_offset
                        break
                    else:
                        print("0-20 범위 내에서 입력하세요.")
                except ValueError:
                    print("숫자를 입력하세요.")
            
            # 로우 오프셋 입력
            while True:
                try:
                    row_offset = int(input("새로운 로우 오프셋 (0-20): "))
                    if 0 <= row_offset <= 20:
                        self.row_offset = row_offset
                        break
                    else:
                        print("0-20 범위 내에서 입력하세요.")
                except ValueError:
                    print("숫자를 입력하세요.")
            
            # 디스플레이 재초기화
            print("디스플레이 재초기화 중...")
            self.init_display()
            
            # 테스트 패턴 표시
            self.show_test_pattern()
            
            print(f"오프셋 설정 완료!")
            print(f"컬럼 오프셋: {self.column_offset}")
            print(f"로우 오프셋: {self.row_offset}")
            
        except Exception as e:
            print(f"오프셋 설정 오류: {e}")
    
    def test_offset_visual(self):
        """오프셋 시각적 테스트"""
        print("오프셋 시각적 테스트 시작...")
        
        # 테스트 패턴 표시
        self.show_test_pattern()
        
        print("화면이 흰색으로 채워지고 빨간색 테두리가 그려졌습니다.")
        print("가장자리가 완전히 채워지는지 확인하세요.")
        print("5초 후 검은색으로 지워집니다...")
        time.sleep_ms(5000)
        
        # 화면 지우기
        self.clear_screen()
        print("오프셋 시각적 테스트 완료!")
        
    def test_color_screen(self, color):
        """특정 색상으로 화면 채우기"""
        # 컬럼 주소 설정 (전체 영역)
        self.write_cmd(0x2A)
        self.write_data(bytearray([0x00, self.column_offset, 0x00, self.column_offset + 159]))
        
        # 로우 주소 설정 (전체 영역)
        self.write_cmd(0x2B)
        self.write_data(bytearray([0x00, self.row_offset, 0x00, self.row_offset + 127]))
        
        # 메모리 쓰기
        self.write_cmd(0x2C)
        
        # RGB565 컬러로 변환
        color_565 = self.rgb_to_565(*color)
        color_bytes = bytearray([color_565 >> 8, color_565 & 0xFF])
        
        # 전체 픽셀 데이터 전송 (160 * 128 = 20480 픽셀)
        self.dc.value(1)
        self.cs.value(0)
        for _ in range(160 * 128):
            self.spi.write(color_bytes)
        self.cs.value(1)
        
        print(f"화면을 {color} 색상으로 채웠습니다. (오프셋: X={self.column_offset}, Y={self.row_offset})")

def interactive_offset_adjustment():
    """대화형 오프셋 조정"""
    print("=" * 60)
    print("ST7735 대화형 오프셋 조정")
    print("=" * 60)
    
    # 테스트 객체 생성
    offset_test = ST7735OffsetTest()
    
    print("\n대화형 오프셋 조정 시작!")
    print("다음 명령어를 사용하세요:")
    print("  up()     - 위로 1픽셀 이동")
    print("  down()   - 아래로 1픽셀 이동")
    print("  left()   - 왼쪽으로 1픽셀 이동")
    print("  right()  - 오른쪽으로 1픽셀 이동")
    print("  reset()  - 오프셋 초기화")
    print("  show()   - 현재 테스트 패턴 표시")
    print("  set(x,y) - 특정 오프셋으로 설정")
    print("  quit()   - 종료")

def test_offset_with_colors():
    """색상과 함께 오프셋 테스트"""
    print("=" * 60)
    print("색상과 함께 오프셋 테스트")
    print("=" * 60)
    
    # 테스트 객체 생성
    offset_test = ST7735OffsetTest()
    
    # 테스트할 색상들
    test_colors = [
        (0, 0, 255),    # 파란색
        (255, 0, 0),    # 빨간색
        (0, 255, 0),    # 초록색
        (255, 255, 0),  # 노란색
        (255, 0, 255),  # 마젠타
        (0, 255, 255),  # 시안
        (255, 165, 0),  # 주황색
        (128, 0, 128),  # 보라색
    ]
    
    print("색상과 함께 오프셋 테스트를 시작합니다.")
    print("각 색상마다 오프셋을 조정할 수 있습니다.")
    
    for i, color in enumerate(test_colors):
        print(f"\n--- 색상 {i+1}/{len(test_colors)}: {color} ---")
        
        # 색상으로 화면 채우기
        offset_test.test_color_screen(color)
        
        # 오프셋 조정 여부 확인
        while True:
            try:
                adjust = input("오프셋을 조정하시겠습니까? (y/n): ").strip().lower()
                if adjust in ['y', 'yes', 'n', 'no']:
                    break
                else:
                    print("y 또는 n을 입력하세요.")
            except:
                break
        
        if adjust in ['y', 'yes']:
            # 오프셋 조정
            offset_test.set_offset_interactive()
            
            # 조정된 오프셋으로 다시 색상 표시
            offset_test.test_color_screen(color)
        
        # 다음 색상으로 진행 여부 확인
        if i < len(test_colors) - 1:
            while True:
                try:
                    next_color = input("다음 색상으로 진행하시겠습니까? (y/n): ").strip().lower()
                    if next_color in ['y', 'yes', 'n', 'no']:
                        break
                    else:
                        print("y 또는 n을 입력하세요.")
                except:
                    break
            
            if next_color in ['n', 'no']:
                break
    
    print("색상과 함께 오프셋 테스트 완료!")

def test_offset_cycle():
    """오프셋 순환 테스트"""
    print("=" * 60)
    print("오프셋 순환 테스트")
    print("=" * 60)
    
    # 테스트 객체 생성
    offset_test = ST7735OffsetTest()
    
    # 테스트할 오프셋들
    test_offsets = [
        (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
        (0, 1), (1, 1), (2, 1), (3, 1), (4, 1),
        (0, 2), (1, 2), (2, 2), (3, 2), (4, 2),
    ]
    
    # 파란색으로 화면 채우기
    blue_color = (0, 0, 255)
    
    for i, (col_offset, row_offset) in enumerate(test_offsets):
        print(f"테스트 {i+1}/{len(test_offsets)}: 오프셋 ({col_offset}, {row_offset})")
        
        # 오프셋 설정
        offset_test.column_offset = col_offset
        offset_test.row_offset = row_offset
        
        # 디스플레이 재초기화
        offset_test.init_display()
        
        # 파란색으로 화면 채우기
        offset_test.test_color_screen(blue_color)
        
        # 2초 대기
        time.sleep_ms(2000)
        
    print("오프셋 순환 테스트 완료!")

def quick_test():
    """빠른 테스트"""
    print("빠른 오프셋 테스트 시작...")
    
    # 테스트 객체 생성
    offset_test = ST7735OffsetTest()
    
    # 빠른 테스트 오프셋들
    quick_offsets = [(0, 0), (2, 1), (1, 2), (3, 2), (0, 0)]
    
    # 파란색으로 화면 채우기
    blue_color = (0, 0, 255)
    
    for i, (col_offset, row_offset) in enumerate(quick_offsets):
        print(f"빠른 테스트 {i+1}: 오프셋 ({col_offset}, {row_offset})")
        
        # 오프셋 설정
        offset_test.column_offset = col_offset
        offset_test.row_offset = row_offset
        
        # 디스플레이 재초기화
        offset_test.init_display()
        
        # 파란색으로 화면 채우기
        offset_test.test_color_screen(blue_color)
        
        # 1.5초 대기
        time.sleep_ms(1500)
        
    print("빠른 테스트 완료!")

def test_lvgl_basic():
    """LVGL 기본 기능 테스트"""
    print("=" * 50)
    print("LVGL 기본 기능 테스트 시작")
    print("=" * 50)
    
    try:
        # LVGL 초기화 확인
        print("LVGL 초기화 상태 확인 중...")
        
        # 간단한 테스트 화면 생성
        screen = test_st7735_lvgl()
        
        print("✅ LVGL 기본 기능 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ LVGL 기본 기능 테스트 실패: {e}")
        return False

def test_lvgl_demo():
    """LVGL 데모 실행"""
    print("=" * 50)
    print("LVGL 데모 실행")
    print("=" * 50)
    
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
        
        # 오프셋 설정
        set_st7735_offset(-1, -2)
        
        # ST7735 디스플레이 초기화
        display = St7735(
            res=(DISPLAY_WIDTH, DISPLAY_HEIGHT),
            model='blacktab',
            cs=cs,
            dc=dc,
            rst=rst,
            spi=spi,
            rot=1,
            doublebuffer=True,
            factor=4
        )
        
        # 이벤트 루프 시작
        if not lv_utils.event_loop.is_running():
            event_loop = lv_utils.event_loop()
        
        # 데모 화면 생성
        screen = lv.screen_active()
        screen.set_style_bg_color(lv.color_hex(0x000080), 0)
        
        # 데모 라벨
        demo_label = lv.label(screen)
        demo_label.set_text("LVGL Demo\npill_box")
        demo_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        demo_label.set_style_text_font(lv.font_montserrat_16, 0)
        demo_label.align(lv.ALIGN.CENTER, 0, 0)
        
        # 3초간 데모 표시
        print("3초간 데모 화면 표시 중...")
        for i in range(30):
            lv.task_handler()
            time.sleep_ms(100)
        
        print("✅ LVGL 데모 완료")
        return True
        
    except Exception as e:
        print(f"❌ LVGL 데모 실패: {e}")
        return False

def test_lvgl_keyboard():
    """LVGL 키보드 테스트 (물리 버튼으로 키 선택)"""
    print("=" * 60)
    print("LVGL 키보드 테스트")
    print("=" * 60)
    print("버튼 매핑:")
    print("  버튼 0 (Select): 선택된 키 입력")
    print("  버튼 1 (Left): 왼쪽 키로 이동")
    print("  버튼 2 (Right): 오른쪽 키로 이동")
    print("  버튼 3 (Cancel): 글자 삭제")
    print("=" * 60)
    
    try:
        # 버튼 인터페이스 초기화
        import sys
        sys.path.append('src')
        from button_interface import ButtonInterface
        button_interface = ButtonInterface()
        
        # LVGL 초기화
        lv.init()
        
        # 디스플레이 초기화 (오프셋 0, 2 적용)
        set_st7735_offset(1, 2)
        init_display()
        
        # 디스플레이 백라이트 설정
        if current_display:
            current_display.set_backlight(100)
            print("✅ 디스플레이 백라이트 설정 완료")
        
        # ST7735가 이미 LVGL 디스플레이 드라이버를 자동으로 설정함
        print("ST7735 LVGL 통합 완료")
        
        print("LVGL 디스플레이 설정 완료")
        
        # 화면 생성 (올바른 구조)
        scr = lv.obj()
        scr.set_style_bg_color(lv.color_hex(0x000000), 0)
        
        # 제목 라벨 추가
        title_label = lv.label(scr)
        title_label.set_text("Keyboard Test")
        title_label.align(lv.ALIGN.TOP_MID, 0, 5)
        title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 텍스트 영역 생성
        text_area = lv.textarea(scr)
        text_area.set_size(120, 25)
        text_area.align(lv.ALIGN.CENTER, 0, -35)
        text_area.set_placeholder_text("Type here...")
        text_area.set_one_line(True)
        text_area.set_style_bg_color(lv.color_hex(0x333333), 0)
        text_area.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 키보드 생성 (큰 키보드)
        kb = lv.keyboard(scr)
        kb.set_size(150, 80)  # 키보드 크기 증가
        kb.align(lv.ALIGN.BOTTOM_MID, 0, -5)  # 아래쪽에 가득차게
        kb.set_textarea(text_area)
        kb.set_style_bg_color(lv.color_hex(0x444444), 0)
        
        # 현재 선택된 키 표시 라벨
        selected_key_label = lv.label(scr)
        selected_key_label.set_text("Selected: A")
        selected_key_label.align(lv.ALIGN.CENTER, 0, 50)
        selected_key_label.set_style_text_color(lv.color_hex(0x00FF00), 0)
        
        # 설명 라벨
        desc_label = lv.label(scr)
        desc_label.set_text("0:Type 1:Up 2:Down 3:Exit")
        desc_label.align(lv.ALIGN.BOTTOM_MID, 0, -10)
        desc_label.set_style_text_color(lv.color_hex(0x888888), 0)
        
        # 화면 로드
        lv.screen_load(scr)
        
        print("UI 요소 생성 완료")
        
        # 키보드 키 배열 정의 (간단한 키보드)
        keyboard_keys = [
            ['Q', 'W', 'E', 'R', 'T'],
            ['A', 'S', 'D', 'F', 'G'],
            ['Z', 'X', 'C', 'V', 'B'],
            ['1', '2', '3', '4', '5'],
            [' ', 'Back', 'Enter', 'Clear', 'Exit']
        ]
        
        # 현재 선택된 키 위치
        current_row = 0
        current_col = 0
        
        # 버튼 상태 추적
        last_button_states = {'select': False, 'up': False, 'down': False, 'menu': False}
        
        # 이벤트 루프 시작
        try:
            event_loop = lv_utils.event_loop(freq=25)
        except RuntimeError as e:
            if "already running" in str(e):
                event_loop = None
        
        print("키보드 테스트 시작! 물리 버튼으로 키를 선택하고 입력하세요.")
        
        while True:
            # 버튼 상태 읽기
            button_states = button_interface.get_all_button_states()
            select_pressed = button_states.get('select', 1) == 0
            up_pressed = button_states.get('up', 1) == 0
            down_pressed = button_states.get('down', 1) == 0
            menu_pressed = button_states.get('menu', 1) == 0
            
            # 버튼 0 (Select) - 선택된 키 입력
            if select_pressed and not last_button_states['select']:
                selected_key = keyboard_keys[current_row][current_col]
                print(f"키 입력: {selected_key}")
                
                if selected_key == 'Back':
                    # 백스페이스
                    current_text = text_area.get_text()
                    if current_text and len(current_text) > 0:
                        new_text = current_text[:-1]
                        text_area.set_text(new_text)
                elif selected_key == 'Enter':
                    # 엔터
                    text_area.add_char(ord('\n'))
                elif selected_key == 'Clear':
                    # 텍스트 지우기
                    text_area.set_text("")
                elif selected_key == 'Exit':
                    # 테스트 종료
                    print("키보드 테스트 종료")
                    break
                elif selected_key == ' ':
                    # 스페이스
                    text_area.add_char(ord(' '))
                else:
                    # 일반 문자
                    text_area.add_char(ord(selected_key))
            
            # 버튼 1 (Left) - 왼쪽으로 이동
            if up_pressed and not last_button_states['up']:
                if current_col > 0:
                    current_col -= 1
                else:
                    # 맨 왼쪽에서 위로 이동
                    if current_row > 0:
                        current_row -= 1
                        current_col = len(keyboard_keys[current_row]) - 1
                print(f"왼쪽 이동: ({current_row}, {current_col})")
            
            # 버튼 2 (Right) - 오른쪽으로 이동
            if down_pressed and not last_button_states['down']:
                if current_col < len(keyboard_keys[current_row]) - 1:
                    current_col += 1
                else:
                    # 맨 오른쪽에서 아래로 이동
                    if current_row < len(keyboard_keys) - 1:
                        current_row += 1
                        current_col = 0
                print(f"오른쪽 이동: ({current_row}, {current_col})")
            
            # 버튼 3 (Cancel) - 글자 삭제
            if menu_pressed and not last_button_states['menu']:
                # 현재 텍스트 가져오기
                current_text = text_area.get_text()
                if current_text and len(current_text) > 0:
                    # 마지막 문자 제거
                    new_text = current_text[:-1]
                    text_area.set_text(new_text)
                    print("글자 삭제")
                else:
                    print("삭제할 글자가 없음")
            
            # 현재 선택된 키 표시 업데이트
            selected_key = keyboard_keys[current_row][current_col]
            selected_key_label.set_text(f"Selected: {selected_key}")
            
            last_button_states = {'select': select_pressed, 'up': up_pressed, 'down': down_pressed, 'menu': menu_pressed}
            time.sleep_ms(50)
            
    except Exception as e:
        print(f"❌ LVGL 키보드 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_lvgl_buttons():
    """LVGL 버튼 테스트 (물리 버튼으로 버튼 조작)"""
    print("=" * 60)
    print("LVGL 버튼 테스트")
    print("=" * 60)
    print("버튼 매핑:")
    print("  버튼 0 (Select): 버튼 클릭")
    print("  버튼 1 (Left): 버튼 색상 변경")
    print("  버튼 2 (Right): 버튼 크기 변경")
    print("  버튼 3 (Cancel): 테스트 종료")
    print("=" * 60)
    
    try:
        # 버튼 인터페이스 초기화
        import sys
        sys.path.append('src')
        from button_interface import ButtonInterface
        button_interface = ButtonInterface()
        
        # LVGL 초기화
        lv.init()
        
        # 디스플레이 초기화 (오프셋 0, 2 적용)
        set_st7735_offset(1, 2)
        init_display()
        
        # 디스플레이 백라이트 설정
        if current_display:
            current_display.set_backlight(100)
            print("✅ 디스플레이 백라이트 설정 완료")
        
        # ST7735가 이미 LVGL 디스플레이 드라이버를 자동으로 설정함
        print("ST7735 LVGL 통합 완료")
        
        print("LVGL 디스플레이 설정 완료")
        
        # 화면 생성 (올바른 구조)
        scr = lv.obj()
        scr.set_style_bg_color(lv.color_hex(0x000000), 0)
        
        # 한글 폰트 로드 시도
        korean_font = load_korean_font()
        
        # 제목 라벨
        title_label = lv.label(scr)
        title_label.align(lv.ALIGN.TOP_MID, 0, 5)
        title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        if korean_font:
            title_label.set_style_text_font(korean_font, 0)
            title_label.set_text("버튼 테스트")
        else:
            title_label.set_text("Button Test")
        
        # 버튼 생성
        btn = lv.button(scr)
        btn.set_size(100, 40)
        btn.align(lv.ALIGN.CENTER, 0, -20)
        btn.set_style_bg_color(lv.color_hex(0x0066CC), 0)  # 파란색 버튼
        btn.set_style_border_width(2, 0)  # 테두리 추가
        btn.set_style_border_color(lv.color_hex(0x004499), 0)  # 진한 파란색 테두리
        btn.set_style_shadow_width(5, 0)  # 그림자 효과
        btn.set_style_shadow_color(lv.color_hex(0x000000), 0)  # 검은색 그림자
        
        # 버튼 라벨
        label = lv.label(btn)
        label.center()
        label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)  # 흰색 텍스트
        
        if korean_font:
            label.set_style_text_font(korean_font, 0)
            label.set_text("클릭하세요!")
        else:
            label.set_text("Click Me!")
        
        # 상태 표시 라벨
        status_label = lv.label(scr)
        status_label.align(lv.ALIGN.CENTER, 0, 20)
        status_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        if korean_font:
            status_label.set_style_text_font(korean_font, 0)
            status_label.set_text("클릭 횟수: 0")
        else:
            status_label.set_text("Click count: 0")
        
        # 설명 라벨
        desc_label = lv.label(scr)
        desc_label.align(lv.ALIGN.BOTTOM_MID, 0, -10)
        desc_label.set_style_text_color(lv.color_hex(0x888888), 0)
        
        if korean_font:
            desc_label.set_style_text_font(korean_font, 0)
            desc_label.set_text("0:클릭 1:색상 2:크기 3:종료")
        else:
            desc_label.set_text("0:Click 1:Color 2:Size 3:Exit")
        
        # 버튼을 맨 앞으로 가져오기
        btn.move_foreground()
        
        # 화면 로드
        lv.screen_load(scr)
        
        # 클릭 카운터 및 버튼 상태
        click_count = 0
        color_index = 0
        size_index = 0
        
        # 버튼 색상 배열
        colors = [
            (0x0066CC, "Blue"),    # 파란색
            (0xCC0000, "Red"),     # 빨간색
            (0x00CC00, "Green"),   # 초록색
            (0xCCCC00, "Yellow"),  # 노란색
            (0xCC00CC, "Purple")   # 보라색
        ]
        
        # 버튼 크기 배열
        sizes = [
            (80, 30, "Small"),
            (100, 40, "Medium"),
            (120, 50, "Large")
        ]
        
        # 버튼 이벤트 핸들러
        def btn_event_handler(e):
            nonlocal click_count
            code = e.get_code()
            if code == lv.EVENT.CLICKED:
                click_count += 1
                if korean_font:
                    status_label.set_text(f"클릭 횟수: {click_count}")
                else:
                    status_label.set_text(f"Click count: {click_count}")
                print(f"버튼 클릭: {click_count}")
        
        btn.add_event_cb(btn_event_handler, lv.EVENT.ALL, None)
        
        # 버튼 눌림 효과 변수
        button_press_timer = 0
        button_pressed = False
        
        print("버튼 테스트 시작! 물리 버튼으로 버튼을 조작하세요.")
        
        # 버튼 상태 추적
        last_button_states = {'select': False, 'up': False, 'down': False, 'menu': False}
        
        # 이벤트 루프 시작
        try:
            event_loop = lv_utils.event_loop(freq=25)
        except RuntimeError as e:
            if "already running" in str(e):
                event_loop = None
        
        while True:
            try:
                # 버튼 상태 읽기
                button_states = button_interface.get_all_button_states()
                select_pressed = button_states.get('select', 1) == 0
                up_pressed = button_states.get('up', 1) == 0
                down_pressed = button_states.get('down', 1) == 0
                menu_pressed = button_states.get('menu', 1) == 0
                
                # 버튼 0 (Select) - 버튼 클릭
                if select_pressed and not last_button_states['select']:
                    # 버튼 눌림 효과 시작
                    button_pressed = True
                    button_press_timer = 0
                    btn.set_style_bg_color(lv.color_hex(0x003366), 0)  # 어두운 파란색
                    btn.set_style_shadow_width(0, 0)  # 그림자 제거
                    btn.set_style_border_color(lv.color_hex(0x001133), 0)  # 더 어두운 테두리
                    
                    btn.send_event(lv.EVENT.CLICKED, None)
                    print("Select 버튼 눌림 - 버튼 클릭")
                
                # 버튼 1 (Up/Left) - 색상 변경
                if up_pressed and not last_button_states['up']:
                    color_index = (color_index + 1) % len(colors)
                    color_hex, color_name = colors[color_index]
                    btn.set_style_bg_color(lv.color_hex(color_hex), 0)
                    print(f"색상 변경: {color_name}")
                
                # 버튼 2 (Down/Right) - 크기 변경
                if down_pressed and not last_button_states['down']:
                    size_index = (size_index + 1) % len(sizes)
                    width, height, size_name = sizes[size_index]
                    btn.set_size(width, height)
                    print(f"크기 변경: {size_name}")
                
                # 버튼 3 (Menu/Back) - 테스트 종료
                if menu_pressed and not last_button_states['menu']:
                    print("버튼 테스트 종료")
                    break
                
                # 버튼 눌림 효과 처리
                if button_pressed:
                    button_press_timer += 1
                    if button_press_timer >= 3:  # 150ms 후 복원 (50ms * 3)
                        # 원래 상태로 복원
                        color_hex, _ = colors[color_index]
                        btn.set_style_bg_color(lv.color_hex(color_hex), 0)
                        btn.set_style_shadow_width(5, 0)
                        btn.set_style_shadow_ofs_x(2, 0)
                        btn.set_style_shadow_ofs_y(2, 0)
                        btn.set_style_border_color(lv.color_hex(0x004499), 0)
                        button_pressed = False
                        button_press_timer = 0
                
                last_button_states = {'select': select_pressed, 'up': up_pressed, 'down': down_pressed, 'menu': menu_pressed}
                time.sleep_ms(50)
                
            except KeyboardInterrupt:
                print("\n버튼 테스트 중단됨")
                break
            
    except Exception as e:
        print(f"❌ LVGL 버튼 테스트 실패: {e}")
        import sys
        sys.print_exception(e)

def load_korean_font():
    """메모리 효율적인 폰트 로드 (크기 순서로 시도)"""
    try:
        import os
        
        # 메모리 효율적인 폰트 파일들 (크기 순서)
        font_files = [
            ("font-PHT-en-20.bin", "영어 폰트 (3.7KB)"),
            ("font-PHT-cn-20.bin", "중국어 폰트 (2.3KB)"),
            ("font-PHT-jp-20.bin", "일본어 폰트 (456B)"),
            ("NotoSansKR.bin", "한글 폰트 (346KB - 메모리 부족 가능)")
        ]
        
        for font_file, description in font_files:
            try:
                print(f"  {description} 시도 중...")
                korean_font = lv.binfont_create(font_file)
                if korean_font is not None:
                    print(f"✅ {description} 로드 성공")
                    print(f"폰트 객체 생성됨: {korean_font}")
                    return korean_font
            except MemoryError as e:
                print(f"❌ {description} 메모리 부족: {e}")
                print(f"   파일이 너무 큽니다. 다음 폰트를 시도합니다.")
                continue
            except Exception as e:
                print(f"❌ {description} 로드 실패: {e}")
                continue
        
        print("❌ 모든 폰트 로드 실패, 기본 폰트 사용")
        return None
            
    except Exception as e:
        print(f"❌ 폰트 로드 오류: {e}")
        return None

def test_lvgl_simple():
    """LVGL 간단한 테스트 (라벨만 표시)"""
    print("=" * 60)
    print("LVGL 간단한 테스트")
    print("=" * 60)
    
    try:
        # 기존 디스플레이 정리
        global current_display
        if current_display:
            current_display = None
            print("기존 디스플레이 객체 정리 완료")
        
        # LVGL 초기화
        lv.init()
        
        # 디스플레이 초기화 (오프셋 -1, 2 적용)
        set_st7735_offset(1, 2)
        init_display()
        
        # 디스플레이 백라이트 설정
        if current_display:
            current_display.set_backlight(100)
            print("✅ 디스플레이 백라이트 설정 완료")
        
        # ST7735가 이미 LVGL 디스플레이 드라이버를 자동으로 설정함
        print("ST7735 LVGL 통합 완료")
        
        print("LVGL 디스플레이 설정 완료")
        
        # 이벤트 루프 시작 (화면 업데이트를 위해)
        if not lv_utils.event_loop.is_running():
            event_loop = lv_utils.event_loop()
            print("✅ LVGL 이벤트 루프 시작")
        
        # 화면 생성
        scr = lv.obj()
        scr.set_style_bg_color(lv.color_hex(0x000000), 0)  # 검은 배경
        
        # 한글 폰트 로드 시도
        korean_font = load_korean_font()
        
        # 간단한 라벨 생성
        label = lv.label(scr)
        label.align(lv.ALIGN.CENTER, 0, 0)
        label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)  # 흰색 텍스트
        
        if korean_font:
            # 한글 폰트 적용
            label.set_style_text_font(korean_font, 0)
            label.set_text("PILLBOX")
            print("✅ 한글 폰트 적용 완료")
        else:
            label.set_text("PILLBOX")
            print("❌ 한글 폰트 없음, 영어로 표시")
        
        # 화면 로드
        lv.screen_load(scr)
        
        print("간단한 라벨 표시 완료")
        print("화면에 'PILLBOX' 텍스트가 가운데 정렬되어 표시되어야 합니다.")
        
        # LVGL 타이머 핸들러 호출 (화면 강제 업데이트)
        for i in range(10):
            lv.timer_handler()
            time.sleep(0.1)
        
        # 5초 대기
        time.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"❌ LVGL 간단한 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_lvgl_symbol_buttons():
    """LVGL 심볼 버튼 테스트 (물리 버튼으로 버튼 선택)"""
    print("=" * 60)
    print("LVGL 심볼 버튼 테스트")
    print("=" * 60)
    print("버튼 매핑:")
    print("  버튼 0 (Select): 선택된 버튼 클릭")
    print("  버튼 1 (Left): 왼쪽 버튼으로 이동")
    print("  버튼 2 (Right): 오른쪽 버튼으로 이동")
    print("  버튼 3 (Cancel): 테스트 종료")
    print("=" * 60)
    
    try:
        # 버튼 인터페이스 초기화
        import sys
        sys.path.append('src')
        from button_interface import ButtonInterface
        button_interface = ButtonInterface()
        
        # LVGL 초기화
        lv.init()
        
        # 디스플레이 초기화 (오프셋 0, 2 적용)
        set_st7735_offset(1, 2)
        init_display()
        
        # 디스플레이 백라이트 설정
        if current_display:
            current_display.set_backlight(100)
            print("✅ 디스플레이 백라이트 설정 완료")
        
        # ST7735가 이미 LVGL 디스플레이 드라이버를 자동으로 설정함
        print("ST7735 LVGL 통합 완료")
        
        print("LVGL 디스플레이 설정 완료")
        
        # 화면 생성
        scr = lv.obj()
        scr.set_style_bg_color(lv.color_hex(0x000000), 0)
        
        # 제목 라벨
        title_label = lv.label(scr)
        title_label.set_text("Symbol Button Test")
        title_label.align(lv.ALIGN.TOP_MID, 0, 5)
        title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 심볼 버튼들 생성 (2x2 그리드)
        btn1 = lv.button(scr)
        btn1.set_size(50, 40)
        btn1.align(lv.ALIGN.CENTER, -30, -25)
        btn1.set_style_bg_color(lv.color_hex(0x0066CC), 0)
        btn1.set_style_border_width(2, 0)
        btn1.set_style_border_color(lv.color_hex(0x004499), 0)
        btn1.set_style_shadow_width(3, 0)
        btn1.set_style_shadow_color(lv.color_hex(0x000000), 0)
        
        btn1_label = lv.label(btn1)
        btn1_label.set_text(lv.SYMBOL.PLAY)
        btn1_label.center()
        btn1_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        btn2 = lv.button(scr)
        btn2.set_size(50, 40)
        btn2.align(lv.ALIGN.CENTER, 30, -25)
        btn2.set_style_bg_color(lv.color_hex(0x0066CC), 0)
        btn2.set_style_border_width(2, 0)
        btn2.set_style_border_color(lv.color_hex(0x004499), 0)
        btn2.set_style_shadow_width(3, 0)
        btn2.set_style_shadow_color(lv.color_hex(0x000000), 0)
        
        btn2_label = lv.label(btn2)
        btn2_label.set_text(lv.SYMBOL.PAUSE)
        btn2_label.center()
        btn2_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        btn3 = lv.button(scr)
        btn3.set_size(50, 40)
        btn3.align(lv.ALIGN.CENTER, -30, 25)
        btn3.set_style_bg_color(lv.color_hex(0x0066CC), 0)
        btn3.set_style_border_width(2, 0)
        btn3.set_style_border_color(lv.color_hex(0x004499), 0)
        btn3.set_style_shadow_width(3, 0)
        btn3.set_style_shadow_color(lv.color_hex(0x000000), 0)
        
        btn3_label = lv.label(btn3)
        btn3_label.set_text(lv.SYMBOL.STOP)
        btn3_label.center()
        btn3_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        btn4 = lv.button(scr)
        btn4.set_size(50, 40)
        btn4.align(lv.ALIGN.CENTER, 30, 25)
        btn4.set_style_bg_color(lv.color_hex(0x0066CC), 0)
        btn4.set_style_border_width(2, 0)
        btn4.set_style_border_color(lv.color_hex(0x004499), 0)
        btn4.set_style_shadow_width(3, 0)
        btn4.set_style_shadow_color(lv.color_hex(0x000000), 0)
        
        btn4_label = lv.label(btn4)
        btn4_label.set_text(lv.SYMBOL.REFRESH)
        btn4_label.center()
        btn4_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 버튼 배열
        buttons = [btn1, btn2, btn3, btn4]
        button_names = ["Play", "Pause", "Stop", "Refresh"]
        
        # 현재 선택된 버튼 표시 라벨
        selected_label = lv.label(scr)
        selected_label.set_text("Selected: Play")
        selected_label.align(lv.ALIGN.CENTER, 0, 60)
        selected_label.set_style_text_color(lv.color_hex(0x00FF00), 0)
        
        # 설명 라벨
        desc_label = lv.label(scr)
        desc_label.set_text("0:Click 1:Up 2:Down 3:Exit")
        desc_label.align(lv.ALIGN.BOTTOM_MID, 0, -10)
        desc_label.set_style_text_color(lv.color_hex(0x888888), 0)
        
        # 화면 로드
        lv.screen_load(scr)
        
        # 현재 선택된 버튼 인덱스
        current_button = 0
        
        # 버튼 상태 추적
        last_button_states = {'select': False, 'up': False, 'down': False, 'menu': False}
        
        # 버튼 눌림 효과 변수
        button_press_timer = 0
        button_pressed = False
        
        # 버튼 시각적 피드백 함수
        def update_button_selection():
            nonlocal current_button
            # 모든 버튼을 기본 색상으로 리셋
            for btn in buttons:
                btn.set_style_bg_color(lv.color_hex(0x0066CC), 0)
                btn.set_style_border_width(2, 0)
                btn.set_style_border_color(lv.color_hex(0x004499), 0)
                btn.set_style_shadow_width(3, 0)
                btn.set_style_shadow_ofs_x(1, 0)
                btn.set_style_shadow_ofs_y(1, 0)
            
            # 현재 선택된 버튼을 강조
            selected_btn = buttons[current_button]
            selected_btn.set_style_bg_color(lv.color_hex(0x00AA00), 0)  # 초록색으로 강조
            selected_btn.set_style_border_width(3, 0)
            selected_btn.set_style_border_color(lv.color_hex(0xFFFFFF), 0)  # 흰색 테두리
            selected_btn.set_style_shadow_width(5, 0)
            selected_btn.set_style_shadow_ofs_x(2, 0)
            selected_btn.set_style_shadow_ofs_y(2, 0)
            
            # 선택된 버튼 이름 업데이트
            selected_label.set_text(f"Selected: {button_names[current_button]}")
        
        # 초기 선택 상태 설정
        update_button_selection()
        
        print("심볼 버튼 테스트 시작! 물리 버튼으로 버튼을 선택하고 클릭하세요.")
        
        # 이벤트 루프 시작
        try:
            event_loop = lv_utils.event_loop(freq=25)
        except RuntimeError as e:
            if "already running" in str(e):
                event_loop = None
        
        while True:
            try:
                # 버튼 상태 읽기
                button_states = button_interface.get_all_button_states()
                select_pressed = button_states.get('select', 1) == 0
                up_pressed = button_states.get('up', 1) == 0
                down_pressed = button_states.get('down', 1) == 0
                menu_pressed = button_states.get('menu', 1) == 0
                
                # 버튼 0 (Select) - 선택된 버튼 클릭
                if select_pressed and not last_button_states['select']:
                    # 버튼 눌림 효과 시작
                    button_pressed = True
                    button_press_timer = 0
                    buttons[current_button].set_style_bg_color(lv.color_hex(0xFF0000), 0)  # 빨간색으로 눌림 효과
                    buttons[current_button].set_style_shadow_width(0, 0)  # 그림자 제거
                    buttons[current_button].set_style_border_color(lv.color_hex(0xCC0000), 0)  # 어두운 빨간색 테두리
                    print(f"버튼 클릭: {button_names[current_button]}")
                
                # 버튼 1 (Left) - 왼쪽 버튼으로 이동
                if up_pressed and not last_button_states['up']:
                    if current_button == 0:
                        current_button = 1  # 왼쪽 위에서 오른쪽 위로
                    elif current_button == 1:
                        current_button = 0  # 오른쪽 위에서 왼쪽 위로
                    elif current_button == 2:
                        current_button = 3  # 왼쪽 아래에서 오른쪽 아래로
                    elif current_button == 3:
                        current_button = 2  # 오른쪽 아래에서 왼쪽 아래로
                    
                    update_button_selection()
                    print(f"왼쪽 이동: {button_names[current_button]}")
                
                # 버튼 2 (Right) - 오른쪽 버튼으로 이동
                if down_pressed and not last_button_states['down']:
                    if current_button == 0:
                        current_button = 1  # 왼쪽 위에서 오른쪽 위로
                    elif current_button == 1:
                        current_button = 0  # 오른쪽 위에서 왼쪽 위로
                    elif current_button == 2:
                        current_button = 3  # 왼쪽 아래에서 오른쪽 아래로
                    elif current_button == 3:
                        current_button = 2  # 오른쪽 아래에서 왼쪽 아래로
                    
                    update_button_selection()
                    print(f"오른쪽 이동: {button_names[current_button]}")
                
                # 버튼 3 (Cancel) - 테스트 종료
                if menu_pressed and not last_button_states['menu']:
                    print("심볼 버튼 테스트 종료")
                    break
                
                # 버튼 눌림 효과 처리
                if button_pressed:
                    button_press_timer += 1
                    if button_press_timer >= 3:  # 150ms 후 복원 (50ms * 3)
                        update_button_selection()
                        button_pressed = False
                        button_press_timer = 0
                
                last_button_states = {'select': select_pressed, 'up': up_pressed, 'down': down_pressed, 'menu': menu_pressed}
                time.sleep_ms(50)
                
            except KeyboardInterrupt:
                print("\n심볼 버튼 테스트 중단됨")
                break
            
    except Exception as e:
        print(f"❌ LVGL 심볼 버튼 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_lvgl_slider():
    """LVGL 슬라이더 테스트 (용량 설정용)"""
    print("=" * 60)
    print("LVGL 슬라이더 테스트")
    print("=" * 60)
    print("버튼 매핑:")
    print("  버튼 0 (Select): 선택/확인")
    print("  버튼 1 (Left): 값 감소")
    print("  버튼 2 (Right): 값 증가")
    print("  버튼 3 (Cancel): 테스트 종료")
    print("=" * 60)
    
    try:
        # 버튼 인터페이스 초기화
        import sys
        sys.path.append('src')
        from button_interface import ButtonInterface
        button_interface = ButtonInterface()
        
        # LVGL 초기화
        lv.init()
        
        # 디스플레이 초기화 (메모리 절약을 위해 기존 디스플레이 재사용)
        if current_display is None:
            set_st7735_offset(1, 2)
            init_display()
        
        if current_display:
            current_display.set_backlight(100)
        
        # 화면 생성
        scr = lv.obj()
        scr.set_style_bg_color(lv.color_hex(0x000000), 0)
        
        # 제목 라벨
        title_label = lv.label(scr)
        title_label.set_text("Slider Test")
        title_label.align(lv.ALIGN.TOP_MID, 0, 5)
        title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 슬라이더 생성
        slider = lv.slider(scr)
        slider.set_size(100, 10)
        slider.align(lv.ALIGN.CENTER, 0, -20)
        slider.set_range(0, 100)
        slider.set_value(50, 0)
        slider.set_style_bg_color(lv.color_hex(0x333333), lv.PART.MAIN)
        slider.set_style_bg_color(lv.color_hex(0x0066CC), lv.PART.INDICATOR)
        slider.set_style_bg_color(lv.color_hex(0xFFFFFF), lv.PART.KNOB)
        
        # 값 표시 라벨
        value_label = lv.label(scr)
        value_label.set_text("Value: 50")
        value_label.align(lv.ALIGN.CENTER, 0, 10)
        value_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 설명 라벨
        desc_label = lv.label(scr)
        desc_label.set_text("0:Select 1:Left 2:Right 3:Cancel")
        desc_label.align(lv.ALIGN.BOTTOM_MID, 0, -10)
        desc_label.set_style_text_color(lv.color_hex(0x888888), 0)
        
        # 화면 로드
        lv.screen_load(scr)
        
        # 버튼 상태 추적
        last_button_states = {'select': False, 'up': False, 'down': False, 'menu': False}
        
        # 이벤트 루프 시작
        try:
            event_loop = lv_utils.event_loop(freq=25)
        except RuntimeError as e:
            if "already running" in str(e):
                event_loop = None
        
        print("슬라이더 테스트 시작! 1:감소, 2:증가, 0:선택, 3:취소")
        
        while True:
            try:
                button_states = button_interface.get_all_button_states()
                select_pressed = button_states.get('select', 1) == 0
                up_pressed = button_states.get('up', 1) == 0
                down_pressed = button_states.get('down', 1) == 0
                menu_pressed = button_states.get('menu', 1) == 0
                
                # 버튼 0 (Select) - 선택/확인
                if select_pressed and not last_button_states['select']:
                    current_value = slider.get_value()
                    print(f"슬라이더 값 선택: {current_value}")
                
                # 버튼 1 (Left) - 값 감소
                if down_pressed and not last_button_states['down']:
                    current_value = slider.get_value()
                    new_value = max(0, current_value - 10)
                    slider.set_value(new_value, 0)
                    value_label.set_text(f"Value: {new_value}")
                    print(f"슬라이더 값 감소: {new_value}")
                
                # 버튼 2 (Right) - 값 증가
                if menu_pressed and not last_button_states['menu']:
                    current_value = slider.get_value()
                    new_value = min(100, current_value + 10)
                    slider.set_value(new_value, 0)
                    value_label.set_text(f"Value: {new_value}")
                    print(f"슬라이더 값 증가: {new_value}")
                
                # 버튼 3 (Cancel) - 테스트 종료
                if up_pressed and not last_button_states['up']:
                    print("슬라이더 테스트 종료")
                    break
                
                last_button_states = {'select': select_pressed, 'up': up_pressed, 'down': down_pressed, 'menu': menu_pressed}
                time.sleep_ms(50)
                
            except KeyboardInterrupt:
                print("\n슬라이더 테스트 중단됨")
                break
            
    except Exception as e:
        print(f"❌ LVGL 슬라이더 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_lvgl_dropdown():
    """LVGL 드롭다운 테스트 (시간/날짜 선택용)"""
    print("=" * 60)
    print("LVGL 드롭다운 테스트")
    print("=" * 60)
    print("버튼 매핑:")
    print("  버튼 0 (Select): 선택/확인")
    print("  버튼 1 (Left): 이전 옵션")
    print("  버튼 2 (Right): 다음 옵션")
    print("  버튼 3 (Cancel): 테스트 종료")
    print("=" * 60)
    
    try:
        # 버튼 인터페이스 초기화
        import sys
        sys.path.append('src')
        from button_interface import ButtonInterface
        button_interface = ButtonInterface()
        
        # LVGL 초기화
        lv.init()
        
        # 디스플레이 초기화 (메모리 절약을 위해 기존 디스플레이 재사용)
        if current_display is None:
            set_st7735_offset(1, 2)
            init_display()
        
        if current_display:
            current_display.set_backlight(100)
        
        # 화면 생성
        scr = lv.obj()
        scr.set_style_bg_color(lv.color_hex(0x000000), 0)
        
        # 제목 라벨
        title_label = lv.label(scr)
        title_label.set_text("Dropdown Test")
        title_label.align(lv.ALIGN.TOP_MID, 0, 5)
        title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 드롭다운 옵션 배열
        dropdown_options = [
            "6:00 AM", "7:00 AM", "8:00 AM", "9:00 AM", "10:00 AM",
            "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM"
        ]
        
        # 현재 선택된 인덱스
        current_selection = 0
        
        # 드롭다운 생성
        dropdown = lv.dropdown(scr)
        dropdown.set_options("\n".join(dropdown_options))
        dropdown.align(lv.ALIGN.CENTER, 0, -20)
        dropdown.set_size(100, 30)
        dropdown.set_style_bg_color(lv.color_hex(0x333333), 0)
        dropdown.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 선택된 값 표시 라벨
        selected_label = lv.label(scr)
        selected_label.set_text(f"Selected: {dropdown_options[current_selection]}")
        selected_label.align(lv.ALIGN.CENTER, 0, 20)
        selected_label.set_style_text_color(lv.color_hex(0x00FF00), 0)
        
        # 현재 선택된 옵션 강조 표시
        highlight_label = lv.label(scr)
        highlight_label.set_text(f"Current: {dropdown_options[current_selection]}")
        highlight_label.align(lv.ALIGN.CENTER, 0, 40)
        highlight_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 설명 라벨
        desc_label = lv.label(scr)
        desc_label.set_text("0:Select 1:Left 2:Right 3:Cancel")
        desc_label.align(lv.ALIGN.BOTTOM_MID, 0, -10)
        desc_label.set_style_text_color(lv.color_hex(0x888888), 0)
        
        # 화면 로드
        lv.screen_load(scr)
        
        # 버튼 상태 추적
        last_button_states = {'select': False, 'up': False, 'down': False, 'menu': False}
        
        # 이벤트 루프 시작
        try:
            event_loop = lv_utils.event_loop(freq=25)
        except RuntimeError as e:
            if "already running" in str(e):
                event_loop = None
        
        print("드롭다운 테스트 시작! 1:이전, 2:다음, 0:선택, 3:취소")
        
        while True:
            try:
                button_states = button_interface.get_all_button_states()
                select_pressed = button_states.get('select', 1) == 0
                up_pressed = button_states.get('up', 1) == 0
                down_pressed = button_states.get('down', 1) == 0
                menu_pressed = button_states.get('menu', 1) == 0
                
                # 버튼 0 (Select) - 현재 선택된 옵션 확정
                if select_pressed and not last_button_states['select']:
                    # 드롭다운에 선택된 값 설정
                    dropdown.set_selected(current_selection)
                    selected_label.set_text(f"Selected: {dropdown_options[current_selection]}")
                    print(f"드롭다운 선택 확정: {dropdown_options[current_selection]}")
                
                # 버튼 1 (Left) - 이전 옵션으로 이동
                if down_pressed and not last_button_states['down']:
                    current_selection = (current_selection - 1) % len(dropdown_options)
                    highlight_label.set_text(f"Current: {dropdown_options[current_selection]}")
                    print(f"옵션 이동 (이전): {dropdown_options[current_selection]}")
                
                # 버튼 2 (Right) - 다음 옵션으로 이동
                if menu_pressed and not last_button_states['menu']:
                    current_selection = (current_selection + 1) % len(dropdown_options)
                    highlight_label.set_text(f"Current: {dropdown_options[current_selection]}")
                    print(f"옵션 이동 (다음): {dropdown_options[current_selection]}")
                
                # 버튼 3 (Cancel) - 테스트 종료
                if up_pressed and not last_button_states['up']:
                    print("드롭다운 테스트 종료")
                    break
                
                last_button_states = {'select': select_pressed, 'up': up_pressed, 'down': down_pressed, 'menu': menu_pressed}
                time.sleep_ms(50)
                
            except KeyboardInterrupt:
                print("\n드롭다운 테스트 중단됨")
                break
            
    except Exception as e:
        print(f"❌ LVGL 드롭다운 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_lvgl_checkbox():
    """LVGL 체크박스 테스트 (알림 설정용)"""
    print("=" * 60)
    print("LVGL 체크박스 테스트")
    print("=" * 60)
    print("버튼 매핑:")
    print("  버튼 0 (Select): 체크박스 토글")
    print("  버튼 1 (Left): 위로 이동")
    print("  버튼 2 (Right): 아래로 이동")
    print("  버튼 3 (Cancel): 테스트 종료")
    print("=" * 60)
    
    try:
        # 버튼 인터페이스 초기화
        import sys
        sys.path.append('src')
        from button_interface import ButtonInterface
        button_interface = ButtonInterface()
        
        # LVGL 초기화
        lv.init()
        
        # 디스플레이 초기화 (메모리 절약을 위해 기존 디스플레이 재사용)
        if current_display is None:
            set_st7735_offset(1, 2)
            init_display()
        
        if current_display:
            current_display.set_backlight(100)
        
        # 화면 생성
        scr = lv.obj()
        scr.set_style_bg_color(lv.color_hex(0x000000), 0)
        
        # 제목 라벨
        title_label = lv.label(scr)
        title_label.set_text("Checkbox Test")
        title_label.align(lv.ALIGN.TOP_MID, 0, 5)
        title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 체크박스들 생성
        cb1 = lv.checkbox(scr)
        cb1.set_text("Enable Alert")
        cb1.align(lv.ALIGN.CENTER, 0, -30)
        cb1.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        cb2 = lv.checkbox(scr)
        cb2.set_text("Sound Alert")
        cb2.align(lv.ALIGN.CENTER, 0, -10)
        cb2.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        cb3 = lv.checkbox(scr)
        cb3.set_text("Vibration Alert")
        cb3.align(lv.ALIGN.CENTER, 0, 10)
        cb3.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 현재 선택된 체크박스 표시 라벨
        current_label = lv.label(scr)
        current_label.set_text("Current: Enable Alert")
        current_label.align(lv.ALIGN.CENTER, 0, 30)
        current_label.set_style_text_color(lv.color_hex(0x00FF00), 0)
        
        # 상태 표시 라벨
        status_label = lv.label(scr)
        status_label.set_text("Status: ☐ ☐ ☐")
        status_label.align(lv.ALIGN.CENTER, 0, 50)
        status_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 설명 라벨
        desc_label = lv.label(scr)
        desc_label.set_text("0:Toggle 1:Up 2:Down 3:Cancel")
        desc_label.align(lv.ALIGN.BOTTOM_MID, 0, -10)
        desc_label.set_style_text_color(lv.color_hex(0x888888), 0)
        
        # 화면 로드
        lv.screen_load(scr)
        
        # 현재 선택된 체크박스 인덱스
        current_cb = 0
        checkboxes = [cb1, cb2, cb3]
        checkbox_names = ["Enable Alert", "Sound Alert", "Vibration Alert"]
        
        # 버튼 상태 추적
        last_button_states = {'select': False, 'up': False, 'down': False, 'menu': False}
        
        # 이벤트 루프 시작
        try:
            event_loop = lv_utils.event_loop(freq=25)
        except RuntimeError as e:
            if "already running" in str(e):
                event_loop = None
        
        print("체크박스 테스트 시작! 1:위, 2:아래, 0:토글, 3:취소")
        
        while True:
            try:
                button_states = button_interface.get_all_button_states()
                select_pressed = button_states.get('select', 1) == 0
                up_pressed = button_states.get('up', 1) == 0
                down_pressed = button_states.get('down', 1) == 0
                menu_pressed = button_states.get('menu', 1) == 0
                
                # 버튼 0 (Select) - 체크박스 토글
                if select_pressed and not last_button_states['select']:
                    current_checkbox = checkboxes[current_cb]
                    # 올바른 API 사용
                    current_state = current_checkbox.get_state()
                    if current_state & lv.STATE.CHECKED:
                        # 체크 해제
                        current_checkbox.set_state(lv.STATE.CHECKED, False)
                    else:
                        # 체크 설정
                        current_checkbox.set_state(lv.STATE.CHECKED, True)
                    
                    # 상태 업데이트
                    states = []
                    for cb in checkboxes:
                        states.append("✓" if cb.get_state() & lv.STATE.CHECKED else "☐")
                    status_label.set_text(f"Status: {states[0]} {states[1]} {states[2]}")
                    print(f"체크박스 {current_cb + 1} ({checkbox_names[current_cb]}) 토글")
                
                # 버튼 1 (Left) - 위로 이동
                if down_pressed and not last_button_states['down']:
                    current_cb = (current_cb - 1) % len(checkboxes)
                    current_label.set_text(f"Current: {checkbox_names[current_cb]}")
                    print(f"체크박스 이동 (위): {checkbox_names[current_cb]}")
                
                # 버튼 2 (Right) - 아래로 이동
                if menu_pressed and not last_button_states['menu']:
                    current_cb = (current_cb + 1) % len(checkboxes)
                    current_label.set_text(f"Current: {checkbox_names[current_cb]}")
                    print(f"체크박스 이동 (아래): {checkbox_names[current_cb]}")
                
                # 버튼 3 (Cancel) - 테스트 종료
                if up_pressed and not last_button_states['up']:
                    print("체크박스 테스트 종료")
                    break
                
                last_button_states = {'select': select_pressed, 'up': up_pressed, 'down': down_pressed, 'menu': menu_pressed}
                time.sleep_ms(50)
                
            except KeyboardInterrupt:
                print("\n체크박스 테스트 중단됨")
                break
            
    except Exception as e:
        print(f"❌ LVGL 체크박스 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_lvgl_spinner():
    """LVGL 스피너 테스트 (로딩 표시용)"""
    print("=" * 60)
    print("LVGL 스피너 테스트")
    print("=" * 60)
    print("버튼 매핑:")
    print("  버튼 0 (Select): 스피너 시작/중지")
    print("  버튼 1 (Left): 회전 방향 왼쪽")
    print("  버튼 2 (Right): 회전 방향 오른쪽")
    print("  버튼 3 (Cancel): 테스트 종료")
    print("=" * 60)
    
    try:
        # 버튼 인터페이스 초기화
        import sys
        sys.path.append('src')
        from button_interface import ButtonInterface
        button_interface = ButtonInterface()
        
        # LVGL 초기화
        lv.init()
        
        # 디스플레이 초기화 (메모리 절약을 위해 기존 디스플레이 재사용)
        if current_display is None:
            set_st7735_offset(1, 2)
            init_display()
        
        if current_display:
            current_display.set_backlight(100)
        
        # 화면 생성
        scr = lv.obj()
        scr.set_style_bg_color(lv.color_hex(0x000000), 0)
        
        # 제목 라벨
        title_label = lv.label(scr)
        title_label.set_text("Spinner Test")
        title_label.align(lv.ALIGN.TOP_MID, 0, 5)
        title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 스피너 생성
        spinner = lv.spinner(scr)
        spinner.set_size(40, 40)
        spinner.align(lv.ALIGN.CENTER, 0, -20)
        spinner.set_style_arc_color(lv.color_hex(0x0066CC), lv.PART.INDICATOR)
        spinner.set_style_arc_width(4, lv.PART.INDICATOR)
        
        # 상태 라벨
        status_label = lv.label(scr)
        status_label.set_text("Loading...")
        status_label.align(lv.ALIGN.CENTER, 0, 20)
        status_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 설명 라벨
        desc_label = lv.label(scr)
        desc_label.set_text("0:Start/Stop 3:Cancel")
        desc_label.align(lv.ALIGN.BOTTOM_MID, 0, -10)
        desc_label.set_style_text_color(lv.color_hex(0x888888), 0)
        
        # 화면 로드
        lv.screen_load(scr)
        
        # 스피너 상태
        spinner_running = True
        spinner_direction = 1  # 1: 시계방향, -1: 반시계방향
        
        # 버튼 상태 추적
        last_button_states = {'select': False, 'up': False, 'down': False, 'menu': False}
        
        # 이벤트 루프 시작
        try:
            event_loop = lv_utils.event_loop(freq=25)
        except RuntimeError as e:
            if "already running" in str(e):
                event_loop = None
        
        print("스피너 테스트 시작! 0:시작/중지, 1:왼쪽, 2:오른쪽, 3:취소")
        
        while True:
            try:
                button_states = button_interface.get_all_button_states()
                select_pressed = button_states.get('select', 1) == 0
                up_pressed = button_states.get('up', 1) == 0
                down_pressed = button_states.get('down', 1) == 0
                menu_pressed = button_states.get('menu', 1) == 0
                
                # 버튼 0 (Select) - 스피너 시작/중지
                if select_pressed and not last_button_states['select']:
                    if spinner_running:
                        # 스피너 중지 (색상 변경으로 표시)
                        spinner.set_style_arc_color(lv.color_hex(0x666666), lv.PART.INDICATOR)
                        status_label.set_text("Spinner Stopped")
                        print("스피너 중지")
                    else:
                        # 스피너 시작 (색상 복원)
                        spinner.set_style_arc_color(lv.color_hex(0x0066CC), lv.PART.INDICATOR)
                        status_label.set_text("Loading...")
                        print("스피너 시작")
                    
                    spinner_running = not spinner_running
                
                # 버튼 1 (Left) - 회전 방향 왼쪽 (반시계방향)
                if up_pressed and not last_button_states['up']:
                    spinner_direction = -1
                    spinner.set_style_arc_color(lv.color_hex(0x00CC00), lv.PART.INDICATOR)  # 초록색
                    print("회전 방향: 왼쪽 (반시계방향)")
                
                # 버튼 2 (Right) - 회전 방향 오른쪽 (시계방향)
                if down_pressed and not last_button_states['down']:
                    spinner_direction = 1
                    spinner.set_style_arc_color(lv.color_hex(0x0066CC), lv.PART.INDICATOR)  # 파란색
                    print("회전 방향: 오른쪽 (시계방향)")
                
                # 버튼 3 (Cancel) - 테스트 종료
                if menu_pressed and not last_button_states['menu']:
                    print("스피너 테스트 종료")
                    break
                
                last_button_states = {'select': select_pressed, 'up': up_pressed, 'down': down_pressed, 'menu': menu_pressed}
                time.sleep_ms(50)
                
            except KeyboardInterrupt:
                print("\n스피너 테스트 중단됨")
                break
            
    except Exception as e:
        print(f"❌ LVGL 스피너 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_lvgl_bar():
    """LVGL 바 테스트 (진행률 표시용)"""
    print("=" * 60)
    print("LVGL 바 테스트")
    print("=" * 60)
    print("버튼 매핑:")
    print("  버튼 0 (Select): 값 선택")
    print("  버튼 1 (Left): 진행률 감소")
    print("  버튼 2 (Right): 진행률 증가")
    print("  버튼 3 (Cancel): 테스트 종료")
    print("=" * 60)
    
    try:
        # 버튼 인터페이스 초기화
        import sys
        sys.path.append('src')
        from button_interface import ButtonInterface
        button_interface = ButtonInterface()
        
        # LVGL 초기화
        lv.init()
        
        # 디스플레이 초기화 (메모리 절약을 위해 기존 디스플레이 재사용)
        if current_display is None:
            set_st7735_offset(1, 2)
            init_display()
        
        if current_display:
            current_display.set_backlight(100)
        
        # 화면 생성
        scr = lv.obj()
        scr.set_style_bg_color(lv.color_hex(0x000000), 0)
        
        # 제목 라벨
        title_label = lv.label(scr)
        title_label.set_text("Bar Test")
        title_label.align(lv.ALIGN.TOP_MID, 0, 5)
        title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 바 생성
        bar = lv.bar(scr)
        bar.set_size(100, 20)
        bar.align(lv.ALIGN.CENTER, 0, -20)
        bar.set_range(0, 100)
        bar.set_value(50, 0)
        bar.set_style_bg_color(lv.color_hex(0x333333), lv.PART.MAIN)
        bar.set_style_bg_color(lv.color_hex(0x00CC00), lv.PART.INDICATOR)
        
        # 값 표시 라벨
        value_label = lv.label(scr)
        value_label.set_text("Progress: 50%")
        value_label.align(lv.ALIGN.CENTER, 0, 10)
        value_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 설명 라벨
        desc_label = lv.label(scr)
        desc_label.set_text("Select: +, Menu: -")
        desc_label.align(lv.ALIGN.BOTTOM_MID, 0, -10)
        desc_label.set_style_text_color(lv.color_hex(0x888888), 0)
        
        # 화면 로드
        lv.screen_load(scr)
        
        # 버튼 상태 추적
        last_button_states = {'select': False, 'menu': False}
        
        # 이벤트 루프 시작
        try:
            event_loop = lv_utils.event_loop(freq=25)
        except RuntimeError as e:
            if "already running" in str(e):
                event_loop = None
        
        print("바 테스트 시작! Select: 증가, Menu: 감소")
        
        while True:
            try:
                button_states = button_interface.get_all_button_states()
                select_pressed = button_states.get('select', 1) == 0
                up_pressed = button_states.get('up', 1) == 0
                down_pressed = button_states.get('down', 1) == 0
                menu_pressed = button_states.get('menu', 1) == 0
                
                # 버튼 0 (Select) - 진행률 증가
                if select_pressed and not last_button_states['select']:
                    current_value = bar.get_value()
                    new_value = min(100, current_value + 10)
                    bar.set_value(new_value, 0)
                    value_label.set_text(f"Progress: {new_value}%")
                    print(f"바 값 증가: {new_value}%")
                
                # 버튼 1 (Left) - 진행률 감소
                if up_pressed and not last_button_states['up']:
                    current_value = bar.get_value()
                    new_value = max(0, current_value - 10)
                    bar.set_value(new_value, 0)
                    value_label.set_text(f"Progress: {new_value}%")
                    print(f"바 값 감소: {new_value}%")
                
                # 버튼 2 (Right) - 진행률 증가
                if down_pressed and not last_button_states['down']:
                    current_value = bar.get_value()
                    new_value = min(100, current_value + 10)
                    bar.set_value(new_value, 0)
                    value_label.set_text(f"Progress: {new_value}%")
                    print(f"바 값 증가: {new_value}%")
                
                # 버튼 3 (Cancel) - 테스트 종료
                if menu_pressed and not last_button_states['menu']:
                    print("바 테스트 종료")
                    break
                
                last_button_states = {'select': select_pressed, 'up': up_pressed, 'down': down_pressed, 'menu': menu_pressed}
                time.sleep_ms(50)
                
            except KeyboardInterrupt:
                print("\n바 테스트 중단됨")
                break
            
    except Exception as e:
        print(f"❌ LVGL 바 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_lvgl_arc():
    """LVGL 아크 테스트 (원형 진행률용)"""
    print("=" * 60)
    print("LVGL 아크 테스트")
    print("=" * 60)
    print("버튼 매핑:")
    print("  버튼 0 (Select): 값 선택")
    print("  버튼 1 (Left): 진행률 감소")
    print("  버튼 2 (Right): 진행률 증가")
    print("  버튼 3 (Cancel): 테스트 종료")
    print("=" * 60)
    
    try:
        # 버튼 인터페이스 초기화
        import sys
        sys.path.append('src')
        from button_interface import ButtonInterface
        button_interface = ButtonInterface()
        
        # LVGL 초기화
        lv.init()
        
        # 디스플레이 초기화 (메모리 절약을 위해 기존 디스플레이 재사용)
        if current_display is None:
            set_st7735_offset(1, 2)
            init_display()
        
        if current_display:
            current_display.set_backlight(100)
        
        # 화면 생성
        scr = lv.obj()
        scr.set_style_bg_color(lv.color_hex(0x000000), 0)
        
        # 제목 라벨
        title_label = lv.label(scr)
        title_label.set_text("Arc Test")
        title_label.align(lv.ALIGN.TOP_MID, 0, 5)
        title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 아크 생성
        arc = lv.arc(scr)
        arc.set_size(80, 80)
        arc.align(lv.ALIGN.CENTER, 0, -20)
        arc.set_range(0, 100)
        arc.set_value(50)
        arc.set_bg_angles(0, 360)
        arc.set_angles(0, 180)  # 50% = 180도
        arc.set_style_arc_color(lv.color_hex(0x333333), lv.PART.MAIN)
        arc.set_style_arc_color(lv.color_hex(0x0066CC), lv.PART.INDICATOR)
        arc.set_style_arc_width(6, lv.PART.MAIN)
        arc.set_style_arc_width(6, lv.PART.INDICATOR)
        
        # 값 표시 라벨
        value_label = lv.label(scr)
        value_label.set_text("50%")
        value_label.align(lv.ALIGN.CENTER, 0, 40)
        value_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 설명 라벨
        desc_label = lv.label(scr)
        desc_label.set_text("Select: +, Menu: -")
        desc_label.align(lv.ALIGN.BOTTOM_MID, 0, -10)
        desc_label.set_style_text_color(lv.color_hex(0x888888), 0)
        
        # 화면 로드
        lv.screen_load(scr)
        
        # 버튼 상태 추적
        last_button_states = {'select': False, 'menu': False}
        
        # 이벤트 루프 시작
        try:
            event_loop = lv_utils.event_loop(freq=25)
        except RuntimeError as e:
            if "already running" in str(e):
                event_loop = None
        
        print("아크 테스트 시작! 0:선택, 1:감소, 2:증가, 3:취소")
        
        while True:
            try:
                button_states = button_interface.get_all_button_states()
                select_pressed = button_states.get('select', 1) == 0
                up_pressed = button_states.get('up', 1) == 0
                down_pressed = button_states.get('down', 1) == 0
                menu_pressed = button_states.get('menu', 1) == 0
                
                # 버튼 0 (Select) - 값 선택
                if select_pressed and not last_button_states['select']:
                    current_value = arc.get_value()
                    print(f"아크 값 선택: {current_value}%")
                
                # 버튼 1 (Left) - 진행률 감소
                if up_pressed and not last_button_states['up']:
                    current_value = arc.get_value()
                    new_value = max(0, current_value - 10)
                    arc.set_value(new_value)
                    arc.set_angles(0, int(360 * new_value / 100))
                    value_label.set_text(f"{new_value}%")
                    print(f"아크 값 감소: {new_value}%")
                
                # 버튼 2 (Right) - 진행률 증가
                if down_pressed and not last_button_states['down']:
                    current_value = arc.get_value()
                    new_value = min(100, current_value + 10)
                    arc.set_value(new_value)
                    arc.set_angles(0, int(360 * new_value / 100))
                    value_label.set_text(f"{new_value}%")
                    print(f"아크 값 증가: {new_value}%")
                
                # 버튼 3 (Cancel) - 테스트 종료
                if menu_pressed and not last_button_states['menu']:
                    print("아크 테스트 종료")
                    break
                
                last_button_states = {'select': select_pressed, 'up': up_pressed, 'down': down_pressed, 'menu': menu_pressed}
                time.sleep_ms(50)
                
            except KeyboardInterrupt:
                print("\n아크 테스트 중단됨")
                break
            
    except Exception as e:
        print(f"❌ LVGL 아크 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_lvgl_list():
    """LVGL 리스트 테스트 (메뉴용)"""
    print("=" * 60)
    print("LVGL 리스트 테스트")
    print("=" * 60)
    print("버튼 매핑:")
    print("  버튼 0 (Select): 항목 선택")
    print("  버튼 1 (Up): 위로 이동")
    print("  버튼 2 (Down): 아래로 이동")
    print("  버튼 3 (Cancel): 테스트 종료")
    print("=" * 60)
    
    try:
        # 버튼 인터페이스 초기화
        import sys
        sys.path.append('src')
        from button_interface import ButtonInterface
        button_interface = ButtonInterface()
        
        # LVGL 초기화
        lv.init()
        
        # 디스플레이 초기화 (메모리 절약을 위해 기존 디스플레이 재사용)
        if current_display is None:
            set_st7735_offset(1, 2)
            init_display()
        
        if current_display:
            current_display.set_backlight(100)
        
        # 화면 생성
        scr = lv.obj()
        scr.set_style_bg_color(lv.color_hex(0x000000), 0)
        
        # 제목 라벨
        title_label = lv.label(scr)
        title_label.set_text("List Test")
        title_label.align(lv.ALIGN.TOP_MID, 0, 5)
        title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 리스트 생성
        list_obj = lv.list(scr)
        list_obj.set_size(120, 100)
        list_obj.align(lv.ALIGN.CENTER, 0, -10)
        list_obj.set_style_bg_color(lv.color_hex(0x222222), 0)
        
        # 리스트 항목들 추가 (사용 가능한 심볼만 사용)
        btn1 = list_obj.add_button(lv.SYMBOL.HOME, "Home")
        btn2 = list_obj.add_button(lv.SYMBOL.SETTINGS, "Settings")
        btn3 = list_obj.add_button(lv.SYMBOL.REFRESH, "Refresh")
        btn4 = list_obj.add_button(lv.SYMBOL.POWER, "Power")
        btn5 = list_obj.add_button("?", "Help")
        
        # 선택된 항목 표시 라벨
        selected_label = lv.label(scr)
        selected_label.set_text("Selected: Home")
        selected_label.align(lv.ALIGN.CENTER, 0, 60)
        selected_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 설명 라벨
        desc_label = lv.label(scr)
        desc_label.set_text("Up/Down: Move, Select: Choose")
        desc_label.align(lv.ALIGN.BOTTOM_MID, 0, -10)
        desc_label.set_style_text_color(lv.color_hex(0x888888), 0)
        
        # 화면 로드
        lv.screen_load(scr)
        
        # 현재 선택된 항목 인덱스
        current_item = 0
        items = ["Home", "Settings", "Refresh", "Power", "Help"]
        
        # 버튼 상태 추적
        last_button_states = {'select': False, 'up': False, 'down': False, 'menu': False}
        
        # 이벤트 루프 시작
        try:
            event_loop = lv_utils.event_loop(freq=25)
        except RuntimeError as e:
            if "already running" in str(e):
                event_loop = None
        
        print("리스트 테스트 시작! 0:선택, 1:위, 2:아래, 3:취소")
        
        while True:
            try:
                button_states = button_interface.get_all_button_states()
                select_pressed = button_states.get('select', 1) == 0
                up_pressed = button_states.get('up', 1) == 0
                down_pressed = button_states.get('down', 1) == 0
                menu_pressed = button_states.get('menu', 1) == 0
                
                # 버튼 0 (Select) - 항목 선택
                if select_pressed and not last_button_states['select']:
                    selected_label.set_text(f"Selected: {items[current_item]}")
                    print(f"리스트 항목 선택: {items[current_item]}")
                
                # 버튼 1 (Up) - 위로 이동
                if up_pressed and not last_button_states['up']:
                    current_item = (current_item - 1) % len(items)
                    # focus_obj 대신 시각적 피드백으로 선택 표시
                    selected_label.set_text(f"Current: {items[current_item]}")
                    print(f"리스트 위로 이동: {items[current_item]}")
                
                # 버튼 2 (Down) - 아래로 이동
                if down_pressed and not last_button_states['down']:
                    current_item = (current_item + 1) % len(items)
                    # focus_obj 대신 시각적 피드백으로 선택 표시
                    selected_label.set_text(f"Current: {items[current_item]}")
                    print(f"리스트 아래로 이동: {items[current_item]}")
                
                # 버튼 3 (Cancel) - 테스트 종료
                if menu_pressed and not last_button_states['menu']:
                    print("리스트 테스트 종료")
                    break
                
                last_button_states = {'select': select_pressed, 'up': up_pressed, 'down': down_pressed, 'menu': menu_pressed}
                time.sleep_ms(50)
                
            except KeyboardInterrupt:
                print("\n리스트 테스트 중단됨")
                break
            
    except Exception as e:
        print(f"❌ LVGL 리스트 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_lvgl_msgbox():
    """LVGL 메시지박스 테스트 (확인/경고용)"""
    print("=" * 60)
    print("LVGL 메시지박스 테스트")
    print("=" * 60)
    print("버튼 매핑:")
    print("  버튼 0 (Select): 확인")
    print("  버튼 1 (Left): 취소")
    print("  버튼 2 (Right): 확인")
    print("  버튼 3 (Cancel): 테스트 종료")
    print("=" * 60)
    
    try:
        # 버튼 인터페이스 초기화
        import sys
        sys.path.append('src')
        from button_interface import ButtonInterface
        button_interface = ButtonInterface()
        
        # LVGL 초기화
        lv.init()
        
        # 디스플레이 초기화 (메모리 절약을 위해 기존 디스플레이 재사용)
        if current_display is None:
            set_st7735_offset(1, 2)
            init_display()
        
        if current_display:
            current_display.set_backlight(100)
        
        # 화면 생성
        scr = lv.obj()
        scr.set_style_bg_color(lv.color_hex(0x000000), 0)
        
        # 제목 라벨
        title_label = lv.label(scr)
        title_label.set_text("MessageBox Test")
        title_label.align(lv.ALIGN.TOP_MID, 0, 5)
        title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 메시지박스 생성 (간단한 버전)
        mbox = lv.obj(scr)
        mbox.set_size(140, 80)
        mbox.align(lv.ALIGN.CENTER, 0, 0)
        mbox.set_style_bg_color(lv.color_hex(0x333333), 0)
        mbox.set_style_border_width(2, 0)
        mbox.set_style_border_color(lv.color_hex(0x666666), 0)
        
        # 메시지 텍스트
        msg_text = lv.label(mbox)
        msg_text.set_text("Did you take\nthe pill?")
        msg_text.align(lv.ALIGN.CENTER, 0, -10)
        msg_text.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 버튼들
        yes_btn = lv.button(mbox)
        yes_btn.set_size(50, 25)
        yes_btn.align(lv.ALIGN.BOTTOM_LEFT, 10, -10)
        yes_btn.set_style_bg_color(lv.color_hex(0x00CC00), 0)
        
        yes_label = lv.label(yes_btn)
        yes_label.set_text("Yes")
        yes_label.center()
        yes_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        no_btn = lv.button(mbox)
        no_btn.set_size(50, 25)
        no_btn.align(lv.ALIGN.BOTTOM_RIGHT, -10, -10)
        no_btn.set_style_bg_color(lv.color_hex(0xCC0000), 0)
        
        no_label = lv.label(no_btn)
        no_label.set_text("No")
        no_label.center()
        no_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 상태 표시 라벨
        status_label = lv.label(scr)
        status_label.set_text("MessageBox displayed")
        status_label.align(lv.ALIGN.CENTER, 0, 50)
        status_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 설명 라벨
        desc_label = lv.label(scr)
        desc_label.set_text("Select: Confirm/Cancel")
        desc_label.align(lv.ALIGN.BOTTOM_MID, 0, -10)
        desc_label.set_style_text_color(lv.color_hex(0x888888), 0)
        
        # 화면 로드
        lv.screen_load(scr)
        
        # 현재 선택된 버튼 (0: Yes, 1: No)
        current_btn = 0
        
        # 버튼 상태 추적
        last_button_states = {'select': False, 'up': False, 'down': False, 'menu': False}
        
        # 이벤트 루프 시작
        try:
            event_loop = lv_utils.event_loop(freq=25)
        except RuntimeError as e:
            if "already running" in str(e):
                event_loop = None
        
        print("메시지박스 테스트 시작! 0:확인, 1:취소, 2:확인, 3:종료")
        
        while True:
            try:
                button_states = button_interface.get_all_button_states()
                select_pressed = button_states.get('select', 1) == 0
                up_pressed = button_states.get('up', 1) == 0
                down_pressed = button_states.get('down', 1) == 0
                menu_pressed = button_states.get('menu', 1) == 0
                
                # 버튼 0 (Select) - 확인 (Yes)
                if select_pressed and not last_button_states['select']:
                    status_label.set_text("'Yes' button clicked")
                    print("메시지박스 'Yes' 버튼 클릭")
                
                # 버튼 1 (Left) - 취소 (No)
                if up_pressed and not last_button_states['up']:
                    status_label.set_text("'No' button clicked")
                    print("메시지박스 'No' 버튼 클릭")
                
                # 버튼 2 (Right) - 확인 (Yes)
                if down_pressed and not last_button_states['down']:
                    status_label.set_text("'Yes' button clicked")
                    print("메시지박스 'Yes' 버튼 클릭")
                
                # 버튼 3 (Cancel) - 테스트 종료
                if menu_pressed and not last_button_states['menu']:
                    print("메시지박스 테스트 종료")
                    break
                
                last_button_states = {'select': select_pressed, 'up': up_pressed, 'down': down_pressed, 'menu': menu_pressed}
                time.sleep_ms(50)
                
            except KeyboardInterrupt:
                print("\n메시지박스 테스트 중단됨")
                break
            
    except Exception as e:
        print(f"❌ LVGL 메시지박스 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_font_apis():
    """MicroPython LVGL 폰트 API 테스트"""
    print("=" * 60)
    print("MicroPython LVGL 폰트 API 테스트")
    print("=" * 60)
    
    try:
        # 사용 가능한 폰트 관련 API 확인
        print("사용 가능한 폰트 API들:")
        
        # lv 모듈의 속성들 확인
        lv_attrs = [attr for attr in dir(lv) if 'font' in attr.lower()]
        print(f"LVGL 폰트 관련 속성: {lv_attrs}")
        
        # 기본 폰트들 확인
        try:
            default_font = lv.font_default()
            print(f"기본 폰트: {default_font}")
        except:
            print("기본 폰트 정보 없음")
        
        # 폰트 로드 방법들 테스트
        print("\n폰트 로드 방법 테스트:")
        
        # 방법 1: binfont_create
        try:
            font1 = lv.binfont_create("NotoSansKR.bin")
            print(f"binfont_create 결과: {font1} (타입: {type(font1)})")
        except Exception as e:
            print(f"binfont_create 오류: {e}")
        
        # 방법 2: font_load
        try:
            font2 = lv.font_load("NotoSansKR.bin")
            print(f"font_load 결과: {font2} (타입: {type(font2)})")
        except Exception as e:
            print(f"font_load 오류: {e}")
        
        # 방법 3: 다른 가능한 API들
        font_methods = ['font_create', 'load_font', 'create_font', 'font_open']
        for method in font_methods:
            if hasattr(lv, method):
                try:
                    font = getattr(lv, method)("NotoSansKR.bin")
                    print(f"{method} 결과: {font} (타입: {type(font)})")
                except Exception as e:
                    print(f"{method} 오류: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 폰트 API 테스트 실패: {e}")
        return False

def test_korean_font():
    """한글 폰트 테스트"""
    print("=" * 60)
    print("한글 폰트 테스트")
    print("=" * 60)
    
    try:
        # LVGL 초기화
        lv.init()
        
        # 디스플레이 초기화
        set_st7735_offset(1, 2)
        init_display()
        
        # 디스플레이 백라이트 설정
        if current_display:
            current_display.set_backlight(100)
            print("✅ 디스플레이 백라이트 설정 완료")
        
        print("ST7735 LVGL 통합 완료")
        print("LVGL 디스플레이 설정 완료")
        
        # 이벤트 루프 시작
        if not lv_utils.event_loop.is_running():
            event_loop = lv_utils.event_loop()
            print("✅ LVGL 이벤트 루프 시작")
        
        # 화면 생성
        scr = lv.obj()
        scr.set_style_bg_color(lv.color_hex(0x000000), 0)  # 검은 배경
        
        # 한글 폰트 로드 시도
        korean_font = load_korean_font()
        print(f"폰트 객체: {korean_font}")
        print(f"폰트 타입: {type(korean_font)}")
        
        # 제목 라벨
        title_label = lv.label(scr)
        title_label.align(lv.ALIGN.TOP_MID, 0, 5)
        title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        title_label.set_text("Korean Font Test")
        
        # 한글 텍스트 라벨
        korean_label = lv.label(scr)
        korean_label.align(lv.ALIGN.CENTER, 0, -10)
        korean_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        if korean_font:
            # 한글 폰트 적용 (폰트 설정 후 텍스트 설정)
            korean_label.set_style_text_font(korean_font, 0)
            korean_label.set_text("필박스")
            print("✅ 한글 폰트 적용 완료")
        else:
            # 기본 폰트로 한글 시도
            try:
                korean_label.set_text("필박스")
                print("✅ 기본 폰트로 한글 표시 시도")
            except:
                korean_label.set_text("PILLBOX")
                print("❌ 한글 폰트 없음, 영어로 표시")
        
        # 폰트 상태 표시 라벨
        status_label = lv.label(scr)
        status_label.align(lv.ALIGN.CENTER, 0, 20)
        status_label.set_style_text_color(lv.color_hex(0x888888), 0)
        
        if korean_font:
            status_label.set_text("Korean Font: Loaded")
        else:
            status_label.set_text("Korean Font: Not Available")
        
        # 설명 라벨
        desc_label = lv.label(scr)
        desc_label.align(lv.ALIGN.BOTTOM_MID, 0, -10)
        desc_label.set_style_text_color(lv.color_hex(0x666666), 0)
        desc_label.set_text("Press any key to exit")
        
        # 화면 로드
        lv.screen_load(scr)
        
        print("한글 폰트 테스트 완료")
        if korean_font:
            print("화면에 '필박스' 텍스트가 한글 폰트로 표시되어야 합니다.")
        else:
            print("화면에 'PILLBOX' 텍스트가 기본 폰트로 표시되어야 합니다.")
        
        # LVGL 타이머 핸들러 호출 (화면 강제 업데이트)
        for i in range(10):
            lv.timer_handler()
            time.sleep(0.1)
        
        # 5초 대기
        time.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"❌ 한글 폰트 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_korean_text_display():
    """한글 텍스트 출력 테스트 (사용자 제공 코드 기반)"""
    print("=" * 60)
    print("한글 텍스트 출력 테스트")
    print("=" * 60)
    
    try:
        # LVGL 초기화
        lv.init()
        
        # 파일 시스템 드라이버 초기화 (bin 폰트 사용을 위해 필요)
        print("파일 시스템 드라이버 초기화 중...")
        print("LVGL에서 사용 가능한 파일 시스템 관련 함수들 확인 중...")
        
        # LVGL 모듈의 모든 속성 확인
        lv_attrs = [attr for attr in dir(lv) if 'fs' in attr.lower()]
        print(f"LVGL 파일 시스템 관련 속성: {lv_attrs}")
        
        # 실제 LVGL 파일 시스템 함수들 시도
        fs_methods = [
            'fs_init',           # LVGL 파일 시스템 초기화
            'fs_deinit',         # LVGL 파일 시스템 종료
            'fs_get_drv',        # 특정 드라이버 가져오기
            'fs_get_ext',        # 파일 확장자 가져오기
            'fs_get_last',       # 마지막 파일 관련 정보
            'fs_get_letters',    # 드라이브 문자 목록 반환
            'fs_up',             # 상위 디렉터리 이동
            'fs_file_t',         # 파일 객체 타입
            'fs_file_cache_t',   # 파일 캐시 객체
            'fs_dir_t',          # 디렉터리 객체
            'fs_drv_t'           # 파일 시스템 드라이버 객체
        ]
        
        for method in fs_methods:
            if hasattr(lv, method):
                print(f"✅ LVGL에 {method} 함수/클래스 존재")
                try:
                    if method in ['fs_file_t', 'fs_file_cache_t', 'fs_dir_t', 'fs_drv_t']:
                        # 클래스/타입인 경우
                        obj_type = getattr(lv, method)
                        print(f"✅ {method} 타입 확인: {obj_type}")
                    elif method == 'fs_init':
                        # 파일 시스템 초기화
                        result = getattr(lv, method)()
                        print(f"✅ {method} 호출 성공: {result}")
                    elif method == 'fs_get_letters':
                        # 드라이브 문자 목록 가져오기
                        letters = getattr(lv, method)()
                        print(f"✅ {method} 호출 성공: {letters}")
                    else:
                        # 기타 함수들
                        print(f"⚠️ {method} 함수는 매개변수가 필요할 수 있음")
                except Exception as e:
                    print(f"❌ {method} 호출 실패: {e}")
            else:
                print(f"❌ LVGL에 {method} 함수/클래스 없음")
        
        # 파일 시스템 드라이버 실제 설정 시도 (실제 fs_driver.py 구현 기반)
        print("\n파일 시스템 드라이버 실제 설정 시도:")
        try:
            if hasattr(lv, 'fs_drv_t'):
                # 파일 시스템 드라이버 객체 생성
                fs_drv = lv.fs_drv_t()
                print(f"✅ fs_drv_t 객체 생성 성공: {fs_drv}")
                
                # 실제 fs_driver.py 구현 사용
                print("실제 fs_driver.py 구현을 사용하여 드라이버 등록...")
                fs_driver.fs_register(fs_drv, 'S')  # 'S' 드라이버 문자로 등록
                print("✅ 파일 시스템 드라이버 등록 성공")
                    
            else:
                print("❌ fs_drv_t 클래스 없음")
        except Exception as e:
            print(f"❌ 파일 시스템 드라이버 설정 실패: {e}")
        
        # 디스플레이 초기화
        set_st7735_offset(1, 2)
        init_display()
        
        # 디스플레이 백라이트 설정
        if current_display:
            current_display.set_backlight(100)
            print("✅ 디스플레이 백라이트 설정 완료")
        
        print("ST7735 LVGL 통합 완료")
        print("LVGL 디스플레이 설정 완료")
        
        # 이벤트 루프 시작
        if not lv_utils.event_loop.is_running():
            event_loop = lv_utils.event_loop()
            print("✅ LVGL 이벤트 루프 시작")
        
        # 화면 생성
        scr = lv.obj()
        scr.set_style_bg_color(lv.color_hex(0x000000), 0)  # 검은 배경
        
        # NotoSansKR.bin 폰트 로드 시도 (예제 코드 방식)
        print("폰트 로드 시도 중 (메모리 효율적인 순서로)...")
        font = None
        
        # 메모리 효율적인 폰트 파일들 (크기 순서)
        font_files = [
            ("S:font-PHT-en-20.bin", "영어 폰트 (3.7KB)"),
            ("S:font-PHT-cn-20.bin", "중국어 폰트 (2.3KB)"),
            ("S:font-PHT-jp-20.bin", "일본어 폰트 (456B)"),
            ("S:NotoSansKR.bin", "한글 폰트 (346KB - 메모리 부족 가능)")
        ]
        
        for font_path, description in font_files:
            try:
                print(f"  {description} 시도 중...")
                font = lv.binfont_create(font_path)
                print(f"✅ {description} 로드 성공: {font}")
                print(f"폰트 타입: {type(font)}")
                break
            except MemoryError as e:
                print(f"❌ {description} 메모리 부족: {e}")
                print(f"   파일이 너무 큽니다. 다음 폰트를 시도합니다.")
                continue
            except Exception as e:
                print(f"❌ {description} 로드 실패: {e}")
                continue
        
        if font is None:
            print("❌ 모든 폰트 로드 실패, 기본 폰트 사용")
        
        # 라벨 생성 및 한글 텍스트 설정
        label = lv.label(scr)
        label.set_text("안녕하세요, LVGL!")
        print("✅ 한글 텍스트 설정 완료")
        
        # 폰트 적용 (폰트가 로드된 경우에만)
        if font:
            label.set_style_text_font(font, 0)
            print("✅ 한글 폰트 적용 완료")
        else:
            print("❌ 폰트 없음, 기본 폰트 사용")
            # 기본 폰트로도 한글 시도
            try:
                label.set_text("안녕하세요, LVGL!")
                print("✅ 기본 폰트로 한글 표시 시도")
            except:
                label.set_text("Hello, LVGL!")
                print("❌ 기본 폰트로도 한글 실패, 영어로 표시")
        
        # 라벨 중앙 정렬
        label.center()
        print("✅ 라벨 중앙 정렬 완료")
        
        # 라벨 색상 설정 (흰색)
        label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 폰트 상태 표시 라벨 추가
        status_label = lv.label(scr)
        status_label.align(lv.ALIGN.CENTER, 0, 30)
        status_label.set_style_text_color(lv.color_hex(0x888888), 0)
        
        if font:
            status_label.set_text("Korean Font: Loaded")
        else:
            status_label.set_text("Korean Font: Not Available")
        
        # 화면 로드
        lv.screen_load(scr)
        print("✅ 화면 로드 완료")
        
        print("한글 텍스트 출력 테스트 완료")
        if font:
            print("화면에 '안녕하세요, LVGL!' 텍스트가 한글 폰트로 표시되어야 합니다.")
        else:
            print("화면에 기본 폰트로 텍스트가 표시되어야 합니다.")
        
        # LVGL 타이머 핸들러 호출 (화면 강제 업데이트)
        for i in range(20):
            lv.timer_handler()
            time.sleep(0.1)
        
        # 5초 대기
        time.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"❌ 한글 텍스트 출력 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_fs_driver_setup():
    """LVGL 파일 시스템 드라이버 설정 테스트"""
    print("=" * 60)
    print("LVGL 파일 시스템 드라이버 설정 테스트")
    print("=" * 60)
    
    try:
        # LVGL 초기화
        lv.init()
        
        # LVGL에서 사용 가능한 모든 속성 확인
        print("LVGL 모듈의 모든 속성 확인 중...")
        all_attrs = [attr for attr in dir(lv) if not attr.startswith('_')]
        print(f"LVGL 전체 속성 수: {len(all_attrs)}")
        
        # 파일 시스템 관련 속성만 필터링
        fs_attrs = [attr for attr in all_attrs if 'fs' in attr.lower()]
        print(f"파일 시스템 관련 속성: {fs_attrs}")
        
        # 폰트 관련 속성 확인
        font_attrs = [attr for attr in all_attrs if 'font' in attr.lower()]
        print(f"폰트 관련 속성: {font_attrs}")
        
        # 파일 시스템 드라이버 설정 방법들 시도
        print("\n파일 시스템 드라이버 설정 시도 중...")
        
        # 방법 1: 실제 LVGL 파일 시스템 함수들 테스트
        fs_methods = [
            'fs_init',           # LVGL 파일 시스템 초기화
            'fs_deinit',         # LVGL 파일 시스템 종료
            'fs_get_drv',        # 특정 드라이버 가져오기
            'fs_get_ext',        # 파일 확장자 가져오기
            'fs_get_last',       # 마지막 파일 관련 정보
            'fs_get_letters',    # 드라이브 문자 목록 반환
            'fs_up',             # 상위 디렉터리 이동
            'fs_file_t',         # 파일 객체 타입
            'fs_file_cache_t',   # 파일 캐시 객체
            'fs_dir_t',          # 디렉터리 객체
            'fs_drv_t'           # 파일 시스템 드라이버 객체
        ]
        
        for method in fs_methods:
            if hasattr(lv, method):
                print(f"✅ LVGL에 {method} 함수/클래스 존재")
                try:
                    if method in ['fs_file_t', 'fs_file_cache_t', 'fs_dir_t', 'fs_drv_t']:
                        # 클래스/타입인 경우
                        obj_type = getattr(lv, method)
                        print(f"✅ {method} 타입 확인: {obj_type}")
                    elif method == 'fs_init':
                        # 파일 시스템 초기화
                        result = getattr(lv, method)()
                        print(f"✅ {method} 호출 성공: {result}")
                    elif method == 'fs_get_letters':
                        # 드라이브 문자 목록 가져오기
                        letters = getattr(lv, method)()
                        print(f"✅ {method} 호출 성공: {letters}")
                    else:
                        # 기타 함수들
                        print(f"⚠️ {method} 함수는 매개변수가 필요할 수 있음")
                except Exception as e:
                    print(f"❌ {method} 호출 실패: {e}")
            else:
                print(f"❌ LVGL에 {method} 함수/클래스 없음")
        
        # 방법 1.5: 파일 시스템 드라이버 실제 설정 시도 (실제 fs_driver.py 구현 기반)
        print("\n파일 시스템 드라이버 실제 설정 시도:")
        try:
            if hasattr(lv, 'fs_drv_t'):
                # 파일 시스템 드라이버 객체 생성
                fs_drv = lv.fs_drv_t()
                print(f"✅ fs_drv_t 객체 생성 성공: {fs_drv}")
                
                # 실제 fs_driver.py 구현 사용
                print("실제 fs_driver.py 구현을 사용하여 드라이버 등록...")
                fs_driver.fs_register(fs_drv, 'S')  # 'S' 드라이버 문자로 등록
                print("✅ 파일 시스템 드라이버 등록 성공")
                    
            else:
                print("❌ fs_drv_t 클래스 없음")
        except Exception as e:
            print(f"❌ 파일 시스템 드라이버 설정 실패: {e}")
        
        # 방법 2: 파일 시스템 접근 테스트
        print("\n파일 시스템 접근 테스트:")
        try:
            import os
            files = os.listdir()
            print(f"✅ 현재 디렉토리 파일 목록: {files}")
            
            # NotoSansKR.bin 파일 확인
            if "NotoSansKR.bin" in files:
                print("✅ NotoSansKR.bin 파일 존재")
                # 파일 크기 확인
                try:
                    stat = os.stat("NotoSansKR.bin")
                    print(f"✅ 파일 크기: {stat[6]} bytes")
                except Exception as e:
                    print(f"❌ 파일 정보 읽기 실패: {e}")
            else:
                print("❌ NotoSansKR.bin 파일 없음")
        except Exception as e:
            print(f"❌ 파일 시스템 접근 실패: {e}")
        
        # 방법 3: LVGL 폰트 로드 테스트 (예제 코드 방식)
        print("\nLVGL 폰트 로드 테스트:")
        
        # 방법 3-1: 예제 코드 방식 - 드라이버 문자 사용
        try:
            font_path = "S:NotoSansKR.bin"  # 'S' 드라이버 문자 사용
            font = lv.binfont_create(font_path)
            print(f"✅ binfont_create (드라이버 문자) 성공: {font}")
            print(f"폰트 타입: {type(font)}")
        except Exception as e:
            print(f"❌ binfont_create (드라이버 문자) 실패: {e}")
        
        # 방법 3-2: 직접 파일 경로
        try:
            font = lv.binfont_create("NotoSansKR.bin")
            print(f"✅ binfont_create (직접 경로) 성공: {font}")
            print(f"폰트 타입: {type(font)}")
        except Exception as e:
            print(f"❌ binfont_create (직접 경로) 실패: {e}")
        
        # 방법 4: 대안 폰트 로드 방법
        try:
            font = lv.font_load("NotoSansKR.bin")
            print(f"✅ font_load 성공: {font}")
            print(f"폰트 타입: {type(font)}")
        except Exception as e:
            print(f"❌ font_load 실패: {e}")
        
        # 방법 5: 파일 시스템 드라이버 없이 폰트 로드 시도
        print("\n파일 시스템 드라이버 없이 폰트 로드 시도:")
        try:
            # 파일을 직접 읽어서 폰트 데이터로 사용
            with open("NotoSansKR.bin", "rb") as f:
                font_data = f.read()
                print(f"✅ 폰트 파일 읽기 성공: {len(font_data)} bytes")
                # 여기서 폰트 데이터를 직접 사용하는 방법을 시도할 수 있음
        except Exception as e:
            print(f"❌ 폰트 파일 직접 읽기 실패: {e}")
        
        # 방법 6: 폰트 관련 모든 함수 테스트
        print("\n폰트 관련 모든 함수 테스트:")
        font_methods = ['binfont_create', 'font_load', 'font_create', 'font_open', 'font_close']
        for method in font_methods:
            if hasattr(lv, method):
                print(f"✅ LVGL에 {method} 함수 존재")
                try:
                    if method == 'binfont_create':
                        result = getattr(lv, method)("NotoSansKR.bin")
                        print(f"✅ {method} 호출 성공: {result}")
                    elif method == 'font_load':
                        result = getattr(lv, method)("NotoSansKR.bin")
                        print(f"✅ {method} 호출 성공: {result}")
                    else:
                        print(f"⚠️ {method} 함수는 매개변수가 필요할 수 있음")
                except Exception as e:
                    print(f"❌ {method} 호출 실패: {e}")
            else:
                print(f"❌ LVGL에 {method} 함수 없음")
        
        print("\n파일 시스템 드라이버 설정 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ 파일 시스템 드라이버 설정 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_memory_efficient_font_loading():
    """메모리 효율적인 폰트 로딩 테스트"""
    print("=" * 60)
    print("메모리 효율적인 폰트 로딩 테스트")
    print("=" * 60)
    
    try:
        # LVGL 초기화
        lv.init()
        
        # 디스플레이 초기화
        if not init_display():
            print("❌ 디스플레이 초기화 실패")
            return False
        
        # 이벤트 루프 초기화
        if not lv_utils.event_loop.is_running():
            lv_utils.event_loop()
        
        # 파일 시스템 드라이버 설정
        print("파일 시스템 드라이버 설정 중...")
        try:
            if hasattr(lv, 'fs_drv_t'):
                fs_drv = lv.fs_drv_t()
                fs_driver.fs_register(fs_drv, 'S')
                print("✅ 파일 시스템 드라이버 등록 성공")
            else:
                print("❌ fs_drv_t 클래스 없음")
        except Exception as e:
            print(f"❌ 파일 시스템 드라이버 설정 실패: {e}")
        
        # 화면 생성
        scr = lv.obj()
        scr.set_style_bg_color(lv.color_hex(0x000000), 0)
        
        print("메모리 효율적인 폰트 로드 시도 중...")
        font = None
        
        # 메모리 효율적인 폰트 파일들 (크기 순서)
        font_files = [
            ("S:font-PHT-en-20.bin", "영어 폰트 (3.7KB)"),
            ("S:font-PHT-cn-20.bin", "중국어 폰트 (2.3KB)"),
            ("S:font-PHT-jp-20.bin", "일본어 폰트 (456B)"),
            ("S:NotoSansKR.bin", "한글 폰트 (346KB - 메모리 부족 가능)")
        ]
        
        for font_path, description in font_files:
            try:
                print(f"  {description} 시도 중...")
                font = lv.binfont_create(font_path)
                print(f"✅ {description} 로드 성공: {font}")
                break
            except MemoryError as e:
                print(f"❌ {description} 메모리 부족: {e}")
                print(f"   파일이 너무 큽니다. 다음 폰트를 시도합니다.")
                continue
            except Exception as e:
                print(f"❌ {description} 로드 실패: {e}")
                continue
        
        if font is None:
            print("❌ 모든 폰트 로드 실패, 기본 폰트 사용")
        
        # 라벨 생성 및 텍스트 설정
        label = lv.label(scr)
        if font and "한글" in str(font_files):
            label.set_text("안녕하세요, LVGL!")
        else:
            label.set_text("Hello LVGL!")
        
        # 폰트 적용
        if font:
            label.set_style_text_font(font, 0)
        
        # 라벨 중앙 정렬
        label.center()
        label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 상태 표시 라벨
        status_label = lv.label(scr)
        if font:
            status_text = "폰트 로드 성공"
        else:
            status_text = "기본 폰트 사용"
        status_label.set_text(status_text)
        status_label.align(lv.ALIGN.BOTTOM_MID, 0, -10)
        status_label.set_style_text_color(lv.color_hex(0x888888), 0)
        
        # 화면 로드
        lv.screen_load(scr)
        
        # 5초 대기
        time.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"❌ 메모리 효율적인 폰트 로딩 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_korean_font_example_style():
    """예제 코드 스타일의 한글 폰트 테스트"""
    print("=" * 60)
    print("예제 코드 스타일 한글 폰트 테스트")
    print("=" * 60)
    
    try:
        # LVGL 초기화
        lv.init()
        
        # 디스플레이 초기화
        set_st7735_offset(1, 2)
        init_display()
        
        # 디스플레이 백라이트 설정
        if current_display:
            current_display.set_backlight(100)
            print("✅ 디스플레이 백라이트 설정 완료")
        
        print("ST7735 LVGL 통합 완료")
        print("LVGL 디스플레이 설정 완료")
        
        # 이벤트 루프 시작
        if not lv_utils.event_loop.is_running():
            event_loop = lv_utils.event_loop()
            print("✅ LVGL 이벤트 루프 시작")
        
        # 예제 코드 방식: 파일 시스템 드라이버 설정
        print("예제 코드 방식으로 파일 시스템 드라이버 설정 중...")
        try:
            if hasattr(lv, 'fs_drv_t'):
                # 예제 코드: fs_drv = lv.fs_drv_t()
                fs_drv = lv.fs_drv_t()
                print(f"✅ fs_drv_t 객체 생성 성공: {fs_drv}")
                
                # 예제 코드: fs_driver.fs_driver.fs_register(fs_drv, 'S')
                # 실제 fs_driver.py 구현 사용
                print("실제 fs_driver.py 구현을 사용하여 드라이버 등록...")
                fs_driver.fs_register(fs_drv, 'S')  # 'S' 드라이버 문자로 등록
                print("✅ 파일 시스템 드라이버 등록 성공")
                
            else:
                print("❌ fs_drv_t 클래스 없음")
        except Exception as e:
            print(f"❌ 파일 시스템 드라이버 설정 실패: {e}")
        
        # 화면 생성 (예제 코드 방식)
        scr = lv.screen_active()
        scr.clean()  # 예제 코드에서 사용한 방식
        scr.set_style_bg_color(lv.color_hex(0x000000), 0)  # 검은 배경
        
        # 예제 코드 방식: 폰트 로드
        print("예제 코드 방식으로 폰트 로드 시도 중...")
        font = None
        
        # 예제 코드: myfont_cn = lv.binfont_create("S:%s/font/font-PHT-cn-20.bin" % script_path)
        try:
            # 드라이버 문자 사용한 경로
            font_path = "S:NotoSansKR.bin"
            font = lv.binfont_create(font_path)
            print(f"✅ 예제 방식 폰트 로드 성공: {font}")
            print(f"폰트 타입: {type(font)}")
        except Exception as e:
            print(f"❌ 예제 방식 폰트 로드 실패: {e}")
        
        # 대안: 직접 경로
        if font is None:
            try:
                font = lv.binfont_create("NotoSansKR.bin")
                print(f"✅ 직접 경로 폰트 로드 성공: {font}")
            except Exception as e:
                print(f"❌ 직접 경로 폰트 로드 실패: {e}")
        
        # 예제 코드 방식: 라벨 생성 및 텍스트 설정
        # 예제 코드: label1 = lv.label(scr)
        label = lv.label(scr)
        
        # 예제 코드: label1.set_style_text_font(myfont_cn, 0)
        if font:
            label.set_style_text_font(font, 0)
            print("✅ 한글 폰트 적용 완료")
        else:
            print("❌ 폰트 없음, 기본 폰트 사용")
        
        # 예제 코드: label1.set_text("上中下乎")
        label.set_text("안녕하세요, LVGL!")
        print("✅ 한글 텍스트 설정 완료")
        
        # 예제 코드: label1.align(lv.ALIGN.CENTER, 0, -25)
        label.align(lv.ALIGN.CENTER, 0, 0)
        print("✅ 라벨 중앙 정렬 완료")
        
        # 라벨 색상 설정 (흰색)
        label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # 폰트 상태 표시 라벨 추가
        status_label = lv.label(scr)
        status_label.align(lv.ALIGN.CENTER, 0, 30)
        status_label.set_style_text_color(lv.color_hex(0x888888), 0)
        
        if font:
            status_label.set_text("Korean Font: Loaded")
        else:
            status_label.set_text("Korean Font: Not Available")
        
        print("예제 코드 스타일 한글 폰트 테스트 완료")
        if font:
            print("화면에 '안녕하세요, LVGL!' 텍스트가 한글 폰트로 표시되어야 합니다.")
        else:
            print("화면에 기본 폰트로 텍스트가 표시되어야 합니다.")
        
        # LVGL 타이머 핸들러 호출 (화면 강제 업데이트)
        for i in range(20):
            lv.timer_handler()
            time.sleep(0.1)
        
        # 5초 대기
        time.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"❌ 예제 코드 스타일 한글 폰트 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def main():
    """메인 함수"""
    print("=" * 60)
    print("LVGL 통합 테스트 메뉴")
    print("=" * 60)
    print("1. 간단한 디스플레이 테스트")
    print("2. 오프셋 조정 테스트")
    print("3. ST7735 LVGL 테스트")
    print("4. LVGL 기본 기능 테스트")
    print("5. LVGL 데모")
    print("6. 대화형 오프셋 조정")
    print("7. 색상과 함께 오프셋 테스트")
    print("8. 오프셋 순환 테스트")
    print("9. 빠른 테스트")
    print("10. LVGL 간단한 테스트 (라벨만)")
    print("11. LVGL 키보드 테스트 (버튼 4개)")
    print("12. LVGL 버튼 테스트 (버튼 1개)")
    print("13. LVGL 심볼 버튼 테스트")
    print("14. LVGL 슬라이더 테스트")
    print("15. LVGL 드롭다운 테스트")
    print("16. LVGL 체크박스 테스트")
    print("17. LVGL 스피너 테스트")
    print("18. LVGL 바 테스트")
    print("19. LVGL 아크 테스트")
    print("20. LVGL 리스트 테스트")
    print("21. LVGL 메시지박스 테스트")
    print("22. 한글 폰트 테스트")
    print("23. 폰트 API 테스트")
    print("24. 한글 텍스트 출력 테스트")
    print("25. 파일 시스템 드라이버 설정 테스트")
    print("26. 예제 코드 스타일 한글 폰트 테스트")
    print("27. 메모리 효율적인 폰트 로딩 테스트")
    print("28. 종료")
    
    while True:
        try:
            choice = input("\n테스트 선택 (1-28): ").strip()
            
            if choice == '1':
                test_simple_display()
            elif choice == '2':
                test_offset_adjustment()
            elif choice == '3':
                test_st7735_lvgl()
            elif choice == '4':
                test_lvgl_basic()
            elif choice == '5':
                test_lvgl_demo()
            elif choice == '6':
                interactive_offset_adjustment()
            elif choice == '7':
                test_offset_with_colors()
            elif choice == '8':
                test_offset_cycle()
            elif choice == '9':
                quick_test()
            elif choice == '10':
                test_lvgl_simple()
            elif choice == '11':
                test_lvgl_keyboard()
            elif choice == '12':
                test_lvgl_buttons()
            elif choice == '13':
                test_lvgl_symbol_buttons()
            elif choice == '14':
                test_lvgl_slider()
            elif choice == '15':
                test_lvgl_dropdown()
            elif choice == '16':
                test_lvgl_checkbox()
            elif choice == '17':
                test_lvgl_spinner()
            elif choice == '18':
                test_lvgl_bar()
            elif choice == '19':
                test_lvgl_arc()
            elif choice == '20':
                test_lvgl_list()
            elif choice == '21':
                test_lvgl_msgbox()
            elif choice == '22':
                test_korean_font()
            elif choice == '23':
                test_font_apis()
            elif choice == '24':
                test_korean_text_display()
            elif choice == '25':
                test_fs_driver_setup()
            elif choice == '26':
                test_korean_font_example_style()
            elif choice == '27':
                test_memory_efficient_font_loading()
            elif choice == '28':
                print("테스트 종료")
                break
            else:
                print("잘못된 선택입니다. 1-28 중 선택하세요.")
                
        except KeyboardInterrupt:
            print("\n테스트 중단됨")
            break
        except Exception as e:
            print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()