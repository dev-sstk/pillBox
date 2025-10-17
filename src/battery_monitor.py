"""
배터리 모니터링 시스템
ESP32-C6의 ADC를 사용하여 Li-ion 배터리 전압을 모니터링합니다.

하드웨어 사양 (HARDWARE.md 참조):
- GPIO: IO4 (BAT_AD)
- 배터리: 3.7V Li-ion (3.0V ~ 4.2V)
- 전압 분배기: R1=100kΩ, R2=100kΩ (분배 비율 1:2)
- ADC: 12bit (0 ~ 4095), 0V ~ 3.3V
- 배터리 전압 계산: V_battery = ADC_value * 3.3 / 4095 * 2
"""

import machine
import time
from memory_manager import safe_print

class BatteryMonitor:
    """배터리 전압 모니터링 클래스"""
    
    def __init__(self):
        """배터리 모니터 초기화"""
        self.adc_pin = 4  # IO4 (BAT_AD)
        self.adc = None
        self.voltage_divider_ratio = 2.0  # 전압 분배기 비율 (R1=R2=100kΩ)
        self.adc_max_value = 4095  # 12bit ADC 최대값
        self.adc_reference_voltage = 3.3  # ADC 기준 전압
        
        # 배터리 상태 임계값
        self.voltage_low = 3.0      # 저전압 경고 (3.0V)
        self.voltage_critical = 2.8  # 위험 전압 (2.8V)
        self.voltage_full = 4.2     # 충전 완료 (4.2V)
        self.voltage_charging = 3.7  # 충전 중 (3.7V)
        
        # ADC 초기화
        self._init_adc()
        
        safe_print("[OK] BatteryMonitor 초기화 완료")
    
    def _init_adc(self):
        """ADC 초기화"""
        try:
            # ADC 핀 설정
            adc_pin = machine.Pin(self.adc_pin)
            self.adc = machine.ADC(adc_pin)
            
            # ADC 설정 (0V ~ 3.3V 범위)
            self.adc.atten(machine.ADC.ATTN_11DB)
            
            safe_print(f"[OK] ADC 초기화 완료: GPIO{self.adc_pin}")
            
        except Exception as e:
            safe_print(f"[ERROR] ADC 초기화 실패: {e}")
            self.adc = None
    
    def read_raw_adc(self):
        """원시 ADC 값 읽기"""
        if not self.adc:
            return 0
        
        try:
            # 여러 번 읽어서 평균값 계산 (노이즈 제거)
            readings = []
            for _ in range(5):
                readings.append(self.adc.read())
                time.sleep_ms(1)  # 1ms 대기
            
            # 평균값 계산
            raw_value = sum(readings) // len(readings)
            return raw_value
            
        except Exception as e:
            safe_print(f"[ERROR] ADC 읽기 실패: {e}")
            return 0
    
    def read_battery_voltage(self):
        """배터리 전압 읽기 (V)"""
        raw_adc = self.read_raw_adc()
        
        if raw_adc == 0:
            return 0.0
        
        try:
            # ADC 전압 계산
            adc_voltage = raw_adc * self.adc_reference_voltage / self.adc_max_value
            
            # 전압 분배기 보정하여 실제 배터리 전압 계산
            battery_voltage = adc_voltage * self.voltage_divider_ratio
            
            return round(battery_voltage, 2)
            
        except Exception as e:
            safe_print(f"[ERROR] 배터리 전압 계산 실패: {e}")
            return 0.0
    
    def get_battery_percentage(self):
        """배터리 잔량 백분율 계산"""
        voltage = self.read_battery_voltage()
        
        if voltage == 0:
            return 0
        
        # Li-ion 배터리 방전 곡선 기반 백분율 계산
        if voltage >= self.voltage_full:
            return 100
        elif voltage >= 3.7:
            # 4.2V ~ 3.7V: 100% ~ 50%
            percentage = ((voltage - 3.7) / (self.voltage_full - 3.7)) * 50 + 50
        elif voltage >= 3.4:
            # 3.7V ~ 3.4V: 50% ~ 20%
            percentage = ((voltage - 3.4) / (3.7 - 3.4)) * 30 + 20
        elif voltage >= 3.0:
            # 3.4V ~ 3.0V: 20% ~ 5%
            percentage = ((voltage - 3.0) / (3.4 - 3.0)) * 15 + 5
        else:
            # 3.0V 이하: 5% 이하
            percentage = max(0, (voltage - 2.5) / (3.0 - 2.5) * 5)
        
        return max(0, min(100, int(percentage)))
    
    def get_battery_status(self):
        """배터리 상태 반환"""
        voltage = self.read_battery_voltage()
        percentage = self.get_battery_percentage()
        
        if voltage == 0:
            return {
                'voltage': 0.0,
                'percentage': 0,
                'status': 'error',
                'message': 'ADC 읽기 실패'
            }
        elif voltage >= self.voltage_full:
            return {
                'voltage': voltage,
                'percentage': percentage,
                'status': 'full',
                'message': '충전 완료'
            }
        elif voltage >= self.voltage_charging:
            return {
                'voltage': voltage,
                'percentage': percentage,
                'status': 'good',
                'message': '정상'
            }
        elif voltage >= self.voltage_low:
            return {
                'voltage': voltage,
                'percentage': percentage,
                'status': 'low',
                'message': '저전압 경고'
            }
        elif voltage >= self.voltage_critical:
            return {
                'voltage': voltage,
                'percentage': percentage,
                'status': 'critical',
                'message': '위험 전압'
            }
        else:
            return {
                'voltage': voltage,
                'percentage': percentage,
                'status': 'dead',
                'message': '배터리 방전'
            }
    
    def is_charging(self):
        """충전 상태 확인 (전압 기반 추정)"""
        voltage = self.read_battery_voltage()
        
        # USB 연결 시 전압이 4.0V 이상이면 충전 중으로 추정
        return voltage >= 4.0
    
    def is_low_battery(self):
        """저전압 상태 확인"""
        voltage = self.read_battery_voltage()
        return voltage <= self.voltage_low
    
    def is_critical_battery(self):
        """위험 전압 상태 확인"""
        voltage = self.read_battery_voltage()
        return voltage <= self.voltage_critical
    
    def get_charging_led_color(self):
        """충전 상태에 따른 LED 색상 반환"""
        if self.is_charging():
            if self.read_battery_voltage() >= self.voltage_full:
                return 'green'  # 충전 완료
            else:
                return 'red'    # 충전 중
        else:
            return 'off'        # 충전 안함
    
    def test_battery_monitor(self):
        """배터리 모니터 테스트"""
        safe_print("🔋 배터리 모니터 테스트 시작")
        
        # 원시 ADC 값
        raw_adc = self.read_raw_adc()
        safe_print(f"  📊 원시 ADC 값: {raw_adc}")
        
        # 배터리 전압
        voltage = self.read_battery_voltage()
        safe_print(f"  ⚡ 배터리 전압: {voltage}V")
        
        # 배터리 백분율
        percentage = self.get_battery_percentage()
        safe_print(f"  📈 배터리 잔량: {percentage}%")
        
        # 배터리 상태
        status = self.get_battery_status()
        safe_print(f"  🔋 배터리 상태: {status['status']} ({status['message']})")
        
        # 충전 상태
        charging = self.is_charging()
        safe_print(f"  🔌 충전 상태: {'충전 중' if charging else '충전 안함'}")
        
        # LED 색상
        led_color = self.get_charging_led_color()
        safe_print(f"  💡 LED 색상: {led_color}")
        
        safe_print("🔋 배터리 모니터 테스트 완료")
        
        return status

# 전역 인스턴스
_battery_monitor = None

def get_battery_monitor():
    """배터리 모니터 인스턴스 반환 (싱글톤)"""
    global _battery_monitor
    if _battery_monitor is None:
        _battery_monitor = BatteryMonitor()
    return _battery_monitor

# 편의 함수들
def read_battery_voltage():
    """배터리 전압 읽기"""
    return get_battery_monitor().read_battery_voltage()

def get_battery_percentage():
    """배터리 잔량 백분율"""
    return get_battery_monitor().get_battery_percentage()

def get_battery_status():
    """배터리 상태 정보"""
    return get_battery_monitor().get_battery_status()

def is_charging():
    """충전 상태 확인"""
    return get_battery_monitor().is_charging()

def is_low_battery():
    """저전압 상태 확인"""
    return get_battery_monitor().is_low_battery()

def is_critical_battery():
    """위험 전압 상태 확인"""
    return get_battery_monitor().is_critical_battery()

# 테스트 함수
def test_battery():
    """배터리 모니터 테스트 실행"""
    return get_battery_monitor().test_battery_monitor()

if __name__ == "__main__":
    # 직접 실행 시 테스트
    test_battery()
