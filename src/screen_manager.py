"""
화면 관리 시스템
모든 화면의 생성, 전환, 업데이트를 관리
"""

import lvgl as lv

class ScreenManager:
    """화면 관리자 클래스"""
    
    def __init__(self, app=None):
        """화면 관리자 초기화"""
        self.screens = {}
        self.current_screen_name = None
        self.current_screen = None
        self.screen_stack = []  # 화면 스택 (뒤로가기 기능)
        self.app = app  # PillBoxApp 참조
        
        print("✅ ScreenManager 초기화 완료")
    
    def register_screen(self, screen_name, screen_instance):
        """화면 등록"""
        self.screens[screen_name] = screen_instance
        print(f"✅ 화면 등록: {screen_name}")
    
    def set_current_screen(self, screen_name):
        """현재 화면 설정"""
        if screen_name not in self.screens:
            print(f"❌ 존재하지 않는 화면: {screen_name}")
            return False
        
        # 현재 화면이 있으면 숨기기
        if self.current_screen:
            self.current_screen.hide()
        
        # 새 화면으로 전환
        self.current_screen_name = screen_name
        self.current_screen = self.screens[screen_name]
        self.current_screen.show()
        
        print(f"📱 화면 전환: {screen_name}")
        return True
    
    def show_screen(self, screen_name, add_to_stack=True, **kwargs):
        """화면 전환"""
        if screen_name not in self.screens:
            # 화면이 등록되지 않았다면 동적으로 생성 시도
            print(f"📱 {screen_name} 화면이 등록되지 않음. 동적 생성 중...")
            if self.app and hasattr(self.app, 'create_and_register_screen'):
                self.app.create_and_register_screen(screen_name, **kwargs) # kwargs 전달
            else:
                # app 참조가 없으면 직접 화면 생성 시도
                self._create_screen_directly(screen_name, **kwargs)
            if screen_name not in self.screens:
                print(f"❌ 존재하지 않는 화면: {screen_name}")
                return False
        else:
            # 기존 화면이 있으면 새로운 매개변수로 업데이트 시도
            if kwargs and screen_name == 'dose_time':
                print(f"📱 기존 {screen_name} 화면에 새로운 매개변수 적용 중...")
                existing_screen = self.screens[screen_name]
                if hasattr(existing_screen, 'update_meal_selections'):
                    dose_count = kwargs.get('dose_count', 1)
                    selected_meals = kwargs.get('selected_meals', None)
                    existing_screen.update_meal_selections(dose_count, selected_meals)
                    print(f"✅ {screen_name} 화면 상태 업데이트 완료")
        
        # 현재 화면이 있으면 숨기기
        if self.current_screen:
            self.current_screen.hide()
            if add_to_stack:
                self.screen_stack.append(self.current_screen_name)
        
        # 새 화면으로 전환
        self.current_screen_name = screen_name
        self.current_screen = self.screens[screen_name]
        self.current_screen.show()
        
        print(f"📱 화면 전환: {screen_name}")
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
                print(f"✅ {screen_name} 화면 직접 생성 완료")
            elif screen_name == "meal_time":
                from screens.meal_time_screen import MealTimeScreen
                screen = MealTimeScreen(self)
                self.register_screen(screen_name, screen)
                print(f"✅ {screen_name} 화면 직접 생성 완료")
            else:
                print(f"❌ 지원하지 않는 화면: {screen_name}")
        except Exception as e:
            print(f"❌ 화면 직접 생성 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def go_back(self):
        """이전 화면으로 돌아가기"""
        if self.screen_stack:
            previous_screen = self.screen_stack.pop()
            self.show_screen(previous_screen, add_to_stack=False)
            print(f"⬅️ 이전 화면으로 돌아감: {previous_screen}")
            return True
        else:
            print("❌ 돌아갈 화면이 없음")
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