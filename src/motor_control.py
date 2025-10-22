"""
스테퍼 모터 제어 시스템 (74HC595D + ULN2003 기반)
필박스의 알약 충전/배출을 위한 스테퍼 모터 제어
"""

from machine import Pin
import time

class InputShiftRegister:
    """74HC165D 입력 시프트 레지스터 제어 클래스"""
    
    def __init__(self, clock_pin=3, pload_pin=15, data_pin=10):
        """입력 시프트 레지스터 초기화"""
        # 핀 설정 (button_interface.py와 동일)
        self.pload_pin = Pin(pload_pin, Pin.OUT)      # PL 핀 (IO15)
        self.data_pin = Pin(data_pin, Pin.IN)         # Q7 출력 (IO10)
        self.clock_pin = Pin(clock_pin, Pin.OUT)      # CLK 핀 (IO3)
        
        # 기본 파라미터
        self.NUMBER_OF_SHIFT_CHIPS = 1
        self.DATA_WIDTH = self.NUMBER_OF_SHIFT_CHIPS * 8
        self.PULSE_WIDTH_USEC = 5
        
        # 초기 상태 설정
        self.clock_pin.value(0)
        self.pload_pin.value(1)
        
    def read_byte(self):
        """1바이트 데이터 읽기 (test_74hc165.py와 동일한 로직)"""
        bytes_val = 0

        # 병렬 입력을 래치
        self.pload_pin.value(0)  # Load data (Active LOW)
        time.sleep_us(self.PULSE_WIDTH_USEC)
        self.pload_pin.value(1)  # Stop loading
        time.sleep_us(self.PULSE_WIDTH_USEC)

        # 직렬 데이터 읽기 (test_74hc165.py와 동일한 순서)
        for i in range(self.DATA_WIDTH):
            bit_val = self.data_pin.value()
            bytes_val |= (bit_val << ((self.DATA_WIDTH - 1) - i))

            # CLK 상승엣지
            self.clock_pin.value(1)
            time.sleep_us(self.PULSE_WIDTH_USEC)
            self.clock_pin.value(0)
            time.sleep_us(self.PULSE_WIDTH_USEC)

        return bytes_val

class LimitSwitch:
    """리미트 스위치 클래스"""
    
    def __init__(self, input_shift_register, bit_position):
        """리미트 스위치 초기화"""
        self.input_shift_register = input_shift_register
        self.bit_position = bit_position
        
    def is_pressed(self):
        """리미트 스위치가 눌렸는지 확인 (최적화된 버전)"""
        data = self.input_shift_register.read_byte()
        # HIGH=눌리지 않음, LOW=눌림
        is_pressed = (data & (1 << self.bit_position)) == 0
        # 로그 출력 제거로 성능 향상 (필요시 주석 해제)
        # if is_pressed:
        #     # print(f"  [BTN] 리미트 스위치 {self.bit_position} 감지! (데이터: 0b{data:08b})")
        return is_pressed

