"""
LED 제어 시스템
알람 LED, 상태 LED 등을 관리하는 시스템
"""

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
    
    
