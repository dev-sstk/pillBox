"""
알약 충전 화면
알약을 디스크에 충전하는 화면
"""

import time
import math
import json
import lvgl as lv
from ui_style import UIStyle

class DiskState:
    """디스크 상태 관리 클래스 (리미트 스위치 기반)"""
    
    def __init__(self, disk_id):
        self.disk_id = disk_id
        self.total_compartments = 15  # 총 15칸
        self.compartments_per_loading = 3  # 한 번에 3칸씩 충전 (리미트 스위치 3번 감지)
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
        
        # 식사 시간과 디스크 매핑
        self.meal_to_disk_mapping = {
            'breakfast': 0,  # 아침 → 디스크 1
            'lunch': 1,      # 점심 → 디스크 2
            'dinner': 2      # 저녁 → 디스크 3
        }
        
        # 설정된 복용 시간 정보 (dose_time 화면에서 전달받음)
        self.dose_times = []
        self.selected_meals = []
        self.available_disks = []  # 충전 가능한 디스크 목록
        
        # 순차적 충전 관련 변수
        self.sequential_mode = False  # 순차적 충전 모드 여부
        self.current_sequential_index = 0  # 현재 충전 중인 디스크 인덱스
        self.sequential_disks = []  # 순차적 충전할 디스크 목록
        
        # 디스크 상태 관리
        self.disk_states = {}
        self.disk_states_file = "/disk_states.json"  # 저장 파일 경로
        
        # 저장된 상태 불러오기 (있으면)
        self._load_disk_states()
        
        # 불러온 상태가 없으면 새로 생성
        for i in range(3):
            if i not in self.disk_states:
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
        
        # 화면 생성 (복용 시간 정보가 설정된 후에 생성)
        # self._create_modern_screen()  # update_dose_times 후에 생성
        
        print(f"✅ {self.screen_name} 화면 초기화 완료")
    
    def show(self):
        """화면 표시"""
        try:
            print(f"📱 {self.screen_name} 화면 표시 시작...")
            
            # 화면이 없으면 기본 화면 생성
            if not hasattr(self, 'screen_obj') or not self.screen_obj:
                print(f"📱 화면이 없음 - 기본 화면 생성")
                self._create_modern_screen()
            
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
                
                # 순차적 충전 모드인 경우 이미 충전 화면이 생성됨
                if self.sequential_mode and self.current_mode == 'loading':
                    print(f"📱 순차적 충전 모드 - 충전 화면이 이미 생성됨")
            else:
                print(f"❌ {self.screen_name} 화면 객체가 없음")
                
        except Exception as e:
            print(f"  ❌ {self.screen_name} 화면 표시 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def update_dose_times(self, dose_times):
        """복용 시간 정보 업데이트 및 충전 가능한 디스크 결정"""
        try:
            print(f"📱 복용 시간 정보 업데이트 시작")
            self.dose_times = dose_times or []
            
            # 선택된 식사 시간 추출
            self.selected_meals = []
            for dose_info in self.dose_times:
                if isinstance(dose_info, dict) and 'meal_key' in dose_info:
                    self.selected_meals.append(dose_info['meal_key'])
            
            print(f"📱 설정된 복용 시간: {len(self.dose_times)}개")
            for dose_info in self.dose_times:
                if isinstance(dose_info, dict):
                    print(f"  - {dose_info['meal_name']}: {dose_info['time']}")
            
            print(f"📱 선택된 식사 시간: {self.selected_meals}")
            
            # 충전 가능한 디스크 결정
            self._determine_available_disks()
            
            # 순차적 충전 모드 결정
            self._determine_sequential_mode()
            
            # 화면 생성 (복용 시간 정보 설정 후)
            if not hasattr(self, 'screen_obj') or not self.screen_obj:
                print(f"📱 복용 시간 정보 설정 완료 - 화면 생성 시작")
                self._create_modern_screen()
                print(f"📱 화면 생성 완료")
            
            print(f"✅ 복용 시간 정보 업데이트 완료")
            
        except Exception as e:
            print(f"❌ 복용 시간 정보 업데이트 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _determine_available_disks(self):
        """선택된 식사 시간에 따라 충전 가능한 디스크 결정"""
        try:
            self.available_disks = []
            
            if not self.selected_meals:
                # 선택된 식사 시간이 없으면 모든 디스크 충전 가능
                self.available_disks = [0, 1, 2]  # 디스크 1, 2, 3
                print(f"📱 선택된 식사 시간 없음 - 모든 디스크 충전 가능")
            elif len(self.selected_meals) == 1:
                # 1개만 선택했으면 모든 디스크 충전 가능
                self.available_disks = [0, 1, 2]  # 디스크 1, 2, 3
                print(f"📱 1개 식사 시간 선택 - 모든 디스크 충전 가능")
            else:
                # 2개 이상 선택했으면 해당 디스크만 충전 가능
                for meal_key in self.selected_meals:
                    if meal_key in self.meal_to_disk_mapping:
                        disk_index = self.meal_to_disk_mapping[meal_key]
                        self.available_disks.append(disk_index)
                
                print(f"📱 {len(self.selected_meals)}개 식사 시간 선택 - 제한된 디스크 충전")
                for disk_index in self.available_disks:
                    meal_name = self._get_meal_name_by_disk(disk_index)
                    print(f"  - 디스크 {disk_index + 1}: {meal_name}")
            
        except Exception as e:
            print(f"❌ 충전 가능한 디스크 결정 실패: {e}")
            # 오류 시 모든 디스크 허용
            self.available_disks = [0, 1, 2]
    
    def _get_meal_name_by_disk(self, disk_index):
        """디스크 인덱스로 식사 시간 이름 반환"""
        for meal_key, disk_idx in self.meal_to_disk_mapping.items():
            if disk_idx == disk_index:
                meal_names = {'breakfast': '아침', 'lunch': '점심', 'dinner': '저녁'}
                return meal_names.get(meal_key, '알 수 없음')
        return '알 수 없음'
    
    def _determine_sequential_mode(self):
        """순차적 충전 모드 결정"""
        try:
            if len(self.selected_meals) >= 2:
                # 2개 이상 선택했으면 순차적 충전 모드
                self.sequential_mode = True
                self.sequential_disks = []
                
                # 아침, 점심, 저녁 순서로 정렬
                meal_order = ['breakfast', 'lunch', 'dinner']
                for meal_key in meal_order:
                    if meal_key in self.selected_meals:
                        disk_index = self.meal_to_disk_mapping[meal_key]
                        self.sequential_disks.append(disk_index)
                
                self.current_sequential_index = 0
                print(f"📱 순차적 충전 모드 활성화: {len(self.sequential_disks)}개 디스크")
                for i, disk_index in enumerate(self.sequential_disks):
                    meal_name = self._get_meal_name_by_disk(disk_index)
                    print(f"  {i+1}. 디스크 {disk_index + 1} ({meal_name})")
            else:
                # 1개 이하 선택했으면 개별 선택 모드
                self.sequential_mode = False
                self.sequential_disks = []
                self.current_sequential_index = 0
                print(f"📱 개별 선택 모드 활성화")
                
        except Exception as e:
            print(f"❌ 순차적 충전 모드 결정 실패: {e}")
            self.sequential_mode = False
            self.sequential_disks = []
    
    def start_sequential_loading(self):
        """순차적 충전 시작"""
        try:
            if not self.sequential_mode or not self.sequential_disks:
                print(f"❌ 순차적 충전 모드가 아니거나 디스크 목록이 비어있음")
                return False
            
            print(f"📱 순차적 충전 시작: {len(self.sequential_disks)}개 디스크")
            self.current_sequential_index = 0
            self._start_current_disk_loading()
            return True
            
        except Exception as e:
            print(f"❌ 순차적 충전 시작 실패: {e}")
            return False
    
    def _start_current_disk_loading(self):
        """현재 디스크 충전 시작"""
        try:
            if self.current_sequential_index >= len(self.sequential_disks):
                print(f"📱 모든 디스크 충전 완료!")
                self._complete_sequential_loading()
                return
            
            current_disk_index = self.sequential_disks[self.current_sequential_index]
            meal_name = self._get_meal_name_by_disk(current_disk_index)
            
            print(f"📱 {meal_name} 디스크 충전 시작 ({self.current_sequential_index + 1}/{len(self.sequential_disks)})")
            
            # 현재 디스크로 설정
            self.selected_disk_index = current_disk_index
            self.current_disk_state = self.disk_states[current_disk_index]
            self.current_mode = 'loading'
            
            # 디스크 상태 초기화 (새로운 디스크로 전환 시)
            if self.current_sequential_index > 0:  # 첫 번째 디스크가 아닌 경우
                print(f"  📱 새로운 디스크로 전환 - 디스크 상태 초기화")
                # 디스크 상태를 현재 로드된 상태로 초기화
                self.current_disk_state.loaded_count = self.current_disk_state.loaded_count  # 현재 상태 유지
                print(f"  📱 디스크 {current_disk_index} 현재 상태: {self.current_disk_state.loaded_count}칸")
            
            # 화면 업데이트 (서브 화면 생성 대신)
            self._update_loading_screen()
            
        except Exception as e:
            print(f"❌ 현재 디스크 충전 시작 실패: {e}")
    
    def _complete_current_disk_loading(self):
        """현재 디스크 충전 완료 후 다음 디스크로"""
        try:
            print(f"📱 현재 디스크 충전 완료")
            self.current_sequential_index += 1
            
            if self.current_sequential_index < len(self.sequential_disks):
                # 다음 디스크로
                print(f"📱 다음 디스크로 이동")
                self._start_current_disk_loading()
            else:
                # 모든 디스크 완료
                print(f"📱 모든 디스크 충전 완료!")
                self._complete_sequential_loading()
                
        except Exception as e:
            print(f"❌ 현재 디스크 충전 완료 처리 실패: {e}")
    
    def _complete_sequential_loading(self):
        """순차적 충전 완료"""
        try:
            print(f"📱 순차적 충전 완료 - 메인 화면으로 이동")
            
            # 메인 화면으로 이동
            if hasattr(self.screen_manager, 'screens') and 'main' in self.screen_manager.screens:
                self.screen_manager.show_screen('main')
            else:
                print(f"📱 메인 화면이 없어서 현재 화면에 머물기")
            
        except Exception as e:
            print(f"❌ 순차적 충전 완료 처리 실패: {e}")
    
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
        
        # 순차적 충전 모드인 경우 바로 충전 화면 생성
        if self.sequential_mode:
            print(f"  📱 순차적 충전 모드 - 바로 충전 화면 생성")
            self._create_loading_screen_directly()
        else:
            # 개별 선택 모드인 경우 기존 방식
            print(f"  📱 개별 선택 모드 - 기존 화면 생성")
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
    
    def _create_loading_screen_directly(self):
        """순차적 충전 모드에서 바로 충전 화면을 메인 화면으로 생성"""
        try:
            print(f"  📱 직접 충전 화면 생성 시작...")
            
            # 첫 번째 디스크 설정
            if self.sequential_disks:
                self.selected_disk_index = self.sequential_disks[0]
                self.current_disk_state = self.disk_states[self.selected_disk_index]
                self.current_mode = 'loading'
                
                # 제목 생성
                meal_name = self._get_meal_name_by_disk(self.selected_disk_index)
                self.title_text = lv.label(self.screen_obj)
                self.title_text.set_text(f"{meal_name}약 충전")
                self.title_text.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
                self.title_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
                self.title_text.align(lv.ALIGN.TOP_MID, 0, 10)
                
                # 한국어 폰트 적용
                korean_font = getattr(lv, "font_notosans_kr_regular", None)
                if korean_font:
                    self.title_text.set_style_text_font(korean_font, 0)
                
                # 아크 프로그레스 바 생성
                self.progress_arc = lv.arc(self.screen_obj)
                self.progress_arc.set_size(60, 60)
                self.progress_arc.align(lv.ALIGN.CENTER, -30, 10)
                self.progress_arc.set_bg_angles(0, 360)
                
                # 현재 충전 상태를 반영한 각도 설정
                progress = self.current_disk_state.get_loading_progress()
                arc_angle = int((progress / 100) * 360)
                self.progress_arc.set_angles(0, arc_angle)
                self.progress_arc.set_rotation(270)
                
                # 아크 스타일 설정
                self.progress_arc.set_style_arc_width(8, 0)  # 배경 아크
                self.progress_arc.set_style_arc_color(lv.color_hex(0xE5E5EA), 0)  # 배경 회색
                self.progress_arc.set_style_arc_width(8, lv.PART.INDICATOR)  # 진행 아크
                self.progress_arc.set_style_arc_color(lv.color_hex(0x00C9A7), lv.PART.INDICATOR)  # 진행 민트색
                
                # 아크 노브 색상 설정 (아크와 동일한 민트색)
                try:
                    self.progress_arc.set_style_bg_color(lv.color_hex(0x00C9A7), lv.PART.KNOB)
                    self.progress_arc.set_style_bg_opa(255, lv.PART.KNOB)
                    print(f"  ✅ 아크 노브 색상 설정 완료 (민트색)")
                except AttributeError:
                    print(f"  ⚠️ lv.PART.KNOB 지원 안됨, 건너뛰기")
                
                # 진행률 텍스트 라벨
                self.progress_label = lv.label(self.screen_obj)
                self.progress_label.set_text(f"{progress:.0f}%")
                self.progress_label.align(lv.ALIGN.CENTER, -30, 10)
                self.progress_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
                self.progress_label.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
                
                if korean_font:
                    self.progress_label.set_style_text_font(korean_font, 0)
                
                # 세부 정보 라벨
                self.detail_label = lv.label(self.screen_obj)
                loaded_count = self.current_disk_state.loaded_count
                self.detail_label.set_text(f"{loaded_count}/15칸")
                self.detail_label.align(lv.ALIGN.CENTER, 30, 10)
                self.detail_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
                self.detail_label.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
                
                if korean_font:
                    self.detail_label.set_style_text_font(korean_font, 0)
                
                # 버튼 힌트 (lv.SYMBOL.DOWNLOAD 사용)
                self.hints_text = lv.label(self.screen_obj)
                self.hints_text.set_text(f"A:- B:- C:- D:{lv.SYMBOL.DOWNLOAD}")
                self.hints_text.align(lv.ALIGN.BOTTOM_MID, 0, -2)
                self.hints_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
                self.hints_text.set_style_text_color(lv.color_hex(0x8E8E93), 0)
                # lv 기본 폰트 사용 (한국어 폰트 적용하지 않음) - dose_count_screen과 동일
                
                print(f"  ✅ 직접 충전 화면 생성 완료: {meal_name}약 충전")
                
        except Exception as e:
            print(f"  ❌ 직접 충전 화면 생성 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _update_loading_screen(self):
        """순차적 충전 모드에서 다음 디스크로 화면 업데이트"""
        try:
            print(f"  📱 충전 화면 업데이트 시작...")
            
            # 제목 업데이트
            if hasattr(self, 'title_text'):
                meal_name = self._get_meal_name_by_disk(self.selected_disk_index)
                self.title_text.set_text(f"{meal_name}약 충전")
                print(f"  ✅ 제목 업데이트 완료: {meal_name}약 충전")
            
            # 진행률 업데이트
            if hasattr(self, 'progress_arc') and hasattr(self, 'progress_label'):
                progress = self.current_disk_state.get_loading_progress()
                arc_angle = int((progress / 100) * 360)
                self.progress_arc.set_angles(0, arc_angle)
                self.progress_label.set_text(f"{progress:.0f}%")
                print(f"  ✅ 진행률 업데이트 완료: {progress:.0f}%")
            
            # 세부 정보 업데이트
            if hasattr(self, 'detail_label'):
                loaded_count = self.current_disk_state.loaded_count
                self.detail_label.set_text(f"{loaded_count}/15칸")
                print(f"  ✅ 세부 정보 업데이트 완료: {loaded_count}/15칸 (디스크 {self.selected_disk_index})")
            
            print(f"  ✅ 충전 화면 업데이트 완료")
            
        except Exception as e:
            print(f"  ❌ 충전 화면 업데이트 실패: {e}")
            import sys
            sys.print_exception(e)
    
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
            if self.sequential_mode:
                # 순차적 충전 모드에서는 디스크 선택 영역을 생성하지 않음
                print("  📱 순차적 충전 모드 - 디스크 선택 영역 생략")
                self.disk_label = None
                self.disk_roller = None
                return
            
            # 개별 선택 모드에서만 디스크 선택 영역 생성
            # 디스크 선택 안내 텍스트
            self.disk_label = lv.label(self.main_container)
            self.disk_label.set_text("디스크를 선택하세요")
            self.disk_label.align(lv.ALIGN.CENTER, 0, -10)
            self.disk_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            self.disk_label.set_style_text_color(lv.color_hex(0x333333), 0)
            
            # 한국어 폰트 적용
            korean_font = getattr(lv, "font_notosans_kr_regular", None)
            if korean_font:
                self.disk_label.set_style_text_font(korean_font, 0)
            
            # 디스크 옵션 생성
            self._update_disk_options()
            
            # 디스크 선택 롤러 생성
            self.disk_roller = lv.roller(self.main_container)
            self.disk_roller.set_size(120, 50)
            self.disk_roller.align(lv.ALIGN.CENTER, 0, 10)
            self.disk_roller.set_options(self.disk_options_text, lv.roller.MODE.INFINITE)
            self.disk_roller.set_selected(0, True)  # 첫 번째 디스크 선택
            
            # 롤러 스타일 설정
            self.disk_roller.set_style_bg_color(lv.color_hex(0xF2F2F7), 0)
            self.disk_roller.set_style_border_width(0, 0)
            self.disk_roller.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
            
            # 한국어 폰트 적용
            if korean_font:
                self.disk_roller.set_style_text_font(korean_font, 0)
            
            # 롤러 선택된 항목 스타일 - 로고 색상(민트)
            try:
                self.disk_roller.set_style_bg_color(lv.color_hex(0x00C9A7), lv.PART.SELECTED)
                self.disk_roller.set_style_bg_opa(255, lv.PART.SELECTED)
                self.disk_roller.set_style_text_color(lv.color_hex(0xFFFFFF), lv.PART.SELECTED)
                self.disk_roller.set_style_radius(6, lv.PART.SELECTED)
            except AttributeError:
                pass
            
            print("  ✅ 디스크 선택 영역 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 디스크 선택 영역 생성 실패: {e}")
    
    def _update_disk_options(self):
        """충전 가능한 디스크 옵션 업데이트"""
        try:
            if not hasattr(self, 'available_disks') or not self.available_disks:
                # 기본값: 모든 디스크
                self.available_disks = [0, 1, 2]
            
            # 디스크 옵션 텍스트 생성
            disk_options = []
            for disk_index in self.available_disks:
                meal_name = self._get_meal_name_by_disk(disk_index)
                if meal_name != '알 수 없음':
                    disk_options.append(f"{meal_name} 디스크")
                else:
                    disk_options.append(f"디스크 {disk_index + 1}")
            
            self.disk_options_text = "\n".join(disk_options)
            print(f"  📱 디스크 옵션 업데이트: {self.disk_options_text}")
            
        except Exception as e:
            print(f"  ❌ 디스크 옵션 업데이트 실패: {e}")
            # 기본값으로 설정
            self.disk_options_text = "디스크 1\n디스크 2\n디스크 3"
            self.available_disks = [0, 1, 2]
    
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
    
    def _create_disk_selection_area_old(self):
        """디스크 선택 영역 생성 (기존 버전 - 사용 안함)"""
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
            
            # 롤러 선택된 항목 스타일 - 로고 색상(민트)
            try:
                self.disk_roller.set_style_bg_color(lv.color_hex(0x00C9A7), lv.PART.SELECTED)  # 민트색 (로고와 동일)
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
            
            # 버튼 힌트 설정 (lv.SYMBOL.DOWNLOAD 사용)
            self.hints_text.set_text(f"A:- B:- C:- D:{lv.SYMBOL.DOWNLOAD}")
            print(f"  ✅ 버튼 힌트 설정 완료: A:- B:- C:- D:{lv.SYMBOL.DOWNLOAD}")
            
            self.hints_text.set_style_text_color(lv.color_hex(0x8E8E93), 0)  # 모던 라이트 그레이
            # lv 기본 폰트 사용 (한국어 폰트 적용하지 않음) - dose_count_screen과 동일
            
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
            if hasattr(self, 'disk_roller') and self.disk_roller:
                self.disk_roller.set_style_opa(0, 0)  # 투명하게
                print(f"  ✅ 롤러 숨김 완료")
            else:
                print(f"  📱 롤러가 없음 (순차적 충전 모드)")
            
            # 제목 업데이트
            print(f"  📱 제목 업데이트...")
            if hasattr(self, 'title_text'):
                meal_name = self._get_meal_name_by_disk(self.selected_disk_index)
                self.title_text.set_text(f"{meal_name}약 충전")
                print(f"  ✅ 제목 업데이트 완료: {meal_name}약 충전")
            
            # 아크 프로그레스 바 생성 (왼쪽으로 이동, 아래로 10픽셀)
            print(f"  📱 아크 프로그레스 바 생성...")
            self.progress_arc = lv.arc(self.screen_obj)
            self.progress_arc.set_size(60, 60)
            self.progress_arc.align(lv.ALIGN.CENTER, -30, 10)
            print(f"  ✅ 아크 생성 및 위치 설정 완료")
            
            # 아크 설정 (270도에서 시작하여 시계방향으로)
            print(f"  📱 아크 설정...")
            self.progress_arc.set_bg_angles(0, 360)
            
            # 현재 충전 상태를 반영한 각도 설정
            progress = self.current_disk_state.get_loading_progress()
            arc_angle = int((progress / 100) * 360)
            self.progress_arc.set_angles(0, arc_angle)  # 저장된 상태 반영
            print(f"  📱 아크 초기 각도: {arc_angle}도 (진행률: {progress:.0f}%)")
            
            self.progress_arc.set_rotation(270)  # 12시 방향에서 시작
            print(f"  ✅ 아크 각도 설정 완료")
            
            # 아크 스타일 설정
            print(f"  📱 아크 스타일 설정...")
            self.progress_arc.set_style_arc_width(6, 0)  # 배경 아크 두께
            self.progress_arc.set_style_arc_color(lv.color_hex(0xE0E0E0), 0)  # 배경 회색
            self.progress_arc.set_style_arc_width(6, lv.PART.INDICATOR)  # 진행 아크 두께
            self.progress_arc.set_style_arc_color(lv.color_hex(0x00C9A7), lv.PART.INDICATOR)  # 진행 민트색
            
            # 아크 끝부분 동그라미(knob) 스타일 - 민트색으로 설정
            try:
                self.progress_arc.set_style_bg_color(lv.color_hex(0x00C9A7), lv.PART.KNOB)  # 민트색
                self.progress_arc.set_style_bg_opa(255, lv.PART.KNOB)
                print(f"  ✅ 아크 knob 스타일 설정 완료 (민트색)")
            except AttributeError:
                print(f"  ⚠️ lv.PART.KNOB 지원 안됨, 건너뛰기")
            
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
                    self.hints_text.set_text(f"A:- B:- C:- D:{lv.SYMBOL.DOWNLOAD}")
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
            
            # ⚡ LVGL 화면 갱신 제거 (모터 성능 우선)
            # import lvgl as lv
            # lv.timer_handler()
            
            # ⚡ 파일 저장 제거 (매 칸마다 저장하지 않음, 3칸 완료 후에만 저장)
            # self._save_disk_states()
            
        except Exception as e:
            print(f"  ❌ 아크 프로그레스 바 업데이트 실패: {e}")
    
    def get_selected_disk(self):
        """선택된 디스크 번호 반환 (실제 디스크 인덱스)"""
        try:
            if hasattr(self, 'disk_roller') and self.disk_roller:
                # 롤러에서 선택된 인덱스 가져오기
                roller_selected = self.disk_roller.get_selected()
                
                # available_disks에서 실제 디스크 인덱스 가져오기
                if roller_selected < len(self.available_disks):
                    actual_disk_index = self.available_disks[roller_selected]
                    self.selected_disk_index = actual_disk_index
                    return actual_disk_index + 1  # 1, 2, 3
                else:
                    print(f"  ❌ 잘못된 롤러 선택 인덱스: {roller_selected}")
                    return 1  # 기본값
            else:
                # 롤러가 없으면 기본값
                return self.selected_disk_index + 1
        except Exception as e:
            print(f"  ❌ 선택된 디스크 가져오기 실패: {e}")
            return 1  # 기본값
    
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
        print(f"🔘 버튼 B 클릭됨 - 현재 모드: {self.current_mode}")
        
        if self.current_mode == 'selection':
            print("다음 화면으로 이동 (메인 화면)")
            
            # 화면 매니저 상태 확인
            print(f"  📱 화면 매니저 존재: {hasattr(self.screen_manager, 'screens')}")
            if hasattr(self.screen_manager, 'screens'):
                print(f"  📱 등록된 화면들: {list(self.screen_manager.screens.keys())}")
                print(f"  📱 main 화면 등록됨: {'main' in self.screen_manager.screens}")
            
            # 메인 화면으로 이동
            if hasattr(self.screen_manager, 'screens') and 'main' in self.screen_manager.screens:
                print("  📱 기존 main 화면으로 이동 시도...")
                success = self.screen_manager.show_screen('main')
                print(f"  📱 화면 전환 결과: {success}")
            else:
                # 메인 화면이 없으면 동적으로 생성
                print("  📱 main 화면이 등록되지 않음. 동적 생성 중...")
                try:
                    from screens.main_screen import MainScreen
                    main_screen = MainScreen(self.screen_manager)
                    self.screen_manager.register_screen('main', main_screen)
                    print("  ✅ main 화면 생성 및 등록 완료")
                    success = self.screen_manager.show_screen('main')
                    print(f"  📱 메인 화면으로 전환 완료: {success}")
                except Exception as e:
                    print(f"  ❌ 메인 화면 생성 실패: {e}")
                    print("  📱 메인 화면 생성 실패로 현재 화면에 머물기")
        
        elif self.current_mode == 'loading':
            print("디스크 회전 기능 비활성화 - 리미트 스위치 기반 충전만 사용")
    
    def on_button_c(self):
        """버튼 C 처리 - 디스크 선택 (알약 충전 서브 화면으로)"""
        if self.current_mode == 'selection':
            if self.sequential_mode:
                # 순차적 충전 모드 - 바로 첫 번째 디스크 충전 시작
                print(f"순차적 충전 시작")
                self.start_sequential_loading()
            else:
                # 개별 선택 모드
                selected_disk = self.get_selected_disk()
                print(f"디스크 {selected_disk} 선택 - 충전 모드로 전환")
                
                # 충전 모드로 전환
                self.current_disk_state = self.disk_states[self.selected_disk_index]
                self.current_mode = 'loading'
                
                # 서브 화면 생성
                self._create_loading_sub_screen()
        
        elif self.current_mode == 'loading':
            print("디스크 충전 완료")
            
            if self.sequential_mode:
                # 순차적 충전 모드에서 15칸이 모두 충전된 경우에만 다음 디스크로
                if self.current_disk_state.loaded_count >= 15:
                    print(f"📱 디스크 {self.selected_disk_index} 15칸 완료 - 다음 디스크로 이동")
                    self._complete_current_disk_loading()
                else:
                    print(f"📱 디스크 {self.selected_disk_index} {self.current_disk_state.loaded_count}/15칸 - 아직 완료되지 않음")
            else:
                # 개별 선택 모드에서 디스크 선택 화면으로 돌아가기
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
            self.hints_text.set_text(f"A:- B:- C:- D:{lv.SYMBOL.DOWNLOAD}")
        
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
            
            # ⚡ 충전 시작 전 모든 모터 코일 OFF (전력 소모 방지)
            print(f"  ⚡ 충전 시작 전 모든 모터 코일 OFF")
            self.motor_system.motor_controller.stop_all_motors()
            
            if self.current_disk_state.start_loading():
                print(f"  📱 모터 회전 시작 (리미트 스위치 눌림 감지 3번까지)")
                
                # 리미트 스위치 상태 추적 변수 (한 번만 초기화)
                prev_limit_state = False
                current_limit_state = False
                step_count = 0
                max_steps = 5000  # 최대 5000스텝 후 강제 종료 (안전장치)
                
                # 초기 리미트 스위치 상태 확인
                motor_index = disk_index + 1  # disk_index는 0,1,2이지만 모터 번호는 1,2,3이므로 +1
                current_limit_state = self.motor_system.motor_controller.is_limit_switch_pressed(motor_index)
                print(f"  📱 초기 리미트 스위치 상태: {'눌림' if current_limit_state else '안눌림'}")
                
                # 초기 상태가 눌린 경우 첫 번째 감지를 무시하기 위한 플래그
                skip_first_detection = current_limit_state
                
                try:
                    # 단일 루프로 3칸 모두 처리
                    while self.current_disk_state.is_loading and step_count < max_steps:
                        step_count += 1
                        
                        # 100스텝마다 진행 상황 출력
                        if step_count % 100 == 0:
                            print(f"  📍 충전 진행 중... 스텝 {step_count}, 현재 상태: {self.current_disk_state.loaded_count}칸")
                        
                        # 1스텝씩 회전 (리미트 스위치 감지되어도 계속 회전) - 반시계방향
                        # disk_index는 0,1,2이지만 모터 번호는 1,2,3이므로 +1
                        motor_index = disk_index + 1
                        
                        # 100스텝마다 모터 동작 확인
                        if step_count % 100 == 0:
                            print(f"  🔧 모터 {motor_index} 회전 시도 (스텝 {step_count})")
                        
                        success = self.motor_system.motor_controller.step_motor_continuous(motor_index, -1, 1)
                        if not success:
                            print(f"  ❌ 모터 {motor_index} 회전 실패 (스텝 {step_count})")
                            break
                        
                        # 현재 리미트 스위치 상태 확인 (엣지 감지 정확성 위해 매 스텝 체크)
                        # disk_index는 0,1,2이지만 모터 번호는 1,2,3이므로 +1
                        current_limit_state = self.motor_system.motor_controller.is_limit_switch_pressed(motor_index)
                        
                        # 리미트 스위치 눌림 감지: 이전에 안눌려있었고 지금 눌린 상태
                        if not prev_limit_state and current_limit_state:
                            # 초기 상태가 눌린 경우 첫 번째 감지를 무시
                            if skip_first_detection:
                                print(f"  ⏭️ 첫 번째 리미트 스위치 감지 무시 (초기 상태) - 스텝 {step_count}")
                                skip_first_detection = False  # 다음부터는 정상 감지
                            else:
                                print(f"  🔘 리미트 스위치 눌림 감지! ({self.current_disk_state.loaded_count + 1}칸) - 스텝 {step_count}")
                                # 리미트 스위치 눌림 감지 시 충전 완료 (데이터만 업데이트, UI는 주기적으로)
                                loading_complete = self.current_disk_state.complete_loading()
                                
                                # ⚡ UI 업데이트 제거 - 200스텝마다 갱신으로 충분 (끊김 완전 제거)
                                # self._update_disk_visualization()
                                
                                # 3칸 충전이 완료되면 루프 종료
                                if loading_complete:
                                    print(f"  ✅ 3칸 충전 완료! 총 {self.current_disk_state.loaded_count}칸")
                                    # ✅ 3칸 완료 후 UI 최종 업데이트 & 파일 저장
                                    self._update_disk_visualization()  # 최종 상태 반영
                                    self._save_disk_states()
                                    
                                    # 15칸 충전 완료 시 자동으로 다음 디스크로 넘어가기
                                    if self.current_disk_state.loaded_count >= 15:
                                        if self.sequential_mode:
                                            print(f"  📱 15칸 충전 완료 - 자동으로 다음 디스크로 이동")
                                            self._complete_current_disk_loading()
                                    else:
                                        print(f"  📱 3칸 충전 완료 - 다음 3칸 충전을 위해 D버튼을 눌러주세요")
                                    
                                    break
                        
                        # 상태 업데이트 (매번 업데이트, 리셋 안함!)
                        prev_limit_state = current_limit_state
                        
                        # ⚡ 최고 성능 - UI 업데이트 완전 제거 (끊김 0%)
                        # 모터 회전 중에는 UI 업데이트 안함, 3칸 완료 후에만 최종 업데이트
                        # 이렇게 하면 완전히 끊김 없는 부드러운 회전 가능
                        pass
                    
                    # 안전장치: 최대 스텝 수에 도달한 경우
                    if step_count >= max_steps:
                        print(f"  ⚠️ 최대 스텝 수 ({max_steps}) 도달, 충전 강제 종료")
                        self.current_disk_state.is_loading = False
                        # 현재까지의 진행 상황 저장
                        self._update_disk_visualization()
                        self._save_disk_states()
                
                except Exception as e:
                    print(f"  ❌ 모터 제어 중 오류: {e}")
                    # 오류 발생 시에도 모터 정지
                    self.motor_system.motor_controller.stop_motor(motor_index)
                    return False
                
                # ⚡ 충전 완료 후 모터 코일 OFF (전력 소모 방지)
                print(f"  ⚡ 충전 완료, 모터 {motor_index} 코일 OFF")
                self.motor_system.motor_controller.stop_motor(motor_index)
                
                # 완전히 충전된 경우 확인
                if not self.current_disk_state.can_load_more():
                    print("  🎉 실제 모터: 디스크 충전 완료! (15/15칸)")
                    # 충전 완료 - 수동으로 완료 버튼을 눌러야 함
                    print("  📱 완료 버튼(C)을 눌러 디스크 선택 화면으로 돌아가세요")
                    return True
                
                return True
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
                # 초기화 후 파일에 저장
                self._save_disk_states()
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
                    # 설정 후 파일에 저장
                    self._save_disk_states()
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
            # 초기화 후 파일에 저장
            self._save_disk_states()
            return True
        except Exception as e:
            print(f"  ❌ 모든 디스크 상태 초기화 실패: {e}")
            return False
    
    def _save_disk_states(self):
        """디스크 충전 상태를 파일에 저장"""
        try:
            config = {
                'disk_0_loaded': self.disk_states[0].loaded_count,
                'disk_1_loaded': self.disk_states[1].loaded_count,
                'disk_2_loaded': self.disk_states[2].loaded_count,
                'saved_at': time.time()
            }
            
            with open(self.disk_states_file, 'w') as f:
                json.dump(config, f)
            
            print(f"  💾 디스크 충전 상태 저장됨: {self.disk_states[0].loaded_count}, {self.disk_states[1].loaded_count}, {self.disk_states[2].loaded_count}")
            
        except Exception as e:
            print(f"  ❌ 디스크 충전 상태 저장 실패: {e}")
    
    def _load_disk_states(self):
        """저장된 디스크 충전 상태 불러오기"""
        try:
            with open(self.disk_states_file, 'r') as f:
                config = json.load(f)
            
            # 불러온 상태로 디스크 생성
            for i in range(3):
                self.disk_states[i] = DiskState(i + 1)
                loaded_count = config.get(f'disk_{i}_loaded', 0)
                self.disk_states[i].loaded_count = loaded_count
            
            print(f"  📂 디스크 충전 상태 불러옴: {self.disk_states[0].loaded_count}, {self.disk_states[1].loaded_count}, {self.disk_states[2].loaded_count}")
            
        except Exception as e:
            print(f"  ⚠️ 저장된 디스크 충전 상태 없음: {e}")