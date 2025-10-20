"""
Wi-Fi 비밀번호 입력 화면
LVGL 기본 키보드 매핑을 활용한 버튼 매트릭스로 구현
"""

import lvgl as lv
import time
from ui_style import UIStyle

class WifiPasswordScreen:
    def __init__(self, screen_manager, selected_network="Wi-Fi 네트워크"):
        # 메모리 모니터링
        from memory_monitor import log_memory
        log_memory("WifiPasswordScreen 초기화 시작")
        
        # 메모리 정리
        import gc
        gc.collect()
        
        self.screen_manager = screen_manager
        self.screen_name = "wifi_password"
        self.selected_network = selected_network
        self._password = ""
        
        # 지연 로딩을 위한 캐시
        self.ui_style = None
        self.screen_obj = None
        self._initialized = False
        
        log_memory("WifiPasswordScreen 초기화 완료")
        print("[OK] WifiPasswordScreen 초기화 완료 (메모리 최적화 적용)")
    
    def _get_ui_style(self):
        """UI 스타일 지연 로딩"""
        if self.ui_style is None:
            self.ui_style = UIStyle()
            print("[DEBUG] UI 스타일 지연 로딩 완료")
        return self.ui_style
    
    def _create_modern_screen(self):
        """Modern 스타일 화면 생성"""
       
        try:
            # [FAST] 메모리 부족 해결: 더 강력한 메모리 정리
            import gc
            for i in range(15):  # 15회 가비지 컬렉션 (더 강력하게)
                gc.collect()
                time.sleep(0.03)  # 0.03초 대기 (더 오래)
            
            # 화면 생성
            self.screen_obj = lv.obj()
           
            # 화면 배경 스타일 적용 (Modern 스타일)
            self._get_ui_style().apply_screen_style(self.screen_obj)
            
            # 스크롤바 비활성화
            self.screen_obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.screen_obj.set_scroll_dir(lv.DIR.NONE)  # 스크롤 방향 비활성화
            
            # 화면 크기 설정
            self.screen_obj.set_size(160, 128)
            
            # 메인 컨테이너 생성
            self.main_container = lv.obj(self.screen_obj)
            self.main_container.set_size(160, 128)
            self.main_container.align(lv.ALIGN.CENTER, 0, 0)
            self.main_container.set_style_bg_opa(0, 0)  # 투명 배경
            self.main_container.set_style_border_width(0, 0)  # 테두리 없음
            
            # 스크롤바 비활성화
            self.main_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.main_container.set_scroll_dir(lv.DIR.NONE)  # 스크롤 방향 비활성화
            
            # 네트워크명 제목 영역 생성
            self._create_network_title_area()
            
            # 비밀번호 입력 영역 생성
            self._create_password_area()
            
            # 키보드 영역 생성
            self._create_keyboard_area()
            
            # 버튼 힌트 영역 생성 (간단한 방식)
            self._create_simple_button_hints()           
         
        except Exception as e:
            import sys
            sys.print_exception(e)
            raise e  # 상위로 예외 전파
    
    def _create_basic_screen(self):
        """기본 화면 생성 (오류 시 대안)"""
        
        # 기본 화면 객체 생성
        self.screen_obj = lv.obj()
        self.screen_obj.set_size(160, 128)
        
        # 기본 라벨 생성
        self.title_label = lv.label(self.screen_obj)
        self.title_label.set_text(f"Wi-Fi 비밀번호\n{self.selected_network}")
        self.title_label.align(lv.ALIGN.CENTER, 0, 0)  # 6픽셀 더 아래로 이동 (-6 -> 0)
        
        # 기본 버튼 힌트 생성 (메모리 절약을 위해 간단하게)
        try:
            self.hints_label = lv.label(self.screen_obj)
            # LVGL 심볼 사용 (기본 폰트에서 지원)
            self.hints_label.set_text(f"A:{lv.SYMBOL.LEFT} B:{lv.SYMBOL.RIGHT} C:{lv.SYMBOL.CLOSE} D:{lv.SYMBOL.OK}")
            self.hints_label.align(lv.ALIGN.BOTTOM_MID, 0, -2)  # Wi-Fi 스캔 화면과 동일한 위치
            self.hints_label.set_style_text_color(lv.color_hex(0x8E8E93), 0)
            self.hints_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        except Exception as e:
            print(f"  [WARN] 기본 버튼 힌트 생성 실패: {e}")
        
    
    def _create_network_title_area(self):
        """네트워크명 제목 영역 생성"""
        try:
            # 네트워크 제목 컨테이너
            self.network_title_container = lv.obj(self.main_container)
            self.network_title_container.set_size(160, 25)
            self.network_title_container.align(lv.ALIGN.TOP_MID, 0, -16)  # 6픽셀 더 아래로 이동 (-22 -> -16)
            self.network_title_container.set_style_bg_opa(0, 0)
            self.network_title_container.set_style_border_width(0, 0)
            
            # 네트워크 제목 컨테이너 스크롤바 비활성화
            self.network_title_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.network_title_container.set_scroll_dir(lv.DIR.NONE)
            
            
            # 선택된 네트워크 SSID만 표시 (간단하게)
            self.network_title_text = lv.label(self.network_title_container)
            self.network_title_text.set_text(self.selected_network)
            self.network_title_text.align(lv.ALIGN.CENTER, 0, 0)
            self.network_title_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            self.network_title_text.set_style_text_color(lv.color_hex(0x0066CC), 0)
            
            # 한국어 폰트 적용
            korean_font = getattr(lv, "font_notosans_kr_regular", None)
            if korean_font:
                self.network_title_text.set_style_text_font(korean_font, 0)
            
            
        except Exception as e:
            # 기본 네트워크 제목 생성
            try:
                self.network_title_text = lv.label(self.main_container)
                self.network_title_text.set_text(f"Wi-Fi 비밀번호\n{self.selected_network}")
                self.network_title_text.align(lv.ALIGN.TOP_MID, 0, 5)
            except Exception as e2:
                print(f"  [ERROR] 기본 네트워크 제목 생성도 실패: {e2}")
    
    def _create_password_area(self):
        """비밀번호 입력 영역 생성"""
        try:
            # 패스워드 입력 컨테이너 생성
            self.password_container = lv.obj(self.main_container)
            self.password_container.set_size(160, 24)  # 높이를 4픽셀 늘림 (20 -> 24)
            self.password_container.align(lv.ALIGN.TOP_MID, 0, 8)  # 2픽셀 더 아래로 이동 (6 -> 8)
            self.password_container.set_style_bg_opa(0, 0)  # 투명 배경
            self.password_container.set_style_border_width(0, 0)
            self.password_container.set_style_pad_all(0, 0)
            
            # 스크롤바 비활성화
            self.password_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.password_container.set_scroll_dir(lv.DIR.NONE)
            
            # 텍스트 영역 생성 (110픽셀로 설정)
            self.textarea = lv.textarea(self.password_container)
            self.textarea.set_size(110, 24)  # 높이를 4픽셀 늘림 (20 -> 24)
            self.textarea.align(lv.ALIGN.LEFT_MID, 0, 0)  # 왼쪽에 정렬
            self.textarea.set_placeholder_text("Password")
            self.textarea.set_one_line(True)
            self.textarea.set_password_mode(False)  # 비밀번호 모드 해제 (텍스트 그대로 표시)
            
            # 텍스트 영역 스타일
            self.textarea.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
            self.textarea.set_style_border_width(0, 0)  # 테두리 제거
            
            # 텍스트 영역 스크롤바 비활성화
            self.textarea.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.textarea.set_scroll_dir(lv.DIR.NONE)
            self.textarea.set_style_text_color(lv.color_hex(0x333333), 0)
            self.textarea.set_style_radius(5, 0)
            self.textarea.set_style_pad_all(5, 0)
            
            # 한국어 폰트 적용
            korean_font = getattr(lv, "font_notosans_kr_regular", None)
            if korean_font:
                self.textarea.set_style_text_font(korean_font, 0)
            
            # 미리보기 라벨 생성 (오른쪽에 50픽셀 길이)
            self.preview_label = lv.label(self.password_container)
            self.preview_label.set_size(50, 24)  # 높이를 4픽셀 늘림 (20 -> 24)
            self.preview_label.align(lv.ALIGN.RIGHT_MID, 0, 0)  # 오른쪽에 정렬
            self.preview_label.set_text("q")  # 기본값으로 q 표시
            self.preview_label.set_style_text_color(lv.color_hex(0x000000), 0)  # 검정색
            self.preview_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            self.preview_label.set_style_bg_color(lv.color_hex(0xF0F0F0), 0)  # 연한 회색 배경
            self.preview_label.set_style_border_width(1, 0)  # 테두리 추가
            self.preview_label.set_style_border_color(lv.color_hex(0x999999), 0)  # 더 밝은 회색으로 시도
            # 테두리 색상을 강제로 적용하기 위해 추가 설정
            self.preview_label.set_style_border_opa(255, 0)  # 테두리 불투명도 설정
            self.preview_label.set_style_radius(5, 0)
            self.preview_label.set_style_pad_all(2, 0)
            
            # 미리보기 라벨 스크롤바 비활성화
            self.preview_label.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.preview_label.set_scroll_dir(lv.DIR.NONE)
            
            # 한국어 폰트 적용
            if korean_font:
                self.preview_label.set_style_text_font(korean_font, 0)
            
            
        except Exception as e:
            print(f"  [ERROR] 비밀번호 입력 영역 생성 실패: {e}")
            import sys
            sys.print_exception(e)
            # 기본 텍스트 영역 생성
            try:
                self.textarea = lv.textarea(self.main_container)
                self.textarea.set_size(140, 20)
                self.textarea.align(lv.ALIGN.TOP_MID, 0, 30)
                self.textarea.set_placeholder_text("Password")
                self.textarea.set_password_mode(True)
            except Exception as e2:
                print(f"  [ERROR] 기본 텍스트 영역 생성도 실패: {e2}")
    
    def _create_keyboard_area(self):
        """텍스트 기반 키보드 영역 생성"""
        
        try:
            print("  [INFO] 키보드 컨테이너 생성 중...")
            # 키보드 컨테이너 생성
            self.keyboard_container = lv.obj(self.main_container)
            self.keyboard_container.set_size(160, 60)  # 높이 증가로 키보드 잘림 방지
            self.keyboard_container.align(lv.ALIGN.CENTER, 0, 16)  # 4픽셀 아래로 이동 (12 -> 16)
            self.keyboard_container.set_style_bg_opa(0, 0)  # 투명 배경
            self.keyboard_container.set_style_border_width(0, 0)
            
            # 스크롤바 비활성화
            self.keyboard_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.keyboard_container.set_scroll_dir(lv.DIR.NONE)  # 스크롤 방향 비활성화
            
            # 텍스트 기반 키보드 초기화
            self.keyboard_mode = "lower"  # lower, upper, numbers, symbols
            self.selected_row = 0
            self.selected_col = 0
            
            # 간단한 키보드 레이아웃 정의
            self.keyboard_layouts = {
                "lower": [
                    ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
                    ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
                    ["z", "x", "c", "v", "b", "n", "m"],
                    ["ABC", "DEL", "123", "OK"]
                ],
                "upper": [
                    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
                    ["Z", "X", "C", "V", "B", "N", "M"],
                    ["abc", "DEL", "123", "OK"]
                ],
                "numbers": [
                    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                    ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")"],
                    ["-", "_", "+", "=", "[", "]", "{", "}", "\\", "|"],
                    ["abc", "DEL", "OK"]
                ]
            }
            
            
            # 키보드 그리기
            self._draw_keyboard()
            
            
        except Exception as e:
            print(f"  [ERROR] 텍스트 기반 키보드 생성 실패: {e}")
            print(f"  [INFO] 에러 타입: {type(e).__name__}")
            import sys
            sys.print_exception(e)
    
    def _draw_keyboard(self):
        """키보드 표시 (일반 텍스트)"""
        
        try:
            # 현재 모드의 레이아웃 가져오기
            layout = self.keyboard_layouts[self.keyboard_mode]
            
            # 키보드 텍스트 생성 (일반 텍스트)
            keyboard_text = ""
            for row_idx, row in enumerate(layout):
                # 키보드 모드에 따라 간격 조정
                if self.keyboard_mode == "upper":
                    # 대문자 모드: 간격을 줄여서 글자 잘림 방지
                    row_text = " ".join(row)  # 공백 1개
                else:
                    # 소문자, 숫자 모드: 원래 간격 유지
                    row_text = "  ".join(row)  # 공백 2개
                keyboard_text += row_text + "\n"
            
            # 키보드 텍스트 라벨 생성
            self.keyboard_label = lv.label(self.keyboard_container)
            self.keyboard_label.set_text(keyboard_text.strip())
            self.keyboard_label.align(lv.ALIGN.CENTER, 0, 0)
            self.keyboard_label.set_style_text_color(lv.color_hex(0x333333), 0)
            self.keyboard_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            
            # 키보드 라벨 스크롤바 비활성화
            self.keyboard_label.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.keyboard_label.set_scroll_dir(lv.DIR.NONE)
            
            # 미리보기 라벨 업데이트
            self._update_preview_label()
            
            
        except Exception as e:
            print(f"  [ERROR] 키보드 표시 실패: {e}")
            import sys
            sys.print_exception(e)
    
    
    def _update_network_display(self, network_name):
        """네트워크 표시 업데이트"""
        self.selected_network = network_name
        if hasattr(self, 'network_title_text'):
            self.network_title_text.set_text(network_name)
        print(f"네트워크 표시 업데이트: {network_name}")
    
    def show(self):
        """화면 표시"""
        
        # [FAST] 메모리 부족 해결: 지연 초기화 (show() 시점에 화면 생성)
        if not self._initialized:
            
            # [FAST] 메모리 부족 해결: show() 시점 메모리 정리
            import gc
            for i in range(10):  # 10회 가비지 컬렉션
                gc.collect()
                time.sleep(0.02)  # 0.02초 대기
            
            try:
                self._create_modern_screen()
                self._initialized = True
            except Exception as e:
                print(f"[ERROR] {self.screen_name} 지연 초기화 실패: {e}")
                # [FAST] 메모리 할당 실패 시 추가 메모리 정리
                print(f"🧹 지연 초기화 실패 후 추가 메모리 정리...")
                for i in range(5):
                    gc.collect()
                    time.sleep(0.01)
                print(f"[OK] 추가 메모리 정리 완료")
                
                # 기본 화면으로 대체
                try:
                    self._create_basic_screen()
                    self._initialized = True
                except Exception as e2:
                    return
        
        if hasattr(self, 'screen_obj') and self.screen_obj:
            
            # 네트워크 제목 업데이트
            if hasattr(self, 'network_title_text') and hasattr(self, 'selected_network'):
                self.network_title_text.set_text(self.selected_network)
            
            lv.screen_load(self.screen_obj)
            
            # 화면 강제 업데이트
            for i in range(5):
                lv.timer_handler()
                time.sleep(0.01)
            
            # 디스플레이 플러시
            try:
                lv.disp_drv_t.flush_ready(None)
            except AttributeError:
                try:
                    lv.disp_t.flush_ready(None)
                except AttributeError:
                    print("[WARN] 디스플레이 플러시 오류 (무시): 'module' object has no attribute 'disp_t'")
            
        else:
            print(f"[ERROR] {self.screen_name} 화면 객체가 없음")
    
    def update(self):
        # 현재는 특별한 업데이트 로직이 없음
        pass
    
    
    def _attempt_connection(self):
        """Wi-Fi 연결 시도"""
        
        try:
            # 실제 WiFi 연결 시도
            from wifi_manager import get_wifi_manager
            
            # WiFi 연결 시도
            wifi_mgr = get_wifi_manager()
            success = wifi_mgr.connect_to_network(self.selected_network, self._password)
            
            if success:
                time.sleep(1)
                
                # WiFi 연결 성공 시 다음 화면으로 전환
                print("[INFO] WiFi 연결 성공 - 다음 화면으로 전환")
                self._request_screen_transition('meal_time')
            else:
                print("[ERROR] WiFi 연결 실패!")
                # 연결 실패 시 현재 화면에 머물기 (팝업 제거)
                
        except Exception as e:
            print(f"[ERROR] WiFi 연결 오류: {e}")
            # 연결 오류 시 현재 화면에 머물기 (팝업 제거)
    
    
    
    def on_button_a(self):
        """버튼 A - 키보드 왼쪽으로 이동"""
        try:
            print("[DEBUG] WifiPasswordScreen on_button_a 호출됨")
            
            # 화면이 초기화되었는지 확인
            if not hasattr(self, 'keyboard_layouts') or not hasattr(self, 'keyboard_mode'):
                print("[WARN] WifiPasswordScreen이 아직 초기화되지 않음, 버튼 A 무시")
                return
            
            # 추가 안전성 검사
            if not hasattr(self, 'selected_row') or not hasattr(self, 'selected_col'):
                print("[WARN] WifiPasswordScreen 키보드 상태가 초기화되지 않음, 버튼 A 무시")
                return
            
            print("[DEBUG] WifiPasswordScreen 키보드 커서 왼쪽으로 이동")
            self._move_keyboard_cursor('left')
        except Exception as e:
            print(f"[ERROR] 버튼 A 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def on_button_b(self):
        """버튼 B - 키보드 오른쪽으로 이동"""
        try:
            print("[DEBUG] WifiPasswordScreen on_button_b 호출됨")
            
            # 화면이 초기화되었는지 확인
            if not hasattr(self, 'keyboard_layouts') or not hasattr(self, 'keyboard_mode'):
                print("[WARN] WifiPasswordScreen이 아직 초기화되지 않음, 버튼 B 무시")
                return
            
            # 추가 안전성 검사
            if not hasattr(self, 'selected_row') or not hasattr(self, 'selected_col'):
                print("[WARN] WifiPasswordScreen 키보드 상태가 초기화되지 않음, 버튼 B 무시")
                return
            
            print("[DEBUG] WifiPasswordScreen 키보드 커서 오른쪽으로 이동")
            self._move_keyboard_cursor('right')
        except Exception as e:
            print(f"[ERROR] 버튼 B 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def on_button_c(self):
        """버튼 C - 완료/뒤로가기"""
        try:
            print("[DEBUG] WifiPasswordScreen on_button_c 호출됨")
            print("완료/뒤로가기")
            
            # 비밀번호가 입력되어 있으면 연결 시도
            if hasattr(self, '_password') and self._password:
                print("[DEBUG] 비밀번호가 입력됨, 연결 시도")
                self._attempt_connection()
            else:
                print("[DEBUG] 비밀번호가 입력되지 않음, wifi_scan으로 돌아가기")
                self._request_screen_transition('wifi_scan')
        except Exception as e:
            print(f"[ERROR] 버튼 C 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def on_button_d(self):
        """버튼 D - 키보드 키 선택/입력"""
        try:
            print("[DEBUG] WifiPasswordScreen on_button_d 호출됨")
            
            # 화면이 초기화되었는지 확인
            if not hasattr(self, 'keyboard_layouts') or not hasattr(self, 'keyboard_mode'):
                print("[WARN] WifiPasswordScreen이 아직 초기화되지 않음, 버튼 D 무시")
                return
            
            # 추가 안전성 검사
            if not hasattr(self, 'selected_row') or not hasattr(self, 'selected_col'):
                print("[WARN] WifiPasswordScreen 키보드 상태가 초기화되지 않음, 버튼 D 무시")
                return
            
            print("[DEBUG] WifiPasswordScreen 키보드 키 선택/입력")
            self._press_current_keyboard_key()
        except Exception as e:
            print(f"[ERROR] 버튼 D 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _move_keyboard_cursor(self, direction):
        """텍스트 기반 키보드 커서 이동"""
        
        try:
            layout = self.keyboard_layouts[self.keyboard_mode]
            max_row = len(layout) - 1
            max_col = len(layout[self.selected_row]) - 1
            
            # 이전 위치 저장
            old_row = self.selected_row
            old_col = self.selected_col
            
            if direction == 'left':
                # 왼쪽으로 이동
                if self.selected_col > 0:
                    self.selected_col -= 1
                else:
                    # 현재 행의 첫 번째 열에서 왼쪽으로 가면 이전 행의 마지막 열로
                    if self.selected_row > 0:
                        self.selected_row -= 1
                        self.selected_col = len(layout[self.selected_row]) - 1
                    else:
                        # 첫 번째 행이면 마지막 행의 마지막 열로
                        self.selected_row = max_row
                        self.selected_col = len(layout[self.selected_row]) - 1
            
            elif direction == 'right':
                # 오른쪽으로 이동
                if self.selected_col < max_col:
                    self.selected_col += 1
                else:
                    # 현재 행의 마지막 열에서 오른쪽으로 가면 다음 행으로
                    if self.selected_row < max_row:
                        self.selected_row += 1
                        self.selected_col = 0
                    else:
                        # 마지막 행이면 첫 번째 행의 첫 번째 열(q)로
                        self.selected_row = 0
                        self.selected_col = 0
            
            # 선택 표시 업데이트
            self._update_selection_display()
            
            # 현재 선택된 키 정보 출력
            current_key = layout[self.selected_row][self.selected_col]
            
        except Exception as e:
            print(f"  [ERROR] 키보드 커서 이동 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _press_current_keyboard_key(self):
        """텍스트 기반 키보드 키 입력"""
        
        try:
            layout = self.keyboard_layouts[self.keyboard_mode]
            current_key = layout[self.selected_row][self.selected_col]
            
            # 키 타입에 따른 처리
            input_chars = [
                # 영문 소문자
                'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p',
                                       'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l',
                                       'z', 'x', 'c', 'v', 'b', 'n', 'm',
                # 영문 대문자
                                       'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P',
                                       'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L',
                                       'Z', 'X', 'C', 'V', 'B', 'N', 'M',
                # 숫자
                                       '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                # 특수문자
                                       '!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
                '-', '_', '+', '=', '[', ']', '{', '}', '\\', '|'
            ]
            
            if current_key in input_chars:
                                # 문자 입력
                self._add_character(current_key)
            
            elif current_key == 'DEL':
                                # 백스페이스
                self._handle_backspace()
            
            elif current_key == 'OK':
                                # 엔터 (완료)
                self._handle_ok()
            
            elif current_key == '123':
                # 숫자 모드 전환
                self._switch_to_numbers_mode()
                            
            elif current_key == 'ABC':
                # 대소문자 전환
                self._switch_case_mode()
                            
            elif current_key == 'abc':
                # 소문자 모드로 전환
                self.keyboard_mode = "lower"
                self.selected_row = 0
                self.selected_col = 0
                self._redraw_keyboard()
            
            
        except Exception as e:
            print(f"  [ERROR] 키 입력 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _switch_to_numbers_mode(self):
        """숫자 모드로 전환"""
        self.keyboard_mode = "numbers"
        self.selected_row = 0
        self.selected_col = 0
        self._redraw_keyboard()
    
    def _switch_case_mode(self):
        """대소문자 모드 전환"""
        
        if self.keyboard_mode == "lower":
            self.keyboard_mode = "upper"
        else:
            self.keyboard_mode = "lower"
        
        self.selected_row = 0
        self.selected_col = 0
        self._redraw_keyboard()
    
    
    def _redraw_keyboard(self):
        """키보드 다시 그리기 (선택된 문자 볼드체)"""
        
        try:
            # 기존 라벨 제거
            if hasattr(self, 'keyboard_label'):
                self.keyboard_label.delete()
            
            # 키보드 다시 그리기
            self._draw_keyboard()
            
            
        except Exception as e:
            print(f"  [ERROR] 키보드 다시 그리기 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _update_preview_label(self):
        """미리보기 라벨 업데이트"""
        try:
            if hasattr(self, 'preview_label'):
                # 현재 선택된 문자 가져오기
                layout = self.keyboard_layouts[self.keyboard_mode]
                current_char = layout[self.selected_row][self.selected_col]
                
                # 미리보기 라벨에 현재 선택된 문자 표시
                self.preview_label.set_text(current_char)
        except Exception as e:
            print(f"  [ERROR] 미리보기 업데이트 실패: {e}")
    
    def _update_selection_display(self):
        """선택 표시 업데이트 (미리보기 라벨만 업데이트)"""
        try:
            # 미리보기 라벨만 업데이트 (키보드는 다시 그리지 않음)
            self._update_preview_label()
        except Exception as e:
            print(f"  [ERROR] 선택 업데이트 실패: {e}")
    
    def _handle_backspace(self):
        """백스페이스 처리"""
        
        try:
            # 내부 텍스트에서 마지막 문자 제거
            if hasattr(self, '_internal_text') and len(self._internal_text) > 0:
                self._internal_text = self._internal_text[:-1]
                
                # textarea 업데이트 (실제 텍스트로 표시)
                if hasattr(self, 'textarea'):
                    try:
                        self.textarea.set_text(self._internal_text)
                    except Exception as e:
                        print(f"  [WARN] textarea 업데이트 실패: {e}")
            else:
                print("  [INFO] 백스페이스: 텍스트가 비어있음")
                
        except Exception as e:
            print(f"  [ERROR] 백스페이스 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _handle_ok(self):
        """OK 버튼 처리 (입력 완료)"""
        
        try:
            current_text = ""
            
            # textarea에서 텍스트 가져오기
            if hasattr(self, 'textarea'):
                try:
                    current_text = self.textarea.get_text()
                except Exception as text_e:
                    print(f"  [WARN] textarea 텍스트 가져오기 실패: {text_e}")
            
            # 내부 텍스트도 확인 (더 길면 우선 사용)
            if hasattr(self, '_internal_text'):
                if len(self._internal_text) > len(current_text):
                    current_text = self._internal_text
            
            # 비밀번호 길이 검증
            if len(current_text) >= 8:
                self._password = current_text  # 비밀번호 저장
                self._attempt_connection()
            elif len(current_text) > 0:
                # 짧은 비밀번호도 허용 (실제 환경에서는 더 유연하게)
                self._password = current_text
                self._attempt_connection()
            else:
                # 빈 비밀번호도 연결 시도 (개방형 네트워크일 수 있음)
                self._password = ""
                self._attempt_connection()
                
        except Exception as e:
            print(f"  [ERROR] OK 버튼 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _add_character(self, char):
        """문자 추가 (안전한 방식)"""
        
        try:
            # 내부 텍스트로만 관리
            if not hasattr(self, '_internal_text'):
                self._internal_text = ""
            
            # 문자 추가 (안전하게)
            self._internal_text += str(char)
            
            # textarea 업데이트 (실제 텍스트로 표시)
            if hasattr(self, 'textarea'):
                try:
                    self.textarea.set_text(self._internal_text)
                except Exception as e:
                    print(f"  [WARN] textarea 업데이트 실패: {e}")
                
        except Exception as e:
            print(f"  [ERROR] 문자 추가 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _create_simple_button_hints(self):
        """간단한 버튼 힌트 생성 - 메모리 절약"""
        try:
            # 화면에 직접 라벨 생성 (컨테이너 없이)
            self.hints_label = lv.label(self.screen_obj)
            # LVGL 심볼 사용 (기본 폰트에서 지원)
            self.hints_label.set_text(f"A:{lv.SYMBOL.LEFT} B:{lv.SYMBOL.RIGHT} C:{lv.SYMBOL.CLOSE} D:{lv.SYMBOL.OK}")
            self.hints_label.align(lv.ALIGN.BOTTOM_MID, 0, -2)  # Wi-Fi 스캔 화면과 동일한 위치
            self.hints_label.set_style_text_color(lv.color_hex(0x8E8E93), 0)
            self.hints_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            
        except Exception as e:
            print(f"  [ERROR] 간단한 버튼 힌트 생성 중 오류: {e}")
            import sys
            sys.print_exception(e)
    
    def _create_button_hints_area(self):
        """하단 버튼 힌트 영역 생성 - Modern 스타일 (사용 안함)"""
        try:
            # 버튼 힌트 컨테이너
            self.hints_container = lv.obj(self.main_container)
            self.hints_container.set_size(140, 18)
            self.hints_container.align(lv.ALIGN.BOTTOM_MID, 0, 0)
            # 투명 배경 (Modern 스타일)
            self.hints_container.set_style_bg_opa(0, 0)
            self.hints_container.set_style_border_width(0, 0)
            self.hints_container.set_style_pad_all(0, 0)
            
            # 버튼 힌트 텍스트 (Modern 스타일) - 모던 UI 색상
            self.hints_text = self.ui_style.create_label(
                self.hints_container,
                "A:←  B:→  C:×  D:✓",
                'text_caption',
                0x8E8E93  # 모던 라이트 그레이
            )
            self.hints_text.align(lv.ALIGN.CENTER, 0, 0)
            # 버튼 힌트 텍스트 위치 고정 (움직이지 않도록)
            self.hints_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            
            
        except Exception as e:
            print(f"  [ERROR] 버튼 힌트 영역 생성 중 오류: {e}")
            import sys
            sys.print_exception(e)
    
    def _cleanup_references(self):
        """참조 정리 - 메모리 최적화"""
        try:
            print("[INFO] WifiPasswordScreen 참조 정리 시작...")
            
            # UI 스타일 참조 정리
            if self.ui_style:
                self.ui_style = None
                print("[DEBUG] UI 스타일 참조 정리")
            
            # 화면 객체 참조 정리
            if self.screen_obj:
                self.screen_obj = None
                print("[DEBUG] 화면 객체 참조 정리")
            
            print("[OK] WifiPasswordScreen 참조 정리 완료")
            
        except Exception as e:
            print(f"[WARN] 참조 정리 실패: {e}")
    
    def _request_screen_transition(self, screen_name):
        """화면 전환 요청 - ScreenManager에 위임 (StartupScreen과 동일한 방식)"""
        print(f"[INFO] 화면 전환 요청: {screen_name}")
        
        # ScreenManager에 화면 전환 요청 (올바른 책임 분리)
        try:
            self.screen_manager.transition_to(screen_name)
            print(f"[OK] 화면 전환 요청 완료: {screen_name}")
        except Exception as e:
            print(f"[ERROR] 화면 전환 요청 실패: {e}")
            import sys
            sys.print_exception(e)
        
        # 화면 전환 (올바른 책임 분리 - ScreenManager가 처리)
        print("[INFO] WiFi 비밀번호 입력 완료 - ScreenManager에 완료 신호 전송")
        
        # ScreenManager에 WiFi 비밀번호 입력 완료 신호 전송 (올바른 책임 분리)
        try:
            self.screen_manager.wifi_password_completed(screen_name)
            print("[OK] WiFi 비밀번호 입력 완료 신호 전송 완료")
        except Exception as e:
            print(f"[ERROR] WiFi 비밀번호 입력 완료 신호 전송 실패: {e}")
            import sys
            sys.print_exception(e)

    def _force_garbage_collection(self):
        """강제 가비지 컬렉션 - 표준화된 시스템 사용"""
        try:
            from memory_utils import quick_garbage_collection
            
            print("[INFO] WifiPasswordScreen 강제 가비지 컬렉션 시작")
            
            # 표준화된 빠른 가비지 컬렉션 사용
            result = quick_garbage_collection("WifiPasswordScreen")
            
            print("[OK] WifiPasswordScreen 강제 가비지 컬렉션 완료")
            return result
            
        except Exception as e:
            print(f"[ERROR] 가비지 컬렉션 실패: {e}")
            return None
    