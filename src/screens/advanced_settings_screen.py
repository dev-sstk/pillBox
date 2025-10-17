"""
고급 설정 화면
시스템 설정, 알람 설정, 데이터 관리 등 고급 기능 제공
"""

import sys
sys.path.append("/")

import lvgl as lv
from ui_style import UIStyle
from data_manager import DataManager
from memory_monitor import MemoryMonitor

class AdvancedSettingsScreen:
    """고급 설정 화면 클래스"""
    
    def __init__(self, screen_manager):
        self.screen_manager = screen_manager
        self.data_manager = DataManager()
        self.memory_monitor = MemoryMonitor()  # 메모리 모니터 추가
        self.screen = lv.obj()
        self.screen_name = "advanced_settings"
        self.ui_style = UIStyle()
        
        self.current_selection = 0
        self.settings_options = [
            {"name": "1. 시스템 설정", "key": "system"},
            {"name": "2. 알람 설정", "key": "alarm"},
            {"name": "3. 데이터 관리", "key": "data"},
            {"name": "4. 정보", "key": "info"}
        ]
        
        # 메모리 상태 확인
        self.memory_monitor.log_memory_usage("고급설정 초기화 시작")
        
        self._create_ui()
        
        # 메모리 상태 확인
        self.memory_monitor.log_memory_usage("고급설정 초기화 완료")
        
        print(f"[OK] {self.screen_name} 초기화 완료")
    
    def _create_ui(self):
        """UI 생성"""
        try:
            print("[DEBUG] UI 생성 시작")
            
            # 메모리 정리
            import gc
            gc.collect()
            print("[DEBUG] UI 생성 전 메모리 정리 완료")
            
            print("[DEBUG] 화면 배경 설정 중...")
            self.screen.set_style_bg_color(lv.color_hex(0x000000), 0)  # 검은색 배경
            self.screen.set_style_pad_all(5, 0)
            print("[DEBUG] 화면 배경 설정 완료")
            
            # 메인 컨테이너
            print("[DEBUG] 메인 컨테이너 생성 중...")
            self.main_container = lv.obj(self.screen)
            self.main_container.set_size(lv.pct(100), lv.pct(100))
            self.main_container.set_flex_flow(lv.FLEX_FLOW.COLUMN)
            self.main_container.set_style_bg_opa(0, 0)
            self.main_container.set_style_border_width(0, 0)
            self.main_container.set_style_pad_all(0, 0)
            print("[DEBUG] 메인 컨테이너 생성 완료")
            
            print("[DEBUG] 제목 영역 생성 중...")
            self._create_title_area()
            self.memory_monitor.log_memory_usage("제목 영역 생성 완료")
            print("[DEBUG] 제목 영역 생성 완료")
            
            print("[DEBUG] 설정 목록 생성 중...")
            self._create_settings_list()
            self.memory_monitor.log_memory_usage("설정 목록 생성 완료")
            print("[DEBUG] 설정 목록 생성 완료")
            
            print("[DEBUG] 버튼 힌트 영역 생성 중...")
            self._create_button_hints_area()
            self.memory_monitor.log_memory_usage("버튼 힌트 영역 생성 완료")
            print("[DEBUG] 버튼 힌트 영역 생성 완료")
            
            print("[OK] UI 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] UI 생성 실패: {e}")
            import sys
            sys.print_exception(e)
            raise e
    
    def _create_title_area(self):
        """제목 영역 생성 (간소화)"""
        try:
            print("[DEBUG] 제목 라벨 생성 중...")
            # 제목 라벨만 생성 (컨테이너 없이)
            self.title_label = lv.label(self.main_container)
            self.title_label.set_text("고급 설정")
            # 한글 폰트 적용
            try:
                self.title_label.set_style_text_font(self.ui_style.get_font('title_font'), 0)
                print("[DEBUG] 제목 폰트 설정 완료")
            except Exception as e:
                print(f"[WARN] 제목 폰트 설정 실패: {e}")
            self.title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)  # 흰색 텍스트
            self.title_label.set_pos(5, 5)  # 간단한 위치 설정
            print("[DEBUG] 제목 라벨 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] 제목 영역 생성 실패: {e}")
            import sys
            sys.print_exception(e)
            raise e
    
    def _create_settings_list(self):
        """설정 목록 영역 생성 - 단순한 라벨 방식 (메모리 절약)"""
        try:
            print("[INFO] 단순한 설정 목록 생성 시작 (메모리 절약)")
            
            # 단순한 컨테이너 생성 (스크롤바 제거)
            self.settings_list_container = lv.obj(self.main_container)
            self.settings_list_container.set_size(lv.pct(100), 80)  # 고정 높이로 변경
            self.settings_list_container.set_style_bg_opa(0, 0)
            self.settings_list_container.set_style_border_width(0, 0)
            self.settings_list_container.set_style_pad_all(0, 0)  # 패딩 제거
            self.settings_list_container.set_style_radius(0, 0)  # 모서리 둥글기 제거
            self.settings_list_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)  # 스크롤바 완전 비활성화
            
            # 설정 항목들을 단순한 라벨로 생성
            for i, option in enumerate(self.settings_options):
                self._create_simple_menu_item(i, option)
                
            print("[OK] 단순한 메뉴 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] 메뉴 생성 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _create_simple_fallback(self):
        """단순한 폴백 메뉴 생성"""
        try:
            print("[INFO] 단순한 폴백 메뉴 생성")
            
            # 단순한 컨테이너 생성
            self.settings_list_container = lv.obj(self.main_container)
            self.settings_list_container.set_size(lv.pct(100), lv.pct(70))
            self.settings_list_container.set_style_bg_opa(0, 0)
            self.settings_list_container.set_style_border_width(0, 0)
            self.settings_list_container.set_style_pad_all(5, 0)
            
            # 설정 항목들을 단순한 라벨로 생성
            for i, option in enumerate(self.settings_options):
                self._create_simple_menu_item(i, option)
                
            print("[OK] 단순한 폴백 메뉴 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] 폴백 메뉴 생성 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _create_simple_menu_item(self, index, option):
        """초간단 메뉴 아이템 생성 (메모리 절약)"""
        try:
            print(f"[DEBUG] 메뉴 아이템 {index} 생성 시작: {option['name']}")
            
            # 라벨만 생성 (컨테이너 없이)
            item_label = lv.label(self.settings_list_container)
            print(f"[DEBUG] 메뉴 아이템 {index} 라벨 생성 완료")
            
            # 심볼 제거하고 숫자만 사용
            item_text = option['name']
            item_label.set_text(item_text)
            print(f"[DEBUG] 메뉴 아이템 {index} 텍스트 설정 완료")
            
            # 한글 폰트 적용
            try:
                item_label.set_style_text_font(self.ui_style.get_font('small_font'), 0)
                print(f"[DEBUG] 메뉴 아이템 {index} 폰트 설정 완료")
            except Exception as e:
                print(f"[WARN] 메뉴 아이템 {index} 폰트 설정 실패: {e}")
            
            # 선택된 항목은 파란색, 나머지는 흰색
            if index == self.current_selection:
                item_label.set_style_text_color(lv.color_hex(0x007AFF), 0)  # 파란색
            else:
                item_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)  # 흰색
            print(f"[DEBUG] 메뉴 아이템 {index} 색상 설정 완료")
            
            # 위치 설정 (세로로 배치) - 5픽셀 위로 이동
            y_pos = index * 20 + 20  # 5픽셀 위로 이동 (5 → 20)
            item_label.set_pos(5, y_pos)
            print(f"[DEBUG] 메뉴 아이템 {index} 위치 설정 완료")
            
            # 라벨만 저장
            if not hasattr(self, 'menu_labels'):
                self.menu_labels = []
            self.menu_labels.append(item_label)
            
            print(f"[OK] 메뉴 아이템 {index} 생성: {option['name']}")
            
        except Exception as e:
            print(f"[ERROR] 메뉴 아이템 {index} 생성 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _create_settings_list_fallback(self):
        """설정 목록 영역 생성 (폴백 방식)"""
        self.settings_list_container = lv.obj(self.main_container)
        self.settings_list_container.set_size(lv.pct(100), lv.pct(70))
        self.settings_list_container.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.settings_list_container.set_style_bg_opa(0, 0)
        self.settings_list_container.set_style_border_width(0, 0)
        self.settings_list_container.set_style_pad_all(0, 0)
        self.settings_list_container.set_style_pad_row(3, 0)
        
        # 설정 항목들 생성
        for i, option in enumerate(self.settings_options):
            self._create_setting_item(i, option)
    
    def _on_menu_item_clicked(self, index):
        """메뉴 아이템 클릭 처리"""
        try:
            if index < len(self.settings_options):
                option = self.settings_options[index]
                print(f"[INFO] 메뉴 선택: {option['name']}")
                option["action"]()
        except Exception as e:
            print(f"[ERROR] 메뉴 아이템 클릭 처리 실패: {e}")
    
    def _create_setting_item(self, index, option):
        """설정 항목 생성"""
        item_container = lv.obj(self.settings_list_container)
        item_container.set_size(lv.pct(100), 25)
        item_container.set_flex_flow(lv.FLEX_FLOW.ROW)
        item_container.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        item_container.set_style_bg_opa(0, 0)
        item_container.set_style_border_width(0, 0)
        item_container.set_style_pad_all(0, 0)
        
        # 선택 표시 (현재 선택된 항목)
        if index == self.current_selection:
            item_container.set_style_bg_color(lv.color_hex(0x007AFF), 0)  # 파란색 강조
            item_container.set_style_bg_opa(20, 0)
        
        # 아이콘
        icon_label = lv.label(item_container)
        icon_label.set_text(option["icon"])
        icon_label.set_style_text_font(self.ui_style.get_font('icon_font'), 0)
        icon_label.set_style_text_color(lv.color_hex(0x007AFF), 0)  # 파란색
        icon_label.set_width(20)
        
        # 설정 이름
        name_label = lv.label(item_container)
        name_label.set_text(option["name"])
        name_label.set_style_text_font(self.ui_style.get_font('small_font'), 0)
        name_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)  # 흰색
        name_label.set_width(100)
        
        # 화살표 아이콘
        arrow_label = lv.label(item_container)
        arrow_label.set_text(lv.SYMBOL.RIGHT)
        arrow_label.set_style_text_font(self.ui_style.get_font('icon_font'), 0)
        arrow_label.set_style_text_color(lv.color_hex(0x8E8E93), 0)  # 회색
        arrow_label.set_width(20)
    
    def _create_button_hints_area(self):
        """하단 버튼 힌트 영역 생성 (간소화)"""
        try:
            print("[DEBUG] 힌트 라벨 생성 중...")
            # 힌트 라벨만 생성 (컨테이너 없이)
            hint_label = lv.label(self.main_container)
            hint_label.set_text(f"A:{lv.SYMBOL.UP} B:{lv.SYMBOL.DOWN} C:{lv.SYMBOL.LEFT} D:선택")
            hint_label.set_style_text_color(lv.color_hex(0x8E8E93), 0)  # 회색
            hint_label.set_pos(5, 110)  # 하단에 위치 (더 아래로)
            print("[DEBUG] 힌트 라벨 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] 버튼 힌트 영역 생성 실패: {e}")
            import sys
            sys.print_exception(e)
            raise e
    
    def _update_selection_display(self):
        """선택 표시 업데이트 (간단한 색상 변경)"""
        try:
            # 라벨 방식인 경우 색상으로만 선택 표시
            if hasattr(self, 'menu_labels') and self.menu_labels:
                for i, label in enumerate(self.menu_labels):
                    if i == self.current_selection:
                        label.set_style_text_color(lv.color_hex(0x007AFF), 0)  # 파란색
                    else:
                        label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)  # 흰색
                print(f"[INFO] 선택 표시 업데이트: 항목 {self.current_selection + 1}")
                return
                    
        except Exception as e:
            print(f"[ERROR] 선택 표시 업데이트 실패: {e}")
    
    def on_button_a(self):
        """버튼 A - 이전 항목"""
        print("🔵 버튼 A: 이전 설정 항목")
        self.current_selection = (self.current_selection - 1) % len(self.settings_options)
        self._update_selection_display()
        print(f"[OK] 선택: {self.settings_options[self.current_selection]['name']}")
    
    def on_button_b(self):
        """버튼 B - 다음 항목"""
        print("🔴 버튼 B: 다음 설정 항목")
        self.current_selection = (self.current_selection + 1) % len(self.settings_options)
        self._update_selection_display()
        print(f"[OK] 선택: {self.settings_options[self.current_selection]['name']}")
    
    def on_button_c(self):
        """버튼 C - 뒤로가기 (메인 화면으로)"""
        print("🟡 버튼 C: 뒤로가기 (메인 화면)")
        self.screen_manager.show_screen("main")
    
    def on_button_d(self):
        """버튼 D - 선택된 설정 실행"""
        selected_option = self.settings_options[self.current_selection]
        print(f"🟢 버튼 D: {selected_option['name']} 선택")
        
        try:
            if selected_option['key'] == 'system':
                self._show_system_settings()
            elif selected_option['key'] == 'alarm':
                self._show_alarm_settings()
            elif selected_option['key'] == 'data':
                self._show_data_management()
            elif selected_option['key'] == 'info':
                self._show_system_info()
        except Exception as e:
            print(f"[ERROR] 설정 실행 실패: {e}")
    
    def _show_system_settings(self):
        """시스템 설정 표시"""
        print("[INFO] 시스템 설정 표시")
        # TODO: 시스템 설정 화면 구현
    
    def _show_alarm_settings(self):
        """알람 설정 표시"""
        print("[INFO] 알람 설정 표시")
        # TODO: 알람 설정 화면 구현
    
    def _show_data_management(self):
        """데이터 관리 표시"""
        print("[INFO] 데이터 관리 화면으로 전환")
        try:
            # 데이터 관리 화면 생성 및 전환
            self.screen_manager.show_screen("data_management")
        except Exception as e:
            print(f"[ERROR] 데이터 관리 화면 전환 실패: {e}")
            # 폴백: 간단한 데이터 관리 메뉴 표시
            self._show_simple_data_menu()
    
    def _show_simple_data_menu(self):
        """간단한 데이터 관리 메뉴 표시"""
        try:
            print("[INFO] 간단한 데이터 관리 메뉴 표시")
            
            # 현재 데이터 상태 표시
            print("=== 데이터 관리 ===")
            
            # 배출 기록 확인
            today_logs = self.data_manager.get_today_dispense_logs()
            print(f"오늘 배출 기록: {len(today_logs)}건")
            
            # 약물 데이터 확인
            medication_data = self.data_manager.load_medication_data()
            if medication_data:
                for i, disk in enumerate(medication_data.get('disks', []), 1):
                    quantity = disk.get('quantity', 0)
                    print(f"디스크 {i} 수량: {quantity}개")
            
            # 메모리 상태
            memory_info = self.memory_monitor.get_memory_info()
            if memory_info:
                print(f"메모리 사용량: {memory_info['usage_percent']:.1f}%")
                print(f"여유 메모리: {memory_info['free']:,} bytes")
            
            print("=== 데이터 관리 완료 ===")
            
        except Exception as e:
            print(f"[ERROR] 데이터 관리 메뉴 표시 실패: {e}")
    
    def _show_system_info(self):
        """시스템 정보 표시"""
        print("[INFO] 시스템 정보 표시")
        # TODO: 시스템 정보 화면 구현
    
    def show(self):
        """화면 표시"""
        try:
            # 메모리 상태 확인
            self.memory_monitor.log_memory_usage("화면 표시 시작")
            
            # 메모리 정리
            import gc
            gc.collect()
            print("[DEBUG] 메모리 정리 완료")
            
            # 메모리 상태 재확인
            self.memory_monitor.log_memory_usage("메모리 정리 후")
            
            # 화면 로드
            lv.screen_load(self.screen)
            print(f"[OK] {self.screen_name} 화면 로드 완료")
            
            # 최종 메모리 상태 확인
            self.memory_monitor.log_memory_usage("화면 로드 완료")
            
        except Exception as e:
            print(f"[ERROR] 화면 로드 실패: {e}")
            self.memory_monitor.log_memory_usage("화면 로드 실패")
            import sys
            sys.print_exception(e)
    
    def hide(self):
        """화면 숨김"""
        print(f"[INFO] {self.screen_name} 화면 숨김")
    
    def update(self):
        """화면 업데이트 (주기적으로 호출)"""
        pass
