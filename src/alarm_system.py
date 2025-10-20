"""
알람 시스템
5분 간격 재알람 및 배출 확인 기능
"""

import time

class AlarmSystem:
    """알람 시스템 클래스"""
    
    def __init__(self, data_manager, main_screen=None):
        """알람 시스템 초기화 - 지연 로딩 적용"""
        self.data_manager = data_manager
        self.main_screen = main_screen  # 메인 화면 참조 추가
        
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
        
        # 지연 로딩을 위한 캐시 (각 컴포넌트별)
        self._wifi_manager = None
        self._audio_system = None
        self._led_controller = None
        self._time_cache = {}
        self._last_time_check = 0
        
        # print("[OK] AlarmSystem 초기화 완료 (지연 로딩 적용)")
    
    def _get_wifi_manager(self):
        """WiFi 매니저 지연 로딩"""
        if self._wifi_manager is None:
            try:
                from wifi_manager import get_wifi_manager
                self._wifi_manager = get_wifi_manager()
                # print("[DEBUG] WiFi 매니저 지연 로딩 완료")
            except Exception as e:
                # print(f"[WARN] WiFi 매니저 로딩 실패: {e}")
                return None
        return self._wifi_manager
    
    def _get_audio_system(self):
        """오디오 시스템 지연 로딩"""
        if self._audio_system is None:
            try:
                from audio_system import AudioSystem
                self._audio_system = AudioSystem()
                # print("[DEBUG] 오디오 시스템 지연 로딩 완료")
            except Exception as e:
                # print(f"[WARN] 오디오 시스템 로딩 실패: {e}")
                return None
        return self._audio_system
    
    def _get_led_controller(self):
        """LED 컨트롤러 지연 로딩"""
        if self._led_controller is None:
            try:
                from led_controller import LEDController
                self._led_controller = LEDController()
                # print("[DEBUG] LED 컨트롤러 지연 로딩 완료")
            except Exception as e:
                # print(f"[WARN] LED 컨트롤러 로딩 실패: {e}")
                return None
        return self._led_controller
    
    def _cleanup_audio_system(self):
        """오디오 시스템 참조 정리 및 가비지 컬렉션"""
        try:
            if self._audio_system is not None:
                # print("[INFO] 오디오 시스템 참조 정리 시작...")
                # 오디오 시스템 정리 (필요시)
                if hasattr(self._audio_system, 'cleanup'):
                    self._audio_system.cleanup()
                self._audio_system = None
                # print("[OK] 오디오 시스템 참조 정리 완료")
        except Exception as e:
            # print(f"[WARN] 오디오 시스템 참조 정리 실패: {e}")
            pass
        finally:
            # 가비지 컬렉션
            import gc
            gc.collect()
            # print("[DEBUG] 오디오 시스템 가비지 컬렉션 완료")
    
    def _cleanup_led_controller(self):
        """LED 컨트롤러 참조 정리 및 가비지 컬렉션"""
        try:
            if self._led_controller is not None:
                # print("[INFO] LED 컨트롤러 참조 정리 시작...")
                # LED 컨트롤러 정리 (필요시)
                if hasattr(self._led_controller, 'cleanup'):
                    self._led_controller.cleanup()
                self._led_controller = None
                # print("[OK] LED 컨트롤러 참조 정리 완료")
        except Exception as e:
            # print(f"[WARN] LED 컨트롤러 참조 정리 실패: {e}")
            pass
        finally:
            # 가비지 컬렉션
            import gc
            gc.collect()
            # print("[DEBUG] LED 컨트롤러 가비지 컬렉션 완료")
    
    def _cleanup_wifi_manager(self):
        """WiFi 매니저 참조 정리 및 가비지 컬렉션"""
        try:
            if self._wifi_manager is not None:
                # print("[INFO] WiFi 매니저 참조 정리 시작...")
                self._wifi_manager = None
                # print("[OK] WiFi 매니저 참조 정리 완료")
        except Exception as e:
            # print(f"[WARN] WiFi 매니저 참조 정리 실패: {e}")
            pass
        finally:
            # 가비지 컬렉션
            import gc
            gc.collect()
            # print("[DEBUG] WiFi 매니저 가비지 컬렉션 완료")
    
    def cleanup_all_components(self):
        """모든 컴포넌트 참조 정리 및 가비지 컬렉션"""
        # print("[INFO] 알람 시스템 모든 컴포넌트 정리 시작...")
        self._cleanup_audio_system()
        self._cleanup_led_controller()
        self._cleanup_wifi_manager()
        # print("[OK] 알람 시스템 모든 컴포넌트 정리 완료")
    
    def _get_current_time(self):
        """현재 시간 지연 로딩"""
        wifi_mgr = self._get_wifi_manager()
        if wifi_mgr:
            try:
                return wifi_mgr.get_kst_time()
            except Exception as e:
                # print(f"[WARN] 시간 조회 실패: {e}")
                pass
        
        # WiFi 매니저가 없으면 시스템 시간 사용
        try:
            import time
            t = time.localtime()
            return (t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7])
        except Exception as e:
            # print(f"[WARN] 시스템 시간 조회 실패: {e}")
            return (2025, 1, 1, 0, 0, 0, 0, 1)
    
    def _get_current_timestamp(self):
        """현재 시간 타임스탬프 반환 (초 단위) - 지연 로딩"""
        try:
            import time
            return time.time()  # Unix timestamp (초 단위)
        except Exception as e:
            # print(f"[ERROR] 타임스탬프 생성 실패: {e}")
            return 0
    
    def _get_current_timestamp_string(self):
        """현재 시간 타임스탬프 반환 (문자열) - 지연 로딩"""
        try:
            current_time = self._get_current_time()
            return f"{current_time[0]:04d}-{current_time[1]:02d}-{current_time[2]:02d}T{current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"
        except Exception as e:
            # print(f"[ERROR] 타임스탬프 문자열 생성 실패: {e}")
            return "2025-01-01T00:00:00"
    
    def trigger_dose_alarm(self, dose_index, dose_time, meal_name):
        """복용 알람 트리거 - 자동 배출 시 알림음 재생"""
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
            
            # print(f"🔔 복용 알람 트리거: {meal_name} ({dose_time})")
            
            # 자동 배출 시 알림음 재생 (버저 3회 + LED 깜빡임 + 음성안내)
            self._play_auto_dispense_alarm()
            
            return True
            
        except Exception as e:
            # print(f"[ERROR] 복용 알람 트리거 실패: {e}")
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
                    # print(f"[WARN] 알람 {dose_index}: 타임스탬프가 문자열입니다. 숫자로 변환합니다.")
                    # 문자열 타임스탬프를 현재 시간으로 재설정
                    alarm_info["last_alarm_time"] = current_timestamp
                    last_alarm_time = current_timestamp
                
                time_diff = current_timestamp - last_alarm_time
                minutes_passed = time_diff // 60  # 초를 분으로 변환
                
                # print(f"[DEBUG] 알람 {dose_index}: 마지막 알람 {minutes_passed}분 전, 재알람 횟수 {alarm_info['reminder_count']}/{alarm_info['max_reminders']}")
                
                # 5분 경과 시 재알람
                if minutes_passed >= self.alarm_settings["reminder_interval"]:
                    if alarm_info["reminder_count"] < alarm_info["max_reminders"]:
                        # print(f"🔔 재알람 {alarm_info['reminder_count'] + 1}/{alarm_info['max_reminders']}: {alarm_info['meal_name']}")
                        self._trigger_reminder(dose_index)
                    else:
                        # 최대 재알람 횟수 초과 시 실패 처리
                        # print(f"❌ 최대 재알람 횟수 초과: {alarm_info['meal_name']} 복용 실패")
                        self._end_alarm(dose_index, reason="max_reminders_reached")
            
        except Exception as e:
            # print(f"[ERROR] 재알람 확인 실패: {e}")
            try:
                import sys
                if hasattr(sys, 'print_exception'):
                    sys.print_exception(e)
                else:
                    # print_exception이 없는 경우 상세 정보 출력
                    # print(f"[ERROR] 상세 정보: {type(e).__name__}: {e}")
                    pass
            except ImportError:
                # sys 모듈이 없는 경우 상세 정보 출력
                # print(f"[ERROR] 상세 정보: {type(e).__name__}: {e}")
                pass
    
    def _trigger_reminder(self, dose_index):
        """재알람 트리거 - 5분 간격으로 최대 5회"""
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
            
            # print(f"🔔 재알람 {alarm_info['reminder_count']}/{alarm_info['max_reminders']}: {alarm_info['meal_name']} ({alarm_info['dose_time']})")
            
            # 재알람 시에도 동일한 알림음 재생 (버저 3회 + LED 깜빡임 + 음성안내)
            self._play_auto_dispense_alarm()
            
            return True
            
        except Exception as e:
            # print(f"[ERROR] 재알람 트리거 실패: {e}")
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
            
            # print(f"✅ 복용 확인됨: {alarm_info['meal_name']} ({alarm_info['dose_time']})")
            self._stop_alarm_sound()
            self._hide_alarm_led()
            
            return True
            
        except Exception as e:
            # print(f"[ERROR] 복용 확인 실패: {e}")
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
            
            # print(f"💊 배출 확인됨: {alarm_info['meal_name']} ({alarm_info['dose_time']})")
            self._stop_alarm_sound()
            self._hide_alarm_led()
            
            return True
            
        except Exception as e:
            # print(f"[ERROR] 배출 확인 실패: {e}")
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
            
            # print(f"🔕 알람 종료: {alarm_info['meal_name']} ({reason})")
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
            # print(f"[ERROR] 알람 종료 실패: {e}")
            return False
    
    def _handle_dispense_failure(self, dose_index, alarm_info):
        """복용 실패 처리 - 심볼을 lv.SYMBOL.CLOSE로 변경"""
        try:
            meal_name = alarm_info.get("meal_name", f"일정 {dose_index + 1}")
            dose_time = alarm_info.get("dose_time", "")
            
            # print(f"❌ 복용 실패 처리: {meal_name} ({dose_time})")
            
            # 데이터 매니저에 실패 기록 저장 (지연 로딩)
            if hasattr(self, 'data_manager') and self.data_manager:
                try:
                    self.data_manager.log_dispense(dose_index, False)
                except Exception as e:
                    # print(f"[WARN] 실패 기록 저장 실패: {e}")
                    pass
            
            # 실패 기록 추가
            self.alarm_history.append({
                "timestamp": self._get_current_timestamp(),
                "dose_index": dose_index,
                "dose_time": dose_time,
                "meal_name": meal_name,
                "action": "dispense_failed"
            })
            
            # 복용 실패 시 심볼을 lv.SYMBOL.CLOSE로 변경 (화면 업데이트)
            self._update_failure_symbol(dose_index)
            
            # print(f"[OK] 복용 실패 기록 저장 및 심볼 변경: {meal_name}")
            
        except Exception as e:
            # print(f"[ERROR] 복용 실패 처리 실패: {e}")
            pass
    def _update_failure_symbol(self, dose_index):
        """복용 실패 시 심볼을 lv.SYMBOL.CLOSE로 변경"""
        try:
            # print(f"❌ 복용 실패 심볼 변경: 일정 {dose_index + 1}")
            
            # 메인 화면이 있으면 해당 일정의 상태를 "failed"로 업데이트
            if self.main_screen and hasattr(self.main_screen, 'dose_schedule'):
                if dose_index < len(self.main_screen.dose_schedule):
                    self.main_screen.dose_schedule[dose_index]["status"] = "failed"
                    # print(f"[OK] 복용 실패 상태 업데이트: 일정 {dose_index + 1} → failed")
                    
                    # 화면 업데이트 요청
                    if hasattr(self.main_screen, '_update_schedule_display'):
                        self.main_screen._update_schedule_display()
                        # print(f"[OK] 복용 실패 화면 업데이트 완료: 일정 {dose_index + 1}")
                else:
                    # print(f"[WARN] 잘못된 일정 인덱스: {dose_index}")
                    pass
            else:
                # print(f"[WARN] 메인 화면 참조 없음: 복용 실패 상태 업데이트 불가")
                pass
        except Exception as e:
            # print(f"[ERROR] 복용 실패 심볼 변경 실패: {e}")
            pass
    def _play_auto_dispense_alarm(self):
        """자동 배출 시 알림음 재생 (버저 3회 + LED 깜빡임 + 음성안내)"""
        try:
            if not self.alarm_settings["sound_enabled"]:
                return
            
            # print("🔊 자동 배출 알림음 시작 (버저 3회 + LED 깜빡임 + 음성안내)")
            
            # 1단계: 버저 3회 알림
            audio_system = self._get_audio_system()
            if audio_system:
                # print("🔔 1단계: 버저 3회 알림")
                for i in range(3):
                    # print(f"🔔 버저 알림 {i+1}/3")
                    audio_system.play_alarm_sound()
                    time.sleep_ms(500)  # 0.5초 간격
                
                # 버저 사용 후 즉시 참조 정리 및 가비지 컬렉션
                # print("[INFO] 버저 사용 후 참조 정리 및 메모리 정리")
                self._cleanup_audio_system()
                self._force_garbage_collection()
            
            # 2단계: LED 깜빡임
            # print("💡 2단계: LED 깜빡임")
            self._show_alarm_led()
            
            # LED 사용 후 참조 정리 및 가비지 컬렉션
            # print("[INFO] LED 사용 후 참조 정리 및 메모리 정리")
            self._cleanup_led_controller()
            self._force_garbage_collection()
            
            # 3단계: 음성안내 재생 (take_medicine.wav)
            # print("🔊 3단계: 음성안내 재생 (take_medicine.wav)")
            self._play_take_medicine_voice()
                
        except Exception as e:
            # print(f"[ERROR] 자동 배출 알림음 재생 실패: {e}")
            pass
        finally:
            # 최종 가비지 컬렉션
            self._force_garbage_collection()
            # print("[DEBUG] 자동 배출 알림음 재생 후 최종 가비지 컬렉션 완료")
    
    def _play_alarm_sound(self):
        """알람 소리 재생 (버저 → LED → 음성) - 메모리 최적화 순서"""
        try:
            if not self.alarm_settings["sound_enabled"]:
                return
            
            # print("🔊 알람 안내 시작 (버저 → LED → 음성)")
            
            # 1단계: 버저 소리 재생
            audio_system = self._get_audio_system()
            if audio_system:
                # print("🔔 1단계: 버저 알람 소리 재생")
                audio_system.play_alarm_sound()
                
                # 버저 사용 후 즉시 참조 정리 및 가비지 컬렉션
                # print("[INFO] 버저 사용 후 참조 정리 및 메모리 정리")
                self._cleanup_audio_system()
                self._force_garbage_collection()
            
            # 2단계: LED 표시
            # print("💡 2단계: LED 표시")
            self._show_alarm_led()
            
            # LED 사용 후 참조 정리 및 가비지 컬렉션
            # print("[INFO] LED 사용 후 참조 정리 및 메모리 정리")
            self._cleanup_led_controller()
            self._force_garbage_collection()
            
            # 3단계: 음성 재생 (메모리 정리 후)
            # print("🔊 3단계: 음성 재생 (메모리 정리 완료 후)")
            self._play_voice_after_cleanup()
                
        except Exception as e:
            # print(f"[ERROR] 알람 소리 재생 실패: {e}")
            pass
        finally:
            # 최종 가비지 컬렉션
            self._force_garbage_collection()
            # print("[DEBUG] 알람 소리 재생 후 최종 가비지 컬렉션 완료")
    
    def _stop_alarm_sound(self):
        """알람 소리 정지 - 지연 로딩 적용"""
        try:
            # 오디오 시스템 지연 로딩
            audio_system = self._get_audio_system()
            if audio_system:
                audio_system.stop_alarm_sound()
                # 사용 후 참조 정리
                self._cleanup_audio_system()
            else:
                # print("🔇 알람 소리 정지 (시뮬레이션)")
                pass
        except Exception as e:
            # print(f"[ERROR] 알람 소리 정지 실패: {e}")
            pass
    def _play_take_medicine_voice(self):
        """take_medicine.wav 음성 재생 (자동 배출 시)"""
        try:
            # print("🔊 take_medicine.wav 음성 재생 시작")
            
            # 오디오 시스템 새로 로딩 (메모리 정리 후)
            audio_system = self._get_audio_system()
            if audio_system:
                # print("🔊 take_medicine.wav 음성 파일 재생 (I2S 초기화 포함)")
                # blocking=True로 변경해서 음성이 완전히 재생되도록 함
                audio_system.play_voice("take_medicine.wav", blocking=True)
                
                # 음성 재생 후 참조 정리
                self._cleanup_audio_system()
            else:
                # print("🔊 복용 안내 음성 재생 (시뮬레이션)")
                pass
        except Exception as e:
            # print(f"[ERROR] take_medicine.wav 음성 재생 실패: {e}")
            pass
    def _play_voice_after_cleanup(self):
        """메모리 정리 후 음성 재생 (I2S 초기화 포함)"""
        try:
            # print("🔊 메모리 정리 완료 후 음성 재생 시작")
            
            # 오디오 시스템 새로 로딩 (메모리 정리 후)
            audio_system = self._get_audio_system()
            if audio_system:
                # print("🔊 take_medicine.wav 음성 파일 재생 (I2S 초기화 포함)")
                audio_system.play_voice("take_medicine.wav", blocking=False)
                
                # 음성 재생 후 참조 정리
                self._cleanup_audio_system()
            else:
                # print("🔊 복용 안내 음성 재생 (시뮬레이션)")
                pass
        except Exception as e:
            # print(f"[ERROR] 음성 재생 실패: {e}")
            pass
    def _force_garbage_collection(self):
        """강제 가비지 컬렉션 수행"""
        try:
            import gc
            import time
            
            # print("[INFO] 강제 가비지 컬렉션 시작")
            
            # 여러 번 가비지 컬렉션 수행
            for i in range(5):
                gc.collect()
                time.sleep_ms(50)
                # print(f"[INFO] GC {i+1}/5 완료")
            
            # print("[OK] 강제 가비지 컬렉션 완료")
            
        except Exception as e:
            # print(f"[ERROR] 가비지 컬렉션 실패: {e}")
            pass
    def _show_alarm_led(self):
        """알람 LED 표시 - 지연 로딩 적용"""
        try:
            if not self.alarm_settings["led_enabled"]:
                return
            
            # LED 컨트롤러 지연 로딩
            led_controller = self._get_led_controller()
            if led_controller:
                # 실제 LED 컨트롤러 사용
                led_controller.show_alarm_led()
                # print("💡 알람 LED 켜짐")
            else:
                # LED 컨트롤러가 없으면 시뮬레이션
                # print("💡 알람 LED 켜짐 (시뮬레이션)")
                pass
        except Exception as e:
            # print(f"[ERROR] 알람 LED 표시 실패: {e}")
            pass
        finally:
            # 가비지 컬렉션
            import gc
            gc.collect()
            # print("[DEBUG] 알람 LED 표시 후 가비지 컬렉션 완료")
    
    def _hide_alarm_led(self):
        """알람 LED 숨김 - 지연 로딩 적용"""
        try:
            if not self.alarm_settings["led_enabled"]:
                return
            
            # LED 컨트롤러 지연 로딩
            led_controller = self._get_led_controller()
            if led_controller:
                # 실제 LED 컨트롤러 사용
                led_controller.hide_alarm_led()
                # print("💡 알람 LED 꺼짐")
                # 사용 후 참조 정리
                self._cleanup_led_controller()
            else:
                # LED 컨트롤러가 없으면 시뮬레이션
                # print("💡 알람 LED 꺼짐 (시뮬레이션)")
                pass
        except Exception as e:
            # print(f"[ERROR] 알람 LED 숨김 실패: {e}")
            pass
    def get_active_alarms(self):
        """활성 알람 목록 반환"""
        return {k: v for k, v in self.active_alarms.items() if v["status"] == "active"}
    
    
    def get_alarm_summary(self):
        """알람 요약 정보 반환"""
        try:
            active_count = len(self.get_active_alarms())
            total_history = len(self.alarm_history)
            
            # 오늘 알람 통계 (지연 로딩)
            current_time = self._get_current_time()
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
            # print(f"[ERROR] 알람 요약 생성 실패: {e}")
            return None
    
    def get_alarm_history(self):
        """알람 기록 반환"""
        try:
            return self.alarm_history
        except Exception as e:
            # print(f"[ERROR] 알람 기록 조회 실패: {e}")
            return []
