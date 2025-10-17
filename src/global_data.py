"""
전역 데이터 저장소
화면 전환 시에도 유지되어야 하는 데이터들을 저장
"""

class GlobalData:
    """전역 데이터 저장소 클래스"""
    
    def __init__(self):
        self.dose_times = []  # 복용 시간 정보
        self.selected_meals = []  # 선택된 식사 시간 정보
        self.dose_count = 1  # 복용 횟수
        
    def save_dose_times(self, dose_times):
        """복용 시간 정보 저장"""
        self.dose_times = dose_times.copy() if dose_times else []
        print(f"[INFO] 전역 데이터에 복용 시간 저장: {len(self.dose_times)}개")
        for dose_info in self.dose_times:
            if isinstance(dose_info, dict):
                print(f"  - {dose_info.get('meal_name', 'Unknown')}: {dose_info.get('time', 'Unknown')}")
    
    def get_dose_times(self):
        """복용 시간 정보 반환"""
        return self.dose_times.copy() if self.dose_times else []
    
    def save_selected_meals(self, selected_meals):
        """선택된 식사 시간 정보 저장"""
        self.selected_meals = selected_meals.copy() if selected_meals else []
        print(f"[INFO] 전역 데이터에 선택된 식사 시간 저장: {len(self.selected_meals)}개")
        for meal in self.selected_meals:
            if isinstance(meal, dict):
                print(f"  - {meal.get('name', 'Unknown')}")
    
    def get_selected_meals(self):
        """선택된 식사 시간 정보 반환"""
        return self.selected_meals.copy() if self.selected_meals else []
    
    def save_dose_count(self, dose_count):
        """복용 횟수 저장"""
        self.dose_count = dose_count
        print(f"[INFO] 전역 데이터에 복용 횟수 저장: {dose_count}")
    
    def get_dose_count(self):
        """복용 횟수 반환"""
        return self.dose_count
    
    def clear_all(self):
        """모든 데이터 초기화"""
        self.dose_times = []
        self.selected_meals = []
        self.dose_count = 1
        print("[INFO] 전역 데이터 초기화 완료")

# 전역 인스턴스 생성
global_data = GlobalData()
