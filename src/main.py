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
from screens.startup_screen import StartupScreen
from screens.wifi_scan_screen import WifiScanScreen

def set_st7735_offset(offset_x=0, offset_y=0):
    """ST7735 오프셋 설정 (test_lvgl.py 방식)"""
    print(f"ST7735 오프셋 설정: X={offset_x}, Y={offset_y}")
    
    # ST7735 드라이버의 오프셋 맵 수정
    from st77xx import ST77XX_COL_ROW_MODEL_START_ROTMAP
    
    # blacktab 모델의 오프셋을 조정
    new_offset = [(offset_x, offset_y), (offset_x, offset_y), (offset_x, offset_y), (offset_x, offset_y)]
    ST77XX_COL_ROW_MODEL_START_ROTMAP[(128, 160, 'blacktab')] = new_offset
    
    print(f"오프셋 설정 완료: {new_offset}")

def init_display():
    """ST7735 디스플레이 초기화 (test_lvgl.py 방식)"""
    try:
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
        
        # ST7735 디스플레이 초기화
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
        
        # 디스플레이 백라이트 설정
        display.set_backlight(100)
        
        print("✅ ST7735 디스플레이 초기화 완료")
        return True
        
    except Exception as e:
        print(f"❌ 디스플레이 초기화 실패: {e}")
        return False

