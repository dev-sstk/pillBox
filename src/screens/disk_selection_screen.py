"""
디스크 선택 화면
체크박스를 활용한 중복 선택 가능한 UI (meal_time_screen.py와 동일한 구조)
"""

import lvgl as lv
import time
from ui_style import UIStyle
from global_data import global_data

class DiskSelectionScreen:
    """디스크 선택 화면 클래스 - meal_time_screen.py와 동일한 구조"""
    
    def __init__(self, screen_manager, dose_info=None):
        self.screen_manager = screen_manager
        self.screen_name = "disk_selection"
        self.screen_obj = None
        self.ui_style = None
        self.dose_info = dose_info or {}
        
        # 선택된 디스크들 (중복 선택 가능)
        self.selected_disks = {
            1: False,  # 디스크 1
            2: False,  # 디스크 2
            3: False   # 디스크 3
        }
        
        # UI 컴포넌트들
        self.main_container = None
        self.title_label = None
        self.disk_checkboxes = {}
        self.disk_labels = {}
        self.current_selection = 0  # 현재 선택된 항목 인덱스 (0: 디스크1, 1: 디스크2, 2: 디스크3)
        
        print(f"[INFO] {self.screen_name} 화면 초기화 완료")
        print(f"[INFO] 복용 정보: {self.dose_info}")
        
        # 화면 자동 생성
        self.create_screen()
    
    def create_screen(self):
        """화면 생성"""
        print(f"[INFO] {self.screen_name} 화면 생성 시작...")
        
        try:
            # UI 스타일 초기화
            self.ui_style = UIStyle()
            print(f"[OK] UI 스타일 초기화 완료")
            
            # Modern 화면 생성 시도
            try:
                self._create_modern_screen()
            except Exception as e:
                print(f"[WARN] Modern 화면 생성 실패, 기본 화면으로 대체: {e}")
                self._create_basic_screen()
            
            print(f"[OK] {self.screen_name} 화면 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] {self.screen_name} 화면 생성 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _create_basic_screen(self):
        """기본 화면 생성 (폴백)"""
        print(f"[INFO] {self.screen_name} 기본 화면 생성 시작...")
        
        # 기본 화면 객체 생성
        self.screen_obj = lv.obj()
        self.screen_obj.set_size(160, 128)
        
        # 기본 라벨 생성
        self.title_label = lv.label(self.screen_obj)
        self.title_label.set_text("디스크 선택")
        self.title_label.align(lv.ALIGN.CENTER, 0, -20)
        
        # 기본 버튼 힌트 생성
        try:
            self.hints_label = lv.label(self.screen_obj)
            self.hints_label.set_text(f"A:O B:{lv.SYMBOL.UP} C:{lv.SYMBOL.DOWN} D:{lv.SYMBOL.NEXT}")
            self.hints_label.align(lv.ALIGN.BOTTOM_MID, 0, -2)
            self.hints_label.set_style_text_color(lv.color_hex(0x8E8E93), 0)
            self.hints_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            print(f"  [OK] 기본 버튼 힌트 생성 완료 (LVGL 심볼 사용)")
        except Exception as e:
            print(f"  [WARN] 기본 버튼 힌트 생성 실패: {e}")
        
        print(f"  [OK] 기본 화면 생성 완료")
    
    def _create_modern_screen(self):
        """Modern 화면 생성"""
        print(f"[INFO] {self.screen_name} Modern 화면 생성 시작...")
        
        try:
            # 화면 객체 생성
            print(f"  [INFO] 화면 객체 생성...")
            self.screen_obj = lv.obj()
            print(f"  [INFO] 화면 객체 생성됨: {self.screen_obj}")
            
            # 화면 배경 설정
            self.screen_obj.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)  # 흰색 배경
            self.screen_obj.set_style_bg_opa(255, 0)
            print(f"  [OK] 화면 배경 설정 완료")
            
            # 화면 크기 설정
            self.screen_obj.set_size(160, 128)
            print(f"  [OK] 화면 크기 설정 완료")
            
            # 제목 영역 생성
            self._create_title_area()
            
            # 디스크 선택 영역 생성
            self._create_disk_selection_area()
            
            # 버튼 힌트 영역 생성
            self._create_button_hints_area()
            
            print(f"  [OK] Modern 화면 생성 완료")
            
        except Exception as e:
            print(f"  [ERROR] Modern 화면 생성 실패: {e}")
            import sys
            sys.print_exception(e)
            raise e
    
    def _create_title_area(self):
        """제목 영역 생성"""
        try:
            print(f"  [INFO] 제목 영역 생성 시작...")
            
            # 제목 라벨 생성
            self.title_label = lv.label(self.screen_obj)
            self._update_title_text()
            self.title_label.align(lv.ALIGN.TOP_MID, 0, 10)
            self.title_label.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
            
            # 한국어 폰트 적용
            try:
                korean_font = getattr(lv, "font_notosans_kr_regular", None)
                if korean_font:
                    self.title_label.set_style_text_font(korean_font, 0)
                    print(f"  [OK] 제목 한국어 폰트 적용 완료")
            except Exception as e:
                print(f"  [WARN] 제목 한국어 폰트 적용 실패: {e}")
            
            print(f"  [OK] 제목 영역 생성 완료")
            
        except Exception as e:
            print(f"  [ERROR] 제목 영역 생성 실패: {e}")
            import sys
            sys.print_exception(e)
            raise e
    
    def _update_title_text(self):
        """제목 텍스트 업데이트"""
        try:
            if hasattr(self, 'title_label'):
                # 간단한 제목으로 변경
                title_text = "디스크 선택"
                self.title_label.set_text(title_text)
                print(f"[INFO] 제목 업데이트: {title_text}")
        except Exception as e:
            print(f"[ERROR] 제목 텍스트 업데이트 실패: {e}")
    
    def _create_disk_selection_area(self):
        """디스크 선택 영역 생성"""
        try:
            print(f"  [INFO] 디스크 선택 영역 생성 시작...")
            
            # 디스크 선택 컨테이너 생성 (화면 중앙 정렬)
            self.disk_selection_container = lv.obj(self.screen_obj)
            self.disk_selection_container.set_size(140, 80)
            self.disk_selection_container.align(lv.ALIGN.CENTER, 0, 5)  # 중앙 정렬
            self.disk_selection_container.set_style_bg_opa(0, 0)
            self.disk_selection_container.set_style_border_width(0, 0)
            self.disk_selection_container.set_style_pad_all(0, 0)
            self.disk_selection_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            print(f"  [OK] 디스크 선택 컨테이너 생성 완료")
            
            # 3개 디스크 옵션 생성
            disk_options = [
                {"key": 1, "name": "디스크 1"},
                {"key": 2, "name": "디스크 2"},
                {"key": 3, "name": "디스크 3"}
            ]
            
            print(f"  [INFO] 3개 디스크 옵션 생성 시작...")
            for i, option in enumerate(disk_options):
                print(f"  [INFO] {option['name']} 옵션 생성 중... (y_offset: {i * 25})")
                self._create_disk_option(option, i * 25)
                print(f"  [OK] {option['name']} 옵션 생성 완료")
            
            print(f"  [OK] 디스크 선택 영역 생성 완료")
            
        except Exception as e:
            print(f"  [ERROR] 디스크 선택 영역 생성 실패: {e}")
            import sys
            sys.print_exception(e)
            raise e
    
    def _create_disk_option(self, option, y_offset):
        """디스크 옵션 생성"""
        try:
            disk_key = option["key"]
            disk_name = option["name"]
            
            # 체크박스 생성 (중앙 정렬)
            checkbox = lv.checkbox(self.disk_selection_container)
            checkbox.set_text("")
            checkbox.set_size(20, 20)
            checkbox.set_pos(30, y_offset)  # 왼쪽으로 5픽셀 추가 이동 (35-5=30)
            checkbox.set_style_bg_opa(0, 0)
            checkbox.set_style_border_width(0, 0)
            checkbox.set_style_pad_all(0, 0)
            print(f"    [INFO] {disk_name} 체크박스 객체 생성됨")
            
            # 체크박스 스타일 설정 (meal_time_screen.py와 동일)
            try:
                # 체크박스 내부 배경 색상을 흰색으로 설정
                checkbox.set_style_bg_color(lv.color_hex(0xFFFFFF), lv.PART.INDICATOR)
                checkbox.set_style_bg_opa(255, lv.PART.INDICATOR)
                # 체크박스 테두리 색상을 로고 색상으로 설정
                checkbox.set_style_border_color(lv.color_hex(0xd2b13f), lv.PART.INDICATOR)
                checkbox.set_style_border_width(2, lv.PART.INDICATOR)
                # 체크 표시 색상을 검정색으로 설정
                checkbox.set_style_text_color(lv.color_hex(0x000000), lv.PART.INDICATOR)
                # 선택됐을 때 내부 색상을 로고 색상으로 변경
                checkbox.set_style_bg_color(lv.color_hex(0xd2b13f), lv.PART.INDICATOR | lv.STATE.CHECKED)
                checkbox.set_style_bg_opa(255, lv.PART.INDICATOR | lv.STATE.CHECKED)
                print(f"    [INFO] {disk_name} 체크박스 색상 설정 완료 (흰색 배경, 로고 색상 선택시, 검정 체크)")
            except AttributeError:
                print(f"    [WARN] {disk_name} 체크박스 색상 설정 실패 (LVGL 버전 호환성)")
            print(f"    [OK] {disk_name} 체크박스 설정 완료")
            
            # 디스크 이름 라벨 생성 (중앙 정렬)
            disk_label = lv.label(self.disk_selection_container)
            disk_label.set_text(disk_name)
            disk_label.set_pos(55, y_offset + 2)  # 왼쪽으로 5픽셀 추가 이동 (60-5=55)
            disk_label.set_style_text_color(lv.color_hex(0x333333), 0)
            print(f"    [INFO] {disk_name} 라벨 생성 중...")
            
            # 한국어 폰트 적용
            try:
                korean_font = getattr(lv, "font_notosans_kr_regular", None)
                if korean_font:
                    disk_label.set_style_text_font(korean_font, 0)
                    print(f"    [OK] {disk_name} 한국어 폰트 적용 완료")
            except Exception as e:
                print(f"    [WARN] {disk_name} 한국어 폰트 적용 실패: {e}")
            
            print(f"    [OK] {disk_name} 라벨 생성 완료")
            
            # 화살표 제거 (meal_time_screen.py와 동일)
            try:
                # 체크박스의 화살표 제거 시도
                checkbox.set_style_bg_opa(0, lv.PART.INDICATOR)
                print(f"    [INFO] {disk_name} 화살표 제거됨")
            except Exception as e:
                print(f"    [WARN] {disk_name} 화살표 제거 실패: {e}")
            
            # UI 컴포넌트 저장
            self.disk_checkboxes[disk_key] = checkbox
            self.disk_labels[disk_key] = disk_label
            
            print(f"    [OK] {disk_name} 옵션 생성 완료")
            
        except Exception as e:
            print(f"    [ERROR] {disk_name} 옵션 생성 실패: {e}")
            import sys
            sys.print_exception(e)
            raise e
    
    def _create_button_hints_area(self):
        """버튼 힌트 영역 생성"""
        try:
            print(f"  [INFO] 버튼 힌트 영역 생성 시도...")
            
            # 버튼 힌트 라벨 생성
            self.hints_label = lv.label(self.screen_obj)
            self.hints_label.set_text(f"A:O B:{lv.SYMBOL.UP} C:{lv.SYMBOL.DOWN} D:{lv.SYMBOL.NEXT}")
            self.hints_label.align(lv.ALIGN.BOTTOM_MID, 0, -2)
            self.hints_label.set_style_text_color(lv.color_hex(0x8E8E93), 0)
            self.hints_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            print(f"  [OK] 간단한 버튼 힌트 생성 완료 (LVGL 심볼 사용)")
            
            print(f"  [OK] 버튼 힌트 영역 생성 완료")
            
        except Exception as e:
            print(f"  [ERROR] 버튼 힌트 영역 생성 실패: {e}")
            import sys
            sys.print_exception(e)
            raise e
    
    def _update_selection_display(self):
        """선택 표시 업데이트"""
        try:
            disk_keys = [1, 2, 3]
            
            for i, disk_key in enumerate(disk_keys):
                checkbox = self.disk_checkboxes.get(disk_key)
                disk_label = self.disk_labels.get(disk_key)
                
                if checkbox and disk_label:
                    # 현재 포커스된 디스크는 로고 색상
                    if i == self.current_selection:
                        disk_label.set_style_text_color(lv.color_hex(0xd2b13f), 0)
                    else:
                        disk_label.set_style_text_color(lv.color_hex(0x333333), 0)
                    
                    # 선택된 디스크는 체크 표시
                    if self.selected_disks[disk_key]:
                        checkbox.add_state(lv.STATE.CHECKED)
                    else:
                        checkbox.remove_state(lv.STATE.CHECKED)
            
            print(f"[INFO] 현재 선택: 디스크 {self.current_selection + 1}")
            
        except Exception as e:
            print(f"[ERROR] 선택 표시 업데이트 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def on_button_a(self):
        """A 버튼: 선택/체크박스 토글"""
        try:
            print(f"[BTN] 버튼 A (SW1) 눌림 - 선택/체크박스 토글")
            
            # 현재 포커스된 디스크 선택/해제
            self.toggle_disk_selection()
            
        except Exception as e:
            print(f"  [ERROR] A 버튼 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def on_button_b(self):
        """B 버튼: 위로 이동"""
        try:
            print(f"[BTN] 버튼 B (SW2) 눌림 - 위로 이동")
            self.current_selection = (self.current_selection - 1) % 3
            self._update_selection_display()
            print(f"  [INFO] 포커스 이동: 디스크 {self.current_selection + 1}")
        except Exception as e:
            print(f"  [ERROR] B 버튼 처리 실패: {e}")
    
    def on_button_c(self):
        """C 버튼: 아래로 이동"""
        try:
            print(f"[BTN] 버튼 C (SW3) 눌림 - 아래로 이동")
            self.current_selection = (self.current_selection + 1) % 3
            self._update_selection_display()
            print(f"  [INFO] 포커스 이동: 디스크 {self.current_selection + 1}")
        except Exception as e:
            print(f"  [ERROR] C 버튼 처리 실패: {e}")
    
    def on_button_d(self):
        """D 버튼: 다음 화면으로 - 알약 충전 화면으로"""
        try:
            print(f"[BTN] 버튼 D (SW4) 눌림 - 다음 화면으로 이동")
            
            # 선택된 디스크 정보를 복용 정보에 추가
            selected_disk_list = [disk_key for disk_key, selected in self.selected_disks.items() if selected]
            if not selected_disk_list:
                print(f"  [WARN] 최소 1개 디스크를 선택해주세요")
                return
                
            self.dose_info['selected_disks'] = selected_disk_list
            self.dose_info['disk_count'] = len(selected_disk_list)
            
            print(f"  [INFO] 디스크 선택 완료: {selected_disk_list}")
            
            # 전역 데이터에 저장
            global_data.save_dose_times([self.dose_info])
            
            # 알약 충전 화면으로 이동
            self._go_to_pill_loading_screen()
            
        except Exception as e:
            print(f"  [ERROR] D 버튼 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _go_to_pill_loading_screen(self):
        """알약 충전 화면으로 이동"""
        try:
            print(f"  [INFO] 알약 충전 화면으로 이동 시작...")
            
            # PillLoadingScreen 생성 및 등록
            from screens.pill_loading_screen import PillLoadingScreen
            pill_loading_screen = PillLoadingScreen(self.screen_manager)
            
            # 선택된 디스크 정보 전달
            pill_loading_screen.update_dose_times([self.dose_info])
            pill_loading_screen.set_selected_disks(self.dose_info['selected_disks'])
            
            # 화면 등록 및 이동
            self.screen_manager.register_screen('pill_loading', pill_loading_screen)
            self.screen_manager.show_screen('pill_loading')
            
            print(f"  [OK] 알약 충전 화면으로 이동 완료")
            
        except Exception as e:
            print(f"  [ERROR] 알약 충전 화면 이동 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def toggle_disk_selection(self):
        """현재 포커스된 디스크 선택/해제"""
        try:
            disk_key = self.current_selection + 1
            self.selected_disks[disk_key] = not self.selected_disks[disk_key]
            self._update_selection_display()
            print(f"  [INFO] 디스크 {disk_key} 선택: {self.selected_disks[disk_key]}")
        except Exception as e:
            print(f"  [ERROR] 디스크 선택 토글 실패: {e}")
    
    def update_dose_info(self, dose_info):
        """복용 정보 업데이트"""
        try:
            self.dose_info = dose_info
            self._update_title_text()
            print(f"[INFO] 복용 정보 업데이트: {self.dose_info}")
        except Exception as e:
            print(f"[ERROR] 복용 정보 업데이트 실패: {e}")
    
    def show(self):
        """화면 표시"""
        try:
            print(f"[INFO] {self.screen_name} 화면 표시 시작...")
            
            if hasattr(self, 'screen_obj') and self.screen_obj:
                print(f"[INFO] 화면 객체 존재 확인됨")
                
                lv.screen_load(self.screen_obj)
                print(f"[OK] {self.screen_name} 화면 로드 완료")
                
                # 화면 강제 업데이트
                print(f"[INFO] {self.screen_name} 화면 강제 업데이트 시작...")
                for i in range(5):
                    lv.timer_handler()
                    time.sleep(0.01)
                    print(f"  [INFO] 업데이트 {i+1}/5")
                print(f"[OK] {self.screen_name} 화면 강제 업데이트 완료")
                
                # 디스플레이 플러시
                print(f"[INFO] 디스플레이 플러시 실행...")
                try:
                    lv.disp.flush()
                except Exception as flush_error:
                    print(f"[WARN] 디스플레이 플러시 오류 (무시): {flush_error}")
                
                print(f"[OK] {self.screen_name} 화면 실행됨")
            else:
                print(f"[ERROR] {self.screen_name} 화면 객체가 없음")
                
        except Exception as e:
            print(f"  [ERROR] {self.screen_name} 화면 표시 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def hide(self):
        """화면 숨기기"""
        try:
            print(f"[INFO] {self.screen_name} 화면 숨김")
        except Exception as e:
            print(f"  [ERROR] {self.screen_name} 화면 숨김 실패: {e}")
    
    def update(self):
        """화면 업데이트"""
        try:
            # 현재는 특별한 업데이트 로직이 없음
            pass
        except Exception as e:
            print(f"  [ERROR] {self.screen_name} 화면 업데이트 실패: {e}")