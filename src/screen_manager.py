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
    
    def show_screen(self, screen_name, add_to_stack=True):
        """화면 전환"""
        if screen_name not in self.screens:
            print(f"❌ 존재하지 않는 화면: {screen_name}")
            return False
        
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
