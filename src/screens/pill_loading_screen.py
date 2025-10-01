"""
알약 충전 화면
알약을 디스크에 충전하는 화면
"""

import time
import math
import lvgl as lv
from ui_style import UIStyle

class DiskState:
    """디스크 상태 관리 클래스 (리미트 스위치 기반)"""
    
    def __init__(self, disk_id):
        self.disk_id = disk_id
        self.total_compartments = 15  # 총 15칸
        self.compartments_per_loading = 3  # 한 번에 3칸씩 충전
        self.loaded_count = 0  # 리미트 스위치로 카운트된 충전된 칸 수
        self.is_loading = False  # 현재 충전 중인지 여부
        self.current_loading_count = 0  # 현재 충전 중인 칸 수 (0-3)
        
    def can_load_more(self):
        """더 충전할 수 있는지 확인"""
        return self.loaded_count < self.total_compartments
    
    def start_loading(self):
        """충전 시작 (3칸씩)"""
        if self.can_load_more():
            self.is_loading = True
            self.current_loading_count = 0
            return True
        return False
    
    def complete_loading(self):
        """충전 완료 (리미트 스위치 감지 시 호출)"""
        if self.is_loading:
            self.current_loading_count += 1
            self.loaded_count += 1  # 리미트 스위치 1번 감지 = 1칸 이동
            print(f"  📱 리미트 스위치 {self.current_loading_count}번째 감지 - 1칸 이동 (총 {self.loaded_count}칸)")
            
            # 3칸이 모두 충전되면 충전 완료
            if self.current_loading_count >= 3:
                self.is_loading = False
                print(f"  📱 3칸 충전 완료! 총 {self.loaded_count}칸")
                return True
            return False
        return False
    
    def get_loading_progress(self):
        """충전 진행률 반환 (0-100)"""
        return (self.loaded_count / self.total_compartments) * 100

