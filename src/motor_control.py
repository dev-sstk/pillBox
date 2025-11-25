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
    
    def shift_out(self, data, latch=True):
        """74HC595D에 8비트 데이터 전송 (타이밍 안정화 버전)
        
        Args:
            data: 전송할 8비트 데이터
            latch: True이면 latch 수행, False이면 시프트만 수행 (기본값: True)
        """
        # 디버깅: 첫 번째 전송에서만 출력
        if not hasattr(self, '_shift_debug_printed'):
            # print(f"  [SEARCH] 74HC595D 전송: 0x{data:02X} ({bin(data)})")
            self._shift_debug_printed = True
        
        for i in range(8):
            # MSB first
            bit = (data >> (7 - i)) & 1
            self.di.value(bit)
            time.sleep_us(1)  # 타이밍 안정화를 위한 딜레이
            
            # Shift clock pulse (타이밍 안정화)
            self.sh_cp.value(1)
            time.sleep_us(1)  # 타이밍 안정화를 위한 딜레이
            self.sh_cp.value(0)
            time.sleep_us(1)  # 타이밍 안정화를 위한 딜레이
        
        # Storage clock pulse (latch) - latch=True일 때만 수행
        if latch:
            self.st_cp.value(1)
            time.sleep_us(1)  # 타이밍 안정화를 위한 딜레이
            self.st_cp.value(0)
            time.sleep_us(1)  # 타이밍 안정화를 위한 딜레이
    
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
        
        # print(f"    [MOTOR] 상태: {[hex(self.motor_states[i]) for i in range(1, 4)]}")
        # print(f"    [MOTOR] 출력: 0x{upper_byte:02X} 0x{lower_byte:02X}")

        # 디버깅: 모터 상태 출력 (첫 번째 호출에서만)
        # if not hasattr(self, '_debug_printed'):
        #     # print(f"  [SEARCH] 모터 상태: {[hex(self.motor_states[i]) for i in range(4)]}")
        #     # print(f"  [SEARCH] 모터 스텝: {self.motor_steps}")
        #     # print(f"  [SEARCH] 출력 데이터: 0x{upper_byte:02X} 0x{lower_byte:02X}")
        #     self._debug_printed = True

        # 상위 바이트 전송 (모터 3, 4 포함) - 두 번째 칩으로 전송
        # 시프트 레지스터 체인에서는 모든 데이터를 먼저 시프트하고 마지막에 한 번만 latch
        self.shift_out(upper_byte, latch=False)  # 시프트만 수행 (latch 없음)
        # 두 번째 칩으로 데이터가 전파되는 시간 확보 (시프트 레지스터 체인 지연)
        time.sleep_us(10)  # 바이트 전송 간 추가 딜레이 (모터 4 안정화)
        
        # 하위 바이트 전송 (모터 1, 2 포함) - 첫 번째 칩으로 전송
        self.shift_out(lower_byte, latch=True)  # 마지막 바이트 시 latch 수행
        
        # Latch 후 안정화 시간 (모든 출력 핀이 안정화될 때까지 대기)
        time.sleep_us(10)  # 최종 출력 안정화를 위한 추가 딜레이 (모터 4 포함)
    
    def set_motor_step(self, motor_index, step_value, update_output=True):
        """특정 모터의 스텝 설정 (test_74hc595_stepper.py와 동일)"""
        if 1 <= motor_index <= 4:
            self.motor_states[motor_index] = self.stepper_sequence[step_value % 8]
            if update_output:
                self.update_motor_output()
    
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
    
    def step_all_motors_simultaneous(self, directions, steps=1):
        """모든 모터를 동시에 회전 (한번의 패킷으로 모든 모터 제어) - 최적화된 성능"""
        # directions: [motor1_direction, motor2_direction, motor3_direction, motor4_direction]
        # 각 방향은 1 또는 -1
        
        for i in range(steps):
            # 모든 모터의 스텝을 동시에 계산
            for motor_idx in range(1, 5):  # 모터 1, 2, 3, 4
                if motor_idx <= len(directions):
                    direction = directions[motor_idx - 1]
                    self.motor_steps[motor_idx] = (self.motor_steps[motor_idx] + direction) % 8
                    current_step = self.motor_steps[motor_idx]
                    
                    # 모터 스텝 설정 (내부 상태만 업데이트, 아직 출력하지 않음)
                    self.set_motor_step(motor_idx, current_step, update_output=False)
            
            # 모든 모터 상태를 한번에 출력 (한번의 패킷 전송)
            self.update_motor_output()
            
            # 회전 속도 조절
            time.sleep_us(self.step_delay_us)
        
        return True
    
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
                        # 이 모터는 1스텝 진행
                        self.motor_steps[motor_index] = (self.motor_steps[motor_index] - 1) % 8
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
                # 1스텝씩 이동 (시계방향)
                self.motor_steps[motor_index] = (self.motor_steps[motor_index] - 1) % 8
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
    
    

