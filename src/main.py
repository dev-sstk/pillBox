"""
필박스 통합 테스트
전체 시스템의 통합 테스트를 수행
"""

import sys
import os
import time
import lvgl as lv
import lv_utils
from machine import Pin, SPI
from st77xx import St7735

# ESP32에서 실행 시 경로 설정
# 루트를 sys.path에 추가
sys.path.append("/")
# screens/ 폴더를 sys.path에 추가
sys.path.append("/screens")

from pillbox_app import PillBoxApp
from audio_system import AudioSystem
from ui_style import UIStyle

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
        
        return True
        
    except Exception as e:
        print(f"❌ LVGL 설정 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_ui_style_system():
    """UI 스타일 시스템 테스트"""
    print("=" * 60)
    print("UI 스타일 시스템 테스트")
    print("=" * 60)
    
    try:
        # UI 스타일 생성
        ui_style = UIStyle()
        
        # 색상 테스트
        print("색상 테스트:")
        colors = ['primary', 'secondary', 'text', 'background', 'alert']
        for color_name in colors:
            color_value = ui_style.get_color(color_name)
            print(f"  {color_name}: #{color_value:06X}")
        
        # 폰트 테스트
        print("\n폰트 테스트:")
        fonts = ['title', 'subtitle', 'body', 'caption', 'korean']
        for font_name in fonts:
            font_obj = ui_style.get_font(font_name)
            print(f"  {font_name}: {font_obj}")
        
        # 스타일 객체 테스트
        print("\n스타일 객체 테스트:")
        styles = ['screen_bg', 'card', 'button', 'text_title', 'text_body']
        for style_name in styles:
            style_obj = ui_style.get_style(style_name)
            print(f"  {style_name}: {'✅' if style_obj else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ UI 스타일 시스템 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_audio_system_integration():
    """오디오 시스템 통합 테스트"""
    print("=" * 60)
    print("오디오 시스템 통합 테스트")
    print("=" * 60)
    
    try:
        # 오디오 시스템 생성
        audio_system = AudioSystem()
        
        # 시스템 정보 출력
        info = audio_system.get_audio_info()
        print("오디오 시스템 정보:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # 화면별 오디오 재생 시뮬레이션
        screen_flow = [
            ("startup", "wav_startup_hello.wav"),
            ("wifi_scan", "wav_wifi_scan_prompt.wav"),
            ("dose_count", "wav_dose_count_prompt.wav"),
            ("dose_time", "wav_dose_time_prompt.wav"),
            ("main", "wav_main_screen.wav"),
            ("notification", "wav_take_pill_prompt.wav")
        ]
        
        print("\n화면 플로우 오디오 재생 시뮬레이션:")
        for screen_name, audio_file in screen_flow:
            print(f"  {screen_name} 화면: {audio_file}")
            audio_system.play_voice(audio_file)
            time.sleep(0.1)
        
        # 버튼 상호작용 시뮬레이션
        print("\n버튼 상호작용 시뮬레이션:")
        interactions = [
            ("버튼 클릭", "wav_button_click.wav"),
            ("선택", "wav_select.wav"),
            ("조정", "wav_adjust.wav"),
            ("성공", "wav_success.wav"),
            ("오류", "wav_error.wav")
        ]
        
        for action, audio_file in interactions:
            print(f"  {action}: {audio_file}")
            audio_system.play_effect(audio_file)
            time.sleep(0.05)
        
        return True
        
    except Exception as e:
        print(f"❌ 오디오 시스템 통합 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_screen_navigation():
    """화면 네비게이션 테스트"""
    print("=" * 60)
    print("화면 네비게이션 테스트")
    print("=" * 60)
    
    try:
        # 필박스 앱 생성
        app = PillBoxApp()
        
        # 화면 관리자 가져오기
        screen_manager = app.get_screen_manager()
        
        # 화면 네비게이션 시뮬레이션
        navigation_flow = [
            "startup",
            "wifi_scan", 
            "wifi_password",
            "dose_count",
            "dose_time",
            "main",
            "settings",
            "pill_loading",
            "pill_dispense",
            "notification"
        ]
        
        print("화면 네비게이션 시뮬레이션:")
        for screen_name in navigation_flow:
            print(f"  화면 전환: {screen_name}")
            screen_manager.show_screen(screen_name)
            time.sleep(0.1)
        
        # 뒤로가기 테스트
        print("\n뒤로가기 테스트:")
        for i in range(3):
            print(f"  뒤로가기 {i+1}")
            screen_manager.go_back()
            time.sleep(0.1)
        
        return True
        
    except Exception as e:
        print(f"❌ 화면 네비게이션 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_complete_user_flow():
    """완전한 사용자 플로우 테스트"""
    print("=" * 60)
    print("완전한 사용자 플로우 테스트")
    print("=" * 60)
    
    try:
        # 필박스 앱 생성
        app = PillBoxApp()
        audio_system = app.get_audio_system()
        screen_manager = app.get_screen_manager()
        
        # 사용자 시나리오 시뮬레이션
        scenarios = [
            {
                "name": "초기 설정",
                "screens": ["startup", "wifi_scan", "wifi_password", "dose_count", "dose_time"],
                "audios": ["wav_startup_hello.wav", "wav_wifi_scan_prompt.wav", "wav_dose_count_prompt.wav"]
            },
            {
                "name": "일상 사용",
                "screens": ["main", "notification"],
                "audios": ["wav_main_screen.wav", "wav_take_pill_prompt.wav"]
            },
            {
                "name": "설정 관리",
                "screens": ["settings", "pill_loading", "pill_dispense"],
                "audios": ["wav_settings_prompt.wav", "wav_pill_loading_prompt.wav"]
            }
        ]
        
        for scenario in scenarios:
            print(f"\n{scenario['name']} 시나리오:")
            
            # 화면 전환
            for screen in scenario["screens"]:
                print(f"  화면: {screen}")
                screen_manager.show_screen(screen)
                time.sleep(0.1)
            
            # 오디오 재생
            for audio in scenario["audios"]:
                print(f"  오디오: {audio}")
                audio_system.play_voice(audio)
                time.sleep(0.1)
        
        return True
        
    except Exception as e:
        print(f"❌ 완전한 사용자 플로우 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def test_system_performance():
    """시스템 성능 테스트"""
    print("=" * 60)
    print("시스템 성능 테스트")
    print("=" * 60)
    
    try:
        # 메모리 사용량 테스트
        import gc
        gc.collect()
        initial_memory = gc.mem_free()
        print(f"초기 메모리: {initial_memory} bytes")
        
        # 필박스 앱 생성
        app = PillBoxApp()
        gc.collect()
        after_app_memory = gc.mem_free()
        print(f"앱 생성 후 메모리: {after_app_memory} bytes")
        print(f"앱 메모리 사용량: {initial_memory - after_app_memory} bytes")
        
        # 화면 전환 성능 테스트
        screen_manager = app.get_screen_manager()
        start_time = time.ticks_ms()
        
        test_screens = ["startup", "wifi_scan", "dose_count", "main", "settings"]
        for screen in test_screens:
            screen_manager.show_screen(screen)
        
        end_time = time.ticks_ms()
        total_time = time.ticks_diff(end_time, start_time)
        print(f"화면 전환 총 시간: {total_time}ms")
        print(f"화면당 평균 시간: {total_time / len(test_screens)}ms")
        
        # 오디오 시스템 성능 테스트
        audio_system = app.get_audio_system()
        start_time = time.ticks_ms()
        
        test_audios = ["wav_button_click.wav", "wav_select.wav", "wav_success.wav"]
        for audio in test_audios:
            audio_system.play_effect(audio)
        
        end_time = time.ticks_ms()
        total_time = time.ticks_diff(end_time, start_time)
        print(f"오디오 재생 총 시간: {total_time}ms")
        print(f"오디오당 평균 시간: {total_time / len(test_audios)}ms")
        
        # 최종 메모리 사용량
        gc.collect()
        final_memory = gc.mem_free()
        print(f"최종 메모리: {final_memory} bytes")
        print(f"총 메모리 사용량: {initial_memory - final_memory} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ 시스템 성능 테스트 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def run_pillbox_app():
    """실제 필박스 애플리케이션 실행"""
    print("=" * 60)
    print("필박스 애플리케이션 시작")
    print("=" * 60)
    
    try:
        # LVGL 환경 설정
        if not setup_lvgl():
            print("❌ LVGL 환경 설정 실패")
            return False
        
        # 필박스 앱 생성 및 실행
        app = PillBoxApp()
        
        # 화면 등록
        print("📱 화면 등록 시작...")
        from screens.startup_screen import StartupScreen
        from screens.wifi_scan_screen import WifiScanScreen
        from screens.wifi_password_screen import WifiPasswordScreen
        from screens.dose_count_screen import DoseCountScreen
        from screens.dose_time_screen import DoseTimeScreen
        from screens.main_screen import MainScreen
        from screens.notification_screen import NotificationScreen
        from screens.settings_screen import SettingsScreen
        from screens.pill_loading_screen import PillLoadingScreen
        from screens.pill_dispense_screen import PillDispenseScreen
        
        # 각 화면을 개별적으로 등록하여 오류 추적
        try:
            print("📱 startup 화면 등록...")
            app.screen_manager.register_screen("startup", StartupScreen(app.screen_manager))
            print("✅ startup 화면 등록 완료")
        except Exception as e:
            print(f"❌ startup 화면 등록 실패: {e}")
            return False
            
        try:
            print("📱 wifi_scan 화면 등록...")
            app.screen_manager.register_screen("wifi_scan", WifiScanScreen(app.screen_manager))
            print("✅ wifi_scan 화면 등록 완료")
        except Exception as e:
            print(f"❌ wifi_scan 화면 등록 실패: {e}")
            return False
            
        try:
            print("📱 wifi_password 화면 등록...")
            app.screen_manager.register_screen("wifi_password", WifiPasswordScreen(app.screen_manager, "Example_SSID"))
            print("✅ wifi_password 화면 등록 완료")
        except Exception as e:
            print(f"❌ wifi_password 화면 등록 실패: {e}")
            return False
            
        try:
            print("📱 dose_count 화면 등록...")
            app.screen_manager.register_screen("dose_count", DoseCountScreen(app.screen_manager))
            print("✅ dose_count 화면 등록 완료")
        except Exception as e:
            print(f"❌ dose_count 화면 등록 실패: {e}")
            return False
            
        try:
            print("📱 dose_time 화면 등록...")
            app.screen_manager.register_screen("dose_time", DoseTimeScreen(app.screen_manager, dose_count=2))
            print("✅ dose_time 화면 등록 완료")
        except Exception as e:
            print(f"❌ dose_time 화면 등록 실패: {e}")
            return False
            
        try:
            print("📱 main_screen 화면 등록...")
            app.screen_manager.register_screen("main_screen", MainScreen(app.screen_manager))
            print("✅ main_screen 화면 등록 완료")
        except Exception as e:
            print(f"❌ main_screen 화면 등록 실패: {e}")
            return False
            
        try:
            print("📱 notification 화면 등록...")
            app.screen_manager.register_screen("notification", NotificationScreen(app.screen_manager, {"time": "10:00", "pills": ["Test Pill"]}))
            print("✅ notification 화면 등록 완료")
        except Exception as e:
            print(f"❌ notification 화면 등록 실패: {e}")
            return False
            
        try:
            print("📱 settings 화면 등록...")
            app.screen_manager.register_screen("settings", SettingsScreen(app.screen_manager))
            print("✅ settings 화면 등록 완료")
        except Exception as e:
            print(f"❌ settings 화면 등록 실패: {e}")
            return False
            
        try:
            print("📱 pill_loading 화면 등록...")
            app.screen_manager.register_screen("pill_loading", PillLoadingScreen(app.screen_manager))
            print("✅ pill_loading 화면 등록 완료")
        except Exception as e:
            print(f"❌ pill_loading 화면 등록 실패: {e}")
            return False
            
        try:
            print("📱 pill_dispense 화면 등록...")
            app.screen_manager.register_screen("pill_dispense", PillDispenseScreen(app.screen_manager))
            print("✅ pill_dispense 화면 등록 완료")
        except Exception as e:
            print(f"❌ pill_dispense 화면 등록 실패: {e}")
            return False
        
        # 시작 화면으로 이동
        print("📱 시작 화면으로 이동...")
        app.screen_manager.set_current_screen("startup")
        
        print("✅ 필박스 애플리케이션 시작됨")
        print("Ctrl+C로 종료하세요")
        
        # 메인 루프 실행
        app.start()
        
        return True
        
    except Exception as e:
        print(f"❌ 필박스 애플리케이션 실행 실패: {e}")
        import sys
        sys.print_exception(e)
        return False

def main():
    """메인 함수"""
    print("=" * 60)
    print("필박스 시스템")
    print("=" * 60)
    print("1. 필박스 애플리케이션 실행")
    print("2. UI 스타일 시스템 테스트")
    print("3. 오디오 시스템 통합 테스트")
    print("4. 화면 네비게이션 테스트")
    print("5. 완전한 사용자 플로우 테스트")
    print("6. 시스템 성능 테스트")
    print("7. 모든 테스트 실행")
    print("8. 종료")
    
    while True:
        try:
            choice = input("\n선택 (1-8): ").strip()
            
            if choice == '1':
                run_pillbox_app()
            elif choice == '2':
                test_ui_style_system()
            elif choice == '3':
                test_audio_system_integration()
            elif choice == '4':
                test_screen_navigation()
            elif choice == '5':
                test_complete_user_flow()
            elif choice == '6':
                test_system_performance()
            elif choice == '7':
                print("모든 테스트 실행 중...")
                test_ui_style_system()
                print("\n" + "="*60)
                test_audio_system_integration()
                print("\n" + "="*60)
                test_screen_navigation()
                print("\n" + "="*60)
                test_complete_user_flow()
                print("\n" + "="*60)
                test_system_performance()
                print("\n✅ 모든 통합 테스트 완료")
            elif choice == '8':
                print("시스템 종료")
                break
            else:
                print("잘못된 선택입니다. 1-8 중 선택하세요.")
                
        except KeyboardInterrupt:
            print("\n테스트 중단됨")
            break
        except Exception as e:
            print(f"오류 발생: {e}")
            import sys
            sys.print_exception(e)

if __name__ == "__main__":
    main()