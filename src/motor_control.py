"""
스테퍼 모터 제어 시스템 (74HC595D + ULN2003 기반)
필박스의 알약 충전/배출을 위한 스테퍼 모터 제어
"""

from machine import Pin
import time
import _thread

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
        """1바이트 데이터 읽기"""
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

class LimitSwitch:
    """리미트 스위치 클래스"""
    
    def __init__(self, input_shift_register, bit_position):
        """리미트 스위치 초기화"""
        self.input_shift_register = input_shift_register
        self.bit_position = bit_position
        
    def is_pressed(self):
        """리미트 스위치가 눌렸는지 확인"""
        data = self.input_shift_register.read_byte()
        # HIGH=눌리지 않음, LOW=눌림
        return (data & (1 << self.bit_position)) == 0

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
        
        # 리미트 스위치 초기화 (74HC165D 비트 4, 5, 6, 7 사용)
        self.limit_switches = [
            LimitSwitch(self.input_shift_register, 4),  # 모터 0 리미트 스위치 (LIMIT SW1)
            LimitSwitch(self.input_shift_register, 5),  # 모터 1 리미트 스위치 (LIMIT SW2)
            LimitSwitch(self.input_shift_register, 6),  # 모터 2 리미트 스위치 (LIMIT SW3)
            LimitSwitch(self.input_shift_register, 7),  # 모터 3 리미트 스위치 (LIMIT SW4)
        ]
        
        # 스테퍼모터 설정 (28BYJ-48)
        self.steps_per_rev = 2048  # 28BYJ-48의 스텝 수
        self.steps_per_compartment = 204  # 1칸당 스텝 수 (2048/10칸)
        
        # 각 모터별 독립적인 스텝 상태
        self.motor_steps = [0, 0, 0, 0]  # 모터 0,1,2,3의 현재 스텝
        self.motor_positions = [0, 0, 0, 0]  # 각 모터의 현재 칸 위치
        
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
        self.step_delay_us = 200  # 스텝 간 지연 시간 (마이크로초)
        
        # 비블로킹 제어를 위한 변수들
        self.motor_running = [False, False, False, False]  # 각 모터별 실행 상태
        self.motor_direction = [1, 1, 1, 1]  # 각 모터별 방향
        self.last_step_times = [0, 0, 0, 0]  # 각 모터별 마지막 스텝 시간
        
        print("✅ StepperMotorController 초기화 완료")
    
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
        """74HC595D에 8비트 데이터 전송"""
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
        """모터 속도 설정"""
        if delay_ms < 0.001:
            delay_ms = 0.001  # 최소 0.001ms
        elif delay_ms > 100:
            delay_ms = 100  # 최대 100ms
        
        self.step_delay_us = int(delay_ms * 1000)  # 마이크로초 단위로 저장
        frequency = 1000000 / self.step_delay_us
        print(f"모터 속도 설정: {delay_ms}ms 지연 ({frequency:.0f}Hz)")
    
    def get_speed(self):
        """현재 모터 속도 반환"""
        delay_ms = self.step_delay_us / 1000
        frequency = 1000000 / self.step_delay_us
        return delay_ms, frequency
    
    def calibrate_motor(self, motor_index):
        """모터 원점 보정"""
        if 0 <= motor_index <= 3:
            print(f"모터 {motor_index} 원점 보정 시작...")
            
            # 천천히 회전하면서 리미트 스위치 감지
            while not self.is_limit_switch_pressed(motor_index):
                self.step_motor(motor_index, -1, 1)  # 반시계 방향으로 1스텝
                time.sleep_ms(10)  # 천천히
            
            # 원점 위치 설정
            self.motor_positions[motor_index] = 0
            self.motor_steps[motor_index] = 0
            print(f"모터 {motor_index} 원점 보정 완료")
            return True
        
        return False
    
    def move_to_compartment(self, motor_index, compartment):
        """특정 칸으로 이동"""
        if 0 <= motor_index <= 3 and 0 <= compartment <= 9:
            current_pos = self.motor_positions[motor_index]
            steps_needed = (compartment - current_pos) * self.steps_per_compartment
            
            if steps_needed != 0:
                direction = 1 if steps_needed > 0 else -1
                steps = abs(steps_needed)
                
                print(f"모터 {motor_index}: 칸 {current_pos} → 칸 {compartment} ({steps}스텝)")
                
                # 8스텝씩 나누어서 실행
                for i in range(0, steps, 8):
                    remaining_steps = min(8, steps - i)
                    if not self.step_motor(motor_index, direction, remaining_steps):
                        print(f"모터 {motor_index} 이동 중단됨 (리미트 스위치)")
                        return False
                
                self.motor_positions[motor_index] = compartment
                print(f"모터 {motor_index} 칸 {compartment} 이동 완료")
            
            return True
        
        return False
    
    def next_compartment(self, motor_index):
        """다음 칸으로 이동"""
        if 0 <= motor_index <= 3:
            next_comp = (self.motor_positions[motor_index] + 1) % 10
            return self.move_to_compartment(motor_index, next_comp)
        return False
    
    def get_motor_position(self, motor_index):
        """모터의 현재 칸 위치 반환"""
        if 0 <= motor_index <= 3:
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

