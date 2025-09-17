"""
GPT가 작성한 74HC165D 코드를 ESP32-C6에 맞게 수정
"""

from machine import Pin
import time

# 핀 설정 (ESP32-C6 GPIO 번호로 수정)
ploadPin = Pin(15, Pin.OUT)      # PL 핀 (IO15)
# clockEnablePin = Pin(9, Pin.OUT) # CE 핀 - 그라운드에 연결되어 있음
dataPin = Pin(10, Pin.IN)        # Q7 출력 (IO10)
clockPin = Pin(3, Pin.OUT)       # CLK 핀 (IO3)

# 기본 파라미터
NUMBER_OF_SHIFT_CHIPS = 1
DATA_WIDTH = NUMBER_OF_SHIFT_CHIPS * 8
PULSE_WIDTH_USEC = 5
POLL_DELAY_MSEC = 1

# 초기 상태
clockPin.value(0)
ploadPin.value(1)
# clockEnablePin.value(0)  # CE 핀은 그라운드에 연결되어 있음

def read_shift_regs():
    """SN74HC165에서 직렬 데이터 읽기 (CE 핀 없이)"""
    bytesVal = 0

    # 병렬 입력을 래치 (CE 핀 없이)
    ploadPin.value(0)  # Load data (Active LOW)
    time.sleep_us(PULSE_WIDTH_USEC)
    ploadPin.value(1)  # Stop loading
    time.sleep_us(PULSE_WIDTH_USEC)

    # 직렬 데이터 읽기
    for i in range(DATA_WIDTH):
        bitVal = dataPin.value()
        bytesVal |= (bitVal << ((DATA_WIDTH - 1) - i))

        # CLK 상승엣지
        clockPin.value(1)
        time.sleep_us(PULSE_WIDTH_USEC)
        clockPin.value(0)
        time.sleep_us(PULSE_WIDTH_USEC)

    return bytesVal

def display_pin_values(pinValues):
    """읽은 비트 값을 핀별로 출력"""
    input_names = [
        "SW1(Menu)",      # Pin 0
        "SW2(Select)",    # Pin 1
        "SW3(Up)",        # Pin 2
        "SW4(Down)",      # Pin 3
        "LIMIT SW1",      # Pin 4
        "LIMIT SW2",      # Pin 5
        "LIMIT SW3",      # Pin 6
        "LIMIT SW4"       # Pin 7
    ]
    
    print("Pin States:")
    for i in range(DATA_WIDTH):
        state = "HIGH" if ((pinValues >> i) & 1) else "LOW"
        print(f"  {input_names[i]}: {state}")
    print("")

def test_single_read():
    """단일 읽기 테스트"""
    print("=== 단일 읽기 테스트 ===")
    pinValues = read_shift_regs()
    print(f"Raw Data: 0b{pinValues:08b} (0x{pinValues:02X})")
    display_pin_values(pinValues)
    return pinValues

def test_continuous_monitor():
    """연속 모니터링 (변경 감지 시에만 출력)"""
    print("=== 연속 모니터링 시작 ===")
    print("스위치 상태가 변경될 때만 출력합니다")
    print("Ctrl+C로 중단하세요")
    print("=" * 50)
    
    # 초기 상태 읽기
    oldPinValues = read_shift_regs()
    print("초기 상태:")
    display_pin_values(oldPinValues)
    
    count = 0
    try:
        while True:
            pinValues = read_shift_regs()
            count += 1
            
            if pinValues != oldPinValues:
                # 현재 시간과 카운트
                current_time = time.time()
                
                # 모든 스위치 상태를 한 줄로 출력
                input_names = [
                    "SW1", "SW2", "SW3", "SW4", 
                    "LIM1", "LIM2", "LIM3", "LIM4"
                ]
                
                status_line = f"[{count:4d}] {current_time:7.1f}s - 변경 감지! "
                for i in range(DATA_WIDTH):
                    state = "H" if ((pinValues >> i) & 1) else "L"
                    status_line += f"{input_names[i]}:{state} "
                
                print(status_line)
                oldPinValues = pinValues
            
            time.sleep_ms(POLL_DELAY_MSEC)
            
    except KeyboardInterrupt:
        print(f"\n모니터링 중단됨")
        print(f"총 {count}회 읽기 완료")

def test_debug_read():
    """디버그 읽기 (모든 읽기 출력)"""
    print("=== 디버그 읽기 (10초) ===")
    start_time = time.time()
    count = 0
    
    while time.time() - start_time < 10:
        pinValues = read_shift_regs()
        count += 1
        print(f"[{count}] {time.time() - start_time:.1f}s: 0b{pinValues:08b} (0x{pinValues:02X})")
        time.sleep_ms(100)
    
    print(f"총 {count}회 읽기 완료")

def main():
    print("74HC165D 테스트 프로그램")
    print("=" * 50)
    
    print("1. 단일 읽기 테스트")
    print("2. 연속 모니터링 (변경 감지 시에만 출력)")
    print("3. 디버그 읽기 (10초)")
    
    choice = input("선택하세요 (1-3): ").strip()
    
    if choice == "1":
        test_single_read()
    elif choice == "2":
        test_continuous_monitor()
    elif choice == "3":
        test_debug_read()
    else:
        print("잘못된 선택입니다. 연속 모니터링을 시작합니다.")
        test_continuous_monitor()

if __name__ == "__main__":
    main()