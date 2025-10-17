"""
Wi-Fi 스캔 화면
사용 가능한 Wi-Fi 네트워크 목록을 표시하고 선택할 수 있는 화면
Modern/Xiaomi-like 스타일 적용
"""

import time
import lvgl as lv
from wifi_manager import get_wifi_manager
from ui_style import UIStyle

class WifiScanScreen:
    """Wi-Fi 스캔 화면 클래스 - Modern UI 스타일"""
    
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
        
        # UI 스타일 시스템 초기화
        self.ui_style = UIStyle()
        
        # WiFi 네트워크 스캔
        self._scan_wifi_networks()
        
        # Modern 화면 생성
        self._create_modern_screen()
        
    
    def _create_modern_screen(self):
        """Modern 스타일 화면 생성"""
        
        # 메모리 정리
        import gc
        gc.collect()
        
        # 화면 생성
        self.screen_obj = lv.obj()
        
        # 화면 배경 스타일 적용 (Modern 스타일)
        self.ui_style.apply_screen_style(self.screen_obj)
        
        # 화면 크기 확인
        screen_w = self.screen_obj.get_width()
        screen_h = self.screen_obj.get_height()
        
        # 메인 컨테이너 생성
        self._create_main_container()
        
        # 메인 컨테이너가 제대로 생성되지 않으면 화면에 직접 생성
        if not hasattr(self, 'main_container') or self.main_container.get_width() == 0:
            self._create_direct_screen_elements()
        else:
            # 제목 영역 생성
            self._create_title_area()
            
            # Wi-Fi 리스트 영역 생성
            self._create_wifi_list_area()
            
            # 하단 버튼 힌트 영역 생성
            self._create_button_hints_area()
        
    
    def _create_main_container(self):
        """메인 컨테이너 생성 - Modern 스타일"""
        # 메인 컨테이너 (전체 화면)
        self.main_container = lv.obj(self.screen_obj)
        
        # 크기 설정
        self.main_container.set_size(160, 128)
        
        # 위치 설정
        self.main_container.align(lv.ALIGN.CENTER, 0, 0)
        
        # 스타일 설정
        self.main_container.set_style_bg_opa(0, 0)
        self.main_container.set_style_border_width(0, 0)
        self.main_container.set_style_pad_all(0, 0)
        
        # 강제로 LVGL 업데이트
        lv.timer_handler()
        
        # 메인 컨테이너 정보 출력 (업데이트 후)
        main_x = self.main_container.get_x()
        main_y = self.main_container.get_y()
        main_w = self.main_container.get_width()
        main_h = self.main_container.get_height()
        
        # 크기가 0이면 강제로 다시 설정
        if main_w == 0 or main_h == 0:
            self.main_container.set_size(160, 128)
            self.main_container.align(lv.ALIGN.CENTER, 0, 0)
            lv.timer_handler()
            
            # 다시 확인
            main_w = self.main_container.get_width()
            main_h = self.main_container.get_height()
    
    def _create_direct_screen_elements(self):
        """화면에 직접 요소들 생성 (메인 컨테이너 문제 시)"""
        
        # 제목 텍스트 (화면에 직접) - 모던 UI 색상
        self.title_text = lv.label(self.screen_obj)
        self.title_text.set_text("Wi-Fi 네트워크")
        self.title_text.set_style_text_color(lv.color_hex(0x1D1D1F), 0)  # 모던 다크 그레이
        # 한글 폰트로 강제 설정
        if hasattr(lv, "font_notosans_kr_regular"):
            self.title_text.set_style_text_font(lv.font_notosans_kr_regular, 0)
        else:
            # 폰트를 설정하지 않음 (기본값 사용)
            pass
        self.title_text.align(lv.ALIGN.TOP_MID, 0, 10)
        # 제목 텍스트 위치 고정 (움직이지 않도록)
        self.title_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        
        # 스캔 상태 아이콘 제거
        
        # 모던 WiFi 리스트 생성
        self._create_modern_wifi_list()
        
        # 버튼 힌트 (화면에 직접) - 모던 UI 색상
        self.hints_text = lv.label(self.screen_obj)
        # LVGL 심볼 사용 (기본 폰트에서 지원)
        self.hints_text.set_text(f"A:O B:{lv.SYMBOL.UP} C:{lv.SYMBOL.DOWN} D: -")
        self.hints_text.set_style_text_color(lv.color_hex(0x8E8E93), 0)  # 모던 라이트 그레이
        # 기본 폰트 사용 (LVGL 심볼 지원을 위해)
        self.hints_text.align(lv.ALIGN.BOTTOM_MID, 0, -2)  # 4픽셀 더 아래로 이동 (-6 -> -2)
        # 버튼 힌트 텍스트 위치 고정 (움직이지 않도록)
        self.hints_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
    
    def _create_modern_wifi_list(self):
        """LVGL lv.list 위젯을 사용한 모던 WiFi 리스트 생성"""
        
        try:
            # 스캔된 네트워크가 없으면 메시지 표시
            if not self.wifi_networks:
                pass
            # LVGL 리스트 위젯 생성
            self.wifi_list = lv.list(self.screen_obj)
            self.wifi_list.set_size(140, 80)  # 높이 조정 (70 -> 80)
            self.wifi_list.align(lv.ALIGN.CENTER, 0, 5)  # 아래로 5픽셀 이동하여 제목과 겹치지 않게
            
            # 리스트 스타일 설정 - 로고 색상(골드) 배경과 테두리
            self.wifi_list.set_style_bg_color(lv.color_hex(0xd2b13f), 0)  # 골드색 배경 (로고와 동일)
            self.wifi_list.set_style_bg_opa(255, 0)  # 불투명 배경
            self.wifi_list.set_style_border_width(2, 0)  # 테두리 두께 증가 (1 -> 2)
            self.wifi_list.set_style_border_color(lv.color_hex(0xd2b13f), 0)  # 골드색 테두리 (로고와 동일)
            self.wifi_list.set_style_radius(10, 0)  # 둥근 모서리 (알약 충전 디스크와 동일)
            self.wifi_list.set_style_pad_left(5, 0)  # 왼쪽 패딩
            self.wifi_list.set_style_pad_right(5, 0)  # 오른쪽 패딩
            self.wifi_list.set_style_pad_top(6, 0)  # 위쪽 패딩
            self.wifi_list.set_style_pad_bottom(6, 0)  # 아래쪽 패딩
            # 스크롤 정책 설정 (세로 스크롤만 허용)
            self.wifi_list.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.wifi_list.set_scroll_dir(lv.DIR.VER)  # 세로 방향만 스크롤
            
            
            # 최대 4개 네트워크만 표시
            max_networks = min(len(self.wifi_networks), 4)
            
            self.wifi_list_items = []
            # 현재 선택된 항목 인덱스
            self.current_selected_index = 0
            
            for i in range(max_networks):
                try:
                    network = self.wifi_networks[i]
                    
                    # 리스트 아이템 텍스트 (네트워크 이름만 표시)
                    item_text = network['ssid']
                    
                    # 리스트에 버튼 아이템 추가 (다른 메서드 시도)
                    try:
                        list_btn = self.wifi_list.add_btn(None, item_text)
                    except AttributeError:
                        # add_btn이 없으면 add_button 시도
                        try:
                            list_btn = self.wifi_list.add_button(None, item_text)
                        except AttributeError:
                            # add_button도 없으면 직접 버튼 생성 - 고정 위치
                            list_btn = lv.btn(self.wifi_list)
                            list_btn.set_size(130, 25)  # 버튼 크기 고정 (높이 5픽셀 더 증가)
                            list_btn.align(lv.ALIGN.TOP_MID, 0, 2 + i * 27)  # 위치 고정 (간격 조정)
                            btn_label = lv.label(list_btn)
                            btn_label.set_text(item_text)
                            btn_label.align(lv.ALIGN.CENTER, 0, 0)  # 중앙 정렬로 변경
                            btn_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)  # 텍스트 중앙 정렬 추가
                            # 텍스트 오버플로우 방지 (LVGL 호환 방식)
                            btn_label.set_style_text_long_mode(lv.TEXT_LONG.CLIP, 0)
                    
                    # 리스트 버튼 스타일 설정 - 모던 UI 카드 스타일
                    list_btn.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)  # 흰색 배경
                    list_btn.set_style_bg_opa(255, 0)
                    list_btn.set_style_radius(8, 0)  # 둥근 모서리
                    list_btn.set_style_border_width(1, 0)
                    list_btn.set_style_border_color(lv.color_hex(0xD1D5DB), 0)  # 더 진한 테두리로 구분감 향상
                    list_btn.set_style_pad_all(4, 0)  # 패딩 줄임 (8 -> 4)
                    # 그림자 효과 (안전하게 처리)
                    try:
                        list_btn.set_style_shadow_width(2, 0)
                        list_btn.set_style_shadow_color(lv.color_hex(0x000000), 0)
                        list_btn.set_style_shadow_opa(25, 0)
                        list_btn.set_style_shadow_ofs_x(0, 0)
                        list_btn.set_style_shadow_ofs_y(2, 0)
                    except (AttributeError, Exception) as e:
                        # 그림자 스타일이 지원되지 않는 경우 무시
                        pass
                    # 버튼 크기 고정 (텍스트가 잘리지 않도록 높이 증가)
                    list_btn.set_size(130, 25)
                    # 버튼 정렬 고정 (간격도 조정)
                    list_btn.align(lv.ALIGN.TOP_MID, 0, 2 + i * 27)
                    
                    # 리스트 버튼 텍스트 스타일 설정 - 고정 위치 (흘러가는 것 방지)
                    btn_label = list_btn.get_child(0)  # 버튼의 라벨 가져오기
                    if btn_label:
                        btn_label.set_style_text_color(lv.color_hex(self.ui_style.get_color('text')), 0)
                        # 노토산스 폰트 적용
                        if hasattr(lv, "font_notosans_kr_regular"):
                            btn_label.set_style_text_font(lv.font_notosans_kr_regular, 0)
                        # 텍스트 위치 강력 고정 (중앙 정렬)
                        btn_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
                        btn_label.align(lv.ALIGN.CENTER, 0, 0)  # 중앙 정렬로 변경
                        # 텍스트 오버플로우 방지 (안전하게 처리)
                        try:
                            btn_label.set_style_text_long_mode(lv.TEXT_LONG.CLIP, 0)
                        except AttributeError:
                            # LVGL 버전에 따라 지원되지 않을 수 있음
                            pass
                    
                    self.wifi_list_items.append(list_btn)
                    
                except Exception as e:
                    import sys
                    sys.print_exception(e)
                    continue
            
            # 첫 번째 아이템 선택
            if self.wifi_list_items:
                try:
                    self.wifi_list.focus(self.wifi_list_items[0], lv.ANIM.OFF)
                except AttributeError:
                    # focus 메서드가 없으면 다른 방법 시도
                    try:
                        self.wifi_list.set_focused(self.wifi_list_items[0])
                    except AttributeError:
                        pass
            
        except Exception as e:
            import sys
            sys.print_exception(e)
            self.wifi_list_items = []
    
            self.wifi_labels = []
    
    def _create_title_area(self):
        """제목 영역 생성 - Modern 스타일"""
        # 제목 컨테이너
        self.title_container = lv.obj(self.main_container)
        self.title_container.set_size(140, 25)
        self.title_container.align(lv.ALIGN.TOP_MID, 0, 8)
        # 투명 배경 (Modern 스타일)
        self.title_container.set_style_bg_opa(0, 0)
        self.title_container.set_style_border_width(0, 0)
        self.title_container.set_style_pad_all(0, 0)
        
        # 제목 텍스트 (Modern 스타일) - 모던 UI 색상
        self.title_text = self.ui_style.create_label(
            self.title_container,
            "Wi-Fi 네트워크",
            'text_title',
            0x1D1D1F  # 모던 다크 그레이
        )
        self.title_text.align(lv.ALIGN.CENTER, 0, 0)
        # 제목 텍스트 위치 고정 (움직이지 않도록)
        self.title_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        
        # 스캔 상태 표시 (우측 상단) - 모던 UI 색상
        self.scan_status = self.ui_style.create_label(
            self.title_container,
            "📡",
            'text_caption',
            0x007AFF  # iOS 블루
        )
        self.scan_status.align(lv.ALIGN.RIGHT_MID, -5, 0)
        # 스캔 상태 아이콘 위치 고정 (움직이지 않도록)
        self.scan_status.set_style_text_align(lv.TEXT_ALIGN.RIGHT, 0)
    
    def _create_wifi_list_area(self):
        """Wi-Fi 리스트 영역 생성 - Modern 스타일"""
        # Wi-Fi 리스트 컨테이너 (높이 조정 및 위치 개선)
        self.wifi_list_container = lv.obj(self.main_container)
        self.wifi_list_container.set_size(140, 80)  # 높이 조정 (70 -> 80)
        self.wifi_list_container.align(lv.ALIGN.CENTER, 0, 5)  # 아래로 이동하여 제목과 겹치지 않게
        # 투명 배경 (Modern 스타일)
        self.wifi_list_container.set_style_bg_opa(0, 0)
        self.wifi_list_container.set_style_border_width(0, 0)
        self.wifi_list_container.set_style_pad_all(0, 0)
        
        # Wi-Fi 네트워크 리스트 생성
        self._create_wifi_list()
    
    def _create_button_hints_area(self):
        """하단 버튼 힌트 영역 생성 - Modern 스타일"""
        # 버튼 힌트 컨테이너
        self.hints_container = lv.obj(self.main_container)
        self.hints_container.set_size(140, 18)
        self.hints_container.align(lv.ALIGN.BOTTOM_MID, 0, 0)  # 4픽셀 더 아래로 이동 (-4 -> 0)
        # 투명 배경 (Modern 스타일)
        self.hints_container.set_style_bg_opa(0, 0)
        self.hints_container.set_style_border_width(0, 0)
        self.hints_container.set_style_pad_all(0, 0)
        
        # 버튼 힌트 텍스트 (Modern 스타일) - 모던 UI 색상
        self.hints_text = self.ui_style.create_label(
            self.hints_container,
            f"A:O B:{lv.SYMBOL.UP} C:{lv.SYMBOL.DOWN} D: -",
            'text_caption',
            0x8E8E93  # 모던 라이트 그레이
        )
        self.hints_text.align(lv.ALIGN.CENTER, 0, 0)
        # 버튼 힌트 텍스트 위치 고정 (움직이지 않도록)
        self.hints_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
    
    def _create_wifi_list(self):
        """Wi-Fi 네트워크 리스트 생성 - Modern 스타일"""
        
        try:
            self.wifi_labels = []
            
            # 스캔된 네트워크가 없으면 메시지 표시
            if not self.wifi_networks:
                pass
            # 최대 4개 네트워크만 표시 (Modern 스타일)
            max_networks = min(len(self.wifi_networks), 4)
            
            for i in range(max_networks):
                try:
                    network = self.wifi_networks[i]
                    
                    # Wi-Fi 아이템 컨테이너 생성 (Modern 카드 스타일) - 고정 위치
                    wifi_item = lv.obj(self.wifi_list_container)
                    wifi_item.set_size(130, 25)  # 높이 5픽셀 더 증가로 텍스트 잘림 방지
                    wifi_item.align(lv.ALIGN.TOP_MID, 0, 2 + i * 27)  # 간격 조정
                    # 컨테이너 스크롤 방지
                    wifi_item.set_style_overflow(lv.OVERFLOW.HIDDEN, 0)
                    
                    # Modern 카드 스타일 적용 - 모던 UI
                    wifi_item.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)  # 흰색 배경
                    wifi_item.set_style_bg_opa(255, 0)
                    wifi_item.set_style_radius(10, 0)  # 둥근 모서리
                    wifi_item.set_style_border_width(1, 0)
                    wifi_item.set_style_border_color(lv.color_hex(0xD1D5DB), 0)  # 더 진한 테두리로 구분감 향상
                    wifi_item.set_style_pad_all(4, 0)  # 패딩 줄임 (8 -> 4)
                    # 그림자 효과 (모던 UI)
                    try:
                        wifi_item.set_style_shadow_width(3, 0)
                        wifi_item.set_style_shadow_color(lv.color_hex(0x000000), 0)
                        wifi_item.set_style_shadow_opa(20, 0)
                    except AttributeError:
                        pass
                    try:
                        wifi_item.set_style_shadow_ofs_x(0, 0)
                        wifi_item.set_style_shadow_ofs_y(2, 0)
                    except AttributeError:
                        pass
                    
                    # 신호 강도에 따른 아이콘
                    if network['signal'] > 70:
                        signal_icon = "📶"
                    elif network['signal'] > 40:
                        signal_icon = "📶"
                    else:
                        signal_icon = "📶"
                    
                    # Wi-Fi 네트워크 텍스트 (Modern 스타일) - 모던 UI 색상
                    wifi_text = self.ui_style.create_label(
                        wifi_item,
                        f"{signal_icon} {network['ssid']}",
                        'text_body',
                        0x1D1D1F  # 모던 다크 그레이
                    )
                    wifi_text.align(lv.ALIGN.CENTER, 0, 0)
                    # 텍스트 위치 강력 고정 (중앙 정렬)
                    wifi_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
                    wifi_text.set_style_text_long_mode(lv.TEXT_LONG.CLIP, 0)
                    
                    # 보안 아이콘 (우측에) - 모던 UI 색상
                    security_icon = "🔒" if network['security'] != "Open" else "🔓"
                    security_text = self.ui_style.create_label(
                        wifi_item,
                        security_icon,
                        'text_caption',
                        0x8E8E93  # 모던 라이트 그레이
                    )
                    security_text.align(lv.ALIGN.RIGHT_MID, -2, 0)
                    # 보안 아이콘 위치 강력 고정 (움직이지 않도록)
                    security_text.set_style_text_align(lv.TEXT_ALIGN.RIGHT, 0)
                    security_text.set_style_text_long_mode(lv.TEXT_LONG.CLIP, 0)
                    
                    self.wifi_labels.append(wifi_item)
                    
                except Exception as e:
                    continue
            
            # 선택된 항목 하이라이트
            self._update_selection()
            
        except Exception as e:
            # 빈 리스트로 초기화
            self.wifi_labels = []
    
    
    def _update_selection(self):
        """선택된 항목 하이라이트 업데이트 - 모던 스타일"""
        try:
            if not hasattr(self, 'wifi_labels') or not self.wifi_labels:
                return
                
            
            for i, wifi_item in enumerate(self.wifi_labels):
                try:
                    if i == self.selected_index:
                        # 선택된 항목 스타일 (모던 하이라이트) - 그라데이션 효과
                        wifi_item.set_style_bg_color(lv.color_hex(0x007AFF), 0)  # iOS 블루
                        wifi_item.set_style_bg_opa(255, 0)
                        wifi_item.set_style_radius(12, 0)
                        wifi_item.set_style_border_width(2, 0)
                        wifi_item.set_style_border_color(lv.color_hex(0x0056CC), 0)  # 더 진한 블루 테두리
                        # 선택된 항목 그림자 강화
                        try:
                            wifi_item.set_style_shadow_width(4, 0)
                            wifi_item.set_style_shadow_color(lv.color_hex(0x007AFF), 0)
                            wifi_item.set_style_shadow_opa(30, 0)
                        except AttributeError:
                            pass
                        try:
                            wifi_item.set_style_shadow_ofs_x(0, 0)
                            wifi_item.set_style_shadow_ofs_y(3, 0)
                        except AttributeError:
                            pass
                    else:
                        # 일반 항목 스타일 (모던 카드)
                        wifi_item.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)  # 흰색 배경
                        wifi_item.set_style_bg_opa(255, 0)
                        wifi_item.set_style_radius(10, 0)
                        wifi_item.set_style_border_width(1, 0)
                        wifi_item.set_style_border_color(lv.color_hex(0xD1D5DB), 0)  # 더 진한 테두리로 구분감 향상
                        # 일반 항목 그림자
                        wifi_item.set_style_shadow_width(3, 0)
                        wifi_item.set_style_shadow_color(lv.color_hex(0x000000), 0)
                        wifi_item.set_style_shadow_opa(20, 0)  # 그림자 강화
                        wifi_item.set_style_shadow_ofs_x(0, 0)
                        wifi_item.set_style_shadow_ofs_y(2, 0)
                        
                except Exception as e:
                    continue
                    
            
        except Exception as e:
            import sys
            sys.print_exception(e)
    
    def get_title(self):
        """화면 제목"""
        return "Wi-Fi 네트워크"
    
    def get_button_hints(self):
        """버튼 힌트"""
        return ""
    
    def get_voice_file(self):
        """안내 음성 파일"""
        return "wav_wifi_scan_prompt.wav"
    
    def get_effect_file(self):
        """효과음 파일"""
        return "wav_select.wav"
    
    def show(self):
        """화면 표시"""
        
        if self.screen_obj:
            
            # 화면 로드 전에 현재 화면 정보 출력 (안전한 방식)
            try:
                current_screen = lv.screen_active()
            except Exception as e:
                pass
            # 화면 로드
            try:
                lv.screen_load(self.screen_obj)
            except Exception as e:
                return
            
            # 로드 후 활성 화면 확인 (안전한 방식)
            try:
                new_screen = lv.screen_active()
            except Exception as e:
                pass
            # 메인 컨테이너 확인
            if hasattr(self, 'main_container'):
                # 메인 컨테이너 위치와 크기 확인
                main_x = self.main_container.get_x()
                main_y = self.main_container.get_y()
                main_w = self.main_container.get_width()
                main_h = self.main_container.get_height()
            
            # LVGL 타이머 핸들러 강제 호출 (더 많이)
            for i in range(20):
                lv.timer_handler()
                time.sleep(0.05)
            
        else:
            pass
    
    def hide(self):
        """화면 숨기기"""
        pass
    
    def update(self):
        """화면 업데이트"""
        pass
    
    def on_button_a(self):
        """버튼 A (Select) 처리 - LVGL 리스트에서 선택"""
        
        # 단계별 디버깅
        if hasattr(self, 'wifi_list_items'):
            pass
        if hasattr(self, 'current_selected_index'):
            pass
        if hasattr(self, 'wifi_list_items') and self.wifi_list_items and hasattr(self, 'current_selected_index'):
            
            # 현재 선택된 인덱스로 네트워크 선택
            selected_index = self.current_selected_index
            
            if 0 <= selected_index < len(self.wifi_networks):
                selected_network = self.wifi_networks[selected_index]

                # 현재 연결된 네트워크인지 확인
                from wifi_manager import get_wifi_manager
                connection_status = get_wifi_manager().get_connection_status()
                is_currently_connected = (connection_status['connected'] and 
                                        connection_status['ssid'] == selected_network['ssid'])
                
                
                # 이미 연결된 네트워크라면 패스워드 입력 없이 바로 다음 화면으로
                if is_currently_connected:
                    self._go_to_next_screen()
                    return

                # 보안이 있는 네트워크인지 확인
                security = selected_network.get('security', 'Unknown').lower()
                
                # WPA2-PSK, WPA3-SAE 등 다양한 보안 타입 지원
                if any(sec_type in security for sec_type in ['wpa2', 'wpa3', 'wep', 'wpa', 'psk', 'sae']):
                    # 보안이 있는 네트워크 - 저장된 비밀번호 확인
                    
                    # 저장된 비밀번호 확인
                    saved_password = get_wifi_manager().get_saved_password(selected_network['ssid'])
                    
                    if saved_password is not None:
                        # 저장된 비밀번호가 있으면 자동 연결
                        success = get_wifi_manager().connect_to_network(selected_network['ssid'], saved_password)
                        
                        if success:
                            time.sleep(1)
                            # 저장된 비밀번호로 연결 성공 시 바로 다음 화면으로 이동
                            self._go_to_next_screen()
                        else:
                            # 저장된 비밀번호가 틀렸으면 비밀번호 입력 화면으로
                            self._show_password_screen(selected_network)
                        return
                    
                    # 저장된 비밀번호가 없으면 패스워드 화면으로 이동
                    self._show_password_screen(selected_network)
                else:
                    # 보안이 없는 네트워크 - 직접 연결 시도
                    self._connect_to_open_network(selected_network)
            else:
                pass
        else:
            pass
    def on_button_b(self):
        """버튼 B (Up) 처리 - LVGL 리스트 위로 이동"""
        if hasattr(self, 'wifi_list_items') and self.wifi_list_items:
            # 인덱스 기반으로 이전 아이템으로 이동
            if self.current_selected_index > 0:
                self.current_selected_index -= 1
                prev_item = self.wifi_list_items[self.current_selected_index]
                try:
                    self.wifi_list.focus(prev_item, lv.ANIM.OFF)
                except AttributeError:
                    try:
                        self.wifi_list.set_focused(prev_item)
                    except AttributeError:
                        # 포커스 설정이 안되면 시각적 하이라이트만
                        self._update_selection_highlight()
            else:
                pass
    def on_button_c(self):
        """버튼 C (Down) 처리 - LVGL 리스트 아래로 이동"""
        if hasattr(self, 'wifi_list_items') and self.wifi_list_items:
            # 인덱스 기반으로 다음 아이템으로 이동
            if self.current_selected_index < len(self.wifi_list_items) - 1:
                self.current_selected_index += 1
                next_item = self.wifi_list_items[self.current_selected_index]
                try:
                    self.wifi_list.focus(next_item, lv.ANIM.OFF)
                except AttributeError:
                    try:
                        self.wifi_list.set_focused(next_item)
                    except AttributeError:
                        # 포커스 설정이 안되면 시각적 하이라이트만
                        self._update_selection_highlight()
            else:
                pass
    def on_button_d(self):
        """버튼 D 처리 - 기능 없음"""
        # 버튼 D 기능 제거됨
    
    def _show_password_screen(self, selected_network):
        """비밀번호 입력 화면 표시"""
        
        # 패스워드 화면이 등록되어 있지 않으면 동적 생성
        if 'wifi_password' not in self.screen_manager.screens:
            
            # [FAST] 메모리 부족 해결: 강력한 메모리 정리
            import gc
            for i in range(10):  # 10회 가비지 컬렉션 (더 강력하게)
                gc.collect()
                time.sleep(0.05)  # 0.05초 대기 (더 오래)
            
            try:
                from screens.wifi_password_screen import WifiPasswordScreen
                wifi_password_screen = WifiPasswordScreen(self.screen_manager, selected_network['ssid'])
                self.screen_manager.register_screen('wifi_password', wifi_password_screen)
            except Exception as e:
                # [FAST] 메모리 할당 실패 시 추가 메모리 정리
                for i in range(5):
                    gc.collect()
                    time.sleep(0.02)
                import sys
                sys.print_exception(e)
                return
        else:
            wifi_password_screen = self.screen_manager.screens['wifi_password']
        
        # 네트워크 정보 설정
        wifi_password_screen.selected_network = selected_network['ssid']
        wifi_password_screen.selected_network_info = selected_network
        
        # 화면 전환
        self.screen_manager.show_screen('wifi_password')
    
    def _update_selection_highlight(self):
        """선택된 항목 하이라이트 업데이트"""
        if hasattr(self, 'wifi_list_items') and self.wifi_list_items:
            for i, item in enumerate(self.wifi_list_items):
                if i == self.current_selected_index:
                    # 선택된 항목 하이라이트
                    try:
                        item.set_style_bg_color(lv.color_hex(0x007AFF), 0)
                        item.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
                    except:
                        pass
                else:
                    # 일반 항목 스타일
                    try:
                        item.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
                        item.set_style_text_color(lv.color_hex(0x000000), 0)
                    except:
                        pass
    
    def _go_to_next_screen(self):
        """다음 화면으로 이동 (복용 시간 선택)"""
        
        # meal_time 화면이 등록되어 있지 않으면 동적 생성
        if 'meal_time' not in self.screen_manager.screens:
            try:
                from screens.meal_time_screen import MealTimeScreen
                meal_time_screen = MealTimeScreen(self.screen_manager)
                self.screen_manager.register_screen('meal_time', meal_time_screen)
            except Exception as e:
                import sys
                sys.print_exception(e)
                return
        
        # 화면 전환
        self.screen_manager.show_screen('meal_time')

    def _connect_to_open_network(self, network):
        """오픈 네트워크에 직접 연결"""
        
        # 실제 WiFi 연결 로직
        from wifi_manager import get_wifi_manager
        success = get_wifi_manager().connect_to_network(network['ssid'], "")
        
        if success:
            time.sleep(1)
            # 다음 화면으로 이동
            self._go_to_next_screen()
        else:
            # 연결 실패 시 현재 화면에 머물기
            pass
    def _scan_wifi_networks(self):
        """WiFi 네트워크 스캔"""
        self.scanning = True
        
        try:
            # WiFi 매니저를 통해 네트워크 스캔 (재시도 로직 추가)
            scanned_networks = get_wifi_manager().scan_networks(force=True)
            
            # 스캔 결과가 없으면 재시도
            if not scanned_networks:
                time.sleep(2)
                scanned_networks = get_wifi_manager().scan_networks(force=True)
            
            if scanned_networks:
                self.wifi_networks = scanned_networks
            else:
                # 스캔 실패 시 빈 목록
                self.wifi_networks = []
            
            self.scanning = False
            self.last_scan_time = time.ticks_ms()
            
        except Exception as e:
            import sys
            sys.print_exception(e)
            self.scanning = False
    