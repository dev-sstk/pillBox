"""
boot.py - ESP32 부팅 시 실행되는 초기화 스크립트
스테퍼 모터 핀 초기화 및 기타 하드웨어 초기 설정
"""

from machine import Pin
import time

def initialize_stepper_motor_pins():
    """
    74HC595D 시프트 레지스터를 통해 스테퍼 모터의 모든 핀을 HIGH로 초기화
    
    이 함수는 부팅 시 스테퍼 모터의 모든 출력 핀을 HIGH 상태로 설정하여
    초기 상태를 안정화시킵니다.
    
    하드웨어 구성:
    - 74HC595D x 2개 (캐스케이드 연결)
    - DI (Data Input): GPIO2
    - SH_CP (Shift Clock): GPIO3
    - ST_CP (Storage Clock): GPIO15
    - 총 16개 출력 핀 (4개 모터 x 4개 코일)
    """
    print("스테퍼 모터 핀 초기화 시작...")
    
    try:
        # 74HC595D 제어 핀 초기화
        di = Pin(2, Pin.OUT)      # Data Input
        sh_cp = Pin(3, Pin.OUT)   # Shift Clock
        st_cp = Pin(15, Pin.OUT)  # Storage Clock (Latch)
        
        # 초기 상태 설정
        di.value(0)
        sh_cp.value(0)
        st_cp.value(0)
        
        def shift_out_byte(data):
            """8비트 데이터를 74HC595D로 전송 (MSB first)"""
            for i in range(8):
                # MSB first
                bit = (data >> (7 - i)) & 1
                di.value(bit)
                
                # Shift clock pulse
                sh_cp.value(1)
                sh_cp.value(0)
        
        def latch_output():
            """Storage clock pulse - 데이터를 출력 래치에 저장"""
            st_cp.value(1)
            st_cp.value(0)
        
        # 모든 코일을 OFF로 설정 (74HC595 출력 LOW → ULN2003A 출력 HIGH)
        # 2개의 74HC595D가 캐스케이드로 연결되어 있으므로 2바이트 전송
        # 상위 바이트 먼저 전송 (두 번째 74HC595D)
        shift_out_byte(0x00)  # 모터 2, 3의 모든 코일 OFF
        shift_out_byte(0x00)  # 모터 0, 1의 모든 코일 OFF
        
        # 출력 래치
        latch_output()
        
        print("스테퍼 모터 핀 초기화 완료 (모든 코일 OFF)")
        print("  - 모터 0: 0x00 (코일 OFF)")
        print("  - 모터 1: 0x00 (코일 OFF)")
        print("  - 모터 2: 0x00 (코일 OFF)")
        print("  - 모터 3: 0x00 (코일 OFF)")
        
        return True
        
    except Exception as e:
        print(f"스테퍼 모터 핀 초기화 실패: {e}")
        return False

# 부팅 시 자동 실행
if __name__ == "__main__":
    print("=" * 50)
    print("ESP32-C6 필박스 부팅 초기화")
    print("=" * 50)
    
    # ⚡ 메모리 부족 해결: 부팅 시 메모리 정리
    import gc
    print("🧹 부팅 시 메모리 정리 시작...")
    for i in range(5):  # 5회 가비지 컬렉션
        gc.collect()
        time.sleep(0.02)  # 0.02초 대기
    print("✅ 부팅 시 메모리 정리 완료")
    
    # 스테퍼 모터 핀 초기화
    initialize_stepper_motor_pins()
    # 짧은 지연 후 메인 프로그램으로 진행
    time.sleep_ms(100)
    
    print("부팅 초기화 완료")
    print("=" * 50)

