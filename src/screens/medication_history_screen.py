"""
복용 기록 화면
과거 복용 내역 조회 및 통계 표시
"""

import sys
sys.path.append("/")

import time
import lvgl as lv
from ui_style import UIStyle
from data_manager import DataManager
from wifi_manager import get_wifi_manager

class MedicationHistoryScreen:
    """복용 기록 화면 클래스"""
    
    def __init__(self, screen_manager):
        """복용 기록 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = "medication_history"
        
        # 데이터 관리자 초기화
        self.data_manager = DataManager()
        
        # UI 스타일 시스템 초기화
        self.ui_style = UIStyle()
        
        # 화면 객체
        self.screen = None
        self.main_container = None
        self.title_label = None
        self.history_list = None
        self.stats_container = None
        self.back_button = None
        
        # 데이터
        self.dispense_logs = []
        self.current_page = 0
        self.items_per_page = 5
        
        print(f"[INFO] {self.screen_name} 화면 초기화")
    
    def create_screen(self):
        """복용 기록 화면 생성"""
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
            
            # 통계 영역 생성
            self._create_stats_area()
            
            # 기록 목록 생성
            self._create_history_list()
            
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
            self.title_label.set_text("복용 기록")
            self.title_label.set_style_text_font(self.ui_style.font_large, 0)
            self.title_label.set_style_text_color(lv.color_hex(0x333333), 0)
            self.title_label.align(lv.ALIGN.TOP_MID, 0, 5)
            
            print("[OK] 제목 영역 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] 제목 영역 생성 실패: {e}")
    
    def _create_stats_area(self):
        """통계 영역 생성"""
        try:
            # 통계 컨테이너
            self.stats_container = lv.obj(self.main_container)
            self.stats_container.set_size(150, 25)
            self.stats_container.set_pos(5, 25)
            self.stats_container.set_style_bg_color(lv.color_hex(0xF0F0F0), 0)
            self.stats_container.set_style_radius(5, 0)
            self.stats_container.set_style_pad_all(3, 0)
            
            # 통계 정보 업데이트
            self._update_stats_display()
            
            print("[OK] 통계 영역 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] 통계 영역 생성 실패: {e}")
    
    def _create_history_list(self):
        """기록 목록 생성"""
        try:
            # 기록 목록 컨테이너
            self.history_list = lv.obj(self.main_container)
            self.history_list.set_size(150, 70)
            self.history_list.set_pos(5, 55)
            self.history_list.set_style_bg_color(lv.color_hex(0xFFFFFF), 0)
            self.history_list.set_style_border_width(1, 0)
            self.history_list.set_style_border_color(lv.color_hex(0xCCCCCC), 0)
            self.history_list.set_style_radius(5, 0)
            self.history_list.set_style_pad_all(3, 0)
            
            # 기록 데이터 로드 및 표시
            self._load_and_display_history()
            
            print("[OK] 기록 목록 생성 완료")
            
        except Exception as e:
            print(f"[ERROR] 기록 목록 생성 실패: {e}")
    
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
    
    def _load_and_display_history(self):
        """기록 데이터 로드 및 표시"""
        try:
            # 복용 기록 로드
            self.dispense_logs = self.data_manager.load_dispense_logs()
            
            # 최근 기록만 표시 (최대 5개)
            recent_logs = self.dispense_logs[-5:] if self.dispense_logs else []
            
            # 기존 라벨들 제거
            for child in self.history_list.get_children():
                child.delete()
            
            if not recent_logs:
                # 기록이 없는 경우
                no_data_label = lv.label(self.history_list)
                no_data_label.set_text("복용 기록이 없습니다")
                no_data_label.set_style_text_color(lv.color_hex(0x999999), 0)
                no_data_label.align(lv.ALIGN.CENTER, 0, 0)
                return
            
            # 기록 항목들 생성
            y_offset = 0
            for i, log in enumerate(recent_logs):
                self._create_history_item(log, y_offset)
                y_offset += 12
            
            print(f"[OK] 기록 표시 완료: {len(recent_logs)}개 항목")
            
        except Exception as e:
            print(f"[ERROR] 기록 데이터 로드 실패: {e}")
    
    def _create_history_item(self, log, y_offset):
        """기록 항목 생성"""
        try:
            # 시간 정보
            timestamp = log.get("timestamp", "")
            if timestamp:
                try:
                    # MicroPython time 모듈 사용
                    # timestamp 형식: "2025-01-17T12:57:00"
                    if 'T' in timestamp:
                        date_part, time_part = timestamp.split('T')
                        time_str = time_part[:5]  # "12:57"
                        date_parts = date_part.split('-')
                        if len(date_parts) >= 3:
                            date_str = f"{date_parts[1]}/{date_parts[2]}"  # "01/17"
                        else:
                            date_str = "??/??"
                    else:
                        time_str = "??:??"
                        date_str = "??/??"
                except:
                    time_str = "??:??"
                    date_str = "??/??"
            else:
                time_str = "??:??"
                date_str = "??/??"
            
            # 일정 정보
            dose_index = log.get("dose_index", 0)
            meal_names = ["아침", "점심", "저녁"]
            meal_name = meal_names[dose_index] if dose_index < len(meal_names) else f"일정 {dose_index + 1}"
            
            # 성공/실패 상태
            success = log.get("success", False)
            status_icon = "✅" if success else "❌"
            
            # 항목 컨테이너
            item_container = lv.obj(self.history_list)
            item_container.set_size(140, 10)
            item_container.set_pos(5, y_offset)
            item_container.set_style_bg_opa(0, 0)
            item_container.set_style_border_width(0, 0)
            item_container.set_style_pad_all(0, 0)
            
            # 시간 라벨
            time_label = lv.label(item_container)
            time_label.set_text(f"{date_str} {time_str}")
            time_label.set_style_text_font(self.ui_style.font_small, 0)
            time_label.set_style_text_color(lv.color_hex(0x666666), 0)
            time_label.set_pos(0, 0)
            
            # 일정 라벨
            meal_label = lv.label(item_container)
            meal_label.set_text(meal_name)
            meal_label.set_style_text_font(self.ui_style.font_small, 0)
            meal_label.set_style_text_color(lv.color_hex(0x333333), 0)
            meal_label.set_pos(50, 0)
            
            # 상태 라벨
            status_label = lv.label(item_container)
            status_label.set_text(status_icon)
            status_label.set_style_text_font(self.ui_style.font_small, 0)
            status_label.set_pos(120, 0)
            
        except Exception as e:
            print(f"[ERROR] 기록 항목 생성 실패: {e}")
    
    def _update_stats_display(self):
        """통계 정보 업데이트"""
        try:
            # 기존 라벨들 제거
            for child in self.stats_container.get_children():
                child.delete()
            
            # 오늘 통계 계산
            wifi_mgr = get_wifi_manager()
            today = wifi_mgr.get_kst_time()
            today_str = f"{today[0]:04d}-{today[1]:02d}-{today[2]:02d}"
            today_logs = [log for log in self.dispense_logs if log.get("date") == today_str]
            
            success_count = len([log for log in today_logs if log.get("success")])
            total_count = len(today_logs)
            
            # 통계 텍스트
            if total_count > 0:
                stats_text = f"오늘: {success_count}/{total_count} 성공"
            else:
                stats_text = "오늘: 복용 기록 없음"
            
            # 통계 라벨
            stats_label = lv.label(self.stats_container)
            stats_label.set_text(stats_text)
            stats_label.set_style_text_font(self.ui_style.font_small, 0)
            stats_label.set_style_text_color(lv.color_hex(0x333333), 0)
            stats_label.align(lv.ALIGN.CENTER, 0, 0)
            
        except Exception as e:
            print(f"[ERROR] 통계 정보 업데이트 실패: {e}")
    
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
            # 기록 데이터 새로고침
            self._load_and_display_history()
            self._update_stats_display()
            
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
