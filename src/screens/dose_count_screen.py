"""
복용 횟수 선택 화면
하루 복용 횟수를 선택하는 화면 (1회, 2회, 3회)
Modern UI 스타일 적용
"""

import time
import lvgl as lv
from ui_style import UIStyle

class DoseCountScreen:
    """복용 횟수 선택 화면 클래스 - Modern UI 스타일"""
    
    def __init__(self, screen_manager):
        """복용 횟수 선택 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = 'dose_count'
        self.screen_obj = None
        self.dose_options = [1, 2, 3]
        self.selected_index = 0  # 기본값: 1회 (첫 번째 옵션)
        
        # UI 스타일 시스템 초기화
        self.ui_style = UIStyle()
        
        # Modern 화면 생성
        self._create_modern_screen()
        
        print(f"✅ {self.screen_name} 화면 초기화 완료")
    
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
            self.screen_obj.set_scroll_dir(lv.DIR.NONE)
            print(f"  ✅ 화면 배경 설정 완료")
            
            # 화면 크기 설정
            self.screen_obj.set_size(160, 128)
            print(f"  📱 화면 크기: 160x128")
            
            # 3개 영역으로 구조화
            self._create_status_container()  # 상단 상태 컨테이너
            self._create_main_container()    # 중앙 메인 컨테이너
            self._create_button_hints_area() # 하단 버튼힌트 컨테이너
            
            print(f"  ✅ Modern 화면 생성 완료")
            
        except Exception as e:
            print(f"  ❌ Modern 화면 생성 중 오류 발생: {e}")
            import sys
            sys.print_exception(e)
            # 기본 화면 생성 시도
            print(f"  📱 {self.screen_name} 기본 화면 생성 시도...")
            try:
                self._create_basic_screen()
                print(f"  ✅ {self.screen_name} 기본 화면 초기화 완료")
            except Exception as e2:
                print(f"  ❌ {self.screen_name} 기본 화면 초기화도 실패: {e2}")
                import sys
                sys.print_exception(e2)
    
    def _create_basic_screen(self):
        """기본 화면 생성 (오류 시 대안)"""
        print(f"  📱 {self.screen_name} 기본 화면 생성 시작...")
        
        # 기본 화면 객체 생성
        self.screen_obj = lv.obj()
        self.screen_obj.set_size(160, 128)
        
        # 기본 라벨 생성
        self.title_label = lv.label(self.screen_obj)
        self.title_label.set_text("복용 횟수 설정")
        self.title_label.align(lv.ALIGN.CENTER, 0, 0)
        
        print(f"  ✅ 기본 화면 생성 완료")
    
    def _create_status_container(self):
        """상단 상태 컨테이너 생성"""
        # 상단 상태 컨테이너 (제목 표시)
        self.status_container = lv.obj(self.screen_obj)
        self.status_container.set_size(160, 25)
        self.status_container.align(lv.ALIGN.TOP_MID, 0, 0)
        self.status_container.set_style_bg_opa(0, 0)
        self.status_container.set_style_border_width(0, 0)
        self.status_container.set_style_pad_all(0, 0)
        
        # 제목 텍스트
        self.title_text = lv.label(self.status_container)
        self.title_text.set_text("복용 횟수 설정")
        self.title_text.align(lv.ALIGN.CENTER, 0, 0)
        self.title_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.title_text.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
        
        # 한국어 폰트 적용
        korean_font = getattr(lv, "font_notosans_kr_regular", None)
        if korean_font:
            self.title_text.set_style_text_font(korean_font, 0)
        
        print("  ✅ 상단 상태 컨테이너 생성 완료")
    
    def _create_main_container(self):
        """중앙 메인 컨테이너 생성"""
        # 메인 컨테이너 (상단 25px, 하단 20px 제외)
        self.main_container = lv.obj(self.screen_obj)
        self.main_container.set_size(160, 83)
        self.main_container.align(lv.ALIGN.TOP_MID, 0, 25)
        self.main_container.set_style_bg_opa(0, 0)
        self.main_container.set_style_border_width(0, 0)
        self.main_container.set_style_pad_all(0, 0)
        
        # 스크롤바 비활성화
        self.main_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.main_container.set_scroll_dir(lv.DIR.NONE)
        
        # 복용 횟수 선택 영역 생성
        self._create_dose_selection_area()
        
        print("  ✅ 중앙 메인 컨테이너 생성 완료")
    
    def _create_dose_selection_area(self):
        """복용 횟수 선택 영역 생성"""
        try:
            # 롤러 생성
            self.dose_roller = lv.roller(self.main_container)
            self.dose_roller.set_size(140, 60)
            self.dose_roller.align(lv.ALIGN.CENTER, 0, 0)
            
            # 롤러 옵션 설정
            options = "\n".join([f"{i}회" for i in self.dose_options])
            self.dose_roller.set_options(options, lv.ROLLER_MODE.INFINITE)
            self.dose_roller.set_selected(self.selected_index, True)  # True = 애니메이션 있음
            
            # 롤러 스타일
            self.dose_roller.set_style_bg_color(lv.color_hex(0xF2F2F7), 0)
            self.dose_roller.set_style_border_width(0, 0)
            self.dose_roller.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
            
            # 한국어 폰트 적용
            korean_font = getattr(lv, "font_notosans_kr_regular", None)
            if korean_font:
                self.dose_roller.set_style_text_font(korean_font, 0)
            
            print("  ✅ 복용 횟수 선택 영역 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 복용 횟수 선택 영역 생성 실패: {e}")
    
    def _create_button_hints_area(self):
        """하단 버튼힌트 컨테이너 생성"""
        # 버튼힌트 컨테이너 (화면 하단에 직접 배치)
        self.hints_container = lv.obj(self.screen_obj)
        self.hints_container.set_size(140, 18)
        self.hints_container.align(lv.ALIGN.BOTTOM_MID, 0, -2)
        self.hints_container.set_style_bg_opa(0, 0)
        self.hints_container.set_style_border_width(0, 0)
        self.hints_container.set_style_pad_all(0, 0)
        
        # 버튼힌트 텍스트 (lv 기본 폰트 사용)
        self.hints_text = lv.label(self.hints_container)
        self.hints_text.set_text(f"A:{lv.SYMBOL.UP} B:{lv.SYMBOL.DOWN} C:{lv.SYMBOL.PREV} D:{lv.SYMBOL.OK}")
        self.hints_text.align(lv.ALIGN.CENTER, 0, 0)
        self.hints_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.hints_text.set_style_text_color(lv.color_hex(0x8E8E93), 0)
        # lv 기본 폰트 사용 (한국어 폰트 적용하지 않음)
        
        print("  ✅ 하단 버튼힌트 컨테이너 생성 완료")
    
    def _create_title_area(self):
        """제목 영역 생성 (Wi-Fi 스캔 화면과 동일한 위치)"""
        try:
            # 제목 텍스트 (화면에 직접) - Wi-Fi 스캔 화면과 동일한 스타일
            self.title_text = lv.label(self.screen_obj)
            self.title_text.set_text("복용 횟수 설정")
            self.title_text.set_style_text_color(lv.color_hex(0x1D1D1F), 0)  # 모던 다크 그레이
            
            # 한국어 폰트 적용
            korean_font = getattr(lv, "font_notosans_kr_regular", None)
            if korean_font:
                self.title_text.set_style_text_font(korean_font, 0)
                print("  ✅ 제목에 한국어 폰트 적용 완료")
            
            # Wi-Fi 스캔 화면과 동일한 위치 (TOP_MID, 0, 10)
            self.title_text.align(lv.ALIGN.TOP_MID, 0, 10)
            self.title_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            
            print("  ✅ 제목 텍스트 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 제목 영역 생성 실패: {e}")
    
    def _create_dose_selection_area(self):
        """복용 횟수 선택 영역 생성 (롤러 위젯 사용)"""
        try:
            # 롤러 옵션 문자열 생성
            roller_options = []
            for dose_count in self.dose_options:
                roller_options.append(f"{dose_count}회")
            
            # 롤러 옵션을 개행 문자로 연결
            roller_options_str = "\n".join(roller_options)
            print(f"  📱 롤러 옵션: {roller_options_str}")
            
            # 롤러 위젯 생성 (화면에 직접)
            self.dose_roller = lv.roller(self.screen_obj)
            self.dose_roller.set_options(roller_options_str, lv.roller.MODE.NORMAL)  # INFINITE → NORMAL
            self.dose_roller.set_size(120, 60)
            self.dose_roller.align(lv.ALIGN.CENTER, 0, 0)  # 화면 중앙에 배치
            
            # 롤러 스타일 설정 (이전 스타일로 복원)
            self.dose_roller.set_style_bg_color(lv.color_hex(0xF2F2F7), 0)  # iOS 라이트 그레이
            self.dose_roller.set_style_bg_opa(255, 0)
            self.dose_roller.set_style_radius(10, 0)
            self.dose_roller.set_style_border_width(1, 0)
            self.dose_roller.set_style_border_color(lv.color_hex(0xD1D5DB), 0)  # 회색 테두리
            
            # 롤러 텍스트 스타일
            self.dose_roller.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
            self.dose_roller.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            
            # 한국어 폰트 적용
            korean_font = getattr(lv, "font_notosans_kr_regular", None)
            if korean_font:
                self.dose_roller.set_style_text_font(korean_font, 0)
                print("  ✅ 롤러에 한국어 폰트 적용 완료")
            
            # 롤러 선택된 항목 스타일 (선택된 행) - 더 명확하게
            try:
                self.dose_roller.set_style_bg_color(lv.color_hex(0x007AFF), lv.PART.SELECTED)  # iOS 블루
                self.dose_roller.set_style_bg_opa(255, lv.PART.SELECTED)
                self.dose_roller.set_style_text_color(lv.color_hex(0xFFFFFF), lv.PART.SELECTED)  # 흰색 텍스트
                self.dose_roller.set_style_radius(6, lv.PART.SELECTED)
                print("  ✅ 롤러 선택된 항목 스타일 설정 완료")
            except AttributeError:
                print("  ⚠️ lv.PART.SELECTED 지원 안됨, 기본 스타일 사용")
            
            # 초기 선택 설정 (1회가 기본값)
            try:
                # LVGL 버전에 따라 애니메이션 상수가 다를 수 있음
                self.dose_roller.set_selected(self.selected_index, lv.ANIM.OFF)
            except AttributeError:
                # lv.ANIM이 없는 경우 애니메이션 없이 설정
                self.dose_roller.set_selected(self.selected_index, 0)
            
            # 롤러 이벤트 콜백 등록
            self.dose_roller.add_event_cb(self._on_roller_value_changed, lv.EVENT.VALUE_CHANGED, None)
            
            print("  ✅ 복용 횟수 롤러 생성 완료")
            print("  ✅ 복용 횟수 선택 영역 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 복용 횟수 선택 영역 생성 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _on_roller_value_changed(self, event):
        """롤러 값 변경 이벤트 처리"""
        try:
            roller = event.get_target()
            selected_idx = roller.get_selected()
            
            if selected_idx != self.selected_index:
                self.selected_index = selected_idx
                selected_dose = self.dose_options[self.selected_index]
                print(f"  📱 롤러 선택 변경: {selected_dose}회 (인덱스: {self.selected_index})")
                
        except Exception as e:
            print(f"  ❌ 롤러 값 변경 처리 실패: {e}")
    
    
    def get_title(self):
        """화면 제목"""
        return "복용 횟수"
    
    def get_button_hints(self):
        """버튼 힌트 (기호 사용)"""
        return f"A:{lv.SYMBOL.UP} B:{lv.SYMBOL.DOWN} C:{lv.SYMBOL.PREV} D:{lv.SYMBOL.OK}"
    
    def get_voice_file(self):
        """안내 음성 파일"""
        return "wav_dose_count_prompt.wav"
    
    def get_effect_file(self):
        """효과음 파일"""
        return "wav_adjust.wav"
    
    def show(self):
        """화면 표시"""
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
                lv.disp_drv_t.flush_ready(None)
            except AttributeError:
                try:
                    lv.disp_t.flush_ready(None)
                except AttributeError:
                    print("⚠️ 디스플레이 플러시 오류 (무시): 'module' object has no attribute 'disp_t'")
            
            print(f"📱 화면 전환: {self.screen_name}")
        else:
            print(f"❌ {self.screen_name} 화면 객체가 없음")
    
    def hide(self):
        """화면 숨기기"""
        print(f"📱 {self.screen_name} 화면 숨기기")
        # 화면 숨기기 로직 (필요시 구현)
        pass
    
    def update(self):
        """화면 업데이트 (ScreenManager에서 호출)"""
        # 현재는 특별한 업데이트 로직이 없음
        pass
    
    def on_button_a(self):
        """버튼 A (위) 처리 - 이전 복용 횟수로 이동"""
        print("복용 횟수 위로 이동")
        
        if self.selected_index > 0:
            prev_index = self.selected_index - 1
            print(f"  📱 롤러 선택 업데이트: 인덱스 {prev_index}")
            
            # 롤러 직접 조작 (애니메이션과 함께)
            try:
                self.dose_roller.set_selected(prev_index, lv.ANIM.ON)
                print(f"  📱 롤러 애니메이션과 함께 설정 완료")
            except AttributeError:
                self.dose_roller.set_selected(prev_index, 1)
                print(f"  📱 롤러 애니메이션 없이 설정 완료")
            
            # 강제 업데이트
            try:
                lv.timer_handler()
            except:
                pass
            
            self.selected_index = prev_index
            print(f"  ✅ 롤러 선택 업데이트 완료: {self.dose_options[self.selected_index]}회")
        else:
            print(f"  📱 이미 첫 번째 옵션 (1회)")
    
    def on_button_b(self):
        """버튼 B (아래) 처리 - 다음 복용 횟수로 이동"""
        print("복용 횟수 아래로 이동")
        
        if self.selected_index < len(self.dose_options) - 1:
            next_index = self.selected_index + 1
            print(f"  📱 롤러 선택 업데이트: 인덱스 {next_index}")
            
            # 롤러 직접 조작 (애니메이션과 함께)
            try:
                self.dose_roller.set_selected(next_index, lv.ANIM.ON)
                print(f"  📱 롤러 애니메이션과 함께 설정 완료")
            except AttributeError:
                self.dose_roller.set_selected(next_index, 1)
                print(f"  📱 롤러 애니메이션 없이 설정 완료")
            
            # 강제 업데이트
            try:
                lv.timer_handler()
            except:
                pass
            
            self.selected_index = next_index
            print(f"  ✅ 롤러 선택 업데이트 완료: {self.dose_options[self.selected_index]}회")
        else:
            print(f"  📱 이미 마지막 옵션 (3회)")
    
    def on_button_c(self):
        """버튼 C (뒤로가기) 처리"""
        print("복용 횟수 화면 뒤로가기")
        
        # Wi-Fi 패스워드 화면으로 돌아가기
        if 'wifi_password' in self.screen_manager.screens:
            self.screen_manager.show_screen('wifi_password')
        else:
            print("  📱 Wi-Fi 패스워드 화면이 없어서 Wi-Fi 스캔으로 돌아갑니다")
            if 'wifi_scan' in self.screen_manager.screens:
                self.screen_manager.show_screen('wifi_scan')
            else:
                print("  📱 Wi-Fi 스캔 화면도 없습니다")
    
    def on_button_d(self):
        """버튼 D (선택) 처리 - 복용 횟수 선택 완료"""
        # 롤러에서 현재 선택된 값 가져오기
        selected_dose_count = self.get_selected_dose_count()
        print(f"복용 횟수 선택 완료: {selected_dose_count}회")
        
        # 선택된 복용 횟수를 저장 (필요시)
        self.selected_dose_count = selected_dose_count
        
        # 복용 시간 화면으로 이동
        print(f"  📱 복용 시간 설정 화면으로 이동... (복용 횟수: {selected_dose_count}회)")
        
        try:
            print(f"  📱 복용 시간 화면 생성 시작...")
            
            # 새로운 복용 시간 화면 생성 (항상 새로 생성)
            from screens.dose_time_screen import DoseTimeScreen
            dose_time_screen = DoseTimeScreen(self.screen_manager, dose_count=selected_dose_count)
            
            print(f"  📱 복용 시간 화면 등록 시작...")
            self.screen_manager.register_screen('dose_time', dose_time_screen)
            print(f"  📱 복용 시간 화면 등록 완료")
            
            print(f"  📱 복용 시간 화면으로 이동 시작...")
            # 복용 시간 화면으로 이동
            self.screen_manager.show_screen('dose_time')
            print(f"  ✅ 복용 시간 화면으로 이동 완료")
            
        except Exception as e:
            print(f"  ❌ 복용 시간 화면으로 이동 실패: {e}")
            import sys
            sys.print_exception(e)
            print(f"  📱 복용 횟수 설정 완료! (현재 화면에 머물기)")
            print(f"  📱 선택된 복용 횟수: {selected_dose_count}회")
    
    def on_button_a(self):
        """A 버튼: 위로 이동"""
        try:
            if hasattr(self, 'dose_roller'):
                current_selected = self.dose_roller.get_selected()
                if current_selected > 0:
                    self.dose_roller.set_selected(current_selected - 1, True)  # True = 애니메이션 있음
                    self.selected_index = current_selected - 1
                    print(f"  📱 복용 횟수: {self.dose_options[self.selected_index]}회")
        except Exception as e:
            print(f"  ❌ A 버튼 처리 실패: {e}")
    
    def on_button_b(self):
        """B 버튼: 아래로 이동"""
        try:
            if hasattr(self, 'dose_roller'):
                current_selected = self.dose_roller.get_selected()
                if current_selected < len(self.dose_options) - 1:
                    self.dose_roller.set_selected(current_selected + 1, True)  # True = 애니메이션 있음
                    self.selected_index = current_selected + 1
                    print(f"  📱 복용 횟수: {self.dose_options[self.selected_index]}회")
        except Exception as e:
            print(f"  ❌ B 버튼 처리 실패: {e}")
    
    def on_button_c(self):
        """C 버튼: 뒤로가기"""
        try:
            print(f"  📱 뒤로가기 - Wi-Fi 스캔 화면으로 이동")
            self.screen_manager.show_screen('wifi_scan')
        except Exception as e:
            print(f"  ❌ C 버튼 처리 실패: {e}")
    
    def on_button_d(self):
        """D 버튼: 선택/확인"""
        try:
            if hasattr(self, 'dose_roller'):
                self.selected_index = self.dose_roller.get_selected()
            selected_dose_count = self.dose_options[self.selected_index]
            print(f"  📱 복용 횟수 {selected_dose_count}회 선택됨")
            
            # 다음 화면으로 이동 (복용 시간 설정)
            self._go_to_next_screen(selected_dose_count)
        except Exception as e:
            print(f"  ❌ D 버튼 처리 실패: {e}")
    
    def _go_to_next_screen(self, selected_dose_count):
        """다음 화면으로 이동 (복용 시간 설정)"""
        try:
            print(f"  📱 복용 시간 설정 화면으로 이동")
            
            # 복용 시간 설정 화면이 등록되어 있으면 이동, 없으면 생성
            if 'dose_time' in self.screen_manager.screens:
                self.screen_manager.show_screen('dose_time')
            else:
                print("  📱 dose_time 화면을 생성합니다.")
                
                # 메모리 정리
                import gc
                gc.collect()
                print("  ✅ 화면 생성 전 메모리 정리 완료")
                
                # 추가 메모리 정리
                gc.collect()
                print("  ✅ 추가 메모리 정리 완료")
                
                try:
                    from screens.dose_time_screen import DoseTimeScreen
                    print("  📱 DoseTimeScreen 클래스 로드 완료")
                    
                    # 메모리 정리
                    gc.collect()
                    
                    dose_time_screen = DoseTimeScreen(self.screen_manager, selected_dose_count)
                    print("  📱 DoseTimeScreen 객체 생성 완료")
                    
                    # 메모리 정리
                    gc.collect()
                    
                    self.screen_manager.register_screen('dose_time', dose_time_screen)
                    print("✅ dose_time 화면 생성 및 등록 완료")
                    
                    # 메모리 정리
                    gc.collect()
                    
                    self.screen_manager.show_screen('dose_time')
                except Exception as e:
                    print(f"❌ dose_time 화면 생성 실패: {e}")
                    print("  📱 복용 횟수 설정 화면에 머물기")
        except Exception as e:
            print(f"  ❌ 다음 화면으로 이동 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def get_selected_dose_count(self):
        """선택된 복용 횟수 반환"""
        try:
            return self.dose_options[self.selected_index]
        except Exception as e:
            print(f"  ❌ 선택된 복용 횟수 가져오기 실패: {e}")
            return 1  # 기본값