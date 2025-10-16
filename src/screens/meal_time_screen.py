"""
아침/점심/저녁 복용 이벤트 선택 화면
체크박스를 활용한 중복 선택 가능한 UI
"""

import lvgl as lv
from ui_style import UIStyle

class MealTimeScreen:
    """아침/점심/저녁 복용 이벤트 선택 화면 클래스 - Modern UI 스타일"""
    
    def __init__(self, screen_manager):
        self.screen_manager = screen_manager
        self.screen_name = "meal_time"
        self.screen_obj = None
        self.ui_style = None
        
        # 선택된 복용 시간들 (중복 선택 가능)
        self.selected_meals = {
            'breakfast': False,  # 아침
            'lunch': False,      # 점심
            'dinner': False      # 저녁
        }
        
        # UI 컴포넌트들
        self.main_container = None
        self.title_label = None
        self.meal_checkboxes = {}
        self.meal_labels = {}
        self.current_selection = 0  # 현재 선택된 항목 인덱스 (0: 아침, 1: 점심, 2: 저녁)
        
        print(f"📱 {self.screen_name} 화면 초기화 완료")
    
    def create_screen(self):
        """화면 생성"""
        print(f"📱 {self.screen_name} 화면 생성 시작...")
        
        try:
            # UI 스타일 초기화
            self.ui_style = UIStyle()
            print(f"✅ UI 스타일 초기화 완료")
            
            # Modern 화면 생성 시도
            try:
                self._create_modern_screen()
            except Exception as e:
                print(f"⚠️ Modern 화면 생성 실패, 기본 화면으로 대체: {e}")
                self._create_basic_screen()
            
            print(f"✅ {self.screen_name} 화면 생성 완료")
            
        except Exception as e:
            print(f"❌ {self.screen_name} 화면 생성 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _create_basic_screen(self):
        """기본 화면 생성 (폴백)"""
        print(f"📱 {self.screen_name} 기본 화면 생성 시작...")
        
        # 기본 화면 객체 생성
        self.screen_obj = lv.obj()
        self.screen_obj.set_size(160, 128)
        
        # 기본 라벨 생성
        self.title_label = lv.label(self.screen_obj)
        self.title_label.set_text("복용 시간 선택")
        self.title_label.align(lv.ALIGN.CENTER, 0, -20)
        
        # 기본 버튼 힌트 생성
        try:
            self.hints_label = lv.label(self.screen_obj)
            self.hints_label.set_text(f"A:{lv.SYMBOL.UP} B:{lv.SYMBOL.DOWN} C:{lv.SYMBOL.CLOSE} D:{lv.SYMBOL.OK}")
            self.hints_label.align(lv.ALIGN.BOTTOM_MID, 0, -2)
            self.hints_label.set_style_text_color(lv.color_hex(0x8E8E93), 0)
            self.hints_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            print(f"  ✅ 기본 버튼 힌트 생성 완료 (LVGL 심볼 사용)")
        except Exception as e:
            print(f"  ⚠️ 기본 버튼 힌트 생성 실패: {e}")
        
        print(f"  ✅ 기본 화면 생성 완료")
    
    def _create_modern_screen(self):
        """Modern 화면 생성"""
        print(f"📱 {self.screen_name} Modern 화면 생성 시작...")
        
        try:
            # 화면 객체 생성
            print(f"  📱 화면 객체 생성...")
            self.screen_obj = lv.obj()
            print(f"  📱 화면 객체 생성됨: {self.screen_obj}")
            
            # 화면 배경 설정
            self.screen_obj.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)  # 흰색 배경
            self.screen_obj.set_style_bg_opa(255, 0)
            print(f"  ✅ 화면 배경 설정 완료")
            
            # 화면 크기 설정
            self.screen_obj.set_size(160, 128)
            print(f"  📱 화면 크기: 160x128")
            
            # 메인 컨테이너 생성
            print(f"  📱 메인 컨테이너 생성 시도...")
            self._create_main_container()
            print(f"  📱 메인 컨테이너 생성 완료")
            
            # 제목 영역 생성
            print(f"  📱 제목 영역 생성 시도...")
            self._create_title_area()
            print(f"  📱 제목 영역 생성 완료")
            
            # 복용 시간 선택 영역 생성
            print(f"  📱 복용 시간 선택 영역 생성 시도...")
            self._create_meal_selection_area()
            print(f"  📱 복용 시간 선택 영역 생성 완료")
            
            # 버튼 힌트 영역 생성
            print(f"  📱 버튼 힌트 영역 생성 시도...")
            self._create_simple_button_hints()
            print(f"  📱 버튼 힌트 영역 생성 완료")
            
            print(f"  ✅ Modern 화면 생성 완료")
            
        except Exception as e:
            print(f"  ❌ Modern 화면 생성 중 오류 발생: {e}")
            import sys
            sys.print_exception(e)
    
    def _create_main_container(self):
        """메인 컨테이너 생성 - Modern 스타일"""
        # 메인 컨테이너 (전체 화면)
        self.main_container = lv.obj(self.screen_obj)
        print(f"    📱 메인 컨테이너 객체 생성됨: {self.main_container}")
        
        # 크기 설정
        self.main_container.set_size(160, 128)
        print(f"    📱 메인 컨테이너 크기 설정: 160x128")
        
        # 위치 설정
        self.main_container.align(lv.ALIGN.CENTER, 0, 0)
        print(f"    📱 메인 컨테이너 위치 설정: CENTER")
        
        # 스타일 설정
        self.main_container.set_style_bg_opa(0, 0)
        self.main_container.set_style_border_width(0, 0)
        self.main_container.set_style_pad_all(0, 0)
        print(f"    📱 메인 컨테이너 스타일 설정 완료")
        
        # 메인 컨테이너 크기 확인 (MicroPython LVGL 호환성)
        try:
            w, h = self.main_container.get_size()
            print(f"    📱 메인 컨테이너 크기: {w}x{h}")
            
            # 크기가 0인 경우 재설정
            if w == 0 or h == 0:
                print(f"    ⚠️ 메인 컨테이너 크기가 0입니다. 강제로 다시 설정합니다.")
                self.main_container.set_size(160, 128)
                print(f"    📱 재설정 완료")
        except AttributeError:
            print(f"    ⚠️ get_size() 메서드 지원 안됨, 크기 확인 건너뛰기")
        
        print(f"  📱 메인 컨테이너 생성 완료")
    
    def _create_title_area(self):
        """제목 영역 생성"""
        try:
            # 제목 컨테이너
            self.title_container = lv.obj(self.main_container)
            self.title_container.set_size(160, 25)
            self.title_container.align(lv.ALIGN.TOP_MID, 0, 4)
            self.title_container.set_style_bg_opa(0, 0)
            self.title_container.set_style_border_width(0, 0)
            self.title_container.set_style_pad_all(0, 0)
            
            # 제목 컨테이너 스크롤바 비활성화
            self.title_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.title_container.set_scroll_dir(lv.DIR.NONE)
            
            # 제목 텍스트 생성
            self.title_label = self.ui_style.create_label(
                self.title_container,
                "복용 시간 선택",
                'text_title',
                0x333333  # 다크 그레이
            )
            self.title_label.align(lv.ALIGN.CENTER, 0, 0)
            self.title_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            
            print(f"  ✅ 제목 영역 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 제목 영역 생성 중 오류: {e}")
            import sys
            sys.print_exception(e)
    
    def _create_meal_selection_area(self):
        """복용 시간 선택 영역 생성"""
        try:
            print(f"  📱 복용 시간 선택 컨테이너 생성 시작...")
            
            # 복용 시간 선택 컨테이너
            self.meal_container = lv.obj(self.main_container)
            print(f"  📱 복용 시간 선택 컨테이너 객체 생성됨")
            
            self.meal_container.set_size(140, 80)
            print(f"  📱 복용 시간 선택 컨테이너 크기 설정: 140x80")
            
            self.meal_container.align(lv.ALIGN.CENTER, 0, 5)
            print(f"  📱 복용 시간 선택 컨테이너 위치 설정: CENTER")
            
            self.meal_container.set_style_bg_opa(0, 0)
            self.meal_container.set_style_border_width(0, 0)
            self.meal_container.set_style_pad_all(0, 0)
            print(f"  📱 복용 시간 선택 컨테이너 스타일 설정 완료")
            
            # 스크롤바 비활성화
            self.meal_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.meal_container.set_scroll_dir(lv.DIR.NONE)
            print(f"  📱 복용 시간 선택 컨테이너 스크롤 설정 완료")
            
            # 복용 시간 옵션들
            meals = [
                ('breakfast', '아침'),
                ('lunch', '점심'),
                ('dinner', '저녁')
            ]
            
            # 각 복용 시간에 대한 체크박스와 라벨 생성
            print(f"  📱 {len(meals)}개 복용 시간 옵션 생성 시작...")
            
            for i, (meal_key, meal_name) in enumerate(meals):
                y_offset = i * 25  # 각 항목마다 25픽셀 간격
                print(f"  📱 {meal_name} 옵션 생성 중... (y_offset: {y_offset})")
                
                # 체크박스 생성
                checkbox = lv.checkbox(self.meal_container)
                print(f"  📱 {meal_name} 체크박스 객체 생성됨")
                
                checkbox.set_text("")
                checkbox.align(lv.ALIGN.TOP_MID, -18, y_offset)
                checkbox.set_style_bg_opa(0, 0)
                checkbox.set_style_border_width(0, 0)
                print(f"  📱 {meal_name} 체크박스 설정 완료")
                
                # 체크박스 상태 설정
                if self.selected_meals[meal_key]:
                    checkbox.add_state(lv.STATE.CHECKED)
                    print(f"  📱 {meal_name} 체크박스 체크 상태 설정")
                
                # 라벨 생성
                print(f"  📱 {meal_name} 라벨 생성 중...")
                label = self.ui_style.create_label(
                    self.meal_container,
                    meal_name,
                    'text_body',
                    0x333333
                )
                label.align(lv.ALIGN.TOP_MID, 13, y_offset + 2)
                print(f"  📱 {meal_name} 라벨 생성 완료")
                
                # 화살표 제거 - 문제 해결을 위해 완전 제거
                print(f"  📱 {meal_name} 화살표 제거됨")
                
                # 컴포넌트 저장
                self.meal_checkboxes[meal_key] = checkbox
                self.meal_labels[meal_key] = label
                print(f"  ✅ {meal_name} 옵션 생성 완료")
            
            print(f"  ✅ 복용 시간 선택 영역 생성 완료")
            
            # 초기 선택 표시 설정
            self._update_selection_display()
            
        except Exception as e:
            print(f"  ❌ 복용 시간 선택 영역 생성 중 오류: {e}")
            import sys
            sys.print_exception(e)
    
    def _create_simple_button_hints(self):
        """간단한 버튼 힌트 생성 - 메모리 절약"""
        try:
            # 화면에 직접 라벨 생성 (컨테이너 없이)
            self.hints_label = lv.label(self.screen_obj)
            # LVGL 심볼 사용 (기본 폰트에서 지원)
            self.hints_label.set_text(f"A:{lv.SYMBOL.UP} B:{lv.SYMBOL.DOWN} C:{lv.SYMBOL.OK} D:{lv.SYMBOL.NEXT}")
            self.hints_label.align(lv.ALIGN.BOTTOM_MID, 0, -2)  # Wi-Fi 스캔 화면과 동일한 위치
            self.hints_label.set_style_text_color(lv.color_hex(0x8E8E93), 0)
            self.hints_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            print(f"  ✅ 간단한 버튼 힌트 생성 완료 (LVGL 심볼 사용)")
            
        except Exception as e:
            print(f"  ❌ 간단한 버튼 힌트 생성 중 오류: {e}")
            import sys
            sys.print_exception(e)
    
    def show(self):
        """화면 표시"""
        print(f"📱 {self.screen_name} 화면 표시 시작...")
        
        try:
            if self.screen_obj is None:
                print(f"⚠️ 화면 객체가 없습니다. 화면을 생성합니다.")
                self.create_screen()
            
            if self.screen_obj:
                print(f"📱 화면 객체 존재 확인됨")
                
                # 화면 로드 전에 현재 화면 정보 출력
                current_screen = lv.screen_active()
                print(f"📱 현재 활성 화면: {current_screen}")
                
                # 화면 로드
                lv.screen_load(self.screen_obj)
                print(f"✅ {self.screen_name} 화면 로드 완료")
                
                # 로드 후 활성 화면 확인
                loaded_screen = lv.screen_active()
                print(f"📱 로드 후 활성 화면: {loaded_screen}")
            else:
                print(f"❌ {self.screen_name} 화면 로드 실패")
                
        except Exception as e:
            print(f"❌ {self.screen_name} 화면 표시 중 오류: {e}")
            import sys
            sys.print_exception(e)
    
    def hide(self):
        """화면 숨기기"""
        print(f"📱 {self.screen_name} 화면 숨기기")
        # 화면 숨기기 로직 (필요시 구현)
        pass
    
    def update(self):
        """화면 업데이트 (ScreenManager에서 호출)"""
        # 화면 업데이트 로직 (필요시 구현)
        pass
    
    def on_button_a(self):
        """버튼 A 처리 (위로 이동)"""
        print(f"🔘 버튼 A (SW1) 눌림 - 위로 이동")
        # 현재 선택된 항목을 위로 이동 (순환)
        self.current_selection = (self.current_selection - 1) % 3
        self._update_selection_display()
    
    def on_button_b(self):
        """버튼 B 처리 (아래로 이동)"""
        print(f"🔘 버튼 B (SW2) 눌림 - 아래로 이동")
        # 현재 선택된 항목을 아래로 이동 (순환)
        self.current_selection = (self.current_selection + 1) % 3
        self._update_selection_display()
    
    def on_button_c(self):
        """버튼 C 처리 (OK/체크박스 토글)"""
        print(f"🔘 버튼 C (SW3) 눌림 - OK/체크박스 토글")
        
        # 현재 선택된 항목의 체크박스 토글
        meal_keys = ['breakfast', 'lunch', 'dinner']
        current_meal = meal_keys[self.current_selection]
        
        if current_meal in self.meal_checkboxes:
            checkbox = self.meal_checkboxes[current_meal]
            if checkbox.has_state(lv.STATE.CHECKED):
                # 체크 상태 제거
                checkbox.remove_state(lv.STATE.CHECKED)
                self.selected_meals[current_meal] = False
                print(f"📱 {current_meal} 선택 해제")
            else:
                # 체크 상태 추가
                checkbox.add_state(lv.STATE.CHECKED)
                self.selected_meals[current_meal] = True
                print(f"📱 {current_meal} 선택")
    
    def on_button_d(self):
        """버튼 D 처리 (다음 화면으로 이동)"""
        print(f"🔘 버튼 D (SW4) 눌림 - 다음 화면으로 이동")
        
        # 선택된 복용 시간 개수 계산
        selected_count = sum(1 for selected in self.selected_meals.values() if selected)
        print(f"📱 선택된 복용 시간 개수: {selected_count}")
        
        # 선택된 항목이 있으면 다음 화면으로 이동
        if selected_count > 0:
            print("📱 선택된 복용 시간이 있습니다. 다음 화면으로 이동합니다.")
            if self.screen_manager:
                # 선택된 식사 시간 정보를 dose_time 화면으로 전달
                selected_meals_info = self._get_selected_meals_info()
                print(f"📱 전달할 식사 시간 정보: {selected_meals_info}")
                
                # dose_time 화면으로 이동 (선택된 복용 시간 개수와 식사 시간 정보 전달)
                self.screen_manager.show_screen('dose_time', 
                                               dose_count=selected_count,
                                               selected_meals=selected_meals_info)
        else:
            print("⚠️ 복용 시간을 선택해주세요")
    
    def _update_selection_display(self):
        """선택 표시 업데이트"""
        try:
            meal_keys = ['breakfast', 'lunch', 'dinner']
            meal_names = ['아침', '점심', '저녁']
            
            # 순서대로 라벨 색상 설정 (딕셔너리 순서 보장)
            for i, meal_key in enumerate(meal_keys):
                if meal_key in self.meal_labels:
                    label = self.meal_labels[meal_key]
                    if i == self.current_selection:
                        # 현재 선택된 항목은 강조 색상 (lv_color_hex 사용)
                        label.set_style_text_color(lv.color_hex(0x0066CC), 0)
                    else:
                        # 선택되지 않은 항목은 기본 색상
                        label.set_style_text_color(lv.color_hex(0x333333), 0)
            
            print(f"📱 현재 선택: {meal_names[self.current_selection]}")
                    
        except Exception as e:
            print(f"❌ 선택 표시 업데이트 중 오류: {e}")
            import sys
            sys.print_exception(e)
    
    def _get_selected_meals_info(self):
        """선택된 식사 시간 정보 반환 (아침, 점심, 저녁 순서)"""
        try:
            selected_meals_info = []
            meal_names = {'breakfast': '아침', 'lunch': '점심', 'dinner': '저녁'}
            
            # 아침, 점심, 저녁 순서로 정렬하여 선택된 것만 추가
            meal_order = ['breakfast', 'lunch', 'dinner']
            
            for meal_key in meal_order:
                if self.selected_meals.get(meal_key, False):
                    selected_meals_info.append({
                        'key': meal_key,
                        'name': meal_names[meal_key],
                        'default_hour': self._get_default_hour(meal_key),
                        'default_minute': 0
                    })
            
            print(f"📱 선택된 식사 시간 정보 생성: {len(selected_meals_info)}개 (아침, 점심, 저녁 순서)")
            for meal_info in selected_meals_info:
                print(f"  - {meal_info['name']}: 기본 시간 {meal_info['default_hour']:02d}:{meal_info['default_minute']:02d}")
            
            return selected_meals_info
            
        except Exception as e:
            print(f"❌ 선택된 식사 시간 정보 생성 중 오류: {e}")
            import sys
            sys.print_exception(e)
            return []
    
    def _get_default_hour(self, meal_key):
        """식사 시간별 기본 시간 반환"""
        default_hours = {
            'breakfast': 8,   # 아침 8시
            'lunch': 12,      # 점심 12시
            'dinner': 18      # 저녁 6시
        }
        return default_hours.get(meal_key, 8)
    
    def _save_meal_selections(self):
        """선택된 복용 시간들 저장"""
        try:
            # 체크박스 상태를 selected_meals에 반영
            for meal_key, checkbox in self.meal_checkboxes.items():
                self.selected_meals[meal_key] = checkbox.has_state(lv.STATE.CHECKED)
            
            print(f"📱 선택된 복용 시간들:")
            for meal_key, is_selected in self.selected_meals.items():
                if is_selected:
                    meal_name = {'breakfast': '아침', 'lunch': '점심', 'dinner': '저녁'}[meal_key]
                    print(f"  - {meal_name}")
            
            # TODO: 선택된 복용 시간들을 영구 저장소에 저장
            
        except Exception as e:
            print(f"❌ 복용 시간 저장 중 오류: {e}")
            import sys
            sys.print_exception(e)
    
    def get_title(self):
        """화면 제목"""
        return "복용 시간 선택"
    
    def get_button_hints(self):
        """버튼 힌트"""
        return f"A:{lv.SYMBOL.UP} B:{lv.SYMBOL.DOWN} C:{lv.SYMBOL.OK} D:{lv.SYMBOL.NEXT}"
    
    def get_voice_file(self):
        """안내 음성 파일"""
        return "wav_meal_time_prompt.wav"
    
    def get_effect_file(self):
        """효과음 파일"""
        return "wav_select.wav"
