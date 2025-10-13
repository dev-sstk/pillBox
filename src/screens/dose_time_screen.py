"""
복용 시간 설정 화면
각 복용 시간을 설정하는 화면 (롤러 UI 스타일)
"""

import time
import lvgl as lv
from ui_style import UIStyle

class DoseTimeScreen:
    """복용 시간 설정 화면 클래스 - 롤러 UI 스타일"""
    
    def __init__(self, screen_manager, dose_count=1):
        """복용 시간 설정 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = 'dose_time'
        self.screen_obj = None
        self.dose_count = dose_count
        self.dose_times = []  # 설정된 복용 시간들
        self.current_dose_index = 0  # 현재 설정 중인 복용 시간 인덱스
        self.current_hour = 8  # 기본값: 오전 8시
        self.current_minute = 0  # 기본값: 0분
        self.editing_hour = True  # True: 시간 편집, False: 분 편집
        
        # 롤러 객체들
        self.hour_roller = None
        self.minute_roller = None
        
        # UI 스타일 시스템 초기화
        self.ui_style = UIStyle()
        
        # 간단한 화면 생성
        self._create_simple_screen()
        
        print(f"✅ {self.screen_name} 화면 초기화 완료 (복용 횟수: {dose_count})")
    
    def _create_simple_screen(self):
        """간단한 화면 생성"""
        print(f"  📱 {self.screen_name} 간단한 화면 생성 시작...")
        
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
            self.title_label.set_text(f"복용 시간 {self.current_dose_index + 1}")
            self.title_label.align(lv.ALIGN.TOP_MID, 0, 10)
            self.title_label.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
            
            # 한국어 폰트 적용
            korean_font = getattr(lv, "font_notosans_kr_regular", None)
            if korean_font:
                self.title_label.set_style_text_font(korean_font, 0)
            
            # 시간 롤러 생성
            print("  📱 시간 롤러 생성 중...")
            self.hour_roller = lv.roller(self.screen_obj)
            self.hour_roller.set_size(50, 60)
            self.hour_roller.align(lv.ALIGN.CENTER, -30, 0)
            
            # 시간 옵션 설정
            hours = [f"{i:02d}" for i in range(24)]
            self.hour_roller.set_options("\n".join(hours), lv.roller.MODE.INFINITE)
            self.hour_roller.set_selected(8, True)
            
            # 시간 롤러 스타일
            self.hour_roller.set_style_bg_color(lv.color_hex(0xF2F2F7), 0)
            self.hour_roller.set_style_border_width(0, 0)
            self.hour_roller.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
            
            if korean_font:
                self.hour_roller.set_style_text_font(korean_font, 0)
            
            # 롤러 선택된 항목 스타일 - 로고 색상(민트)
            try:
                self.hour_roller.set_style_bg_color(lv.color_hex(0x00C9A7), lv.PART.SELECTED)
                self.hour_roller.set_style_bg_opa(255, lv.PART.SELECTED)
                self.hour_roller.set_style_text_color(lv.color_hex(0xFFFFFF), lv.PART.SELECTED)
                self.hour_roller.set_style_radius(6, lv.PART.SELECTED)
            except AttributeError:
                pass
            
            print("  ✅ 시간 롤러 생성 완료")
            
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
            print("  📱 분 롤러 생성 중...")
            self.minute_roller = lv.roller(self.screen_obj)
            self.minute_roller.set_size(50, 60)
            self.minute_roller.align(lv.ALIGN.CENTER, 30, 0)
            
            # 분 옵션 설정
            minutes = [f"{i:02d}" for i in range(0, 60, 5)]
            self.minute_roller.set_options("\n".join(minutes), lv.roller.MODE.INFINITE)
            self.minute_roller.set_selected(0, True)
            
            # 분 롤러 스타일
            self.minute_roller.set_style_bg_color(lv.color_hex(0xF2F2F7), 0)
            self.minute_roller.set_style_border_width(0, 0)
            self.minute_roller.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
            
            if korean_font:
                self.minute_roller.set_style_text_font(korean_font, 0)
            
            # 롤러 선택된 항목 스타일 - 로고 색상(민트)
            try:
                self.minute_roller.set_style_bg_color(lv.color_hex(0x00C9A7), lv.PART.SELECTED)
                self.minute_roller.set_style_bg_opa(255, lv.PART.SELECTED)
                self.minute_roller.set_style_text_color(lv.color_hex(0xFFFFFF), lv.PART.SELECTED)
                self.minute_roller.set_style_radius(6, lv.PART.SELECTED)
            except AttributeError:
                pass
            
            print("  ✅ 분 롤러 생성 완료")
            
            # 메모리 정리
            import gc
            gc.collect()
            
            # 버튼 힌트 (복용 횟수 화면과 동일한 위치 및 색상)
            self.hints_label = lv.label(self.screen_obj)
            self.hints_label.set_text(f"A:{lv.SYMBOL.UP} B:{lv.SYMBOL.DOWN} C:{lv.SYMBOL.PREV} D:{lv.SYMBOL.OK}")
            self.hints_label.align(lv.ALIGN.BOTTOM_MID, 0, -2)  # -5 → -2로 변경
            self.hints_label.set_style_text_color(lv.color_hex(0x8E8E93), 0)  # 0x007AFF → 0x8E8E93 (모던 라이트 그레이)
            self.hints_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            
            print(f"  ✅ 간단한 화면 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 화면 생성 중 오류 발생: {e}")
            import sys
            sys.print_exception(e)
    
    def on_button_a(self):
        """A 버튼: 위로 이동"""
        try:
            if self.editing_hour and hasattr(self, 'hour_roller') and self.hour_roller:
                current_selected = self.hour_roller.get_selected()
                self.hour_roller.set_selected(current_selected - 1, True)
                self._update_time_from_rollers()
                print(f"  📱 시간 변경: {self.current_hour:02d}:{self.current_minute:02d}")
            elif not self.editing_hour and hasattr(self, 'minute_roller') and self.minute_roller:
                current_selected = self.minute_roller.get_selected()
                self.minute_roller.set_selected(current_selected - 1, True)
                self._update_time_from_rollers()
                print(f"  📱 시간 변경: {self.current_hour:02d}:{self.current_minute:02d}")
            else:
                print(f"  ⚠️ 롤러 객체가 없습니다. editing_hour: {self.editing_hour}")
        except Exception as e:
            print(f"  ❌ A 버튼 처리 실패: {e}")
    
    def on_button_b(self):
        """B 버튼: 아래로 이동"""
        try:
            if self.editing_hour and hasattr(self, 'hour_roller') and self.hour_roller:
                current_selected = self.hour_roller.get_selected()
                self.hour_roller.set_selected(current_selected + 1, True)
                self._update_time_from_rollers()
                print(f"  📱 시간 변경: {self.current_hour:02d}:{self.current_minute:02d}")
            elif not self.editing_hour and hasattr(self, 'minute_roller') and self.minute_roller:
                current_selected = self.minute_roller.get_selected()
                self.minute_roller.set_selected(current_selected + 1, True)
                self._update_time_from_rollers()
                print(f"  📱 시간 변경: {self.current_hour:02d}:{self.current_minute:02d}")
        except Exception as e:
            print(f"  ❌ B 버튼 처리 실패: {e}")
    
    def on_button_c(self):
        """C 버튼: 뒤로가기 - 복용 횟수 화면으로 되돌아가기"""
        try:
            print(f"  📱 뒤로가기 - 복용 횟수 화면으로 이동")
            
            # 복용 횟수 화면으로 되돌아가기
            if 'dose_count' in self.screen_manager.screens:
                self.screen_manager.show_screen('dose_count')
                print(f"  ✅ 복용 횟수 화면으로 이동 완료")
            else:
                print(f"  ❌ 복용 횟수 화면이 등록되지 않음")
                # 복용 횟수 화면이 없으면 동적으로 생성
                try:
                    from screens.dose_count_screen import DoseCountScreen
                    dose_count_screen = DoseCountScreen(self.screen_manager)
                    self.screen_manager.register_screen('dose_count', dose_count_screen)
                    self.screen_manager.show_screen('dose_count')
                    print(f"  ✅ 복용 횟수 화면 생성 및 이동 완료")
                except Exception as e:
                    print(f"  ❌ 복용 횟수 화면 생성 실패: {e}")
                    
        except Exception as e:
            print(f"  ❌ C 버튼 처리 실패: {e}")
    
    def on_button_d(self):
        """D 버튼: 선택/확인 - 시간/분 모드 전환 또는 다음 단계"""
        try:
            if self.editing_hour:
                # 시간 설정 완료, 분 설정으로 이동
                self.editing_hour = False
                self._update_roller_options()
                print(f"  📱 시간 {self.current_hour:02d}시 설정 완료, 분 설정으로 이동")
            else:
                # 분 설정 완료, 시간 저장하고 다음 단계
                self._save_current_time()
                self._next_time_setup()
        except Exception as e:
            print(f"  ❌ D 버튼 처리 실패: {e}")
    
    def _update_time_from_rollers(self):
        """롤러에서 선택된 값을 시간으로 업데이트"""
        try:
            if hasattr(self, 'hour_roller') and hasattr(self, 'minute_roller'):
                self.current_hour = self.hour_roller.get_selected()
                self.current_minute = self.minute_roller.get_selected() * 5  # 5분 간격
        except Exception as e:
            print(f"  ❌ 시간 업데이트 실패: {e}")
    
    def _update_roller_options(self):
        """롤러 옵션 업데이트"""
        try:
            # 제목 업데이트
            if hasattr(self, 'title_label'):
                if self.editing_hour:
                    self.title_label.set_text(f"복용 시간 {self.current_dose_index + 1} - 시간 설정")
                else:
                    self.title_label.set_text(f"복용 시간 {self.current_dose_index + 1} - 분 설정")
            
        except Exception as e:
            print(f"  ❌ 롤러 옵션 업데이트 실패: {e}")
    
    def _save_current_time(self):
        """현재 설정된 시간 저장"""
        try:
            self._update_time_from_rollers()
            time_str = f"{self.current_hour:02d}:{self.current_minute:02d}"
            self.dose_times.append(time_str)
            print(f"  📱 복용 시간 {self.current_dose_index + 1} 저장: {time_str}")
        except Exception as e:
            print(f"  ❌ 시간 저장 실패: {e}")
    
    def _next_time_setup(self):
        """다음 복용 시간 설정 또는 완료"""
        try:
            self.current_dose_index += 1
            
            if self.current_dose_index < self.dose_count:
                # 다음 복용 시간 설정
                self.editing_hour = True  # 다시 시간 편집 모드로
                self.current_hour = 8  # 기본값으로 리셋
                self.current_minute = 0
                
                # 롤러를 기본값으로 리셋
                if hasattr(self, 'hour_roller') and hasattr(self, 'minute_roller'):
                    self.hour_roller.set_selected(8, True)
                    self.minute_roller.set_selected(0, True)
                
                # 제목 업데이트
                if hasattr(self, 'title_label'):
                    self.title_label.set_text(f"복용 시간 {self.current_dose_index + 1}")
                
                print(f"  📱 복용 시간 {self.current_dose_index + 1} 설정 시작")
            else:
                # 모든 복용 시간 설정 완료
                print(f"  📱 모든 복용 시간 설정 완료!")
                print(f"  📱 설정된 시간들: {self.dose_times}")
                
                # 필 로딩 설정 화면으로 이동
                if 'pill_loading' in self.screen_manager.screens:
                    self.screen_manager.show_screen('pill_loading')
                else:
                    # 필 로딩 화면이 없으면 동적으로 생성
                    print("  📱 pill_loading 화면이 등록되지 않음. 동적 생성 중...")
                    try:
                        from screens.pill_loading_screen import PillLoadingScreen
                        pill_loading_screen = PillLoadingScreen(self.screen_manager)
                        self.screen_manager.register_screen('pill_loading', pill_loading_screen)
                        print("  ✅ pill_loading 화면 생성 및 등록 완료")
                        self.screen_manager.show_screen('pill_loading')
                        print("  📱 필 로딩 화면으로 전환 완료")
                    except Exception as e:
                        print(f"  ❌ 필 로딩 화면 생성 실패: {e}")
                        print("  📱 필 로딩 화면 생성 실패로 현재 화면에 머물기")
            
        except Exception as e:
            print(f"  ❌ 다음 단계 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def get_dose_times(self):
        """설정된 복용 시간들 반환"""
        try:
            return self.dose_times
        except Exception as e:
            print(f"  ❌ 복용 시간 반환 실패: {e}")
            return []
    
    def show(self):
        """화면 표시"""
        try:
            print(f"📱 {self.screen_name} 화면 표시 시작...")
            
            if hasattr(self, 'screen_obj') and self.screen_obj:
                print(f"📱 화면 객체 존재 확인됨")
                
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
                    lv.disp.flush()
                except Exception as flush_error:
                    print(f"⚠️ 디스플레이 플러시 오류 (무시): {flush_error}")
                
                print(f"✅ {self.screen_name} 화면 실행됨")
            else:
                print(f"❌ {self.screen_name} 화면 객체가 없음")
                
        except Exception as e:
            print(f"  ❌ {self.screen_name} 화면 표시 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def hide(self):
        """화면 숨기기"""
        try:
            print(f"📱 {self.screen_name} 화면 숨김")
        except Exception as e:
            print(f"  ❌ {self.screen_name} 화면 숨김 실패: {e}")
    
    def update(self):
        """화면 업데이트"""
        try:
            # 현재는 특별한 업데이트 로직이 없음
            pass
        except Exception as e:
            print(f"  ❌ {self.screen_name} 화면 업데이트 실패: {e}")