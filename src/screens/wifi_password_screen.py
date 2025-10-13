"""
Wi-Fi 비밀번호 입력 화면
LVGL 기본 키보드 매핑을 활용한 버튼 매트릭스로 구현
"""

import lvgl as lv
import time
from ui_style import UIStyle

class WifiPasswordScreen:
    def __init__(self, screen_manager, selected_network="Wi-Fi 네트워크"):
        self.screen_manager = screen_manager
        self.screen_name = "wifi_password"
        self.selected_network = selected_network
        self._password = ""
        
        # UI 스타일 초기화
        self.ui_style = UIStyle()
        
        # Modern 화면 생성
        print(f"📱 {self.screen_name} Modern 화면 생성 시도...")
        try:
            self._create_modern_screen()
            print(f"✅ {self.screen_name} 화면 초기화 완료")
        except Exception as e:
            print(f"❌ {self.screen_name} 화면 초기화 실패: {e}")
            import sys
            sys.print_exception(e)
            # 기본 화면 생성 시도
            print(f"📱 {self.screen_name} 기본 화면 생성 시도...")
            try:
                self._create_basic_screen()
                print(f"✅ {self.screen_name} 기본 화면 초기화 완료")
            except Exception as e2:
                print(f"❌ {self.screen_name} 기본 화면 초기화도 실패: {e2}")
                import sys
                sys.print_exception(e2)
    
    def _create_modern_screen(self):
        """Modern 스타일 화면 생성"""
        print(f"  📱 {self.screen_name} Modern 화면 생성 시작...")
        
        try:
            # 메모리 정리
            import gc
            gc.collect()
            print(f"  ✅ 메모리 정리 완료")
            
            # 화면 생성
            print(f"  📱 화면 객체 생성...")
            self.screen_obj = lv.obj()
            print(f"  📱 화면 객체 생성됨: {self.screen_obj}")
            
            # 화면 배경 스타일 적용 (Modern 스타일)
            self.ui_style.apply_screen_style(self.screen_obj)
            
            # 스크롤바 비활성화
            self.screen_obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.screen_obj.set_scroll_dir(lv.DIR.NONE)  # 스크롤 방향 비활성화
            print(f"  ✅ 화면 배경 설정 완료")
            
            # 화면 크기 설정
            self.screen_obj.set_size(160, 128)
            print(f"  📱 화면 크기: 160x128")
            
            # 메인 컨테이너 생성
            print(f"  📱 메인 컨테이너 생성 시도...")
            self.main_container = lv.obj(self.screen_obj)
            self.main_container.set_size(160, 128)
            self.main_container.align(lv.ALIGN.CENTER, 0, 0)
            self.main_container.set_style_bg_opa(0, 0)  # 투명 배경
            self.main_container.set_style_border_width(0, 0)  # 테두리 없음
            
            # 스크롤바 비활성화
            self.main_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.main_container.set_scroll_dir(lv.DIR.NONE)  # 스크롤 방향 비활성화
            print(f"  📱 메인 컨테이너 생성 완료")
            
            # 네트워크명 제목 영역 생성
            print(f"  📱 네트워크명 제목 영역 생성 시도...")
            self._create_network_title_area()
            print(f"  📱 네트워크명 제목 영역 생성 완료")
            
            # 비밀번호 입력 영역 생성
            print(f"  📱 비밀번호 입력 영역 생성 시도...")
            self._create_password_area()
            print(f"  📱 비밀번호 입력 영역 생성 완료")
            
            # 키보드 영역 생성
            print(f"  📱 키보드 영역 생성 시도...")
            self._create_keyboard_area()
            print(f"  📱 키보드 영역 생성 완료")
            
            print(f"  ✅ Modern 화면 생성 완료")
            
        except Exception as e:
            print(f"  ❌ Modern 화면 생성 중 오류 발생: {e}")
            import sys
            sys.print_exception(e)
            raise e  # 상위로 예외 전파
    
    def _create_basic_screen(self):
        """기본 화면 생성 (오류 시 대안)"""
        print(f"  📱 {self.screen_name} 기본 화면 생성 시작...")
        
        # 기본 화면 객체 생성
        self.screen_obj = lv.obj()
        self.screen_obj.set_size(160, 128)
        
        # 기본 라벨 생성
        self.title_label = lv.label(self.screen_obj)
        self.title_label.set_text(f"Wi-Fi 비밀번호\n{self.selected_network}")
        self.title_label.align(lv.ALIGN.CENTER, 0, 0)
        
        print(f"  ✅ 기본 화면 생성 완료")
    
    def _create_network_title_area(self):
        """네트워크명 제목 영역 생성"""
        try:
            # 네트워크 제목 컨테이너
            self.network_title_container = lv.obj(self.main_container)
            self.network_title_container.set_size(160, 25)
            self.network_title_container.align(lv.ALIGN.TOP_MID, 0, -8)  # 위로 10픽셀 이동 (2 -> -8)
            self.network_title_container.set_style_bg_opa(0, 0)
            self.network_title_container.set_style_border_width(0, 0)
            
            # 네트워크 제목 컨테이너 스크롤바 비활성화
            self.network_title_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.network_title_container.set_scroll_dir(lv.DIR.NONE)
            
            print("  ✅ 네트워크 제목 컨테이너 생성 완료")
            
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
                print("  ✅ 네트워크 제목에 한국어 폰트 적용 완료")
            
            print("  ✅ 네트워크 제목 텍스트 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 네트워크 제목 영역 생성 실패: {e}")
            # 기본 네트워크 제목 생성
            try:
                self.network_title_text = lv.label(self.main_container)
                self.network_title_text.set_text(f"Wi-Fi 비밀번호\n{self.selected_network}")
                self.network_title_text.align(lv.ALIGN.TOP_MID, 0, 5)
                print("  ✅ 기본 네트워크 제목 생성 완료")
            except Exception as e2:
                print(f"  ❌ 기본 네트워크 제목 생성도 실패: {e2}")
    
    def _create_password_area(self):
        """비밀번호 입력 영역 생성"""
        try:
            # 패스워드 입력 컨테이너 생성
            self.password_container = lv.obj(self.main_container)
            self.password_container.set_size(160, 24)  # 높이를 4픽셀 늘림 (20 -> 24)
            self.password_container.align(lv.ALIGN.TOP_MID, 0, 20)  # 원래 위치로 복원
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
            print("  ✅ 텍스트 영역 기본 설정 완료")
            
            # 텍스트 영역 스타일
            self.textarea.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
            self.textarea.set_style_border_width(0, 0)  # 테두리 제거
            
            # 텍스트 영역 스크롤바 비활성화
            self.textarea.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.textarea.set_scroll_dir(lv.DIR.NONE)
            self.textarea.set_style_text_color(lv.color_hex(0x333333), 0)
            self.textarea.set_style_radius(5, 0)
            self.textarea.set_style_pad_all(5, 0)
            print("  ✅ 텍스트 영역 스타일 설정 완료")
            
            # 한국어 폰트 적용
            korean_font = getattr(lv, "font_notosans_kr_regular", None)
            if korean_font:
                self.textarea.set_style_text_font(korean_font, 0)
                print("  ✅ 텍스트 영역에 한국어 폰트 적용 완료")
            
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
                print("  ✅ 미리보기 라벨에 한국어 폰트 적용 완료")
            
            print("  ✅ 비밀번호 입력 영역 생성 완료 (미리보기 라벨 포함)")
            
        except Exception as e:
            print(f"  ❌ 비밀번호 입력 영역 생성 실패: {e}")
            import sys
            sys.print_exception(e)
            # 기본 텍스트 영역 생성
            try:
                self.textarea = lv.textarea(self.main_container)
                self.textarea.set_size(140, 20)
                self.textarea.align(lv.ALIGN.TOP_MID, 0, 30)
                self.textarea.set_placeholder_text("Password")
                self.textarea.set_password_mode(True)
                print("  ✅ 기본 텍스트 영역 생성 완료")
            except Exception as e2:
                print(f"  ❌ 기본 텍스트 영역 생성도 실패: {e2}")
    
    def _create_keyboard_area(self):
        """텍스트 기반 키보드 영역 생성"""
        print("  📱 텍스트 기반 키보드 영역 생성 시도...")
        
        try:
            print("  📱 키보드 컨테이너 생성 중...")
            # 키보드 컨테이너 생성
            self.keyboard_container = lv.obj(self.main_container)
            print("  📱 키보드 컨테이너 크기 설정 중...")
            self.keyboard_container.set_size(160, 60)  # 높이 증가로 키보드 잘림 방지
            print("  📱 키보드 컨테이너 정렬 설정 중...")
            self.keyboard_container.align(lv.ALIGN.CENTER, 0, 30)  # 아래로 5픽셀 추가 이동 (25 -> 30)
            print("  📱 키보드 컨테이너 스타일 설정 중...")
            self.keyboard_container.set_style_bg_opa(0, 0)  # 투명 배경
            self.keyboard_container.set_style_border_width(0, 0)
            
            # 스크롤바 비활성화
            self.keyboard_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.keyboard_container.set_scroll_dir(lv.DIR.NONE)  # 스크롤 방향 비활성화
            print("  ✅ 키보드 컨테이너 생성 완료")
            
            # 텍스트 기반 키보드 초기화
            print("  📱 텍스트 기반 키보드 초기화...")
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
            
            print(f"  ✅ 텍스트 기반 키보드 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 텍스트 기반 키보드 생성 실패: {e}")
            print(f"  📱 에러 타입: {type(e).__name__}")
            import sys
            sys.print_exception(e)
    
    def _draw_keyboard(self):
        """키보드 표시 (일반 텍스트)"""
        print("  📱 키보드 표시 시작...")
        
        try:
            # 현재 모드의 레이아웃 가져오기
            layout = self.keyboard_layouts[self.keyboard_mode]
            print(f"  📱 레이아웃 모드: {self.keyboard_mode}")
            
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
            
            print(f"  ✅ 키보드 표시 완료")
            
        except Exception as e:
            print(f"  ❌ 키보드 표시 실패: {e}")
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
        print(f"📱 {self.screen_name} 화면 표시 시작...")
        
        if hasattr(self, 'screen_obj') and self.screen_obj:
            print(f"📱 화면 객체 존재 확인됨")
            
            # 네트워크 제목 업데이트
            if hasattr(self, 'network_title_text') and hasattr(self, 'selected_network'):
                self.network_title_text.set_text(self.selected_network)
                print(f"📱 네트워크 제목 업데이트: {self.selected_network}")
            
            lv.screen_load(self.screen_obj)
            print(f"✅ {self.screen_name} 화면 로드 완료")
            
            # 화면 강제 업데이트
            print(f"📱 {self.screen_name} 화면 강제 업데이트 시작...")
            for i in range(5):
                lv.timer_handler()
                time.sleep(0.01)
                print(f"  📱 업데이트 {i+1}/5")
            print(f"✅ {self.screen_name} 화면 강제 업데이트 완료")
            
            # 디스플레이 플러시
            print(f"📱 디스플레이 플러시 실행...")
            try:
                lv.disp_drv_t.flush_ready(None)
            except AttributeError:
                try:
                    lv.disp_t.flush_ready(None)
                except AttributeError:
                    print("⚠️ 디스플레이 플러시 오류 (무시): 'module' object has no attribute 'disp_t'")
            
            print(f"📱 화면 전환: {self.screen_name}")
        else:
            print(f"❌ {self.screen_name} 화면 객체가 없음")
    
    def update(self):
        """화면 업데이트 (ScreenManager에서 호출)"""
        # 현재는 특별한 업데이트 로직이 없음
        pass
    
    
    def _attempt_connection(self):
        """Wi-Fi 연결 시도"""
        print(f"🔐 보안 WiFi 연결 시도: {self.selected_network}")
        
        try:
            # 실제 WiFi 연결 시도
            from wifi_manager import wifi_manager
            
            # WiFi 연결 시도
            success = wifi_manager.connect_to_network(self.selected_network, self._password)
            
            if success:
                print("✅ 보안 WiFi 연결 성공!")
                time.sleep(1)
                
                # dose_count 화면으로 이동 (없으면 생성)
                if 'dose_count' not in self.screen_manager.screens:
                    print("📱 복용 횟수 설정 화면 동적 생성 중...")
                    try:
                        from screens.dose_count_screen import DoseCountScreen
                        dose_count_screen = DoseCountScreen(self.screen_manager)
                        self.screen_manager.register_screen('dose_count', dose_count_screen)
                        print("✅ 복용 횟수 설정 화면 생성 및 등록 완료")
                    except Exception as e:
                        print(f"❌ 복용 횟수 설정 화면 생성 실패: {e}")
                        import sys
                        sys.print_exception(e)
                        # 실패 시 wifi_scan으로 돌아가기
                        self.screen_manager.show_screen('wifi_scan')
                        return
                
                # 복용 횟수 설정 화면으로 이동
                print("📱 복용 횟수 설정 화면으로 이동")
                self.screen_manager.show_screen('dose_count')
            else:
                print("❌ WiFi 연결 실패!")
                # 연결 실패 시 현재 화면에 머물기 (팝업 제거)
                
        except Exception as e:
            print(f"❌ WiFi 연결 오류: {e}")
            # 연결 오류 시 현재 화면에 머물기 (팝업 제거)
    
    def get_title(self):
        """화면 제목"""
        return "Wi-Fi 비밀번호"
    
    
    def on_button_a(self):
        """버튼 A - 키보드 왼쪽으로 이동"""
        print("키보드 왼쪽으로 이동")
        self._move_keyboard_cursor('left')
    
    def on_button_b(self):
        """버튼 B - 키보드 오른쪽으로 이동"""
        print("키보드 오른쪽으로 이동")
        self._move_keyboard_cursor('right')
    
    def on_button_c(self):
        """버튼 C - 완료/뒤로가기"""
        print("완료/뒤로가기")
        
        # 비밀번호가 입력되어 있으면 연결 시도
        if hasattr(self, '_password') and self._password:
            print(f"비밀번호 입력 완료: '{self._password}'")
            self._attempt_connection()
        else:
            print("Wi-Fi 비밀번호 화면 뒤로가기")
            self.screen_manager.show_screen('wifi_scan')
    
    def on_button_d(self):
        """버튼 D - 키보드 키 선택/입력"""
        print("키보드 키 선택/입력")
        self._press_current_keyboard_key()
    
    def _move_keyboard_cursor(self, direction):
        """텍스트 기반 키보드 커서 이동"""
        print(f"  📱 키보드 커서 이동: {direction}")
        
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
            print(f"  ✅ 키보드 커서 이동 완료: {current_key}")
            
        except Exception as e:
            print(f"  ❌ 키보드 커서 이동 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _press_current_keyboard_key(self):
        """텍스트 기반 키보드 키 입력"""
        print("  📱 현재 키보드 키 입력")
        
        try:
            layout = self.keyboard_layouts[self.keyboard_mode]
            current_key = layout[self.selected_row][self.selected_col]
            print(f"  📱 선택된 키: {current_key}")
            
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
                print(f"  📱 문자 입력: '{current_key}'")
                self._add_character(current_key)
            
            elif current_key == 'DEL':
                                # 백스페이스
                print(f"  📱 백스페이스")
                self._handle_backspace()
            
            elif current_key == 'OK':
                                # 엔터 (완료)
                print(f"  📱 입력 완료")
                self._handle_ok()
            
            elif current_key == '123':
                                # 숫자 모드 전환
                                print(f"  📱 숫자 모드 전환")
                                self._switch_to_numbers_mode()
                            
            elif current_key == 'ABC':
                                # 대소문자 전환
                                print(f"  📱 대소문자 전환")
                                self._switch_case_mode()
                            
            elif current_key == 'abc':
                # 소문자 모드로 전환
                print(f"  📱 소문자 모드 전환")
                self.keyboard_mode = "lower"
                self.selected_row = 0
                self.selected_col = 0
                self._redraw_keyboard()
            
            print(f"  ✅ 키 입력 처리 완료: {current_key}")
            
        except Exception as e:
            print(f"  ❌ 키 입력 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _switch_to_numbers_mode(self):
        """숫자 모드로 전환"""
        print("  📱 숫자 모드로 전환")
        self.keyboard_mode = "numbers"
        self.selected_row = 0
        self.selected_col = 0
        self._redraw_keyboard()
        print("  ✅ 숫자 모드로 전환 완료")
    
    def _switch_case_mode(self):
        """대소문자 모드 전환"""
        print("  📱 대소문자 모드 전환")
        
        if self.keyboard_mode == "lower":
            self.keyboard_mode = "upper"
        else:
            self.keyboard_mode = "lower"
        
        self.selected_row = 0
        self.selected_col = 0
        self._redraw_keyboard()
        print(f"  ✅ {self.keyboard_mode} 모드로 전환 완료")
    
    
    def _redraw_keyboard(self):
        """키보드 다시 그리기 (선택된 문자 볼드체)"""
        print(f"  📱 키보드 다시 그리기: {self.keyboard_mode}")
        
        try:
            # 기존 라벨 제거
            if hasattr(self, 'keyboard_label'):
                self.keyboard_label.delete()
            
            # 키보드 다시 그리기
            self._draw_keyboard()
            
            print(f"  ✅ 키보드 다시 그리기 완료")
            
        except Exception as e:
            print(f"  ❌ 키보드 다시 그리기 실패: {e}")
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
                print(f"  📱 미리보기 업데이트: {current_char}")
        except Exception as e:
            print(f"  ❌ 미리보기 업데이트 실패: {e}")
    
    def _update_selection_display(self):
        """선택 표시 업데이트 (미리보기 라벨만 업데이트)"""
        try:
            # 미리보기 라벨만 업데이트 (키보드는 다시 그리지 않음)
            self._update_preview_label()
            print(f"  📱 선택 업데이트: ({self.selected_row}, {self.selected_col})")
        except Exception as e:
            print(f"  ❌ 선택 업데이트 실패: {e}")
    
    def _handle_backspace(self):
        """백스페이스 처리"""
        print("  📱 백스페이스 처리 시작...")
        
        try:
            # 내부 텍스트에서 마지막 문자 제거
            if hasattr(self, '_internal_text') and len(self._internal_text) > 0:
                self._internal_text = self._internal_text[:-1]
                print(f"  ✅ 백스페이스 성공: '{self._internal_text}'")
                
                # textarea 업데이트 (실제 텍스트로 표시)
                if hasattr(self, 'textarea'):
                    try:
                        self.textarea.set_text(self._internal_text)
                        print(f"  📱 textarea 업데이트: '{self._internal_text}'")
                    except Exception as e:
                        print(f"  ⚠️ textarea 업데이트 실패: {e}")
            else:
                print("  📱 백스페이스: 텍스트가 비어있음")
                
        except Exception as e:
            print(f"  ❌ 백스페이스 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _handle_ok(self):
        """OK 버튼 처리 (입력 완료)"""
        print("  📱 OK 버튼 처리 시작...")
        
        try:
            current_text = ""
            
            # textarea에서 텍스트 가져오기
            if hasattr(self, 'textarea'):
                try:
                    current_text = self.textarea.get_text()
                    print(f"  📱 textarea 텍스트: '{current_text}'")
                except Exception as text_e:
                    print(f"  ⚠️ textarea 텍스트 가져오기 실패: {text_e}")
            
            # 내부 텍스트도 확인 (더 길면 우선 사용)
            if hasattr(self, '_internal_text'):
                if len(self._internal_text) > len(current_text):
                    current_text = self._internal_text
                    print(f"  📱 내부 텍스트 사용: '{current_text}'")
            
            # 비밀번호 길이 검증
            if len(current_text) >= 8:
                print(f"  ✅ 비밀번호 입력 완료: '{current_text}'")
                self._password = current_text  # 비밀번호 저장
                self._attempt_connection()
            elif len(current_text) > 0:
                print(f"  📱 비밀번호가 너무 짧습니다: {len(current_text)}자 (최소 8자 필요)")
                # 짧은 비밀번호도 허용 (실제 환경에서는 더 유연하게)
                print(f"  📱 비밀번호를 그대로 사용합니다: '{current_text}'")
                self._password = current_text
                self._attempt_connection()
            else:
                print(f"  📱 비밀번호가 입력되지 않았습니다")
                # 빈 비밀번호도 연결 시도 (개방형 네트워크일 수 있음)
                print(f"  📱 빈 비밀번호로 연결 시도합니다")
                self._password = ""
                self._attempt_connection()
                
        except Exception as e:
            print(f"  ❌ OK 버튼 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _add_character(self, char):
        """문자 추가 (안전한 방식)"""
        print(f"  📱 문자 추가 처리: '{char}' (타입: {type(char)})")
        
        try:
            # 내부 텍스트로만 관리
            if not hasattr(self, '_internal_text'):
                self._internal_text = ""
            
            # 문자 추가 (안전하게)
            self._internal_text += str(char)
            print(f"  ✅ 문자 추가 성공: '{char}' -> '{self._internal_text}'")
            
            # textarea 업데이트 (실제 텍스트로 표시)
            if hasattr(self, 'textarea'):
                try:
                    self.textarea.set_text(self._internal_text)
                    print(f"  📱 textarea 업데이트: '{self._internal_text}'")
                except Exception as e:
                    print(f"  ⚠️ textarea 업데이트 실패: {e}")
                
        except Exception as e:
            print(f"  ❌ 문자 추가 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def hide(self):
        """화면 숨기기"""
        print(f"📱 {self.screen_name} 화면 숨기기")
        # 화면 숨기기 로직 (필요시 구현)
        pass