def setup_lvgl():
    """LVGL 환경 설정 (올바른 순서)"""
    try:
        # 이미 초기화된 경우 체크
        if lv.is_initialized():
            print("⚠️ LVGL이 이미 초기화됨, 재초기화 시도...")
            # 기존 리소스 정리
            cleanup_lvgl()
            # 추가 대기
            time.sleep(0.1)
        
        # 1단계: LVGL 초기화
        lv.init()
        print("✅ LVGL 초기화 완료")
        
        # 2단계: 디스플레이 드라이버 초기화 (ST7735)
        # 이 단계에서 lv.display_register()가 호출됨
        init_display()
        print("✅ 디스플레이 드라이버 초기화 완료")
        
        # 3단계: 이벤트 루프 시작
        if not lv_utils.event_loop.is_running():
            event_loop = lv_utils.event_loop()
            print("✅ LVGL 이벤트 루프 시작")
        
        # 초기화 후 메모리 정리
        import gc
        gc.collect()
        
        return True
        
    except Exception as e:
        print(f"❌ LVGL 설정 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def cleanup_lvgl():
    """LVGL 리소스 정리"""
    try:
        print("🧹 LVGL 리소스 정리 중...")
        
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
                    print("✅ 화면 자식 객체 정리 완료")
            
            # 디스플레이 버퍼 정리
            if hasattr(lv, 'display_get_default'):
                disp = lv.display_get_default()
                if disp:
                    # 디스플레이 버퍼 강제 정리
                    try:
                        disp.set_draw_buffers(None, None)
                    except:
                        pass
                    print("✅ 디스플레이 버퍼 정리 완료")
            
            print("✅ LVGL 리소스 정리 완료")
        except Exception as e:
            print(f"⚠️ LVGL 정리 중 일부 오류 (무시됨): {e}")
        
        # 강제 가비지 컬렉션 여러 번 실행
        for i in range(3):
            gc.collect()
            time.sleep(0.01)  # 짧은 대기
        
        print("✅ 메모리 정리 완료")
        
    except Exception as e:
        print(f"⚠️ 리소스 정리 중 오류 (무시됨): {e}")

def run_screen_test(screen_name):
    """특정 화면 테스트 실행"""
    print("=" * 60)
    print(f"필박스 {screen_name} 화면 테스트")
    print("=" * 60)
    
    try:
        # 이전 리소스 정리
        cleanup_lvgl()
        
        # LVGL 환경 설정
        if not setup_lvgl():
            print("❌ LVGL 환경 설정 실패")
            return False
        
        # 화면 관리자 생성
        screen_manager = ScreenManager()
        
        # 화면 생성 전 추가 메모리 정리
        print("🧹 화면 생성 전 메모리 정리...")
        import gc
        for i in range(10):  # 10회 가비지 컬렉션
            gc.collect()
            time.sleep(0.02)  # 더 긴 대기 시간
        
        # 화면 캐싱 방식: 이미 등록된 화면이 있으면 재사용
        if screen_name in screen_manager.screens:
            print(f"♻️ {screen_name} 화면 재사용 (캐싱됨)")
            screen = screen_manager.screens[screen_name]
        else:
            # 화면 생성 및 등록
            print(f"📱 {screen_name} 화면 생성 중...")
            
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
                    print("✅ wifi_password 화면도 함께 등록됨")
            elif screen_name == "wifi_password":
                from screens.wifi_password_screen import WifiPasswordScreen
                screen = WifiPasswordScreen(screen_manager, "Example_SSID")
            elif screen_name == "dose_count":
                from screens.dose_count_screen import DoseCountScreen
                screen = DoseCountScreen(screen_manager)
            elif screen_name == "dose_time":
                from screens.dose_time_screen import DoseTimeScreen
                # 테스트를 위해 기본값 1회로 설정 (실제로는 dose_count에서 전달받아야 함)
                screen = DoseTimeScreen(screen_manager, dose_count=1)
            elif screen_name == "main":
                from screens.main_screen_ui import MainScreen
                screen = MainScreen(screen_manager)
                
                # 약품 배출 테스트 함수들을 바로 사용할 수 있도록 전역 변수로 설정
                global main_screen_instance
                main_screen_instance = screen
                print("✅ 약품 배출 테스트 함수들이 전역 변수로 설정됨")
                print("💡 사용법:")
                print("   main_screen_instance.test_auto()        # 자동 배출 테스트")
                print("   main_screen_instance.test_manual(0)     # 수동 배출 테스트")
                print("   main_screen_instance.test_slide(1)      # 슬라이드 테스트")
                print("   main_screen_instance.test_disk(0)       # 디스크 테스트")
                print("   main_screen_instance.test_all()         # 모든 테스트")
                print("   main_screen_instance.show_status()      # 상태 확인")
                print("   main_screen_instance.reset_schedule()   # 일정 초기화")
            elif screen_name == "notification":
                from screens.mock_screen import NotificationMockScreen
                screen = NotificationMockScreen(screen_manager, {"time": "10:00", "pills": ["Test Pill"]})
            elif screen_name == "settings":
                from screens.settings_screen import SettingsScreen
                screen = SettingsScreen(screen_manager)
            elif screen_name == "pill_loading":
                from screens.pill_loading_screen import PillLoadingScreen
                screen = PillLoadingScreen(screen_manager)
            elif screen_name == "pill_dispense":
                from screens.mock_screen import PillDispenseMockScreen
                screen = PillDispenseMockScreen(screen_manager)
            else:
                print(f"❌ 알 수 없는 화면: {screen_name}")
                return False
            
            # 화면 등록
            screen_manager.register_screen(screen_name, screen)
            print(f"✅ {screen_name} 화면 생성 및 등록 완료")
        
        # 화면 표시
        print(f"📱 {screen_name} 화면 표시 중...")
        screen_manager.set_current_screen(screen_name)
        
        print(f"✅ {screen_name} 화면 실행됨")
        print("📱 화면이 표시되었습니다!")
        print("🎮 버튼 조작법:")
        print("   - A: 위/이전")
        print("   - B: 아래/다음") 
        print("   - C: 뒤로가기")
        print("   - D: 선택/확인")
        print("💡 실제 ESP32-C6 하드웨어에서 버튼으로 조작하세요")
        print("💡 Ctrl+C로 종료하세요")
        
        # 자동 시뮬레이션 제거 - 물리 버튼으로만 조작
        
        # 버튼 인터페이스 초기화
        print("🔘 버튼 인터페이스 초기화 중...")
        try:
            from button_interface import ButtonInterface
            button_interface = ButtonInterface()
            
            # 버튼 콜백 설정 (ScreenManager의 핸들러 사용)
            button_interface.set_callback('A', screen_manager.handle_button_a)
            button_interface.set_callback('B', screen_manager.handle_button_b)
            button_interface.set_callback('C', screen_manager.handle_button_c)
            button_interface.set_callback('D', screen_manager.handle_button_d)
            
            print("✅ 버튼 인터페이스 초기화 완료")
        except Exception as e:
            print(f"⚠️ 버튼 인터페이스 초기화 실패: {e}")
            print("💡 실제 ESP32-C6 하드웨어에서만 버튼 입력이 가능합니다")
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
            print(f"\n🛑 {screen_name} 화면 테스트 중단됨")
            # 중단 시에도 리소스 정리
            cleanup_lvgl()
        return True
        
    except Exception as e:
        print(f"❌ {screen_name} 화면 실행 실패: {e}")
        import sys
        sys.print_exception(e)
        return False


def show_screen_menu():
    """화면 선택 메뉴 표시"""
    print("=" * 60)
    print("필박스 화면 테스트 메뉴")
    print("=" * 60)
    print("테스트할 화면을 선택하세요:")
    print()
    print("1.  스타트업 화면 (Startup Screen)")
    print("2.  Wi-Fi 스캔 화면 (Wi-Fi Scan Screen)")
    print("3.  Wi-Fi 비밀번호 화면 (Wi-Fi Password Screen)")
    print("4.  복용 횟수 설정(Dose Count Screen)")
    print("5.  복용 시간 설정(Dose Time Screen)")
    print("6.  알약 로딩 화면 (Pill Loading Screen) - 알약 충전")
    print("7.  메인 화면 (Main Screen) - 약품 배출 기능 + 테스트")
    print("8.  알림 화면 (Notification Screen) - Coming Soon")
    print("9.  설정 화면 (Settings Screen) - Coming Soon")
    print("10. 알약 배출 화면 (Pill Dispense Screen) - Coming Soon")
    print("11. 종료")
    print("=" * 60)
    


def main():
    """메인 함수 - 화면 테스트 메뉴"""
    print("=" * 60)
    print("필박스 화면 테스트 시스템")
    print("=" * 60)
    print("각 화면을 개별적으로 테스트할 수 있습니다!")
    print("Modern UI 스타일이 적용된 화면들을 확인하세요!")
    print()
    
    while True:
        try:
            show_screen_menu()
            choice = input("선택 (1-12): ").strip()
            
            if choice == '1':
                run_screen_test("startup")
            elif choice == '2':
                run_screen_test("wifi_scan")
            elif choice == '3':
                run_screen_test("wifi_password")
            elif choice == '4':
                run_screen_test("dose_count")
            elif choice == '5':
                run_screen_test("dose_time")
            elif choice == '6':
                run_screen_test("pill_loading")
            elif choice == '7':
                run_screen_test("main")
            elif choice == '8':
                run_screen_test("notification")
            elif choice == '9':
                run_screen_test("settings")
            elif choice == '10':
                run_screen_test("pill_dispense")
            elif choice == '11':
                print("🛑 프로그램을 종료합니다")
                break
            else:
                print("❌ 잘못된 선택입니다. 1-11 중 선택하세요.")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 프로그램이 중단되었습니다")
            cleanup_lvgl()
            break
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            import sys
            sys.print_exception(e)
            cleanup_lvgl()
            time.sleep(2)

if __name__ == "__main__":
    main()