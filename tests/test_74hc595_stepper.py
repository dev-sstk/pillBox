"""
74HC595D + ULN2003 스테퍼모터 제어 테스트
ESP32-C6에서 74HC595D 시프트 레지스터를 통해 ULN2003 드라이버로 스테퍼모터 제어
"""

from machine import Pin
import time
import _thread

class InputShiftRegister:
    """74HC165D 입력 시프트 레지스터 제어 클래스 (test_74hc165.py 참고)"""
    
    def __init__(self, clock_pin=3, pload_pin=15, data_pin=10):
        """입력 시프트 레지스터 초기화"""
        # 핀 설정 (test_74hc165.py와 동일)
        self.ploadPin = Pin(pload_pin, Pin.OUT)      # PL 핀 (IO15)
        self.dataPin = Pin(data_pin, Pin.IN)         # Q7 출력 (IO10)
        self.clockPin = Pin(clock_pin, Pin.OUT)      # CLK 핀 (IO3)
        
        # 기본 파라미터 (test_74hc165.py와 동일)
        self.NUMBER_OF_SHIFT_CHIPS = 1
        self.DATA_WIDTH = self.NUMBER_OF_SHIFT_CHIPS * 8
        self.PULSE_WIDTH_USEC = 5
        
        # 초기 상태 설정 (test_74hc165.py와 동일)
        self.clockPin.value(0)
        self.ploadPin.value(1)
        
    def read_byte(self):
        """1바이트 데이터 읽기 (test_74hc165.py와 동일)"""
        bytesVal = 0

        # 병렬 입력을 래치 (test_74hc165.py와 동일)
        self.ploadPin.value(0)  # Load data (Active LOW)
        time.sleep_us(self.PULSE_WIDTH_USEC)
        self.ploadPin.value(1)  # Stop loading
        time.sleep_us(self.PULSE_WIDTH_USEC)

        # 직렬 데이터 읽기 (test_74hc165.py와 동일)
        for i in range(self.DATA_WIDTH):
            bitVal = self.dataPin.value()
            bytesVal |= (bitVal << ((self.DATA_WIDTH - 1) - i))

            # CLK 상승엣지
            self.clockPin.value(1)
            time.sleep_us(self.PULSE_WIDTH_USEC)
            self.clockPin.value(0)
            time.sleep_us(self.PULSE_WIDTH_USEC)

        return bytesVal

class LimitSwitch:
    """리미트 스위치 클래스"""
    
    def __init__(self, input_shift_register, bit_position):
        """리미트 스위치 초기화"""
        self.input_shift_register = input_shift_register
        self.bit_position = bit_position
        
    def is_pressed(self):
        """리미트 스위치가 눌렸는지 확인 (test_74hc165.py 기준)"""
        data = self.input_shift_register.read_byte()
        # test_74hc165.py 기준: HIGH=눌리지 않음, LOW=눌림
        # 비트가 0이면 눌린 상태, 1이면 눌리지 않은 상태
        return (data & (1 << self.bit_position)) == 0

