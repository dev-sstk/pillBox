"""
버튼 인터페이스 (74HC165 시프트 레지스터 기반)
SW1(Menu), SW2(Select), SW3(Up), SW4(Down) 버튼의 입력을 처리하는 클래스
"""

from machine import Pin
import time

class ButtonInterface:
    """74HC165 시프트 레지스터 기반 버튼 인터페이스 클래스"""
    
    def __init__(self):
        """버튼 인터페이스 초기화"""
        # 74HC165 핀 설정 (ESP32-C6 GPIO)
        self.pload_pin = Pin(15, Pin.OUT)      # PL 핀 (IO15)
        self.data_pin = Pin(10, Pin.IN)        # Q7 출력 (IO10)
        self.clock_pin = Pin(3, Pin.OUT)       # CLK 핀 (IO3)
        
        # 기본 파라미터
        self.NUMBER_OF_SHIFT_CHIPS = 1
        self.DATA_WIDTH = self.NUMBER_OF_SHIFT_CHIPS * 8
        self.PULSE_WIDTH_USEC = 5
        self.POLL_DELAY_MSEC = 1
        
        # 초기 상태 설정
        self.clock_pin.value(0)
        self.pload_pin.value(1)
        
        # 버튼 매핑 (74HC165 핀 순서)
        self.button_mapping = {
            0: 'SW1',  # 버튼 A 역할
            1: 'SW2',  # 버튼 B 역할
            2: 'SW3',  # 버튼 C 역할
            3: 'SW4',  # 버튼 D 역할
            4: 'LIMIT_SW1',  # 리미트 스위치 1
            5: 'LIMIT_SW2',  # 리미트 스위치 2
            6: 'LIMIT_SW3',  # 리미트 스위치 3
            7: 'UNUSED'      # 사용 안함
        }
        
        # 버튼 콜백 함수들 (A, B, C, D 매핑)
        self.callbacks = {
            'A': None,  # SW1
            'B': None,  # SW2
            'C': None,  # SW3
            'D': None   # SW4
        }
        
        # 버튼 상태 추적
        self.last_button_states = 0xFF  # 모든 버튼이 HIGH 상태로 초기화
        self.current_button_states = 0xFF
        
        # 디바운싱 설정
        self.debounce_time = 50  # ms
        self.last_press_time = {key: 0 for key in self.callbacks.keys()}
        
        # print("[OK] ButtonInterface (74HC165) 초기화 완료")
        # print(f"핀 설정: PL={self.pload_pin}, DATA={self.data_pin}, CLK={self.clock_pin}")
    
    def read_shift_regs(self):
        """SN74HC165에서 직렬 데이터 읽기"""
        bytes_val = 0
        
        # 병렬 입력을 래치
        self.pload_pin.value(0)  # Load data (Active LOW)
        time.sleep_us(self.PULSE_WIDTH_USEC)
        self.pload_pin.value(1)  # Stop loading
        time.sleep_us(self.PULSE_WIDTH_USEC)
        
        # 직렬 데이터 읽기
        for i in range(self.DATA_WIDTH):
            bit_val = self.data_pin.value()
            bytes_val |= (bit_val << ((self.DATA_WIDTH - 1) - i))
            
            # CLK 상승엣지
            self.clock_pin.value(1)
            time.sleep_us(self.PULSE_WIDTH_USEC)
            self.clock_pin.value(0)
            time.sleep_us(self.PULSE_WIDTH_USEC)
        
        return bytes_val
    
    def update(self):
        """버튼 상태 업데이트 및 변경 감지"""
        self.current_button_states = self.read_shift_regs()
        current_time = time.ticks_ms()
        
        # 버튼 상태 변경 감지
        if self.current_button_states != self.last_button_states:
            # 각 버튼의 상태 변화 확인
            for pin_num, button_name in self.button_mapping.items():
                old_state = (self.last_button_states >> pin_num) & 1
                new_state = (self.current_button_states >> pin_num) & 1
                
                # 버튼이 눌렸을 때 (HIGH -> LOW)
                if old_state == 1 and new_state == 0:
                    self._handle_button_press(button_name, pin_num, current_time)
            
            self.last_button_states = self.current_button_states
            return True
        
        return False
    
    def _handle_button_press(self, button_name, pin_num, current_time):
        """버튼 눌림 처리"""
        # A, B, C, D 버튼 매핑
        button_id = None
        if button_name == 'SW1':  # SW1 → A
            button_id = 'A'
        elif button_name == 'SW2':  # SW2 → B
            button_id = 'B'
        elif button_name == 'SW3':  # SW3 → C
            button_id = 'C'
        elif button_name == 'SW4':  # SW4 → D
            button_id = 'D'
        
        if button_id:
            # 디바운싱 체크
            if time.ticks_diff(current_time, self.last_press_time[button_id]) > self.debounce_time:
                self.last_press_time[button_id] = current_time
                # print(f"[BTN] 버튼 {button_id} ({button_name}) 눌림")
                
                # 콜백 함수 호출
                if self.callbacks[button_id]:
                    try:
                        self.callbacks[button_id]()
                    except Exception as e:
                        # print(f"[ERROR] 버튼 {button_id} 콜백 실행 오류: {e}")
                        pass
    
    def set_callback(self, button_id, callback):
        """버튼 콜백 함수 설정"""
        if button_id in self.callbacks:
            self.callbacks[button_id] = callback
            # print(f"[OK] 버튼 {button_id} 콜백 설정 완료")
        else:
            # print(f"[ERROR] 잘못된 버튼 ID: {button_id}")
            pass
    
    def get_button_state(self, button_id):
        """버튼 상태 반환"""
        # A, B, C, D를 실제 핀 번호로 매핑
        pin_mapping = {
            'A': 0,  # SW1
            'B': 1,  # SW2
            'C': 2,  # SW3
            'D': 3   # SW4
        }
        
        if button_id in pin_mapping:
            pin_num = pin_mapping[button_id]
            return not ((self.current_button_states >> pin_num) & 1)  # LOW일 때 눌림
        else:
            return False
    
    def get_all_button_states(self):
        """모든 버튼 상태 반환"""
        return {
            'A': self.get_button_state('A'),  # SW1 → A
            'B': self.get_button_state('B'),  # SW2 → B
            'C': self.get_button_state('C'),  # SW3 → C
            'D': self.get_button_state('D')   # SW4 → D
        }
    
    def get_raw_button_states(self):
        """원시 버튼 상태 반환 (74HC165 전체 데이터)"""
        return self.current_button_states
    
    def get_shift_register_info(self):
        """시프트 레지스터 정보 반환"""
        return {
            'raw_data': self.current_button_states,
            'binary': f"0b{self.current_button_states:08b}",
            'hex': f"0x{self.current_button_states:02X}",
            'button_mapping': self.button_mapping
        }
    
    def get_button_info(self):
        """버튼 정보 반환"""
        return {
            'A': 'SW1 (Button A)',
            'B': 'SW2 (Button B)', 
            'C': 'SW3 (Button C)',
            'D': 'SW4 (Button D)'
        }
    
    def test_buttons(self):
        """버튼 테스트 함수"""
        # print("=== 74HC165 버튼 테스트 시작 ===")
        # print("버튼을 눌러보세요. Ctrl+C로 중단하세요.")
        # print("=" * 50)
        
        try:
            count = 0
            while True:
                if self.update():
                    count += 1
                    # 변경된 버튼 상태 출력
                    info = self.get_shift_register_info()
                    # print(f"[{count}] Raw: {info['binary']} ({info['hex']})")
                    
                    # 각 버튼 상태 출력
                    states = self.get_all_button_states()
                    for btn_id, state in states.items():
                        if state:
                            # print(f"  {btn_id} 버튼 눌림")
                            pass
                
                time.sleep_ms(10)
                
        except KeyboardInterrupt:
            # print(f"\n버튼 테스트 중단됨 (총 {count}회 변경 감지)")
            pass
    
    def display_pin_values(self, pin_values):
        """읽은 비트 값을 핀별로 출력"""
        input_names = [
            "SW1(Menu)",      # Pin 0
            "SW2(Select)",    # Pin 1
            "SW3(Up)",        # Pin 2
            "SW4(Down)",      # Pin 3
            "LIMIT SW3",      # Pin 4 (역순)
            "LIMIT SW2",      # Pin 5
            "LIMIT SW1",      # Pin 6 (역순)
            "LIMIT SW4"       # Pin 7
        ]
        
        # print("Pin States:")
        for i in range(self.DATA_WIDTH):
            state = "HIGH" if ((pin_values >> i) & 1) else "LOW"
            # print(f"  {input_names[i]}: {state}")
        # print("")