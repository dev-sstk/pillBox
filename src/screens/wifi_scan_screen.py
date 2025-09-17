"""
Wi-Fi 스캔 화면
사용 가능한 Wi-Fi 네트워크 목록을 표시하고 선택할 수 있는 화면
"""

import time
import lvgl as lv
from wifi_manager import wifi_manager

class WifiScanScreen:
    """Wi-Fi 스캔 화면 클래스 (간단한 버전)"""
    
    def __init__(self, screen_manager):
        """Wi-Fi 스캔 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = 'wifi_scan'
        self.screen_obj = None
        self.wifi_networks = []
        self.selected_index = 0
        self.scanning = False
        self.last_scan_time = 0
        self.scan_interval = 10000
        
        # WiFi 네트워크 스캔
        self._scan_wifi_networks()
        
        # 간단한 화면 생성
        self._create_simple_screen()
        
        print(f"✅ {self.screen_name} 화면 초기화 완료")
    
    def _create_simple_screen(self):
        """간단한 화면 생성 (test_lvgl.py 방식)"""
        print(f"  📱 {self.screen_name} 간단한 화면 생성 시작...")
        
        # 메모리 정리
        import gc
        gc.collect()
        print(f"  ✅ 메모리 정리 완료")
        
        # 화면 생성
        print(f"  📱 화면 객체 생성...")
        self.screen_obj = lv.obj()
        self.screen_obj.set_style_bg_color(lv.color_hex(0x000000), 0)
        print(f"  ✅ 화면 객체 생성 완료")
        
        # 한글 폰트 로드 (안전하게)
        print(f"  📱 한글 폰트 로드...")
        korean_font = getattr(lv, "font_notosans_kr_regular", None)
        if korean_font:
            print(f"  ✅ 한글 폰트 로드 성공")
        else:
            print(f"  ⚠️ 한글 폰트 없음, 기본 폰트 사용")
        
        # 제목 라벨 생성 (메모리 안전 방식)
        print(f"  📱 제목 라벨 생성...")
        try:
            # 메모리 정리
            import gc
            gc.collect()
            print(f"  📱 라벨 생성 전 메모리 정리 완료")
            
            # 라벨 생성
            title_label = lv.label(self.screen_obj)
            print(f"  📱 라벨 객체 생성 완료")
            
            # 폰트 설정
            if korean_font:
                title_label.set_style_text_font(korean_font, 0)
                print(f"  📱 폰트 설정 완료")
            
            # 텍스트 설정
            title_label.set_text("Wi-Fi 스캔중 . . .")
            print(f"  📱 텍스트 설정 완료")
            
            # 색상 설정
            title_label.set_style_text_color(lv.color_hex(0x00C9A7), 0)
            print(f"  📱 색상 설정 완료")
            
            # 정렬 설정 (상단에 위치)
            title_label.align(lv.ALIGN.TOP_MID, 0, 5)
            print(f"  📱 정렬 설정 완료")
            
            print(f"  ✅ 제목 라벨 생성 완료")
        except Exception as e:
            print(f"  ❌ 제목 라벨 생성 실패: {e}")
            import sys
            sys.print_exception(e)
        
        # Wi-Fi 리스트 영역 생성 (안전하게)
        try:
            print(f"  📱 Wi-Fi 리스트 영역 생성 중...")
            self.wifi_list_area = lv.obj(self.screen_obj)
            print(f"    ✅ 리스트 영역 객체 생성 완료")
            
            print(f"    📱 크기 설정 중...")
            self.wifi_list_area.set_size(150, 90)  # 더 넓게
            print(f"    ✅ 크기 설정 완료")
            
            print(f"    📱 정렬 설정 중...")
            self.wifi_list_area.align(lv.ALIGN.TOP_MID, 0, 25)  # 제목 아래에
            print(f"    ✅ 정렬 설정 완료")
            
            print(f"    📱 배경 투명 설정 중...")
            self.wifi_list_area.set_style_bg_opa(0, 0)  # 투명 배경
            print(f"    ✅ 배경 투명 설정 완료")
            
            print(f"  ✅ Wi-Fi 리스트 영역 생성 완료")
            
        except Exception as e:
            print(f"  ❌ Wi-Fi 리스트 영역 생성 실패: {e}")
            import sys
            sys.print_exception(e)
            # 대안: 화면 객체를 직접 사용
            self.wifi_list_area = self.screen_obj
            print(f"  ⚠️ 화면 객체를 리스트 영역으로 사용")
        
        # Wi-Fi 네트워크 리스트 생성
        self._create_wifi_list()
        
        print(f"  📱 Wi-Fi 네트워크 리스트 생성 완료")
    
    def _create_wifi_list(self):
        """Wi-Fi 네트워크 리스트 생성"""
        print(f"  📱 Wi-Fi 네트워크 리스트 생성...")
        
        try:
            self.wifi_labels = []
            
            # 스캔된 네트워크가 있으면 표시, 없으면 샘플 데이터 사용
            if not self.wifi_networks:
                self.wifi_networks = [
                    {"ssid": "Home_WiFi", "signal": 85, "security": "WPA2"},
                    {"ssid": "Office_Network", "signal": 72, "security": "WPA3"},
                    {"ssid": "Guest_WiFi", "signal": 45, "security": "Open"},
                    {"ssid": "Neighbor_5G", "signal": 38, "security": "WPA2"}
                ]
                print("📡 샘플 WiFi 네트워크 사용")
            
            # 최대 6개 네트워크만 표시 (작은 폰트로 더 많이 표시 가능)
            max_networks = min(len(self.wifi_networks), 6)
            print(f"  📱 {max_networks}개 네트워크 표시 예정...")
            
            # LVGL 문서 참고한 안전한 라벨 생성
            print(f"  📱 LVGL 문서 참고한 안전한 라벨 생성 시도...")
            
            for i in range(max_networks):
                try:
                    network = self.wifi_networks[i]
                    print(f"  📱 네트워크 {i+1}: {network['ssid']} 생성 중...")
                    
                    # LVGL 문서 방식으로 라벨 생성
                    wifi_label = lv.label(self.wifi_list_area)
                    
                    # 텍스트 설정 (안전하게)
                    try:
                        display_text = f"📶 {network['ssid']}"
                        wifi_label.set_text(display_text)
                        print(f"    ✅ 텍스트 설정: {display_text}")
                    except Exception as e:
                        print(f"    ❌ 텍스트 설정 실패: {e}")
                        continue
                    
                    # 색상 설정 (안전하게)
                    try:
                        wifi_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
                        print(f"    ✅ 색상 설정 완료")
                    except Exception as e:
                        print(f"    ❌ 색상 설정 실패: {e}")
                    
                    # 폰트 설정 (작은 크기로 변경)
                    try:
                        # 기본 폰트 사용 (더 작은 크기)
                        wifi_label.set_style_text_font(lv.font_default(), 0)
                        print(f"    ✅ 폰트 설정 완료")
                    except Exception as e:
                        print(f"    ❌ 폰트 설정 실패: {e}")
                    
                    # 정렬 설정 (안전하게) - 간격 줄임
                    try:
                        wifi_label.align(lv.ALIGN.TOP_LEFT, 5, 5 + i * 12)  # 18 -> 12로 줄임
                        print(f"    ✅ 정렬 설정 완료")
                    except Exception as e:
                        print(f"    ❌ 정렬 설정 실패: {e}")
                    
                    self.wifi_labels.append(wifi_label)
                    print(f"  ✅ 네트워크 {i+1} 라벨 생성 완료")
                    
                except Exception as e:
                    print(f"  ❌ 네트워크 {i+1} 라벨 생성 실패: {e}")
                    import sys
                    sys.print_exception(e)
                    continue
            
            # 선택된 항목 하이라이트
            self._update_selection()
            print(f"  ✅ {len(self.wifi_labels)}개 Wi-Fi 네트워크 리스트 생성 완료")
            
        except Exception as e:
            print(f"  ❌ Wi-Fi 리스트 생성 실패: {e}")
            import sys
            sys.print_exception(e)
            # 빈 리스트로 초기화
            self.wifi_labels = []
    
    def _create_sample_wifi_list(self):
        """샘플 Wi-Fi 네트워크 리스트 생성"""
        print(f"  📱 Wi-Fi 네트워크 리스트 생성...")
        self.wifi_labels = []
        
        for i, network in enumerate(self.wifi_networks):
            # Wi-Fi 네트워크 라벨 생성
            wifi_label = lv.label(self.wifi_list_area)
            wifi_label.set_text(f"{network['ssid']} ({network['signal']}%)")
            wifi_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
            wifi_label.align(lv.ALIGN.TOP_LEFT, 5, 5 + i * 20)
            self.wifi_labels.append(wifi_label)
        
        # 선택된 항목 하이라이트
        self._update_selection()
        print(f"  ✅ Wi-Fi 네트워크 리스트 생성 완료")
    
    def _update_selection(self):
        """선택된 항목 하이라이트 업데이트"""
        try:
            if not hasattr(self, 'wifi_labels') or not self.wifi_labels:
                print("  ⚠️ WiFi 라벨이 없어서 선택 업데이트 건너뜀")
                return
                
            print(f"  📱 선택 업데이트: {len(self.wifi_labels)}개 라벨, 선택된 인덱스: {self.selected_index}")
            
        for i, label in enumerate(self.wifi_labels):
                try:
            if i == self.selected_index:
                        label.set_style_text_color(lv.color_hex(0x00C9A7), 0)  # 선택된 항목 (민트색)
                label.set_style_bg_color(lv.color_hex(0x333333), 0)
                label.set_style_bg_opa(128, 0)
                        print(f"    ✅ 라벨 {i+1} 선택됨")
            else:
                        label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)  # 일반 항목 (흰색)
                label.set_style_bg_opa(0, 0)
                except Exception as e:
                    print(f"    ❌ 라벨 {i+1} 스타일 설정 실패: {e}")
                    continue
                    
            print("  ✅ 선택 업데이트 완료")
            
        except Exception as e:
            print(f"  ❌ 선택 업데이트 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def get_title(self):
        """화면 제목"""
        return "Wi-Fi 네트워크"
    
    def get_button_hints(self):
        """버튼 힌트"""
        return "A:위  B:아래  C:뒤로  D:선택"
    
    def get_voice_file(self):
        """안내 음성 파일"""
        return "wav_wifi_scan_prompt.wav"
    
    def get_effect_file(self):
        """효과음 파일"""
        return "wav_select.wav"
    
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
        """버튼 A (Up) 처리"""
        print("Wi-Fi 네트워크 위로 이동")
        if self.selected_index > 0:
            self.selected_index -= 1
            self._update_selection()
    
    def on_button_b(self):
        """버튼 B (Down) 처리"""
        print("Wi-Fi 네트워크 아래로 이동")
        if self.selected_index < len(self.wifi_networks) - 1:
            self.selected_index += 1
            self._update_selection()
    
    def on_button_c(self):
        """버튼 C (Back) 처리"""
        print("Wi-Fi 스캔 화면 뒤로가기")
        self.screen_manager.show_screen('startup')
    
    def on_button_d(self):
        """버튼 D (Select) 처리"""
        selected_network = self.wifi_networks[self.selected_index]
        print(f"Wi-Fi 네트워크 선택: {selected_network['ssid']}")
        # 선택된 네트워크 정보를 wifi_password 화면에 전달
        self.screen_manager.show_screen('wifi_password')
    
    def _scan_wifi_networks(self):
        """WiFi 네트워크 스캔"""
        print("📡 WiFi 네트워크 스캔 중...")
        self.scanning = True
        
        try:
            # WiFi 매니저를 통해 네트워크 스캔
            scanned_networks = wifi_manager.scan_networks(force=True)
            
            if scanned_networks:
                self.wifi_networks = scanned_networks
                print(f"✅ {len(self.wifi_networks)}개 네트워크 발견")
            else:
                # 스캔 실패 시 샘플 네트워크 사용
                self.wifi_networks = [
                    {"ssid": "Home_WiFi", "signal": 85, "security": "WPA2"},
                    {"ssid": "Office_Network", "signal": 72, "security": "WPA3"},
                    {"ssid": "Guest_WiFi", "signal": 45, "security": "Open"},
                    {"ssid": "Neighbor_5G", "signal": 38, "security": "WPA2"}
                ]
                print("⚠️ WiFi 스캔 실패, 샘플 네트워크 사용")
            
            self.scanning = False
            self.last_scan_time = time.ticks_ms()
            
        except Exception as e:
            print(f"❌ WiFi 스캔 오류: {e}")
            self.scanning = False
    
    def _start_scan(self):
        """Wi-Fi 스캔 시작"""
        print("Wi-Fi 스캔 시작")
        self._scan_wifi_networks()
        
        # UI 업데이트 (네트워크 목록 새로고침)
        if hasattr(self, 'wifi_list'):
            # 기존 리스트 아이템들 제거
            while self.wifi_list.get_child_cnt() > 0:
                self.wifi_list.remove(self.wifi_list.get_child(0))
            
            # 새로운 네트워크 목록 추가
            for network in self.wifi_networks:
                wifi_btn = self.wifi_list.add_btn(lv.SYMBOL.WIFI, f"{network['ssid']} ({network['signal']}%)")
                wifi_btn.set_style_bg_color(lv.color_hex(0xF7F7F7), 0)
                wifi_btn.set_style_bg_opa(255, 0)
                wifi_btn.set_style_radius(8, 0)
                wifi_btn.set_style_pad_all(8, 0)