class PillLoadingScreen:
    """알약 충전 화면 클래스"""
    
    def __init__(self, screen_manager):
        """알약 충전 화면 초기화"""
        # 메모리 정리
        import gc
        gc.collect()
        
        self.screen_manager = screen_manager
        self.screen_name = 'pill_loading'
        self.screen_obj = None
        self.selected_disk_index = 0  # 0, 1, 2 (디스크 1, 2, 3)
        self.is_loading = False
        self.loading_progress = 0  # 0-100%
        self.current_mode = 'selection'  # 'selection' 또는 'loading'
        self.current_disk_state = None
        
        # 디스크 상태 관리
        self.disk_states = {}
        for i in range(3):
            self.disk_states[i] = DiskState(i + 1)
        
        # UI 스타일 초기화
        try:
            self.ui_style = UIStyle()
            print("✅ UI 스타일 초기화 완료")
        except Exception as e:
            print(f"⚠️ UI 스타일 초기화 실패: {e}")
            self.ui_style = None
        
        # 모터 시스템 초기화
        try:
            from motor_control import PillBoxMotorSystem
            self.motor_system = PillBoxMotorSystem()
            
            # 모터 시스템 초기화 시 원점 보정 (선택사항)
            # self.motor_system.calibrate_all_disks()
            
            print("✅ 모터 시스템 초기화 완료")
        except Exception as e:
            print(f"⚠️ 모터 시스템 초기화 실패: {e}")
            self.motor_system = None
        
        # 화면 생성
        self._create_modern_screen()
        
        print(f"✅ {self.screen_name} 화면 초기화 완료")
    
    def _create_modern_screen(self):
        """Modern 스타일 화면 생성 (dose_count_screen과 일관된 스타일)"""
        print(f"  📱 {self.screen_name} Modern 화면 생성 시작...")
        
        # 강력한 메모리 정리
        import gc
        for i in range(5):
            gc.collect()
            time.sleep(0.02)
        print(f"  ✅ 메모리 정리 완료")
        
        # 화면 객체 생성
        print(f"  📱 화면 객체 생성...")
        self.screen_obj = lv.obj()
        self.screen_obj.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)  # 화이트 배경
        
        # 메인 화면 스크롤바 비활성화
        self.screen_obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.screen_obj.set_scroll_dir(lv.DIR.NONE)
        
        print(f"  ✅ 화면 객체 생성 완료")
        
        # 3개 영역으로 구조화 (단계별 메모리 정리)
        print(f"  📱 상단 상태 컨테이너 생성...")
        self._create_status_container()  # 상단 상태 컨테이너
        import gc; gc.collect()
        
        print(f"  📱 중앙 메인 컨테이너 생성...")
        self._create_main_container()    # 중앙 메인 컨테이너
        import gc; gc.collect()
        
        print(f"  📱 하단 버튼힌트 컨테이너 생성...")
        self._create_button_hints_area() # 하단 버튼힌트 컨테이너
        import gc; gc.collect()
        
        print(f"  ✅ Modern 화면 생성 완료")
    
    def _create_status_container(self):
        """상단 상태 컨테이너 생성"""
        # 상단 상태 컨테이너 (제목 표시)
        self.status_container = lv.obj(self.screen_obj)
        self.status_container.set_size(160, 25)
        self.status_container.align(lv.ALIGN.TOP_MID, 0, 0)
        self.status_container.set_style_bg_opa(0, 0)
        self.status_container.set_style_border_width(0, 0)
        self.status_container.set_style_pad_all(0, 0)
        
        # 스크롤바 비활성화
        self.status_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.status_container.set_scroll_dir(lv.DIR.NONE)
        
        # 제목 텍스트
        self.title_text = lv.label(self.status_container)
        self.title_text.set_text("알약 충전")
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
        
        # 디스크 선택 영역 생성
        self._create_disk_selection_area()
        
        print("  ✅ 중앙 메인 컨테이너 생성 완료")
    
    def _create_disk_selection_area(self):
        """디스크 선택 영역 생성"""
        try:
            # 디스크 선택 안내 텍스트
            self.disk_label = lv.label(self.main_container)
            self.disk_label.set_text("디스크를 선택하세요")
            self.disk_label.align(lv.ALIGN.CENTER, 0, 0)
            self.disk_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            self.disk_label.set_style_text_color(lv.color_hex(0x333333), 0)
            
            # 한국어 폰트 적용
            korean_font = getattr(lv, "font_notosans_kr_regular", None)
            if korean_font:
                self.disk_label.set_style_text_font(korean_font, 0)
            
            print("  ✅ 디스크 선택 영역 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 디스크 선택 영역 생성 실패: {e}")
    
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
        self.hints_text.set_text(f"A:{lv.SYMBOL.UP} B:{lv.SYMBOL.DOWN} C:{lv.SYMBOL.PREV} D:{lv.SYMBOL.DOWNLOAD}")
        self.hints_text.align(lv.ALIGN.CENTER, 0, 0)
        self.hints_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.hints_text.set_style_text_color(lv.color_hex(0x8E8E93), 0)
        # lv 기본 폰트 사용 (한국어 폰트 적용하지 않음)
        
        # 스크롤바 비활성화
        self.hints_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.hints_container.set_scroll_dir(lv.DIR.NONE)
        
        print("  ✅ 하단 버튼힌트 컨테이너 생성 완료")
    
    def _create_main_container(self):
        """중앙 메인 컨테이너 생성"""
        # 메인 컨테이너 (상단 25px, 하단 20px 제외)
        self.main_container = lv.obj(self.screen_obj)
        self.main_container.set_size(160, 83)  # 128 - 25 - 20 = 83
        self.main_container.align(lv.ALIGN.TOP_MID, 0, 25)
        self.main_container.set_style_bg_opa(0, 0)
        self.main_container.set_style_border_width(0, 0)
        self.main_container.set_style_pad_all(0, 0)
        
        # 스크롤바 비활성화
        self.main_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.main_container.set_scroll_dir(lv.DIR.NONE)
        
        # 메인 컨테이너 안에 디스크 선택 영역 생성
        self._create_disk_selection_area()
        
        print("  ✅ 중앙 메인 컨테이너 생성 완료")
    
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
        self.hints_text.set_text(f"A:{lv.SYMBOL.UP} B:{lv.SYMBOL.DOWN} C:{lv.SYMBOL.PREV} D:{lv.SYMBOL.DOWNLOAD}")
        self.hints_text.align(lv.ALIGN.CENTER, 0, 0)
        self.hints_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.hints_text.set_style_text_color(lv.color_hex(0x8E8E93), 0)
        # lv 기본 폰트 사용 (한국어 폰트 적용하지 않음)
        
        print("  ✅ 하단 버튼힌트 컨테이너 생성 완료")
        
        # 스크롤바 비활성화
        self.hints_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.hints_container.set_scroll_dir(lv.DIR.NONE)
    
    def _create_title_area(self):
        """제목 영역 생성"""
        print(f"  📱 제목 영역 생성 시도...")
        
        try:
            # 제목 라벨 (화면에 직접)
            self.title_text = lv.label(self.screen_obj)
            self.title_text.set_text("알약 충전")
            self.title_text.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
            self.title_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            
            # 한국어 폰트 적용
            if hasattr(lv, "font_notosans_kr_regular"):
                self.title_text.set_style_text_font(lv.font_notosans_kr_regular, 0)
                print("  ✅ 제목에 한국어 폰트 적용 완료")
            
            # 제목 위치 (상단 중앙)
            self.title_text.align(lv.ALIGN.TOP_MID, 0, 10)
            
            print("  ✅ 제목 텍스트 생성 완료")
            print("  📱 제목 영역 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 제목 영역 생성 실패: {e}")
    
    def _create_disk_selection_area(self):
        """디스크 선택 영역 생성"""
        print(f"  📱 디스크 선택 영역 생성 시도...")
        
        try:
            # 디스크 옵션들
            self.disk_options = ["디스크 1", "디스크 2", "디스크 3"]
            
            # 롤러 옵션을 개행 문자로 연결
            roller_options_str = "\n".join(self.disk_options)
            print(f"  📱 롤러 옵션: {roller_options_str}")
            
            # 롤러 위젯 생성 (화면에 직접)
            self.disk_roller = lv.roller(self.screen_obj)
            self.disk_roller.set_options(roller_options_str, lv.roller.MODE.INFINITE)
            self.disk_roller.set_size(120, 60)
            self.disk_roller.align(lv.ALIGN.CENTER, 0, 0)  # 화면 중앙에 배치
            
            # 롤러 스타일 설정 (dose_count_screen과 동일)
            self.disk_roller.set_style_bg_color(lv.color_hex(0xF2F2F7), 0)  # iOS 라이트 그레이
            self.disk_roller.set_style_bg_opa(255, 0)
            self.disk_roller.set_style_radius(10, 0)
            self.disk_roller.set_style_border_width(1, 0)
            self.disk_roller.set_style_border_color(lv.color_hex(0xD1D5DB), 0)
            
            # 롤러 텍스트 스타일
            self.disk_roller.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
            self.disk_roller.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            
            # 한국어 폰트 적용
            if hasattr(lv, "font_notosans_kr_regular"):
                self.disk_roller.set_style_text_font(lv.font_notosans_kr_regular, 0)
                print("  ✅ 롤러에 한국어 폰트 적용 완료")
            
            # 롤러 선택된 항목 스타일
            try:
                self.disk_roller.set_style_bg_color(lv.color_hex(0x007AFF), lv.PART.SELECTED)  # iOS 블루
                self.disk_roller.set_style_bg_opa(255, lv.PART.SELECTED)
                self.disk_roller.set_style_text_color(lv.color_hex(0xFFFFFF), lv.PART.SELECTED)  # 흰색 텍스트
                self.disk_roller.set_style_radius(6, lv.PART.SELECTED)
                print("  ✅ 롤러 선택된 항목 스타일 설정 완료")
            except AttributeError:
                print("  ⚠️ lv.PART.SELECTED 지원 안됨, 기본 스타일 사용")
            
            # 초기 선택 설정 (디스크 1이 기본값)
            try:
                self.disk_roller.set_selected(self.selected_disk_index, lv.ANIM.OFF)
            except AttributeError:
                self.disk_roller.set_selected(self.selected_disk_index, 0)
            
            print("  ✅ 디스크 선택 롤러 생성 완료")
            print("  ✅ 디스크 선택 영역 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 디스크 선택 영역 생성 실패: {e}")
    
    def _create_button_hints_area(self):
        """하단 버튼 힌트 영역 생성 (간단한 방식)"""
        try:
            print("  📱 버튼 힌트 텍스트 생성 시도...")
            
            # 버튼 힌트 텍스트 (화면에 직접) - dose_count_screen과 동일한 스타일
            self.hints_text = lv.label(self.screen_obj)
            
            # LVGL 심볼 사용 시 안전하게 처리
            try:
                prev_symbol = getattr(lv.SYMBOL, 'PREV', '<')
                next_symbol = getattr(lv.SYMBOL, 'NEXT', '>')
                ok_symbol = getattr(lv.SYMBOL, 'OK', '✓')
                down_symbol = getattr(lv.SYMBOL, 'DOWN', 'v')
                
                button_text = f"A:{prev_symbol} B:{next_symbol} C:{ok_symbol} D:{down_symbol}"
                self.hints_text.set_text(button_text)
                print(f"  ✅ 버튼 힌트 텍스트 설정 완료: {button_text}")
            except Exception as symbol_error:
                print(f"  ⚠️ 심볼 사용 실패, 텍스트로 대체: {symbol_error}")
                self.hints_text.set_text("A:< B:> C:✓ D:v")
            
            self.hints_text.set_style_text_color(lv.color_hex(0x8E8E93), 0)  # 모던 라이트 그레이
            
            # 한국어 폰트 적용 (기본 폰트 사용으로 변경)
            try:
                # lv 기본 폰트 사용 (한국어 폰트 대신)
                print("  ✅ 버튼 힌트에 기본 폰트 사용")
            except Exception as font_error:
                print(f"  ⚠️ 폰트 설정 실패: {font_error}")
            
            # dose_count_screen과 동일한 위치 (BOTTOM_MID, 0, -2)
            self.hints_text.align(lv.ALIGN.BOTTOM_MID, 0, -2)
            self.hints_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            
            print("  ✅ 버튼 힌트 영역 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 버튼 힌트 영역 생성 실패: {e}")
    
    def _create_loading_sub_screen(self):
        """디스크 충전 서브 화면 생성"""
        print(f"  📱 디스크 충전 서브 화면 생성 시작...")
        
        try:
            # 기존 화면 숨기기
            print(f"  📱 기존 화면 숨기기...")
            if hasattr(self, 'disk_roller'):
                self.disk_roller.set_style_opa(0, 0)  # 투명하게
                print(f"  ✅ 롤러 숨김 완료")
            
            # 제목 업데이트
            print(f"  📱 제목 업데이트...")
            if hasattr(self, 'title_text'):
                disk_id = self.selected_disk_index + 1
                self.title_text.set_text(f"디스크 {disk_id} 충전")
                print(f"  ✅ 제목 업데이트 완료: 디스크 {disk_id} 충전")
            
            # 아크 프로그레스 바 생성 (왼쪽으로 이동, 아래로 10픽셀)
            print(f"  📱 아크 프로그레스 바 생성...")
            self.progress_arc = lv.arc(self.screen_obj)
            self.progress_arc.set_size(60, 60)
            self.progress_arc.align(lv.ALIGN.CENTER, -30, 10)
            print(f"  ✅ 아크 생성 및 위치 설정 완료")
            
            # 아크 설정 (270도에서 시작하여 시계방향으로)
            print(f"  📱 아크 설정...")
            self.progress_arc.set_bg_angles(0, 360)
            self.progress_arc.set_angles(0, 0)  # 초기값 0%
            self.progress_arc.set_rotation(270)  # 12시 방향에서 시작
            print(f"  ✅ 아크 각도 설정 완료")
            
            # 아크 스타일 설정
            print(f"  📱 아크 스타일 설정...")
            self.progress_arc.set_style_arc_width(6, 0)  # 배경 아크 두께
            self.progress_arc.set_style_arc_color(lv.color_hex(0xE0E0E0), 0)  # 배경 회색
            self.progress_arc.set_style_arc_width(6, lv.PART.INDICATOR)  # 진행 아크 두께
            self.progress_arc.set_style_arc_color(lv.color_hex(0x00C9A7), lv.PART.INDICATOR)  # 진행 민트색
            print(f"  ✅ 아크 스타일 설정 완료")
            
            # 진행률 텍스트 라벨 (아크 중앙에)
            print(f"  📱 진행률 텍스트 라벨 생성...")
            self.progress_label = lv.label(self.screen_obj)
            progress = self.current_disk_state.get_loading_progress()
            self.progress_label.set_text(f"{progress:.0f}%")
            self.progress_label.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
            self.progress_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            print(f"  ✅ 진행률 라벨 생성 완료: {progress:.0f}%")
            
            # 한국어 폰트 적용
            if hasattr(lv, "font_notosans_kr_regular"):
                self.progress_label.set_style_text_font(lv.font_notosans_kr_regular, 0)
                print("  ✅ 진행률 라벨에 한국어 폰트 적용 완료")
            
            # 아크 중앙에 텍스트 배치 (아크와 함께 왼쪽으로 이동, 아래로 10픽셀)
            self.progress_label.align(lv.ALIGN.CENTER, -30, 10)
            print(f"  ✅ 진행률 라벨 위치 설정 완료")
            
            # 세부 정보 라벨 (아크 오른쪽에) - 리미트 스위치 기반 카운트
            print(f"  📱 세부 정보 라벨 생성...")
            self.detail_label = lv.label(self.screen_obj)
            loaded_count = self.current_disk_state.loaded_count
            self.detail_label.set_text(f"{loaded_count}/15칸")
            self.detail_label.set_style_text_color(lv.color_hex(0x000000), 0)  # 검정색
            self.detail_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            self.detail_label.set_style_opa(255, 0)  # 완전 불투명
            print(f"  ✅ 세부 정보 라벨 생성 완료: {loaded_count}/15칸")
            
            # 한국어 폰트 적용 (Noto Sans KR) - wifi_scan_screen 방식 사용
            if hasattr(lv, "font_notosans_kr_regular"):
                self.detail_label.set_style_text_font(lv.font_notosans_kr_regular, 0)
                print("  ✅ 0/15칸 라벨에 한국어 폰트 적용 완료")
            else:
                print("  ⚠️ 한국어 폰트를 찾을 수 없습니다")
            
            # 아크 오른쪽에 배치 (아크와 같은 높이)
            print(f"  📱 세부 정보 라벨 위치 설정: CENTER, 30, 10")
            self.detail_label.align(lv.ALIGN.CENTER, 30, 10)
            print(f"  ✅ 세부 정보 라벨 위치 설정 완료")
            
            # 위치 강제 업데이트
            print(f"  📱 라벨 위치 강제 업데이트...")
            try:
                lv.timer_handler()
                print(f"  ✅ 라벨 위치 강제 업데이트 완료")
            except Exception as e:
                print(f"  ⚠️ 라벨 위치 강제 업데이트 실패: {e}")
            
            # 디스크 시각화 제거 - 아크만 사용
            
            # 버튼 힌트 업데이트
            print(f"  📱 버튼 힌트 업데이트...")
            try:
                if hasattr(self, 'hints_text') and self.hints_text:
                    try:
                        ok_symbol = getattr(lv.SYMBOL, 'OK', '✓')
                        download_symbol = getattr(lv.SYMBOL, 'DOWNLOAD', '⬇')
                        self.hints_text.set_text(f"A: -  B: -  C:{ok_symbol}  D:{download_symbol}")
                    except:
                        self.hints_text.set_text("A: -  B: -  C:✓  D:⬇")
                    print(f"  ✅ 버튼 힌트 업데이트 완료")
                else:
                    print(f"  ⚠️ 버튼 힌트 텍스트 객체가 없음")
            except Exception as e:
                print(f"  ❌ 버튼 힌트 업데이트 실패: {e}")
            
            print("  ✅ 디스크 충전 서브 화면 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 디스크 충전 서브 화면 생성 실패: {e}")
    
    def _create_disk_visualization(self):
        """디스크 시각화 제거됨 - 아크만 사용"""
        # 디스크 시각화 기능 제거됨
        pass
    
    def _update_disk_visualization(self):
        """아크 프로그레스 바 업데이트 (리미트 스위치 기반)"""
        try:
            # 진행률 업데이트
            if hasattr(self, 'progress_label'):
                progress = self.current_disk_state.get_loading_progress()
                
                # 아크 프로그레스 바 업데이트
                if hasattr(self, 'progress_arc'):
                    # 0-360도 범위로 변환 (0% = 0도, 100% = 360도)
                    arc_angle = int((progress / 100) * 360)
                    self.progress_arc.set_angles(0, arc_angle)
                
                # 진행률 텍스트 업데이트
                self.progress_label.set_text(f"{progress:.0f}%")
                
                # 세부 정보 업데이트 (리미트 스위치 기반 카운트)
                if hasattr(self, 'detail_label'):
                    loaded_count = self.current_disk_state.loaded_count
                    self.detail_label.set_text(f"{loaded_count}/15칸")
            
        except Exception as e:
            print(f"  ❌ 아크 프로그레스 바 업데이트 실패: {e}")
    
    def get_selected_disk(self):
        """선택된 디스크 번호 반환"""
        return self.selected_disk_index + 1  # 1, 2, 3
    
    def get_title(self):
        """화면 제목"""
        return "알약 충전"
    
    def get_button_hints(self):
        """버튼 힌트 (기호 사용)"""
        try:
            up_symbol = getattr(lv.SYMBOL, 'UP', '^')
            down_symbol = getattr(lv.SYMBOL, 'DOWN', 'v')
            prev_symbol = getattr(lv.SYMBOL, 'PREV', '<')
            ok_symbol = getattr(lv.SYMBOL, 'OK', '✓')
            return f"A:{up_symbol} B:{down_symbol} C:{prev_symbol} D:{ok_symbol}"
        except:
            return "A:^ B:v C:< D:✓"
    
    def get_voice_file(self):
        """안내 음성 파일"""
        return "wav_pill_loading_prompt.wav"
    
    def get_effect_file(self):
        """효과음 파일"""
        return "wav_select.wav"
    
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
        pass
    
    def update(self):
        """화면 업데이트"""
        pass
    
    def on_button_a(self):
        """버튼 A 처리 - 이전 화면으로 (복용 시간 설정 화면으로)"""
        if self.current_mode == 'selection':
            print("이전 화면으로 이동 (복용 시간 설정 화면)")
            
            # 복용 시간 설정 화면으로 이동
            if hasattr(self.screen_manager, 'screens') and 'dose_time' in self.screen_manager.screens:
                self.screen_manager.show_screen('dose_time')
            else:
                print("  📱 복용 시간 설정 화면이 없어서 현재 화면에 머물기")
        
        elif self.current_mode == 'loading':
            print("디스크 회전 기능 비활성화 - 리미트 스위치 기반 충전만 사용")
    
    def on_button_b(self):
        """버튼 B 처리 - 다음 화면으로 (메인 화면으로)"""
        if self.current_mode == 'selection':
            print("다음 화면으로 이동 (메인 화면)")
            
            # 메인 화면으로 이동
            if hasattr(self.screen_manager, 'screens') and 'main' in self.screen_manager.screens:
                self.screen_manager.show_screen('main')
            else:
                # 메인 화면이 없으면 동적으로 생성
                print("  📱 main 화면이 등록되지 않음. 동적 생성 중...")
                try:
                    from screens.main_screen_ui import MainScreen
                    main_screen = MainScreen(self.screen_manager)
                    self.screen_manager.register_screen('main', main_screen)
                    print("  ✅ main 화면 생성 및 등록 완료")
                    self.screen_manager.show_screen('main')
                    print("  📱 메인 화면으로 전환 완료")
                except Exception as e:
                    print(f"  ❌ 메인 화면 생성 실패: {e}")
                    print("  📱 메인 화면 생성 실패로 현재 화면에 머물기")
        
        elif self.current_mode == 'loading':
            print("디스크 회전 기능 비활성화 - 리미트 스위치 기반 충전만 사용")
    
    def on_button_c(self):
        """버튼 C 처리 - 디스크 선택 (알약 충전 서브 화면으로)"""
        if self.current_mode == 'selection':
            selected_disk = self.get_selected_disk()
            print(f"디스크 {selected_disk} 선택 - 충전 모드로 전환")
            
            # 충전 모드로 전환
            self.current_disk_state = self.disk_states[self.selected_disk_index]
            self.current_mode = 'loading'
            
            # 서브 화면 생성
            self._create_loading_sub_screen()
        
        elif self.current_mode == 'loading':
            print("디스크 충전 완료")
            
            # 디스크 선택 화면으로 돌아가기
            self._return_to_selection_mode()
    
    def on_button_d(self):
        """버튼 D 처리 - 디스크 선택 (디스크1, 2, 3 이동)"""
        if self.current_mode == 'selection':
            print("알약 충전 디스크 아래로 이동")
            
            # 무한 회전을 위해 인덱스 순환
            next_index = (self.selected_disk_index + 1) % len(self.disk_options)
            print(f"  📱 롤러 선택 업데이트: 인덱스 {next_index}")
            
            # 롤러 직접 조작 (애니메이션과 함께)
            try:
                self.disk_roller.set_selected(next_index, lv.ANIM.ON)
                print(f"  📱 롤러 애니메이션과 함께 설정 완료")
            except AttributeError:
                self.disk_roller.set_selected(next_index, 1)
                print(f"  📱 롤러 애니메이션 없이 설정 완료")
            
            # 강제 업데이트
            try:
                lv.timer_handler()
            except:
                pass
            
            self.selected_disk_index = next_index
            print(f"  ✅ 롤러 선택 업데이트 완료: {self.disk_options[self.selected_disk_index]}")
            
        elif self.current_mode == 'loading':
            print("알약 충전 실행 - 리미트 스위치 기반")
            
            # 충전 가능한지 확인
            if self.current_disk_state.can_load_more():
                disk_index = self.current_disk_state.disk_id - 1  # 0, 1, 2
                
                # 실제 모터 제어만 사용
                if self.motor_system and self.motor_system.motor_controller:
                    success = self._real_loading(disk_index)
                    if not success:
                        print("  📱 충전 작업이 완료되지 않음")
                else:
                    print("  ❌ 모터 시스템이 초기화되지 않음 - 충전 불가능")
            else:
                print("  📱 더 이상 충전할 칸이 없습니다")
                print("  🎉 디스크 충전 완료! (15/15칸)")
                # 충전 완료 - 수동으로 완료 버튼을 눌러야 함
                print("  📱 완료 버튼(C)을 눌러 디스크 선택 화면으로 돌아가세요")
    
    def _return_to_selection_mode(self):
        """디스크 선택 모드로 돌아가기"""
        print("  📱 디스크 선택 모드로 돌아가기")
        
        # 모드 변경
        self.current_mode = 'selection'
        
        # 기존 서브 화면 요소들 숨기기
        if hasattr(self, 'progress_arc'):
            self.progress_arc.set_style_opa(0, 0)
        if hasattr(self, 'progress_label'):
            self.progress_label.set_style_opa(0, 0)
        if hasattr(self, 'detail_label'):
            self.detail_label.set_style_opa(0, 0)
        
        # 원래 화면 복원
        if hasattr(self, 'disk_roller'):
            self.disk_roller.set_style_opa(255, 0)  # 다시 보이게
        
        # 제목과 버튼 힌트 복원
        if hasattr(self, 'title_text'):
            self.title_text.set_text("알약 충전")
        if hasattr(self, 'hints_text'):
            try:
                prev_symbol = getattr(lv.SYMBOL, 'PREV', '<')
                next_symbol = getattr(lv.SYMBOL, 'NEXT', '>')
                ok_symbol = getattr(lv.SYMBOL, 'OK', '✓')
                down_symbol = getattr(lv.SYMBOL, 'DOWN', 'v')
                self.hints_text.set_text(f"A:{prev_symbol} B:{next_symbol} C:{ok_symbol} D:{down_symbol}")
            except:
                self.hints_text.set_text("A:< B:> C:✓ D:v")
        
        # 화면 강제 업데이트
        try:
            lv.timer_handler()
        except:
            pass
    
    
    def _real_loading(self, disk_index):
        """실제 모터 제어를 통한 알약 충전 (리미트 스위치 엣지 감지 방식)"""
        print(f"  📱 실제 모터 제어: 디스크 {disk_index + 1} 충전 시작")
        
        try:
            if not self.motor_system or not self.motor_system.motor_controller:
                print("  ❌ 모터 시스템이 초기화되지 않음")
                return False
            
            if self.current_disk_state.start_loading():
                print(f"  📱 모터 회전 시작 (리미트 스위치 엣지 감지 3번까지)")
                
                # 리미트 스위치가 3번 감지될 때까지 계속 회전
                while self.current_disk_state.is_loading:
                    try:
                        # 리미트 스위치 상태 추적을 위한 변수
                        prev_limit_state = False
                        current_limit_state = False
                        
                        # 리미트 스위치 엣지 감지 (눌렸다가 떼어지는 순간) - 모터 우선순위
                        ui_update_counter = 0  # UI 업데이트 카운터
                        
                        while self.current_disk_state.is_loading:
                            # 1스텝씩 회전 (리미트 스위치 감지되어도 계속 회전) - 최우선 (반시계방향)
                            self.motor_system.motor_controller.step_motor_continuous(disk_index, -1, 1)
                            
                            # 현재 리미트 스위치 상태 확인
                            current_limit_state = self.motor_system.motor_controller.is_limit_switch_pressed(disk_index)
                            
                            # 엣지 감지: 이전에 눌려있었고 지금 떼어진 상태
                            if prev_limit_state and not current_limit_state:
                                print("  📱 리미트 스위치 엣지 감지 (눌렸다가 떼어짐), 카운트...")
                                
                                # 리미트 스위치 엣지 감지 시 충전 완료
                                loading_complete = self.current_disk_state.complete_loading()
                                
                                # UI 업데이트는 엣지 감지 시에만 (모터 성능 우선)
                                self._update_disk_visualization()
                                
                                # 3칸 충전이 완료되면 루프 종료
                                if loading_complete:
                                    print("  📱 3칸 충전 완료!")
                                    break
                                
                                # 다음 칸을 위해 리미트 스위치가 완전히 떼어질 때까지 대기
                                print("  📱 리미트 스위치가 완전히 떼어질 때까지 대기...")
                                while self.motor_system.motor_controller.is_limit_switch_pressed(disk_index):
                                    # 리미트 스위치 대기 중에도 모터는 계속 회전 (UI 업데이트 없음, 반시계방향)
                                    self.motor_system.motor_controller.step_motor_continuous(disk_index, -1, 1)
                                    time.sleep_ms(2)  # 더 짧은 지연으로 모터 성능 향상
                                
                                print("  📱 리미트 스위치 완전히 떼어짐, 다음 칸으로 이동...")
                                break  # 내부 루프 종료, 다음 칸으로
                            
                            # 상태 업데이트
                            prev_limit_state = current_limit_state
                            
                            # 모터 성능 우선 - UI 업데이트 최소화
                            ui_update_counter += 1
                            if ui_update_counter >= 100:  # 100번마다 UI 업데이트 (선택사항)
                                ui_update_counter = 0
                                # self._update_disk_visualization()  # 주석 처리로 UI 업데이트 비활성화
                            
                            # 최소 지연으로 모터 성능 최적화
                            time.sleep_ms(1)  # 5ms → 1ms로 단축
                    
                    except Exception as e:
                        print(f"  ❌ 모터 제어 중 오류: {e}")
                        break
                
                # 완전히 충전된 경우 확인
                if not self.current_disk_state.can_load_more():
                    print("  🎉 실제 모터: 디스크 충전 완료! (15/15칸)")
                    # 충전 완료 - 수동으로 완료 버튼을 눌러야 함
                    print("  📱 완료 버튼(C)을 눌러 디스크 선택 화면으로 돌아가세요")
                    return True
                
                return False
            else:
                print("  📱 실제 모터: 더 이상 충전할 수 없습니다")
                return False
                
        except Exception as e:
            print(f"  ❌ 실제 모터 충전 실패: {e}")
            return False
    
    def reset_disk_state(self, disk_index):
        """특정 디스크 상태 초기화"""
        try:
            if disk_index in self.disk_states:
                self.disk_states[disk_index] = DiskState(disk_index + 1)
                print(f"  📱 디스크 {disk_index + 1} 상태 초기화 완료")
                return True
            else:
                print(f"  ❌ 디스크 {disk_index + 1} 상태 초기화 실패: 인덱스 오류")
                return False
        except Exception as e:
            print(f"  ❌ 디스크 상태 초기화 실패: {e}")
            return False
    
    def get_disk_loading_status(self):
        """모든 디스크의 충전 상태 반환"""
        try:
            status = {}
            for i, disk_state in self.disk_states.items():
                status[f"disk_{i+1}"] = {
                    "loaded_count": disk_state.loaded_count,
                    "total_compartments": disk_state.total_compartments,
                    "progress_percent": disk_state.get_loading_progress(),
                    "is_loading": disk_state.is_loading,
                    "can_load_more": disk_state.can_load_more()
                }
            return status
        except Exception as e:
            print(f"  ❌ 디스크 상태 조회 실패: {e}")
            return {}
    
    def cleanup(self):
        """리소스 정리"""
        try:
            print(f"  📱 {self.screen_name} 리소스 정리 시작...")
            
            # 모터 시스템 정리
            if hasattr(self, 'motor_system') and self.motor_system:
                try:
                    # 모터 정지 등 필요한 정리 작업
                    pass
                except:
                    pass
            
            # 화면 객체 정리
            if hasattr(self, 'screen_obj') and self.screen_obj:
                try:
                    # LVGL 객체 정리
                    pass
                except:
                    pass
            
            print(f"  ✅ {self.screen_name} 리소스 정리 완료")
            
        except Exception as e:
            print(f"  ❌ {self.screen_name} 리소스 정리 실패: {e}")
    
    def get_screen_info(self):
        """화면 정보 반환"""
        return {
            "screen_name": self.screen_name,
            "current_mode": self.current_mode,
            "selected_disk": self.get_selected_disk() if self.current_mode == 'selection' else None,
            "disk_states": self.get_disk_loading_status(),
            "is_loading": self.is_loading,
            "loading_progress": self.loading_progress
        }
    
    def set_disk_loading_count(self, disk_index, count):
        """특정 디스크의 충전된 칸 수를 설정"""
        try:
            if disk_index in self.disk_states:
                if 0 <= count <= 15:
                    self.disk_states[disk_index].loaded_count = count
                    print(f"  📱 디스크 {disk_index + 1} 충전 칸 수를 {count}로 설정")
                    return True
                else:
                    print(f"  ❌ 잘못된 칸 수: {count} (0-15 범위)")
                    return False
            else:
                print(f"  ❌ 잘못된 디스크 인덱스: {disk_index}")
                return False
        except Exception as e:
            print(f"  ❌ 디스크 충전 칸 수 설정 실패: {e}")
            return False
    
    def is_disk_fully_loaded(self, disk_index):
        """특정 디스크가 완전히 충전되었는지 확인"""
        try:
            if disk_index in self.disk_states:
                return self.disk_states[disk_index].loaded_count >= 15
            return False
        except Exception as e:
            print(f"  ❌ 디스크 충전 상태 확인 실패: {e}")
            return False
    
    def get_next_available_disk(self):
        """충전 가능한 다음 디스크 반환"""
        try:
            for i in range(3):
                if self.disk_states[i].can_load_more():
                    return i
            return None  # 모든 디스크가 충전됨
        except Exception as e:
            print(f"  ❌ 다음 사용 가능한 디스크 조회 실패: {e}")
            return None
    
    def reset_all_disks(self):
        """모든 디스크 상태 초기화"""
        try:
            for i in range(3):
                self.disk_states[i] = DiskState(i + 1)
            print("  📱 모든 디스크 상태 초기화 완료")
            return True
        except Exception as e:
            print(f"  ❌ 모든 디스크 상태 초기화 실패: {e}")
            return False