"""
복용 시간 설정 화면
각 복용 시간을 설정하는 화면 (롤러 UI 스타일)
"""

import time
import lvgl as lv
from ui_style import UIStyle
from global_data import global_data

class DoseTimeScreen:
    """복용 시간 설정 화면 클래스 - 롤러 UI 스타일"""
    
    def __init__(self, screen_manager, dose_count=1, selected_meals=None):
        """복용 시간 설정 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = 'dose_time'
        self.screen_obj = None
        self.dose_count = dose_count
        self.selected_meals = selected_meals or []  # 선택된 식사 시간 정보
        
        # 전역 데이터에서 기존 정보 복원
        self.dose_times = global_data.get_dose_times()
        if not self.dose_times:
            self.dose_times = []  # 설정된 복용 시간들
        
        self.current_dose_index = 0  # 현재 설정 중인 복용 시간 인덱스
        self.current_hour = 8  # 기본값: 오전 8시
        self.current_minute = 0  # 기본값: 0분
        self.editing_hour = True  # True: 시간 편집, False: 분 편집
        
        # 롤러 객체들
        self.hour_roller = None
        self.minute_roller = None
        
        # UI 스타일은 필요할 때만 초기화 (메모리 절약)
        self.ui_style = None
        
        # 선택된 식사 시간에 따라 기본 시간 설정
        self._set_default_time_from_meals()
        
        # 간단한 화면 생성
        self._create_simple_screen()
        
        print(f"[OK] {self.screen_name} 화면 초기화 완료 (복용 횟수: {dose_count})")
        if self.selected_meals:
            print(f"[INFO] 선택된 식사 시간: {[meal['name'] for meal in self.selected_meals]}")
        print(f"[INFO] 복원된 복용 시간: {len(self.dose_times)}개")
        for dose_info in self.dose_times:
            if isinstance(dose_info, dict):
                print(f"  - {dose_info.get('meal_name', 'Unknown')}: {dose_info.get('time', 'Unknown')}")
    
    def _ensure_ui_style(self):
        """UI 스타일이 필요할 때만 초기화"""
        if self.ui_style is None:
            try:
                import gc
                gc.collect()
                self.ui_style = UIStyle()
                print("[OK] UI 스타일 지연 초기화 완료")
            except Exception as e:
                print(f"[WARN] UI 스타일 지연 초기화 실패: {e}")
                self.ui_style = None
    
    def _set_default_time_from_meals(self):
        """선택된 식사 시간에 따라 기본 시간 설정"""
        try:
            if self.selected_meals and len(self.selected_meals) > 0:
                # 첫 번째 선택된 식사 시간의 기본 시간 사용
                first_meal = self.selected_meals[0]
                self.current_hour = first_meal.get('default_hour', 8)
                self.current_minute = first_meal.get('default_minute', 0)
                print(f"[INFO] 첫 번째 식사 시간 기본값 설정: {self.current_hour:02d}:{self.current_minute:02d} ({first_meal['name']})")
            else:
                # 기본값 유지
                print(f"[INFO] 선택된 식사 시간이 없어 기본값 사용: {self.current_hour:02d}:{self.current_minute:02d}")
        except Exception as e:
            print(f"[ERROR] 기본 시간 설정 실패: {e}")
    
    def _update_title_text(self):
        """제목 텍스트 업데이트"""
        try:
            if self.selected_meals and self.current_dose_index < len(self.selected_meals):
                # 선택된 식사 시간이 있으면 해당 식사 시간 표시
                current_meal = self.selected_meals[self.current_dose_index]
                title_text = f"{current_meal['name']} - 시간 설정"
            else:
                # 기본 제목
                title_text = f"복용 시간 {self.current_dose_index + 1}"
            
            if hasattr(self, 'title_label') and self.title_label:
                self.title_label.set_text(title_text)
                print(f"[INFO] 제목 업데이트: {title_text}")
        except Exception as e:
            print(f"[ERROR] 제목 텍스트 업데이트 실패: {e}")
    
    def _create_simple_screen(self):
        """간단한 화면 생성"""
        print(f"  [INFO] {self.screen_name} 간단한 화면 생성 시작...")
        
        try:
            # 메모리 정리
            import gc
            gc.collect()
            
            # 화면 생성
            self.screen_obj = lv.obj()
            self.screen_obj.set_size(160, 128)
            self.screen_obj.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
            
            # 제목
            self.title_label = lv.label(self.screen_obj)
            self._update_title_text()
            self.title_label.align(lv.ALIGN.TOP_MID, 0, 10)
            self.title_label.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
            
            # 한국어 폰트 적용
            korean_font = getattr(lv, "font_notosans_kr_regular", None)
            if korean_font:
                self.title_label.set_style_text_font(korean_font, 0)
            
            # 시간 롤러 생성
            print("  [INFO] 시간 롤러 생성 중...")
            self.hour_roller = lv.roller(self.screen_obj)
            self.hour_roller.set_size(50, 60)
            self.hour_roller.align(lv.ALIGN.CENTER, -30, 0)
            
            # 시간 옵션 설정
            hours = [f"{i:02d}" for i in range(24)]
            self.hour_roller.set_options("\n".join(hours), lv.roller.MODE.INFINITE)
            self.hour_roller.set_selected(self.current_hour, True)
            
            # 시간 롤러 스타일
            self.hour_roller.set_style_bg_color(lv.color_hex(0xF2F2F7), 0)
            self.hour_roller.set_style_border_width(0, 0)
            self.hour_roller.set_style_text_color(lv.color_hex(0x000000), 0)
            
            if korean_font:
                self.hour_roller.set_style_text_font(korean_font, 0)
            
            # 롤러 선택된 항목 스타일 - 로고 색상(민트)
            try:
                self.hour_roller.set_style_bg_color(lv.color_hex(0xd2b13f), lv.PART.SELECTED)
                self.hour_roller.set_style_bg_opa(255, lv.PART.SELECTED)
                self.hour_roller.set_style_text_color(lv.color_hex(0xFFFFFF), lv.PART.SELECTED)
                self.hour_roller.set_style_radius(6, lv.PART.SELECTED)
            except AttributeError:
                pass
            
            print("  [OK] 시간 롤러 생성 완료")
            
            # 메모리 정리
            import gc
            gc.collect()
            
            # 콜론 표시
            self.colon_label = lv.label(self.screen_obj)
            self.colon_label.set_text(":")
            self.colon_label.align(lv.ALIGN.CENTER, 0, 0)
            self.colon_label.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
            
            if korean_font:
                self.colon_label.set_style_text_font(korean_font, 0)
            
            # 분 롤러 생성
            print("  [INFO] 분 롤러 생성 중...")
            self.minute_roller = lv.roller(self.screen_obj)
            self.minute_roller.set_size(50, 60)
            self.minute_roller.align(lv.ALIGN.CENTER, 30, 0)
            
            # 분 옵션 설정
            minutes = [f"{i:02d}" for i in range(0, 60, 5)]
            self.minute_roller.set_options("\n".join(minutes), lv.roller.MODE.INFINITE)
            self.minute_roller.set_selected(self.current_minute // 5, True)
            
            # 분 롤러 스타일
            self.minute_roller.set_style_bg_color(lv.color_hex(0xF2F2F7), 0)
            self.minute_roller.set_style_border_width(0, 0)
            self.minute_roller.set_style_text_color(lv.color_hex(0x000000), 0)
            
            if korean_font:
                self.minute_roller.set_style_text_font(korean_font, 0)
            
            # 롤러 선택된 항목 스타일 - 로고 색상(민트)
            try:
                self.minute_roller.set_style_bg_color(lv.color_hex(0xd2b13f), lv.PART.SELECTED)
                self.minute_roller.set_style_bg_opa(255, lv.PART.SELECTED)
                self.minute_roller.set_style_text_color(lv.color_hex(0xFFFFFF), lv.PART.SELECTED)
                self.minute_roller.set_style_radius(6, lv.PART.SELECTED)
            except AttributeError:
                pass
            
            print("  [OK] 분 롤러 생성 완료")
            
            # 메모리 정리
            import gc
            gc.collect()
            
            # 버튼 힌트 (복용 횟수 화면과 동일한 위치 및 색상)
            self.hints_label = lv.label(self.screen_obj)
            self.hints_label.set_text(f"A:O B:{lv.SYMBOL.UP} C:{lv.SYMBOL.DOWN} D:{lv.SYMBOL.CLOSE}")
            self.hints_label.align(lv.ALIGN.BOTTOM_MID, 0, -2)  # -5 → -2로 변경
            self.hints_label.set_style_text_color(lv.color_hex(0x8E8E93), 0)  # 0x007AFF → 0x8E8E93 (모던 라이트 그레이)
            self.hints_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            
            print(f"  [OK] 간단한 화면 생성 완료")
            
            # 초기 롤러 가시성과 제목 설정
            self._update_roller_visibility()
            self._update_title()
            
        except Exception as e:
            print(f"  [ERROR] 화면 생성 중 오류 발생: {e}")
            import sys
            sys.print_exception(e)
    
    def on_button_a(self):
        """A 버튼: 선택/확인 - 시간/분 모드 전환 또는 다음 단계"""
        try:
            if self.editing_hour:
                # 시간 설정 완료, 분 설정으로 이동
                self.editing_hour = False
                self._update_roller_visibility()
                self._update_title()
                self._update_roller_options()
                print(f"  [INFO] 시간 {self.current_hour:02d}시 설정 완료, 분 설정으로 이동")
            else:
                # 분 설정 완료, 시간 저장하고 다음 단계
                self._save_current_time()
                self._next_time_setup()
        except Exception as e:
            print(f"  [ERROR] A 버튼 처리 실패: {e}")
    
    def on_button_b(self):
        """B 버튼: 시간/분 증가"""
        try:
            if self.editing_hour and hasattr(self, 'hour_roller') and self.hour_roller:
                current_selected = self.hour_roller.get_selected()
                self.hour_roller.set_selected(current_selected + 1, True)
                self._update_time_from_rollers()
                print(f"  [INFO] 시간 증가: {self.current_hour:02d}:{self.current_minute:02d}")
            elif not self.editing_hour and hasattr(self, 'minute_roller') and self.minute_roller:
                current_selected = self.minute_roller.get_selected()
                self.minute_roller.set_selected(current_selected + 1, True)
                self._update_time_from_rollers()
                print(f"  [INFO] 분 증가: {self.current_hour:02d}:{self.current_minute:02d}")
        except Exception as e:
            print(f"  [ERROR] B 버튼 처리 실패: {e}")
    
    def on_button_c(self):
        """C 버튼: 시간/분 감소"""
        try:
            if self.editing_hour and hasattr(self, 'hour_roller') and self.hour_roller:
                current_selected = self.hour_roller.get_selected()
                self.hour_roller.set_selected(current_selected - 1, True)
                self._update_time_from_rollers()
                print(f"  [INFO] 시간 감소: {self.current_hour:02d}:{self.current_minute:02d}")
            elif not self.editing_hour and hasattr(self, 'minute_roller') and self.minute_roller:
                current_selected = self.minute_roller.get_selected()
                self.minute_roller.set_selected(current_selected - 1, True)
                self._update_time_from_rollers()
                print(f"  [INFO] 분 감소: {self.current_hour:02d}:{self.current_minute:02d}")
            else:
                print(f"  [WARN] 롤러 객체가 없습니다. editing_hour: {self.editing_hour}")
        except Exception as e:
            print(f"  [ERROR] C 버튼 처리 실패: {e}")
    
    def _update_roller_visibility(self):
        """시간/분 편집 모드에 따라 롤러 스타일 업데이트"""
        try:
            if self.editing_hour:
                # 시간 편집 모드: 시간 롤러 강조
                if self.hour_roller:
                    self.hour_roller.set_style_border_width(2, 0)
                    self.hour_roller.set_style_border_color(lv.color_hex(0xd2b13f), 0)
                if self.minute_roller:
                    self.minute_roller.set_style_border_width(0, 0)
                print(f"  [INFO] 시간 편집 모드로 전환")
            else:
                # 분 편집 모드: 분 롤러 강조
                if self.hour_roller:
                    self.hour_roller.set_style_border_width(0, 0)
                if self.minute_roller:
                    self.minute_roller.set_style_border_width(2, 0)
                    self.minute_roller.set_style_border_color(lv.color_hex(0xd2b13f), 0)
                print(f"  [INFO] 분 편집 모드로 전환")
        except Exception as e:
            print(f"  [ERROR] 롤러 스타일 업데이트 실패: {e}")
    
    def _update_title(self):
        """현재 편집 모드에 따라 제목 업데이트"""
        try:
            if hasattr(self, 'title_label'):
                print(f"  [INFO] 제목 업데이트 시작 - current_dose_index: {self.current_dose_index}, editing_hour: {self.editing_hour}")
                print(f"  [INFO] selected_meals 길이: {len(self.selected_meals) if self.selected_meals else 0}")
                
                if self.selected_meals and self.current_dose_index < len(self.selected_meals):
                    meal_name = self.selected_meals[self.current_dose_index]['name']
                    if self.editing_hour:
                        new_title = f"{meal_name} - 시간 설정"
                    else:
                        new_title = f"{meal_name} - 분 설정"
                    
                    self.title_label.set_text(new_title)
                    print(f"  [INFO] 제목 업데이트 완료: {new_title}")
                else:
                    print(f"  [ERROR] 제목 업데이트 실패: 인덱스 범위 초과")
        except Exception as e:
            print(f"  [ERROR] 제목 업데이트 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _setup_current_dose_time(self):
        """현재 복용 시간 설정"""
        try:
            # 전역 데이터에서 최신 정보 다시 가져오기
            latest_dose_times = global_data.get_dose_times()
            if latest_dose_times:
                self.dose_times = latest_dose_times
                print(f"  [INFO] 전역 데이터에서 최신 dose_times 불러옴: {len(self.dose_times)}개")
            
            # 이미 저장된 시간 정보가 있는지 확인
            saved_time = None
            if self.selected_meals and self.current_dose_index < len(self.selected_meals):
                current_meal = self.selected_meals[self.current_dose_index]
                meal_key = current_meal['key']
                
                print(f"  [SEARCH] 저장된 시간 검색 중... (현재 인덱스: {self.current_dose_index}, 식사: {current_meal['name']}, 키: {meal_key})")
                print(f"  [SEARCH] 저장된 dose_times 개수: {len(self.dose_times)}")
                
                # dose_times에서 해당 식사 시간의 저장된 정보 찾기
                for i, dose_time in enumerate(self.dose_times):
                    print(f"  [SEARCH] dose_times[{i}]: {dose_time}")
                    if isinstance(dose_time, dict) and dose_time.get('meal_key') == meal_key:
                        saved_time = dose_time
                        print(f"  [OK] 저장된 시간 찾음: {saved_time}")
                        break
                
                if not saved_time:
                    print(f"  [WARN] 저장된 시간을 찾지 못함 (meal_key: {meal_key})")
            
            if saved_time:
                # 저장된 시간 정보 사용
                self.current_hour = saved_time['hour']
                self.current_minute = saved_time['minute']
                print(f"  [INFO] 저장된 시간 정보 사용: {self.current_hour:02d}:{self.current_minute:02d} ({saved_time['meal_name']})")
            else:
                # 저장된 정보가 없으면 기본값 사용
                if self.selected_meals and self.current_dose_index < len(self.selected_meals):
                    current_meal = self.selected_meals[self.current_dose_index]
                    self.current_hour = current_meal.get('default_hour', 8)
                    self.current_minute = current_meal.get('default_minute', 0)
                    print(f"  [INFO] 기본값 사용: {self.current_hour:02d}:{self.current_minute:02d} ({current_meal['name']})")
                else:
                    # 기본값으로 리셋
                    self.current_hour = 8
                    self.current_minute = 0
            
            # 시간 편집 모드로 리셋
            self.editing_hour = True
            
            # 롤러 값 업데이트
            if hasattr(self, 'hour_roller') and hasattr(self, 'minute_roller'):
                self.hour_roller.set_selected(self.current_hour, True)
                self.minute_roller.set_selected(self.current_minute // 5, True)  # 5분 간격으로 나누기
                print(f"  [INFO] 롤러 값 업데이트: 시간={self.current_hour}, 분={self.current_minute}")
            
            # 제목과 롤러 포커스 업데이트
            self._update_title()
            self._update_roller_visibility()
            
            print(f"  [OK] 현재 복용 시간 설정 완료")
                    
        except Exception as e:
            print(f"  [ERROR] 현재 복용 시간 설정 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def on_button_d(self):
        """D 버튼: 취소 및 이전화면으로"""
        try:
            if self.editing_hour:
                # 시간 설정 중이면 이전 복용 시간으로 되돌아가기
                if self.current_dose_index > 0:
                    # 이전 복용 시간으로 되돌아가기
                    self.current_dose_index -= 1
                    self._setup_current_dose_time()
                    print(f"  [INFO] 이전 복용 시간으로 되돌아가기: {self.current_dose_index + 1}번째")
                else:
                    # 첫 번째 복용 시간이면 복용 시간 선택 화면으로
                    print(f"  [INFO] 취소 - 복용 시간 선택 화면으로 이동")
                    if 'meal_time' in self.screen_manager.screens:
                        self.screen_manager.show_screen('meal_time')
                        print(f"  [OK] 복용 시간 선택 화면으로 이동 완료")
                    else:
                        print(f"  [ERROR] 복용 시간 선택 화면이 등록되지 않음")
            else:
                # 분 설정 중이면 시간 설정으로 되돌아가기
                self.editing_hour = True
                self._update_roller_visibility()
                self._update_title()
                self._update_roller_options()
                print(f"  [INFO] 분 설정에서 시간 설정으로 되돌아가기")
        except Exception as e:
            print(f"  [ERROR] D 버튼 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _update_time_from_rollers(self):
        """롤러에서 선택된 값을 시간으로 업데이트"""
        try:
            if hasattr(self, 'hour_roller') and hasattr(self, 'minute_roller'):
                self.current_hour = self.hour_roller.get_selected()
                self.current_minute = self.minute_roller.get_selected() * 5  # 5분 간격
        except Exception as e:
            print(f"  [ERROR] 시간 업데이트 실패: {e}")
    
    def _update_roller_options(self):
        """롤러 옵션 업데이트"""
        try:
            # 제목 업데이트
            if hasattr(self, 'title_label'):
                if self.selected_meals and self.current_dose_index < len(self.selected_meals):
                    current_meal = self.selected_meals[self.current_dose_index]
                    if self.editing_hour:
                        self.title_label.set_text(f"{current_meal['name']} - 시간 설정")
                    else:
                        self.title_label.set_text(f"{current_meal['name']} - 분 설정")
                else:
                    if self.editing_hour:
                        self.title_label.set_text(f"복용 시간 {self.current_dose_index + 1} - 시간 설정")
                    else:
                        self.title_label.set_text(f"복용 시간 {self.current_dose_index + 1} - 분 설정")
            
        except Exception as e:
            print(f"  [ERROR] 롤러 옵션 업데이트 실패: {e}")
    
    def _save_current_time(self):
        """현재 설정된 시간 저장"""
        try:
            self._update_time_from_rollers()
            time_str = f"{self.current_hour:02d}:{self.current_minute:02d}"
            
            # 식사 시간 정보와 함께 저장
            if self.selected_meals and self.current_dose_index < len(self.selected_meals):
                current_meal = self.selected_meals[self.current_dose_index]
                dose_info = {
                    'time': time_str,
                    'meal_key': current_meal['key'],
                    'meal_name': current_meal['name'],
                    'hour': self.current_hour,
                    'minute': self.current_minute
                }
                
                # 기존에 같은 meal_key가 있는지 확인하고 업데이트
                existing_index = None
                for i, existing_dose in enumerate(self.dose_times):
                    if isinstance(existing_dose, dict) and existing_dose.get('meal_key') == current_meal['key']:
                        existing_index = i
                        break
                
                if existing_index is not None:
                    # 기존 항목 업데이트
                    self.dose_times[existing_index] = dose_info
                    print(f"  [INFO] {current_meal['name']} 시간 업데이트: {time_str} (인덱스: {existing_index})")
                else:
                    # 새 항목 추가
                    self.dose_times.append(dose_info)
                    print(f"  [INFO] {current_meal['name']} 시간 저장: {time_str} (새 항목)")
                
                print(f"  [INFO] 현재 dose_times 상태: {self.dose_times}")
                
                # 전역 데이터에도 저장
                global_data.save_dose_times(self.dose_times)
                print(f"  [INFO] 전역 데이터에 복용 시간 저장: {len(self.dose_times)}개")
                for dose_info in self.dose_times:
                    if isinstance(dose_info, dict):
                        print(f"    - {dose_info['meal_name']}: {dose_info['time']}")
            else:
                # 기본 저장 방식
                self.dose_times.append(time_str)
                print(f"  [INFO] 복용 시간 {self.current_dose_index + 1} 저장: {time_str}")
                
                # 전역 데이터에도 저장
                global_data.save_dose_times(self.dose_times)
        except Exception as e:
            print(f"  [ERROR] 시간 저장 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _next_time_setup(self):
        """다음 복용 시간 설정 또는 완료"""
        try:
            self.current_dose_index += 1
            
            if self.current_dose_index < self.dose_count:
                # 다음 복용 시간 설정
                self.editing_hour = True  # 다시 시간 편집 모드로
                
                # 저장된 시간이 있는지 먼저 확인
                saved_time = None
                if self.selected_meals and self.current_dose_index < len(self.selected_meals):
                    next_meal = self.selected_meals[self.current_dose_index]
                    meal_key = next_meal['key']
                    
                    # dose_times에서 해당 식사 시간의 저장된 정보 찾기
                    for dose_time in self.dose_times:
                        if isinstance(dose_time, dict) and dose_time.get('meal_key') == meal_key:
                            saved_time = dose_time
                            break
                
                if saved_time:
                    # 저장된 시간 정보 사용
                    self.current_hour = saved_time['hour']
                    self.current_minute = saved_time['minute']
                    print(f"  [INFO] 다음 식사 시간 저장된 값 사용: {self.current_hour:02d}:{self.current_minute:02d} ({saved_time['meal_name']})")
                else:
                    # 저장된 정보가 없으면 기본값 사용
                    if self.selected_meals and self.current_dose_index < len(self.selected_meals):
                        next_meal = self.selected_meals[self.current_dose_index]
                        self.current_hour = next_meal.get('default_hour', 8)
                        self.current_minute = next_meal.get('default_minute', 0)
                        print(f"  [INFO] 다음 식사 시간 기본값 설정: {self.current_hour:02d}:{self.current_minute:02d} ({next_meal['name']})")
                    else:
                        # 기본값으로 리셋
                        self.current_hour = 8
                        self.current_minute = 0
                
                # 롤러를 설정된 값으로 업데이트
                if hasattr(self, 'hour_roller') and hasattr(self, 'minute_roller'):
                    self.hour_roller.set_selected(self.current_hour, True)
                    self.minute_roller.set_selected(self.current_minute // 5, True)
                    print(f"  [INFO] 롤러 값 업데이트: 시간={self.current_hour}, 분={self.current_minute}")
                
                # 제목과 롤러 가시성 업데이트 (시간 설정 모드로)
                self._update_title()
                self._update_roller_visibility()
                
                print(f"  [INFO] 복용 시간 {self.current_dose_index + 1} 설정 시작")
            else:
                # 모든 복용 시간 설정 완료
                print(f"  [INFO] 모든 복용 시간 설정 완료!")
                print(f"  [INFO] 설정된 시간들: {self.dose_times}")
                
                # 1개 복용만 선택한 경우에만 디스크 선택 화면으로 이동
                if self.dose_count == 1:
                    print(f"  [INFO] 1개 복용 선택 - 디스크 선택 화면으로 이동")
                    self._go_to_disk_selection_screen()
                else:
                    print(f"  [INFO] {self.dose_count}개 복용 선택 - 직접 알약 충전 화면으로 이동")
                    self._go_to_pill_loading_screen()
            
        except Exception as e:
            print(f"  [ERROR] 다음 단계 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _go_to_disk_selection_screen(self):
        """디스크 선택 화면으로 이동"""
        try:
            print(f"  [INFO] 디스크 선택 화면으로 이동 시작...")
            
            # 현재 설정된 복용 시간 정보 가져오기
            if not self.dose_times:
                print(f"  [ERROR] 복용 시간 정보가 없습니다")
                return
            
            # 첫 번째 복용 시간 정보 사용 (1회 복용의 경우)
            dose_info = self.dose_times[0] if isinstance(self.dose_times[0], dict) else {
                'time': self.dose_times[0],
                'meal_name': '복용',
                'hour': 8,
                'minute': 0
            }
            
            print(f"  [INFO] 복용 정보: {dose_info}")
            
            # DiskSelectionScreen 생성
            from screens.disk_selection_screen import DiskSelectionScreen
            disk_selection_screen = DiskSelectionScreen(self.screen_manager, dose_info)
            
            # 화면 등록 및 이동
            self.screen_manager.register_screen('disk_selection', disk_selection_screen)
            self.screen_manager.show_screen('disk_selection')
            
            print(f"  [OK] 디스크 선택 화면으로 이동 완료")
        except Exception as e:
            print(f"  [ERROR] 디스크 선택 화면 이동 실패: {e}")
            import sys
            sys.print_exception(e)
                        
    def _go_to_pill_loading_screen(self):
        """알약 충전 화면으로 직접 이동 (2개 이상 복용 선택 시)"""
        try:
            print(f"  [INFO] 알약 충전 화면으로 직접 이동 시작...")
            
            # 기존 방식으로 알약 충전 화면으로 이동
            if 'pill_loading' in self.screen_manager.screens:
                # 기존 화면에 selected_meals 정보 전달
                pill_loading_screen = self.screen_manager.screens['pill_loading']
                if hasattr(pill_loading_screen, 'set_selected_meals'):
                    pill_loading_screen.set_selected_meals(self.selected_meals)
                    print(f"  [INFO] 기존 pill_loading 화면에 selected_meals 전달: {len(self.selected_meals)}개")
                self.screen_manager.show_screen('pill_loading')
                print(f"  [OK] 알약 충전 화면으로 이동 완료")
            else:
                # PillLoadingScreen이 없으면 동적으로 생성
                print("[INFO] pill_loading 화면이 등록되지 않음. 동적 생성 중...")
                from screens.pill_loading_screen import PillLoadingScreen
                pill_loading_screen = PillLoadingScreen(self.screen_manager)
                # selected_meals 정보 전달
                if hasattr(pill_loading_screen, 'set_selected_meals'):
                    pill_loading_screen.set_selected_meals(self.selected_meals)
                    print(f"  [INFO] 새 pill_loading 화면에 selected_meals 전달: {len(self.selected_meals)}개")
                self.screen_manager.register_screen('pill_loading', pill_loading_screen)
                self.screen_manager.show_screen('pill_loading')
                print(f"  [OK] 알약 충전 화면 생성 및 이동 완료")
            
        except Exception as e:
            print(f"  [ERROR] 알약 충전 화면 이동 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def update_meal_selections(self, dose_count, selected_meals):
        """식사 시간 선택 정보 업데이트"""
        try:
            print(f"[INFO] dose_time 화면 상태 업데이트 시작")
            print(f"  - 이전 복용 횟수: {self.dose_count} → 새로운 복용 횟수: {dose_count}")
            print(f"  - 이전 선택된 식사: {[meal.get('name', 'Unknown') for meal in self.selected_meals] if self.selected_meals else 'None'}")
            print(f"  - 새로운 선택된 식사: {[meal.get('name', 'Unknown') for meal in selected_meals] if selected_meals else 'None'}")
            
            # 상태 초기화
            self.dose_count = dose_count
            self.selected_meals = selected_meals or []
            self.dose_times = []
            self.current_dose_index = 0
            self.editing_hour = True
            
            # 새로운 식사 시간에 따라 기본 시간 설정
            self._set_default_time_from_meals()
            
            # 제목 업데이트
            self._update_title_text()
            
            # 롤러 값 업데이트
            if hasattr(self, 'hour_roller') and hasattr(self, 'minute_roller'):
                self.hour_roller.set_selected(self.current_hour, True)
                self.minute_roller.set_selected(self.current_minute // 5, True)
                print(f"  [INFO] 롤러 값 업데이트: {self.current_hour:02d}:{self.current_minute:02d}")
            
            print(f"[OK] dose_time 화면 상태 업데이트 완료")
            
        except Exception as e:
            print(f"[ERROR] dose_time 화면 상태 업데이트 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def get_dose_times(self):
        """설정된 복용 시간들 반환"""
        try:
            # 전역 데이터에서 최신 정보 가져오기
            latest_dose_times = global_data.get_dose_times()
            if latest_dose_times:
                self.dose_times = latest_dose_times
            
            print(f"[INFO] 저장된 복용 시간 정보 반환: {len(self.dose_times)}개")
            for i, dose_info in enumerate(self.dose_times):
                if isinstance(dose_info, dict):
                    print(f"  {i+1}. {dose_info['meal_name']}: {dose_info['time']}")
                else:
                    print(f"  {i+1}. {dose_info}")
            return self.dose_times
        except Exception as e:
            print(f"  [ERROR] 복용 시간 반환 실패: {e}")
            return []
    
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
    
    def _cleanup_current_screen_resources(self):
        """현재 화면의 리소스 정리"""
        try:
            print("  🧹 현재 화면 리소스 정리 시작...")
            
            # UI 스타일 정리
            if hasattr(self, 'ui_style') and self.ui_style:
                try:
                    self.ui_style.cleanup()
                    self.ui_style = None
                    print("  [OK] UI 스타일 정리 완료")
                except:
                    pass
            
            # 롤러 객체들 정리
            if hasattr(self, 'hour_roller'):
                self.hour_roller = None
            if hasattr(self, 'minute_roller'):
                self.minute_roller = None
            if hasattr(self, 'colon_label'):
                self.colon_label = None
            if hasattr(self, 'hints_label'):
                self.hints_label = None
            if hasattr(self, 'title_label'):
                self.title_label = None
            
            print("  [OK] 현재 화면 리소스 정리 완료")
            
        except Exception as e:
            print(f"  [WARN] 현재 화면 리소스 정리 실패: {e}")
    
    def _aggressive_memory_cleanup(self):
        """적극적인 메모리 정리"""
        try:
            print("  🧹 적극적인 메모리 정리 시작...")
            import gc
            import micropython
            
            # 10회 가비지 컬렉션
            for i in range(10):
                gc.collect()
                time.sleep(0.01)
                if i % 3 == 0:
                    print(f"    🧹 가비지 컬렉션 {i+1}/10")
            
            # 메모리 상태 확인
            try:
                print("  [STATS] 적극적 정리 후 메모리 상태:")
                micropython.mem_info()
            except:
                pass
            
            print("  [OK] 적극적인 메모리 정리 완료")
            
        except Exception as e:
            print(f"  [WARN] 적극적인 메모리 정리 실패: {e}")
    
    def _final_memory_cleanup(self):
        """최종 메모리 정리 (최후의 수단)"""
        try:
            print("  [ALERT] 최종 메모리 정리 시작...")
            import gc
            import micropython
            
            # 30회 가비지 컬렉션 (더 적극적으로)
            for i in range(30):
                gc.collect()
                time.sleep(0.003)  # 더 짧은 간격
                if i % 5 == 0:
                    print(f"    [ALERT] 최종 가비지 컬렉션 {i+1}/30")
            
            # 메모리 상태 확인
            try:
                print("  [STATS] 최종 정리 후 메모리 상태:")
                micropython.mem_info()
            except:
                pass
            
            # 추가 정리: 메모리 모니터링 시스템 활용
            from memory_monitor import cleanup_memory
            cleanup_memory("최종 메모리 정리")
            
            print("  [OK] 최종 메모리 정리 완료")
            
        except Exception as e:
            print(f"  [WARN] 최종 메모리 정리 실패: {e}")