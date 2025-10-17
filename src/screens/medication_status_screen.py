"""
약물 상태 화면
디스크별 약물 수량 및 상태 표시
"""

import sys
sys.path.append("/")

import time
import lvgl as lv
from ui_style import UIStyle
from data_manager import DataManager
from medication_tracker import MedicationTracker

class MedicationStatusScreen:
    """약물 상태 화면 클래스"""
    
    def __init__(self, screen_manager):
        """약물 상태 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = "medication_status"
        
        # 데이터 관리자 및 약물 추적기 초기화
        self.data_manager = DataManager()
        self.medication_tracker = MedicationTracker(self.data_manager)
        
        # UI 스타일 시스템 초기화
        self.ui_style = UIStyle()
        
        # 화면 객체
        self.screen = None
        self.main_container = None
        self.title_label = None
        self.disk_containers = []
        self.back_button = None
        
        print(f"[INFO] {self.screen_name} 화면 초기화")
    
    def create_screen(self):
        """약물 상태 화면 생성"""
        try:
            print(f"[INFO] {self.screen_name} 화면 생성 시작...")
            
            # 화면 객체 생성
            self.screen = lv.obj()
            self.screen.set_size(160, 128)
            self.screen.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
            
            # 메인 컨테이너 생성
            self._create_main_container()
            
            # 제목 영역 생성
            self._create_title_area()
            
            # 디스크 상태 영역 생성
            self._create_disk_status_area()
            
            # 하단 버튼 영역 생성
            self._create_button_area()
            
            print(f"[OK] {self.screen_name} 화면 생성 완료")
            return True
            
        except Exception as e:
            print(f"[ERROR] {self.screen_name} 화면 생성 실패: {e}")
            return False
    
    def _create_main_container(self):
        """메인 컨테이너 생성"""
        try:
            self.main_container = lv.obj(self.screen)
            self.main_container.set_size(160, 128)
            self.main_container.set_pos(0, 0)
            self.main_container.set_style_bg_opa(0, 0)
            self.main_container.set_style_border_width(0, 0)
            self.main_container.set_style_pad_all(0, 0)
            
            print("[OK] 메인 컨테이너 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] 메인 컨테이너 생성 실패: {e}")
    
    def _create_title_area(self):
        """제목 영역 생성"""
        try:
            # 제목 라벨
            self.title_label = lv.label(self.main_container)
            self.title_label.set_text("약물 상태")
            self.title_label.set_style_text_font(self.ui_style.font_large, 0)
            self.title_label.set_style_text_color(lv.color_hex(0x333333), 0)
            self.title_label.align(lv.ALIGN.TOP_MID, 0, 5)
            
            print("[OK] 제목 영역 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] 제목 영역 생성 실패: {e}")
    
    def _create_disk_status_area(self):
        """디스크 상태 영역 생성"""
        try:
            # 3개 디스크 상태 표시
            for disk_num in [1, 2, 3]:
                self._create_disk_status_item(disk_num, 20 + (disk_num - 1) * 30)
            
            print("[OK] 디스크 상태 영역 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] 디스크 상태 영역 생성 실패: {e}")
    
    def _create_disk_status_item(self, disk_num, y_pos):
        """디스크 상태 항목 생성"""
        try:
            # 디스크 컨테이너
            disk_container = lv.obj(self.main_container)
            disk_container.set_size(150, 25)
            disk_container.set_pos(5, y_pos)
            disk_container.set_style_bg_color(lv.color_hex(0xF8F8F8), 0)
            disk_container.set_style_radius(5, 0)
            disk_container.set_style_pad_all(3, 0)
            disk_container.set_style_border_width(1, 0)
            disk_container.set_style_border_color(lv.color_hex(0xE0E0E0), 0)
            
            # 디스크 정보 업데이트
            self._update_disk_status_item(disk_container, disk_num)
            
            self.disk_containers.append(disk_container)
            
        except Exception as e:
            print(f"[ERROR] 디스크 {disk_num} 상태 항목 생성 실패: {e}")
    
    def _update_disk_status_item(self, container, disk_num):
        """디스크 상태 항목 업데이트"""
        try:
            # 기존 라벨들 제거
            for child in container.get_children():
                child.delete()
            
            # 디스크 정보 가져오기
            disk_info = self.medication_tracker.get_disk_medication_info(disk_num)
            if not disk_info:
                return
            
            # 디스크 이름
            disk_name = disk_info.get("name", f"디스크 {disk_num}")
            name_label = lv.label(container)
            name_label.set_text(disk_name)
            name_label.set_style_text_font(self.ui_style.font_small, 0)
            name_label.set_style_text_color(lv.color_hex(0x333333), 0)
            name_label.set_pos(5, 2)
            
            # 수량 정보
            current_count = disk_info.get("current_count", 0)
            total_capacity = disk_info.get("total_capacity", 15)
            count_text = f"{current_count}/{total_capacity}"
            count_label = lv.label(container)
            count_label.set_text(count_text)
            count_label.set_style_text_font(self.ui_style.font_small, 0)
            count_label.set_style_text_color(lv.color_hex(0x666666), 0)
            count_label.set_pos(80, 2)
            
            # 상태 아이콘
            status_icon = self._get_disk_status_icon(disk_num)
            status_label = lv.label(container)
            status_label.set_text(status_icon)
            status_label.set_style_text_font(self.ui_style.font_small, 0)
            status_label.set_pos(120, 2)
            
            # 진행률 바 (선택적)
            if total_capacity > 0:
                progress = current_count / total_capacity
                if progress < 0.2:  # 20% 미만
                    container.set_style_border_color(lv.color_hex(0xFF4444), 0)  # 빨간색
                elif progress < 0.5:  # 50% 미만
                    container.set_style_border_color(lv.color_hex(0xFFAA00), 0)  # 주황색
                else:
                    container.set_style_border_color(lv.color_hex(0x44AA44), 0)  # 초록색
            
        except Exception as e:
            print(f"[ERROR] 디스크 {disk_num} 상태 업데이트 실패: {e}")
    
    def _get_disk_status_icon(self, disk_num):
        """디스크 상태 아이콘 반환"""
        try:
            if self.medication_tracker.is_disk_low_stock(disk_num):
                current_count = self.data_manager.get_disk_count(disk_num)
                if current_count <= 0:
                    return "🚨"  # 소진
                elif current_count <= 1:
                    return "⚠️"   # 위험
                else:
                    return "📢"   # 부족
            else:
                return "✅"      # 정상
                
        except Exception as e:
            print(f"[ERROR] 디스크 {disk_num} 상태 아이콘 생성 실패: {e}")
            return "❓"
    
    def _create_button_area(self):
        """하단 버튼 영역 생성"""
        try:
            # 뒤로가기 버튼
            self.back_button = lv.btn(self.main_container)
            self.back_button.set_size(60, 20)
            self.back_button.set_pos(50, 100)
            self.back_button.set_style_bg_color(lv.color_hex(0x007AFF), 0)
            self.back_button.set_style_radius(10, 0)
            
            # 버튼 라벨
            back_label = lv.label(self.back_button)
            back_label.set_text("뒤로")
            back_label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
            back_label.center()
            
            # 버튼 이벤트
            self.back_button.add_event_cb(self._on_back_button, lv.EVENT.CLICKED, None)
            
            print("[OK] 하단 버튼 영역 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] 하단 버튼 영역 생성 실패: {e}")
    
    def _on_back_button(self, event):
        """뒤로가기 버튼 이벤트"""
        try:
            if event == lv.EVENT.CLICKED:
                print("[BTN] 뒤로가기 버튼 눌림")
                self.screen_manager.show_screen("main")
                
        except Exception as e:
            print(f"[ERROR] 뒤로가기 버튼 이벤트 실패: {e}")
    
    def show(self):
        """화면 표시"""
        try:
            if self.screen:
                lv.scr_load(self.screen)
                print(f"[OK] {self.screen_name} 화면 표시")
            else:
                print(f"[ERROR] {self.screen_name} 화면 객체 없음")
                
        except Exception as e:
            print(f"[ERROR] {self.screen_name} 화면 표시 실패: {e}")
    
    def hide(self):
        """화면 숨기기"""
        try:
            print(f"[INFO] {self.screen_name} 화면 숨기기")
            # 화면 숨김 처리
            
        except Exception as e:
            print(f"[ERROR] {self.screen_name} 화면 숨기기 실패: {e}")
    
    def update(self):
        """화면 업데이트"""
        try:
            # 디스크 상태 업데이트
            for i, container in enumerate(self.disk_containers):
                disk_num = i + 1
                self._update_disk_status_item(container, disk_num)
            
        except Exception as e:
            print(f"[ERROR] {self.screen_name} 화면 업데이트 실패: {e}")
    
    def cleanup(self):
        """화면 정리"""
        try:
            if self.screen:
                self.screen.delete()
                self.screen = None
            print(f"[OK] {self.screen_name} 화면 정리 완료")
            
        except Exception as e:
            print(f"[ERROR] {self.screen_name} 화면 정리 실패: {e}")
