"""
메인 화면
오늘의 알약 일정을 표시하는 대시보드 화면
Modern UI 스타일 적용
"""

import sys
sys.path.append("/")

import time
import lvgl as lv
from ui_style import UIStyle
from machine import RTC
from wifi_manager import wifi_manager

class MainScreen:
    """메인 화면 클래스 - Modern UI 스타일"""
    
    def __init__(self, screen_manager):
        """메인 화면 초기화"""
        self.screen_manager = screen_manager
        self.screen_name = 'main'
        self.screen_obj = None
        self.current_dose_index = 0
        self.dose_schedule = []  # 복용 일정
        self.last_update_time = 0
        
        # 실시간 정보
        self.rtc = RTC()
        self.current_time = ""
        self.next_dose_time = ""
        self.time_until_next = ""
        self.wifi_status = {"connected": False, "ssid": None}
        
        # 필박스 상태
        self.disk_states = {"disk_1": 0, "disk_2": 0, "disk_3": 0}  # 각 디스크의 충전된 칸 수
        self.battery_level = 85  # 배터리 레벨 (시뮬레이션)
        self.wifi_connected = True  # WiFi 연결 상태 (시뮬레이션)
        
        # UI 업데이트 타이머
        self.ui_update_counter = 0
        self.battery_simulation_step = 0  # 배터리 시뮬레이션 단계 (0: 완충, 1: 3단계, 2: 2단계, 3: 1단계, 4: 방전)
        self.is_charging = False  # 충전 상태 (고정값)
        
        # UI 스타일 시스템 초기화
        self.ui_style = UIStyle()
        
        # 샘플 데이터 초기화
        self._init_sample_data()
        
        # Modern 화면 생성
        self._create_modern_screen()
        
        print(f"✅ {self.screen_name} 화면 초기화 완료")
    
    def _init_sample_data(self):
        """샘플 데이터 초기화"""
        # NTP 시간을 활용한 현재 날짜 가져오기 (RTC 백업 포함)
        try:
            # WiFi 매니저에서 한국 시간 가져오기
            if hasattr(self, 'wifi_manager') and self.wifi_manager and self.wifi_manager.is_connected and self.wifi_manager.time_synced:
                kst_time = self.wifi_manager.get_kst_time()
                year, month, day, hour, minute, second = kst_time[:6]
                print(f"  📅 NTP 시간으로 날짜 설정: {year}년 {month}월 {day}일 {hour}:{minute:02d}:{second:02d}")
                
                # NTP 시간을 RTC에 백업 저장 (외부 배터리 활용)
                from machine import RTC
                rtc = RTC()
                # RTC는 (year, month, day, weekday, hour, minute, second, microsecond) 형식
                weekday = (day - 1) % 7  # 간단한 요일 계산 (0=월요일)
                rtc.datetime((year, month, day, weekday, hour, minute, second, 0))
                print(f"  💾 NTP 시간을 RTC에 백업 저장 완료")
                
            else:
                # NTP가 없으면 RTC 백업 시간 사용 (외부 배터리로 유지됨)
                from machine import RTC
                rtc = RTC()
                year, month, day = rtc.datetime()[:3]
                print(f"  📅 RTC 백업 시간으로 날짜 설정: {year}년 {month}월 {day}일 (외부 배터리)")
                
        except Exception as e:
            # 오류 시 기본값 사용
            month, day = 12, 25
            print(f"  ⚠️ 날짜 설정 오류, 기본값 사용: {month}월 {day}일 ({e})")
        
        # 샘플 복용 일정 (새로운 형식) - 약 종류 제거
        self.dose_schedule = [
            {"time": "08:00", "status": "completed"},  # 복용완료
            {"time": "12:00", "status": "failed"},     # 복용실패
            {"time": "18:00", "status": "pending"}     # 복용대기
        ]
        self.current_date = f"{year}-{month:02d}-{day:02d}"
    
    def _create_modern_screen(self):
        """Modern 스타일 화면 생성"""
        print(f"  📱 {self.screen_name} Modern 화면 생성 시작...")
        
        try:
            # 메모리 정리
            import gc
            gc.collect()
            print(f"  ✅ 메모리 정리 완료")
            
            # 화면 생성
            print(f"  📱 화면 객체 생성...")
            self.screen_obj = lv.obj()
            print(f"  📱 화면 객체 생성됨: {self.screen_obj}")
            
            # 화면 배경 스타일 적용 (Modern 스타일)
            self.ui_style.apply_screen_style(self.screen_obj)
            
            # 스크롤바 완전 비활성화
            self.screen_obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.screen_obj.set_scroll_dir(lv.DIR.NONE)
            
            print(f"  ✅ 화면 배경 설정 완료")
            
            # 화면 크기 설정
            self.screen_obj.set_size(160, 128)
            print(f"  📱 화면 크기: 160x128")
            
            # 메인 컨테이너 생성
            print(f"  📱 메인 컨테이너 생성 시도...")
            self.main_container = lv.obj(self.screen_obj)
            self.main_container.set_size(160, 128)
            self.main_container.align(lv.ALIGN.CENTER, 0, 0)
            self.main_container.set_style_bg_opa(0, 0)  # 투명 배경
            self.main_container.set_style_border_width(0, 0)  # 테두리 없음
            
            # 스크롤바 완전 비활성화
            self.main_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.main_container.set_scroll_dir(lv.DIR.NONE)
            
            print(f"  📱 메인 컨테이너 생성 완료")
            
            # 제목 영역 생성
            print(f"  📱 제목 영역 생성 시도...")
            self._create_title_area()
            print(f"  📱 제목 영역 생성 완료")
            
            # 복용 일정 영역 생성
            print(f"  📱 복용 일정 영역 생성 시도...")
            self._create_schedule_area()
            print(f"  📱 복용 일정 영역 생성 완료")
            
            # 하단 버튼 힌트 영역 생성
            print(f"  📱 버튼 힌트 영역 생성 시도...")
            self._create_button_hints_area()
            print(f"  📱 버튼 힌트 영역 생성 완료")
            
            print(f"  ✅ Modern 화면 생성 완료")
            
        except Exception as e:
            print(f"  ❌ Modern 화면 생성 중 오류 발생: {e}")
            import sys
            sys.print_exception(e)
            # 기본 화면 생성 시도
            print(f"  📱 {self.screen_name} 기본 화면 생성 시도...")
            try:
                self._create_basic_screen()
                print(f"  ✅ {self.screen_name} 기본 화면 초기화 완료")
            except Exception as e2:
                print(f"  ❌ {self.screen_name} 기본 화면 초기화도 실패: {e2}")
                import sys
                sys.print_exception(e2)
    
    def _create_basic_screen(self):
        """기본 화면 생성 (오류 시 대안)"""
        print(f"  📱 {self.screen_name} 기본 화면 생성 시작...")
        
        # 기본 화면 객체 생성
        self.screen_obj = lv.obj()
        self.screen_obj.set_size(160, 128)
        
        # 기본 라벨 생성
        self.title_label = lv.label(self.screen_obj)
        self.title_label.set_text("메인 화면")
        self.title_label.align(lv.ALIGN.CENTER, 0, 0)
        
        print(f"  ✅ 기본 화면 생성 완료")
    
    def _create_title_area(self):
        """제목 영역 생성"""
        try:
            # 제목 컨테이너
            self.title_container = lv.obj(self.main_container)
            self.title_container.set_size(160, 30)  # 높이를 30으로 증가
            self.title_container.align(lv.ALIGN.TOP_MID, 0, -5)  # 제목을 위로 4픽셀 더 이동 (-1 -> -5)
            self.title_container.set_style_bg_opa(0, 0)
            self.title_container.set_style_border_width(0, 0)
            
            # 스크롤바 완전 비활성화
            self.title_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.title_container.set_scroll_dir(lv.DIR.NONE)
            
            print("  ✅ 제목 컨테이너 생성 완료")
            
            # 제목 텍스트
            self.title_text = lv.label(self.title_container)
            self.title_text.set_text("오늘의 복용 일정")
            self.title_text.align(lv.ALIGN.TOP_MID, 0, 0)
            self.title_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            self.title_text.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
            
            # 한국어 폰트 적용
            korean_font = getattr(lv, "font_notosans_kr_regular", None)
            if korean_font:
                self.title_text.set_style_text_font(korean_font, 0)
                print("  ✅ 제목에 한국어 폰트 적용 완료")
            
            # 현재 시간 표시 (제목 컨테이너에서 제거하고 독립적으로 배치)
            # self.current_time_label = lv.label(self.title_container)
            # self.current_time_label.set_text(self.current_time)
            # self.current_time_label.align(lv.ALIGN.BOTTOM_MID, 0, -2)
            # self.current_time_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            # self.current_time_label.set_style_text_color(lv.color_hex(0x007AFF), 0)
            # 
            # if korean_font:
            #     self.current_time_label.set_style_text_font(korean_font, 0)
            
            # 상태 표시기 (배터리, WiFi) - 제목 컨테이너에서 제거하고 독립적으로 배치
            # self._create_status_indicators()
            
            print("  ✅ 제목 텍스트 생성 완료")
            
            # 현재 시간과 상태 표시기를 독립적으로 생성
            self._create_current_time_and_status()
            
        except Exception as e:
            print(f"  ❌ 제목 영역 생성 실패: {e}")
    
    def _create_current_time_and_status(self):
        """현재 시간과 상태 표시기를 독립적으로 생성"""
        try:
            # 현재 시간 표시 (좌측 상단) - 기본 폰트 사용
            self.current_time_label = lv.label(self.main_container)
            self.current_time_label.set_text(self.current_time)
            self.current_time_label.align(lv.ALIGN.TOP_LEFT, 5, -10)  # 위로 4픽셀 더 이동 (-6 -> -10)
            self.current_time_label.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
            self.current_time_label.set_style_text_color(lv.color_hex(0x007AFF), 0)
            # 기본 폰트 사용 (한국어 폰트 적용하지 않음)
            
            # 상태 표시기 (우측 상단)
            self._create_status_indicators()
            
            print("  ✅ 현재 시간과 상태 표시기 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 현재 시간과 상태 표시기 생성 실패: {e}")
    
    def _create_status_indicators(self):
        """상태 표시기 생성 (배터리, WiFi)"""
        try:
            # 상태 표시기 컨테이너 (메인 컨테이너에 직접 배치하여 맨 위 상단에 위치)
            status_container = lv.obj(self.main_container)
            status_container.set_size(80, 15)  # 너비를 80으로 증가
            status_container.align(lv.ALIGN.TOP_RIGHT, -5, -10)  # 위로 4픽셀 더 이동 (-6 -> -10)
            status_container.set_style_bg_opa(0, 0)
            status_container.set_style_border_width(0, 0)
            
            # 스크롤바 완전 비활성화
            status_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            status_container.set_scroll_dir(lv.DIR.NONE)
            
            # WiFi 표시 (LVGL 내장 아이콘 사용 - 기본 폰트) - 왼쪽으로 이동
            wifi_icon = lv.SYMBOL.WIFI if self.wifi_connected else lv.SYMBOL.CLOSE
            self.wifi_label = lv.label(status_container)
            self.wifi_label.set_text(wifi_icon)
            self.wifi_label.align(lv.ALIGN.LEFT_MID, 0, 0)
            self.wifi_label.set_style_text_color(lv.color_hex(0x007AFF) if self.wifi_connected else lv.color_hex(0xFF3B30), 0)
            # 기본 폰트 사용 (한국어 폰트 적용하지 않음)
            
            # 배터리 전용 컨테이너 (WiFi와 완전 분리)
            battery_container = lv.obj(self.main_container)
            battery_container.set_size(70, 15)  # 너비를 왼쪽으로 10픽셀 늘림 (60 -> 70)
            battery_container.align(lv.ALIGN.TOP_RIGHT, 19, -10)  # 왼쪽으로 10픽셀 이동 (29 -> 19)
            battery_container.set_style_bg_opa(0, 0)
            battery_container.set_style_border_width(0, 0)
            
            # 스크롤바 완전 비활성화
            battery_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            battery_container.set_scroll_dir(lv.DIR.NONE)
            
            # 배터리 아이콘 (분리된 라벨) - 충전 상태 포함
            if self.is_charging:
                battery_icon = lv.SYMBOL.CHARGE  # 충전중일 때 충전 아이콘
            elif self.battery_level > 75:
                battery_icon = lv.SYMBOL.BATTERY_FULL  # 100% - 완전 충전
            elif self.battery_level > 50:
                battery_icon = lv.SYMBOL.BATTERY_3  # 75% - 3/4 충전
            elif self.battery_level > 25:
                battery_icon = lv.SYMBOL.BATTERY_2  # 50% - 1/2 충전
            elif self.battery_level > 0:
                battery_icon = lv.SYMBOL.BATTERY_1  # 25% - 1/4 충전
            else:
                battery_icon = lv.SYMBOL.BATTERY_EMPTY  # 0% - 방전
            
            self.battery_icon_label = lv.label(battery_container)
            self.battery_icon_label.set_text(battery_icon)
            self.battery_icon_label.align(lv.ALIGN.LEFT_MID, -8, 0)  # 아이콘을 오른쪽으로 12픽셀 이동 (-20 -> -8)
            self.battery_icon_label.set_style_text_color(lv.color_hex(0x34C759), 0)
            # 기본 폰트 사용 (한국어 폰트 적용하지 않음)
            
            # 배터리 텍스트 (분리된 라벨)
            self.battery_text_label = lv.label(battery_container)
            self.battery_text_label.set_text(f"{self.battery_level}%")
            self.battery_text_label.align(lv.ALIGN.RIGHT_MID, 2, 0)  # 텍스트를 왼쪽으로 3픽셀 이동 (5 -> 2)
            self.battery_text_label.set_style_text_align(lv.TEXT_ALIGN.RIGHT, 0)
            self.battery_text_label.set_style_text_color(lv.color_hex(0x34C759), 0)
            # 기본 폰트 사용 (한국어 폰트 적용하지 않음)
            
            print("  ✅ 상태 표시기 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 상태 표시기 생성 실패: {e}")
    
    def _create_schedule_area(self):
        """복용 일정 영역 생성"""
        try:
            # 일정 컨테이너
            self.schedule_container = lv.obj(self.main_container)
            self.schedule_container.set_size(160, 90)  # 높이를 90으로 증가 (3개 일정 + 여백)
            self.schedule_container.align(lv.ALIGN.TOP_MID, 0, 9)  # 중앙 정렬 유지
            self.schedule_container.set_style_bg_opa(0, 0)
            self.schedule_container.set_style_border_width(0, 0)
            
            # 스크롤바 완전 비활성화
            self.schedule_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
            self.schedule_container.set_scroll_dir(lv.DIR.NONE)
            
            print("  ✅ 일정 컨테이너 생성 완료")
            
            # 날짜 표시
            date_label = lv.label(self.schedule_container)
            date_label.set_text(self.current_date)
            date_label.align(lv.ALIGN.TOP_MID, 0, 5)
            date_label.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
            # 기본 폰트 사용 (숫자와 하이픈이므로)
            
            # 복용 일정 표시 (새로운 형식)
            print(f"  📱 복용 일정 개수: {len(self.dose_schedule)}")
            self.schedule_labels = []
            for i, schedule in enumerate(self.dose_schedule):
                print(f"  📱 복용 일정 {i+1} 생성 시작: {schedule}")
                
                # 상태에 따른 아이콘만 사용 (한글 텍스트 제거)
                if schedule["status"] == "completed":
                    status_icon = lv.SYMBOL.OK
                    status_color = lv.color_hex(0x34C759)  # 초록색
                elif schedule["status"] == "failed":
                    status_icon = lv.SYMBOL.CLOSE
                    status_color = lv.color_hex(0xFF3B30)  # 빨간색
                else:  # pending
                    status_icon = lv.SYMBOL.BELL
                    status_color = lv.color_hex(0xFF9500)  # 주황색
                
                # 일정 아이템 컨테이너
                schedule_item = lv.obj(self.schedule_container)
                schedule_item.set_size(145, 22)
                schedule_item.align(lv.ALIGN.TOP_MID, 0, 20 + i * 18)  # 일정 간격을 22에서 18로 줄임
                schedule_item.set_style_bg_opa(0, 0)
                schedule_item.set_style_border_width(0, 0)
                
                # 스크롤바 완전 비활성화
                schedule_item.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
                schedule_item.set_scroll_dir(lv.DIR.NONE)
                
                # 시간과 아이콘을 하나의 라벨로 합쳐서 중앙 정렬
                combined_text = f"{schedule['time']} {status_icon}"
                combined_label = lv.label(schedule_item)
                combined_label.set_text(combined_text)
                combined_label.align(lv.ALIGN.CENTER, 0, 0)  # 화면 중앙 정렬
                combined_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
                combined_label.set_style_text_color(lv.color_hex(0x1D1D1F), 0)
                # 기본 폰트 사용 (시간과 아이콘 모두)
                
                self.schedule_labels.append(combined_label)
                print(f"  📱 복용 일정 {i+1} 생성 완료: {schedule['time']} {status_icon}")
            
            # 복용 카운트다운 표시 (일단 주석 처리)
            # self._create_countdown_display()
            
            # 디스크 상태 표시 (일단 주석 처리)
            # self._create_disk_status_display()
            
            print("  ✅ 복용 일정 영역 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 복용 일정 영역 생성 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _create_countdown_display(self):
        """복용 카운트다운 표시 생성"""
        try:
            # 카운트다운 컨테이너
            countdown_container = lv.obj(self.schedule_container)
            countdown_container.set_size(130, 15)
            countdown_container.align(lv.ALIGN.BOTTOM_MID, 0, -5)
            countdown_container.set_style_bg_opa(0, 0)
            countdown_container.set_style_border_width(0, 0)
            
            # 카운트다운 라벨
            self.countdown_label = lv.label(countdown_container)
            self.countdown_label.set_text("")
            self.countdown_label.align(lv.ALIGN.CENTER, 0, 0)
            self.countdown_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
            self.countdown_label.set_style_text_color(lv.color_hex(0xFF9500), 0)
            
            # 한국어 폰트 적용
            korean_font = getattr(lv, "font_notosans_kr_regular", None)
            if korean_font:
                self.countdown_label.set_style_text_font(korean_font, 0)
            
            print("  ✅ 카운트다운 표시 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 카운트다운 표시 생성 실패: {e}")
    
    def _create_disk_status_display(self):
        """디스크 상태 표시 생성"""
        try:
            # 디스크 상태 컨테이너
            disk_container = lv.obj(self.main_container)
            disk_container.set_size(140, 20)
            disk_container.align(lv.ALIGN.BOTTOM_MID, 0, -25)
            disk_container.set_style_bg_opa(0, 0)
            disk_container.set_style_border_width(0, 0)
            
            # 디스크 상태 라벨들
            self.disk_status_labels = []
            for i, (disk_key, loaded_count) in enumerate(self.disk_states.items()):
                disk_label = lv.label(disk_container)
                status_text = f"디스크{i+1}: {loaded_count}/15"
                disk_label.set_text(status_text)
                disk_label.align(lv.ALIGN.LEFT_MID, 0, i * 6)
                disk_label.set_style_text_color(lv.color_hex(0x8E8E93), 0)
                
                # 한국어 폰트 적용
                korean_font = getattr(lv, "font_notosans_kr_regular", None)
                if korean_font:
                    disk_label.set_style_text_font(korean_font, 0)
                
                self.disk_status_labels.append(disk_label)
            
            print("  ✅ 디스크 상태 표시 생성 완료")
            
        except Exception as e:
            print(f"  ❌ 디스크 상태 표시 생성 실패: {e}")
    
    def _create_button_hints_area(self):
        """하단 버튼 힌트 영역 생성 - Modern 스타일"""
        # 버튼 힌트 컨테이너
        self.hints_container = lv.obj(self.main_container)
        self.hints_container.set_size(140, 18)
        self.hints_container.align(lv.ALIGN.BOTTOM_MID, 0, 12)  # 12픽셀 아래로 이동
        # 투명 배경 (Modern 스타일)
        self.hints_container.set_style_bg_opa(0, 0)
        self.hints_container.set_style_border_width(0, 0)
        self.hints_container.set_style_pad_all(0, 0)
        
        # 버튼 힌트 텍스트 (Modern 스타일) - 모던 UI 색상
        self.hints_text = self.ui_style.create_label(
            self.hints_container,
            "A:^  B:v  C:<  D:OK",
            'text_caption',
            0x8E8E93  # 모던 라이트 그레이
        )
        self.hints_text.align(lv.ALIGN.BOTTOM_MID, 0, -2)
        # 버튼 힌트 텍스트 위치 고정 (움직이지 않도록)
        self.hints_text.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
    
    def get_title(self):
        """화면 제목"""
        return "메인 화면"
    
    def get_button_hints(self):
        """버튼 힌트"""
        return "A:^  B:v  C:<  D:OK"
    
    def get_voice_file(self):
        """안내 음성 파일"""
        return "wav_main_screen.wav"
    
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
        print(f"📱 {self.screen_name} 화면 숨기기")
        # 화면 숨기기 로직 (필요시 구현)
        pass
    
    def update(self):
        """화면 업데이트 (ScreenManager에서 호출)"""
        try:
            # UI 업데이트 카운터 증가
            self.ui_update_counter += 1
            
            # 1초마다 시간 업데이트 (실제로는 더 자주 호출될 수 있음)
            if self.ui_update_counter % 10 == 0:  # 약 1초마다
                self._update_current_time()
                self._update_next_dose_info()
                self._update_disk_states()
                self._update_battery_simulation()  # 배터리 시뮬레이션 업데이트
                self._update_status_indicators()
                
                # 화면 요소들 업데이트
                self._update_time_display()
                self._update_dose_countdown()
                self._update_disk_status_display()
                
        except Exception as e:
            print(f"  ❌ 메인 스크린 업데이트 실패: {e}")
    
    def _update_battery_simulation(self):
        """배터리 시뮬레이션 업데이트 (완충 -> 3단계 -> 2단계 -> 1단계 -> 방전 순서)"""
        try:
            # 배터리 시뮬레이션 단계별 레벨 설정
            battery_levels = [100, 75, 50, 25, 0]  # 완충, 3단계, 2단계, 1단계, 방전
            
            # 현재 단계의 배터리 레벨 설정 (충전 상태는 고정값 False 사용)
            self.battery_level = battery_levels[self.battery_simulation_step]
            # self.is_charging은 고정값 False 유지
            
            # 다음 단계로 이동 (5단계 순환)
            self.battery_simulation_step = (self.battery_simulation_step + 1) % 5
            
            print(f"  🔋 배터리 시뮬레이션: {self.battery_level}% (단계 {self.battery_simulation_step})")
            
        except Exception as e:
            print(f"  ❌ 배터리 시뮬레이션 업데이트 실패: {e}")
    
    def _update_current_time(self):
        """현재 시간 업데이트 (WiFi 매니저 사용)"""
        try:
            # WiFi 매니저에서 한국 시간 가져오기
            if wifi_manager.is_connected and wifi_manager.time_synced:
                kst_time = wifi_manager.get_kst_time()
                hour = kst_time[3]
                minute = kst_time[4]
                self.current_time = f"{hour:02d}:{minute:02d}"
                self.wifi_status = {"connected": True, "ssid": wifi_manager.connected_ssid}
            else:
                # WiFi 연결이 없으면 RTC 사용
                current = self.rtc.datetime()
                hour = current[4]
                minute = current[5]
                self.current_time = f"{hour:02d}:{minute:02d}"
                self.wifi_status = {"connected": False, "ssid": None}
        except Exception as e:
            print(f"  ❌ 현재 시간 업데이트 실패: {e}")
            self.current_time = "00:00"
    
    def _update_next_dose_info(self):
        """다음 복용 시간 정보 업데이트"""
        try:
            if not self.dose_schedule:
                self.next_dose_time = ""
                self.time_until_next = ""
                return
            
            # 현재 시간을 분 단위로 변환
            current_hour, current_minute = map(int, self.current_time.split(':'))
            current_total_minutes = current_hour * 60 + current_minute
            
            next_dose = None
            min_time_diff = float('inf')
            
            # 아직 복용하지 않은 일정 중에서 가장 가까운 시간 찾기
            for schedule in self.dose_schedule:
                if not schedule.get("taken", False):
                    dose_hour, dose_minute = map(int, schedule["time"].split(':'))
                    dose_total_minutes = dose_hour * 60 + dose_minute
                    
                    # 오늘의 복용 시간인지 확인
                    if dose_total_minutes >= current_total_minutes:
                        time_diff = dose_total_minutes - current_total_minutes
                        if time_diff < min_time_diff:
                            min_time_diff = time_diff
                            next_dose = schedule
            
            if next_dose:
                self.next_dose_time = next_dose["time"]
                # 남은 시간을 시간:분 형태로 변환
                hours_left = min_time_diff // 60
                minutes_left = min_time_diff % 60
                if hours_left > 0:
                    self.time_until_next = f"{hours_left}시간 {minutes_left}분"
                else:
                    self.time_until_next = f"{minutes_left}분"
            else:
                self.next_dose_time = "오늘 완료"
                self.time_until_next = "모든 복용 완료"
                
        except Exception as e:
            print(f"  ❌ 다음 복용 시간 업데이트 실패: {e}")
            self.next_dose_time = ""
            self.time_until_next = ""
    
    def _update_disk_states(self):
        """디스크 상태 업데이트 (필박스 시스템과 연동)"""
        try:
            # pill_loading_screen에서 디스크 상태 가져오기
            if hasattr(self.screen_manager, 'screens') and 'pill_loading' in self.screen_manager.screens:
                pill_loading_screen = self.screen_manager.screens['pill_loading']
                if hasattr(pill_loading_screen, 'get_disk_loading_status'):
                    disk_status = pill_loading_screen.get_disk_loading_status()
                    for disk_key, status in disk_status.items():
                        if disk_key in self.disk_states:
                            self.disk_states[disk_key] = status.get('loaded_count', 0)
        except Exception as e:
            print(f"  ❌ 디스크 상태 업데이트 실패: {e}")
    
    def _update_status_indicators(self):
        """상태 표시기 업데이트 (배터리, WiFi 등)"""
        try:
            # WiFi 상태 업데이트
            self.wifi_connected = self.wifi_status["connected"]
            
            # WiFi 표시기 업데이트 (LVGL 내장 아이콘 사용)
            if hasattr(self, 'wifi_label'):
                wifi_icon = lv.SYMBOL.WIFI if self.wifi_connected else lv.SYMBOL.CLOSE
                self.wifi_label.set_text(wifi_icon)
                color = lv.color_hex(0x007AFF) if self.wifi_connected else lv.color_hex(0xFF3B30)
                self.wifi_label.set_style_text_color(color, 0)
            
            # 배터리 아이콘 업데이트 (LVGL 내장 아이콘 사용) - 충전 상태 포함
            if hasattr(self, 'battery_icon_label'):
                # 충전 상태 확인 후 배터리 레벨에 따른 아이콘 선택
                if self.is_charging:
                    battery_icon = lv.SYMBOL.CHARGE  # 충전중일 때 충전 아이콘
                elif self.battery_level > 75:
                    battery_icon = lv.SYMBOL.BATTERY_FULL  # 100% - 완전 충전
                elif self.battery_level > 50:
                    battery_icon = lv.SYMBOL.BATTERY_3  # 75% - 3/4 충전
                elif self.battery_level > 25:
                    battery_icon = lv.SYMBOL.BATTERY_2  # 50% - 1/2 충전
                elif self.battery_level > 0:
                    battery_icon = lv.SYMBOL.BATTERY_1  # 25% - 1/4 충전
                else:
                    battery_icon = lv.SYMBOL.BATTERY_EMPTY  # 0% - 방전
                
                self.battery_icon_label.set_text(battery_icon)
            
            # 배터리 텍스트 업데이트
            if hasattr(self, 'battery_text_label'):
                self.battery_text_label.set_text(f"{self.battery_level}%")
                
        except Exception as e:
            print(f"  ❌ 상태 표시기 업데이트 실패: {e}")
    
    def _update_time_display(self):
        """시간 표시 업데이트"""
        try:
            if hasattr(self, 'current_time_label'):
                self.current_time_label.set_text(self.current_time)
        except Exception as e:
            print(f"  ❌ 시간 표시 업데이트 실패: {e}")
    
    def _update_dose_countdown(self):
        """복용 카운트다운 업데이트"""
        try:
            if hasattr(self, 'countdown_label'):
                if self.time_until_next:
                    countdown_text = f"다음 복용까지: {self.time_until_next}"
                    self.countdown_label.set_text(countdown_text)
                else:
                    self.countdown_label.set_text("")
        except Exception as e:
            print(f"  ❌ 복용 카운트다운 업데이트 실패: {e}")
    
    def _update_disk_status_display(self):
        """디스크 상태 표시 업데이트"""
        try:
            if hasattr(self, 'disk_status_labels'):
                for i, (disk_key, loaded_count) in enumerate(self.disk_states.items()):
                    if i < len(self.disk_status_labels):
                        status_text = f"디스크{i+1}: {loaded_count}/15"
                        self.disk_status_labels[i].set_text(status_text)
        except Exception as e:
            print(f"  ❌ 디스크 상태 표시 업데이트 실패: {e}")
    
    def on_button_a(self):
        """버튼 A (이전) 처리 - 이전 복용 일정으로 이동"""
        print("이전 복용 일정으로 이동")
        
        if self.current_dose_index > 0:
            self.current_dose_index -= 1
            print(f"  📱 현재 복용 일정: {self.current_dose_index + 1}")
        else:
            print(f"  📱 이미 첫 번째 복용 일정")
    
    def on_button_b(self):
        """버튼 B (다음) 처리 - 다음 복용 일정으로 이동"""
        print("다음 복용 일정으로 이동")
        
        if self.current_dose_index < len(self.dose_schedule) - 1:
            self.current_dose_index += 1
            print(f"  📱 현재 복용 일정: {self.current_dose_index + 1}")
        else:
            print(f"  📱 이미 마지막 복용 일정")
    
    def on_button_c(self):
        """버튼 C (설정) 처리 - 설정 화면으로 이동"""
        print("설정 화면으로 이동")
        
        # 설정 화면이 등록되어 있으면 이동
        if 'settings' in self.screen_manager.screens:
            self.screen_manager.show_screen('settings')
        else:
            print("  📱 설정 화면이 등록되지 않았습니다")
    
    def on_button_d(self):
        """버튼 D (상세) 처리 - 복용 상세 정보 표시"""
        print("복용 상세 정보 표시")
        
        if self.dose_schedule and 0 <= self.current_dose_index < len(self.dose_schedule):
            current_schedule = self.dose_schedule[self.current_dose_index]
            print(f"  📱 복용 상세 정보:")
            print(f"    - 시간: {current_schedule['time']}")
            print(f"    - 약물: {current_schedule['medication']}")
            print(f"    - 복용 상태: {'복용 완료' if current_schedule['taken'] else '복용 대기'}")
        else:
            print("  📱 표시할 복용 일정이 없습니다")
    
    def set_dose_schedule(self, dose_times):
        """복용 시간 설정 (dose_time_screen에서 호출)"""
        self.dose_schedule = []
        for i, time_str in enumerate(dose_times):
            self.dose_schedule.append({
                "time": time_str,
                "taken": False,
                "medication": f"약물 {i+1}"
            })
        print(f"  📱 복용 일정 설정됨: {len(self.dose_schedule)}개")
        
        # 화면 업데이트
        self._update_schedule_display()
    
    def _update_schedule_display(self):
        """복용 일정 표시 업데이트"""
        try:
            if hasattr(self, 'schedule_labels') and self.schedule_labels:
                for i, schedule_label in enumerate(self.schedule_labels):
                    if i < len(self.dose_schedule):
                        schedule = self.dose_schedule[i]
                        status_icon = "✅" if schedule["taken"] else "⏰"
                        schedule_text = f"{status_icon} {schedule['time']} {schedule['medication']}"
                        schedule_label.set_text(schedule_text)
                        print(f"  📱 복용 일정 {i+1} 업데이트: {schedule_text}")
        except Exception as e:
            print(f"  ❌ 복용 일정 표시 업데이트 실패: {e}")