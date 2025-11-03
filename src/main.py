"""
필박스 메인 실행 파일
스타트업 스크린만 표시하는 간단한 버전
"""

import sys
import os
import time
import lvgl as lv
import lv_utils
from machine import Pin, SPI
from st77xx import St7735

# ESP32에서 실행 시 경로 설정
sys.path.append("/")
sys.path.append("/screens")

from screen_manager import ScreenManager
from motor_control import PillBoxMotorSystem

def set_st7735_offset(offset_x=0, offset_y=0):
    """ST7735 오프셋 설정 (test_lvgl.py 방식)"""
    # # print(f"ST7735 오프셋 설정: X={offset_x}, Y={offset_y}")
    
    # ST7735 드라이버의 오프셋 맵 수정
    from st77xx import ST77XX_COL_ROW_MODEL_START_ROTMAP
    
    # blacktab 모델의 오프셋을 조정
    new_offset = [(offset_x, offset_y), (offset_x, offset_y), (offset_x, offset_y), (offset_x, offset_y)]
    ST77XX_COL_ROW_MODEL_START_ROTMAP[(128, 160, 'blacktab')] = new_offset
    
    # # print(f"오프셋 설정 완료: {new_offset}")


def init_display():
    """ST7735 디스플레이 초기화 - 백라이트 하드웨어 연결 고려"""
    try:
        # [SIMPLE] 디스플레이 설정 (메모리 정리 최소화)
        import gc
        # # print("🧹 디스플레이 초기화 전 메모리 정리 시작...")
        for i in range(1):  # 2회 → 1회로 최적화 (백라이트 하드웨어 연결 고려)
            gc.collect()
            time.sleep(0.002)  # 0.005초 → 0.002초로 최적화
        # # print("[OK] 디스플레이 초기화 전 메모리 정리 완료")
        
        # 디스플레이 설정
        DISPLAY_WIDTH = 128
        DISPLAY_HEIGHT = 160
        
        # 오프셋 설정 (test_lvgl.py와 동일)
        set_st7735_offset(1, 2)
        
        # SPI 설정
        spi = SPI(1, baudrate=40000000, polarity=0, phase=0, sck=Pin(22), mosi=Pin(21))
        
        # 제어 핀 설정
        dc = Pin(19, Pin.OUT)
        cs = Pin(23, Pin.OUT)
        rst = Pin(20, Pin.OUT)
        
        # [SIMPLE] ST7735 디스플레이 객체 생성 (백라이트는 하드웨어로 항상 켜짐)
        # # print("🧹 ST7735 디스플레이 객체 생성 시작...")
        display = St7735(
            res=(DISPLAY_WIDTH, DISPLAY_HEIGHT),
            model='blacktab',
            cs=cs,
            dc=dc,
            rst=rst,
            spi=spi,
            rot=3,  # 180도 회전
            doublebuffer=False
        )
        # # print("[OK] ST7735 디스플레이 객체 생성 완료")
        
        # [NOTE] 백라이트는 하드웨어로 3.3V에 직접 연결되어 소프트웨어 제어 불가
        # # print("[INFO] 백라이트는 하드웨어로 항상 켜짐 (3.3V 직접 연결)")
        
        # # print("[OK] ST7735 디스플레이 초기화 완료")
        return True
        
    except Exception as e:
        # # print(f"[ERROR] 디스플레이 초기화 실패: {e}")
        # [SIMPLE] 메모리 정리 최소화
        # # print("🧹 디스플레이 초기화 실패 후 메모리 정리...")
        for i in range(1):  # 2회 → 1회로 최적화
            gc.collect()
            time.sleep(0.002)
        # # print("[OK] 메모리 정리 완료")
        return False