class StepperMotorController:
    """74HC595D + ULN2003 스테퍼모터 제어 클래스"""
    
    def __init__(self, di_pin=2, sh_cp_pin=3, st_cp_pin=15, data_out_pin=10):
        """
        초기화
        Args:
            di_pin: 74HC595D Data Input 핀 (GPIO2)
            sh_cp_pin: 74HC595D Shift Clock 핀 (GPIO3)
            st_cp_pin: 74HC595D Storage Clock 핀 (GPIO15)
            data_out_pin: 74HC165D Data Output 핀 (GPIO10)
        """
        # 74HC595D 핀 설정
        self.di = Pin(di_pin, Pin.OUT)
        self.sh_cp = Pin(sh_cp_pin, Pin.OUT)
        self.st_cp = Pin(st_cp_pin, Pin.OUT)
        
        # 초기 상태 설정
        self.di.value(0)
        self.sh_cp.value(0)
        self.st_cp.value(0)
        
        # 입력 시프트 레지스터 초기화 (별도 핀 사용)
        # 74HC165D는 별도의 클록 핀을 사용해야 할 수 있음
        self.input_shift_register = InputShiftRegister(sh_cp_pin, st_cp_pin, data_out_pin)
        
        # 리미트 스위치 초기화 (test_74hc165.py 기준: 비트 4, 5, 6, 7 사용)
        self.limit_switches = [
            LimitSwitch(self.input_shift_register, 4),  # 모터 0 리미트 스위치 (LIMIT SW1)
            LimitSwitch(self.input_shift_register, 5),  # 모터 1 리미트 스위치 (LIMIT SW2)
            LimitSwitch(self.input_shift_register, 6),  # 모터 2 리미트 스위치 (LIMIT SW3)
            LimitSwitch(self.input_shift_register, 7),  # 모터 3 리미트 스위치 (LIMIT SW4)
        ]
        
        # 스테퍼모터 설정 (28BYJ-48)
        self.steps_per_rev = 2048  # 28BYJ-48의 스텝 수
        # 각 모터별 독립적인 스텝 상태
        self.motor_steps = [0, 0, 0, 0]  # 모터 0,1,2,3의 현재 스텝
        
        # ULN2003 시퀀스 (8스텝 시퀀스)
        self.stepper_sequence = [
            0b00001000,  # 0x08 - A
            0b00001100,  # 0x0C - A,B
            0b00000100,  # 0x04 - B
            0b00000110,  # 0x06 - B,C
            0b00000010,  # 0x02 - C
            0b00000011,  # 0x03 - C,D
            0b00000001,  # 0x01 - D
            0b00001001   # 0x09 - D,A
        ]
        
        # 4개 모터의 현재 상태 (각 모터당 8비트)
        self.motor_states = [0, 0, 0, 0]
        
        # 속도 설정 (기본값: 0.2ms = 5000Hz)
        self.step_delay_us = 200  # 스텝 간 지연 시간 (마이크로초) - 0.2ms
        
        # 비블로킹 제어를 위한 변수들
        self.motor_running = [False, False, False, False]  # 각 모터별 실행 상태
        self.motor_direction = [1, 1, 1, 1]  # 각 모터별 방향
        self.last_step_times = [0, 0, 0, 0]  # 각 모터별 마지막 스텝 시간
        
        print("74HC595D + ULN2003 스테퍼모터 컨트롤러 초기화 완료")
    
    def check_limit_switches(self):
        """모든 리미트 스위치 상태 확인"""
        states = []
        raw_data = self.input_shift_register.read_byte()
        
        for i, limit_switch in enumerate(self.limit_switches):
            is_pressed = limit_switch.is_pressed()
            states.append(is_pressed)
            if is_pressed:
                print(f"모터 {i} 리미트 스위치 눌림!")
        return states
    
    def is_limit_switch_pressed(self, motor_index):
        """특정 모터의 리미트 스위치가 눌렸는지 확인"""
        if 0 <= motor_index <= 3:
            return self.limit_switches[motor_index].is_pressed()
        return False
    
    def shift_out(self, data):
        """74HC595D에 8비트 데이터 전송 (최적화됨)"""
        for i in range(8):
            # MSB first
            bit = (data >> (7 - i)) & 1
            self.di.value(bit)
            
            # Shift clock pulse (딜레이 제거)
            self.sh_cp.value(1)
            
            self.sh_cp.value(0)
        
        # Storage clock pulse (latch) - 최소 딜레이만 유지
        self.st_cp.value(1)
        self.st_cp.value(0)
    

    
    def update_motor_output(self):
        """모든 모터 상태를 74HC595D에 출력"""
        combined_data = 0

        # 모터0 → 하위 4비트 (Q0~Q3)
        combined_data |= (self.motor_states[0] & 0x0F)

        # 모터1 → 상위 4비트 (Q4~Q7)
        combined_data |= ((self.motor_states[1] & 0x0F) << 4)

        # 모터2 → 두 번째 칩 하위 4비트 (Q0~Q3 of 2번 74HC595)
        combined_data |= ((self.motor_states[2] & 0x0F) << 8)

        # 모터3 → 두 번째 칩 상위 4비트 (Q4~Q7 of 2번 74HC595)
        combined_data |= ((self.motor_states[3] & 0x0F) << 12)

        # 전송 (상위 바이트 먼저)
        upper_byte = (combined_data >> 8) & 0xFF
        lower_byte = combined_data & 0xFF

        self.shift_out(upper_byte)
        self.shift_out(lower_byte)
    

    
    def set_motor_step(self, motor_index, step_value):
        """특정 모터의 스텝 설정"""
        if 0 <= motor_index <= 3:
            self.motor_states[motor_index] = self.stepper_sequence[step_value % 8]
            self.update_motor_output()
    
    def step_motor(self, motor_index, direction=1, steps=1):
        """스테퍼모터 회전"""
        if 0 <= motor_index <= 3:
            for _ in range(steps):
                # 리미트 스위치 확인
                if self.is_limit_switch_pressed(motor_index):
                    print(f"모터 {motor_index} 리미트 스위치 감지! 회전 중단")
                    return False
                
                # 각 모터의 독립적인 스텝 계산
                self.motor_steps[motor_index] = (self.motor_steps[motor_index] + direction) % 8
                current_step = self.motor_steps[motor_index]
                
                # 모터 스텝 설정
                self.set_motor_step(motor_index, current_step)
                
                # 회전 속도 조절
                time.sleep_us(self.step_delay_us)
            
            return True
    
    def rotate_motor(self, motor_index, direction=1, revolutions=1):
        """스테퍼모터 완전 회전"""
        total_steps = int(self.steps_per_rev * revolutions)
        print(f"모터 {motor_index} {revolutions}회전 시작 ({total_steps}스텝)")
        
        for i in range(0, total_steps, 8):
            remaining_steps = min(8, total_steps - i)
            if not self.step_motor(motor_index, direction, remaining_steps):
                print(f"모터 {motor_index} 회전 중단됨 (리미트 스위치)")
                return False
        
        print(f"모터 {motor_index} 회전 완료")
        return True
    
    def stop_motor(self, motor_index):
        """모터 정지 (모든 코일 OFF)"""
        if 0 <= motor_index <= 3:
            self.motor_states[motor_index] = 0
            self.update_motor_output()
            print(f"모터 {motor_index} 정지")
    
    def stop_all_motors(self):
        """모든 모터 정지"""
        for i in range(4):
            self.motor_states[i] = 0
        self.update_motor_output()
        print("모든 모터 정지")
    
    def set_speed(self, delay_ms):
        """모터 속도 설정 (전역 속도만)"""
        if delay_ms < 0.001:
            delay_ms = 0.001  # 최소 0.001ms (1,000,000Hz)
        elif delay_ms > 100:
            delay_ms = 100  # 최대 100ms (10Hz)
        
        # 전역 속도 설정 (모든 방식에 적용)
        self.step_delay_us = int(delay_ms * 1000)  # 마이크로초 단위로 저장
        
        frequency = 1000000 / self.step_delay_us
        print(f"모터 속도 설정: {delay_ms}ms 지연 ({frequency:.0f}Hz)")
        print("전역 속도가 업데이트되었습니다.")
    
    def get_speed(self):
        """현재 모터 속도 반환"""
        delay_ms = self.step_delay_us / 1000  # 마이크로초를 밀리초로 변환
        frequency = 1000000 / self.step_delay_us
        return delay_ms, frequency
    
    def test_single_motor(self, motor_index):
        """단일 모터 테스트"""
        print(f"=== 모터 {motor_index} 테스트 ===")
        
        # 정방향 1회전
        print("정방향 1회전...")
        self.rotate_motor(motor_index, 1, 1)
        time.sleep(1)
        
        # 역방향 1회전
        print("역방향 1회전...")
        self.rotate_motor(motor_index, -1, 1)
        time.sleep(1)
        
        # 정지
        self.stop_motor(motor_index)
        print(f"모터 {motor_index} 테스트 완료")
    
    def test_all_motors(self):
        """모든 모터 테스트"""
        print("=== 모든 모터 테스트 ===")
        
        for motor in range(4):
            print(f"\n모터 {motor} 테스트 중...")
            self.test_single_motor(motor)
            time.sleep(2)
        
        print("모든 모터 테스트 완료")
    
    def step_all_motors(self, direction=1, steps=1):
        """모든 모터를 동시에 회전"""
        if 0 <= direction <= 1:
            for _ in range(steps):
                # 리미트 스위치 확인
                limit_pressed = False
                for motor in range(4):
                    if self.is_limit_switch_pressed(motor):
                        print(f"모터 {motor} 리미트 스위치 감지! 모든 모터 회전 중단")
                        limit_pressed = True
                        break
                
                if limit_pressed:
                    return False
                
                # 모든 모터의 스텝을 동시에 계산
                for motor in range(4):
                    self.motor_steps[motor] = (self.motor_steps[motor] + direction) % 8
                    current_step = self.motor_steps[motor]
                    self.motor_states[motor] = self.stepper_sequence[current_step]
                
                # 모든 모터 상태를 한 번에 출력
                self.update_motor_output()
                
                # 회전 속도 조절
                time.sleep_us(self.step_delay_us)
            
            return True
    
    def rotate_all_motors(self, direction=1, revolutions=1):
        """모든 모터를 동시에 완전 회전"""
        total_steps = int(self.steps_per_rev * revolutions)
        print(f"모든 모터 {revolutions}회전 시작 ({total_steps}스텝)")
        
        for i in range(0, total_steps, 8):
            remaining_steps = min(8, total_steps - i)
            if not self.step_all_motors(direction, remaining_steps):
                print("모든 모터 회전 중단됨 (리미트 스위치)")
                return False
        
        print("모든 모터 회전 완료")
        return True
    
    def test_all_motors_simultaneous(self):
        """모든 모터 동시 동작 테스트"""
        print("=== 모든 모터 동시 동작 테스트 ===")
        
        # 정방향 0.5회전
        print("모든 모터 정방향 0.5회전...")
        self.rotate_all_motors(1, 0.5)
        time.sleep(1)
        
        # 역방향 0.5회전
        print("모든 모터 역방향 0.5회전...")
        self.rotate_all_motors(-1, 0.5)
        time.sleep(1)
        
        # 모든 모터 정지
        self.stop_all_motors()
        print("모든 모터 동시 동작 테스트 완료")
    
    def test_limit_switches(self):
        """리미트 스위치 테스트 (test_74hc165.py와 동일)"""
        print("=== 리미트 스위치 테스트 ===")
        print("각 모터의 리미트 스위치를 눌러보세요.")
        print("Ctrl+C로 종료")
        
        # 초기 상태 읽기
        old_pin_values = self.input_shift_register.read_byte()
        print("초기 상태:")
        self.display_pin_values(old_pin_values)
        
        count = 0
        try:
            while True:
                pin_values = self.input_shift_register.read_byte()
                count += 1
                
                if pin_values != old_pin_values:
                    # 현재 시간과 카운트
                    current_time = time.time()
                    
                    # 모든 스위치 상태를 한 줄로 출력
                    input_names = [
                        "SW1", "SW2", "SW3", "SW4", 
                        "LIM1", "LIM2", "LIM3", "LIM4"
                    ]
                    
                    status_line = f"[{count:4d}] {current_time:7.1f}s - 변경 감지! "
                    for i in range(8):
                        state = "H" if ((pin_values >> i) & 1) else "L"
                        status_line += f"{input_names[i]}:{state} "
                    
                    print(status_line)
                    old_pin_values = pin_values
                
                time.sleep_ms(1)  # 1ms 대기
                
        except KeyboardInterrupt:
            print(f"\n모니터링 중단됨")
            print(f"총 {count}회 읽기 완료")
    
    def display_pin_values(self, pin_values):
        """읽은 비트 값을 핀별로 출력 (test_74hc165.py 참고)"""
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
        for i in range(8):
            state = "HIGH" if ((pin_values >> i) & 1) else "LOW"
            print(f"  {input_names[i]}: {state}")
        print("")
    
    def test_motor_with_limit_switch(self, motor_index):
        """리미트 스위치가 있는 모터 테스트"""
        print(f"=== 모터 {motor_index} 리미트 스위치 테스트 ===")
        print(f"모터 {motor_index}를 회전시키고 리미트 스위치를 눌러보세요.")
        
        # 정방향 회전 (리미트 스위치까지)
        print(f"모터 {motor_index} 정방향 회전 시작...")
        if not self.rotate_motor(motor_index, 1, 1):
            print(f"모터 {motor_index} 리미트 스위치에 도달!")
        
        time.sleep(1)
        
        # 역방향 회전
        print(f"모터 {motor_index} 역방향 회전 시작...")
        if not self.rotate_motor(motor_index, -1, 1):
            print(f"모터 {motor_index} 리미트 스위치에 도달!")
        
        # 모터 정지
        self.stop_motor(motor_index)
        print(f"모터 {motor_index} 리미트 스위치 테스트 완료")
    
    def test_infinite_rotation_with_limit_switches(self):
        """모든 모터 무한 회전 + 리미트 스위치 테스트"""
        print("=== 모든 모터 무한 회전 + 리미트 스위치 테스트 ===")
        print("모든 모터가 정방향으로 무한 회전합니다.")
        print("리미트 스위치를 누르면 해당 모터가 멈추고, 떼면 다시 회전합니다.")
        print("Ctrl+C로 종료")
        
        # 모터 상태 추적 (True: 회전 중, False: 정지)
        motor_running = [True, True, True, True]
        
        try:
            while True:
                # 각 모터별로 처리
                for motor in range(4):
                    if motor_running[motor]:
                        # 모터가 회전 중이고 리미트 스위치가 눌리지 않았으면 계속 회전
                        if not self.is_limit_switch_pressed(motor):
                            # 1스텝 회전
                            self.motor_steps[motor] = (self.motor_steps[motor] + 1) % 8
                            current_step = self.motor_steps[motor]
                            self.motor_states[motor] = self.stepper_sequence[current_step]
                        else:
                            # 리미트 스위치가 눌렸으면 모터 정지
                            print(f"모터 {motor} 리미트 스위치 감지! 정지")
                            motor_running[motor] = False
                            self.motor_states[motor] = 0
                    else:
                        # 모터가 정지 중이고 리미트 스위치가 떼어졌으면 다시 회전 시작
                        if not self.is_limit_switch_pressed(motor):
                            print(f"모터 {motor} 리미트 스위치 해제! 회전 재개")
                            motor_running[motor] = True
                
                # 모든 모터 상태를 한 번에 출력
                self.update_motor_output()
                
                # 회전 속도 조절
                time.sleep_us(self.step_delay_us)
                
        except KeyboardInterrupt:
            print("\n무한 회전 테스트 종료")
            # 모든 모터 정지
            for i in range(4):
                self.motor_states[i] = 0
            self.update_motor_output()
            print("모든 모터 정지됨")
    
    def test_single_motor_infinite_rotation(self, motor_index):
        """단일 모터 무한 회전 + 리미트 스위치 테스트"""
        print(f"=== 모터 {motor_index} 무한 회전 + 리미트 스위치 테스트 ===")
        print(f"모터 {motor_index}가 정방향으로 무한 회전합니다.")
        print(f"리미트 스위치를 누르면 모터가 멈추고, 떼면 다시 회전합니다.")
        print("Ctrl+C로 종료")
        
        motor_running = True
        
        try:
            while True:
                if motor_running:
                    # 모터가 회전 중이고 리미트 스위치가 눌리지 않았으면 계속 회전
                    if not self.is_limit_switch_pressed(motor_index):
                        # 1스텝 회전
                        self.motor_steps[motor_index] = (self.motor_steps[motor_index] + 1) % 8
                        current_step = self.motor_steps[motor_index]
                        self.motor_states[motor_index] = self.stepper_sequence[current_step]
                    else:
                        # 리미트 스위치가 눌렸으면 모터 정지
                        print(f"모터 {motor_index} 리미트 스위치 감지! 정지")
                        motor_running = False
                        self.motor_states[motor_index] = 0
                else:
                    # 모터가 정지 중이고 리미트 스위치가 떼어졌으면 다시 회전 시작
                    if not self.is_limit_switch_pressed(motor_index):
                        print(f"모터 {motor_index} 리미트 스위치 해제! 회전 재개")
                        motor_running = True
                
                # 모터 상태 출력
                self.update_motor_output()
                
                # 회전 속도 조절
                time.sleep_us(self.step_delay_us)
                
        except KeyboardInterrupt:
            print(f"\n모터 {motor_index} 무한 회전 테스트 종료")
            # 모터 정지
            self.motor_states[motor_index] = 0
            self.update_motor_output()
            print(f"모터 {motor_index} 정지됨")
    
    def test_sequence_pattern(self):
        """시퀀스 패턴 테스트"""
        print("=== 시퀀스 패턴 테스트 ===")
        
        for step in range(8):
            print(f"스텝 {step}: 0x{self.stepper_sequence[step]:02X}")
            self.set_motor_step(0, step)
            time.sleep(500)  # 0.5초 대기
        
        self.stop_motor(0)
        print("시퀀스 패턴 테스트 완료")
    
    def test_shift_register_output(self):
        """시프트 레지스터 출력 테스트"""
        print("=== 시프트 레지스터 출력 테스트 ===")
        
        # 모든 모터 OFF
        for i in range(4):
            self.motor_states[i] = 0
        self.update_motor_output()
        time.sleep(1000)
        
        # 각 모터를 순차적으로 ON/OFF
        for motor in range(4):
            print(f"모터 {motor} ON...")
            self.motor_states[motor] = 0x0F  # 모든 비트 ON
            self.update_motor_output()
            time.sleep(2000)  # 2초 대기
            
            print(f"모터 {motor} OFF...")
            self.motor_states[motor] = 0x00  # 모든 비트 OFF
            self.update_motor_output()
            time.sleep(1000)  # 1초 대기
        
        print("시프트 레지스터 출력 테스트 완료")
    
    def debug_raw_input_data(self):
        """원시 입력 데이터 디버깅"""
        print("=== 원시 입력 데이터 디버깅 ===")
        print("10초간 원시 데이터를 출력합니다.")
        print("Ctrl+C로 중단")
        
        try:
            for i in range(10):
                raw_data = self.input_shift_register.read_byte()
                print(f"[{i+1:2d}] Raw: 0x{raw_data:02X} (0b{raw_data:08b})")
                
                # 각 비트별 상태
                for bit in range(8):
                    bit_value = (raw_data >> bit) & 1
                    print(f"  비트 {bit}: {bit_value}")
                
                print("-" * 30)
                time.sleep(1000)  # 1초 대기
                
        except KeyboardInterrupt:
            print("\n디버깅 중단")
    
    def test_speed_variations(self):
        """다양한 속도로 모터 테스트"""
        print("=== 속도 변화 테스트 ===")
        
        speeds = [0.2, 0.5, 1, 2, 5, 10, 20, 50]  # 다양한 속도 (ms)
        
        for speed in speeds:
            print(f"\n--- 속도: {speed}ms ({1000/speed:.0f}Hz) ---")
            self.set_speed(speed)
            
            # 모터 0으로 0.5회전 테스트
            print("모터 0 정방향 0.5회전...")
            self.rotate_motor(0, 1, 0.5)
            time.sleep(1)
            
            # 역방향으로 원위치
            print("모터 0 역방향 0.5회전...")
            self.rotate_motor(0, -1, 0.5)
            time.sleep(1)
        
        # 기본 속도로 복원
        self.set_speed(2)
        print("\n속도 테스트 완료")
    
    def test_nonblocking_motors(self):
        """비블로킹 모터 테스트"""
        print("=== 비블로킹 모터 테스트 ===")
        print("모든 모터가 동일한 속도로 비블로킹 실행")
        
        # 현재 속도 확인
        current_delay, current_freq = self.get_speed()
        print(f"현재 속도: {current_delay}ms ({current_freq:.0f}Hz)")
        print(f"설정된 마이크로초: {self.step_delay_us}µs")
        print(f"예상 초당 스텝: {1000000/self.step_delay_us:.1f}")
        
        # 모든 모터 비블로킹 시작
        self.start_all_motors_nonblocking(1)  # 정방향
        
        print("모터들이 비블로킹으로 회전 중... (10초)")
        print("Ctrl+C로 중단하세요")
        
        start_time = time.ticks_ms()
        step_count = 0
        motor_step_counts = [0, 0, 0, 0]  # 각 모터별 스텝 카운트
        
        try:
            while time.ticks_diff(time.ticks_ms(), start_time) < 10000:  # 10초
                # 비블로킹 모터 업데이트
                self.update_motors_nonblocking()
                step_count += 1
                
                # 각 모터의 스텝 진행 확인
                for i in range(4):
                    if self.motor_running[i]:
                        motor_step_counts[i] += 1
                
                # 1초마다 상태 출력
                if step_count % 1000 == 0:
                    elapsed_seconds = step_count // 1000
                    print(f"실행 중... ({elapsed_seconds}초)")
                    # 모터 상태 확인
                    for i in range(4):
                        if self.motor_running[i]:
                            steps_per_second = motor_step_counts[i] / elapsed_seconds
                            print(f"  모터 {i}: 실행중, 스텝 {self.motor_steps[i]}, 초당 {steps_per_second:.1f}스텝")
                
                # time.sleep_ms(1)  # 1ms 대기 (CPU 부하 감소)
        except KeyboardInterrupt:
            pass
        
        # 모든 모터 정지
        self.stop_all_motors_nonblocking()
        print("비블로킹 테스트 완료")
    
    def test_single_motor_nonblocking(self, motor_index):
        """단일 모터 비블로킹 테스트"""
        print(f"=== 모터 {motor_index} 비블로킹 테스트 ===")
        
        # 현재 속도 확인
        current_delay, current_freq = self.get_speed()
        print(f"현재 속도: {current_delay}ms ({current_freq:.0f}Hz)")
        print(f"설정된 마이크로초: {self.step_delay_us}µs")
        print(f"예상 초당 스텝: {1000000/self.step_delay_us:.1f}")
        
        # 모터 비블로킹 시작
        self.start_motor_nonblocking(motor_index, 1)  # 정방향
        
        print(f"모터 {motor_index}가 비블로킹으로 회전 중... (5초)")
        print("Ctrl+C로 중단하세요")
        
        start_time = time.ticks_ms()
        step_count = 0
        motor_step_count = 0
        
        try:
            while time.ticks_diff(time.ticks_ms(), start_time) < 5000:  # 5초
                # 비블로킹 모터 업데이트
                self.update_motors_nonblocking()
                step_count += 1
                
                # 모터 스텝 진행 확인
                if self.motor_running[motor_index]:
                    motor_step_count += 1
                
                # 1초마다 상태 출력
                if step_count % 1000 == 0:
                    elapsed_seconds = step_count // 1000
                    steps_per_second = motor_step_count / elapsed_seconds
                    print(f"실행 중... ({elapsed_seconds}초), 초당 {steps_per_second:.1f}스텝")
                
                time.sleep_ms(1)  # 1ms 대기
        except KeyboardInterrupt:
            pass
        
        # 모터 정지
        self.stop_motor_nonblocking(motor_index)
        print(f"모터 {motor_index} 비블로킹 테스트 완료")
    

    
    def test_nonblocking_motor_control(self):
        """비블로킹 모터 개별 제어 테스트"""
        print("=== 비블로킹 모터 개별 제어 테스트 ===")
        print("각 모터를 개별적으로 제어할 수 있습니다.")
        print("명령어:")
        print("  start <모터번호> <방향> - 모터 시작 (예: start 0 1)")
        print("  stop <모터번호> - 모터 정지 (예: stop 0)")
        print("  status - 모든 모터 상태 확인")
        print("  stopall - 모든 모터 정지")
        print("  quit - 종료")
        print("  (속도는 옵션 22번에서 설정)")
        
        print("비블로킹 모터 제어 모드 시작")
        print("모터들이 백그라운드에서 실행됩니다.")
        
        try:
            while True:
                # 비블로킹 모터 업데이트
                self.update_motors_nonblocking()
                
                # 입력이 있는지 확인 (non-blocking)
                try:
                    cmd = input("명령어 입력: ").strip().split()
                    if not cmd:
                        continue
                except:
                    # 입력이 없으면 계속 모터 업데이트
                    time.sleep_ms(1)
                    continue
                
                if cmd[0] == "start" and len(cmd) >= 3:
                    motor = int(cmd[1])
                    direction = int(cmd[2])
                    self.start_motor_nonblocking(motor, direction)
                
                elif cmd[0] == "stop" and len(cmd) >= 2:
                    motor = int(cmd[1])
                    self.stop_motor_nonblocking(motor)
                
                elif cmd[0] == "status":
                    status = self.get_motor_status()
                    for s in status:
                        print(f"모터 {s['motor']}: {'실행중' if s['running'] else '정지'} "
                              f"(방향: {s['direction']}, 속도: {s['speed_ms']}ms)")
                
                elif cmd[0] == "stopall":
                    self.stop_all_motors_nonblocking()
                
                elif cmd[0] == "quit":
                    break
                
                else:
                    print("잘못된 명령어입니다.")
        
        except KeyboardInterrupt:
            pass
        
        # 모든 모터 정지
        self.stop_all_motors_nonblocking()
        print("개별 제어 테스트 완료")
    
    def test_nonblocking_demo(self):
        """비블로킹 데모 테스트"""
        print("=== 비블로킹 데모 테스트 ===")
        print("모터들이 백그라운드에서 실행되면서 다른 작업도 가능합니다.")
        
        # 모든 모터 비블로킹 시작
        self.start_all_motors_nonblocking(1)  # 정방향
        
        print("모터들이 실행 중... (15초)")
        print("이 시간 동안 다른 작업을 시뮬레이션합니다.")
        
        start_time = time.ticks_ms()
        counter = 0
        
        try:
            while time.ticks_diff(time.ticks_ms(), start_time) < 15000:  # 15초
                # 비블로킹 모터 업데이트
                self.update_motors_nonblocking()
                
                # 다른 작업 시뮬레이션 (예: 센서 읽기, 통신 등)
                counter += 1
                if counter % 1000 == 0:  # 1초마다
                    print(f"백그라운드 작업 실행 중... ({counter//1000}초)")
                
                time.sleep_ms(1)  # 1ms 대기
                
        except KeyboardInterrupt:
            pass
        
        # 모든 모터 정지
        self.stop_all_motors_nonblocking()
        print("비블로킹 데모 완료")
    
    def test_interactive_nonblocking(self):
        """대화형 비블로킹 모터 제어 테스트"""
        print("=== 대화형 비블로킹 모터 제어 테스트 ===")
        print("모터들이 백그라운드에서 실행되면서 실시간으로 제어할 수 있습니다.")
        print("명령어:")
        print("  start <모터번호> <방향> - 모터 시작 (예: start 0 1)")
        print("  stop <모터번호> - 모터 정지 (예: stop 0)")
        print("  status - 모든 모터 상태 확인")
        print("  stopall - 모든 모터 정지")
        print("  quit - 종료")
        print("  (속도는 옵션 22번에서 설정)")
        
        print("\n비블로킹 모터 제어 모드 시작")
        print("모터들이 백그라운드에서 실행됩니다.")
        
        try:
            while True:
                # 비블로킹 모터 업데이트
                self.update_motors_nonblocking()
                
                # 입력이 있는지 확인 (non-blocking)
                try:
                    cmd = input("명령어 입력: ").strip().split()
                    if not cmd:
                        continue
                    
                    if cmd[0] == "start" and len(cmd) >= 3:
                        motor = int(cmd[1])
                        direction = int(cmd[2])
                        self.start_motor_nonblocking(motor, direction)
                    
                    elif cmd[0] == "stop" and len(cmd) >= 2:
                        motor = int(cmd[1])
                        self.stop_motor_nonblocking(motor)
                    
                    elif cmd[0] == "status":
                        status = self.get_motor_status()
                        for s in status:
                            print(f"모터 {s['motor']}: {'실행중' if s['running'] else '정지'} "
                                  f"(방향: {s['direction']}, 속도: {s['speed_ms']}ms)")
                    
                    elif cmd[0] == "stopall":
                        self.stop_all_motors_nonblocking()
                    
                    elif cmd[0] == "quit":
                        break
                    
                    else:
                        print("잘못된 명령어입니다.")
                
                except:
                    # 입력이 없으면 계속 모터 업데이트
                    time.sleep_ms(1)
                    continue
        
        except KeyboardInterrupt:
            pass
        
        # 모든 모터 정지
        self.stop_all_motors_nonblocking()
        print("대화형 비블로킹 테스트 완료")
    
    def set_speed_interactive(self):
        """대화형 속도 설정"""
        print("=== 대화형 속도 설정 ===")
        
        current_delay, current_freq = self.get_speed()
        print(f"현재 속도: {current_delay}ms ({current_freq:.0f}Hz)")
        
        try:
            new_delay = float(input("새로운 지연 시간을 입력하세요 (0.001-100ms, 0.001ms 단위): "))
            
            # 입력값 검증
            if new_delay < 0.001:
                print("⚠️ 최소값은 0.001ms입니다. 0.001ms로 설정합니다.")
                new_delay = 0.001
            elif new_delay > 100:
                print("⚠️ 최대값은 100ms입니다. 100ms로 설정합니다.")
                new_delay = 100
            
            self.set_speed(new_delay)
            print("✅ 속도가 업데이트되었습니다!")
            print(f"설정된 속도: {new_delay}ms ({1000/new_delay:.0f}Hz)")
        except ValueError:
            print("잘못된 입력입니다. 속도 변경을 취소합니다.")
    
    def start_motor_nonblocking(self, motor_index, direction=1):
        """비블로킹으로 모터 시작"""
        if 0 <= motor_index <= 3:
            self.motor_running[motor_index] = True
            self.motor_direction[motor_index] = direction
            self.last_step_times[motor_index] = time.ticks_us()  # 마이크로초 단위로 변경
            print(f"모터 {motor_index} 비블로킹 시작 (방향: {direction})")
    
    def stop_motor_nonblocking(self, motor_index):
        """비블로킹 모터 정지"""
        if 0 <= motor_index <= 3:
            self.motor_running[motor_index] = False
            self.motor_states[motor_index] = 0
            self.update_motor_output()
            print(f"모터 {motor_index} 비블로킹 정지")
    
    def stop_all_motors_nonblocking(self):
        """모든 비블로킹 모터 정지"""
        for i in range(4):
            self.stop_motor_nonblocking(i)
        print("모든 비블로킹 모터 정지")
    
    def update_motors_nonblocking(self):
        """비블로킹 모터 업데이트 (메인 루프에서 호출)"""
        current_time = time.ticks_us()  # 마이크로초 단위로 변경
        output_updated = False  # 출력 업데이트 플래그
        
        for motor_index in range(4):
            if self.motor_running[motor_index]:
                # 리미트 스위치 확인
                if self.is_limit_switch_pressed(motor_index):
                    print(f"모터 {motor_index} 리미트 스위치 감지! 정지")
                    self.motor_running[motor_index] = False
                    self.motor_states[motor_index] = 0
                    output_updated = True
                    continue
                
                # 시간 체크로 스텝 진행 (전역 속도 사용)
                time_diff = time.ticks_diff(current_time, self.last_step_times[motor_index])
                if time_diff >= self.step_delay_us:  # 마이크로초 단위로 비교
                    # 모터 스텝 진행
                    self.motor_steps[motor_index] = (self.motor_steps[motor_index] + self.motor_direction[motor_index]) % 8
                    current_step = self.motor_steps[motor_index]
                    self.motor_states[motor_index] = self.stepper_sequence[current_step]
                    
                    # 마지막 스텝 시간 업데이트
                    self.last_step_times[motor_index] = current_time
                    output_updated = True
        
            # 변경사항이 있을 때만 출력 업데이트
            if output_updated:
                self.update_motor_output()
    
    def start_all_motors_nonblocking(self, direction=1):
        """모든 모터를 비블로킹으로 시작"""
        for i in range(4):
            self.start_motor_nonblocking(i, direction)
        print(f"모든 모터 비블로킹 시작 (방향: {direction})")
    
    def get_motor_status(self):
        """모든 모터 상태 확인"""
        status = []
        for i in range(4):
            running = self.motor_running[i]
            direction = self.motor_direction[i]
            speed_ms = self.step_delay_us / 1000  # 마이크로초를 밀리초로 변환
            status.append({
                'motor': i,
                'running': running,
                'direction': direction,
                'speed_ms': speed_ms
            })
        return status
    


