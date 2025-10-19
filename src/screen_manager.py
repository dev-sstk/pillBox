"""
화면 관리 시스템
모든 화면의 생성, 전환, 업데이트를 관리
"""

class ScreenManager:
    """화면 관리자 클래스"""
    
    def __init__(self, app=None):
        """화면 관리자 초기화"""
        self.screens = {}
        self.current_screen_name = None
        self.current_screen = None
        self.screen_stack = []  # 화면 스택 (뒤로가기 기능)
        self.app = app  # PillBoxApp 참조
        
        print("[OK] ScreenManager 초기화 완료")
    
    def register_screen(self, screen_name, screen_instance):
        """화면 등록"""
        print(f"[DEBUG] register_screen 시작: {screen_name}")
        print(f"[DEBUG] screen_instance: {screen_instance}")
        print(f"[DEBUG] screens 딕셔너리에 저장 시작...")
        self.screens[screen_name] = screen_instance
        print(f"[DEBUG] screens 딕셔너리에 저장 완료")
        print(f"[OK] 화면 등록: {screen_name}")
    
    def set_current_screen(self, screen_name):
        """현재 화면 설정"""
        if screen_name not in self.screens:
            print(f"[ERROR] 존재하지 않는 화면: {screen_name}")
            return False
        
        # 현재 화면이 있으면 참조만 정리
        if self.current_screen:
            print(f"[INFO] 이전 화면 참조 정리: {self.current_screen_name}")
        
        # 새 화면으로 전환
        self.current_screen_name = screen_name
        self.current_screen = self.screens[screen_name]
        self.current_screen.show()
        
        print(f"[INFO] 화면 전환: {screen_name}")
        return True
    
    def show_screen(self, screen_name, add_to_stack=True, **kwargs):
        """화면 전환 - 스타트업 화면은 완전 삭제"""
        print(f"[DEBUG] show_screen 메서드 시작: {screen_name}")
        
        # 현재 화면이 있으면 처리
        print(f"[DEBUG] 현재 화면 체크: current_screen={self.current_screen}, current_screen_name={self.current_screen_name}")
        if self.current_screen and self.current_screen_name:
            # 이전 화면 정리 (완전한 동적 로딩 방식)
            if self.current_screen_name != screen_name:
                print(f"[INFO] 이전 화면 정리 시작: {self.current_screen_name}")
                try:
                    self.cleanup_screen(self.current_screen_name)
                    print(f"[OK] 이전 화면 정리 완료: {self.current_screen_name}")
                except Exception as e:
                    print(f"[WARN] 이전 화면 정리 실패: {e}")
        else:
            print("[DEBUG] 현재 화면이 없음 - 새 화면으로 직접 전환")
        
        # 새 화면이 이미 존재하는지 확인
        print(f"[DEBUG] 화면 존재 여부 확인: {screen_name}")
        print(f"[DEBUG] 등록된 화면 목록: {list(self.screens.keys())}")
        if screen_name not in self.screens:
            # 새 화면 동적 생성
            print(f"[INFO] {screen_name} 화면 동적 생성 중...")
            if self.app and hasattr(self.app, 'create_and_register_screen'):
                self.app.create_and_register_screen(screen_name, **kwargs)
            else:
                # app 참조가 없으면 직접 화면 생성 시도
                self._create_screen_directly(screen_name, **kwargs)
            
            if screen_name not in self.screens:
                print(f"[ERROR] 화면 생성 실패: {screen_name}")
                return False
        else:
            print(f"[INFO] {screen_name} 화면이 이미 존재함, 재사용")
            
            # dose_time 화면의 경우 새로운 매개변수가 있으면 업데이트
            if screen_name == 'dose_time' and kwargs:
                dose_count = kwargs.get('dose_count')
                selected_meals = kwargs.get('selected_meals')
                if dose_count is not None or selected_meals is not None:
                    print(f"[INFO] dose_time 화면 상태 업데이트 중...")
                    try:
                        dose_screen = self.screens[screen_name]
                        if hasattr(dose_screen, 'update_meal_selections'):
                            dose_screen.update_meal_selections(dose_count, selected_meals)
                            print(f"[OK] dose_time 화면 상태 업데이트 완료")
                        else:
                            print(f"[WARN] dose_time 화면에 update_meal_selections 메서드가 없음")
                    except Exception as e:
                        print(f"[ERROR] dose_time 화면 상태 업데이트 실패: {e}")
        
        # 새 화면으로 전환
        print(f"[DEBUG] 새 화면으로 전환 시작: {screen_name}")
        self.current_screen_name = screen_name
        print(f"[DEBUG] current_screen_name 설정 완료: {self.current_screen_name}")
        self.current_screen = self.screens[screen_name]
        print(f"[DEBUG] current_screen 설정 완료: {self.current_screen}")
        print(f"[DEBUG] 화면 show() 호출 시작...")
        self.current_screen.show()
        print(f"[DEBUG] 화면 show() 호출 완료")
        
        # 화면 전환 완료 후 메모리 정리
        import gc
        gc.collect()
        print("[DEBUG] 화면 전환 후 메모리 정리 완료")
        
        print(f"[INFO] 화면 전환 완료: {screen_name}")
        return True
    
    def _create_screen_directly(self, screen_name, **kwargs):
        """직접 화면 생성 (app 참조가 없을 때)"""
        print(f"[DEBUG] _create_screen_directly 시작: {screen_name}")
        
        try:
            if screen_name == "dose_time":
                print(f"[DEBUG] DoseTimeScreen import 시작...")
                from screens.dose_time_screen import DoseTimeScreen
                print(f"[DEBUG] DoseTimeScreen import 완료")
                print(f"[DEBUG] DoseTimeScreen 인스턴스 생성 시작...")
                screen = DoseTimeScreen(self)
                print(f"[DEBUG] DoseTimeScreen 인스턴스 생성 완료")
                print(f"[DEBUG] register_screen 호출 시작...")
                self.register_screen(screen_name, screen)
                print(f"[DEBUG] register_screen 호출 완료")
                print(f"[OK] {screen_name} 화면 직접 생성 완료")
            elif screen_name == "meal_time":
                print(f"[DEBUG] MealTimeScreen import 시작...")
                from screens.meal_time_screen import MealTimeScreen
                print(f"[DEBUG] MealTimeScreen import 완료")
                print(f"[DEBUG] MealTimeScreen 인스턴스 생성 시작...")
                screen = MealTimeScreen(self)
                print(f"[DEBUG] MealTimeScreen 인스턴스 생성 완료")
                print(f"[DEBUG] register_screen 호출 시작...")
                self.register_screen(screen_name, screen)
                print(f"[DEBUG] register_screen 호출 완료")
                print(f"[OK] {screen_name} 화면 직접 생성 완료")
            elif screen_name == "disk_selection":
                print(f"[DEBUG] DiskSelectionScreen import 시작...")
                from screens.disk_selection_screen import DiskSelectionScreen
                print(f"[DEBUG] DiskSelectionScreen import 완료")
                print(f"[DEBUG] DiskSelectionScreen 인스턴스 생성 시작...")
                screen = DiskSelectionScreen(self)
                print(f"[DEBUG] DiskSelectionScreen 인스턴스 생성 완료")
                print(f"[DEBUG] register_screen 호출 시작...")
                self.register_screen(screen_name, screen)
                print(f"[DEBUG] register_screen 호출 완료")
                print(f"[OK] {screen_name} 화면 직접 생성 완료")
            elif screen_name == "pill_loading":
                print(f"[DEBUG] PillLoadingScreen import 시작...")
                from screens.pill_loading_screen import PillLoadingScreen
                print(f"[DEBUG] PillLoadingScreen import 완료")
                print(f"[DEBUG] PillLoadingScreen 인스턴스 생성 시작...")
                screen = PillLoadingScreen(self)
                print(f"[DEBUG] PillLoadingScreen 인스턴스 생성 완료")
                print(f"[DEBUG] register_screen 호출 시작...")
                self.register_screen(screen_name, screen)
                print(f"[DEBUG] register_screen 호출 완료")
                print(f"[OK] {screen_name} 화면 직접 생성 완료")
            elif screen_name == "wifi_scan":
                print(f"[DEBUG] WifiScanScreen import 시작...")
                from screens.wifi_scan_screen import WifiScanScreen
                print(f"[DEBUG] WifiScanScreen import 완료")
                print(f"[DEBUG] WifiScanScreen 인스턴스 생성 시작...")
                screen = WifiScanScreen(self)
                print(f"[DEBUG] WifiScanScreen 인스턴스 생성 완료")
                print(f"[DEBUG] register_screen 호출 시작...")
                self.register_screen(screen_name, screen)
                print(f"[DEBUG] register_screen 호출 완료")
                print(f"[OK] {screen_name} 화면 직접 생성 완료")
            elif screen_name == "main":
                print(f"[DEBUG] MainScreen import 시작...")
                from screens.main_screen import MainScreen
                print(f"[DEBUG] MainScreen import 완료")
                print(f"[DEBUG] MainScreen 인스턴스 생성 시작...")
                screen = MainScreen(self)
                print(f"[DEBUG] MainScreen 인스턴스 생성 완료")
                print(f"[DEBUG] register_screen 호출 시작...")
                self.register_screen(screen_name, screen)
                print(f"[DEBUG] register_screen 호출 완료")
                print(f"[OK] {screen_name} 화면 직접 생성 완료")
            else:
                print(f"[ERROR] 지원하지 않는 화면: {screen_name}")
        except Exception as e:
            print(f"[ERROR] 화면 직접 생성 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def go_back(self):
        """이전 화면으로 돌아가기"""
        if self.screen_stack:
            previous_screen = self.screen_stack.pop()
            self.show_screen(previous_screen, add_to_stack=False)
            print(f"[BACK] 이전 화면으로 돌아감: {previous_screen}")
            return True
        else:
            print("[ERROR] 돌아갈 화면이 없음")
            return False
    
    def get_current_screen(self):
        """현재 화면 반환"""
        return self.current_screen
    
    def get_current_screen_name(self):
        """현재 화면 이름 반환"""
        return self.current_screen_name
    
    def update(self):
        """화면 업데이트"""
        if self.current_screen:
            self.current_screen.update()
    
    def get_screen_info(self):
        """화면 정보 반환"""
        return {
            'current_screen': self.current_screen_name,
            'available_screens': list(self.screens.keys()),
            'screen_stack': self.screen_stack.copy()
        }
    
    def handle_button_a(self):
        """버튼 A 처리"""
        if self.current_screen and hasattr(self.current_screen, 'on_button_a'):
            self.current_screen.on_button_a()
    
    def handle_button_b(self):
        """버튼 B 처리"""
        if self.current_screen and hasattr(self.current_screen, 'on_button_b'):
            self.current_screen.on_button_b()
    
    def handle_button_c(self):
        """버튼 C 처리"""
        if self.current_screen and hasattr(self.current_screen, 'on_button_c'):
            self.current_screen.on_button_c()
    
    def handle_button_d(self):
        """버튼 D 처리"""
        if self.current_screen and hasattr(self.current_screen, 'on_button_d'):
            self.current_screen.on_button_d()
    
    def delete_screen(self, screen_name):
        """화면 삭제 (메모리 절약) - 완전한 동적 로딩 방식"""
        if screen_name not in self.screens:
            print(f"[ERROR] 존재하지 않는 화면: {screen_name}")
            return False
        
        try:
            screen_instance = self.screens[screen_name]
            
            # 화면 정리 메서드 호출
            if hasattr(screen_instance, 'cleanup'):
                try:
                    screen_instance.cleanup()
                    print(f"🧹 {screen_name} 화면 정리 완료")
                except Exception as e:
                    print(f"[WARN] {screen_name} 화면 정리 실패: {e}")
            
            # 화면 정리 (hide 메서드 없이 직접 정리)
            print(f"[INFO] {screen_name} 화면 직접 정리")
            
            # 화면 객체 삭제 (clear_screen 함수 사용)
            if hasattr(screen_instance, 'screen_obj') and screen_instance.screen_obj:
                print(f"🗑️ {screen_name} LVGL 객체 삭제 시도...")
                self._clear_screen(screen_instance.screen_obj)
                screen_instance.screen_obj = None  # 참조 정리
                print(f"🗑️ {screen_name} LVGL 객체 삭제 완료")
            else:
                print(f"🗑️ {screen_name} LVGL 객체가 이미 삭제됨 또는 존재하지 않음")
            
            # 딕셔너리에서 제거
            del self.screens[screen_name]
            
            # 현재 화면 참조 정리
            if screen_name == self.current_screen_name:
                self.current_screen_name = None
                self.current_screen = None
                print(f"[INFO] 현재 화면 참조 정리: {screen_name}")
            
            # 화면 스택에서도 제거
            if screen_name in self.screen_stack:
                self.screen_stack.remove(screen_name)
                print(f"📚 {screen_name} 화면 스택에서 제거")
            
            print(f"[OK] {screen_name} 화면 삭제 완료")
            return True
            
        except Exception as e:
            print(f"[ERROR] {screen_name} 화면 삭제 실패: {e}")
            import sys
            sys.print_exception(e)
            return False
    
    def startup_completed(self):
        """스타트업 완료 처리 - 올바른 책임 분리"""
        print("[INFO] 스타트업 완료 처리 시작")
        
        # 1. 스타트업 화면 정리
        self.cleanup_screen('startup')
        
        # 2. 다음 화면으로 전환
        self.transition_to('wifi_scan')
        
        print("[OK] 스타트업 완료 처리 완료")
    
    def wifi_scan_completed(self):
        """WiFi 스캔 완료 처리"""
        print("[INFO] WiFi 스캔 완료 처리 시작")
        
        # 1. WiFi 스캔 화면 정리
        self.cleanup_screen('wifi_scan')
        
        # 2. 다음 화면으로 전환
        self.transition_to('meal_time')
        
        print("[OK] WiFi 스캔 완료 처리 완료")
    
    def meal_time_completed(self):
        """식사 시간 선택 완료 처리"""
        print("[INFO] 식사 시간 선택 완료 처리 시작")
        
        # 1. 식사 시간 화면 정리
        self.cleanup_screen('meal_time')
        
        # 2. 다음 화면으로 전환
        self.transition_to('dose_time')
        
        print("[OK] 식사 시간 선택 완료 처리 완료")
    
    def dose_time_completed(self):
        """복용 시간 설정 완료 처리"""
        print("[INFO] 복용 시간 설정 완료 처리 시작")
        
        # 1. 복용 시간 화면 정리
        self.cleanup_screen('dose_time')
        
        # 2. 자동 할당된 디스크 정보 확인
        try:
            from data_manager import DataManager
            data_manager = DataManager()
            auto_assigned_disks = data_manager.get_auto_assigned_disks()
            
            if auto_assigned_disks:
                # 자동 할당된 디스크가 있으면 충전 화면으로 바로 이동
                print(f"[INFO] 자동 할당된 디스크 {len(auto_assigned_disks)}개 확인됨 - 디스크 선택 건너뛰기")
                self.transition_to('pill_loading')
            else:
                # 자동 할당 정보가 없으면 디스크 선택 화면으로 이동
                print("[INFO] 자동 할당 정보 없음 - 디스크 선택 화면으로 이동")
                self.transition_to('disk_selection')
                
        except Exception as e:
            print(f"[WARN] 자동 할당 정보 확인 실패: {e} - 디스크 선택 화면으로 이동")
            self.transition_to('disk_selection')
        
        print("[OK] 복용 시간 설정 완료 처리 완료")
    
    def disk_selection_completed(self):
        """디스크 선택 완료 처리"""
        print("[INFO] 디스크 선택 완료 처리 시작")
        
        # 1. 디스크 선택 화면 정리
        self.cleanup_screen('disk_selection')
        
        # 2. 다음 화면으로 전환
        self.transition_to('pill_loading')
    
    def pill_loading_completed(self):
        """알약 충전 완료 처리"""
        print("[INFO] 알약 충전 완료 처리 시작")
        
        # 1. 알약 충전 화면 정리
        self.cleanup_screen('pill_loading')
        
        print("[OK] 알약 충전 완료 처리 완료")
        
        print("[OK] 스타트업 완료 처리 완료")
    
    def pill_loading_back_to_disk_selection(self):
        """알약 충전 뒤로가기 처리 - 디스크 선택 화면으로"""
        print("[INFO] 알약 충전 뒤로가기 처리 시작")
        
        # 1. 알약 충전 화면 정리
        self.cleanup_screen('pill_loading')
        
        # 2. 디스크 선택 화면으로 전환
        self.transition_to('disk_selection')
        
        print("[OK] 알약 충전 뒤로가기 처리 완료")
    
    def pill_loading_back_to_dose_time(self):
        """알약 충전 뒤로가기 처리 - 복용 시간 설정 화면으로"""
        print("[INFO] 알약 충전 뒤로가기 처리 시작")
        
        # 1. 알약 충전 화면 정리
        self.cleanup_screen('pill_loading')
        
        # 2. 복용 시간 설정 화면으로 전환
        self.transition_to('dose_time')
        
        print("[OK] 알약 충전 뒤로가기 처리 완료")
    
    def dose_time_cancelled(self):
        """복용 시간 설정 취소 처리 - 식사 시간 선택 화면으로"""
        print("[INFO] 복용 시간 설정 취소 처리 시작")
        
        # 1. 복용 시간 설정 화면 정리
        self.cleanup_screen('dose_time')
        
        # 2. 식사 시간 선택 화면으로 전환
        self.transition_to('meal_time')
        
        print("[OK] 복용 시간 설정 취소 처리 완료")
    
    def cleanup_screen(self, screen_name):
        """화면 정리 담당 - ScreenManager의 책임"""
        print(f"[INFO] 화면 정리 시작: {screen_name}")
        
        if screen_name in self.screens:
            screen = self.screens[screen_name]
            
            # 화면 데이터 백업 (화면 정리 전에 수행)
            self._backup_screen_data(screen_name, screen)
            
            # 각 화면별 전용 정리 작업 수행
            if screen_name == 'startup':
                self._cleanup_startup_screen(screen)
            elif screen_name == 'wifi_scan':
                self._cleanup_wifi_scan_screen(screen)
            elif screen_name == 'meal_time':
                self._cleanup_meal_time_screen(screen)
            elif screen_name == 'dose_time':
                self._cleanup_dose_time_screen(screen)
            elif screen_name == 'disk_selection':
                self._cleanup_disk_selection_screen(screen)
            elif screen_name == 'pill_loading':
                self._cleanup_pill_loading_screen(screen)
            elif screen_name == 'main':
                self._cleanup_main_screen(screen)
            elif screen_name == 'wifi_password':
                self._cleanup_wifi_password_screen(screen)
            else:
                # 다른 화면의 경우 기존 cleanup 메서드 호출
                if hasattr(screen, 'cleanup'):
                    try:
                        screen.cleanup()
                        print(f"[OK] {screen_name} 화면 정리 완료")
                    except Exception as e:
                        print(f"[ERROR] {screen_name} 화면 정리 실패: {e}")
                        import sys
                        sys.print_exception(e)
            
            # 화면 딕셔너리에서 제거
            del self.screens[screen_name]
            print(f"[OK] {screen_name} 화면 딕셔너리에서 제거")
            
            # 현재 화면 참조 정리
            if screen_name == self.current_screen_name:
                self.current_screen_name = None
                self.current_screen = None
                print(f"[OK] 현재 화면 참조 정리: {screen_name}")
        else:
            print(f"[INFO] {screen_name} 화면이 이미 제거됨")
    
    def _cleanup_startup_screen(self, screen):
        """StartupScreen 전용 정리 작업 - ScreenManager의 책임"""
        try:
            print("[INFO] StartupScreen 전용 정리 시작...")
            
            # 화면 직접 정리 (hide 메서드 없이)
            
            # LVGL 객체들 완전 삭제
            if hasattr(screen, 'screen_obj') and screen.screen_obj:
                self._clear_screen(screen.screen_obj)
                try:
                    screen.screen_obj = None
                    print("[DEBUG] screen_obj 참조 정리 완료")
                except Exception as e:
                    print(f"[WARN] screen_obj 참조 정리 실패: {e}")
            
            # 다른 객체 참조들 정리
            if hasattr(screen, 'main_container'):
                screen.main_container = None
            if hasattr(screen, 'logo_container'):
                screen.logo_container = None
            if hasattr(screen, 'icon_bg'):
                screen.icon_bg = None
            
            print("[OK] StartupScreen 전용 정리 완료")
            
        except Exception as e:
            print(f"[ERROR] StartupScreen 전용 정리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _cleanup_wifi_scan_screen(self, screen):
        """WifiScanScreen 전용 정리 작업 - ScreenManager의 책임 (스타트업 화면과 동일한 방식)"""
        try:
            print("[INFO] WifiScanScreen 전용 정리 시작...")
            
            # 화면 직접 정리 (hide 메서드 없이)
            
            # LVGL 객체들 완전 삭제 (스타트업 화면과 동일한 방식)
            if hasattr(screen, 'screen_obj') and screen.screen_obj:
                self._clear_screen(screen.screen_obj)
                try:
                    screen.screen_obj = None
                    print("[DEBUG] screen_obj 참조 정리 완료")
                except Exception as e:
                    print(f"[WARN] screen_obj 참조 정리 실패: {e}")
            
            # 다른 객체 참조들 정리 (스타트업 화면과 동일한 방식)
            if hasattr(screen, 'main_container'):
                screen.main_container = None
            if hasattr(screen, 'title_text'):
                screen.title_text = None
            if hasattr(screen, 'wifi_list'):
                screen.wifi_list = None
            if hasattr(screen, 'hints_text'):
                screen.hints_text = None
            if hasattr(screen, 'wifi_list_items'):
                screen.wifi_list_items = None
            
            print("[OK] WifiScanScreen 전용 정리 완료")
            
        except Exception as e:
            print(f"[ERROR] WifiScanScreen 전용 정리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _cleanup_meal_time_screen(self, screen):
        """MealTimeScreen 전용 정리 작업 - ScreenManager의 책임"""
        try:
            print("[INFO] MealTimeScreen 전용 정리 시작...")
            
            # 화면 직접 정리 (hide 메서드 없이)
            
            # LVGL 객체들 완전 삭제
            if hasattr(screen, 'screen_obj') and screen.screen_obj:
                self._clear_screen(screen.screen_obj)
                try:
                    screen.screen_obj = None
                    print("[DEBUG] screen_obj 참조 정리 완료")
                except Exception as e:
                    print(f"[WARN] screen_obj 참조 정리 실패: {e}")
            
            # 다른 객체 참조들 정리 (스타트업 화면과 동일한 방식)
            if hasattr(screen, 'main_container'):
                screen.main_container = None
            if hasattr(screen, 'title_label'):
                screen.title_label = None
            if hasattr(screen, 'meal_options_container'):
                screen.meal_options_container = None
            if hasattr(screen, 'button_hints'):
                screen.button_hints = None
            
            print("[OK] MealTimeScreen 전용 정리 완료")
            
        except Exception as e:
            print(f"[ERROR] MealTimeScreen 전용 정리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _cleanup_dose_time_screen(self, screen):
        """DoseTimeScreen 전용 정리 작업 - ScreenManager의 책임"""
        try:
            print("[INFO] DoseTimeScreen 전용 정리 시작...")
            
            # 화면 직접 정리 (hide 메서드 없이)
            
            # LVGL 객체들 완전 삭제
            if hasattr(screen, 'screen_obj') and screen.screen_obj:
                self._clear_screen(screen.screen_obj)
                try:
                    screen.screen_obj = None
                    print("[DEBUG] screen_obj 참조 정리 완료")
                except Exception as e:
                    print(f"[WARN] screen_obj 참조 정리 실패: {e}")
            
            # 다른 객체 참조들 정리
            if hasattr(screen, 'main_container'):
                screen.main_container = None
            if hasattr(screen, 'title_label'):
                screen.title_label = None
            if hasattr(screen, 'time_roller'):
                screen.time_roller = None
            if hasattr(screen, 'minute_roller'):
                screen.minute_roller = None
            if hasattr(screen, 'button_hints'):
                screen.button_hints = None
            
            print("[OK] DoseTimeScreen 전용 정리 완료")
            
        except Exception as e:
            print(f"[ERROR] DoseTimeScreen 전용 정리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _cleanup_disk_selection_screen(self, screen):
        """DiskSelectionScreen 전용 정리 작업 - ScreenManager의 책임"""
        try:
            print("[INFO] DiskSelectionScreen 전용 정리 시작...")
            
            # 화면 직접 정리 (hide 메서드 없이)
            
            # LVGL 객체들 완전 삭제
            if hasattr(screen, 'screen_obj') and screen.screen_obj:
                self._clear_screen(screen.screen_obj)
                try:
                    screen.screen_obj = None
                    print("[DEBUG] screen_obj 참조 정리 완료")
                except Exception as e:
                    print(f"[WARN] screen_obj 참조 정리 실패: {e}")
            
            # 다른 객체 참조들 정리
            if hasattr(screen, 'main_container'):
                screen.main_container = None
            if hasattr(screen, 'title_label'):
                screen.title_label = None
            if hasattr(screen, 'disk_options_container'):
                screen.disk_options_container = None
            if hasattr(screen, 'button_hints'):
                screen.button_hints = None
            
            print("[OK] DiskSelectionScreen 전용 정리 완료")
            
        except Exception as e:
            print(f"[ERROR] DiskSelectionScreen 전용 정리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _cleanup_pill_loading_screen(self, screen):
        """PillLoadingScreen 전용 정리 작업 - ScreenManager의 책임"""
        try:
            print("[INFO] PillLoadingScreen 전용 정리 시작...")
            
            # 화면 직접 정리 (hide 메서드 없이)
            
            # LVGL 객체들 완전 삭제
            if hasattr(screen, 'screen_obj') and screen.screen_obj:
                self._clear_screen(screen.screen_obj)
                try:
                    screen.screen_obj = None
                    print("[DEBUG] screen_obj 참조 정리 완료")
                except Exception as e:
                    print(f"[WARN] screen_obj 참조 정리 실패: {e}")
            
            # 다른 객체 참조들 정리
            if hasattr(screen, 'main_container'):
                screen.main_container = None
            if hasattr(screen, 'title_label'):
                screen.title_label = None
            if hasattr(screen, 'progress_arc'):
                screen.progress_arc = None
            if hasattr(screen, 'status_label'):
                screen.status_label = None
            if hasattr(screen, 'button_hints'):
                screen.button_hints = None
            
            print("[OK] PillLoadingScreen 전용 정리 완료")
            
        except Exception as e:
            print(f"[ERROR] PillLoadingScreen 전용 정리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _cleanup_main_screen(self, screen):
        """MainScreen 전용 정리 작업 - ScreenManager의 책임"""
        try:
            print("[INFO] MainScreen 전용 정리 시작...")
            
            # LVGL 객체들 완전 삭제
            if hasattr(screen, 'screen_obj') and screen.screen_obj:
                self._clear_screen(screen.screen_obj)
                try:
                    screen.screen_obj = None
                    print("[DEBUG] screen_obj 참조 정리 완료")
                except Exception as e:
                    print(f"[WARN] screen_obj 참조 정리 실패: {e}")
            
            # 다른 객체 참조들 정리
            if hasattr(screen, 'main_container'):
                screen.main_container = None
            if hasattr(screen, 'title_label'):
                screen.title_label = None
            if hasattr(screen, 'schedule_label'):
                screen.schedule_label = None
            if hasattr(screen, 'status_label'):
                screen.status_label = None
            if hasattr(screen, 'button_hints'):
                screen.button_hints = None
            
            print("[OK] MainScreen 전용 정리 완료")
            
        except Exception as e:
            print(f"[ERROR] MainScreen 전용 정리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _cleanup_wifi_password_screen(self, screen):
        """WifiPasswordScreen 전용 정리 작업 - ScreenManager의 책임"""
        try:
            print("[INFO] WifiPasswordScreen 전용 정리 시작...")
            
            # LVGL 객체들 완전 삭제
            if hasattr(screen, 'screen_obj') and screen.screen_obj:
                self._clear_screen(screen.screen_obj)
                try:
                    screen.screen_obj = None
                    print("[DEBUG] screen_obj 참조 정리 완료")
                except Exception as e:
                    print(f"[WARN] screen_obj 참조 정리 실패: {e}")
            
            # 다른 객체 참조들 정리
            if hasattr(screen, 'main_container'):
                screen.main_container = None
            if hasattr(screen, 'title_label'):
                screen.title_label = None
            if hasattr(screen, 'password_label'):
                screen.password_label = None
            if hasattr(screen, 'button_hints'):
                screen.button_hints = None
            
            print("[OK] WifiPasswordScreen 전용 정리 완료")
            
        except Exception as e:
            print(f"[ERROR] WifiPasswordScreen 전용 정리 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _backup_screen_data(self, screen_name, screen):
        """화면 데이터 백업 - ScreenManager의 책임"""
        try:
            print(f"[INFO] {screen_name} 화면 데이터 백업 시작...")
            
            # global_data import
            from global_data import global_data
            
            # 화면별 데이터 백업
            if screen_name == 'wifi_scan':
                # WiFi 스캔 결과 백업
                data = {}
                if hasattr(screen, 'networks'):
                    data['networks'] = screen.networks
                if hasattr(screen, 'selected_network'):
                    data['selected_network'] = screen.selected_network
                global_data.backup_screen_data(screen_name, data)
                
            elif screen_name == 'meal_time':
                # 식사 시간 선택 결과 백업
                data = {}
                if hasattr(screen, 'selected_meals'):
                    data['selected_meals'] = screen.selected_meals
                if hasattr(screen, 'current_selection'):
                    data['current_selection'] = screen.current_selection
                global_data.backup_screen_data(screen_name, data)
                
            elif screen_name == 'dose_time':
                # 복용 시간 설정 결과 백업
                data = {}
                if hasattr(screen, 'dose_times'):
                    data['dose_times'] = screen.dose_times
                if hasattr(screen, 'current_dose_index'):
                    data['current_dose_index'] = screen.current_dose_index
                global_data.backup_screen_data(screen_name, data)
                
            elif screen_name == 'disk_selection':
                # 디스크 선택 결과 백업
                data = {}
                if hasattr(screen, 'selected_disks'):
                    data['selected_disks'] = screen.selected_disks
                if hasattr(screen, 'current_selection'):
                    data['current_selection'] = screen.current_selection
                global_data.backup_screen_data(screen_name, data)
                
            elif screen_name == 'pill_loading':
                # 알약 충전 결과 백업
                data = {}
                if hasattr(screen, 'loading_progress'):
                    data['loading_progress'] = screen.loading_progress
                if hasattr(screen, 'current_disk'):
                    data['current_disk'] = screen.current_disk
                global_data.backup_screen_data(screen_name, data)
                
            else:
                print(f"[INFO] {screen_name} 화면은 데이터 백업 불필요")
                
        except Exception as e:
            print(f"[ERROR] {screen_name} 화면 데이터 백업 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def transition_to(self, screen_name):
        """안전한 화면 전환 담당 - ScreenManager의 책임"""
        print(f"[INFO] 안전한 화면 전환 시작: {screen_name}")
        print(f"[DEBUG] 현재 등록된 화면 목록: {list(self.screens.keys())}")
        print(f"[DEBUG] 현재 화면: {self.current_screen_name}")
        
        try:
            # 이전 화면 정리 (스타트업, wifi_scan, meal_time, dose_time, disk_selection, pill_loading 화면 제외 - 각자의 completed 메서드에서 정리)
            if self.current_screen_name and self.current_screen_name not in ['startup', 'wifi_scan', 'meal_time', 'dose_time', 'disk_selection', 'pill_loading'] and self.current_screen_name != screen_name:
                print(f"[INFO] 이전 화면 정리 시작: {self.current_screen_name}")
                self.cleanup_screen(self.current_screen_name)
                print(f"[OK] 이전 화면 정리 완료: {self.current_screen_name}")
            
            # 화면이 존재하지 않으면 생성
            print(f"[DEBUG] 화면 존재 여부 확인: {screen_name} in {list(self.screens.keys())}")
            if screen_name not in self.screens:
                print(f"[INFO] {screen_name} 화면 생성 중...")
                self._create_screen_directly(screen_name)
                print(f"[DEBUG] 화면 생성 후 등록된 화면 목록: {list(self.screens.keys())}")
            else:
                print(f"[INFO] {screen_name} 화면이 이미 존재함")
            
            # 현재 화면 참조 정리
            if self.current_screen_name:
                print(f"[INFO] 현재 화면 참조 정리: {self.current_screen_name}")
                self.current_screen_name = None
                self.current_screen = None
            
            # 새 화면으로 전환
            print(f"[DEBUG] 새 화면으로 전환 시작: {screen_name}")
            self.current_screen_name = screen_name
            print(f"[DEBUG] current_screen_name 설정 완료: {self.current_screen_name}")
            self.current_screen = self.screens[screen_name]
            print(f"[DEBUG] current_screen 설정 완료: {self.current_screen}")
            print(f"[DEBUG] 화면 show() 호출 시작...")
            self.current_screen.show()
            print(f"[DEBUG] 화면 show() 호출 완료")
            
            # 화면 전환 완료 후 메모리 정리
            import gc
            gc.collect()
            print("[DEBUG] 화면 전환 후 메모리 정리 완료")
            
            print(f"[OK] 화면 전환 완료: {screen_name}")
            return True
            
        except Exception as e:
            print(f"[ERROR] 화면 전환 실패: {e}")
            import sys
            sys.print_exception(e)
            return False
    
    def _clear_screen(self, screen_obj):
        """LVGL 화면 객체 안전 삭제 - ScreenManager의 책임"""
        if screen_obj:
            try:
                # 비동기 삭제 시도
                screen_obj.delete_async()
                print("[OK] LVGL 화면 객체 비동기 삭제 완료")
            except Exception as e:
                print(f"[WARN] 비동기 삭제 실패, 동기 삭제 시도: {e}")
                try:
                    # 동기 삭제 시도
                    screen_obj.delete()
                    print("[OK] LVGL 화면 객체 동기 삭제 완료")
                except Exception as e2:
                    print(f"[WARN] 동기 삭제도 실패: {e2}")
            finally:
                # 메모리 회수
                import gc
                gc.collect()
                print("[OK] LVGL 화면 삭제 후 메모리 회수 완료")
    
    def _monitor_memory(self, label):
        """메모리 사용량 모니터링 (MicroPython만)"""
        try:
            import micropython
            
            # MicroPython 메모리 정보만 확인
            mem_info = micropython.mem_info()
            print(f"[{label}] MicroPython 메모리:")
            print(f"  {mem_info}")
                
        except Exception as e:
            print(f"[WARN] 메모리 모니터 실패: {e}")
    
    def get_memory_info(self):
        """메모리 사용 정보 반환"""
        import micropython
        try:
            mem_info = micropython.mem_info()
            return {
                'registered_screens': list(self.screens.keys()),
                'current_screen': self.current_screen_name,
                'screen_stack': self.screen_stack.copy(),
                'memory_info': mem_info
            }
        except:
            return {
                'registered_screens': list(self.screens.keys()),
                'current_screen': self.current_screen_name,
                'screen_stack': self.screen_stack.copy(),
                'memory_info': '메모리 정보 조회 실패'
            }