def setup_lvgl():
    """LVGL 환경 설정 - 화면 깜빡임 완전 제거"""
    try:
        # [SMOOTH] LVGL 설정 전 메모리 정리 최소화
        import gc
        # # print("🧹 LVGL 설정 전 메모리 정리 시작...")
        for i in range(2):  # 3회 → 2회로 최적화 (화면 깜빡임 완전 방지)
            gc.collect()
            time.sleep(0.005)  # 0.01초 → 0.005초로 최적화
        # # print("[OK] LVGL 설정 전 메모리 정리 완료")
        
        # 이미 초기화된 경우 체크
        if lv.is_initialized():
            # print("[WARN] LVGL이 이미 초기화됨, 재초기화 시도...")
            # 기존 리소스 정리
            cleanup_lvgl()
            # 추가 대기 최소화
            time.sleep(0.02)  # 0.05초 → 0.02초로 최적화
        
        # 1단계: LVGL 초기화
        lv.init()
        # print("[OK] LVGL 초기화 완료")
        
        # 2단계: 디스플레이 드라이버 초기화 (ST7735)
        # 이 단계에서 lv.display_register()가 호출됨
        display_init_success = init_display()
        if not display_init_success:
            # print("[ERROR] 디스플레이 초기화 실패로 LVGL 설정 중단")
            return False
        # print("[OK] 디스플레이 드라이버 초기화 완료")
        
        # 3단계: 이벤트 루프 시작
        if not lv_utils.event_loop.is_running():
            event_loop = lv_utils.event_loop()
            # print("[OK] LVGL 이벤트 루프 시작")
        
        # 초기화 후 메모리 정리 최소화
        import gc
        gc.collect()
        
        return True
        
    except Exception as e:
        # print(f"[ERROR] LVGL 설정 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def cleanup_lvgl():
    """LVGL 리소스 정리"""
    try:
        # print("🧹 LVGL 리소스 정리 중...")
        
        # 강제 메모리 정리
        import gc
        gc.collect()
        
        # LVGL 정리 (가능한 경우)
        try:
            # 현재 화면의 모든 자식 객체 정리
            if hasattr(lv, 'scr_act'):
                current_screen = lv.scr_act()
                if current_screen:
                    # 모든 자식 객체 삭제
                    while current_screen.get_child_cnt() > 0:
                        child = current_screen.get_child(0)
                        if child:
                            child.delete()
                    # print("[OK] 화면 자식 객체 정리 완료")
            
            # 디스플레이 버퍼 정리
            if hasattr(lv, 'display_get_default'):
                disp = lv.display_get_default()
                if disp:
                    # 디스플레이 버퍼 강제 정리
                    try:
                        disp.set_draw_buffers(None, None)
                    except:
                        pass
                    # print("[OK] 디스플레이 버퍼 정리 완료")
            
            # print("[OK] LVGL 리소스 정리 완료")
        except Exception as e:
            # print(f"[WARN] LVGL 정리 중 일부 오류 (무시됨): {e}")
            pass
        
        # 강제 가비지 컬렉션 여러 번 실행
        for i in range(3):
            gc.collect()
            time.sleep(0.01)  # 짧은 대기
        
        # print("[OK] 메모리 정리 완료")
        
    except Exception as e:
        # print(f"[WARN] 리소스 정리 중 오류 (무시됨): {e}")
        pass

