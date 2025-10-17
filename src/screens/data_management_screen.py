"""
데이터 관리 화면
배출 기록, 약물 수량, 시스템 데이터 관리
"""

import sys
sys.path.append("/")

import lvgl as lv
from ui_style import UIStyle
from data_manager import DataManager
from memory_monitor import MemoryMonitor

class DataManagementScreen:
    """데이터 관리 화면 클래스"""
    
    def __init__(self, screen_manager):
        self.screen_manager = screen_manager
        self.data_manager = DataManager()
        self.memory_monitor = MemoryMonitor()
        self.screen = lv.obj()
        self.screen_name = "data_management"
        self.ui_style = UIStyle()
        
        self.current_selection = 0
        self.data_options = [
            {"name": "1. 배출 기록 초기화", "key": "clear_logs"},
            {"name": "2. 약물 수량 확인", "key": "check_quantity"},
            {"name": "3. 메모리 상태", "key": "memory_status"},
            {"name": "4. 뒤로가기", "key": "back"}
        ]
        
        self.memory_monitor.log_memory_usage("데이터관리 초기화 시작")
        
        self._create_ui()
        
        self.memory_monitor.log_memory_usage("데이터관리 초기화 완료")
        
        print(f"[OK] {self.screen_name} 초기화 완료")
    
    def _create_ui(self):
        """UI 생성 (초간단 버전)"""
        try:
            print("[DEBUG] 데이터관리 UI 생성 시작 (초간단)")
            
            # 메모리 정리
            import gc
            gc.collect()
            print("[DEBUG] UI 생성 전 메모리 정리 완료")
            
            # 화면 배경 설정
            self.screen.set_style_bg_color(lv.color_hex(0x000000), 0)  # 검은색 배경
            self.screen.set_style_pad_all(5, 0)
            
            # 제목 라벨만 생성
            self.title_label = lv.label(self.screen)
            self.title_label.set_text("데이터 관리")
            self.title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
            self.title_label.set_pos(5, 5)
            
            # 메뉴 항목들 생성
            for i, option in enumerate(self.data_options):
                item_label = lv.label(self.screen)
                item_label.set_text(option['name'])
                item_label.set_style_text_color(lv.color_hex(0x007AFF) if i == self.current_selection else lv.color_hex(0xFFFFFF), 0)
                item_label.set_pos(5, 25 + i * 20)
                
                if not hasattr(self, 'data_labels'):
                    self.data_labels = []
                self.data_labels.append(item_label)
            
            # 버튼 힌트
            hint_label = lv.label(self.screen)
            hint_label.set_text("A:이전 B:다음 C:뒤로 D:선택")
            hint_label.set_style_text_color(lv.color_hex(0x8E8E93), 0)
            hint_label.set_pos(5, 120)
            
            print("[OK] 데이터관리 UI 생성 완료 (초간단)")
            
        except Exception as e:
            print(f"[ERROR] 데이터관리 UI 생성 실패: {e}")
            import sys
            sys.print_exception(e)
            raise e
    
    def _create_title_area(self):
        """제목 영역 생성"""
        try:
            self.title_container = lv.obj(self.main_container)
            self.title_container.set_size(lv.pct(100), 20)
            self.title_container.set_style_bg_opa(0, 0)
            self.title_container.set_style_border_width(0, 0)
            self.title_container.set_style_pad_all(0, 0)
            self.title_container.set_flex_flow(lv.FLEX_FLOW.ROW)
            self.title_container.set_flex_align(lv.FLEX_ALIGN.SPACE_BETWEEN, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
            
            # 제목 라벨
            self.title_label = lv.label(self.title_container)
            self.title_label.set_text("데이터 관리")
            self.title_label.set_style_text_font(self.ui_style.get_font('title_font'), 0)
            self.title_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)  # 흰색 텍스트
            self.title_label.align(lv.ALIGN.LEFT_MID, 0, 0)
            
            # 뒤로가기 아이콘
            self.back_icon = lv.label(self.title_container)
            self.back_icon.set_text(lv.SYMBOL.LEFT)
            self.back_icon.set_style_text_color(lv.color_hex(0x007AFF), 0)  # 파란색
            self.back_icon.align(lv.ALIGN.RIGHT_MID, 0, 0)
            
        except Exception as e:
            print(f"[ERROR] 제목 영역 생성 실패: {e}")
            import sys
            sys.print_exception(e)
            raise e
    
    def _create_data_list(self):
        """데이터 관리 목록 생성"""
        try:
            print("[INFO] 데이터 관리 목록 생성 시작")
            
            # 목록 컨테이너 생성
            self.data_list_container = lv.obj(self.main_container)
            self.data_list_container.set_size(lv.pct(100), lv.pct(70))
            self.data_list_container.set_style_bg_opa(0, 0)
            self.data_list_container.set_style_border_width(0, 0)
            self.data_list_container.set_style_pad_all(5, 0)
            
            # 데이터 관리 항목들을 생성
            for i, option in enumerate(self.data_options):
                self._create_data_item(i, option)
                
            print("[OK] 데이터 관리 목록 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] 데이터 목록 생성 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _create_data_item(self, index, option):
        """데이터 관리 항목 생성"""
        try:
            print(f"[DEBUG] 데이터 항목 {index} 생성 시작: {option['name']}")
            
            # 항목 컨테이너 생성 (하이라이트용)
            item_container = lv.obj(self.data_list_container)
            item_container.set_size(lv.pct(95), 22)
            
            # 선택된 항목 하이라이트 설정
            if index == self.current_selection:
                item_container.set_style_bg_color(lv.color_hex(0x007AFF), 0)  # 파란색 배경
                item_container.set_style_bg_opa(30, 0)  # 30% 투명도
                item_container.set_style_border_color(lv.color_hex(0x007AFF), 0)  # 파란색 테두리
                item_container.set_style_border_width(1, 0)
                item_container.set_style_border_opa(100, 0)
            else:
                item_container.set_style_bg_opa(0, 0)  # 투명 배경
                item_container.set_style_border_width(0, 0)
            
            # 항목 라벨 생성
            item_label = lv.label(item_container)
            item_text = option['name']
            item_label.set_text(item_text)
            
            # 한글 폰트 적용
            try:
                item_label.set_style_text_font(self.ui_style.get_font('small_font'), 0)
            except Exception as e:
                print(f"[WARN] 데이터 항목 {index} 폰트 설정 실패: {e}")
            
            # 선택된 항목은 흰색, 나머지는 회색
            if index == self.current_selection:
                item_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)  # 흰색 (하이라이트 배경에)
            else:
                item_label.set_style_text_color(lv.color_hex(0xCCCCCC), 0)  # 밝은 회색
            
            # 라벨을 컨테이너 중앙에 배치
            item_label.align(lv.ALIGN.CENTER, 0, 0)
            
            # 위치 설정 (세로로 배치)
            y_pos = index * 25 + 5
            item_container.set_pos(5, y_pos)
            
            # 컨테이너와 라벨을 저장하여 나중에 업데이트 가능하도록 함
            if not hasattr(self, 'data_containers'):
                self.data_containers = []
            if not hasattr(self, 'data_labels'):
                self.data_labels = []
            self.data_containers.append(item_container)
            self.data_labels.append(item_label)
            
            print(f"[OK] 데이터 항목 {index} 생성: {option['name']}")
            
        except Exception as e:
            print(f"[ERROR] 데이터 항목 {index} 생성 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _create_button_hints_area(self):
        """하단 버튼 힌트 영역 생성"""
        try:
            self.hints_container = lv.obj(self.main_container)
            self.hints_container.set_size(lv.pct(100), 15)
            self.hints_container.set_style_bg_opa(0, 0)
            self.hints_container.set_style_border_width(0, 0)
            self.hints_container.set_style_pad_all(0, 0)
            self.hints_container.set_flex_flow(lv.FLEX_FLOW.ROW)
            self.hints_container.set_flex_align(lv.FLEX_ALIGN.SPACE_AROUND, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
            
            hint_label = lv.label(self.hints_container)
            hint_label.set_text(f"A:{lv.SYMBOL.UP} B:{lv.SYMBOL.DOWN} C:{lv.SYMBOL.LEFT} D:선택")
            hint_label.set_style_text_color(lv.color_hex(0x8E8E93), 0)  # 회색
            
        except Exception as e:
            print(f"[ERROR] 버튼 힌트 영역 생성 실패: {e}")
            import sys
            sys.print_exception(e)
            raise e
    
    def _update_selection_display(self):
        """선택 표시 업데이트 (간단한 색상 변경)"""
        try:
            # 라벨 방식인 경우 색상으로만 선택 표시
            if hasattr(self, 'data_labels') and self.data_labels:
                for i, label in enumerate(self.data_labels):
                    if i == self.current_selection:
                        label.set_style_text_color(lv.color_hex(0x007AFF), 0)  # 파란색
                    else:
                        label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)  # 흰색
                print(f"[INFO] 데이터관리 선택 표시 업데이트: 항목 {self.current_selection + 1}")
                return
                    
        except Exception as e:
            print(f"[ERROR] 선택 표시 업데이트 실패: {e}")
    
    def on_button_a(self):
        """버튼 A - 이전 항목"""
        print("🔵 버튼 A: 이전 데이터 항목")
        self.current_selection = (self.current_selection - 1) % len(self.data_options)
        self._update_selection_display()
        print(f"[OK] 선택: {self.data_options[self.current_selection]['name']}")
    
    def on_button_b(self):
        """버튼 B - 다음 항목"""
        print("🔴 버튼 B: 다음 데이터 항목")
        self.current_selection = (self.current_selection + 1) % len(self.data_options)
        self._update_selection_display()
        print(f"[OK] 선택: {self.data_options[self.current_selection]['name']}")
    
    def on_button_c(self):
        """버튼 C - 뒤로가기 (고급 설정 화면으로)"""
        print("🟡 버튼 C: 뒤로가기 (고급 설정)")
        self.screen_manager.show_screen("advanced_settings")
    
    def on_button_d(self):
        """버튼 D - 선택된 데이터 관리 기능 실행"""
        selected_option = self.data_options[self.current_selection]
        print(f"🟢 버튼 D: {selected_option['name']} 선택")
        
        try:
            if selected_option['key'] == 'clear_logs':
                self._clear_dispense_logs()
            elif selected_option['key'] == 'check_quantity':
                self._check_medication_quantity()
            elif selected_option['key'] == 'memory_status':
                self._show_memory_status()
            elif selected_option['key'] == 'back':
                self.screen_manager.show_screen("advanced_settings")
        except Exception as e:
            print(f"[ERROR] 데이터 관리 기능 실행 실패: {e}")
    
    def _clear_dispense_logs(self):
        """배출 기록 초기화"""
        try:
            print("[INFO] 배출 기록 초기화 시작")
            
            # 오늘 배출 기록 확인
            today_logs = self.data_manager.get_today_dispense_logs()
            print(f"현재 오늘 배출 기록: {len(today_logs)}건")
            
            if len(today_logs) > 0:
                # 배출 기록 초기화
                self.data_manager.clear_today_dispense_logs()
                print("[OK] 오늘 배출 기록 초기화 완료")
            else:
                print("[INFO] 초기화할 배출 기록이 없습니다")
                
        except Exception as e:
            print(f"[ERROR] 배출 기록 초기화 실패: {e}")
    
    def _check_medication_quantity(self):
        """약물 수량 확인"""
        try:
            print("[INFO] 약물 수량 확인")
            
            # 약물 데이터 로드
            medication_data = self.data_manager.load_medication_data()
            if medication_data:
                print("=== 약물 수량 현황 ===")
                for i, disk in enumerate(medication_data.get('disks', []), 1):
                    quantity = disk.get('quantity', 0)
                    max_quantity = disk.get('max_quantity', 30)
                    percentage = (quantity / max_quantity) * 100 if max_quantity > 0 else 0
                    
                    status = "🟢 충분" if percentage > 50 else "🟡 부족" if percentage > 20 else "🔴 위험"
                    print(f"디스크 {i}: {quantity}/{max_quantity}개 ({percentage:.1f}%) {status}")
                print("========================")
            else:
                print("[WARN] 약물 데이터를 불러올 수 없습니다")
                
        except Exception as e:
            print(f"[ERROR] 약물 수량 확인 실패: {e}")
    
    def _show_memory_status(self):
        """메모리 상태 표시"""
        try:
            print("[INFO] 메모리 상태 확인")
            
            # 메모리 정보 수집
            memory_info = self.memory_monitor.get_memory_info()
            if memory_info:
                print("=== 메모리 상태 ===")
                print(f"사용량: {memory_info['allocated']:,} bytes ({memory_info['usage_percent']:.1f}%)")
                print(f"여유량: {memory_info['free']:,} bytes")
                print(f"총량: {memory_info['total']:,} bytes")
                if memory_info['stack'] > 0:
                    print(f"스택: {memory_info['stack']:,} bytes")
                
                # 상태 판정
                if memory_info['free'] < 5000:
                    print("🔴 CRITICAL: 메모리 부족!")
                elif memory_info['free'] < 10000:
                    print("🟠 WARNING: 메모리 부족 경고")
                else:
                    print("🟢 OK: 메모리 상태 양호")
                print("==================")
            else:
                print("[WARN] 메모리 정보를 가져올 수 없습니다")
                
        except Exception as e:
            print(f"[ERROR] 메모리 상태 확인 실패: {e}")
    
    def show(self):
        """화면 표시"""
        try:
            self.memory_monitor.log_memory_usage("데이터관리 화면 표시 시작")
            
            import gc
            gc.collect()
            print("[DEBUG] 메모리 정리 완료")
            
            self.memory_monitor.log_memory_usage("메모리 정리 후")
            
            lv.screen_load(self.screen)
            print(f"[OK] {self.screen_name} 화면 로드 완료")
            
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
