"""
RGB 컬러 디스플레이 테스트 - HELLO 메시지
ST7735S 디스플레이에서 RGB 컬러로 "HELLO"를 한 글자씩 색상을 바꿔가며 표시
"""

import time
import machine
from machine import Pin, SPI

class RGBDisplayTest:
    """RGB 컬러 디스플레이 테스트 클래스"""
    
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
        self.column_offset = 2
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
        
        # RGB 컬러 정의
        self.colors = [
            (255, 0, 0),    # 빨강
            (0, 255, 0),    # 초록
            (0, 0, 255),    # 파랑
            (255, 255, 0),  # 노랑
            (255, 0, 255),  # 마젠타
            (0, 255, 255),  # 시안
            (255, 165, 0),  # 주황
            (128, 0, 128),  # 보라
            (255, 192, 203), # 분홍
            (0, 128, 0),    # 다크 그린
        ]
        
        print("RGB 디스플레이 테스트 초기화 완료")
        
    def init_display(self):
        """ST7735S 디스플레이 초기화 (boochow 라이브러리 기반)"""
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
        
    def draw_text(self, x, y, text, color, font_size=2):
        """간단한 텍스트 그리기 (기본 폰트)"""
        # 간단한 8x8 폰트 정의 (H, E, L, O)
        font = {
            'H': [
                [1, 0, 0, 0, 1],
                [1, 0, 0, 0, 1],
                [1, 1, 1, 1, 1],
                [1, 0, 0, 0, 1],
                [1, 0, 0, 0, 1]
            ],
            'E': [
                [1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0],
                [1, 1, 1, 1, 0],
                [1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1]
            ],
            'L': [
                [1, 0, 0, 0, 0],
                [1, 0, 0, 0, 0],
                [1, 0, 0, 0, 0],
                [1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1]
            ],
            'O': [
                [1, 1, 1, 1, 1],
                [1, 0, 0, 0, 1],
                [1, 0, 0, 0, 1],
                [1, 0, 0, 0, 1],
                [1, 1, 1, 1, 1]
            ]
        }
        
        char_x = x
        for char in text:
            if char in font:
                char_pattern = font[char]
                for row in range(len(char_pattern)):
                    for col in range(len(char_pattern[row])):
                        if char_pattern[row][col]:
                            self.fill_rect(
                                char_x + col * font_size,
                                y + row * font_size,
                                font_size,
                                font_size,
                                color
                            )
                char_x += (len(char_pattern[0]) + 1) * font_size
                
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
        
    def test_rgb_hello(self):
        """RGB 컬러로 HELLO 테스트"""
        print("RGB HELLO 테스트 시작...")
        
        # 화면 지우기
        self.clear_screen()
        
        # HELLO 텍스트를 한 글자씩 다른 색으로 표시
        text = "HELLO"
        start_x = 30
        start_y = 50
        
        for i, char in enumerate(text):
            # 각 글자마다 다른 색 사용
            color = self.colors[i % len(self.colors)]
            
            # 글자 그리기
            self.draw_text(start_x + i * 30, start_y, char, color, font_size=3)
            
            print(f"'{char}' 글자를 {color} 색으로 표시")
            time.sleep_ms(500)  # 0.5초 대기
            
        print("RGB HELLO 테스트 완료!")
        
    def test_color_cycle(self):
        """전체 HELLO 텍스트 색상 순환 테스트"""
        print("색상 순환 테스트 시작...")
        
        text = "HELLO"
        start_x = 30
        start_y = 50
        
        cycle_count = 0
        while cycle_count < 10:  # 10번 반복
            for color_idx, color in enumerate(self.colors):
                # 화면 지우기
                self.clear_screen()
                
                # 전체 HELLO를 같은 색으로 표시
                self.draw_text(start_x, start_y, text, color, font_size=3)
                
                print(f"사이클 {cycle_count + 1}, 색상 {color_idx + 1}: {color}")
                time.sleep_ms(1000)  # 1초 대기
                
            cycle_count += 1
            
        print("색상 순환 테스트 완료!")
        
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
            
            # 테스트 화면 표시
            self.clear_screen()
            self.draw_text(30, 50, "HELLO", (255, 255, 255), font_size=3)
            
            print(f"오프셋 설정 완료!")
            print(f"컬럼 오프셋: {self.column_offset}")
            print(f"로우 오프셋: {self.row_offset}")
            
        except Exception as e:
            print(f"오프셋 설정 오류: {e}")
    
    def test_offset_visual(self):
        """오프셋 시각적 테스트"""
        print("오프셋 시각적 테스트 시작...")
        
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
        
        # 중앙에 HELLO 표시
        self.draw_text(30, 50, "HELLO", (0, 0, 0), font_size=3)
        
        print("화면이 흰색으로 채워지고 빨간색 테두리가 그려졌습니다.")
        print("가장자리가 완전히 채워지는지 확인하세요.")
        print("5초 후 검은색으로 지워집니다...")
        time.sleep_ms(5000)
        
        # 화면 지우기
        self.clear_screen()
        print("오프셋 시각적 테스트 완료!")
        
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
        
    def test_pixels(self):
        """픽셀 테스트 기능"""
        print("\n=== 픽셀 테스트 ===")
        print("1. 개별 픽셀 테스트")
        print("2. 체크보드 패턴")
        print("3. 그라데이션 테스트")
        print("4. 색상 막대 테스트")
        print("5. 돌아가기")
        
        while True:
            try:
                choice = input("\n픽셀 테스트 선택 (1-5): ").strip()
                
                if choice == '1':
                    self.test_individual_pixels()
                elif choice == '2':
                    self.test_checkerboard()
                elif choice == '3':
                    self.test_gradient()
                elif choice == '4':
                    self.test_color_bars()
                elif choice == '5':
                    break
                else:
                    print("잘못된 선택입니다. 1-5 중 선택하세요.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"오류 발생: {e}")
                
    def test_individual_pixels(self):
        """개별 픽셀 테스트"""
        print("개별 픽셀 테스트 시작...")
        
        # 화면 지우기
        self.clear_screen()
        
        # 테스트할 색상들
        test_colors = [
            (255, 0, 0),    # 빨강
            (0, 255, 0),    # 초록
            (0, 0, 255),    # 파랑
            (255, 255, 0),  # 노랑
            (255, 0, 255),  # 마젠타
            (0, 255, 255),  # 시안
            (255, 255, 255), # 흰색
            (0, 0, 0),      # 검정
        ]
        
        # 화면 중앙에 8x8 픽셀 그리드 그리기
        start_x = 76
        start_y = 60
    
        for i, color in enumerate(test_colors):
            x = start_x + (i % 4) * 2
            y = start_y + (i // 4) * 2
            
            # 2x2 픽셀 사각형 그리기
            self.fill_rect(x, y, 2, 2, color)
            print(f"픽셀 ({x},{y}) - 색상 {i+1}: {color}")
            time.sleep_ms(200)
            
        print("개별 픽셀 테스트 완료!")
        time.sleep_ms(3000)
        
    def test_checkerboard(self):
        """체크보드 패턴 테스트"""
        print("체크보드 패턴 테스트 시작...")
        
        # 화면 지우기
        self.clear_screen()
        
        # 10x8 체크보드 패턴
        square_size = 16  # 160/10 = 16, 128/8 = 16
        
        for y in range(8):  # 128/16 = 8
            for x in range(10):  # 160/16 = 10
                if (x + y) % 2 == 0:
                    # 흰색 사각형
                    self.fill_rect(x * square_size, y * square_size, square_size, square_size, (255, 255, 255))
                else:
                    # 검정색 사각형
                    self.fill_rect(x * square_size, y * square_size, square_size, square_size, (0, 0, 0))
                    
        print("체크보드 패턴 테스트 완료!")
        time.sleep_ms(3000)
        
    def test_gradient(self):
        """그라데이션 테스트"""
        print("그라데이션 테스트 시작...")
        
        # 화면 지우기
        self.clear_screen()
        
        # 수평 그라데이션 (빨강 → 파랑)
        for x in range(160):
            # 빨강에서 파랑으로 그라데이션
            red = int(255 * (1 - x / 159))
            blue = int(255 * (x / 159))
            
            color = (red, 0, blue)
            self.fill_rect(x, 0, 1, 128, color)
            
        print("그라데이션 테스트 완료!")
        time.sleep_ms(3000)
        
    def test_color_bars(self):
        """색상 막대 테스트"""
        print("색상 막대 테스트 시작...")
        
        # 화면 지우기
        self.clear_screen()
        
        # 8가지 색상 막대
        colors = [
            (255, 0, 0),    # 빨강
            (255, 165, 0),  # 주황
            (255, 255, 0),  # 노랑
            (0, 255, 0),    # 초록
            (0, 255, 255),  # 시안
            (0, 0, 255),    # 파랑
            (128, 0, 128),  # 보라
            (255, 0, 255),  # 마젠타
        ]
        
        bar_width = 20  # 160/8 = 20
        
        for i, color in enumerate(colors):
            x = i * bar_width
            self.fill_rect(x, 0, bar_width, 128, color)
            print(f"색상 막대 {i+1}: {color}")
            
        print("색상 막대 테스트 완료!")
        time.sleep_ms(3000)

def main():
    """메인 함수"""
    try:
        # 테스트 객체 생성
        display_test = RGBDisplayTest()
        
        print("\n=== RGB 디스플레이 테스트 ===")
        print("1. HELLO 글자별 색상 테스트")
        print("2. 전체 색상 순환 테스트")
        print("3. 오프셋 설정")
        print("4. 오프셋 시각적 테스트")
        print("5. 픽셀 테스트")
        print("6. 종료")
        
        while True:
            try:
                choice = input("\n테스트 선택 (1-5): ").strip()
                
                if choice == '1':
                    display_test.test_rgb_hello()
                elif choice == '2':
                    display_test.test_color_cycle()
                elif choice == '3':
                    display_test.set_offset_interactive()
                elif choice == '4':
                    display_test.test_offset_visual()
                elif choice == '5':
                    display_test.test_pixels()
                elif choice == '6':
                    print("테스트 종료")
                    break
                else:
                    print("잘못된 선택입니다. 1-6 중 선택하세요.")
                    
            except KeyboardInterrupt:
                print("\n테스트 중단됨")
                break
            except Exception as e:
                print(f"오류 발생: {e}")
                
    except Exception as e:
        print(f"초기화 오류: {e}")

if __name__ == "__main__":
    main()