def start_application(screen_name, **kwargs):
    """애플리케이션 시작 및 화면 실행"""
    # print("=" * 60)
    # print(f"필박스 {screen_name} 화면 시작")
    # print("=" * 60)
    
    try:
        # LVGL 환경 설정
        if not setup_lvgl():
            # print("[ERROR] LVGL 환경 설정 실패")
            return False
        
        # 화면 관리자 생성
        screen_manager = ScreenManager()
        
        # 화면 생성 전 추가 메모리 정리 최소화 (화면 깜빡임 완전 방지)
        # print("🧹 화면 생성 전 메모리 정리...")
        import gc
        for i in range(1):  # 2회 → 1회로 최적화 (화면 깜빡임 완전 방지)
            gc.collect()
            time.sleep(0.002)  # 0.005초 → 0.002초로 최적화
        
        # 화면 캐싱 방식: 이미 등록된 화면이 있으면 재사용
        if screen_name in screen_manager.screens:
            # print(f"♻️ {screen_name} 화면 재사용 (캐싱됨)")
            screen = screen_manager.screens[screen_name]
        else:
            # 화면 생성 및 등록
            # print(f"[INFO] {screen_name} 화면 생성 중...")
            
            if screen_name == "startup":
                from screens.startup_screen import StartupScreen
                screen = StartupScreen(screen_manager)
            elif screen_name == "wifi_scan":
                from screens.wifi_scan_screen import WifiScanScreen
                screen = WifiScanScreen(screen_manager)
                # 와이파이 관련 화면들도 함께 등록 (연동을 위해)
                if 'wifi_password' not in screen_manager.screens:
                    from screens.wifi_password_screen import WifiPasswordScreen
                    wifi_password_screen = WifiPasswordScreen(screen_manager, "Example_SSID")
                    screen_manager.register_screen('wifi_password', wifi_password_screen)
                    # print("[OK] wifi_password 화면도 함께 등록됨")
                # WiFi 연결 후 복용 시간 선택 화면으로 이동하기 위해 미리 등록
                if 'meal_time' not in screen_manager.screens:
                    from screens.meal_time_screen import MealTimeScreen
                    meal_time_screen = MealTimeScreen(screen_manager)
                    screen_manager.register_screen('meal_time', meal_time_screen)
                    # print("[OK] meal_time 화면도 함께 등록됨")
            elif screen_name == "wifi_password":
                from screens.wifi_password_screen import WifiPasswordScreen
                screen = WifiPasswordScreen(screen_manager, "Example_SSID")
            elif screen_name == "meal_time":
                from screens.meal_time_screen import MealTimeScreen
                screen = MealTimeScreen(screen_manager)
            elif screen_name == "dose_time":
                from screens.dose_time_screen import DoseTimeScreen
                screen = DoseTimeScreen(screen_manager)
            elif screen_name == "main":
                from screens.main_screen import MainScreen
                screen = MainScreen(screen_manager)
                
                # 약품 배출 테스트 함수들을 바로 사용할 수 있도록 전역 변수로 설정
                global main_screen_instance
                main_screen_instance = screen
            elif screen_name == "pill_loading":
                from screens.pill_loading_screen import PillLoadingScreen
                screen = PillLoadingScreen(screen_manager)
            elif screen_name == "dose_time":
                # 시간-분 설정 화면 (dose_time 화면 사용)
                from screens.dose_time_screen import DoseTimeScreen
                screen = DoseTimeScreen(screen_manager)
            elif screen_name == "meal_time":
                # 복용시간선택 화면 (meal_time 화면 사용)
                from screens.meal_time_screen import MealTimeScreen
                screen = MealTimeScreen(screen_manager)
            else:
                # print(f"[ERROR] 알 수 없는 화면: {screen_name}")
                return False
            
            # 화면 등록
            screen_manager.register_screen(screen_name, screen)
            # print(f"[OK] {screen_name} 화면 생성 및 등록 완료")
        
        # 화면 표시
        # print(f"[INFO] {screen_name} 화면 표시 중...")
        screen_manager.set_current_screen(screen_name)
        
        # print(f"[OK] {screen_name} 화면 실행됨")
        # print("[INFO] 화면이 표시되었습니다!")
        # print("[GAME] 버튼 조작법:")
        # print("   - A: 위/이전")
        # print("   - B: 아래/다음") 
        # print("   - C: 뒤로가기")
        # print("   - D: 선택/확인")
        # print("[TIP] 실제 ESP32-C6 하드웨어에서 버튼으로 조작하세요")
        # print("[TIP] Ctrl+C로 종료하세요")
        
        # 자동 시뮬레이션 제거 - 물리 버튼으로만 조작
        
        # 버튼 인터페이스 초기화
        # print("[BTN] 버튼 인터페이스 초기화 중...")
        try:
            from button_interface import ButtonInterface
            button_interface = ButtonInterface()
            
            # ScreenManager에 button_interface 참조 저장
            screen_manager.set_button_interface(button_interface)
            
            # 버튼 콜백 설정 (ScreenManager의 핸들러 사용)
            button_interface.set_callback('A', screen_manager.handle_button_a)
            button_interface.set_callback('B', screen_manager.handle_button_b)
            button_interface.set_callback('C', screen_manager.handle_button_c)
            button_interface.set_callback('D', screen_manager.handle_button_d)
            
            # print("[OK] 버튼 인터페이스 초기화 완료")
        except Exception as e:
            # print(f"[WARN] 버튼 인터페이스 초기화 실패: {e}")
            # print("[TIP] 실제 ESP32-C6 하드웨어에서만 버튼 입력이 가능합니다")
            button_interface = None
        
        # 메인 루프 실행
        try:
            while True:
                # 화면 업데이트
                screen_manager.update()
                
                # LVGL 이벤트 처리
                lv.timer_handler()
                
                # 버튼 입력 처리
                if button_interface:
                    # 실제 하드웨어 버튼 처리
                    button_interface.update()
                else:
                    # 버튼 인터페이스가 없는 경우 무시
                    pass
                
                # 짧은 대기
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            # print(f"\n🛑 {screen_name} 화면 테스트 중단됨")
            # 중단 시에도 리소스 정리
            cleanup_lvgl()
        return True
        
    except Exception as e:
        # print(f"[ERROR] {screen_name} 화면 실행 실패: {e}")
        import sys
        sys.print_exception(e)
        return False





def check_boot_target():
    """부팅 타겟 확인 (D버튼으로 설정된 특정 화면으로 부팅)"""
    try:
        import json
        import os
        
        boot_file = "/data/boot_target.json"
        
        # 파일이 존재하는지 확인
        try:
            with open(boot_file, 'r') as f:
                data = json.load(f)
                boot_target = data.get('boot_target', None)
                if boot_target:
                    # print(f"[INFO] 부팅 타겟 발견: {boot_target}")
                    # 부팅 타겟 파일은 화면에서 사용한 후 삭제하도록 유지
                    return boot_target
                return None
        except OSError:
            # 파일이 없으면 일반 부팅
            return None
            
    except Exception as e:
        # print(f"[WARN] 부팅 타겟 확인 실패: {e}")
        return None


def main():
    """메인 함수 - 필박스 자동 시작 (백라이트 하드웨어 연결 고려)"""
    # print("=" * 60)
    # print("필박스 시스템 시작")
    # print("=" * 60)
    
    # 부팅 타겟 확인 (D버튼으로 설정된 특정 화면으로 부팅)
    boot_target = check_boot_target()
    
    try:
        if boot_target:
            # 특정 화면으로 부팅 (D버튼으로 설정된 경우)
            # print(f"[INFO] 특정 화면으로 부팅: {boot_target}")
            start_application(boot_target)
        else:
            # 처음 부팅 - WiFi 스캔부터 시작
            # print("[INFO] 처음 부팅 - WiFi 스캔부터 시작...")
            start_application("startup")
        
    except KeyboardInterrupt:
        # print("\n🛑 프로그램이 중단되었습니다")
        cleanup_lvgl()
    except Exception as e:
        # print(f"[ERROR] 오류 발생: {e}")
        import sys
        sys.print_exception(e)
        cleanup_lvgl()

if __name__ == "__main__":
    main()