"""
알약 충전 화면
알약을 디스크에 충전하는 화면
"""

import time
import lvgl as lv
# math, json, UIStyle은 지연 임포트로 변경 (메모리 절약)
from data_manager import DataManager

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
            # print(f"  [INFO] 리미트 스위치 {self.current_loading_count}번째 감지 - 1칸 이동 (총 {self.loaded_count}칸)")
            
            # 3번의 리미트 스위치 감지로 3칸 충전 완료
            if self.current_loading_count >= 3:
                self.is_loading = False
                # print(f"  [INFO] 3칸 충전 완료! 총 {self.loaded_count}칸")
                return True
            return False
        return False
    
    def get_loading_progress(self):
        """충전 진행률 반환 (0-100)"""
        return (self.loaded_count / self.total_compartments) * 100

class PillLoadingScreen:
    """알약 충전 화면 클래스"""
    
    def __init__(self, screen_manager):
        """알약 충전 화면 초기화 - 지연 초기화 강화"""
        # 메모리 모니터링
        from memory_monitor import log_memory
        log_memory("PillLoadingScreen 초기화 시작")
        
        # 메모리 정리
        import gc
        gc.collect()
        
        # 최소한의 기본 변수만 초기화
        self.screen_manager = screen_manager
        self.screen_name = 'pill_loading'
        self.screen_obj = None
        
        # 기본 상태 변수들
        self.selected_disk_index = 0
        self.is_loading = False
        self.loading_progress = 0
        self.current_mode = 'selection'
        self.current_disk_state = None
        
        # 모든 무거운 객체는 None으로 초기화 (지연 초기화)
        self.ui_style = None
        self.motor_system = None
        self.disk_states = {}
        self._disk_states_loaded = False
        
        # 데이터 구조들도 지연 초기화 (메모리 절약)
        self.meal_to_disk_mapping = None
        self.dose_times = None  # 지연 초기화
        self.selected_meals = None  # 지연 초기화
        self.available_disks = None  # 지연 초기화
        self.sequential_mode = False
        self.current_sequential_index = 0
        self.sequential_disks = None  # 지연 초기화
        self.disk_states_file = "/data/disk_states.json"
        
        # 화면 생성 완전 제거 - show() 시점에 생성
        self._screen_created = False
        
        log_memory("PillLoadingScreen 기본 초기화 완료")
        # print(f"[OK] {self.screen_name} 화면 초기화 완료 (지연 초기화 모드)")
    
    def _ensure_ui_style(self):
        """UI 스타일이 필요할 때만 초기화 - 메모리 모니터링 강화"""
        if self.ui_style is None:
            try:
                from memory_monitor import log_memory, check_memory, cleanup_memory
                
                # 메모리 체크 (UIStyle은 약 600 bytes 사용)
                if not check_memory(800, "UIStyle 초기화"):
                    cleanup_memory("UIStyle 초기화 전")
                
                log_memory("UIStyle 초기화 시작")
                
                import gc
                gc.collect()
                # UIStyle 지연 임포트
                from ui_style import UIStyle
                self.ui_style = UIStyle()
                
                log_memory("UIStyle 초기화 완료")
                # print("[OK] UI 스타일 지연 초기화 완료")
            except Exception as e:
                # print(f"[WARN] UI 스타일 지연 초기화 실패: {e}")
                self.ui_style = None
        
    def _ensure_motor_system(self):
        """모터 시스템이 필요할 때만 초기화 - 메모리 모니터링 강화"""
        if self.motor_system is None:
            try:
                from memory_monitor import log_memory, check_memory, cleanup_memory
                
                # 메모리 체크 (PillBoxMotorSystem은 약 500 bytes 사용)
                if not check_memory(700, "모터 시스템 초기화"):
                    cleanup_memory("모터 시스템 초기화 전")
                
                log_memory("모터 시스템 초기화 시작")
                
                import gc
                gc.collect()
                from motor_control import PillBoxMotorSystem
                self.motor_system = PillBoxMotorSystem()
                
                log_memory("모터 시스템 초기화 완료")
                # print("[OK] 모터 시스템 지연 초기화 완료")
            except Exception as e:
                # print(f"[WARN] 모터 시스템 지연 초기화 실패: {e}")
                self.motor_system = None
        
    def _ensure_disk_states(self):
        """디스크 상태가 필요할 때만 초기화"""
        if not self._disk_states_loaded:
            try:
                import gc
                gc.collect()
                self._load_disk_states()
                self._disk_states_loaded = True
                # print("[OK] 디스크 상태 지연 초기화 완료")
            except Exception as e:
                # print(f"[WARN] 디스크 상태 지연 초기화 실패: {e}")
                # 기본 상태로 초기화 (디스크 번호 0, 1, 2)
                for i in range(3):
                    self.disk_states[i] = DiskState(i)
                self._disk_states_loaded = True
    
    def _ensure_meal_mapping(self):
        """식사 시간 매핑이 필요할 때만 초기화"""
        if self.meal_to_disk_mapping is None:
            try:
                from memory_monitor import log_memory
                log_memory("식사 시간 매핑 초기화")
                
                self.meal_to_disk_mapping = {
                    'breakfast': 0,  # 아침 → 디스크 0 (인덱스)
                    'lunch': 1,      # 점심 → 디스크 1 (인덱스)
                    'dinner': 2      # 저녁 → 디스크 2 (인덱스)
                }
                # print("[OK] 식사 시간 매핑 지연 초기화 완료")
            except Exception as e:
                # print(f"[WARN] 식사 시간 매핑 초기화 실패: {e}")
                self.meal_to_disk_mapping = {}
                pass
    
    def _create_modern_screen_lazy(self):
        """지연 초기화 방식의 화면 생성"""
        try:
            from memory_monitor import log_memory
            
            # print(f"  [INFO] {self.screen_name} 지연 화면 생성 시작...")
            log_memory("지연 화면 생성 시작")
            
            # 기존 _create_modern_screen() 호출
            self._create_modern_screen()
            
            log_memory("지연 화면 생성 완료")
            # print(f"  [OK] {self.screen_name} 지연 화면 생성 완료")
            
        except Exception as e:
            # print(f"  [ERROR] 지연 화면 생성 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def show(self):
        """화면 표시 - 지연 초기화 방식"""
        try:
            from memory_monitor import log_memory, check_memory, cleanup_memory
            
            # print(f"[INFO] {self.screen_name} 화면 표시 시작...")
            log_memory("PillLoadingScreen show() 시작")
            
            # 화면이 생성되지 않았으면 지연 생성
            if not self._screen_created:
                # print(f"[INFO] 화면이 생성되지 않음. 지연 생성 시작...")
                
                # 메모리 체크 (화면 생성은 약 1500 bytes 사용)
                if not check_memory(2000, "PillLoadingScreen 화면 생성"):
                    cleanup_memory("PillLoadingScreen 화면 생성 전")
                
                # 단계별 초기화 (메모리 절약)
                # print(f"[INFO] 1단계: JSON에서 복용 시간 정보 불러오기...")
                self.update_dose_times()
                import gc; gc.collect()
                
                # print(f"[INFO] 2단계: 식사-디스크 매핑 초기화...")
                self._ensure_meal_mapping()
                import gc; gc.collect()
                
                # print(f"[INFO] 3단계: 디스크 상태 초기화...")
                self._ensure_disk_states()
                import gc; gc.collect()
                
                # print(f"[INFO] 4단계: 충전 가능한 디스크 결정...")
                self._determine_available_disks()
                import gc; gc.collect()
                
                # print(f"[INFO] 5단계: 순차적 충전 모드 결정...")
                self._determine_sequential_mode()
                import gc; gc.collect()
                
                # print(f"[INFO] 6단계: 화면 생성...")
                self._create_modern_screen_lazy()
                self._screen_created = True
                
                log_memory("PillLoadingScreen 화면 생성 완료")
            
            # 화면 표시
            if hasattr(self, 'screen_obj') and self.screen_obj:
                # print(f"[INFO] 화면 객체 존재 확인됨")
                
                lv.screen_load(self.screen_obj)
                # print(f"[OK] {self.screen_name} 화면 로드 완료")
                
                # 화면 강제 업데이트
                # print(f"[INFO] {self.screen_name} 화면 강제 업데이트 시작...")
                for i in range(5):
                    lv.timer_handler()
                    time.sleep(0.01)
                    # print(f"  [INFO] 업데이트 {i+1}/5")
                # print(f"[OK] {self.screen_name} 화면 강제 업데이트 완료")
                
                # 디스플레이 플러시
                # print(f"[INFO] 디스플레이 플러시 실행...")
                try:
                    lv.disp.flush()
                except Exception as flush_error:
                    # print(f"[WARN] 디스플레이 플러시 오류 (무시): {flush_error}")
                    pass
                
                log_memory("PillLoadingScreen 화면 표시 완료")
                
                # ST7735 디스플레이 PWM 정리 (메모리 누수 방지)
                self._cleanup_display_pwm()
                
                # print(f"[OK] {self.screen_name} 화면 실행됨")
                
                # 순차적 충전 모드인 경우 이미 충전 화면이 생성됨
                if self.sequential_mode and self.current_mode == 'loading':
                    # print(f"[INFO] 순차적 충전 모드 - 충전 화면이 이미 생성됨")
                    pass
                    pass
            else:
                # print(f"[ERROR] {self.screen_name} 화면 객체가 없음")
                pass
                
        except Exception as e:
            # print(f"  [ERROR] {self.screen_name} 화면 표시 실패: {e}")
            pass
            import sys
            sys.print_exception(e)
    
    def update_dose_times(self, dose_times=None):
        """복용 시간 정보 업데이트 (최소한만 처리)"""
        try:
            # print(f"[INFO] 복용 시간 정보 업데이트 시작")
            
            # 전역 데이터에서 최신 정보 가져오기
            if dose_times:
                data_manager = DataManager()
                data_manager.save_dose_times(dose_times)
                self.dose_times = dose_times
            else:
                data_manager = DataManager()
                self.dose_times = data_manager.get_dose_times()
            
            # 선택된 식사 시간 추출 (지연 초기화)
            if self.selected_meals is None:
                self.selected_meals = []
            for dose_info in self.dose_times:
                if isinstance(dose_info, dict) and 'meal_key' in dose_info:
                    self.selected_meals.append(dose_info['meal_key'])
            
            # JSON에서 선택된 디스크 정보 불러오기
            if self.dose_times and len(self.dose_times) > 0:
                first_dose_info = self.dose_times[0]
                if isinstance(first_dose_info, dict) and 'selected_disks' in first_dose_info:
                    self.selected_disks = first_dose_info['selected_disks']
                    # print(f"[INFO] JSON에서 선택된 디스크 불러오기: {self.selected_disks}")
                    
                    # 충전 가능한 디스크 다시 결정
                    self._determine_available_disks()
            
            # print(f"[INFO] 설정된 복용 시간: {len(self.dose_times)}개")
            for dose_info in self.dose_times:
                if isinstance(dose_info, dict):
                    # print(f"  - {dose_info.get('meal_name', 'Unknown')}: {dose_info.get('time', 'Unknown')}")
                    if 'selected_disks' in dose_info:
                        # print(f"    선택된 디스크: {dose_info['selected_disks']}")
                        pass
            # print(f"[INFO] 선택된 식사 시간: {self.selected_meals}")
            # print(f"[OK] 복용 시간 정보 업데이트 완료")
            
        except Exception as e:
            # print(f"[ERROR] 복용 시간 정보 업데이트 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def set_selected_disks(self, selected_disks):
        """선택된 디스크 설정"""
        try:
            self.selected_disks = selected_disks
            # print(f"[INFO] 선택된 디스크 설정: {self.selected_disks}")
            
            # 충전 가능한 디스크 다시 결정
            self._determine_available_disks()
            
        except Exception as e:
            # print(f"[ERROR] 선택된 디스크 설정 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def set_selected_meals(self, selected_meals):
        """선택된 식사 시간 설정"""
        try:
            self.selected_meals = selected_meals
            # print(f"[INFO] 선택된 식사 시간 설정: {len(selected_meals) if selected_meals else 0}개")
            
            # 충전 가능한 디스크 다시 결정
            self._determine_available_disks()
            
        except Exception as e:
            # print(f"[ERROR] 선택된 식사 시간 설정 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _determine_available_disks(self):
        """선택된 디스크에 따라 충전 가능한 디스크 결정"""
        try:
            # 지연 초기화 처리
            if self.available_disks is None:
                self.available_disks = []
            
            # 선택된 디스크가 있으면 해당 디스크들만 충전
            if hasattr(self, 'selected_disks') and self.selected_disks:
                # 디스크 번호를 인덱스로 변환 (1,2,3 → 0,1,2)
                self.available_disks = [disk_num - 1 for disk_num in self.selected_disks]
                # print(f"[INFO] 선택된 디스크로 충전: {self.selected_disks}")
            elif not self.selected_meals or len(self.selected_meals) == 0:
                # 선택된 식사 시간이 없으면 모든 디스크 충전 가능
                self.available_disks = [0, 1, 2]  # 디스크 1, 2, 3
                # print(f"[INFO] 선택된 식사 시간 없음 - 모든 디스크 충전 가능")
            elif len(self.selected_meals) == 1:
                # 1개만 선택했으면 모든 디스크 충전 가능
                self.available_disks = [0, 1, 2]  # 디스크 1, 2, 3
                # print(f"[INFO] 1개 식사 시간 선택 - 모든 디스크 충전 가능")
            else:
                # 2개 이상 선택했으면 해당 디스크만 충전 가능
                for meal_key in self.selected_meals:
                    if meal_key in self.meal_to_disk_mapping:
                        disk_index = self.meal_to_disk_mapping[meal_key]
                        self.available_disks.append(disk_index)
                
                # print(f"[INFO] {len(self.selected_meals)}개 식사 시간 선택 - 제한된 디스크 충전")
                for disk_index in self.available_disks:
                    meal_name = self._get_meal_name_by_disk(disk_index)
                    # print(f"  - 디스크 {disk_index}: {meal_name}")
            
        except Exception as e:
            # print(f"[ERROR] 충전 가능한 디스크 결정 실패: {e}")
            # 오류 시 모든 디스크 허용
            self.available_disks = [0, 1, 2]
    
    def _get_meal_name_by_disk(self, disk_index):
        """디스크 인덱스로 식사 시간 이름 반환"""
        # 먼저 자동 할당된 디스크 정보에서 찾기
        try:
            from data_manager import DataManager
            data_manager = DataManager()
            auto_assigned_disks = data_manager.get_auto_assigned_disks()
            
            if auto_assigned_disks:
                # 자동 할당된 디스크에서 찾기
                disk_number = disk_index + 1  # 인덱스를 디스크 번호로 변환 (0→1, 1→2, 2→3)
                for disk_info in auto_assigned_disks:
                    if disk_info['disk_number'] == disk_number:
                        return disk_info['meal_name']
        except Exception as e:
            # print(f"[WARN] 자동 할당 정보에서 식사 시간 찾기 실패: {e}")
            pass
        # 자동 할당 정보가 없으면 기존 방식 사용
        for meal_key, disk_idx in self.meal_to_disk_mapping.items():
            if disk_idx == disk_index:
                meal_names = {'breakfast': '아침', 'lunch': '점심', 'dinner': '저녁'}
                return meal_names.get(meal_key, '알 수 없음')
        return '알 수 없음'
    
    def _determine_sequential_mode(self):
        """순차적 충전 모드 결정"""
        try:
            # 먼저 DataManager에서 selected_disks 정보 확인
            try:
                from data_manager import DataManager
                data_manager = DataManager()
                dose_times = data_manager.get_dose_times()
                
                if dose_times and len(dose_times) > 0:
                    first_dose = dose_times[0]
                    if isinstance(first_dose, dict) and 'selected_disks' in first_dose:
                        selected_disks = first_dose['selected_disks']
                        # print(f"[INFO] DataManager에서 selected_disks 발견: {selected_disks}")
                        
                        if selected_disks and len(selected_disks) > 1:
                            # 선택된 디스크가 2개 이상이면 순차 충전 모드
                            self.sequential_mode = True
                            if self.sequential_disks is None:
                                self.sequential_disks = []
                            
                            # self.selected_disks 설정 (화면 제목용)
                            self.selected_disks = selected_disks
                            
                            # 선택된 디스크들을 디스크 번호 순으로 정렬한 후 인덱스로 변환 (1,2,3 → 0,1,2)
                            sorted_disks = sorted(selected_disks)  # 디스크 번호 순 정렬
                            self.sequential_disks = [disk_num - 1 for disk_num in sorted_disks]
                            self.current_sequential_index = 0
                            # print(f"[INFO] 선택된 디스크 순차 충전 모드 활성화: {sorted_disks} (정렬됨)")
                            # print(f"[INFO] 원래 선택 순서: {selected_disks}")
                            for i, disk_num in enumerate(sorted_disks):
                                # print(f"  {i+1}. 디스크 {disk_num}")
                                pass
                            return  # 성공적으로 설정했으므로 종료
                        elif selected_disks and len(selected_disks) == 1:
                            # 선택된 디스크가 1개면 단일 디스크 충전
                            self.sequential_mode = True
                            if self.sequential_disks is None:
                                self.sequential_disks = []
                            
                            # self.selected_disks 설정 (화면 제목용)
                            self.selected_disks = selected_disks
                            
                            disk_num = selected_disks[0]
                            self.sequential_disks = [disk_num - 1]  # 인덱스로 변환
                            self.current_sequential_index = 0
                            # print(f"[INFO] 단일 디스크 충전 모드 활성화: 디스크 {disk_num}")
                            return  # 성공적으로 설정했으므로 종료
            except Exception as e:
                # print(f"[WARN] DataManager에서 selected_disks 확인 실패: {e}")
                pass
            
            # 기존 selected_disks 확인 (fallback)
            if hasattr(self, 'selected_disks') and self.selected_disks and len(self.selected_disks) > 1:
                self.sequential_mode = True
                # 지연 초기화 처리
                if self.sequential_disks is None:
                    self.sequential_disks = []
                
                # 선택된 디스크들을 디스크 번호 순으로 정렬한 후 인덱스로 변환 (1,2,3 → 0,1,2)
                sorted_disks = sorted(self.selected_disks)  # 디스크 번호 순 정렬
                self.sequential_disks = [disk_num - 1 for disk_num in sorted_disks]
                self.current_sequential_index = 0
                # print(f"[INFO] 선택된 디스크 순차 충전 모드 활성화: {sorted_disks} (정렬됨)")
                # print(f"[INFO] 원래 선택 순서: {self.selected_disks}")
                for i, disk_num in enumerate(sorted_disks):
                    # print(f"  {i+1}. 디스크 {disk_num}")
                    pass
            elif self.selected_meals and len(self.selected_meals) >= 1:
                # 자동 할당된 디스크 정보 확인
                try:
                    from data_manager import DataManager
                    data_manager = DataManager()
                    auto_assigned_disks = data_manager.get_auto_assigned_disks()
                except Exception as e:
                    # print(f"[WARN] 자동 할당 정보 로드 실패: {e}")
                    auto_assigned_disks = []
                
                if auto_assigned_disks:
                    # 자동 할당된 디스크만 순차 충전
                    self.sequential_mode = True
                    # 지연 초기화 처리
                    if self.sequential_disks is None:
                        self.sequential_disks = []
                    
                    # 자동 할당된 디스크를 디스크 번호 순으로 정렬
                    sorted_disks = sorted([disk_info['disk_number'] for disk_info in auto_assigned_disks])
                    self.sequential_disks = [disk_num - 1 for disk_num in sorted_disks]  # 1,2,3 → 0,1,2
                    self.current_sequential_index = 0
                    
                    # print(f"[INFO] 자동 할당된 디스크 순차 충전 모드 활성화: {sorted_disks}")
                    # print(f"[DEBUG] sequential_disks: {self.sequential_disks}")
                    # print(f"[DEBUG] sequential_mode: {self.sequential_mode}")
                    try:
                        for i, disk_num in enumerate(sorted_disks):
                            disk_info = next((d for d in auto_assigned_disks if d['disk_number'] == disk_num), None)
                            if disk_info:
                                # print(f"  {i+1}. 디스크 {disk_num} ({disk_info['meal_name']} {disk_info['time']})")
                                pass
                    except Exception as e:
                        # print(f"[WARN] 디스크 정보 출력 실패: {e}")
                        pass
                    # print(f"[OK] 자동 할당된 디스크 순차 충전 모드 설정 완료")
                else:
                    # 자동 할당 정보가 없으면 기존 방식 사용
                    self.sequential_mode = True
                    # 지연 초기화 처리
                    if self.sequential_disks is None:
                        self.sequential_disks = []
                    
                    # meal_to_disk_mapping이 초기화되었는지 확인
                    self._ensure_meal_mapping()
                    
                    # 아침, 점심, 저녁 순서로 정렬
                    meal_order = ['breakfast', 'lunch', 'dinner']
                    # print(f"[DEBUG] selected_meals: {self.selected_meals}")
                    # print(f"[DEBUG] meal_to_disk_mapping: {self.meal_to_disk_mapping}")
                    
                    for meal_key in meal_order:
                        # selected_meals가 딕셔너리 리스트인 경우 처리
                        for meal_info in self.selected_meals:
                            # print(f"[DEBUG] meal_info: {meal_info}, meal_key: {meal_key}")
                            if isinstance(meal_info, dict) and meal_info.get('key') == meal_key:
                                disk_index = self.meal_to_disk_mapping[meal_key]
                                self.sequential_disks.append(disk_index)
                                # print(f"[DEBUG] 딕셔너리 매칭: {meal_key} -> 디스크 {disk_index}")
                                break
                            elif meal_info == meal_key:  # 문자열인 경우
                                disk_index = self.meal_to_disk_mapping[meal_key]
                                self.sequential_disks.append(disk_index)
                                # print(f"[DEBUG] 문자열 매칭: {meal_key} -> 디스크 {disk_index}")
                                break
                    
                    self.current_sequential_index = 0
                    # print(f"[INFO] 순차적 충전 모드 활성화: {len(self.sequential_disks)}개 디스크")
                    for i, disk_index in enumerate(self.sequential_disks):
                        try:
                            meal_name = self._get_meal_name_by_disk(disk_index)
                            # print(f"  {i+1}. 디스크 {disk_index} ({meal_name})")
                        except Exception as e:
                            # print(f"  {i+1}. 디스크 {disk_index} (오류: {e})")
                            pass
            else:
                # 선택된 식사 시간이 없으면 개별 선택 모드
                self.sequential_mode = False
                self.sequential_disks = []
                self.current_sequential_index = 0
                # print(f"[INFO] 개별 선택 모드 활성화")
                
        except Exception as e:
            # print(f"[ERROR] 순차적 충전 모드 결정 실패: {e}")
            self.sequential_mode = False
            self.sequential_disks = []
    
    def start_sequential_loading(self):
        """순차적 충전 시작"""
        try:
            if not self.sequential_mode or not self.sequential_disks:
                # print(f"[ERROR] 순차적 충전 모드가 아니거나 디스크 목록이 비어있음")
                return False
            
            # print(f"[INFO] 순차적 충전 시작: {len(self.sequential_disks)}개 디스크")
            self.current_sequential_index = 0
            self._start_current_disk_loading()
            return True
            
        except Exception as e:
            # print(f"[ERROR] 순차적 충전 시작 실패: {e}")
            return False
    
    def _start_current_disk_loading(self):
        """현재 디스크 충전 시작"""
        try:
            if self.current_sequential_index >= len(self.sequential_disks):
                # print(f"[INFO] 모든 디스크 충전 완료!")
                self._complete_sequential_loading()
                return
            
            current_disk_index = self.sequential_disks[self.current_sequential_index]
            
            if hasattr(self, 'selected_disks') and self.selected_disks:
                # 선택된 디스크 모드: 디스크 번호 표시
                disk_num = current_disk_index + 1  # 인덱스를 디스크 번호로 변환
                # print(f"[INFO] 디스크 {disk_num} 충전 시작 ({self.current_sequential_index + 1}/{len(self.sequential_disks)})")
            else:
                # 기존 모드: 식사 시간 표시
                meal_name = self._get_meal_name_by_disk(current_disk_index)
                # print(f"[INFO] {meal_name} 디스크 충전 시작 ({self.current_sequential_index + 1}/{len(self.sequential_disks)})")
            
            # 디스크 충전 화면으로 전환
            self._switch_to_disk_loading(current_disk_index)
            
        except Exception as e:
            # print(f"[ERROR] 현재 디스크 충전 시작 실패: {e}")
            pass
    
    def _complete_current_disk_loading(self):
        """현재 디스크 충전 완료 후 다음 디스크로"""
        try:
            print("현재 디스크 충전 완료")
            self.current_sequential_index += 1
            
            # 모든 디스크가 15칸 완료되었는지 다시 확인
            all_disks_completed = True
            for disk_idx in range(3):
                if self._is_disk_selected(disk_idx):
                    if self.disk_states[disk_idx].loaded_count < 15:
                        all_disks_completed = False
                        break
            
            if all_disks_completed:
                print("모든 디스크 충전 완료 - 메인화면으로 이동")
                self._complete_sequential_loading()
            elif self.current_sequential_index < len(self.sequential_disks):
                # 다음 디스크로
                print("다음 디스크로 이동")
                self._start_current_disk_loading()
            else:
                # 모든 디스크 완료
                print("모든 디스크 충전 완료!")
                self._complete_sequential_loading()
                
        except Exception as e:
            print(f"현재 디스크 충전 완료 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _is_disk_selected(self, disk_index):
        """디스크가 선택된 디스크 목록에 있는지 확인"""
        try:
            print(f"디스크 {disk_index+1} 선택 확인 시작...")
            
            # 순차적 모드에서 순차적 디스크 목록에 있는지 확인
            if self.sequential_mode and self.sequential_disks:
                is_selected = disk_index in self.sequential_disks
                print(f"순차적 모드: 디스크 {disk_index+1} 선택됨 = {is_selected}")
                return is_selected
            
            # 선택된 디스크 모드에서 선택된 디스크 목록에 있는지 확인
            if hasattr(self, 'selected_disks') and self.selected_disks:
                is_selected = disk_index in self.selected_disks
                print(f"선택된 디스크 모드: 디스크 {disk_index+1} 선택됨 = {is_selected}")
                return is_selected
            
            # 기본적으로 모든 디스크가 선택된 것으로 간주 (초기 상태)
            print(f"기본 모드: 디스크 {disk_index+1} 선택됨 = True (모든 디스크 선택)")
            return True
            
        except Exception as e:
            print(f"디스크 선택 확인 실패: {e}")
            return True  # 오류 시에도 선택된 것으로 간주
    
    def _check_completion_and_proceed(self):
        """완충 감지 및 다음 단계 처리"""
        try:
            print("완충 감지 및 다음 단계 처리 시작...")
            
            if self.sequential_mode:
                # 순차적 모드에서 모든 디스크가 15칸 완료되었는지 확인
                all_disks_completed = True
                for disk_idx in range(3):
                    if self._is_disk_selected(disk_idx):
                        if self.disk_states[disk_idx].loaded_count < 15:
                            all_disks_completed = False
                            print(f"디스크 {disk_idx+1} 진행률: {self.disk_states[disk_idx].loaded_count}/15칸")
                        else:
                            print(f"디스크 {disk_idx+1} 완료: 15/15칸")
                
                if all_disks_completed:
                    print("모든 디스크 충전 완료 - 메인화면으로 이동")
                    self._complete_sequential_loading()
                elif self.current_disk_state.loaded_count >= 15:
                    print("현재 디스크 15칸 완료 - 다음 디스크로 이동")
                    self._complete_current_disk_loading()
                else:
                    print(f"현재 디스크 진행률: {self.current_disk_state.loaded_count}/15칸")
            else:
                # 개별 선택 모드에서 모든 선택된 디스크 완료 확인
                all_completed = True
                for disk_idx in range(3):
                    if self._is_disk_selected(disk_idx):
                        if self.disk_states[disk_idx].loaded_count < 15:
                            all_completed = False
                            print(f"디스크 {disk_idx+1} 진행률: {self.disk_states[disk_idx].loaded_count}/15칸")
                        else:
                            print(f"디스크 {disk_idx+1} 완료: 15/15칸")
                
                if all_completed:
                    print("모든 선택된 디스크 충전 완료 - 메인화면으로 이동")
                    self._complete_individual_loading()
            
            print("완충 감지 및 다음 단계 처리 완료")
            
        except Exception as e:
            print(f"완충 감지 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _complete_individual_loading(self):
        """개별 선택 모드 충전 완료 처리"""
        try:
            print("개별 선택 모드 충전 완료 처리 시작...")
            
            # DataManager에 약물 수량 저장
            print("DataManager에 약물 수량 저장")
            self._save_medication_data_to_datamanager()
            
            # 설정 완료 메시지 표시
            print("설정 완료 메시지 표시")
            self._show_completion_message()
            
            # 흰색 화면 만들기
            print("흰색 화면 만들기")
            self._make_screen_white()
            
            # 부팅 타겟을 메인화면으로 설정
            print("부팅 타겟을 메인화면으로 설정")
            self._set_boot_target_to_main()
            
            # 잠시 대기 후 재부팅
            import time
            time.sleep(0.1)
            
            print("ESP 리셋 시작...")
            import machine
            machine.reset()
            
        except Exception as e:
            print(f"개별 선택 모드 충전 완료 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _complete_sequential_loading(self):
        """순차적 충전 완료"""
        try:
            print("순차적 충전 완료 - 메인화면으로 이동")
            
            # DataManager에 약물 수량 저장
            print("DataManager에 약물 수량 저장")
            self._save_medication_data_to_datamanager()
            
            # 메인화면으로 이동
                        
            # 설정 완료 메시지 표시
            print("설정 완료 메시지 표시")
            self._show_completion_message()
            print("설정 완료 메시지 표시 완료")
            
            # 흰색 화면 만들기
            print("흰색 화면 만들기")
            self._make_screen_white()
            print("흰색 화면 만들기 완료")
            
            # 부팅 타겟을 메인화면으로 설정
            print("부팅 타겟을 메인화면으로 설정")
            self._set_boot_target_to_main()
            print("부팅 타겟 설정 완료")
            
            # 잠시 대기 후 재부팅
            print("재부팅 전 대기 시작")
            import time
            time.sleep(0.1)
            print("재부팅 전 대기 완료")
            
            print("ESP 리셋 시작...")
            import machine
            machine.reset()
            
        except Exception as e:
            print(f"순차적 충전 완료 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _show_completion_message(self):
        """설정 완료 메시지 표시"""
        try:
            # print("[INFO] 설정 완료 메시지 표시 시작...")
            
            # 새로운 메시지 컨테이너 생성 (기존 컨테이너와 별개)
            message_container = lv.obj(self.screen_obj)
            message_container.set_size(128, 160)
            message_container.align(lv.ALIGN.CENTER, 0, 0)
            message_container.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)  # 흰색 배경
            message_container.set_style_bg_opa(255, 0)  # 불투명
            message_container.set_style_border_width(0, 0)
            message_container.set_style_pad_all(0, 0)
            
            # 스크롤바 비활성화
            message_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            message_container.set_scroll_dir(lv.DIR.NONE)
            # "디바이스를 재시작합니다." 텍스트
            desc_label = lv.label(message_container)
            # 노토산스 폰트 직접 적용
            korean_font = getattr(lv, "font_notosans_kr_regular", None)
            if korean_font:
                desc_label.set_style_text_font(korean_font, 0)
            else:
                desc_label.set_style_text_font(lv.font_default, 0)
            
            
            # 스크롤바 비활성화
            # title_label.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            # title_label.set_scroll_dir(lv.DIR.NONE)
            desc_label.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            desc_label.set_scroll_dir(lv.DIR.NONE)
            desc_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            desc_label.align(lv.ALIGN.CENTER, 0, 0)
            desc_label.set_style_text_color(lv.color_hex(0x666666), 0)  # 회색
            desc_label.set_text("설정 완료,\n디바이스를\n재시작합니다.")
            
            
            # 1초 대기
            import time
            time.sleep(1.5)
            
            # print("[OK] 설정 완료 메시지 표시 완료")
            
        except Exception as e:
            # print(f"[ERROR] 설정 완료 메시지 표시 실패: {e}")
            pass
    
    def _make_screen_white(self):
        """화면을 흰색으로 만들기 (디스플레이 테스트용)"""
        try:
            # print("[INFO] 화면을 흰색으로 변경 시작...")
            
            # 현재 화면 객체가 있는지 확인
            if hasattr(self, 'screen_obj') and self.screen_obj:
                # 화면 배경을 흰색으로 설정
                self.screen_obj.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)  # 흰색
                # print("[OK] 화면 배경을 흰색으로 변경 완료")
                
                # 모든 자식 객체 숨기기 (깔끔한 흰색 화면을 위해)
                if hasattr(self, 'main_container') and self.main_container:
                    self.main_container.delete()  # 메인 컨테이너 삭제
                    # print("[OK] 기존 UI 요소 제거 완료")
                
                # 새로운 빈 컨테이너 생성 (흰색 배경만)
                self.main_container = lv.obj(self.screen_obj)
                self.main_container.set_size(lv.pct(100), lv.pct(100))
                self.main_container.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)  # 흰색
                self.main_container.set_style_border_width(0, 0)  # 테두리 없음
                self.main_container.center()
                
                # print("[OK] 흰색 화면 설정 완료")
                
            else:
                # print("[ERROR] 화면 객체가 없음")
                pass
        except Exception as e:
            # print(f"[ERROR] 화면을 흰색으로 변경 실패: {e}")
            pass
    
    def _mark_setup_complete(self):
        """초기 설정 완료 플래그 설정 - boot_target.json 공통 사용"""
        try:
            import json
            import os
            
            # /data 디렉토리 존재 확인 및 생성
            data_dir = "/data"
            try:
                if data_dir not in os.listdir("/"):
                    os.mkdir(data_dir)
                    # print(f"[INFO] /data 디렉토리 생성됨")
            except OSError as e:
                if e.errno == 17:  # EEXIST - 디렉토리가 이미 존재
                    # print(f"[INFO] /data 디렉토리가 이미 존재함")
                    pass
                else:
                    raise
            
            # boot_target.json을 사용하여 메인화면으로 부팅하도록 설정
            boot_data = {"boot_target": "main"}
            boot_file = "/data/boot_target.json"
            
            # 부팅 타겟 파일 생성/업데이트
            with open(boot_file, 'w') as f:
                json.dump(boot_data, f)
            
            # print("[OK] 초기 설정 완료 - 메인화면으로 부팅 설정됨")
            
        except Exception as e:
            # print(f"[WARN] 초기 설정 완료 플래그 설정 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _show_simple_completion_message(self):
        """메모리 부족 시 간단한 완료 메시지 표시"""
        try:
            # print("[INFO] 간단한 완료 메시지 표시 시작...")
            
            # 기존 화면 내용 지우기
            if hasattr(self, 'screen_obj') and self.screen_obj:
                # 모든 자식 객체 제거
                try:
                    child_count = self.screen_obj.get_child_cnt()
                    for i in range(child_count):
                        child = self.screen_obj.get_child(0)
                        if child and hasattr(self.screen_obj, 'remove_child'):
                            self.screen_obj.remove_child(child)
                except Exception as e:
                    # print(f"[WARN] 화면 정리 중 오류 (무시): {e}")
                    pass
            
            # 간단한 완료 메시지 생성
            completion_label = lv.label(self.screen_obj)
            completion_label.set_text("충전 완료!")
            completion_label.align(lv.ALIGN.CENTER, 0, -20)
            completion_label.set_style_text_color(lv.color_hex(0x00AA00), 0)
            completion_label.set_style_text_font(lv.font_montserrat_14, 0)
            
            # 안내 메시지
            guide_label = lv.label(self.screen_obj)
            guide_label.set_text("메인 화면으로\n이동합니다...")
            guide_label.align(lv.ALIGN.CENTER, 0, 20)
            guide_label.set_style_text_color(lv.color_hex(0x666666), 0)
            # 폰트 설정 (기본 폰트 사용)
            try:
                korean_font = getattr(lv, "font_notosans_kr_regular", None)
                if korean_font:
                    guide_label.set_style_text_font(korean_font, 0)
                else:
                    guide_label.set_style_text_font(lv.font_default, 0)
            except Exception as e:
                guide_label.set_style_text_font(lv.font_default, 0)
            guide_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            
            # print("[OK] 간단한 완료 메시지 표시 완료")
            
            # 흰색 화면 만들기 후 메인 화면으로 이동
            self._make_screen_white()
            
            # 잠시 대기
            import time
            time.sleep(0.1)
            
            # 메인 화면으로 이동 시도
            if 'main' in self.screen_manager.screens:
                # ScreenManager에 화면 전환 요청
                try:
                    self.screen_manager.show_screen('main')
                    # print("[OK] 화면 전환 요청 완료")
                except Exception as e:
                    # print(f"[ERROR] 화면 전환 요청 실패: {e}")
                    import sys
                    sys.print_exception(e)
                
                # ScreenManager의 완료 처리 메서드 호출
                try:
                    # print("[INFO] 알약 충전 완료 - ScreenManager에 완료 신호 전송")
                    self.screen_manager.pill_loading_completed()
                    # print("[OK] 알약 충전 완료 신호 전송 완료")
                except Exception as e:
                    # print(f"[ERROR] 알약 충전 완료 신호 전송 실패: {e}")
                    import sys
                    sys.print_exception(e)
                # print("[OK] 메인 화면으로 이동 완료")
            else:
                # print("[WARN] 메인 화면이 등록되지 않음")
                pass
                
        except Exception as e:
            # print(f"[ERROR] 간단한 완료 메시지 표시 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _save_medication_data_to_datamanager(self):
        """DataManager에 약물 수량 저장"""
        try:
            # print("[INFO] DataManager에 약물 수량 저장 중...")
            
            # DataManager 임포트 및 초기화
            from data_manager import DataManager
            data_manager = DataManager()
            
            # 각 식사별로 올바른 디스크에만 저장
            if hasattr(self, 'dose_times') and self.dose_times:
                print(f"[DEBUG] 식사별 알약 개수 저장 시작...")
                for i, dose_time in enumerate(self.dose_times):
                    if i < 3:  # 최대 3개 식사
                        disk_num = i + 1  # 디스크 1, 2, 3
                        disk_index = i  # 디스크 인덱스 0, 1, 2
                        
                        if disk_index in self.disk_states:
                            final_count = self.disk_states[disk_index].loaded_count
                            meal_name = dose_time.get('meal_name', f'식사{i+1}')
                            print(f"[DEBUG] {meal_name} -> 디스크 {disk_num}: {final_count}개 저장")
                            
                            success = data_manager.update_disk_count(disk_num, final_count)
                            if success:
                                print(f"[OK] {meal_name} 디스크 {disk_num} 수량 저장: {final_count}개")
                            else:
                                print(f"[ERROR] {meal_name} 디스크 {disk_num} 수량 저장 실패")
                        else:
                            print(f"[WARN] {dose_time.get('meal_name', f'식사{i+1}')} 디스크 {disk_num} 상태 정보 없음")
            else:
                # 기본 디스크별 저장 (식사 정보가 없는 경우)
                print(f"[DEBUG] 기본 디스크별 알약 개수 저장...")
                for disk_num in [1, 2, 3]:
                    disk_index = disk_num - 1  # 디스크 번호를 인덱스로 변환 (1->0, 2->1, 3->2)
                    if disk_index in self.disk_states:
                        final_count = self.disk_states[disk_index].loaded_count
                        success = data_manager.update_disk_count(disk_num, final_count)
                        if success:
                            print(f"[OK] 디스크 {disk_num} 수량 저장: {final_count}개")
                        else:
                            print(f"[ERROR] 디스크 {disk_num} 수량 저장 실패")
                    else:
                        print(f"[WARN] 디스크 {disk_num} 상태 정보 없음 (인덱스 {disk_index})")
            # print("[OK] DataManager 약물 수량 저장 완료")
            
        except Exception as e:
            # print(f"[ERROR] DataManager 약물 수량 저장 실패: {e}")
            pass
        
    def _create_modern_screen(self):
        """간단한 텍스트 기반 UI 화면 생성"""
        # print(f"  [INFO] {self.screen_name} 간단한 UI 화면 생성 시작...")
        
        # 강력한 메모리 정리
        import gc
        for i in range(5):
            gc.collect()
            time.sleep(0.02)
        # print(f"  [OK] 메모리 정리 완료")
        
        # 화면 객체 생성
        # print(f"  [INFO] 화면 객체 생성...")
        self.screen_obj = lv.obj()
        self.screen_obj.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)  # 화이트 배경
        
        # 메인 화면 스크롤바 비활성화
        self.screen_obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.screen_obj.set_scroll_dir(lv.DIR.NONE)
        
        # print(f"  [OK] 화면 객체 생성 완료")
        
        # 새로운 간단한 UI 생성
        self._create_simple_ui()
        
        # print(f"  [OK] 간단한 UI 화면 생성 완료")
    
    def _create_simple_ui(self):
        """간단한 텍스트 기반 UI 생성"""
        try:
            # 제목 생성
            self.title_text = lv.label(self.screen_obj)
            self.title_text.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
            self.title_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            self.title_text.align(lv.ALIGN.TOP_MID, 0, 10)
            
            # 한국어 폰트 적용
            korean_font = getattr(lv, "font_notosans_kr_regular", None)
            if korean_font:
                self.title_text.set_style_text_font(korean_font, 0)
            
            self.title_text.set_text("알약 충전")
            
            # 디스크 상태 표시 영역 생성
            self._create_disk_status_area()
            
            # 버튼 힌트 영역 생성
            self._create_button_hints_area()
            
        except Exception as e:
            # print(f"  [ERROR] 간단한 UI 생성 실패: {e}")
            pass
    
    def _create_disk_status_area(self):
        """디스크 상태 표시 영역 생성"""
        try:
            # 복용 패턴에 따른 디스크 상태 표시
            self._update_disk_status_display()
            
        except Exception as e:
            # print(f"  [ERROR] 디스크 상태 영역 생성 실패: {e}")
            pass
    
    def _update_disk_status_display(self):
        """디스크 상태 표시 업데이트"""
        try:
            print("디스크 상태 표시 업데이트 시작...")
            
            # 디스크 상태 강제 초기화
            if not hasattr(self, 'disk_states') or not self.disk_states:
                self._ensure_disk_states()
            
            # 디버깅: 자동 할당 모드 확인
            is_auto = self._is_auto_assigned_mode()
            print(f"자동 할당 모드: {is_auto}")
            print(f"디스크 상태: {self.disk_states}")
            
            # 기존 상태 표시 라벨들 정리
            if hasattr(self, 'disk_status_labels') and self.disk_status_labels:
                for label in self.disk_status_labels:
                    if label:
                        label.delete()
            
            self.disk_status_labels = []
            
            # 복용 패턴에 따른 디스크 상태 표시
            if is_auto:
                # 자동 할당 모드: 아침약, 점심약, 저녁약 표시
                print("식사별 상태 표시 생성")
                self._create_meal_status_display()
            else:
                # 수동 선택 모드: 디스크1, 디스크2, 디스크3 표시
                print("디스크별 상태 표시 생성")
                self._create_disk_status_display()
            
            # 디스크 상태가 표시되지 않는 경우 강제로 디스크 상태 표시
            if not self.disk_status_labels or len(self.disk_status_labels) == 0:
                print("디스크 상태가 표시되지 않음 - 강제로 디스크 상태 표시")
                self._create_disk_status_display()
            
            print("디스크 상태 표시 업데이트 완료")
                
        except Exception as e:
            print(f"디스크 상태 표시 업데이트 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _is_auto_assigned_mode(self):
        """자동 할당 모드인지 확인"""
        try:
            print(f"[DEBUG] 자동 할당 모드 확인 시작...")
            print(f"[DEBUG] dose_times: {self.dose_times}")
            print(f"[DEBUG] dose_times 길이: {len(self.dose_times) if self.dose_times else 0}")
            
            # 복용 횟수가 2회 이상이면 자동 할당 모드
            if hasattr(self, 'dose_times') and self.dose_times and len(self.dose_times) >= 2:
                print(f"[DEBUG] 복용 횟수 2회 이상으로 자동 할당 모드")
                return True
            
            # DataManager에서 자동 할당된 디스크 확인
            from data_manager import DataManager
            data_manager = DataManager()
            auto_assigned_disks = data_manager.get_auto_assigned_disks()
            print(f"[DEBUG] DataManager 자동 할당 디스크: {auto_assigned_disks}")
            print(f"[DEBUG] DataManager 자동 할당 디스크 길이: {len(auto_assigned_disks) if auto_assigned_disks else 0}")
            
            is_auto = auto_assigned_disks and len(auto_assigned_disks) > 0
            print(f"[DEBUG] 자동 할당 모드 결과: {is_auto}")
            return is_auto
        except Exception as e:
            print(f"[DEBUG] 자동 할당 모드 확인 오류: {e}")
            return False
    
    def _create_meal_status_display(self):
        """식사별 상태 표시 생성"""
        try:
            print("식사별 상태 표시 생성 시작...")
            
            # 복용 패턴에 따른 식사 이름들
            meal_names = self._get_meal_names_by_pattern()
            print(f"식사 이름들: {meal_names}")
            
            y_offset = -20  # 제목 아래쪽에서 시작
            for i, meal_name in enumerate(meal_names):
                print(f"식사 {i}: {meal_name} 생성 중")
                # 식사 이름과 상태 표시
                label = lv.label(self.screen_obj)
                label.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
                label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
                label.align(lv.ALIGN.CENTER, 0, y_offset + i * 20)
                
                # 한국어 폰트 적용
                korean_font = getattr(lv, "font_notosans_kr_regular", None)
                if korean_font:
                    label.set_style_text_font(korean_font, 0)
                
                # 디스크 상태 가져오기
                disk_idx = i  # 디스크 인덱스
                
                # 디스크 상태가 없으면 초기화
                if not hasattr(self, 'disk_states') or not self.disk_states:
                    self._ensure_disk_states()
                
                if disk_idx in self.disk_states:
                    loaded_count = self.disk_states[disk_idx].loaded_count
                    total_count = self.disk_states[disk_idx].total_compartments
                    label.set_text(f"{meal_name}  {loaded_count}/{total_count}")
                    print(f"식사 {i} 상태: {loaded_count}/{total_count}")
                else:
                    label.set_text(f"{meal_name}  0/15")
                    print(f"식사 {i} 상태: 0/15 (기본값)")
                
                self.disk_status_labels.append(label)
            
            print("식사별 상태 표시 생성 완료")
                
        except Exception as e:
            # print(f"  [ERROR] 식사 상태 표시 생성 실패: {e}")
            pass
    
    def _create_disk_status_display(self):
        """디스크별 상태 표시 생성"""
        try:
            print("디스크별 상태 표시 생성 시작...")
            
            # 선택된 디스크만 표시
            selected_disks = []
            if hasattr(self, 'selected_disks') and self.selected_disks:
                # 선택된 디스크 번호를 인덱스로 변환 (1,2,3 → 0,1,2)
                # 번호 순으로 정렬하여 표시 (1,2,3 순서)
                sorted_disk_numbers = sorted(self.selected_disks)
                selected_disks = [disk_num - 1 for disk_num in sorted_disk_numbers]
                print(f"선택된 디스크 번호: {self.selected_disks}")
                print(f"정렬된 디스크 번호: {sorted_disk_numbers}")
                print(f"선택된 디스크 인덱스: {selected_disks}")
            else:
                # 선택된 디스크가 없으면 모든 디스크 표시 (기존 방식)
                selected_disks = [0, 1, 2]
                print("선택된 디스크 없음 - 모든 디스크 표시")
            
            y_offset = -20  # 제목 아래쪽에서 시작
            for i, disk_index in enumerate(selected_disks):
                print(f"디스크 {disk_index+1} 상태 표시 생성 중")
                # 디스크 이름과 상태 표시
                label = lv.label(self.screen_obj)
                label.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
                label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
                label.align(lv.ALIGN.CENTER, 0, y_offset + i * 20)
                
                # 한국어 폰트 적용
                korean_font = getattr(lv, "font_notosans_kr_regular", None)
                if korean_font:
                    label.set_style_text_font(korean_font, 0)
                
                # 디스크 상태가 없으면 초기화
                if not hasattr(self, 'disk_states') or not self.disk_states:
                    self._ensure_disk_states()
                
                if disk_index in self.disk_states:
                    loaded_count = self.disk_states[disk_index].loaded_count
                    total_count = self.disk_states[disk_index].total_compartments
                    label.set_text(f"디스크{disk_index+1}  {loaded_count}/{total_count}")
                    print(f"디스크 {disk_index+1} 상태: {loaded_count}/{total_count}")
                else:
                    label.set_text(f"디스크{disk_index+1}  0/15")
                    print(f"디스크 {disk_index+1} 상태: 0/15 (기본값)")
                
                self.disk_status_labels.append(label)
            
            print("디스크별 상태 표시 생성 완료")
                
        except Exception as e:
            print(f"디스크 상태 표시 생성 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _get_meal_names_by_pattern(self):
        """복용 패턴에 따른 식사 이름들 반환"""
        try:
            print(f"[DEBUG] dose_times 전체 구조: {self.dose_times}")
            
            # 복용 패턴에 따른 식사 이름들
            if hasattr(self, 'dose_times') and self.dose_times:
                meal_names = []
                for dose_time in self.dose_times:
                    print(f"[DEBUG] dose_time 항목: {dose_time}")
                    if isinstance(dose_time, dict):
                        # meal_name 키가 있으면 사용
                        if 'meal_name' in dose_time:
                            meal_names.append(dose_time['meal_name'])
                        # meal 키가 있으면 사용
                        elif 'meal' in dose_time:
                            meal_names.append(dose_time['meal'])
                    elif isinstance(dose_time, str):
                        # 문자열인 경우 직접 사용
                        meal_names.append(dose_time)
                print(f"[DEBUG] dose_times에서 식사 이름 추출: {meal_names}")
                return meal_names
            else:
                # 기본값
                print(f"[DEBUG] dose_times가 없어서 기본값 사용")
                return ["아침약", "점심약", "저녁약"]
        except Exception as e:
            print(f"[DEBUG] _get_meal_names_by_pattern 오류: {e}")
            return ["아침약", "점심약", "저녁약"]
    
    def _create_loading_screen_directly(self):
        """순차적 충전 모드에서 바로 충전 화면을 메인 화면으로 생성"""
        try:
            # print(f"  [INFO] 직접 충전 화면 생성 시작...")
            
            # 첫 번째 디스크 설정
            if self.sequential_disks:
                # print(f"  [DEBUG] sequential_disks: {self.sequential_disks}")
                self.selected_disk_index = self.sequential_disks[0]
                # print(f"  [DEBUG] selected_disk_index: {self.selected_disk_index}")
                self._ensure_disk_states()
                # print(f"  [DEBUG] disk_states keys: {list(self.disk_states.keys()) if hasattr(self, 'disk_states') else 'None'}")
                # print(f"  [DEBUG] disk_states: {self.disk_states}")
                self.current_disk_state = self.disk_states[self.selected_disk_index]
                self.current_mode = 'loading'
                
                # 제목 생성/업데이트
                # 자동 할당된 디스크가 있는지 먼저 확인
                try:
                    from data_manager import DataManager
                    data_manager = DataManager()
                    auto_assigned_disks = data_manager.get_auto_assigned_disks()
                    # print(f"  [DEBUG] _switch_to_disk_loading에서 auto_assigned_disks 확인: {auto_assigned_disks}")
                    # print(f"  [DEBUG] auto_assigned_disks 타입: {type(auto_assigned_disks)}")
                    # print(f"  [DEBUG] auto_assigned_disks 길이: {len(auto_assigned_disks) if auto_assigned_disks else 'None'}")
                    
                    if auto_assigned_disks and len(auto_assigned_disks) > 0:
                        # 자동 할당된 디스크 모드: 식사 시간 이름 표시
                        # print(f"  [DEBUG] 자동 할당된 디스크 모드 - 식사 시간 이름으로 표시")
                        meal_name = self._get_meal_name_by_disk(self.selected_disk_index)
                        # print(f"  [DEBUG] meal_name: {meal_name}")
                        if not hasattr(self, 'title_text') or self.title_text is None:
                            # print(f"  [DEBUG] title_text 새로 생성")
                            self.title_text = lv.label(self.screen_obj)
                            self.title_text.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
                            self.title_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
                            self.title_text.align(lv.ALIGN.TOP_MID, 0, 10)
                            # 한국어 폰트 적용
                            korean_font = getattr(lv, "font_notosans_kr_regular", None)
                            if korean_font:
                                self.title_text.set_style_text_font(korean_font, 0)
                        else:
                            # print(f"  [DEBUG] 기존 title_text 사용")
                            pass
                        self.title_text.set_text(f"{meal_name}약 충전")
                        title_text = f"{meal_name}약 충전"
                        # print(f"  [DEBUG] 제목 설정 완료: {title_text}")
                    elif hasattr(self, 'selected_disks') and self.selected_disks:
                        # 수동 선택된 디스크 모드: 디스크 번호 표시
                        # print(f"  [DEBUG] 수동 선택된 디스크 모드 - 디스크 번호로 표시")
                        # print(f"  [DEBUG] selected_disks: {self.selected_disks}")
                        # sequential_disks에서 현재 인덱스에 해당하는 디스크 번호 찾기
                        if self.sequential_disks and self.current_sequential_index < len(self.sequential_disks):
                            disk_index = self.sequential_disks[self.current_sequential_index]
                            disk_num = disk_index + 1  # 인덱스를 디스크 번호로 변환
                            # print(f"  [DEBUG] sequential_disks에서 디스크 번호 계산: {disk_index} -> {disk_num}")
                        else:
                            disk_num = self.selected_disk_index + 1  # 폴백
                            # print(f"  [DEBUG] 폴백으로 디스크 번호 계산: {self.selected_disk_index} -> {disk_num}")
                        if not hasattr(self, 'title_text') or self.title_text is None:
                            # print(f"  [DEBUG] title_text 새로 생성")
                            self.title_text = lv.label(self.screen_obj)
                            self.title_text.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
                            self.title_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
                            self.title_text.align(lv.ALIGN.TOP_MID, 0, 10)
                            # 한국어 폰트 적용
                            korean_font = getattr(lv, "font_notosans_kr_regular", None)
                            if korean_font:
                                self.title_text.set_style_text_font(korean_font, 0)
                        else:
                            # print(f"  [DEBUG] 기존 title_text 사용")
                            pass
                        self.title_text.set_text(f"디스크 {disk_num} 충전")
                        title_text = f"디스크 {disk_num} 충전"
                        # print(f"  [DEBUG] 제목 설정 완료: {title_text}")
                    else:
                        # 기존 모드: 식사 시간 표시
                        meal_name = self._get_meal_name_by_disk(self.selected_disk_index)
                        if not hasattr(self, 'title_text') or self.title_text is None:
                            self.title_text = lv.label(self.screen_obj)
                            self.title_text.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
                            self.title_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
                            self.title_text.align(lv.ALIGN.TOP_MID, 0, 10)
                            # 한국어 폰트 적용
                            korean_font = getattr(lv, "font_notosans_kr_regular", None)
                            if korean_font:
                                self.title_text.set_style_text_font(korean_font, 0)
                        self.title_text.set_text(f"{meal_name}약 충전")
                        title_text = f"{meal_name}약 충전"
                except Exception as e:
                    # print(f"  [WARN] 제목 설정 중 오류: {e}")
                    # 폴백: 식사 시간 표시
                    meal_name = self._get_meal_name_by_disk(self.selected_disk_index)
                    if not hasattr(self, 'title_text') or self.title_text is None:
                        self.title_text = lv.label(self.screen_obj)
                        self.title_text.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
                        self.title_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
                        self.title_text.align(lv.ALIGN.TOP_MID, 0, 10)
                        # 한국어 폰트 적용
                        korean_font = getattr(lv, "font_notosans_kr_regular", None)
                        if korean_font:
                            self.title_text.set_style_text_font(korean_font, 0)
                    self.title_text.set_text(f"{meal_name}약 충전")
                    title_text = f"{meal_name}약 충전"
                
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
                self.progress_arc.set_style_arc_color(lv.color_hex(0xd2b13f), lv.PART.INDICATOR)  # 진행 로고 색상
                
                # 아크 노브 색상 설정 (아크와 동일한 로고 색상)
                try:
                    self.progress_arc.set_style_bg_color(lv.color_hex(0xd2b13f), lv.PART.KNOB)
                    self.progress_arc.set_style_bg_opa(255, lv.PART.KNOB)
                    # print(f"  [OK] 아크 노브 색상 설정 완료 (로고 색상)")
                except AttributeError:
                    # print(f"  [WARN] lv.PART.KNOB 지원 안됨, 건너뛰기")
                    pass
                
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
                
                # 버튼 힌트는 _create_modern_screen에서 생성됨
                
                # print(f"  [OK] 직접 충전 화면 생성 완료: {title_text}")
                
        except Exception as e:
            # print(f"  [ERROR] 직접 충전 화면 생성 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _update_loading_screen(self):
        """충전 화면 실시간 업데이트"""
        try:
            print("충전 화면 실시간 업데이트 시작...")
            
            # 현재 디스크 상태 확인
            if not hasattr(self, 'current_disk_state') or not self.current_disk_state:
                print("현재 디스크 상태가 없음")
                return
            
            # 진행률 업데이트
            if hasattr(self, 'progress_arc') and hasattr(self, 'progress_label'):
                progress = self.current_disk_state.get_loading_progress()
                arc_angle = int((progress / 100) * 360)
                self.progress_arc.set_angles(0, arc_angle)
                self.progress_label.set_text(f"{progress:.0f}%")
                print(f"진행률 업데이트: {progress:.0f}%")
            
            # 세부 정보 업데이트
            if hasattr(self, 'detail_label'):
                loaded_count = self.current_disk_state.loaded_count
                self.detail_label.set_text(f"{loaded_count}/15칸")
                print(f"세부 정보 업데이트: {loaded_count}/15칸")
            
            # 디스크 상태 표시 업데이트
            self._update_disk_visualization()
            
            # LVGL 화면 갱신
            import lvgl as lv
            lv.timer_handler()
            
            print("충전 화면 실시간 업데이트 완료")
            
        except Exception as e:
            print(f"충전 화면 업데이트 실패: {e}")
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
        self.title_text.set_text("")
        self.title_text.align(lv.ALIGN.CENTER, 0, 0)
        self.title_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.title_text.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
        
        # 한국어 폰트 적용
        korean_font = getattr(lv, "font_notosans_kr_regular", None)
        if korean_font:
            self.title_text.set_style_text_font(korean_font, 0)
        
        # print("  [OK] 상단 상태 컨테이너 생성 완료")
    
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
        
        # print("  [OK] 중앙 메인 컨테이너 생성 완료")
    
    def _create_disk_selection_area(self):
        """디스크 선택 영역 생성"""
        try:
            if self.sequential_mode:
                # 순차적 충전 모드에서는 디스크 선택 영역을 생성하지 않음
                # print("  [INFO] 순차적 충전 모드 - 디스크 선택 영역 생략")
                self.disk_label = None
                self.disk_roller = None
                return
            
            # 순차적 충전 모드만 사용 - 디스크 선택 영역 불필요
            self.disk_label = None
            self.disk_roller = None
            
            # print("  [OK] 디스크 선택 영역 생성 완료")
            
        except Exception as e:
            # print(f"  [ERROR] 디스크 선택 영역 생성 실패: {e}")
    
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
        self.hints_text.set_text(f"A:{lv.SYMBOL.DOWNLOAD} B:- C:{lv.SYMBOL.CLOSE} D:{lv.SYMBOL.NEXT}")
        self.hints_text.align(lv.ALIGN.CENTER, 0, 0)
        self.hints_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.hints_text.set_style_text_color(lv.color_hex(0x8E8E93), 0)
        # lv 기본 폰트 사용 (한국어 폰트 적용하지 않음)
        
        # 스크롤바 비활성화
        self.hints_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        self.hints_container.set_scroll_dir(lv.DIR.NONE)
    
        # print("  [OK] 하단 버튼힌트 컨테이너 생성 완료")

    def _update_disk_visualization(self):
        """디스크 상태 표시 업데이트 (간단한 텍스트 기반)"""
        try:
            print("디스크 상태 표시 업데이트 시작...")
            
            # 디스크 상태 표시 업데이트
            self._update_disk_status_display()
            
            # LVGL 화면 갱신
            import lvgl as lv
            lv.timer_handler()
            
            print("디스크 상태 표시 업데이트 완료")
            
        except Exception as e:
            print(f"디스크 상태 표시 업데이트 실패: {e}")
            import sys
            sys.print_exception(e)

    def on_button_a(self):
        """버튼 A 처리 - 모든 디스크 동시 회전, 선택된 디스크들에 3칸씩 충전"""
        print(f"A버튼: 현재 모드 = {self.current_mode}")
        
        # 충전 모드로 전환 (아직 충전 모드가 아닌 경우)
        if self.current_mode != 'loading':
            print("충전 모드로 전환")
            self.current_mode = 'loading'
            
            # 순차적 충전 모드인 경우 첫 번째 디스크로 설정
            if self.sequential_mode and self.sequential_disks:
                print("순차적 충전 모드 - 첫 번째 디스크로 설정")
                self.current_sequential_index = 0
                self.selected_disk_index = self.sequential_disks[0]
                self.current_disk_state = self.disk_states[self.selected_disk_index]
            else:
                # 개별 선택 모드인 경우 첫 번째 디스크로 설정
                print("개별 선택 모드 - 첫 번째 디스크로 설정")
                self.selected_disk_index = 0
                self.current_disk_state = self.disk_states[0]
        
        print("A버튼: 모든 디스크 동시 회전으로 3칸씩 충전 실행")
        
        # 선택된 디스크들이 더 충전할 수 있는지 확인
        can_load_more = False
        for disk_idx in range(3):
            if self._is_disk_selected(disk_idx) and disk_idx in self.disk_states:
                if self.disk_states[disk_idx].can_load_more():
                    can_load_more = True
                    break
        
        if can_load_more:
            print("충전 시작: 모든 디스크 동시 회전")
            
            # 실제 모터 제어 실행 (모든 디스크 동시 회전, 선택된 디스크들에만 알약 개수 업데이트)
            success = self._real_loading(self.current_disk_state.disk_id)
            if success:
                print("충전 완료: 선택된 디스크들에 3칸씩 추가")
                
                # 화면 실시간 업데이트
                self._update_loading_screen()
                
                # 디스크 상태 저장
                self._save_disk_states()
                
                # 완충 감지 및 다음 단계 처리
                self._check_completion_and_proceed()
            else:
                print("충전 실패")
        else:
            print("더 이상 충전할 칸이 없습니다")
            # 모든 디스크가 완료되었는지 확인
            if self.sequential_mode:
                print("모든 디스크 충전 완료 - 메인화면으로 이동")
                self._complete_sequential_loading()
            else:
                print("개별 선택 모드 - 모든 선택된 디스크 충전 완료")
                self._complete_individual_loading()
    
    def on_button_b(self):
        """버튼 B 처리 - 기능 없음"""
        # 원점 정렬 기능 제거됨
        pass
    
    def on_button_c(self):
        """버튼 C 처리 - 뒤로가기"""
        print(f"C버튼: 현재 모드 = {self.current_mode}")
        print(f"C버튼: sequential_mode = {self.sequential_mode}")
        print(f"C버튼: dose_times 길이 = {len(self.dose_times) if self.dose_times else 0}")
        
        try:
            print("C버튼: 뒤로가기 처리 시작")
            
            # 현재 충전 상태 저장
            print("뒤로가기 전 충전 상태 저장")
            self._save_disk_states()
            
            # 복용 횟수에 따른 뒤로가기 처리
            dose_count = len(self.dose_times) if self.dose_times else 1
            print(f"현재 복용 횟수: {dose_count}")
            
            # 순차적 충전 모드에서 이전 디스크로 돌아가기
            if self.sequential_mode and self.sequential_disks and self.current_sequential_index > 0:
                # 이전 디스크로 이동
                self.current_sequential_index -= 1
                previous_disk_index = self.sequential_disks[self.current_sequential_index]
                disk_num = previous_disk_index + 1
                
                print(f"뒤로가기 - 디스크 {disk_num}로 이동")
                
                # 이전 디스크 충전 화면으로 전환
                self._switch_to_disk_loading(previous_disk_index)
                print(f"디스크 {disk_num} 충전 화면으로 이동 완료")
                
            else:
                # 첫 번째 디스크인 경우 복용 횟수에 따라 분기
                if dose_count >= 2:
                    # 복용 횟수가 2 이상이면 복용 시간 설정 화면으로
                    print("뒤로가기 - 복용 시간 설정 화면으로 이동 (복용 횟수 2 이상)")
                    self._request_screen_transition_to_dose_time()
                    print("복용 시간 설정 화면으로 이동 완료")
                else:
                    # 복용 횟수가 1이면 디스크 선택 화면으로
                    print("뒤로가기 - 디스크 선택 화면으로 이동 (복용 횟수 1)")
                    self._request_screen_transition_to_disk_selection()
                    print("디스크 선택 화면으로 이동 완료")
            
            print("C버튼 뒤로가기 처리 완료")
                    
        except Exception as e:
            print(f"뒤로가기 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _switch_to_disk_loading(self, disk_index):
        """특정 디스크 충전 화면으로 전환"""
        try:
            # print(f"  [INFO] 디스크 {disk_index + 1} 충전 화면으로 전환 시작...")
            
            # 디스크 상태가 존재하는지 확인
            if disk_index not in self.disk_states:
                # print(f"  [WARN] 디스크 {disk_index + 1} 상태가 없음, 새로 생성")
                self.disk_states[disk_index] = DiskState(disk_index)
            
            # 현재 디스크 상태 설정
            self.selected_disk_index = disk_index
            self.current_disk_state = self.disk_states[disk_index]
            self.current_mode = 'loading'
            
            # 화면 제목 업데이트 (자동 할당 디스크 로직 사용)
            try:
                from data_manager import DataManager
                data_manager = DataManager()
                auto_assigned_disks = data_manager.get_auto_assigned_disks()
                # print(f"  [DEBUG] _switch_to_disk_loading에서 auto_assigned_disks 확인: {auto_assigned_disks}")
                
                if auto_assigned_disks and len(auto_assigned_disks) > 0:
                    # 자동 할당된 디스크 모드: 식사 시간 이름 표시
                    # print(f"  [DEBUG] 자동 할당된 디스크 모드 - 식사 시간 이름으로 표시")
                    meal_name = self._get_meal_name_by_disk(disk_index)
                    # print(f"  [DEBUG] meal_name: {meal_name}")
                    if hasattr(self, 'title_text') and self.title_text:
                        self.title_text.set_text(f"{meal_name}약 충전")
                        # print(f"  [OK] 제목 업데이트 완료: {meal_name}약 충전")
                elif hasattr(self, 'selected_disks') and self.selected_disks:
                    # 수동 선택된 디스크 모드: 디스크 번호 표시
                    # print(f"  [DEBUG] 수동 선택된 디스크 모드 - 디스크 번호로 표시")
                    disk_num = disk_index + 1
                    if hasattr(self, 'title_text') and self.title_text:
                        self.title_text.set_text(f"디스크 {disk_num} 충전")
                        # print(f"  [OK] 제목 업데이트 완료: 디스크 {disk_num} 충전")
                else:
                    # 기존 모드: 식사 시간 표시
                    meal_name = self._get_meal_name_by_disk(disk_index)
                    if hasattr(self, 'title_text') and self.title_text:
                        self.title_text.set_text(f"{meal_name}약 충전")
                        # print(f"  [OK] 제목 업데이트 완료: {meal_name}약 충전")
            except Exception as e:
                # print(f"  [WARN] 제목 업데이트 중 오류: {e}")
                # 폴백: 디스크 번호 표시
                disk_num = disk_index + 1
                if hasattr(self, 'title_text') and self.title_text:
                    self.title_text.set_text(f"디스크 {disk_num} 충전")
                    # print(f"  [OK] 제목 업데이트 완료 (폴백): 디스크 {disk_num} 충전")
            
            # 충전 화면 업데이트
            self._update_loading_screen()
            # print(f"  [OK] 디스크 {disk_index + 1} 충전 화면 전환 완료")
            
        except Exception as e:
            # print(f"  [ERROR] 디스크 충전 화면 전환 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def on_button_d(self):
        """버튼 D 처리 - 재부팅 후 메인화면에서 시작"""
        try:
            print("D버튼: 재부팅 후 메인화면에서 시작")
            
            # DataManager에 약물 수량 저장
            print("DataManager에 약물 수량 저장")
            self._save_medication_data_to_datamanager()
            
            # 설정 완료 메시지 표시
            print("설정 완료 메시지 표시")
            self._show_completion_message()
            
            # 흰색 화면 만들기
            print("흰색 화면 만들기")
            self._make_screen_white()
            
            # 부팅 타겟을 메인화면으로 설정
            print("부팅 타겟을 메인화면으로 설정")
            self._set_boot_target_to_main()
            
            # 잠시 대기 후 재부팅
            import time
            time.sleep(0.1)
            
            print("ESP 리셋 시작...")
            import machine
            machine.reset()
            
        except Exception as e:
            print(f"D버튼 처리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _set_boot_target_to_main(self):
        """부팅 타겟을 메인화면으로 설정"""
        try:
            print("부팅 타겟 설정 시작...")
            
            # /data 디렉토리 존재 확인 및 생성
            import os
            data_dir = "/data"
            try:
                if data_dir not in os.listdir("/"):
                    os.mkdir(data_dir)
                    print("/data 디렉토리 생성됨")
            except OSError as e:
                if e.errno == 17:  # EEXIST - 디렉토리가 이미 존재
                    print("/data 디렉토리가 이미 존재함")
                    pass
                else:
                    raise
            
            # boot_target.json 파일 생성 (main.py에서 읽는 경로와 동일)
            boot_config = {
                "boot_target": "main"
            }
            
            import json
            boot_file = "/data/boot_target.json"
            with open(boot_file, "w") as f:
                json.dump(boot_config, f)
            
            print("부팅 타겟 설정 완료: 메인화면")
            
        except Exception as e:
            print(f"부팅 타겟 설정 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def update(self):
        """화면 업데이트 - ScreenManager에서 호출됨"""
        # 현재는 특별한 업데이트 로직이 없음
        # 필요시 여기에 주기적 업데이트 로직 추가
        pass
    

    def _real_loading(self, disk_index):
        """실제 모터 제어를 통한 알약 충전 (모든 디스크 동시 회전, 선택된 디스크들에 알약 개수 업데이트)"""
        print("실제 모터 제어: 모든 디스크 동시 회전 시작")
        
        try:
            self._ensure_motor_system()
            if not self.motor_system or not self.motor_system.motor_controller:
                print("모터 시스템이 초기화되지 않음")
                return False
            
            # 충전 시작 전 모든 모터 코일 OFF (전력 소모 방지)
            print("충전 시작 전 모든 모터 코일 OFF")
            self.motor_system.motor_controller.stop_all_motors()
            
            # 모든 디스크의 상태를 시작 상태로 설정
            all_disks_ready = True
            for disk_idx in range(3):  # 디스크 0, 1, 2
                if disk_idx in self.disk_states:
                    if not self.disk_states[disk_idx].start_loading():
                        all_disks_ready = False
                        break
            
            if all_disks_ready:
                # print(f"  [INFO] 모든 디스크 모터 회전 시작 (리미트 스위치 눌림 감지 3번까지)")
                
                # 모든 디스크의 리미트 스위치 상태 추적 변수
                prev_limit_states = [False, False, False]
                current_limit_states = [False, False, False]
                step_count = 0
                max_steps = 8000  # 최대 8000스텝 후 강제 종료 (안전장치)
                
                # 초기 리미트 스위치 상태 확인 (모든 디스크)
                for motor_idx in range(1, 4):  # 모터 번호 1, 2, 3
                    current_limit_states[motor_idx - 1] = self.motor_system.motor_controller.is_limit_switch_pressed(motor_idx)
                    # print(f"  [INFO] 디스크 {motor_idx} 초기 리미트 스위치 상태: {'눌림' if current_limit_states[motor_idx - 1] else '안눌림'}")
                
                # 초기 상태가 눌린 경우 첫 번째 감지를 무시하기 위한 플래그
                skip_first_detections = current_limit_states.copy()
                
                try:
                    # 모든 디스크 동시 회전 + 리미트 스위치 감지 방식
                    motor_controller = self.motor_system.motor_controller
                    import time
                    
                    # 모든 모터를 먼저 정지
                    motor_controller.stop_all_motors()
                    
                    # 모든 디스크를 동시에 3칸씩 이동 (리미트 스위치 감지)
                    step_count = 0
                    limit_released = [False, False, False]  # 각 디스크별 리미트 스위치 해제 상태
                    compartment_count = [0, 0, 0]  # 각 디스크별 이동한 칸 수
                    compartment_done = [False, False, False]  # 각 디스크별 3칸 이동 완료 상태
                    counting_started = [False, False, False]  # 각 디스크별 카운트 시작 상태
                    
                    while not all(compartment_done):  # 안전장치 증가
                        step_count += 1
                        
                        # 모든 모터를 동시에 1스텝씩 진행 (내부 상태만 업데이트)
                        for motor_idx in range(1, 4):  # 모터 번호 1, 2, 3
                            if not compartment_done[motor_idx - 1]:
                                motor_controller.motor_steps[motor_idx] = (motor_controller.motor_steps[motor_idx] - 1) % 8
                                current_step = motor_controller.motor_steps[motor_idx]
                                motor_controller.motor_states[motor_idx] = motor_controller.stepper_sequence[current_step]
                        
                        # 모터4는 항상 OFF 상태로 유지
                        motor_controller.motor_states[4] = 0x00
                        
                        motor_controller.update_motor_output()
                        
                        # 회전 속도 조절 (더 빠르게)
                        time.sleep_us(1000)
                        
                        # 최적화: 10스텝마다만 시프트 레지스터 출력 및 리미트 스위치 감지
                        if step_count % 50 == 0:
                            # 모든 모터 상태를 한 번에 출력 (10스텝마다)
                            
                            # 리미트 스위치 상태 확인 (10스텝마다)
                            for motor_idx in range(1, 4):  # 모터 번호 1, 2, 3
                                if not compartment_done[motor_idx - 1]:
                                    is_pressed = motor_controller.is_limit_switch_pressed(motor_idx)
                                    
                                    if not is_pressed and not limit_released[motor_idx - 1]:
                                        # 리미트 스위치가 떼어짐 - 카운트 시작
                                        limit_released[motor_idx - 1] = True
                                        counting_started[motor_idx - 1] = True
                                    elif is_pressed and limit_released[motor_idx - 1] and counting_started[motor_idx - 1]:
                                        # 리미트 스위치가 다시 눌림 - 1칸 이동 완료
                                        compartment_count[motor_idx - 1] += 1
                                        limit_released[motor_idx - 1] = False  # 다음 칸을 위해 리셋
                                        
                                        # 3칸 이동 완료 확인 (4번째 눌림 시에 3칸으로 업데이트)
                                        if compartment_count[motor_idx - 1] >= 3:
                                            compartment_done[motor_idx - 1] = True
                    
                    # 모든 디스크가 3칸씩 이동한 후 알약 개수 업데이트 (완료된 디스크만)
                    if all(compartment_done):
                        print("모든 디스크 3칸 이동 완료 - 알약 개수 업데이트")
                        for disk_idx in range(3):
                            if self._is_disk_selected(disk_idx):
                                # 3칸씩 추가 (15칸 완료되면 15로 설정)
                                old_count = self.disk_states[disk_idx].loaded_count
                                if self.disk_states[disk_idx].loaded_count + 3 >= 15:
                                    self.disk_states[disk_idx].loaded_count = 15
                                    self.disk_states[disk_idx].is_loading = False
                                    print(f"디스크 {disk_idx+1}: {old_count} → 15 (완료)")
                                else:
                                    self.disk_states[disk_idx].loaded_count += 3
                                    print(f"디스크 {disk_idx+1}: {old_count} → {self.disk_states[disk_idx].loaded_count}")
                    else:
                        print("일부 디스크 이동 미완료")
                        pass                    
                    
                    # 모든 모터 코일 OFF (전력 소모 방지)
                    print("모든 모터 코일 OFF")
                    motor_controller.stop_all_motors()
                    
                    # 실시간 화면 업데이트
                    print("실시간 화면 업데이트 시작")
                    self._update_disk_visualization()
                    time.sleep(0.1)
                    
                    # 디스크 상태 저장
                    print("디스크 상태 저장")
                    self._save_disk_states()
                    
                    # 완충 감지 및 다음 단계 처리
                    self._check_completion_and_proceed()
                    
                    print("모터 제어 완료")
                    return True
                
                except Exception as e:
                    # print(f"  [ERROR] 모터 제어 중 오류: {e}")
                    # 오류 발생 시에도 모든 모터 정지
                    for motor_idx in range(1, 4):
                        self.motor_system.motor_controller.stop_motor(motor_idx)
                    return False
                
                # [FAST] 충전 완료 후 모든 모터 코일 OFF (전력 소모 방지)
                # print(f"  [FAST] 충전 완료, 모든 모터 코일 OFF")
                for motor_idx in range(1, 4):
                    self.motor_system.motor_controller.stop_motor(motor_idx)
                
                # 완전히 충전된 경우 확인
                if not self.current_disk_state.can_load_more():
                    # print("  [SUCCESS] 실제 모터: 디스크 충전 완료! (15/15칸)")
                    # 충전 완료 - 수동으로 완료 버튼을 눌러야 함
                    # print("  [INFO] 완료 버튼(C)을 눌러 디스크 선택 화면으로 돌아가세요")
                    return True
                
                return True
            else:
                # print("  [INFO] 실제 모터: 더 이상 충전할 수 없습니다")
                return False
                
        except Exception as e:
            # print(f"  [ERROR] 실제 모터 충전 실패: {e}")
            return False
    
    
    def _save_disk_states(self):
        """디스크 충전 상태를 파일에 저장"""
        try:
            print("디스크 충전 상태 저장 시작...")
            
            # /data 디렉토리 존재 확인 및 생성
            import os
            data_dir = "/data"
            try:
                if data_dir not in os.listdir("/"):
                    os.mkdir(data_dir)
                    print("/data 디렉토리 생성됨")
            except OSError as e:
                if e.errno == 17:  # EEXIST - 디렉토리가 이미 존재
                    print("/data 디렉토리가 이미 존재함")
                    pass
                else:
                    raise
            
            # 실제로 존재하는 디스크 상태만 저장
            config = {
                'disk_1_loaded': self.disk_states.get(0, DiskState(0)).loaded_count if 0 in self.disk_states else 0,
                'disk_2_loaded': self.disk_states.get(1, DiskState(1)).loaded_count if 1 in self.disk_states else 0,
                'disk_3_loaded': self.disk_states.get(2, DiskState(2)).loaded_count if 2 in self.disk_states else 0,
                'saved_at': time.time()
            }
            
            import json  # 지연 임포트
            with open(self.disk_states_file, 'w') as f:
                json.dump(config, f)
            
            print(f"디스크 충전 상태 저장됨: 디스크1={config['disk_1_loaded']}, 디스크2={config['disk_2_loaded']}, 디스크3={config['disk_3_loaded']}")
            print("디스크 충전 상태 저장 완료")
            
        except Exception as e:
            print(f"디스크 충전 상태 저장 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _load_disk_states(self):
        """저장된 디스크 충전 상태 불러오기 (자동 할당된 디스크만)"""
        try:
            # DataManager에서 실제 약물 수량 불러오기
            from data_manager import DataManager
            data_manager = DataManager()
            
            # 자동 할당된 디스크 정보 확인
            auto_assigned_disks = data_manager.get_auto_assigned_disks()
            unused_disks = data_manager.get_unused_disks()
            
            if auto_assigned_disks:
                # 자동 할당된 디스크만 사용
                # print(f"[INFO] 자동 할당된 디스크만 충전: {len(auto_assigned_disks)}개")
                
                for disk_info in auto_assigned_disks:
                    disk_number = disk_info['disk_number']  # 1, 2, 3
                    disk_index = disk_number - 1  # 0, 1, 2 (배열 인덱스)
                    
                    self.disk_states[disk_index] = DiskState(disk_index)
                    # DataManager에서 실제 수량 가져오기
                    current_count = data_manager.get_disk_count(disk_number)
                    self.disk_states[disk_index].loaded_count = current_count
                    
                    # print(f"[INFO] 디스크 {disk_number} ({disk_info['meal_name']}): {current_count}개")
                
                # 사용하지 않는 디스크는 생성하지 않음
                if unused_disks:
                    # print(f"[INFO] 사용하지 않는 디스크: {unused_disks}")
                    pass
            else:
                # 자동 할당 정보가 없으면 모든 디스크 사용 (기존 방식)
                # print("[INFO] 자동 할당 정보 없음 - 모든 디스크 사용")
                for i in range(3):
                    self.disk_states[i] = DiskState(i)
                    # DataManager에서 실제 수량 가져오기
                    disk_num = i + 1  # 디스크 번호 (1, 2, 3)
                    current_count = data_manager.get_disk_count(disk_num)
                    self.disk_states[i].loaded_count = current_count
            
            # 로드된 디스크 상태 출력
            loaded_disks = []
            for disk_index, disk_state in self.disk_states.items():
                loaded_disks.append(f"디스크{disk_index+1}:{disk_state.loaded_count}")
            # print(f"  📂 디스크 충전 상태 불러옴: {', '.join(loaded_disks)}")
            
        except Exception as e:
            # print(f"  [WARN] 저장된 디스크 충전 상태 없음: {e}")
            # 파일이 없거나 오류 시 기본 상태로 초기화 (디스크 번호 0, 1, 2)
            for i in range(3):
                self.disk_states[i] = DiskState(i)
    
    
    def _update_status(self, status_text):
        """상태 텍스트 업데이트"""
        try:
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.set_text(status_text)
                # print(f"[INFO] 상태 업데이트: {status_text}")
        except Exception as e:
            # print(f"[ERROR] 상태 업데이트 실패: {e}")
            pass
    
    def _request_screen_transition_to_disk_selection(self):
        """디스크 선택 화면으로 전환 요청 - ScreenManager에 위임 (다른 화면들과 동일한 방식)"""
        print("디스크 선택 화면으로 전환 요청")
        
        # ScreenManager에 화면 전환 요청 (올바른 책임 분리)
        try:
            self.screen_manager.transition_to('disk_selection')
            print("디스크 선택 화면으로 전환 요청 완료")
        except Exception as e:
            print(f"디스크 선택 화면 전환 요청 실패: {e}")
            import sys
            sys.print_exception(e)
        
        # ScreenManager에 알약 충전 뒤로가기 신호 전송 (올바른 책임 분리)
        try:
            self.screen_manager.pill_loading_back_to_disk_selection()
            print("알약 충전 뒤로가기 신호 전송 완료")
        except Exception as e:
            print(f"알약 충전 뒤로가기 신호 전송 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _request_screen_transition_to_dose_time(self):
        """복용 시간 설정 화면으로 전환 요청 - ScreenManager에 위임 (다른 화면들과 동일한 방식)"""
        print("복용 시간 설정 화면으로 전환 요청")
        
        # ScreenManager에 화면 전환 요청 (올바른 책임 분리)
        try:
            self.screen_manager.transition_to('dose_time')
            print("복용 시간 설정 화면으로 전환 요청 완료")
        except Exception as e:
            print(f"복용 시간 설정 화면 전환 요청 실패: {e}")
            import sys
            sys.print_exception(e)
        
        # ScreenManager에 알약 충전 뒤로가기 신호 전송 (올바른 책임 분리)
        try:
            self.screen_manager.pill_loading_back_to_dose_time()
            print("알약 충전 뒤로가기 신호 전송 완료")
        except Exception as e:
            print(f"알약 충전 뒤로가기 신호 전송 실패: {e}")
            import sys
            sys.print_exception(e)

    def _request_screen_transition(self):
        """화면 전환 요청 - ScreenManager에 위임 (다른 화면들과 동일한 방식)"""
        # print("[INFO] 화면 전환 요청")
        
        # ScreenManager에 화면 전환 요청 (올바른 책임 분리)
        try:
            self.screen_manager.transition_to('main')
            # print("[OK] 화면 전환 요청 완료")
        except Exception as e:
            # print(f"[ERROR] 화면 전환 요청 실패: {e}")
            import sys
            sys.print_exception(e)
        
        # 화면 전환 (올바른 책임 분리 - ScreenManager가 처리)
        # print("[INFO] 알약 충전 완료 - ScreenManager에 완료 신호 전송")
        
        # ScreenManager에 알약 충전 완료 신호 전송 (올바른 책임 분리)
        try:
            self.screen_manager.pill_loading_completed()
            # print("[OK] 알약 충전 완료 신호 전송 완료")
        except Exception as e:
            # print(f"[ERROR] 알약 충전 완료 신호 전송 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _cleanup_display_pwm(self):
        """ST7735 디스플레이 PWM 정리 - 메모리 누수 방지"""
        try:
            # print("[INFO] PillLoadingScreen ST7735 디스플레이 PWM 정리 시작")
            
            # 디스플레이 객체가 있으면 PWM 정리
            if hasattr(self, 'screen_manager') and self.screen_manager:
                if hasattr(self.screen_manager, 'app') and self.screen_manager.app:
                    app = self.screen_manager.app
                    if hasattr(app, 'display') and app.display:
                        try:
                            # ST7735 cleanup 메서드 호출
                            if hasattr(app.display, 'cleanup'):
                                app.display.cleanup()
                                # print("[OK] PillLoadingScreen ST7735 디스플레이 PWM 정리 완료")
                            else:
                                # cleanup 메서드가 없으면 off() 메서드 호출
                                app.display.off()
                                # print("[OK] PillLoadingScreen ST7735 디스플레이 백라이트 끄기 완료")
                        except Exception as e:
                            # print(f"[WARN] PillLoadingScreen ST7735 디스플레이 정리 실패: {e}")
                            pass
            # print("[OK] PillLoadingScreen ST7735 디스플레이 PWM 정리 완료")
            
        except Exception as e:
            # print(f"[ERROR] PillLoadingScreen ST7735 디스플레이 PWM 정리 실패: {e}")
            pass
    
    def _monitor_memory(self, label):
        """메모리 사용량 모니터링 (MicroPython만)"""
        try:
            import micropython
            
            # MicroPython 메모리 정보만 확인
            mem_info = micropython.mem_info()
            # print(f"[{label}] MicroPython 메모리:")
            # print(f"  {mem_info}")
                    
        except Exception as e:
            # print(f"[WARN] 메모리 모니터 실패: {e}")
            pass
    def _cleanup_lvgl(self):
        """화면 전환 전 LVGL 객체 안전 정리 (ChatGPT 추천 방법)"""
        import lvgl as lv
        import gc
        import time
        
        # print("[INFO] PillLoadingScreen LVGL 정리 시작")
        
        # 메모리 모니터링 (정리 전)
        self._monitor_memory("BEFORE CLEANUP")
        
        try:
            # 1️⃣ 현재 화면 객체가 존재하면 자식부터 모두 삭제
            if hasattr(self, 'screen_obj') and self.screen_obj:
                try:
                    # 모든 자식 객체 삭제
                    while self.screen_obj.get_child_count() > 0:
                        child = self.screen_obj.get_child(0)
                        if child:
                            child.delete()
                    # print("[OK] LVGL 자식 객체 삭제 완료")
                except Exception as e:
                    # print(f"[WARN] 자식 삭제 중 오류: {e}")
                    pass
                # 화면 자체 삭제
                try:
                    self.screen_obj.delete()
                    # print("[OK] 화면 객체 삭제 완료")
                except Exception as e:
                    # print(f"[WARN] 화면 객체 삭제 실패: {e}")
                    pass
                self.screen_obj = None  # Python 참조 제거
            
            # 2️⃣ 스타일 / 폰트 등 Python 객체 참조 해제
            if hasattr(self, 'ui_style'):
                self.ui_style = None
            
            # 3️⃣ LVGL 내부 타이머 및 큐 정리
            try:
                lv.timer_handler()
            except:
                pass
            
            # 4️⃣ 가비지 컬렉션 (여러 번 수행)
            for i in range(3):
                gc.collect()
                time.sleep_ms(10)
            
            # 메모리 모니터링 (정리 후)
            self._monitor_memory("AFTER CLEANUP")
            
            # print("[OK] PillLoadingScreen LVGL 정리 완료")
            
        except Exception as e:
            # print(f"[ERROR] LVGL 정리 실패: {e}")
            pass