class StepperMotorController:
    """74HC595D + ULN2003 스테퍼모터 제어 클래스"""
    
    def __init__(self, di_pin=2, sh_cp_pin=3, st_cp_pin=15, data_out_pin=10):
        """
        초기화
        Args:
            di_pin: 74HC595D Data Input 핀 (GPIO2)
            sh_cp_pin: 74HC595D Shift Clock 핀 (GPIO3) - 74HC165D와 공유
            st_cp_pin: 74HC595D Storage Clock 핀 (GPIO15) - 74HC165D와 공유
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
        
        # 입력 시프트 레지스터 초기화 (리미트 스위치용)
        self.input_shift_register = InputShiftRegister(sh_cp_pin, st_cp_pin, data_out_pin)
        
        # 리미트 스위치 초기화 (사용자 요청 매핑)
        # 모터 1→LIMIT SW1 (Pin 5), 모터 2→LIMIT SW2 (Pin 6), 모터 3→LIMIT SW3 (Pin 7)
        # 모터 4는 리미트 스위치 없음 (게이트 제어용)
        self.limit_switches = [
            None,  # 인덱스 0 사용 안함
            LimitSwitch(self.input_shift_register, 5),  # 모터 1 → LIMIT SW1 (Pin 5)
            LimitSwitch(self.input_shift_register, 6),  # 모터 2 → LIMIT SW2 (Pin 6)
            LimitSwitch(self.input_shift_register, 7),  # 모터 3 → LIMIT SW3 (Pin 7)
            None,  # 모터 4 리미트 스위치 없음 (게이트 제어용)
        ]
        
        # 스테퍼모터 설정 (28BYJ-48)
        self.steps_per_rev = 4096  # 28BYJ-48의 스텝 수 (64:1 감속비)
        self.steps_per_compartment = 273  # 1칸당 스텝 수 (4096/15칸)
        
        # 각 모터별 독립적인 스텝 상태
        self.motor_steps = [0, 0, 0, 0, 0]  # 모터 1,2,3,4의 현재 스텝 (인덱스 0 사용 안함)
        self.motor_positions = [0, 0, 0, 0, 0]  # 각 모터의 현재 칸 위치 (인덱스 0 사용 안함)
        
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
        self.motor_states = [0, 0, 0, 0, 0]  # 모터 1,2,3,4 상태 (인덱스 0 사용 안함)
        
        # 속도 설정 (디스크 회전과 동일한 속도) - 모터 우선순위 모드
        self.step_delay_us = 500  # 스텝 간 지연 시간 (마이크로초) - 디스크 회전과 동일 (0.5ms)
        
        # 비블로킹 제어를 위한 변수들
        self.motor_running = [False, False, False, False, False]  # 각 모터별 실행 상태 (인덱스 0 사용 안함)
        self.motor_direction = [1, 1, 1, 1, 1]  # 각 모터별 방향 (인덱스 0 사용 안함)
        self.last_step_times = [0, 0, 0, 0, 0]  # 각 모터별 마지막 스텝 시간 (인덱스 0 사용 안함)
        
        # 초기화 시 모든 코일 OFF 상태로 설정
        self.turn_off_all_coils()
        
        # print("[OK] StepperMotorController 초기화 완료")
    
    def turn_off_all_coils(self):
        """모든 모터 코일 OFF (74HC595 출력 LOW → ULN2003A 출력 HIGH → 코일 OFF)"""
        # print("[FAST] 모터 코일 초기화: 모든 코일 OFF 설정")
        
        # 모든 모터의 상태를 0x00으로 설정
        # 0x00 = 0b00000000 (모든 코일 OFF)
        for i in range(1, 5):  # 모터 1,2,3,4
            self.motor_states[i] = 0x00
        
        # 74HC595D에 출력
        self.update_motor_output()
        # print("[OK] 모터 코일 초기화 완료: 모든 코일 OFF")
    
    def turn_off_coil(self, motor_index):
        """특정 모터 코일 OFF"""
        if 1 <= motor_index <= 4:
            self.motor_states[motor_index] = 0x00  # 모든 코일 OFF
            self.update_motor_output()
            # print(f"모터 {motor_index} 코일 OFF")
    
    def check_limit_switches(self):
        """모든 리미트 스위치 상태 확인"""
        states = []
        raw_data = self.input_shift_register.read_byte()
        
        for i, limit_switch in enumerate(self.limit_switches):
            if limit_switch is None:
                states.append(False)  # 리미트 스위치 없으면 False
            else:
                is_pressed = limit_switch.is_pressed()
                states.append(is_pressed)
                if is_pressed:
                    # print(f"모터 {i} 리미트 스위치 눌림!")
                    pass
        return states
    
    def is_limit_switch_pressed(self, motor_index):
        """특정 모터의 리미트 스위치가 눌렸는지 확인"""
        if 1 <= motor_index <= 4:
            # 모터 3은 리미트 스위치 없음
            if self.limit_switches[motor_index] is None:
                return False
            
            is_pressed = self.limit_switches[motor_index].is_pressed()
            # 디버깅 로그 제거로 성능 향상 (print는 1-2ms 소요)
            # if is_pressed:
            #     # print(f"  [BTN] 모터 {motor_index} 리미트 스위치 실제로 눌림!")
            return is_pressed
        return False
    
    def shift_out(self, data):
        """74HC595D에 8비트 데이터 전송"""
        # 디버깅: 첫 번째 전송에서만 출력
        if not hasattr(self, '_shift_debug_printed'):
            # print(f"  [SEARCH] 74HC595D 전송: 0x{data:02X} ({bin(data)})")
            self._shift_debug_printed = True
        
        for i in range(8):
            # MSB first
            bit = (data >> (7 - i)) & 1
            self.di.value(bit)
            
            # Shift clock pulse
            self.sh_cp.value(1)
            self.sh_cp.value(0)
        
        # Storage clock pulse (latch)
        self.st_cp.value(1)
        self.st_cp.value(0)
    
    def update_motor_output(self):
        """모든 모터 상태를 74HC595D에 출력 (test_74hc595_stepper.py와 동일)"""
        combined_data = 0

        # 모터1 → 하위 4비트 (Q0~Q3)
        combined_data |= (self.motor_states[1] & 0x0F)

        # 모터2 → 상위 4비트 (Q4~Q7)
        combined_data |= ((self.motor_states[2] & 0x0F) << 4)

        # 모터3 → 두 번째 칩 하위 4비트 (Q0~Q3 of 2번 74HC595)
        combined_data |= ((self.motor_states[3] & 0x0F) << 8)

        # 모터4 → 두 번째 칩 상위 4비트 (Q4~Q7 of 2번 74HC595)
        combined_data |= ((self.motor_states[4] & 0x0F) << 12)

        # 전송 (상위 바이트 먼저)
        upper_byte = (combined_data >> 8) & 0xFF
        lower_byte = combined_data & 0xFF

        # 디버깅: 모터 상태 출력 (첫 번째 호출에서만)
        if not hasattr(self, '_debug_printed'):
            # print(f"  [SEARCH] 모터 상태: {[hex(self.motor_states[i]) for i in range(4)]}")
            # print(f"  [SEARCH] 모터 스텝: {self.motor_steps}")
            # print(f"  [SEARCH] 출력 데이터: 0x{upper_byte:02X} 0x{lower_byte:02X}")
            self._debug_printed = True

        self.shift_out(upper_byte)
        self.shift_out(lower_byte)
    
    def set_motor_step(self, motor_index, step_value):
        """특정 모터의 스텝 설정 (test_74hc595_stepper.py와 동일)"""
        if 1 <= motor_index <= 4:
            self.motor_states[motor_index] = self.stepper_sequence[step_value % 8]
            self.update_motor_output()
    
    def step_motor(self, motor_index, direction=1, steps=1):
        """스테퍼모터 회전 (test_74hc595_stepper.py와 동일)"""
        if 1 <= motor_index <= 4:
            for _ in range(steps):
                # 리미트 스위치 확인
                if self.is_limit_switch_pressed(motor_index):
                    # print(f"모터 {motor_index} 리미트 스위치 감지! 회전 중단")
                    return False
                
                # 각 모터의 독립적인 스텝 계산 (test_74hc595_stepper.py와 동일)
                self.motor_steps[motor_index] = (self.motor_steps[motor_index] + direction) % 8
                current_step = self.motor_steps[motor_index]
                
                # 모터 스텝 설정
                self.set_motor_step(motor_index, current_step)
                
                # 회전 속도 조절 (test_74hc595_stepper.py와 동일)
                time.sleep_us(self.step_delay_us)
            
            # 항상 성공으로 반환 (리미트 스위치 비활성화)
            return True
    
    def step_motor_continuous(self, motor_index, direction=1, steps=1):
        """스테퍼모터 회전 (리미트 스위치 감지되어도 계속 회전) - 최적화된 성능"""
        if 1 <= motor_index <= 4:
            # 디버깅 로그 제거로 성능 향상
            # # print(f"    [TOOL] 모터 {motor_index} 연속 회전 시작: {steps}스텝")
            
            for i in range(steps):
                # 각 모터의 독립적인 스텝 계산 (test_74hc595_stepper.py와 동일)
                self.motor_steps[motor_index] = (self.motor_steps[motor_index] + direction) % 8
                current_step = self.motor_steps[motor_index]
                
                # 모터 스텝 설정
                self.set_motor_step(motor_index, current_step)
                
                # 진행 상황 출력 제거 (성능 향상)
                # if i % 50 == 0 or i == steps - 1:
                #     # print(f"      📍 모터 {motor_index} 스텝 {i+1}/{steps}: 시퀀스={current_step}, 상태=0x{self.motor_states[motor_index]:02X}")
                
                # 회전 속도 조절 (test_74hc595_stepper.py와 동일)
                time.sleep_us(self.step_delay_us)
            
            # 디버깅 로그 제거
            # # print(f"    [OK] 모터 {motor_index} 연속 회전 완료")
            return True
        else:
            # print(f"    [ERROR] 잘못된 모터 인덱스: {motor_index} (1-4 범위여야 함)")
            return False
    
    def stop_motor(self, motor_index):
        """모터 정지 (코일 OFF)"""
        if 1 <= motor_index <= 4:
            self.motor_states[motor_index] = 0x00  # 모든 코일 OFF
            self.update_motor_output()
            # print(f"모터 {motor_index} 정지 (코일 OFF)")
    
    def stop_all_motors(self):
        """모든 모터 정지 (모든 코일 OFF)"""
        for i in range(1, 5):  # 모터 1,2,3,4
            self.motor_states[i] = 0x00  # 모든 코일 OFF
        self.update_motor_output()
        # print("모든 모터 정지 (모든 코일 OFF)")
    
    def set_speed(self, delay_ms):
        """모터 속도 설정"""
        if delay_ms < 0.001:
            delay_ms = 0.001  # 최소 0.001ms
        elif delay_ms > 100:
            delay_ms = 100  # 최대 100ms
        
        self.step_delay_us = int(delay_ms * 1000)  # 마이크로초 단위로 저장
        frequency = 1000000 / self.step_delay_us
        # print(f"모터 속도 설정: {delay_ms}ms 지연 ({frequency:.0f}Hz)")
    
    def get_speed(self):
        """현재 모터 속도 반환"""
        delay_ms = self.step_delay_us / 1000
        frequency = 1000000 / self.step_delay_us
        return delay_ms, frequency
    
    def calibrate_motor(self, motor_index):
        """모터 원점 보정"""
        if 1 <= motor_index <= 4:
            # print(f"모터 {motor_index} 원점 보정 시작...")
            
            # 회전하면서 리미트 스위치 감지
            while not self.is_limit_switch_pressed(motor_index):
                self.step_motor(motor_index, -1, 1)  # 반시계 방향으로 1스텝
            
            # 원점 위치 설정
            self.motor_positions[motor_index] = 0
            self.motor_steps[motor_index] = 0
            # print(f"모터 {motor_index} 원점 보정 완료")
            return True
        
        return False
    
    def calibrate_multiple_motors(self, motor_indices):
        """여러 모터 동시 원점 보정"""
        # print(f"모터 {motor_indices} 동시 원점 보정 시작...")
        
        # 모든 모터를 먼저 정지
        self.stop_all_motors()
        
        # 보정할 모터들의 상태 추적
        calibration_done = [False] * len(motor_indices)
        
        # 모든 모터가 보정될 때까지 반복
        while not all(calibration_done):
            # 각 모터별로 1스텝씩 진행
            for i, motor_index in enumerate(motor_indices):
                if not calibration_done[i]:
                    # 리미트 스위치 확인
                    if self.is_limit_switch_pressed(motor_index):
                        # 이 모터는 보정 완료
                        calibration_done[i] = True
                        self.motor_positions[motor_index] = 0
                        self.motor_steps[motor_index] = 0
                        # print(f"[OK] 모터 {motor_index} 원점 보정 완료")
                    else:
                        # 이 모터는 1스텝 진행 (시계방향)
                        self.motor_steps[motor_index] = (self.motor_steps[motor_index] + 1) % 8
                        current_step = self.motor_steps[motor_index]
                        self.motor_states[motor_index] = self.stepper_sequence[current_step]
            
            # 모든 모터 상태를 한 번에 출력
            self.update_motor_output()
            
            # 회전 속도 조절
            time.sleep_us(self.step_delay_us)
        
        # 모든 모터 정지
        self.stop_all_motors()
        # print(f"모터 {motor_indices} 동시 원점 보정 완료!")
        return True
    
    def move_to_compartment(self, motor_index, compartment):
        """특정 칸으로 이동"""
        if 1 <= motor_index <= 3 and 0 <= compartment <= 14:
            current_pos = self.motor_positions[motor_index]
            steps_needed = (compartment - current_pos) * self.steps_per_compartment
            
            if steps_needed != 0:
                direction = 1 if steps_needed > 0 else -1
                steps = abs(steps_needed)
                
                # print(f"모터 {motor_index}: 칸 {current_pos} → 칸 {compartment} ({steps}스텝)")
                
                # 8스텝씩 나누어서 실행
                for i in range(0, steps, 8):
                    remaining_steps = min(8, steps - i)
                    if not self.step_motor(motor_index, direction, remaining_steps):
                        # print(f"모터 {motor_index} 이동 중단됨 (리미트 스위치)")
                        return False
                
                self.motor_positions[motor_index] = compartment
                # print(f"모터 {motor_index} 칸 {compartment} 이동 완료")
            
            return True
        
        return False
    
    def next_compartment(self, motor_index):
        """다음 칸으로 이동 - 리미트 스위치 기반 (리미트 해제 후 재감지)"""
        if 1 <= motor_index <= 4:
            # print(f"  [RETRY] 모터 {motor_index} 리미트 스위치 기반 이동 시작")
            
            # 리미트 스위치 기반 이동: 리미트가 떼어졌다가 다시 눌릴 때 정지
            step_count = 0
            limit_released = False  # 리미트 스위치 해제 상태
            
            # print(f"  📍 모터 {motor_index} 리미트 스위치 대기 중...")
            
            # 리미트 스위치가 떼어졌다가 다시 눌릴 때까지 회전
            while True:
                # 1스텝씩 이동 (정방향) - 배출시 정방향 회전으로 수정
                self.motor_steps[motor_index] = (self.motor_steps[motor_index] + 1) % 8
                current_step = self.motor_steps[motor_index]
                self.motor_states[motor_index] = self.stepper_sequence[current_step]
                self.update_motor_output()
                
                # 최대 속도
                time.sleep_us(500)  # 0.5ms - 최대 속도
                step_count += 1
                
                # 리미트 스위치 상태 확인
                is_pressed = self.is_limit_switch_pressed(motor_index)
                
                if not is_pressed and not limit_released:
                    # 리미트 스위치가 떼어짐 - 계속 진행
                    # print(f"  [BTN] 모터 {motor_index} 리미트 스위치 해제됨 (계속 진행)")
                    limit_released = True
                elif is_pressed and limit_released:
                    # 리미트 스위치가 다시 눌림 - 1칸 이동 완료
                    # print(f"  [BTN] 모터 {motor_index} 리미트 스위치 재감지! 1칸 이동 완료")
                    break
                
                # 진행 상황 출력 (20스텝마다)
                if step_count % 20 == 0:
                    # print(f"    📍 모터 {motor_index} 진행: {step_count}스텝 (리미트 대기)")
                    pass
            
            # 1칸 이동 완료 (리미트 스위치 해제 후 재감지)
            # print(f"  [OK] 모터 {motor_index} 1칸 이동 완료 ({step_count}스텝, 리미트 스위치 기반)")
            self.motor_positions[motor_index] = (self.motor_positions[motor_index] + 1) % 10
            return True
        return False
    
    def get_motor_position(self, motor_index):
        """모터의 현재 칸 위치 반환"""
        if 1 <= motor_index <= 4:
            return self.motor_positions[motor_index]
        return -1
    
    def get_motor_info(self):
        """모든 모터 정보 반환"""
        info = {
            'positions': self.motor_positions.copy(),
            'steps': self.motor_steps.copy(),
            'speed': self.get_speed(),
            'limit_switches': self.check_limit_switches()
        }
        return info
    
    def test_motor_simple(self, motor_index, steps=10):
        """간단한 모터 테스트 - 리미트 스위치 없이"""
        if 1 <= motor_index <= 4:
            # print(f"  🧪 모터 {motor_index} 간단 테스트 시작 ({steps}스텝)")
            
            # 디버깅 플래그 리셋
            if hasattr(self, '_debug_printed'):
                delattr(self, '_debug_printed')
            if hasattr(self, '_shift_debug_printed'):
                delattr(self, '_shift_debug_printed')
            
            # 모터 3 특별 디버깅
            if motor_index == 3:
                # print(f"  [SEARCH] 모터 3 하드웨어 연결 확인:")
                # print(f"    - 74HC595D 핀: DI={self.di}, SH_CP={self.sh_cp}, ST_CP={self.st_cp}")
                # print(f"    - 초기 상태: {[hex(self.motor_states[i]) for i in range(4)]}")
                # print(f"    - 초기 스텝: {self.motor_steps}")
                # print(f"    - 스텝 시퀀스: {[hex(seq) for seq in self.stepper_sequence]}")
                # print(f"    - 모터 3는 두 번째 74HC595D의 상위 4비트 (Q4~Q7)")
                # print(f"    - 예상 출력: 0xC0 0x00 (모터 3만 활성화)")
                # print(f"    - 1000스텝 테스트: 약 {1000/8}회 완전 회전 예상")
                pass
            
            for step in range(steps):
                # 1스텝씩 이동 (역방향)
                self.motor_steps[motor_index] = (self.motor_steps[motor_index] - 1) % 8
                current_step = self.motor_steps[motor_index]
                self.motor_states[motor_index] = self.stepper_sequence[current_step]
                self.update_motor_output()
                
                # 최대 속도
                time.sleep_us(500)  # 0.5ms - 최대 속도
                
                # 진행 상황 출력 (1000스텝일 때는 100스텝마다)
                if steps >= 1000:
                    if step % 100 == 0:
                        # print(f"    📍 모터 {motor_index} 스텝: {step+1}/{steps} (시퀀스: {current_step}, 상태: 0x{self.motor_states[motor_index]:02X})")
                        pass
                else:
                    if step % 2 == 0:
                        # print(f"    📍 모터 {motor_index} 스텝: {step+1}/{steps} (시퀀스: {current_step}, 상태: 0x{self.motor_states[motor_index]:02X})")
                        pass
                    
                    # 모터 3 특별 디버깅
                    if motor_index == 3:
                        # print(f"      [SEARCH] 모터 3 상태: {[hex(self.motor_states[i]) for i in range(4)]}")
                        pass
            
            # print(f"  [OK] 모터 {motor_index} 테스트 완료")
            return True
        return False

class PillBoxMotorSystem:
    """필박스 모터 시스템 관리 클래스"""
    
    def __init__(self):
        """필박스 모터 시스템 초기화"""
        self.motor_controller = StepperMotorController()
        
        # 필박스 설정
        self.num_disks = 3  # 3개 디스크 (모터 1,2,3)
        self.compartments_per_disk = 15  # 디스크당 15칸
        
        # print("[OK] PillBoxMotorSystem 초기화 완료")
    
    def calibrate_all_disks(self):
        """모든 디스크 원점 보정"""
        # print("모든 디스크 원점 보정 시작...")
        
        for i in range(1, self.num_disks + 1):  # 모터 1,2,3
            if not self.motor_controller.calibrate_motor(i):
                # print(f"디스크 {i} 보정 실패")
                return False
        
        # print("모든 디스크 보정 완료!")
        return True
    
    def calibrate_all_disks_simultaneous(self):
        """모든 디스크 동시 원점 보정"""
        # print("모든 디스크 동시 원점 보정 시작...")
        
        # 모터 1, 2, 3을 동시에 보정
        if self.motor_controller.calibrate_multiple_motors([1, 2, 3]):
            # print("모든 디스크 동시 보정 완료!")
            return True
        else:
            # print("디스크 동시 보정 실패")
            return False
    
    def load_pills(self, disk_index, compartments=3):
        """알약 충전 (3칸씩 회전)"""
        if 1 <= disk_index <= self.num_disks:
            # print(f"디스크 {disk_index} 알약 충전 시작 ({compartments}칸 회전)")
            
            for i in range(compartments):
                if not self.motor_controller.next_compartment(disk_index):
                    # print(f"디스크 {disk_index} 충전 중단됨")
                    return False
                time.sleep_ms(500)  # 각 칸마다 잠시 대기
            
            # print(f"디스크 {disk_index} 알약 충전 완료")
            
            # 동작 완료 후 코일 OFF
            self.motor_controller.stop_motor(disk_index)
            return True
        
        return False
    
    def dispense_pills(self, disk_index, compartment=None):
        """알약 배출"""
        if 1 <= disk_index <= self.num_disks:
            if compartment is None:
                # 현재 칸에서 배출
                compartment = self.motor_controller.get_motor_position(disk_index)
            
            # print(f"디스크 {disk_index} 칸 {compartment}에서 알약 배출")
            
            # 해당 칸으로 이동
            if self.motor_controller.move_to_compartment(disk_index, compartment):
                # print(f"디스크 {disk_index} 칸 {compartment} 배출 완료")
                
                # 동작 완료 후 코일 OFF
                self.motor_controller.stop_motor(disk_index)
                return True
            else:
                # print(f"디스크 {disk_index} 배출 실패")
                
                # 실패 시에도 코일 OFF
                self.motor_controller.stop_motor(disk_index)
                return False
        
        return False
    
    def get_disk_status(self):
        """모든 디스크 상태 반환"""
        status = {}
        motor_info = self.motor_controller.get_motor_info()
        
        for i in range(self.num_disks):
            status[f'disk_{i}'] = {
                'position': motor_info['positions'][i],
                'steps': motor_info['steps'][i],
                'limit_switch': motor_info['limit_switches'][i]
            }
        
        return status
    
    def emergency_stop(self):
        """비상 정지 (모든 모터 HIGH 상태로 설정)"""
        # print("비상 정지 실행!")
        self.motor_controller.stop_all_motors()
    
    def turn_off_all_motor_coils(self):
        """모든 모터 코일 OFF"""
        # print("모든 모터 코일 OFF")
        self.motor_controller.turn_off_all_coils()

    def control_dispense_slide(self, level):
        """배출구 슬라이드 제어 (디스크 모터와 동일한 로직)"""
        try:
            if level < 0 or level > 3:
                # print(f"[ERROR] 잘못된 슬라이드 레벨: {level} (0-3 범위)")
                return False
            
            # 배출구 슬라이드 모터 (모터 3) 제어
            motor_index = 3
            
            if level == 0:
                # 닫기: 0도 (원점)
                steps = 0
                # print("🚪 배출구 슬라이드 닫기 (0도)")
            elif level == 1:
                # 1단: 120도 (28BYJ-48 기준 정확한 스텝수)
                steps = 683  # 2048 ÷ 360° × 120° = 683스텝
                # print("🚪 배출구 슬라이드 1단 (120도 - 683스텝)")
            elif level == 2:
                # 2단: 240도 (28BYJ-48 기준 정확한 스텝수)
                steps = 1365  # 2048 ÷ 360° × 240° = 1365스텝
                # print("🚪 배출구 슬라이드 2단 (240도 - 1365스텝)")
            elif level == 3:
                # 3단: 360도 (28BYJ-48 기준 정확한 스텝수)
                steps = 2048  # 2048 ÷ 360° × 360° = 2048스텝 (한 바퀴)
                # print("🚪 배출구 슬라이드 3단 (360도 - 2048스텝)")
            
            # 배출구 모터 우선순위 모드 - 디스크 모터와 동일한 부드러운 동작
            # print(f"  [RETRY] 모터 {motor_index}를 {steps}스텝으로 이동... (우선순위 모드)")
            # print(f"  [FAST] 모터 {motor_index} 우선순위 모드 활성화")
            # print(f"  [SEARCH] 배출구 모터 디버깅:")
            # print(f"    - 모터 인덱스: {motor_index}")
            # print(f"    - 이동할 스텝: {steps}")
            # print(f"    - 현재 모터 상태: {[hex(self.motor_controller.motor_states[i]) for i in range(4)]}")
            
            # test_74hc595_stepper.py와 동일한 방식: step_motor 함수 사용
            # print(f"  [RETRY] 모터 {motor_index}를 {steps}스텝으로 이동... (step_motor 방식)")
            
            # 8스텝씩 처리 (test 파일과 동일)
            for i in range(0, steps, 8):
                remaining_steps = min(8, steps - i)
                if i % 100 == 0 or i == steps - 8:  # 100스텝마다 진행 상황 출력
                    # print(f"    📍 배출구 슬라이드 {i+1}/{steps}스텝 진행 중...")
                    pass
                # step_motor 함수 사용 (test 파일과 동일)
                success = self.motor_controller.step_motor(motor_index, 1, remaining_steps)
                if not success:
                    # print(f"    [ERROR] 모터 {motor_index} 회전 중단됨")
                    return False
            
            # print(f"  [SEARCH] 배출구 모터 이동 후:")
            # print(f"    - 이동 후 모터 상태: {[hex(self.motor_controller.motor_states[i]) for i in range(4)]}")
            # print(f"    - 모터 스텝: {self.motor_controller.motor_steps}")
            
            if not success:
                # print(f"    [ERROR] 배출구 슬라이드 {steps}스텝 이동 실패")
                # 실패 시에도 코일 OFF
                self.motor_controller.stop_motor(motor_index)
                return False
            
            # print(f"  [OK] 배출구 슬라이드 {steps}스텝 이동 완료")
            # 동작 완료 후 코일 OFF
            self.motor_controller.stop_motor(motor_index)
            return True
            
        except Exception as e:
            # print(f"[ERROR] 배출구 슬라이드 제어 실패: {e}")
            return False
    
    def control_dispense_slide_close(self, level):
        """배출구 슬라이드 닫힘 제어 (열린 각도와 동일하게 역회전)"""
        try:
            if level < 0 or level > 3:
                # print(f"[ERROR] 잘못된 슬라이드 레벨: {level} (0-3 범위)")
                return False
            
            # 배출구 슬라이드 모터 (모터 3) 제어
            motor_index = 3
            
            if level == 0:
                # 닫기: 0도 (원점)
                steps = 0
                # print("🚪 배출구 슬라이드 닫기 (0도)")
            elif level == 1:
                # 1단: 120도 역회전 (28BYJ-48 기준 정확한 스텝수)
                steps = 683  # 2048 ÷ 360° × 120° = 683스텝
                # print("🚪 배출구 슬라이드 1단 역회전 (120도 - 683스텝)")
            elif level == 2:
                # 2단: 240도 역회전 (28BYJ-48 기준 정확한 스텝수)
                steps = 1365  # 2048 ÷ 360° × 240° = 1365스텝
                # print("🚪 배출구 슬라이드 2단 역회전 (240도 - 1365스텝)")
            elif level == 3:
                # 3단: 360도 역회전 (28BYJ-48 기준 정확한 스텝수)
                steps = 2048  # 2048 ÷ 360° × 360° = 2048스텝 (한 바퀴)
                # print("🚪 배출구 슬라이드 3단 역회전 (360도 - 2048스텝)")
            
            # 배출구 모터 우선순위 모드 - 역회전으로 닫기
            # print(f"  [RETRY] 모터 {motor_index}를 {steps}스텝으로 역회전... (우선순위 모드)")
            # print(f"  [FAST] 모터 {motor_index} 우선순위 모드 활성화 (역회전)")
            # print(f"  [SEARCH] 배출구 모터 역회전 디버깅:")
            # print(f"    - 모터 인덱스: {motor_index}")
            # print(f"    - 역회전할 스텝: {steps}")
            # print(f"    - 현재 모터 상태: {[hex(self.motor_controller.motor_states[i]) for i in range(4)]}")
            
            # test_74hc595_stepper.py와 동일한 방식: step_motor 함수 사용 (역방향)
            # print(f"  [RETRY] 모터 {motor_index}를 {steps}스텝으로 역회전... (step_motor 방식)")
            
            # 8스텝씩 처리 (test 파일과 동일)
            for i in range(0, steps, 8):
                remaining_steps = min(8, steps - i)
                if i % 100 == 0 or i == steps - 8:  # 100스텝마다 진행 상황 출력
                    # print(f"    📍 배출구 슬라이드 역회전 {i+1}/{steps}스텝 진행 중...")
                    pass
                # step_motor 함수 사용 (test 파일과 동일, 역방향: -1)
                success = self.motor_controller.step_motor(motor_index, -1, remaining_steps)
                if not success:
                    # print(f"    [ERROR] 모터 {motor_index} 역회전 중단됨")
                    return False
            
            # print(f"  [SEARCH] 배출구 모터 역회전 후:")
            # print(f"    - 역회전 후 모터 상태: {[hex(self.motor_controller.motor_states[i]) for i in range(4)]}")
            # print(f"    - 모터 스텝: {self.motor_controller.motor_steps}")
            
            if not success:
                # print(f"    [ERROR] 배출구 슬라이드 {steps}스텝 역회전 실패")
                # 실패 시에도 코일 OFF
                self.motor_controller.stop_motor(motor_index)
                return False
            
            # print(f"  [OK] 배출구 슬라이드 {steps}스텝 역회전 완료")
            # 동작 완료 후 코일 OFF
            self.motor_controller.stop_motor(motor_index)
            return True
            
        except Exception as e:
            # print(f"[ERROR] 배출구 슬라이드 닫힘 제어 실패: {e}")
            return False
    
    def get_dispense_slide_position(self):
        """배출구 슬라이드 현재 위치 반환"""
        try:
            motor_index = 3
            current_steps = self.motor_controller.motor_steps[motor_index]
            
            # 스텝 수에 따른 레벨 계산 (400스텝/회전 모터 기준)
            if current_steps < 67:  # 0-66 스텝
                return 0  # 닫힘
            elif current_steps < 133:  # 67-132 스텝
                return 1  # 1단 (120도)
            elif current_steps < 267:  # 133-266 스텝
                return 2  # 2단
            else:  # 267+ 스텝
                return 3  # 3단 (360도)
                
        except Exception as e:
            # print(f"[ERROR] 배출구 슬라이드 위치 확인 실패: {e}")
            return 0
    
    def test_motor3_only(self, steps=200):
        """모터 3 전용 테스트 (배출구 슬라이드)"""
        # print(f"[TOOL] 모터 3 전용 테스트 시작 ({steps}스텝)")
        
        try:
            motor_index = 3
            
            # 모터 3 초기화
            self.motor_controller.motor_states[motor_index] = 0x00
            self.motor_controller.motor_steps[motor_index] = 0
            self.motor_controller.update_motor_output()
            
            # print(f"  [SEARCH] 모터 3 초기 상태:")
            # print(f"    - 모터 상태: {[hex(self.motor_controller.motor_states[i]) for i in range(4)]}")
            # print(f"    - 모터 스텝: {self.motor_controller.motor_steps}")
            # print(f"    - 74HC595D 핀: DI={self.motor_controller.di}, SH_CP={self.motor_controller.sh_cp}, ST_CP={self.motor_controller.st_cp}")
            # print(f"    - 모터 3는 두 번째 74HC595D의 상위 4비트 (Q4~Q7)")
            # print(f"    - 예상 출력: 0xC0 0x00 (모터 3만 활성화)")
            
            # 단계별 이동 (회전 방향 반대)
            for step in range(steps):
                # 1스텝씩 이동 (역방향)
                self.motor_controller.motor_steps[motor_index] = (self.motor_controller.motor_steps[motor_index] - 1) % 8
                current_step = self.motor_controller.motor_steps[motor_index]
                self.motor_controller.motor_states[motor_index] = self.motor_controller.stepper_sequence[current_step]
                self.motor_controller.update_motor_output()
                
                # 속도 조절 (모터 3은 더 느리게)
                time.sleep_us(200)  # 0.2ms 지연 (test 파일과 동일)
                
                # 진행 상황 출력 (5스텝마다)
                if step % 5 == 0:
                    # print(f"    📍 모터 3 스텝: {step+1}/{steps} (시퀀스: {current_step}, 상태: 0x{self.motor_controller.motor_states[motor_index]:02X})")
                    # print(f"    [SEARCH] 전체 모터 상태: {[hex(self.motor_controller.motor_states[i]) for i in range(4)]}")
                    pass
            # print(f"  [OK] 모터 3 테스트 완료")
            # 동작 완료 후 코일 OFF
            self.motor_controller.stop_motor(motor_index)
            return True
            
        except Exception as e:
            # print(f"  [ERROR] 모터 3 테스트 실패: {e}")
            # 실패 시에도 코일 OFF
            self.motor_controller.stop_motor(motor_index)
            return False
    
    def rotate_disk(self, disk_num, steps):
        """디스크 회전 (실제 하드웨어 제어) - 우선순위 모드"""
        try:
            # print(f"  [RETRY] 디스크 {disk_num} 회전: {steps} 스텝 (우선순위 모드)")
            
            # 디스크 번호는 1-3, 모터 번호는 1-3
            motor_num = disk_num
            
            if 1 <= motor_num <= 3:
                # 모터 우선순위 모드 - 다른 작업 중단
                # print(f"  [FAST] 모터 {motor_num} 우선순위 모드 활성화")
                
                # 실제 하드웨어 제어: 리미트 스위치 기반 1칸씩 이동
                for i in range(steps):
                    # print(f"    📍 디스크 {disk_num} {i+1}/{steps}칸 이동 중...")
                    
                    # 다음 칸으로 이동 (리미트 스위치 기반) - 블로킹 모드
                    success = self.motor_controller.next_compartment(motor_num)
                    
                    if not success:
                        # print(f"    [ERROR] 디스크 {disk_num} {i+1}칸 이동 실패")
                        return False
                    
                    # 각 칸 이동 후 잠시 대기 (약이 떨어질 시간)
                    time.sleep_ms(500)
                
                # print(f"  [OK] 디스크 {disk_num} {steps}칸 회전 완료")
                # 동작 완료 후 코일 OFF
                self.motor_controller.stop_motor(motor_num)
                return True
            else:
                # print(f"  [ERROR] 잘못된 디스크 번호: {disk_num}")
                return False
                
        except Exception as e:
            # print(f"  [ERROR] 디스크 회전 실패: {e}")
            # 실패 시에도 코일 OFF
            if 1 <= motor_num <= 3:
                self.motor_controller.stop_motor(motor_num)
            return False
    
    
    def control_motor3_direct(self, level=1):
        """모터 4 직접 제어 (배출구 슬라이드 - 4096스텝/360도 기준)"""
        try:
            # print(f"🚫 모터 4 블로킹 모드 시작 - 다른 프로세스 중단")
            
            # [FAST] 모터 4 사용 전 모든 모터 전원 OFF
            # print(f"  [FAST] 모터 4 사용 전 모든 모터 전원 OFF")
            self.motor_controller.stop_all_motors()
            # print(f"  [OK] 모든 모터 전원 OFF 완료")
            
            # 모터 4 (배출구 슬라이드) 레벨별 제어
            motor_index = 4
            
            # 4096스텝/360도 기준으로 각 레벨별 스텝 계산
            if level == 1:
                steps = 1593  # 140도 = 4096 ÷ 360° × 140° = 1593스텝
                degrees = 140
                # print(f"  [TOOL] 모터 4 배출구 1단계: {degrees}도 ({steps}스텝)")
            elif level == 2:
                steps = 3187  # 280도 = 4096 ÷ 360° × 280° = 3187스텝
                degrees = 280
                # print(f"  [TOOL] 모터 4 배출구 2단계: {degrees}도 ({steps}스텝)")
            elif level == 3:
                steps = 4781  # 420도 = 4096 ÷ 360° × 420° = 4781스텝
                degrees = 420
                # print(f"  [TOOL] 모터 4 배출구 3단계: {degrees}도 ({steps}스텝)")
            else:
                # print(f"[ERROR] 잘못된 배출구 레벨: {level} (1-3 범위)")
                return False
            
            # print(f"  [WARN] 모터 동작 중 - UI 업데이트 및 다른 프로세스 중단")
            
            # 1단계: 역방향 회전 (열림)
            # print(f"  📍 1단계: 역방향 {degrees}도 회전 시작...")
            success = self._rotate_motor3_steps(motor_index, -1, steps)
            if not success:
                # print(f"    [ERROR] 모터 4 역방향 회전 실패")
                return False
            
            # 약이 떨어질 시간 대기
            # print(f"  ⏳ 약이 떨어질 시간 대기 (2초)...")
            time.sleep(2)
            
            # 2단계: 정방향 회전 (원위치)
            # print(f"  📍 2단계: 정방향 {degrees}도 회전 시작...")
            success = self._rotate_motor3_steps(motor_index, 1, steps)
            if not success:
                # print(f"    [ERROR] 모터 4 정방향 회전 실패")
                return False
            
            # [FAST] 모터 4 사용 후 모든 모터 전원 OFF
            # print(f"  [FAST] 모터 4 사용 후 모든 모터 전원 OFF")
            self.motor_controller.stop_all_motors()
            # print(f"  [OK] 모든 모터 전원 OFF 완료")
            
            # print(f"  [OK] 모터 4 배출구 {level}단계 완료 ({degrees}도 × 2 = {steps * 2}스텝)")
            # print(f"🚫 모터 4 블로킹 모드 종료 - 다른 프로세스 재개 가능")
            return True
            
        except Exception as e:
            # print(f"[ERROR] 모터 4 배출구 제어 실패: {e}")
            # [FAST] 예외 발생 시에도 모든 모터 전원 OFF
            try:
                # print(f"  [FAST] 예외 발생 시 모든 모터 전원 OFF")
                self.motor_controller.stop_all_motors()
                # print(f"  [OK] 모든 모터 전원 OFF 완료")
            except:
                pass
            # print(f"🚫 모터 4 블로킹 모드 종료 (예외)")
            return False
    
    def _rotate_motor3_steps(self, motor_index, direction, steps):
        """모터 4 스텝 회전 (내부 함수)"""
        try:
            total_steps = steps
            for i in range(0, total_steps, 8):
                remaining_steps = min(8, total_steps - i)
                
                # 진행 상황 출력 (100스텝마다만)
                if i % 100 == 0 or i == total_steps - 8:
                    # print(f"    📍 모터 4 {i+1}/{total_steps}스텝 진행 중...")
                    pass
                # step_motor 함수 사용 - 완전 블로킹
                success = self.motor_controller.step_motor(motor_index, direction, remaining_steps)
                if not success:
                    # print(f"    [ERROR] 모터 4 회전 중단됨")
                    return False
            
            return True
            
        except Exception as e:
            # print(f"[ERROR] 모터 4 스텝 회전 실패: {e}")
            return False
    
    def home_motor(self, disk_index):
        """디스크 홈 포지션 찾기 (기존 calibrate_motor 방식 사용)"""
        try:
            # 디스크 인덱스(0,1,2)를 모터 인덱스(1,2,3)로 변환
            motor_index = disk_index + 1
            
            # print(f"  [INFO] 디스크 {disk_index} (모터 {motor_index}) 홈 포지션 찾기 시작...")
            
            # 기존 calibrate_motor 메서드 사용
            success = self.motor_controller.calibrate_motor(motor_index)
            
            if success:
                # print(f"  [OK] 디스크 {disk_index} 홈 포지션 찾기 완료")
                return True
            else:
                # print(f"  [ERROR] 디스크 {disk_index} 홈 포지션 찾기 실패")
                return False
            
        except Exception as e:
            # print(f"  [ERROR] 디스크 {disk_index} 홈 포지션 찾기 실패: {e}")
            import sys
            sys.print_exception(e)
            return False
    