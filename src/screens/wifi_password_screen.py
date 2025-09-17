"""
Wi-Fi 비밀번호 화면
선택된 Wi-Fi 네트워크의 비밀번호를 입력하는 화면
"""

import time
import lvgl as lv

class WifiPasswordScreen:
    """Wi-Fi 비밀번호 화면 클래스 (간단한 버전)"""
    
    def __init__(self, screen_manager, ssid="Example_SSID"):
        """Wi-Fi 비밀번호 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = 'wifi_password'
        self.screen_obj = None
        self.selected_network = ssid
        self.password = ""
        self.cursor_position = 0
        self.show_password = False
        
        # 키보드 네비게이션 변수들
        self.keyboard_rows = []  # 키보드 행들
        self.current_row = 0     # 현재 선택된 행
        self.current_col = 0     # 현재 선택된 열
        self.keyboard_buttons = []  # 키보드 버튼들
        
        # 간단한 화면 생성
        self._create_simple_screen()
        
        print(f"✅ {self.screen_name} 화면 초기화 완료")
    
    def _create_simple_screen(self):
        """Modern/Xiaomi-like 키보드 카드 스타일 화면 생성"""
        print(f"  📱 {self.screen_name} 키보드 카드 스타일 화면 생성 시작...")
        
        # 메모리 정리
        import gc
        gc.collect()
        print(f"  ✅ 메모리 정리 완료")
        
        # 화면 생성 (흰색 배경)
        print(f"  📱 화면 객체 생성...")
        self.screen_obj = lv.obj()
        self.screen_obj.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)  # 화이트 배경
        print(f"  ✅ 화면 객체 생성 완료")
        
        # 제목 라벨 생성
        print(f"  📱 제목 라벨 생성...")
        title_label = lv.label(self.screen_obj)
        title_label.set_text("Wi-Fi 비밀번호")
        title_label.set_style_text_color(lv.color_hex(0x333333), 0)  # 다크 그레이
        # 한국어 폰트 적용
        korean_font = getattr(lv, "font_notosans_kr_regular", None)
        if korean_font:
            title_label.set_style_text_font(korean_font, 0)
        title_label.align(lv.ALIGN.TOP_MID, 0, 10)
        print(f"  ✅ 제목 라벨 생성 완료")
        
        # 선택된 네트워크 표시
        network_label = lv.label(self.screen_obj)
        network_label.set_text(f"네트워크: {self.selected_network}")
        network_label.set_style_text_color(lv.color_hex(0x666666), 0)
        if korean_font:
            network_label.set_style_text_font(korean_font, 0)
        network_label.align(lv.ALIGN.TOP_MID, 0, 30)
        
        # LVGL 키보드 생성
        self._create_virtual_keyboard()
        
        # 상태 표시 라벨 제거 (깔끔한 UI를 위해)
        
        print(f"  ✅ 키보드 화면 생성 완료")
    
    def _create_virtual_keyboard(self):
        """LVGL 키보드 + 물리 버튼 네비게이션"""
        print("  📱 LVGL 키보드 + 물리 버튼 네비게이션 생성...")
        
        # LVGL 키보드 생성 (안전하게)
        try:
            self.keyboard = lv.keyboard(self.screen_obj)
            print("  ✅ LVGL 키보드 생성 성공")
        except Exception as e:
            print(f"  ❌ LVGL 키보드 생성 실패: {e}")
            # 대안: 직접 버튼 키보드 사용
            self._create_custom_keyboard()
            return
        
        # 키보드 설정
        try:
            self.keyboard.set_size(120, 80)
            self.keyboard.align(lv.ALIGN.BOTTOM_MID, 0, -20)
            
            # 키보드 스타일 설정
            self.keyboard.set_style_bg_color(lv.color_hex(0xF7F7F7), 0)
            self.keyboard.set_style_border_width(1, 0)
            self.keyboard.set_style_border_color(lv.color_hex(0xE0E0E0), 0)
            self.keyboard.set_style_radius(8, 0)
            
            # 키보드 레이아웃 설정
            self.keyboard_map = [
                "1234567890",
                "abcdefghij", 
                "klmnopqrst",
                "uvwxyz",
                "← → ✖ ✓",
                ""
            ]
            
            # Micropython 호환 방식으로 키보드 설정
            self.keyboard.set_map(lv.keyboard.MODE.TEXT_LOWER, self.keyboard_map)
            
            print("  ✅ LVGL 키보드 설정 완료")
            
        except Exception as e:
            print(f"  ⚠️ LVGL 키보드 설정 실패: {e}")
            # 대안: 직접 버튼 키보드 사용
            self._create_custom_keyboard()
            return
        
        # 텍스트 영역 생성
        self._create_text_area()
        
        # 키보드와 텍스트 영역 연결
        try:
            self.keyboard.set_textarea(self.textarea)
            print("  ✅ 키보드-텍스트영역 연결 완료")
            
            # 키보드 이벤트 콜백 추가
            self.keyboard.add_event_cb(self._on_keyboard_event, lv.EVENT.VALUE_CHANGED, None)
            print("  ✅ 키보드 이벤트 콜백 추가 완료")
            
        except Exception as e:
            print(f"  ⚠️ 키보드-텍스트영역 연결 실패: {e}")
        
        print("  ✅ LVGL 키보드 + 물리 버튼 네비게이션 생성 완료")
    
    def _create_custom_keyboard(self):
        """간단한 라벨 기반 키보드 생성 (LVGL 키보드 실패 시 대안)"""
        print("  📱 간단한 라벨 기반 키보드 생성...")
        
        # 키보드 레이아웃 정의
        self.keyboard_layout = [
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
            ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
            ["k", "l", "m", "n", "o", "p", "q", "r", "s", "t"],
            ["u", "v", "w", "x", "y", "z", "←", "→", "✖", "✓"]
        ]
        
        # 간단한 라벨 기반 키보드 생성
        self._create_simple_label_keyboard()
        
        print("  ✅ 간단한 라벨 기반 키보드 생성 완료")
    
    def _create_simple_label_keyboard(self):
        """간단한 라벨 기반 키보드 생성"""
        print("  📱 라벨 기반 키보드 생성...")
        
        self.keyboard_buttons = []
        
        # 키보드 영역 표시 라벨 생성 (한글 폰트 사용)
        keyboard_label = lv.label(self.screen_obj)
        keyboard_label.set_text("키보드")
        keyboard_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
        
        # Noto Sans 한글 폰트 사용
        korean_font = getattr(lv, "font_notosans_kr_regular", None)
        if korean_font:
            keyboard_label.set_style_text_font(korean_font, 0)
        
        keyboard_label.align(lv.ALIGN.BOTTOM_MID, 0, -5)  # 하단에 더 가깝게
        
        # 현재 키보드 상태 표시 (더 큰 글자로)
        self.current_key_label = lv.label(self.screen_obj)
        self.current_key_label.set_text("1")
        self.current_key_label.set_style_text_color(lv.color_hex(0x00C9A7), 0)
        
        # Noto Sans 한글 폰트 사용
        if korean_font:
            self.current_key_label.set_style_text_font(korean_font, 0)
        
        self.current_key_label.align(lv.ALIGN.BOTTOM_MID, 0, -20)  # 키보드 라벨 위에
        
        if korean_font:
            self.current_key_label.set_style_text_font(korean_font, 0)
        
        print("  ✅ 라벨 기반 키보드 생성 완료")
    
    def _create_keyboard_buttons(self):
        """키보드 버튼들 생성"""
        print("  📱 키보드 버튼들 생성...")
        
        self.keyboard_buttons = []
        button_width = 10
        button_height = 15
        button_spacing = 2
        
        # 한국어 폰트 로드
        korean_font = getattr(lv, "font_notosans_kr_regular", None)
        
        for row_idx, row in enumerate(self.keyboard_layout):
            button_row = []
            for col_idx, char in enumerate(row):
                try:
                    # 버튼 생성 (다양한 방법 시도)
                    btn = None
                    button_type = ""
                    
                    try:
                        btn = lv.btn(self.keyboard_container)
                        button_type = "lv.btn"
                    except AttributeError:
                        try:
                            btn = lv.button(self.keyboard_container)
                            button_type = "lv.button"
                        except AttributeError:
                            # 대안: 라벨을 버튼처럼 사용
                            btn = lv.label(self.keyboard_container)
                            btn.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
                            btn.set_style_border_width(1, 0)
                            btn.set_style_border_color(lv.color_hex(0xE0E0E0), 0)
                            btn.set_style_radius(3, 0)
                            btn.set_style_pad_all(2, 0)
                            button_type = "label_as_button"
                    
                    # 첫 번째 버튼에서만 타입 출력
                    if row_idx == 0 and col_idx == 0:
                        print(f"    ✅ 버튼 타입: {button_type}")
                    
                    if not btn:
                        print(f"    ❌ 버튼 생성 실패 (행{row_idx}, 열{col_idx})")
                        continue
                    
                    if btn:
                        btn.set_size(button_width, button_height)
                        
                        # 버튼 위치 계산
                        x = 5 + col_idx * (button_width + button_spacing)
                        y = 5 + row_idx * (button_height + button_spacing)
                        btn.set_pos(x, y)
                        
                        # 버튼 텍스트
                        if hasattr(btn, 'center'):  # lv.btn인 경우
                            btn_label = lv.label(btn)
                            btn_label.set_text(char)
                            btn_label.center()
                            
                            # 버튼 스타일
                            btn.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
                            btn.set_style_border_width(1, 0)
                            btn.set_style_border_color(lv.color_hex(0xE0E0E0), 0)
                            btn.set_style_radius(3, 0)
                            
                            # 폰트 적용
                            if korean_font:
                                btn_label.set_style_text_font(korean_font, 0)
                        else:  # 라벨을 버튼으로 사용하는 경우
                            btn.set_text(char)
                            btn_label = btn
                        
                        button_row.append({
                            'button': btn,
                            'label': btn_label,
                            'char': char
                        })
                        
                except Exception as e:
                    print(f"    ❌ 버튼 생성 실패 (행{row_idx}, 열{col_idx}): {e}")
                    continue
            
            self.keyboard_buttons.append(button_row)
        
        print(f"  ✅ {len(self.keyboard_layout)}행 {len(self.keyboard_layout[0])}열 키보드 버튼 생성 완료")
    
    def _create_text_area(self):
        """텍스트 영역 생성"""
        print("  📱 텍스트 영역 생성...")
        
        # 텍스트 영역 생성
        self.textarea = lv.textarea(self.screen_obj)
        self.textarea.set_size(100, 20)
        self.textarea.align(lv.ALIGN.TOP_MID, 0, 50)
        self.textarea.set_placeholder_text("비밀번호")
        self.textarea.set_one_line(True)
        self.textarea.set_password_mode(True)  # 비밀번호 모드 (마스킹)
        
        # 텍스트 영역 스타일
        self.textarea.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
        self.textarea.set_style_border_width(1, 0)
        self.textarea.set_style_border_color(lv.color_hex(0xE0E0E0), 0)
        self.textarea.set_style_radius(5, 0)
        
        # 한국어 폰트 적용
        korean_font = getattr(lv, "font_notosans_kr_regular", None)
        if korean_font:
            self.textarea.set_style_text_font(korean_font, 0)
        
        print("  ✅ 텍스트 영역 생성 완료")
    
    def _update_keyboard_selection(self):
        """키보드 선택 상태 업데이트"""
        if not hasattr(self, 'keyboard_buttons'):
            return
        
        for row_idx, row in enumerate(self.keyboard_buttons):
            for col_idx, btn_data in enumerate(row):
                try:
                    if row_idx == self.current_row and col_idx == self.current_col:
                        # 선택된 버튼 하이라이트
                        btn_data['button'].set_style_bg_color(lv.color_hex(0x00C9A7), 0)  # 민트색
                        btn_data['button'].set_style_border_color(lv.color_hex(0x00C9A7), 0)
                        btn_data['label'].set_style_text_color(lv.color_hex(0xFFFFFF), 0)  # 흰색 텍스트
                    else:
                        # 일반 버튼 스타일
                        btn_data['button'].set_style_bg_color(lv.color_hex(0xFFFFFF), 0)  # 흰색
                        btn_data['button'].set_style_border_color(lv.color_hex(0xE0E0E0), 0)
                        btn_data['label'].set_style_text_color(lv.color_hex(0x333333), 0)  # 검은색 텍스트
                except Exception as e:
                    print(f"    ⚠️ 버튼 스타일 설정 실패 (행{row_idx}, 열{col_idx}): {e}")
                    continue
    
    def _move_keyboard_cursor(self, direction):
        """키보드 커서 이동"""
        if not hasattr(self, 'keyboard_layout'):
            return
        
        max_rows = len(self.keyboard_layout)
        max_cols = len(self.keyboard_layout[0])
        
        if direction == 'left':
            if self.current_col > 0:
                self.current_col -= 1
            else:
                # 행의 끝으로 이동
                self.current_col = max_cols - 1
                if self.current_row > 0:
                    self.current_row -= 1
                else:
                    self.current_row = max_rows - 1
        elif direction == 'right':
            if self.current_col < max_cols - 1:
                self.current_col += 1
            else:
                # 다음 행으로 이동
                self.current_col = 0
                if self.current_row < max_rows - 1:
                    self.current_row += 1
                else:
                    self.current_row = 0
        
        # 현재 선택된 키 표시
        if hasattr(self, 'current_key_label'):
            current_char = self.keyboard_layout[self.current_row][self.current_col]
            self.current_key_label.set_text(current_char)
        
        print(f"키보드 커서: 행{self.current_row}, 열{self.current_col}, 문자: {current_char}")
    
    def _select_keyboard_char(self):
        """키보드에서 문자 선택"""
        if not hasattr(self, 'keyboard_layout'):
            return
        
        if 0 <= self.current_row < len(self.keyboard_layout) and 0 <= self.current_col < len(self.keyboard_layout[self.current_row]):
            char = self.keyboard_layout[self.current_row][self.current_col]
            print(f"선택된 문자: {char}")
            
            if char == "←":
                # 백스페이스 (마지막 문자 삭제)
                if self.password:
                    self.password = self.password[:-1]
                    print(f"문자 삭제: {self.password}")
            elif char == "→":
                # 공백 추가
                self.password += " "
                print(f"공백 추가: {self.password}")
            elif char == "✖":
                # 전체 삭제
                self.password = ""
                print("전체 삭제")
            elif char == "✓":
                # 확인 (WiFi 연결 시도)
                self._attempt_connection()
                return
            else:
                # 일반 문자 추가
                self.password += char
                print(f"문자 추가: {self.password}")
            
            # 텍스트 영역 업데이트
            self._update_password_display()
    
    def _switch_keyboard_mode(self):
        """LVGL 키보드 모드 전환"""
        if not hasattr(self, 'keyboard'):
            return
        
        try:
            # 현재 모드를 추적하는 변수 사용
            if not hasattr(self, 'current_keyboard_mode'):
                self.current_keyboard_mode = 'lower'
            
            # 대문자 모드 맵
            keyboard_map_upper = [
                "1234567890",
                "ABCDEFGHIJ", 
                "KLMNOPQRST",
                "UVWXYZ",
                "← → ✖ ✓",
                ""
            ]
            
            # 특수문자 모드 맵
            keyboard_map_special = [
                "1234567890",
                "!@#$%^&*()", 
                "[]{}|\\:;\"'",
                "<>,.?/~`",
                "← → ✖ ✓",
                ""
            ]
            
            if self.current_keyboard_mode == 'lower':
                self.keyboard.set_map(lv.keyboard.MODE.TEXT_UPPER, keyboard_map_upper)
                self.current_keyboard_mode = 'upper'
                print("키보드 모드: 대문자")
            elif self.current_keyboard_mode == 'upper':
                self.keyboard.set_map(lv.keyboard.MODE.TEXT_LOWER, keyboard_map_special)
                self.current_keyboard_mode = 'special'
                print("키보드 모드: 특수문자")
            else:
                self.keyboard.set_map(lv.keyboard.MODE.TEXT_LOWER, self.keyboard_map)
                self.current_keyboard_mode = 'lower'
                print("키보드 모드: 소문자")
        except Exception as e:
            print(f"키보드 모드 전환 실패: {e}")
    
    def _create_text_area_only(self):
        """키보드 없이 텍스트 영역만 생성 (대안)"""
        # 텍스트 영역 생성 (키보드와 연결용)
        self.textarea = lv.textarea(self.screen_obj)
        self.textarea.set_size(100, 20)
        self.textarea.align(lv.ALIGN.TOP_MID, 0, 50)  # 텍스트 영역을 위쪽에 배치
        self.textarea.set_placeholder_text("비밀번호")
        self.textarea.set_one_line(True)
        self.textarea.set_password_mode(True)  # 비밀번호 모드 (마스킹)
        
        # 텍스트 영역 스타일
        self.textarea.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
        self.textarea.set_style_border_width(1, 0)
        self.textarea.set_style_border_color(lv.color_hex(0xE0E0E0), 0)
        self.textarea.set_style_radius(5, 0)
        
        # 한국어 폰트 적용
        korean_font = getattr(lv, "font_notosans_kr_regular", None)
        if korean_font:
            self.textarea.set_style_text_font(korean_font, 0)
        
        # 안내 메시지 제거 (깔끔한 UI를 위해)
        
        print("✅ 텍스트 영역만 생성 완료")
    
    def _on_keyboard_event(self, e):
        """키보드 이벤트 처리"""
        code = e.get_code()
        keyboard = e.get_target()
        
        if code == lv.EVENT.VALUE_CHANGED:
            try:
                # 텍스트 영역에서 비밀번호 가져오기
                if hasattr(self, 'textarea'):
                    self.password = self.textarea.get_text()
                    print(f"입력된 비밀번호: {self.password}")
                else:
                    print("텍스트 영역이 없음")
            except Exception as e:
                print(f"키보드 이벤트 처리 오류: {e}")
    
    def _update_password_display(self):
        """비밀번호 표시 업데이트"""
        if hasattr(self, 'textarea'):
            if self.show_password:
                # 비밀번호 표시 모드
                self.textarea.set_text(self.password)
                self.textarea.set_password_mode(False)
            else:
                # 비밀번호 숨김 모드 (마스킹)
                masked_text = "*" * len(self.password)
                self.textarea.set_text(masked_text)
                self.textarea.set_password_mode(True)
            
            # 플레이스홀더 업데이트
            if not self.password:
                self.textarea.set_placeholder_text("비밀번호")
            else:
                self.textarea.set_placeholder_text("")
    
    def _attempt_connection(self):
        """WiFi 연결 시도"""
        if not self.password:
            print("비밀번호를 먼저 입력하세요")
            return
        
        print(f"WiFi 연결 시도: {self.selected_network}")
        
        # TODO: 실제 WiFi 연결 로직
        # wifi_manager.connect_to_network(self.selected_network, self.password)
        
        # 시뮬레이션
        import time
        time.sleep(1)
        
        # 연결 성공 시뮬레이션
        print("WiFi 연결 성공!")
        time.sleep(1)
        self.screen_manager.show_screen('dose_count')
    
    def toggle_password_visibility(self):
        """비밀번호 표시/숨김 토글"""
        self.show_password = not self.show_password
        
        if hasattr(self, 'textarea'):
            self.textarea.set_password_mode(not self.show_password)
        
        self._update_password_display()
        print(f"비밀번호 표시 모드: {'표시' if self.show_password else '숨김'}")
    
    def clear_password(self):
        """비밀번호 전체 삭제"""
        self.password = ""
        if hasattr(self, 'textarea'):
            self.textarea.set_text("")
        self._update_password_display()
        print("비밀번호 삭제됨")
    
    def get_title(self):
        """화면 제목"""
        return "Wi-Fi 비밀번호"
    
    def get_button_hints(self):
        """버튼 힌트"""
        if hasattr(self, 'keyboard_layout'):
            # 직접 버튼 키보드 모드
            return "A:좌측  B:우측  C:뒤로  D:선택"
        elif hasattr(self, 'keyboard'):
            # LVGL 키보드 모드
            return "A:좌측  B:우측  C:삭제  D:입력"
        else:
            return "A:좌측  B:우측  C:뒤로  D:선택"
    
    def get_voice_file(self):
        """안내 음성 파일"""
        return "wav_wifi_password_prompt.wav"
    
    def get_effect_file(self):
        """효과음 파일"""
        return "wav_adjust.wav"
    
    def show(self):
        """화면 표시"""
        if self.screen_obj:
            lv.screen_load(self.screen_obj)
            print(f"✅ {self.screen_name} 화면 표시됨")
            
            # LVGL 타이머 핸들러 강제 호출 (test_lvgl.py 방식)
            print(f"📱 {self.screen_name} 화면 강제 업데이트 시작...")
            for i in range(10):
                lv.timer_handler()
                time.sleep(0.1)  # test_lvgl.py와 동일한 대기 시간
            print(f"✅ {self.screen_name} 화면 강제 업데이트 완료")
    
    def hide(self):
        """화면 숨기기"""
        pass
    
    def update(self):
        """화면 업데이트"""
        pass
    
    
    def on_button_a(self):
        """버튼 A - 키보드 커서 좌측 이동"""
        if hasattr(self, 'keyboard_layout'):
            # 직접 버튼 키보드 모드
            self._move_keyboard_cursor('left')
        elif hasattr(self, 'keyboard'):
            # LVGL 키보드 모드 - 좌측 키 이동 (LVGL 문서 참고)
            print("⬅️ 키보드 버튼 좌측 이동")
            lv.event_send(self.keyboard, lv.EVENT.KEY, lv.KEY.LEFT)
    
    def on_button_b(self):
        """버튼 B - 키보드 커서 우측 이동"""
        if hasattr(self, 'keyboard_layout'):
            # 직접 버튼 키보드 모드
            self._move_keyboard_cursor('right')
        elif hasattr(self, 'keyboard'):
            # LVGL 키보드 모드 - 우측 키 이동 (LVGL 문서 참고)
            print("➡️ 키보드 버튼 우측 이동")
            lv.event_send(self.keyboard, lv.EVENT.KEY, lv.KEY.RIGHT)
    
    def on_button_c(self):
        """버튼 C - 백스페이스 또는 뒤로가기"""
        if hasattr(self, 'keyboard_layout'):
            # 직접 버튼 키보드 모드 - 뒤로가기
        print("Wi-Fi 비밀번호 화면 뒤로가기")
        self.screen_manager.show_screen('wifi_scan')
        elif hasattr(self, 'keyboard'):
            # LVGL 키보드 모드 - 백스페이스
            print("⌫ 백스페이스")
            lv.event_send(self.keyboard, lv.EVENT.KEY, lv.KEY.BACKSPACE)
    
    def on_button_d(self):
        """버튼 D - 키 선택 또는 연결 시도"""
        if hasattr(self, 'keyboard_layout'):
            # 직접 버튼 키보드 모드 - 문자 선택
            self._select_keyboard_char()
        elif hasattr(self, 'keyboard'):
            # LVGL 키보드 모드 - 현재 선택된 키 입력
            print("✔️ 키 입력")
            lv.event_send(self.keyboard, lv.EVENT.KEY, lv.KEY.ENTER)