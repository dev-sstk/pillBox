"""
LED 제어 시스템
알람 LED, 상태 LED 등을 관리하는 시스템
"""

import time
from machine import Pin

class LEDController:
    """LED 제어 시스템 클래스"""
    
    def __init__(self):
        """LED 제어 시스템 초기화"""
        self.led_enabled = True
        self.alarm_led_pin = None
        self.status_led_pin = None
        self.alarm_led_state = False
        self.status_led_state = False
        
        # LED 핀 초기화
        self._init_led_pins()
        
        print("[OK] LEDController 초기화 완료")
    
    def _init_led_pins(self):
        """LED 핀 초기화"""
        try:
            # 알람 LED (GPIO 1 - HARDWARE.md 참조: LED_PWR/B)
            self.alarm_led_pin = Pin(1, Pin.OUT)
            self.alarm_led_pin.value(0)  # 초기값 OFF
            
            # 상태 LED (GPIO 3 - 선택사항)
            # self.status_led_pin = Pin(3, Pin.OUT)
            # self.status_led_pin.value(0)
            
            print("[OK] LED 핀 초기화 완료")
            
        except Exception as e:
            print(f"[WARN] LED 핀 초기화 실패: {e}")
            self.led_enabled = False
    
    def show_alarm_led(self):
        """알람 LED 켜기"""
        try:
            # LED 핀이 없으면 다시 초기화 시도
            if not self.alarm_led_pin:
                print("[WARN] LED 핀 없음 - 재초기화 시도")
                self._init_led_pins()
            
            if self.alarm_led_pin:
                self.alarm_led_pin.value(1)
                self.alarm_led_state = True
                print("💡 알람 LED 켜짐")
            else:
                print("💡 알람 LED 켜짐 (시뮬레이션 - 핀 초기화 실패)")
            
        except Exception as e:
            print(f"[ERROR] 알람 LED 켜기 실패: {e}")
            print("💡 알람 LED 켜짐 (시뮬레이션)")
    
    def hide_alarm_led(self):
        """알람 LED 끄기"""
        try:
            if self.alarm_led_pin:
                self.alarm_led_pin.value(0)
                self.alarm_led_state = False
                print("💡 알람 LED 꺼짐")
            else:
                print("💡 알람 LED 꺼짐 (시뮬레이션 - 핀 없음)")
            
        except Exception as e:
            print(f"[ERROR] 알람 LED 끄기 실패: {e}")
            print("💡 알람 LED 꺼짐 (시뮬레이션)")
    
    def blink_alarm_led(self, duration_ms=1000, interval_ms=200):
        """알람 LED 깜빡이기"""
        try:
            if not self.led_enabled or not self.alarm_led_pin:
                print(f"💡 알람 LED 깜빡임 (시뮬레이션) - {duration_ms}ms")
                return
            
            start_time = time.ticks_ms()
            led_state = False
            
            while time.ticks_diff(time.ticks_ms(), start_time) < duration_ms:
                led_state = not led_state
                self.alarm_led_pin.value(1 if led_state else 0)
                time.sleep_ms(interval_ms)
            
            # 깜빡임 완료 후 LED 끄기
            self.alarm_led_pin.value(0)
            self.alarm_led_state = False
            print(f"💡 알람 LED 깜빡임 완료 ({duration_ms}ms)")
            
        except Exception as e:
            print(f"[ERROR] 알람 LED 깜빡임 실패: {e}")
            print(f"💡 알람 LED 깜빡임 (시뮬레이션) - {duration_ms}ms")
    
    def show_status_led(self):
        """상태 LED 켜기"""
        try:
            if not self.led_enabled or not self.status_led_pin:
                print("🔵 상태 LED 켜짐 (시뮬레이션)")
                return
            
            self.status_led_pin.value(1)
            self.status_led_state = True
            print("🔵 상태 LED 켜짐")
            
        except Exception as e:
            print(f"[ERROR] 상태 LED 켜기 실패: {e}")
            print("🔵 상태 LED 켜짐 (시뮬레이션)")
    
    def hide_status_led(self):
        """상태 LED 끄기"""
        try:
            if not self.led_enabled or not self.status_led_pin:
                print("🔵 상태 LED 꺼짐 (시뮬레이션)")
                return
            
            self.status_led_pin.value(0)
            self.status_led_state = False
            print("🔵 상태 LED 꺼짐")
            
        except Exception as e:
            print(f"[ERROR] 상태 LED 끄기 실패: {e}")
            print("🔵 상태 LED 꺼짐 (시뮬레이션)")
    
    def enable_led(self):
        """LED 시스템 활성화"""
        self.led_enabled = True
        print("💡 LED 시스템 활성화")
    
    def disable_led(self):
        """LED 시스템 비활성화"""
        self.led_enabled = False
        # 모든 LED 끄기
        self.hide_alarm_led()
        self.hide_status_led()
        print("💡 LED 시스템 비활성화")
    
    def get_led_status(self):
        """LED 상태 반환"""
        return {
            'enabled': self.led_enabled,
            'alarm_led_state': self.alarm_led_state,
            'status_led_state': self.status_led_state,
            'alarm_led_pin': self.alarm_led_pin is not None,
            'status_led_pin': self.status_led_pin is not None
        }
    
    def test_leds(self):
        """LED 테스트"""
        print("🧪 LED 테스트 시작")
        
        # 알람 LED 테스트
        print("  - 알람 LED 테스트")
        self.show_alarm_led()
        time.sleep_ms(500)
        self.hide_alarm_led()
        time.sleep_ms(500)
        
        # 알람 LED 깜빡임 테스트
        print("  - 알람 LED 깜빡임 테스트")
        self.blink_alarm_led(1000, 100)
        
        # 상태 LED 테스트 (있는 경우)
        if self.status_led_pin:
            print("  - 상태 LED 테스트")
            self.show_status_led()
            time.sleep_ms(500)
            self.hide_status_led()
        
        print("🧪 LED 테스트 완료")
