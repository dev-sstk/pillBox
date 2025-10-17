"""
알람 시스템
5분 간격 재알람 및 배출 확인 기능
"""
from wifi_manager import get_wifi_manager

class AlarmSystem:
    """알람 시스템 클래스"""
    
    def __init__(self, data_manager, audio_system=None, led_controller=None):
        """알람 시스템 초기화"""
        self.data_manager = data_manager
        self.audio_system = audio_system
        self.led_controller = led_controller
        
        # 알람 설정
        self.alarm_settings = {
            "enabled": True,
            "reminder_interval": 5,  # 분
            "max_reminders": 5,  # 5회로 변경
            "sound_enabled": True,
            "led_enabled": True
        }
        
        # 알람 상태
        self.active_alarms = {}  # {dose_index: alarm_info}
        self.alarm_history = []  # 알람 기록
        
        print("[OK] AlarmSystem 초기화 완료")
    
    def trigger_dose_alarm(self, dose_index, dose_time, meal_name):
        """복용 알람 트리거"""
        try:
            alarm_info = {
                "dose_index": dose_index,
                "dose_time": dose_time,
                "meal_name": meal_name,
                "triggered_at": self._get_current_timestamp(),
                "last_alarm_time": self._get_current_timestamp(),  # 마지막 알람 시간 추가
                "reminder_count": 0,
                "max_reminders": self.alarm_settings["max_reminders"],
                "confirmed": False,
                "dispensed": False,
                "status": "active"
            }
            
            self.active_alarms[dose_index] = alarm_info
            
            # 알람 기록 추가
            self.alarm_history.append({
                "timestamp": self._get_current_timestamp_string(),
                "dose_index": dose_index,
                "dose_time": dose_time,
                "meal_name": meal_name,
                "action": "triggered"
            })
            
            print(f"🔔 복용 알람 트리거: {meal_name} ({dose_time})")
            self._play_alarm_sound()
            self._show_alarm_led()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 복용 알람 트리거 실패: {e}")
            return False
    
    def check_reminder_alarms(self):
        """재알람 확인 - 5분 간격으로 최대 5회"""
        try:
            current_timestamp = self._get_current_timestamp()
            
            for dose_index, alarm_info in list(self.active_alarms.items()):
                if alarm_info["status"] != "active":
                    continue
                
                # 배출 확인됨이면 알람 종료
                if alarm_info["confirmed"] or alarm_info["dispensed"]:
                    self._end_alarm(dose_index, reason="completed")
                    continue
                
                # 마지막 알람 시간으로부터 5분 경과 확인
                last_alarm_time = alarm_info["last_alarm_time"]
                
                # 타입 체크: 문자열이면 숫자로 변환
                if isinstance(last_alarm_time, str):
                    print(f"[WARN] 알람 {dose_index}: 타임스탬프가 문자열입니다. 숫자로 변환합니다.")
                    # 문자열 타임스탬프를 현재 시간으로 재설정
                    alarm_info["last_alarm_time"] = current_timestamp
                    last_alarm_time = current_timestamp
                
                time_diff = current_timestamp - last_alarm_time
                minutes_passed = time_diff // 60  # 초를 분으로 변환
                
                print(f"[DEBUG] 알람 {dose_index}: 마지막 알람 {minutes_passed}분 전, 재알람 횟수 {alarm_info['reminder_count']}/{alarm_info['max_reminders']}")
                
                # 5분 경과 시 재알람
                if minutes_passed >= self.alarm_settings["reminder_interval"]:
                    if alarm_info["reminder_count"] < alarm_info["max_reminders"]:
                        print(f"🔔 재알람 {alarm_info['reminder_count'] + 1}/{alarm_info['max_reminders']}: {alarm_info['meal_name']}")
                        self._trigger_reminder(dose_index)
                    else:
                        # 최대 재알람 횟수 초과 시 실패 처리
                        print(f"❌ 최대 재알람 횟수 초과: {alarm_info['meal_name']} 복용 실패")
                        self._end_alarm(dose_index, reason="max_reminders_reached")
            
        except Exception as e:
            print(f"[ERROR] 재알람 확인 실패: {e}")
            import sys
            sys.print_exception(e)
    
    def _trigger_reminder(self, dose_index):
        """재알람 트리거"""
        try:
            if dose_index not in self.active_alarms:
                return False
            
            alarm_info = self.active_alarms[dose_index]
            alarm_info["reminder_count"] += 1
            alarm_info["last_alarm_time"] = self._get_current_timestamp()  # 마지막 알람 시간 업데이트
            
            # 재알람 기록 추가
            self.alarm_history.append({
                "timestamp": self._get_current_timestamp_string(),
                "dose_index": dose_index,
                "dose_time": alarm_info["dose_time"],
                "meal_name": alarm_info["meal_name"],
                "action": f"reminder_{alarm_info['reminder_count']}"
            })
            
            print(f"🔔 재알람 {alarm_info['reminder_count']}/{alarm_info['max_reminders']}: {alarm_info['meal_name']} ({alarm_info['dose_time']})")
            self._play_alarm_sound()
            self._show_alarm_led()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 재알람 트리거 실패: {e}")
            return False
    
    def confirm_dose(self, dose_index):
        """복용 확인"""
        try:
            if dose_index not in self.active_alarms:
                return False
            
            alarm_info = self.active_alarms[dose_index]
            alarm_info["confirmed"] = True
            alarm_info["confirmed_at"] = self._get_current_timestamp()
            
            # 확인 기록 추가
            self.alarm_history.append({
                "timestamp": alarm_info["confirmed_at"],
                "dose_index": dose_index,
                "dose_time": alarm_info["dose_time"],
                "meal_name": alarm_info["meal_name"],
                "action": "confirmed"
            })
            
            print(f"✅ 복용 확인됨: {alarm_info['meal_name']} ({alarm_info['dose_time']})")
            self._stop_alarm_sound()
            self._hide_alarm_led()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 복용 확인 실패: {e}")
            return False
    
    def confirm_dispense(self, dose_index):
        """배출 확인"""
        try:
            if dose_index not in self.active_alarms:
                return False
            
            alarm_info = self.active_alarms[dose_index]
            alarm_info["dispensed"] = True
            alarm_info["dispensed_at"] = self._get_current_timestamp()
            
            # 배출 기록 추가
            self.alarm_history.append({
                "timestamp": alarm_info["dispensed_at"],
                "dose_index": dose_index,
                "dose_time": alarm_info["dose_time"],
                "meal_name": alarm_info["meal_name"],
                "action": "dispensed"
            })
            
            print(f"💊 배출 확인됨: {alarm_info['meal_name']} ({alarm_info['dose_time']})")
            self._stop_alarm_sound()
            self._hide_alarm_led()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 배출 확인 실패: {e}")
            return False
    
    def _end_alarm(self, dose_index, reason="completed"):
        """알람 종료"""
        try:
            if dose_index not in self.active_alarms:
                return False
            
            alarm_info = self.active_alarms[dose_index]
            alarm_info["status"] = "ended"
            alarm_info["ended_at"] = self._get_current_timestamp()
            alarm_info["end_reason"] = reason
            
            # 종료 기록 추가
            self.alarm_history.append({
                "timestamp": alarm_info["ended_at"],
                "dose_index": dose_index,
                "dose_time": alarm_info["dose_time"],
                "meal_name": alarm_info["meal_name"],
                "action": f"ended_{reason}"
            })
            
            print(f"🔕 알람 종료: {alarm_info['meal_name']} ({reason})")
            self._stop_alarm_sound()
            self._hide_alarm_led()
            
            # 복용 실패 처리 (최대 재알람 횟수 초과)
            if reason == "max_reminders_reached":
                self._handle_dispense_failure(dose_index, alarm_info)
            
            # 완료된 알람은 제거
            if reason in ["completed", "max_reminders_reached"]:
                del self.active_alarms[dose_index]
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 알람 종료 실패: {e}")
            return False
    
    def _handle_dispense_failure(self, dose_index, alarm_info):
        """복용 실패 처리"""
        try:
            meal_name = alarm_info.get("meal_name", f"일정 {dose_index + 1}")
            dose_time = alarm_info.get("dose_time", "")
            
            print(f"❌ 복용 실패 처리: {meal_name} ({dose_time})")
            
            # 데이터 매니저에 실패 기록 저장
            if hasattr(self, 'data_manager') and self.data_manager:
                self.data_manager.log_dispense(dose_index, False, reason="max_reminders_reached")
            
            # 실패 기록 추가
            self.alarm_history.append({
                "timestamp": self._get_current_timestamp(),
                "dose_index": dose_index,
                "dose_time": dose_time,
                "meal_name": meal_name,
                "action": "dispense_failed"
            })
            
            print(f"[OK] 복용 실패 기록 저장: {meal_name}")
            
        except Exception as e:
            print(f"[ERROR] 복용 실패 처리 실패: {e}")
    
    def _play_alarm_sound(self):
        """알람 소리 재생 (버저 + 음성)"""
        try:
            if not self.alarm_settings["sound_enabled"]:
                return
            
            if self.audio_system:
                # 1. 버저 알람 소리 재생
                self.audio_system.play_alarm_sound()
                
                # 2. take_medicine.wav 음성 파일 재생
                print("🔊 알람 시 복용 안내 음성 재생")
                self.audio_system.play_voice("take_medicine.wav", blocking=False)
            else:
                # 시뮬레이션
                print("🔊 알람 소리 재생 (시뮬레이션)")
                print("🔊 복용 안내 음성 재생 (시뮬레이션)")
                
        except Exception as e:
            print(f"[ERROR] 알람 소리 재생 실패: {e}")
    
    def _stop_alarm_sound(self):
        """알람 소리 정지"""
        try:
            if self.audio_system:
                self.audio_system.stop_alarm_sound()
            else:
                print("🔇 알람 소리 정지 (시뮬레이션)")
                
        except Exception as e:
            print(f"[ERROR] 알람 소리 정지 실패: {e}")
    
    def _show_alarm_led(self):
        """알람 LED 표시"""
        try:
            if not self.alarm_settings["led_enabled"]:
                return
            
            if self.led_controller:
                # 실제 LED 컨트롤러 사용
                self.led_controller.show_alarm_led()
            else:
                # LED 컨트롤러가 없으면 시뮬레이션
                print("💡 알람 LED 켜짐 (시뮬레이션)")
            
        except Exception as e:
            print(f"[ERROR] 알람 LED 표시 실패: {e}")
    
    def _hide_alarm_led(self):
        """알람 LED 숨김"""
        try:
            if not self.alarm_settings["led_enabled"]:
                return
            
            if self.led_controller:
                # 실제 LED 컨트롤러 사용
                self.led_controller.hide_alarm_led()
            else:
                # LED 컨트롤러가 없으면 시뮬레이션
                print("💡 알람 LED 꺼짐 (시뮬레이션)")
            
        except Exception as e:
            print(f"[ERROR] 알람 LED 숨김 실패: {e}")
    
    def get_active_alarms(self):
        """활성 알람 목록 반환"""
        return {k: v for k, v in self.active_alarms.items() if v["status"] == "active"}
    
    def get_alarm_status(self, dose_index):
        """특정 알람 상태 반환"""
        if dose_index in self.active_alarms:
            return self.active_alarms[dose_index]
        return None
    
    def get_alarm_summary(self):
        """알람 요약 정보 반환"""
        try:
            active_count = len(self.get_active_alarms())
            total_history = len(self.alarm_history)
            
            # 오늘 알람 통계
            wifi_mgr = get_wifi_manager()
            current_time = wifi_mgr.get_kst_time()
            today = f"{current_time[0]:04d}-{current_time[1]:02d}-{current_time[2]:02d}"
            today_alarms = [a for a in self.alarm_history if a["timestamp"].startswith(today)]
            
            summary = {
                "active_alarms": active_count,
                "total_history": total_history,
                "today_alarms": len(today_alarms),
                "settings": self.alarm_settings,
                "recent_alarms": today_alarms[-5:] if today_alarms else []
            }
            
            return summary
            
        except Exception as e:
            print(f"[ERROR] 알람 요약 생성 실패: {e}")
            return None
    
    def update_alarm_settings(self, new_settings):
        """알람 설정 업데이트"""
        try:
            self.alarm_settings.update(new_settings)
            
            # 데이터 매니저에 설정 저장
            settings = self.data_manager.load_settings()
            settings["alarm_settings"] = self.alarm_settings
            self.data_manager.save_settings(settings)
            
            print("[OK] 알람 설정 업데이트 완료")
            return True
            
        except Exception as e:
            print(f"[ERROR] 알람 설정 업데이트 실패: {e}")
            return False
    
    def _get_current_timestamp(self):
        """현재 시간 타임스탬프 반환 (초 단위)"""
        try:
            import time
            return time.time()  # Unix timestamp (초 단위)
        except Exception as e:
            print(f"[ERROR] 타임스탬프 생성 실패: {e}")
            return 0
    
    def _get_current_timestamp_string(self):
        """현재 시간 타임스탬프 반환 (문자열)"""
        try:
            wifi_mgr = get_wifi_manager()
            current_time = wifi_mgr.get_kst_time()
            return f"{current_time[0]:04d}-{current_time[1]:02d}-{current_time[2]:02d}T{current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"
        except Exception as e:
            print(f"[ERROR] 타임스탬프 문자열 생성 실패: {e}")
            return "2025-01-01T00:00:00"
    
    def get_alarm_history(self):
        """알람 기록 반환"""
        try:
            return self.alarm_history
        except Exception as e:
            print(f"[ERROR] 알람 기록 조회 실패: {e}")
            return []
    
    def clear_alarm_history(self):
        """알람 기록 삭제"""
        try:
            self.alarm_history = []
            print("[OK] 알람 기록 삭제 완료")
            return True
            
        except Exception as e:
            print(f"[ERROR] 알람 기록 삭제 실패: {e}")
            return False
    
    def force_end_all_alarms(self):
        """모든 알람 강제 종료"""
        try:
            for dose_index in list(self.active_alarms.keys()):
                self._end_alarm(dose_index, reason="force_ended")
            
            print("[OK] 모든 알람 강제 종료 완료")
            return True
            
        except Exception as e:
            print(f"[ERROR] 모든 알람 강제 종료 실패: {e}")
            return False