class PillBoxMotorSystem:
    """필박스 모터 시스템 관리 클래스"""
    
    def __init__(self):
        """필박스 모터 시스템 초기화"""
        self.motor_controller = StepperMotorController()
        
        # 필박스 설정
        self.num_disks = 3  # 3개 디스크
        self.compartments_per_disk = 10  # 디스크당 10칸
        
        print("✅ PillBoxMotorSystem 초기화 완료")
    
    def calibrate_all_disks(self):
        """모든 디스크 원점 보정"""
        print("모든 디스크 원점 보정 시작...")
        
        for i in range(self.num_disks):
            if not self.motor_controller.calibrate_motor(i):
                print(f"디스크 {i} 보정 실패")
                return False
        
        print("모든 디스크 보정 완료!")
        return True
    
    def load_pills(self, disk_index, compartments=3):
        """알약 충전 (3칸씩 회전)"""
        if 0 <= disk_index < self.num_disks:
            print(f"디스크 {disk_index} 알약 충전 시작 ({compartments}칸 회전)")
            
            for i in range(compartments):
                if not self.motor_controller.next_compartment(disk_index):
                    print(f"디스크 {disk_index} 충전 중단됨")
                    return False
                time.sleep_ms(500)  # 각 칸마다 잠시 대기
            
            print(f"디스크 {disk_index} 알약 충전 완료")
            return True
        
        return False
    
    def dispense_pills(self, disk_index, compartment=None):
        """알약 배출"""
        if 0 <= disk_index < self.num_disks:
            if compartment is None:
                # 현재 칸에서 배출
                compartment = self.motor_controller.get_motor_position(disk_index)
            
            print(f"디스크 {disk_index} 칸 {compartment}에서 알약 배출")
            
            # 해당 칸으로 이동
            if self.motor_controller.move_to_compartment(disk_index, compartment):
                print(f"디스크 {disk_index} 칸 {compartment} 배출 완료")
                return True
            else:
                print(f"디스크 {disk_index} 배출 실패")
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
    
    def test_motors(self):
        """모터 테스트"""
        print("=== 필박스 모터 테스트 시작 ===")
        
        # 각 디스크별 테스트
        for i in range(self.num_disks):
            print(f"\n디스크 {i} 테스트:")
            
            # 다음 칸으로 이동
            print("  다음 칸으로 이동...")
            self.motor_controller.next_compartment(i)
            time.sleep(1)
            
            # 특정 칸으로 이동
            print("  칸 5로 이동...")
            self.motor_controller.move_to_compartment(i, 5)
            time.sleep(1)
            
            # 원점으로 복귀
            print("  원점으로 복귀...")
            self.motor_controller.move_to_compartment(i, 0)
            time.sleep(1)
        
        print("모터 테스트 완료")
    
    def emergency_stop(self):
        """비상 정지"""
        print("비상 정지 실행!")
        self.motor_controller.stop_all_motors()