def main():
    """74HC595D 스테퍼모터 테스트 메인 함수"""
    print("74HC595D + ULN2003 스테퍼모터 테스트")
    print("=" * 50)
    
    # 컨트롤러 초기화
    controller = StepperMotorController()
    
    try:
        while True:
            print("\n테스트 메뉴:")
            print("1. 모터 0 테스트")
            print("2. 모터 1 테스트")
            print("3. 모터 2 테스트")
            print("4. 모터 3 테스트")
            print("5. 모든 모터 테스트")
            print("6. 모든 모터 동시 동작 테스트")
            print("7. 리미트 스위치 테스트")
            print("8. 모터 0 리미트 스위치 테스트")
            print("9. 모터 1 리미트 스위치 테스트")
            print("10. 모터 2 리미트 스위치 테스트")
            print("11. 모터 3 리미트 스위치 테스트")
            print("12. 모든 모터 무한 회전 + 리미트 스위치 테스트")
            print("13. 모터 0 무한 회전 + 리미트 스위치 테스트")
            print("14. 모터 1 무한 회전 + 리미트 스위치 테스트")
            print("15. 모터 2 무한 회전 + 리미트 스위치 테스트")
            print("16. 모터 3 무한 회전 + 리미트 스위치 테스트")
            print("17. 시퀀스 패턴 테스트")
            print("18. 연속 회전 테스트")
            print("19. 시프트 레지스터 출력 테스트")
            print("20. 원시 입력 데이터 디버깅")
            print("21. 속도 변화 테스트")
            print("22. 대화형 속도 설정")
            print("23. 비블로킹 모터 테스트")
            print("24. 비블로킹 모터 개별 제어 테스트")
            print("25. 비블로킹 데모 테스트")
            print("26. 대화형 비블로킹 모터 제어 테스트")
            print("27. 모터 0 비블로킹 테스트")
            print("28. 모터 1 비블로킹 테스트")
            print("29. 모터 2 비블로킹 테스트")
            print("30. 모터 3 비블로킹 테스트")
            print("0. 종료")
            
            choice = input("선택하세요 (0-30): ").strip()
            
            if choice == "1":
                controller.test_single_motor(0)
            elif choice == "2":
                controller.test_single_motor(1)
            elif choice == "3":
                controller.test_single_motor(2)
            elif choice == "4":
                controller.test_single_motor(3)
            elif choice == "5":
                controller.test_all_motors()
            elif choice == "6":
                controller.test_all_motors_simultaneous()
            elif choice == "7":
                controller.test_limit_switches()
            elif choice == "8":
                controller.test_motor_with_limit_switch(0)
            elif choice == "9":
                controller.test_motor_with_limit_switch(1)
            elif choice == "10":
                controller.test_motor_with_limit_switch(2)
            elif choice == "11":
                controller.test_motor_with_limit_switch(3)
            elif choice == "12":
                controller.test_infinite_rotation_with_limit_switches()
            elif choice == "13":
                controller.test_single_motor_infinite_rotation(0)
            elif choice == "14":
                controller.test_single_motor_infinite_rotation(1)
            elif choice == "15":
                controller.test_single_motor_infinite_rotation(2)
            elif choice == "16":
                controller.test_single_motor_infinite_rotation(3)
            elif choice == "17":
                controller.test_sequence_pattern()
            elif choice == "18":
                print("연속 회전 테스트 (Ctrl+C로 중단)")
                try:
                    while True:
                        controller.rotate_motor(0, 1, 0.1)  # 0.1회전씩
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    controller.stop_all_motors()
                    print("연속 회전 중단")
            elif choice == "19":
                controller.test_shift_register_output()
            elif choice == "20":
                controller.debug_raw_input_data()
            elif choice == "21":
                controller.test_speed_variations()
            elif choice == "22":
                controller.set_speed_interactive()
            elif choice == "23":
                controller.test_nonblocking_motors()
            elif choice == "24":
                controller.test_nonblocking_motor_control()
            elif choice == "25":
                controller.test_nonblocking_demo()
            elif choice == "26":
                controller.test_interactive_nonblocking()
            elif choice == "27":
                controller.test_single_motor_nonblocking(0)
            elif choice == "28":
                controller.test_single_motor_nonblocking(1)
            elif choice == "29":
                controller.test_single_motor_nonblocking(2)
            elif choice == "30":
                controller.test_single_motor_nonblocking(3)
            elif choice == "0":
                break
            else:
                print("잘못된 선택입니다.")
            
            # 모든 모터 정지
            controller.stop_all_motors()
            
    except KeyboardInterrupt:
        print("\n테스트 중단됨")
    finally:
        controller.stop_all_motors()
        print("모든 모터 정지됨")

if __name__ == "__main__":
    main()
