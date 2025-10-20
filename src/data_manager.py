"""
데이터 관리 시스템
JSON 기반 설정 및 복용 기록 영구 저장
"""

# 지연 로딩을 위한 모듈 import 제거

# MicroPython에서 date 모듈 사용 (완전 지연 로딩)
def _get_date_module():
    """date 모듈 지연 로딩"""
    try:
        from datetime import date
        return date
    except ImportError:
        # MicroPython에서는 time 모듈로 날짜 처리 (지연 로딩)
        def get_today_str():
            """오늘 날짜 문자열 반환 (지연 로딩)"""
            try:
                import time
                t = time.localtime()
                return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d}"
            except ImportError:
                return "2025-01-01"
        
        class date:
            @staticmethod
            def today():
                """오늘 날짜 객체 반환 (지연 로딩)"""
                class DateObj:
                    def __init__(self):
                        self._date_str = None
                    
                    def strftime(self, fmt):  # pylint: disable=unused-argument
                        """날짜 포맷팅 (지연 로딩)"""
                        if self._date_str is None:
                            self._date_str = get_today_str()
                        return self._date_str
                return DateObj()
        return date

# 전역 date 객체 (지연 로딩)
date = None

class DataManager:
    """데이터 영속성 관리 클래스 (global_data 기능 포함)"""
    
    def __init__(self):
        """데이터 매니저 초기화"""
        self.data_dir = "/data"
        self.settings_file = "/data/settings.json"
        
        # 전역 데이터 저장소 (화면 전환 시에도 유지되는 데이터) - JSON 파일 기반
        self.global_data_file = "/data/global_data.json"
        
        # 지연 로딩을 위한 캐시 (global_data.py 기능 통합)
        self._dose_times = None
        self._selected_meals = None
        self._dose_count = None
        self._screen_data_backup = None
        self._auto_assigned_disks = None
        self._unused_disks = None
        self.medication_file = "/data/medication.json"
        self.dispense_log_file = "/data/dispense_log.json"
        
        # 메모리 최적화: 데이터 캐싱 완전 비활성화 (I2S 메모리 절약)
        self._medication_cache = None
        self._cache_timestamp = 0
        self._cache_timeout = 0  # 캐시 비활성화 (메모리 절약)
        self._cache_enabled = False  # 캐시 완전 비활성화
        
        # 지연 로딩을 위한 캐시
        self._wifi_manager = None
        self._settings_cache = None
        self._dispense_logs_cache = None
        self._last_file_check = {}
        self._today_date_str = None
        self._today_date_timestamp = 0
        self._modules_cache = {}  # 모듈 캐시
        
        # 데이터 디렉토리 생성
        self._ensure_data_directory()
        
        # print("[OK] DataManager 초기화 완료 (지연 로딩 적용 - 메모리 절약)")
    
    def _get_module(self, module_name):
        """모듈 지연 로딩"""
        if module_name not in self._modules_cache:
            try:
                if module_name == "json":
                    import json
                    self._modules_cache[module_name] = json
                elif module_name == "os":
                    import os
                    self._modules_cache[module_name] = os
                elif module_name == "time":
                    import time
                    self._modules_cache[module_name] = time
                else:
                    # print(f"[WARN] 알 수 없는 모듈: {module_name}")
                    return None
            except Exception as e:
                # print(f"[WARN] 모듈 로딩 실패: {module_name}, {e}")
                return None
        return self._modules_cache[module_name]
    
    def _get_date_module(self):
        """date 모듈 지연 로딩"""
        global date
        if date is None:
            date = _get_date_module()
        return date
    
    def clear_cache(self):
        """캐시 정리 (메모리 절약)"""
        try:
            self._medication_cache = None
            self._cache_timestamp = 0
            self._wifi_manager = None
            self._settings_cache = None
            self._dispense_logs_cache = None
            self._last_file_check.clear()
            self._today_date_str = None
            self._today_date_timestamp = 0
            self._modules_cache.clear()
            # 전역 date 모듈 캐시도 정리
            global date
            date = None
            # print("[INFO] DataManager 캐시 정리 완료 (지연 로딩 캐시 포함)")
        except Exception as e:
            # print(f"[WARN] 캐시 정리 실패: {e}")
            pass
    
    def _get_wifi_manager(self):
        """WiFi 매니저 지연 로딩"""
        if self._wifi_manager is None:
            try:
                from wifi_manager import get_wifi_manager
                self._wifi_manager = get_wifi_manager()
            except Exception as e:
                # print(f"[WARN] WiFi 매니저 로딩 실패: {e}")
                return None
        return self._wifi_manager
    
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
        time = self._get_module("time")
        if time:
            t = time.localtime()
            return (t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7])
        else:
            return (2025, 1, 1, 0, 0, 0, 0, 1)
    
    def _get_today_date_str(self):
        """오늘 날짜 문자열 지연 로딩 (캐싱 적용)"""
        try:
            time = self._get_module("time")
            if time and hasattr(time, 'ticks_ms'):
                current_time = time.ticks_ms()
                
                # 1분간 캐시 유지 (날짜는 하루에 한 번만 바뀌므로)
                if (self._today_date_str is not None and 
                    time.ticks_diff(current_time, self._today_date_timestamp) < 60000):
                    return self._today_date_str
        except AttributeError:
            # MicroPython에서 ticks_ms가 없는 경우
            pass
        
        # 캐시가 없거나 만료된 경우 새로 계산
        try:
            date_module = self._get_date_module()
            if date_module:
                self._today_date_str = date_module.today().strftime("%Y-%m-%d")
            else:
                # date 모듈 로딩 실패 시 직접 계산
                if time:
                    t = time.localtime()
                    self._today_date_str = f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d}"
                else:
                    self._today_date_str = "2025-01-01"
            
            try:
                if time and hasattr(time, 'ticks_ms'):
                    self._today_date_timestamp = time.ticks_ms()
                else:
                    self._today_date_timestamp = 0
            except AttributeError:
                self._today_date_timestamp = 0
            return self._today_date_str
        except Exception as e:
            # print(f"[WARN] 날짜 계산 실패: {e}")
            # fallback: 직접 계산
            if time:
                t = time.localtime()
                return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d}"
            else:
                return "2025-01-01"
    
    def _file_exists(self, file_path):
        """파일 존재 여부 확인 (캐싱 적용) - 지연 로딩"""
        try:
            time = self._get_module("time")
            if time and hasattr(time, 'ticks_ms'):
                current_time = time.ticks_ms()
                cache_key = file_path
                
                # 5초간 캐시 유지
                if (cache_key in self._last_file_check and 
                    time.ticks_diff(current_time, self._last_file_check[cache_key]["timestamp"]) < 5000):
                    return self._last_file_check[cache_key]["exists"]
                
                try:
                    with open(file_path, 'r'):
                        pass
                    exists = True
                except OSError:
                    exists = False
                
                self._last_file_check[cache_key] = {
                    "exists": exists,
                    "timestamp": current_time
                }
                
                return exists
        except AttributeError:
            # MicroPython에서 ticks_ms가 없는 경우 직접 파일 확인
            try:
                with open(file_path, 'r'):
                    pass
                return True
            except OSError:
                return False
    
    def _ensure_data_directory(self):
        """데이터 디렉토리 존재 확인 및 생성 (지연 로딩)"""
        try:
            os = self._get_module("os")
            if os is None:
                # print("[ERROR] os 모듈 로딩 실패")
                return
            
            # MicroPython에서는 os.path.exists가 없으므로 try-except로 확인
            try:
                os.listdir(self.data_dir)
                # print(f"[OK] 데이터 디렉토리 존재: {self.data_dir}")
            except OSError:
                # 디렉토리가 없으면 생성
                os.mkdir(self.data_dir)
                # print(f"[OK] 데이터 디렉토리 생성: {self.data_dir}")
        except Exception as e:
            # print(f"[ERROR] 데이터 디렉토리 생성 실패: {e}")
            pass
    # ===== 설정 관리 =====
    
    def save_settings(self, settings):
        """설정 저장 (캐시 업데이트) - 지연 로딩"""
        try:
            json = self._get_module("json")
            if json is None:
                # print("[ERROR] json 모듈 로딩 실패")
                return False
                pass
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
            
            # 캐시 업데이트
            self._settings_cache = settings
            
            # print(f"[OK] 설정 저장 완료: {self.settings_file}")
            return True
        except Exception as e:
            # print(f"[ERROR] 설정 저장 실패: {e}")
            return False
    
    def load_settings(self):
        """설정 로드 (지연 로딩 적용)"""
        # 캐시된 설정이 있으면 캐시 반환 (파일 존재 여부는 별도 확인)
        if self._settings_cache is not None:
            return self._settings_cache
        
        try:
            json = self._get_module("json")
            if json is None:
                # print("[ERROR] json 모듈 로딩 실패")
                default_settings = self._get_default_settings()
                self._settings_cache = default_settings
                return default_settings
            
            if self._file_exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                self._settings_cache = settings
                # print(f"[OK] 설정 로드 완료: {self.settings_file}")
                return settings
            else:
                # print("[INFO] 설정 파일 없음, 기본값 반환")
                default_settings = self._get_default_settings()
                self._settings_cache = default_settings
                return default_settings
        except Exception as e:
            # print(f"[ERROR] 설정 로드 실패: {e}")
            default_settings = self._get_default_settings()
            self._settings_cache = default_settings
            return default_settings
    
    def _get_default_settings(self):
        """기본 설정 반환"""
        return {
            "wifi": {
                "ssid": "",
                "password": "",
                "connected": False
            },
            "dose_schedule": [
                {"time": "08:00", "meal_name": "아침", "meal_key": "breakfast", "enabled": True},
                {"time": "12:00", "meal_name": "점심", "meal_key": "lunch", "enabled": True},
                {"time": "18:00", "meal_name": "저녁", "meal_key": "dinner", "enabled": True}
            ],
            "dose_count": 3,
            "dose_days": 30,
            "alarm_settings": {
                "enabled": True,
                "reminder_interval": 5,  # 분
                "max_reminders": 3
            },
            "system_settings": {
                "auto_dispense": True,
                "sound_enabled": True,
                "display_brightness": 100
            }
        }
    
    # ===== 약물 관리 =====
    
    def save_medication_data(self, medication_data):
        """약물 데이터 저장 (캐시 업데이트) - 지연 로딩"""
        try:
            # print(f"[DEBUG] save_medication_data 시작: {self.medication_file}")
            # print(f"[DEBUG] 저장할 데이터: {medication_data}")
            
            json = self._get_module("json")
            time = self._get_module("time")
            
            if json is None:
                # print("[ERROR] json 모듈 로딩 실패")
                return False
                pass
            
            # print(f"[DEBUG] JSON 모듈 로드 성공, 파일 쓰기 시작...")
            
            with open(self.medication_file, 'w') as f:
                json.dump(medication_data, f)
            
            # print(f"[DEBUG] 파일 쓰기 완료, 캐시 업데이트 시작...")
            
            # 캐시 업데이트 (무효화 대신 직접 업데이트)
            self._medication_cache = medication_data
            try:
                if time and hasattr(time, 'ticks_ms'):
                    self._cache_timestamp = time.ticks_ms()
                else:
                    self._cache_timestamp = 0
            except AttributeError:
                self._cache_timestamp = 0
            
            # print(f"[OK] 약물 데이터 저장 완료: {self.medication_file}")
            return True
        except Exception as e:
            # print(f"[ERROR] 약물 데이터 저장 실패: {e}")
            import sys
            sys.print_exception(e)
            return False
    
    def load_medication_data(self):
        """약물 데이터 로드 (지연 로딩 및 캐싱 적용)"""
        try:
            time = self._get_module("time")
            try:
                if time and hasattr(time, 'ticks_ms'):
                    current_time = time.ticks_ms()
                    
                    # 캐시가 유효한지 확인
                    if (self._medication_cache is not None and 
                        time.ticks_diff(current_time, self._cache_timestamp) < self._cache_timeout):
                        return self._medication_cache
            except AttributeError:
                # MicroPython에서 ticks_ms가 없는 경우 캐시 무시
                pass
            
            # 파일 존재 여부 먼저 확인 (지연 로딩)
            if not self._file_exists(self.medication_file):
                # print("[INFO] 약물 데이터 파일 없음, 기본값 반환")
                default_data = self._get_default_medication_data()
                self._medication_cache = default_data
                try:
                    if time and hasattr(time, 'ticks_ms'):
                        self._cache_timestamp = time.ticks_ms()
                    else:
                        self._cache_timestamp = 0
                except AttributeError:
                    self._cache_timestamp = 0
                return default_data
            
            # 파일에서 로드 (JSON 파싱 지연 로딩)
            json = self._get_module("json")
            if json is None:
                # print("[ERROR] json 모듈 로딩 실패")
                default_data = self._get_default_medication_data()
                self._medication_cache = default_data
                return default_data
            
            with open(self.medication_file, 'r') as f:
                medication_data = json.load(f)
            
            # 디버그: 로드된 데이터 확인
            # print(f"[DEBUG] 로드된 약물 데이터: {medication_data}")
            
            # 데이터 구조 검증 및 수정
            medication_data = self._validate_and_fix_medication_data(medication_data)
            
            # 캐시 업데이트 (캐시가 활성화된 경우에만)
            if self._cache_enabled:
                self._medication_cache = medication_data
                try:
                    if time and hasattr(time, 'ticks_ms'):
                        self._cache_timestamp = time.ticks_ms()
                    else:
                        self._cache_timestamp = 0
                except AttributeError:
                    self._cache_timestamp = 0
            else:
                # 캐시 비활성화 시 즉시 정리
                self._medication_cache = None
            
            # print(f"[OK] 약물 데이터 로드 완료: {self.medication_file}")
            return medication_data
        except Exception as e:
            # print(f"[ERROR] 약물 데이터 로드 실패: {e}")
            default_data = self._get_default_medication_data()
            self._medication_cache = default_data
            try:
                if time and hasattr(time, 'ticks_ms'):
                    self._cache_timestamp = time.ticks_ms()
                else:
                    self._cache_timestamp = 0
            except AttributeError:
                self._cache_timestamp = 0
            return default_data
    
    def _validate_and_fix_medication_data(self, medication_data):
        """약물 데이터 구조 검증 및 수정"""
        try:
            # print(f"[DEBUG] 데이터 구조 검증 시작: {medication_data}")
            
            # 잘못된 disk_counts 필드가 있으면 제거
            if "disk_counts" in medication_data:
                # print(f"[WARN] 잘못된 disk_counts 필드 발견, 제거: {medication_data['disk_counts']}")
                del medication_data["disk_counts"]
            
            # disks 필드가 없으면 기본 데이터로 교체
            if "disks" not in medication_data:
                # print("[WARN] disks 필드 없음, 기본 데이터로 교체")
                default_data = self._get_default_medication_data()
                medication_data["disks"] = default_data["disks"]
            
            # 각 디스크 데이터 검증 및 수정
            for disk_num in ["1", "2", "3"]:
                if disk_num not in medication_data["disks"]:
                    # print(f"[WARN] 디스크 {disk_num} 데이터 없음, 기본 데이터로 교체")
                    default_data = self._get_default_medication_data()
                    medication_data["disks"][disk_num] = default_data["disks"][disk_num].copy()
                else:
                    disk_data = medication_data["disks"][disk_num]
                    # 필수 필드 검증
                    required_fields = ["name", "total_capacity", "current_count", "last_refill", "medication_type"]
                    for field in required_fields:
                        if field not in disk_data:
                            # print(f"[WARN] 디스크 {disk_num} {field} 필드 없음, 기본값 설정")
                            if field == "name":
                                disk_data[field] = f"{'아침' if disk_num == '1' else '점심' if disk_num == '2' else '저녁'}약"
                            elif field == "total_capacity":
                                disk_data[field] = 15
                            elif field == "current_count":
                                disk_data[field] = 0
                            elif field == "last_refill":
                                disk_data[field] = None
                            elif field == "medication_type":
                                disk_data[field] = "morning" if disk_num == "1" else "lunch" if disk_num == "2" else "dinner"
            
            # refill_history 필드 검증
            if "refill_history" not in medication_data:
                medication_data["refill_history"] = []
            
            # low_stock_threshold 필드 검증
            if "low_stock_threshold" not in medication_data:
                medication_data["low_stock_threshold"] = 3
            
            # print(f"[DEBUG] 데이터 구조 검증 완료: {medication_data}")
            return medication_data
            
        except Exception as e:
            # print(f"[ERROR] 데이터 구조 검증 실패: {e}")
            return self._get_default_medication_data()
    
    def _get_default_medication_data(self):
        """기본 약물 데이터 반환"""
        return {
            "disks": {
                "1": {
                    "name": "아침약",
                    "total_capacity": 15,
                    "current_count": 0,
                    "last_refill": None,
                    "medication_type": "morning"
                },
                "2": {
                    "name": "점심약", 
                    "total_capacity": 15,
                    "current_count": 0,
                    "last_refill": None,
                    "medication_type": "lunch"
                },
                "3": {
                    "name": "저녁약",
                    "total_capacity": 15,
                    "current_count": 0,
                    "last_refill": None,
                    "medication_type": "dinner"
                }
            },
            "refill_history": [],
            "low_stock_threshold": 3
        }
    
    # ===== 배출 기록 관리 =====
    
    def log_dispense(self, dose_index, success, timestamp=None):
        """배출 기록 저장"""
        try:
            if timestamp is None:
                # 지연 로딩된 시간 사용
                current_time = self._get_current_time()
                timestamp = f"{current_time[0]:04d}-{current_time[1]:02d}-{current_time[2]:02d}T{current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"
            
            # 기존 로그 로드
            logs = self.load_dispense_logs()
            
            # 새 로그 추가 (지연 로딩된 시간 사용)
            current_time = self._get_current_time()
            new_log = {
                "timestamp": timestamp,
                "dose_index": dose_index,
                "success": success,
                "date": f"{current_time[0]:04d}-{current_time[1]:02d}-{current_time[2]:02d}",
                "time": f"{current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"
            }
            
            logs.append(new_log)
            
            # 최근 100개 로그만 유지
            if len(logs) > 100:
                logs = logs[-100:]
            
            # 파일에 저장 (MicroPython에서는 encoding 매개변수 지원 안함)
            json = self._get_module("json")
            if json is None:
                # print("[ERROR] json 모듈 로딩 실패")
                return False
                pass
            
            with open(self.dispense_log_file, 'w') as f:
                json.dump(logs, f)
            
            # 캐시 업데이트
            self._dispense_logs_cache = logs
            
            # print(f"[OK] 배출 기록 저장: 일정 {dose_index + 1}, 성공: {success}")
            return True
            
        except Exception as e:
            # print(f"[ERROR] 배출 기록 저장 실패: {e}")
            return False
    
    def load_dispense_logs(self):
        """배출 기록 로드 (지연 로딩 적용)"""
        # 캐시된 로그가 있으면 캐시 반환
        if self._dispense_logs_cache is not None:
            return self._dispense_logs_cache
        
        try:
            json = self._get_module("json")
            if json is None:
                # print("[ERROR] json 모듈 로딩 실패")
                self._dispense_logs_cache = []
                return []
            
            if self._file_exists(self.dispense_log_file):
                with open(self.dispense_log_file, 'r') as f:
                    logs = json.load(f)
                self._dispense_logs_cache = logs
                return logs
            else:
                self._dispense_logs_cache = []
                return []
        except Exception as e:
            # print(f"[ERROR] 배출 기록 로드 실패: {e}")
            self._dispense_logs_cache = []
            return []
    
    def get_today_dispense_logs(self):
        """오늘 배출 기록만 반환 (지연 로딩 적용)"""
        try:
            logs = self.load_dispense_logs()
            today = self._get_today_date_str()  # 지연 로딩된 날짜 사용
            today_logs = [log for log in logs if log.get("date") == today]
            return today_logs
        except Exception as e:
            # print(f"[ERROR] 오늘 배출 기록 로드 실패: {e}")
            return []
    
    def was_dispensed_today(self, dose_index, dose_time=None):
        """오늘 해당 일정이 배출되었는지 확인 (시간별 중복 체크)"""
        try:
            today_logs = self.get_today_dispense_logs()
            
            # 시간이 지정된 경우: 같은 시간에 배출된 기록이 있는지 확인
            if dose_time:
                for log in today_logs:
                    if (log.get("dose_index") == dose_index and 
                        log.get("success") and 
                        log.get("time") == dose_time):
                        return True
                return False
            
            # 시간이 지정되지 않은 경우: 해당 일정 인덱스에 대한 모든 배출 기록 확인
            for log in today_logs:
                if log.get("dose_index") == dose_index and log.get("success"):
                    return True
            return False
            
        except Exception as e:
            # print(f"[ERROR] 오늘 배출 확인 실패: {e}")
            return False
    
    # ===== 약물 수량 관리 =====
    
    def update_disk_count(self, disk_num, new_count):
        """디스크 약물 수량 업데이트"""
        try:
            # print(f"[DEBUG] update_disk_count 시작: 디스크 {disk_num}, 수량 {new_count}")
            
            # 캐시된 데이터가 있으면 사용, 없으면 로드
            if self._medication_cache is not None:
                # print(f"[DEBUG] 캐시된 데이터 사용")
                medication_data = self._medication_cache.copy()
            else:
                # print(f"[DEBUG] 파일에서 데이터 로드")
                medication_data = self.load_medication_data()
            
            disk_key = str(disk_num)
            
            # print(f"[DEBUG] 로드된 medication_data: {medication_data}")
            
            # 디스크 데이터가 없으면 기본 데이터 생성
            if disk_key not in medication_data["disks"]:
                # print(f"[INFO] 디스크 {disk_num} 데이터 없음, 기본 데이터 생성")
                default_data = self._get_default_medication_data()
                medication_data["disks"][disk_key] = default_data["disks"][disk_key].copy()
            
            # 현재 시간 가져오기 (지연 로딩)
            current_time = self._get_current_time()
            
            # print(f"[DEBUG] 업데이트 전 디스크 {disk_num} 수량: {medication_data['disks'][disk_key]['current_count']}")
            
            medication_data["disks"][disk_key]["current_count"] = new_count
            medication_data["disks"][disk_key]["last_refill"] = f"{current_time[0]:04d}-{current_time[1]:02d}-{current_time[2]:02d}T{current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"
            
            # print(f"[DEBUG] 업데이트 후 디스크 {disk_num} 수량: {medication_data['disks'][disk_key]['current_count']}")
            
            # 리필 기록 추가
            refill_record = {
                "disk": disk_num,
                "timestamp": f"{current_time[0]:04d}-{current_time[1]:02d}-{current_time[2]:02d}T{current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}",
                "count": new_count
            }
            medication_data["refill_history"].append(refill_record)
            
            # 최근 50개 리필 기록만 유지
            if len(medication_data["refill_history"]) > 50:
                medication_data["refill_history"] = medication_data["refill_history"][-50:]
            
            # print(f"[DEBUG] save_medication_data 호출 전: {medication_data}")
            save_result = self.save_medication_data(medication_data)
            # print(f"[DEBUG] save_medication_data 결과: {save_result}")
            
            return save_result
                
        except Exception as e:
            # print(f"[ERROR] 디스크 수량 업데이트 실패: {e}")
            import sys
            sys.print_exception(e)
            return False
    
    def get_disk_count(self, disk_num):
        """디스크 약물 수량 조회 (최적화)"""
        try:
            # print(f"[DEBUG] get_disk_count 시작: 디스크 {disk_num}")
            
            medication_data = self.load_medication_data()
            disk_key = str(disk_num)
            
            # print(f"[DEBUG] 로드된 medication_data: {medication_data}")
            # print(f"[DEBUG] disk_key: {disk_key}")
            # print(f"[DEBUG] medication_data['disks']: {medication_data.get('disks', {})}")
            
            if disk_key in medication_data["disks"]:
                current_count = medication_data["disks"][disk_key]["current_count"]
                # print(f"[DEBUG] 디스크 {disk_num} 수량: {current_count}")
                return current_count
            else:
                # print(f"[DEBUG] 디스크 {disk_num} 데이터 없음")
                return 0
        except Exception as e:
            # print(f"[ERROR] get_disk_count({disk_num}) 실패: {e}")
            import sys
            sys.print_exception(e)
            return 0
    
    def is_disk_low_stock(self, disk_num):
        """디스크 약물 부족 여부 확인"""
        try:
            medication_data = self.load_medication_data()
            disk_key = str(disk_num)
            threshold = medication_data.get("low_stock_threshold", 3)
            
            if disk_key in medication_data["disks"]:
                current_count = medication_data["disks"][disk_key]["current_count"]
                return current_count <= threshold
            else:
                return True
        except Exception as e:
            # print(f"[ERROR] 디스크 부족 확인 실패: {e}")
            return True
    
    # ===== 유틸리티 함수 =====
    
    def clear_all_data(self):
        """모든 데이터 삭제 (초기화)"""
        try:
            files_to_clear = [
                self.settings_file,
                self.medication_file,
                self.dispense_log_file
            ]
            
            os = self._get_module("os")
            if os is None:
                # print("[ERROR] os 모듈 로딩 실패")
                return False
            
            for file_path in files_to_clear:
                try:
                    os.remove(file_path)
                    # print(f"[OK] 파일 삭제: {file_path}")
                except OSError:
                    # 파일이 없으면 무시
                    pass
            
            # print("[OK] 모든 데이터 삭제 완료")
            return True
        except Exception as e:
            # print(f"[ERROR] 데이터 삭제 실패: {e}")
            return False
    
    def get_data_summary(self):
        """데이터 요약 정보 반환"""
        try:
            settings = self.load_settings()
            medication_data = self.load_medication_data()
            logs = self.load_dispense_logs()
            
            summary = {
                "settings_loaded": settings is not None,
                "medication_data_loaded": medication_data is not None,
                "total_dispense_logs": len(logs),
                "today_dispense_logs": len(self.get_today_dispense_logs()),
                "disk_counts": {
                    "1": self.get_disk_count(1),
                    "2": self.get_disk_count(2),
                    "3": self.get_disk_count(3)
                },
                "low_stock_disks": []
            }
            
            # 부족한 디스크 확인
            for disk_num in [1, 2, 3]:
                if self.is_disk_low_stock(disk_num):
                    summary["low_stock_disks"].append(disk_num)
            
            return summary
        except Exception as e:
            # print(f"[ERROR] 데이터 요약 생성 실패: {e}")
            return None
        
    def get_dose_times(self):
        """복용 시간 정보 조회"""
        try:
            settings = self.load_settings()
            if settings and "dose_times" in settings:
                return settings["dose_times"]
            else:
                return []
        except Exception:
            # print("[ERROR] 복용 시간 조회 실패")
            return []
    
    def save_dose_times(self, dose_times):
        """복용 시간 정보 저장"""
        try:
            settings = self.load_settings()
            if not settings:
                settings = {}
            
            settings["dose_times"] = dose_times
            return self.save_settings(settings)
        except Exception as e:
            # print(f"[ERROR] 복용 시간 저장 실패: {e}")
            return False
    
    def get_all_disk_counts(self):
        """모든 디스크의 알약 개수 조회"""
        try:
            medication_data = self.load_medication_data()
            if medication_data and "disk_counts" in medication_data:
                return medication_data["disk_counts"]
            return {}
        except Exception as e:
            # print(f"[ERROR] 모든 디스크 알약 개수 조회 실패: {e}")
            return {}
    
    # 전역 데이터 관리 메서드들 (global_data.py 기능 통합 - JSON 파일 기반)
    
    def _load_global_data_from_file(self):
        """전역 데이터 JSON 파일에서 로드 (지연 로딩)"""
        try:
            import gc
            gc.collect()
            
            # json 모듈 지연 로딩
            import json
            
            with open(self.global_data_file, 'r') as f:
                data = json.load(f)
            
            self._dose_times = data.get('dose_times', [])
            self._selected_meals = data.get('selected_meals', [])
            self._dose_count = data.get('dose_count', 1)
            self._auto_assigned_disks = data.get('auto_assigned_disks', [])
            self._unused_disks = data.get('unused_disks', [])
            self._screen_data_backup = data.get('screen_data_backup', {
                'wifi_scan': {},
                'meal_time': {},
                'dose_time': {},
                'disk_selection': {},
                'pill_loading': {},
                'main': {}
            })
            
            # print("[DEBUG] 전역 데이터 JSON 파일 로드 완료")
            return True
            
        except Exception as e:
            # print(f"[WARN] 전역 데이터 JSON 파일 로드 실패: {e}")
            # 기본값 설정
            self._dose_times = []
            self._selected_meals = []
            self._dose_count = 1
            self._screen_data_backup = {
                'wifi_scan': {},
                'meal_time': {},
                'dose_time': {},
                'disk_selection': {},
                'pill_loading': {},
                'main': {}
            }
            return False
    
    def _save_global_data_to_file(self):
        """전역 데이터 JSON 파일에 저장"""
        try:
            import gc
            gc.collect()
            
            # json 모듈 지연 로딩
            import json
            
            data = {
                'dose_times': self._dose_times or [],
                'selected_meals': self._selected_meals or [],
                'dose_count': self._dose_count or 1,
                'auto_assigned_disks': self._auto_assigned_disks or [],
                'unused_disks': self._unused_disks or [],
                'screen_data_backup': self._screen_data_backup or {}
            }
            
            with open(self.global_data_file, 'w') as f:
                json.dump(data, f)
            
            # print("[DEBUG] 전역 데이터 JSON 파일 저장 완료")
            return True
            
        except Exception as e:
            # print(f"[ERROR] 전역 데이터 JSON 파일 저장 실패: {e}")
            return False
    
    
    def add_selected_disks_to_current_data(self, selected_disks):
        """현재 저장된 데이터에 selected_disks 정보 추가 (테스트용)"""
        try:
            # 지연 로딩으로 데이터 로드
            if self._dose_times is None:
                self._load_global_data_from_file()
            
            if self._dose_times and len(self._dose_times) > 0:
                # 첫 번째 복용 시간에 selected_disks 추가
                if isinstance(self._dose_times[0], dict):
                    self._dose_times[0]['selected_disks'] = selected_disks
                    self._dose_times[0]['disk_count'] = len(selected_disks)
                    # print(f"[DEBUG] 테스트용 selected_disks 추가: {selected_disks}")
                    
                    # JSON 파일에 저장
                    self._save_global_data_to_file()
                    
                    # print(f"[DEBUG] 수정된 데이터: {self._dose_times[0]}")
                    return True
            
            # print("[WARN] 수정할 데이터가 없음")
            return False
            
        except Exception as e:
            # print(f"[ERROR] selected_disks 추가 실패: {e}")
            return False

    def save_auto_assigned_disks(self, assigned_disks, unused_disks):
        """자동 할당된 디스크 정보 저장"""
        try:
            # 지연 로딩으로 데이터 로드
            if self._dose_times is None:
                self._load_global_data_from_file()
            
            # 자동 할당된 디스크 정보 저장
            self._auto_assigned_disks = assigned_disks.copy() if assigned_disks else []
            self._unused_disks = unused_disks.copy() if unused_disks else []
            
            # print(f"[INFO] 자동 할당된 디스크 정보 저장:")
            # print(f"  - 사용할 디스크: {len(self._auto_assigned_disks)}개")
            for disk_info in self._auto_assigned_disks:
                # print(f"    * 디스크 {disk_info['disk_number']}: {disk_info['meal_name']} ({disk_info['time']})")
            # print(f"  - 사용하지 않는 디스크: {len(self._unused_disks)}개")
                pass
            for disk_num in self._unused_disks:
                # print(f"    * 디스크 {disk_num}: 사용 안함")
                pass
            # JSON 파일에 저장
            self._save_global_data_to_file()
            
            # 참조 정리
            import gc
            gc.collect()
            
        except Exception as e:
            # print(f"[ERROR] 자동 할당된 디스크 정보 저장 실패: {e}")
            pass
        
    def get_auto_assigned_disks(self):
        """자동 할당된 디스크 정보 반환"""
        try:
            # 지연 로딩으로 데이터 로드
            if self._auto_assigned_disks is None:
                self._load_global_data_from_file()
            
            return self._auto_assigned_disks.copy() if self._auto_assigned_disks else []
            
        except Exception as e:
            # print(f"[ERROR] 자동 할당된 디스크 정보 로드 실패: {e}")
            return []

    def get_unused_disks(self):
        """사용하지 않는 디스크 목록 반환"""
        try:
            # 지연 로딩으로 데이터 로드
            if self._unused_disks is None:
                self._load_global_data_from_file()
            
            return self._unused_disks.copy() if self._unused_disks else []
            
        except Exception as e:
            # print(f"[ERROR] 사용하지 않는 디스크 정보 로드 실패: {e}")
            return []
    
    
    
    def save_selected_meals(self, selected_meals):
        """선택된 식사 시간 정보 저장 (JSON 파일 기반)"""
        try:
            # 지연 로딩으로 데이터 로드
            if self._selected_meals is None:
                self._load_global_data_from_file()
            
            self._selected_meals = selected_meals.copy() if selected_meals else []
            # print(f"[INFO] 전역 데이터에 선택된 식사 시간 저장: {len(self._selected_meals)}개")
            
            # JSON 파일에 저장
            self._save_global_data_to_file()
            
            # 참조 정리
            import gc
            gc.collect()
            
        except Exception as e:
            # print(f"[ERROR] 선택된 식사 시간 저장 실패: {e}")
            pass
        
    def get_selected_meals(self):
        """선택된 식사 시간 정보 반환 (지연 로딩)"""
        try:
            # 지연 로딩으로 데이터 로드
            if self._selected_meals is None:
                self._load_global_data_from_file()
            
            return self._selected_meals.copy() if self._selected_meals else []
            
        except Exception as e:
            # print(f"[ERROR] 선택된 식사 시간 조회 실패: {e}")
            return []
    
    def save_dose_count(self, dose_count):
        """복용 횟수 저장 (JSON 파일 기반)"""
        try:
            # 지연 로딩으로 데이터 로드
            if self._dose_count is None:
                self._load_global_data_from_file()
            
            self._dose_count = dose_count
            # print(f"[INFO] 전역 데이터에 복용 횟수 저장: {dose_count}")
            
            # JSON 파일에 저장
            self._save_global_data_to_file()
            
            # 참조 정리
            import gc
            gc.collect()
            
        except Exception as e:
            # print(f"[ERROR] 복용 횟수 저장 실패: {e}")
            pass
    
    def get_dose_count(self):
        """복용 횟수 반환 (지연 로딩)"""
        try:
            # 지연 로딩으로 데이터 로드
            if self._dose_count is None:
                self._load_global_data_from_file()
            
            return self._dose_count or 1
            
        except Exception as e:
            # print(f"[ERROR] 복용 횟수 조회 실패: {e}")
            return 1
    
    def clear_all_global_data(self):
        """모든 전역 데이터 초기화 (JSON 파일 기반)"""
        try:
            self._dose_times = []
            self._selected_meals = []
            self._dose_count = 1
            self._screen_data_backup = {
                'wifi_scan': {},
                'meal_time': {},
                'dose_time': {},
                'disk_selection': {},
                'pill_loading': {},
                'main': {}
            }
            
            # JSON 파일에 저장
            self._save_global_data_to_file()
            
            # 참조 정리
            import gc
            gc.collect()
            
            # print("[INFO] 전역 데이터 초기화 완료")
            
        except Exception as e:
            # print(f"[ERROR] 전역 데이터 초기화 실패: {e}")
            pass
    
    # 화면별 데이터 백업 메서드들 (global_data.py 기능 통합 - JSON 파일 기반)
    
    def backup_screen_data(self, screen_name, data):
        """화면 데이터 백업 (JSON 파일 기반)"""
        try:
            # 지연 로딩으로 데이터 로드
            if self._screen_data_backup is None:
                self._load_global_data_from_file()
            
            if screen_name in self._screen_data_backup:
                self._screen_data_backup[screen_name] = data.copy() if isinstance(data, dict) else data
                # print(f"[INFO] {screen_name} 화면 데이터 백업 완료")
                
                # JSON 파일에 저장
                self._save_global_data_to_file()
                
                # 참조 정리
                import gc
                gc.collect()
            else:
                # print(f"[WARN] 지원하지 않는 화면: {screen_name}")
                pass
                
        except Exception as e:
            # print(f"[ERROR] {screen_name} 화면 데이터 백업 실패: {e}")
            pass
    
    def restore_screen_data(self, screen_name):
        """화면 데이터 복원 (지연 로딩)"""
        try:
            # 지연 로딩으로 데이터 로드
            if self._screen_data_backup is None:
                self._load_global_data_from_file()
            
            if screen_name in self._screen_data_backup:
                data = self._screen_data_backup[screen_name]
                # print(f"[INFO] {screen_name} 화면 데이터 복원 완료")
                return data.copy() if isinstance(data, dict) else data
            else:
                # print(f"[WARN] 지원하지 않는 화면: {screen_name}")
                return {}
                
        except Exception as e:
            # print(f"[ERROR] {screen_name} 화면 데이터 복원 실패: {e}")
            return {}
    
    def clear_screen_data(self, screen_name):
        """특정 화면 데이터 삭제 (JSON 파일 기반)"""
        try:
            # 지연 로딩으로 데이터 로드
            if self._screen_data_backup is None:
                self._load_global_data_from_file()
            
            if screen_name in self._screen_data_backup:
                self._screen_data_backup[screen_name] = {}
                # print(f"[INFO] {screen_name} 화면 데이터 삭제 완료")
                
                # JSON 파일에 저장
                self._save_global_data_to_file()
                
                # 참조 정리
                import gc
                gc.collect()
            else:
                # print(f"[WARN] 지원하지 않는 화면: {screen_name}")
                pass
                
        except Exception as e:
            # print(f"[ERROR] {screen_name} 화면 데이터 삭제 실패: {e}")
            pass
    
    def clear_all_screen_data(self):
        """모든 화면 데이터 삭제 (JSON 파일 기반)"""
        try:
            # 지연 로딩으로 데이터 로드
            if self._screen_data_backup is None:
                self._load_global_data_from_file()
            
            for screen_name in self._screen_data_backup:
                self._screen_data_backup[screen_name] = {}
            
            # print("[INFO] 모든 화면 데이터 삭제 완료")
            
            # JSON 파일에 저장
            self._save_global_data_to_file()
            
            # 참조 정리
            import gc
            gc.collect()
            
        except Exception as e:
            # print(f"[ERROR] 모든 화면 데이터 삭제 실패: {e}")
            pass