class PillBoxMotorSystem:
    """필박스 모터 시스템 관리 클래스"""
    
    def __init__(self):
        """필박스 모터 시스템 초기화"""
        self.motor_controller = StepperMotorController()
        
        # 필박스 설정
        self.num_disks = 3  # 3개 디스크 (모터 1,2,3)
        self.compartments_per_disk = 15  # 디스크당 15칸
        
        # 도어 위치 추적 (0=닫힘, 1=1단, 2=2단, 3=3단)
        self.current_door_level = 0  # 초기 상태: 닫혀 있음
        
        # print("[OK] PillBoxMotorSystem 초기화 완료")
    
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
    
    def rotate_multiple_disks_simultaneous(self, disk_indices, steps_per_disk):
        """여러 디스크 동시 회전 (3개 디스크 동시 충전용) - 리미트 스위치 무시하고 정확히 3칸씩"""
        try:
            print(f"3개 디스크 동시 회전 시작: 디스크 {disk_indices}, 각 {steps_per_disk}칸")
            
            # 모든 모터를 먼저 정지
            self.motor_controller.stop_all_motors()
            
            # 모터 번호로 변환 (디스크 인덱스 + 1)
            motor_indices = [disk_index + 1 for disk_index in disk_indices]
            print(f"모터 번호: {motor_indices}")
            
            # 원점보정 방식으로 연속적으로 3칸씩 회전 (리미트 스위치 무시)
            print(f"  연속 동시 회전 시작: {steps_per_disk}칸")
            
            # 각 스텝마다 모든 모터를 동시에 1스텝씩 진행 (원점보정 방식)
            for step in range(steps_per_disk):
                print(f"  동시 회전 {step+1}/{steps_per_disk}칸")
                
                # 각 모터별로 1스텝씩 진행 (원점보정과 동일한 방식)
                for motor_index in motor_indices:
                    if 1 <= motor_index <= 3:
                        # 이 모터는 1스텝 진행 (리미트 스위치 확인 없이)
                        old_step = self.motor_controller.motor_steps[motor_index]
                        self.motor_controller.motor_steps[motor_index] = (self.motor_controller.motor_steps[motor_index] - 1) % 8
                        current_step = self.motor_controller.motor_steps[motor_index]
                        self.motor_controller.motor_states[motor_index] = self.motor_controller.stepper_sequence[current_step]
                        print(f"    모터 {motor_index}: {old_step} -> {current_step}, 상태: {self.motor_controller.motor_states[motor_index]}")
                
                # 모든 모터 상태를 한 번에 출력 (원점보정과 동일)
                print(f"    update_motor_output 호출")
                self.motor_controller.update_motor_output()
                
                # 회전 속도 조절 (원점보정과 동일한 속도)
                time.sleep_us(self.motor_controller.step_delay_us)
            
            # 약이 떨어질 시간 대기 (최종에만)
            time.sleep_ms(500)
            
            # 모든 모터 정지 (최종에만)
            self.motor_controller.stop_all_motors()
            print(f"3개 디스크 동시 회전 완료: 각 {steps_per_disk}칸")
            return True
            
        except Exception as e:
            # print(f"[ERROR] 3개 디스크 동시 회전 실패: {e}")
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
                for step_idx in range(steps):
                    # print(f"    📍 디스크 {disk_num} {step_idx+1}/{steps}칸 이동 중...")
                    
                    # 다음 칸으로 이동 (리미트 스위치 기반) - 블로킹 모드
                    success = self.motor_controller.next_compartment(motor_num)
                    
                    if not success:
                        # print(f"    [ERROR] 디스크 {disk_num} {step_idx+1}칸 이동 실패")
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
    
    def control_motor4_direct(self, level=1):
        """모터 4 직접 제어 (배출구 슬라이드) - 기존 호환성 유지용 (deprecated)"""
        # 기존 코드 호환성을 위해 open_door_to_level() 호출
        return self.open_door_to_level(level)
    
    def open_door_to_level(self, level):
        """도어를 지정된 레벨까지 열기 (현재 위치에서 목표 레벨로 이동, 닫지 않음)"""
        try:
            # print(f"🚪 도어 열기 시작: 현재 레벨={self.current_door_level}, 목표 레벨={level}")
            
            # [FAST] 모터 4 사용 전 모든 모터 전원 OFF
            self.motor_controller.stop_all_motors()
            
            # 모터 4 (배출구 슬라이드) 레벨별 제어
            motor_index = 4
            
            # 레벨 범위 확인
            if level < 0 or level > 3:
                # print(f"[ERROR] 잘못된 배출구 레벨: {level} (0-3 범위, 0=닫힘)")
                return False
            
            # 이미 해당 레벨에 있으면 동작하지 않음
            if self.current_door_level == level:
                # print(f"  [INFO] 도어가 이미 레벨 {level}에 있음")
                return True
            
            # 하위 단수로 내려가지 않도록 체크 (목표 레벨이 현재 레벨보다 낮으면 동작하지 않음)
            if level < self.current_door_level:
                # print(f"  [INFO] 도어가 현재 레벨 {self.current_door_level}에 있고, 목표 레벨 {level}은 하위 단수이므로 동작하지 않음")
                return True
            
            # 4096스텝/360도 기준으로 각 레벨별 누적 스텝 계산
            level_steps = {
                0: 0,      # 닫힘 (0도)
                1: 1593,   # 140도 = 4096 ÷ 360° × 140° = 1593스텝
                2: 3187,   # 280도 = 4096 ÷ 360° × 280° = 3187스텝
                3: 4781    # 420도 = 4096 ÷ 360° × 420° = 4781스텝
            }
            
            current_steps = level_steps[self.current_door_level]
            target_steps = level_steps[level]
            steps_to_move = target_steps - current_steps
            
            # print(f"  [INFO] 현재 스텝: {current_steps}, 목표 스텝: {target_steps}, 이동 스텝: {steps_to_move}")
            
            if steps_to_move == 0:
                # 이미 목표 레벨에 있음
                return True
            
            # 방향 결정 (양수=역방향(열기), 음수=정방향(닫기)) - 하드웨어에 맞게 반대 방향
            # 하위 단수로 내려가지 않도록 이미 체크했으므로 steps_to_move는 항상 양수
            direction = -1  # 열기 방향 (역방향)
            steps = steps_to_move
            
            # 도어 이동
            success = self._rotate_motor4_steps(motor_index, direction, steps)
            if not success:
                # print(f"    [ERROR] 도어 이동 실패")
                return False
            
            # 도어 위치 업데이트
            self.current_door_level = level
            # print(f"  [OK] 도어 레벨 {level}로 이동 완료")
            
            # [FAST] 모터 4 사용 후 모든 모터 전원 OFF
            self.motor_controller.stop_all_motors()
            
            return True
            
        except Exception as e:
            # print(f"[ERROR] 도어 열기 실패: {e}")
            # [FAST] 예외 발생 시에도 모든 모터 전원 OFF
            try:
                self.motor_controller.stop_all_motors()
            except:
                pass
            return False
    
    def close_door(self):
        """도어 완전히 닫기 (레벨 0으로 이동) - 강제로 닫기"""
        try:
            # print(f"🚪 도어 닫기 시작: 현재 레벨={self.current_door_level}")
            
            # [FAST] 모터 4 사용 전 모든 모터 전원 OFF
            self.motor_controller.stop_all_motors()
            
            # 모터 4 (배출구 슬라이드) 레벨별 제어
            motor_index = 4
            
            # 이미 닫혀 있으면 동작하지 않음
            if self.current_door_level == 0:
                # print(f"  [INFO] 도어가 이미 닫혀 있음")
                return True
            
            # 4096스텝/360도 기준으로 각 레벨별 누적 스텝 계산
            level_steps = {
                0: 0,      # 닫힘 (0도)
                1: 1593,   # 140도 = 4096 ÷ 360° × 140° = 1593스텝
                2: 3187,   # 280도 = 4096 ÷ 360° × 280° = 3187스텝
                3: 4781    # 420도 = 4096 ÷ 360° × 420° = 4781스텝
            }
            
            current_steps = level_steps[self.current_door_level]
            target_steps = level_steps[0]  # 닫힘 (0도)
            steps_to_move = target_steps - current_steps  # 음수 (닫기 방향)
            
            # print(f"  [INFO] 현재 스텝: {current_steps}, 목표 스텝: {target_steps}, 이동 스텝: {steps_to_move}")
            
            # 방향 결정 (양수=역방향(열기), 음수=정방향(닫기)) - 하드웨어에 맞게 반대 방향
            direction = 1  # 닫기 방향 (정방향)
            steps = abs(steps_to_move)
            
            # 도어 이동
            success = self._rotate_motor4_steps(motor_index, direction, steps)
            if not success:
                # print(f"    [ERROR] 도어 닫기 실패")
                return False
            
            # 도어 위치 업데이트
            self.current_door_level = 0
            # print(f"  [OK] 도어 닫기 완료")
            
            # [FAST] 모터 4 사용 후 모든 모터 전원 OFF
            self.motor_controller.stop_all_motors()
            
            return True
            
        except Exception as e:
            # print(f"[ERROR] 도어 닫기 실패: {e}")
            # [FAST] 예외 발생 시에도 모든 모터 전원 OFF
            try:
                self.motor_controller.stop_all_motors()
            except:
                pass
            return False
    
    def _rotate_motor4_steps(self, motor_index, direction, steps):
        """모터 4 스텝 회전 (내부 함수)"""
        try:
            total_steps = steps
            for i in range(0, total_steps, 8):
                remaining_steps = min(8, total_steps - i)
                
                # 진행 상황 출력 (100스텝마다만)
                if i % 100 == 0 or i == total_steps - 8:
                    # print(f"    📍 모터 4 {i+1}/{total_steps}스텝 진행 중...")
                    pass
                # step_motor_continuous 함수 사용 - 완전 블로킹
                success = self.motor_controller.step_motor_continuous(motor_index, direction, remaining_steps)
                if not success:
                    # print(f"    [ERROR] 모터 4 회전 중단됨")
                    return False
            
            return True
            
        except Exception as e:
            # print(f"[ERROR] 모터 4 스텝 회전 실패: {e}")
            return False