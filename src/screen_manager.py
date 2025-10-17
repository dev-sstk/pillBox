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
        self.screens[screen_name] = screen_instance
        print(f"[OK] 화면 등록: {screen_name}")
    
    def set_current_screen(self, screen_name):
        """현재 화면 설정"""
        if screen_name not in self.screens:
            print(f"[ERROR] 존재하지 않는 화면: {screen_name}")
            return False
        
        # 현재 화면이 있으면 숨기기
        if self.current_screen:
            self.current_screen.hide()
        
        # 새 화면으로 전환
        self.current_screen_name = screen_name
        self.current_screen = self.screens[screen_name]
        self.current_screen.show()
        
        print(f"[INFO] 화면 전환: {screen_name}")
        return True
    
    def show_screen(self, screen_name, add_to_stack=True, **kwargs):
        """화면 전환 - 안전한 방식 (LVGL 객체 삭제 없음)"""
        # 메모리 정리
        import gc
        gc.collect()
        print("[DEBUG] 화면 전환 전 메모리 정리 완료")
        
        # 현재 화면이 있으면 숨기기만 (삭제하지 않음)
        if self.current_screen and self.current_screen_name:
            print(f"[INFO] 현재 화면 숨김: {self.current_screen_name}")
            try:
                self.current_screen.hide()
                # 메모리 정리
                gc.collect()
                print("[DEBUG] 화면 숨김 후 메모리 정리 완료")
            except Exception as e:
                print(f"[WARN] 화면 숨김 실패: {e}")
        
        # 새 화면이 이미 존재하는지 확인
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
        self.current_screen_name = screen_name
        self.current_screen = self.screens[screen_name]
        self.current_screen.show()
        
        print(f"[INFO] 화면 전환 완료: {screen_name}")
        return True
    
    def _create_screen_directly(self, screen_name, **kwargs):
        """직접 화면 생성 (app 참조가 없을 때)"""
        try:
            if screen_name == "dose_time":
                from screens.dose_time_screen import DoseTimeScreen
                dose_count = kwargs.get('dose_count', 1)
                selected_meals = kwargs.get('selected_meals', None)
                screen = DoseTimeScreen(self, dose_count=dose_count, selected_meals=selected_meals)
                self.register_screen(screen_name, screen)
                print(f"[OK] {screen_name} 화면 직접 생성 완료")
            elif screen_name == "meal_time":
                from screens.meal_time_screen import MealTimeScreen
                screen = MealTimeScreen(self)
                self.register_screen(screen_name, screen)
                print(f"[OK] {screen_name} 화면 직접 생성 완료")
            elif screen_name == "advanced_settings":
                from screens.advanced_settings_screen import AdvancedSettingsScreen
                screen = AdvancedSettingsScreen(self)
                self.register_screen(screen_name, screen)
                print(f"[OK] {screen_name} 화면 직접 생성 완료")
            elif screen_name == "data_management":
                from screens.data_management_screen import DataManagementScreen
                screen = DataManagementScreen(self)
                self.register_screen(screen_name, screen)
                print(f"[OK] {screen_name} 화면 직접 생성 완료")
            elif screen_name == "disk_selection":
                from screens.disk_selection_screen import DiskSelectionScreen
                dose_info = kwargs.get('dose_info', None)
                screen = DiskSelectionScreen(self, dose_info=dose_info)
                self.register_screen(screen_name, screen)
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
            
            # 화면 숨기기
            if hasattr(screen_instance, 'hide'):
                try:
                    screen_instance.hide()
                    print(f"[INFO] {screen_name} 화면 숨김")
                except Exception as e:
                    print(f"[WARN] {screen_name} 화면 숨김 실패: {e}")
            
            # 화면 객체 삭제 (안전한 방식)
            if hasattr(screen_instance, 'screen_obj') and screen_instance.screen_obj:
                try:
                    print(f"🗑️ {screen_name} LVGL 객체 삭제 시도...")
                    # LVGL 객체 삭제 전 추가 안전 조치
                    import gc
                    gc.collect()
                    
                    # LVGL 객체 삭제
                    screen_instance.screen_obj.delete()
                    screen_instance.screen_obj = None  # 참조 정리
                    print(f"🗑️ {screen_name} LVGL 객체 삭제 완료")
                    
                    # 삭제 후 메모리 정리
                    gc.collect()
                except Exception as e:
                    print(f"[WARN] {screen_name} LVGL 객체 삭제 실패: {e}")
                    # 삭제 실패해도 계속 진행
                    try:
                        screen_instance.screen_obj = None
                    except:
                        pass
            
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
    
    def delete_all_screens_except(self, keep_screens=None):
        """현재 화면을 제외한 모든 화면 삭제"""
        if keep_screens is None:
            keep_screens = [self.current_screen_name]
        
        deleted_count = 0
        screens_to_delete = []
        
        # 삭제할 화면 목록 생성
        for screen_name in list(self.screens.keys()):
            if screen_name not in keep_screens:
                screens_to_delete.append(screen_name)
        
        # 화면들 삭제
        for screen_name in screens_to_delete:
            if self.delete_screen(screen_name):
                deleted_count += 1
        
        print(f"🧹 {deleted_count}개 화면 삭제 완료 (유지: {keep_screens})")
        return deleted_count
    
    def cleanup_unused_screens(self):
        """사용하지 않는 화면들 정리"""
        import gc
        
        # 현재 화면과 최근 2개 화면만 유지
        keep_screens = [self.current_screen_name]
        if len(self.screen_stack) > 0:
            keep_screens.append(self.screen_stack[-1])  # 이전 화면
        if len(self.screen_stack) > 1:
            keep_screens.append(self.screen_stack[-2])  # 그 이전 화면
        
        # 중복 제거
        keep_screens = list(set(keep_screens))
        keep_screens = [s for s in keep_screens if s is not None]
        
        deleted_count = self.delete_all_screens_except(keep_screens)
        
        # 가비지 컬렉션 실행
        if deleted_count > 0:
            gc.collect()
            print(f"🧹 가비지 컬렉션 실행 (삭제된 화면: {deleted_count}개)")
        
        return deleted_count
    
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