"""
데이터 관리 시스템
JSON 기반 설정 및 복용 기록 영구 저장
"""

import json
import os
import time
from wifi_manager import get_wifi_manager

# MicroPython에서 date 모듈 사용
try:
    from datetime import date
except ImportError:
    # MicroPython에서는 time 모듈로 날짜 처리
    def get_today_str():
        t = time.localtime()
        return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d}"
    
    class date:
        @staticmethod
        def today():
            class DateObj:
                def strftime(self, fmt):
                    return get_today_str()
            return DateObj()

class DataManager:
    """데이터 영속성 관리 클래스"""
    
    def __init__(self):
        """데이터 매니저 초기화"""
        self.data_dir = "/data"
        self.settings_file = "/data/settings.json"
        self.medication_file = "/data/medication.json"
        self.dispense_log_file = "/data/dispense_log.json"
        
        # 데이터 디렉토리 생성
        self._ensure_data_directory()
        
        print("[OK] DataManager 초기화 완료")
    
    def _ensure_data_directory(self):
        """데이터 디렉토리 존재 확인 및 생성"""
        try:
            # MicroPython에서는 os.path.exists가 없으므로 try-except로 확인
            try:
                os.listdir(self.data_dir)
                print(f"[OK] 데이터 디렉토리 존재: {self.data_dir}")
            except OSError:
                # 디렉토리가 없으면 생성
                os.mkdir(self.data_dir)
                print(f"[OK] 데이터 디렉토리 생성: {self.data_dir}")
        except Exception as e:
            print(f"[ERROR] 데이터 디렉토리 생성 실패: {e}")
    
    # ===== 설정 관리 =====
    
    def save_settings(self, settings):
        """설정 저장"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
            print(f"[OK] 설정 저장 완료: {self.settings_file}")
            return True
        except Exception as e:
            print(f"[ERROR] 설정 저장 실패: {e}")
            return False
    
    def load_settings(self):
        """설정 로드"""
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
            print(f"[OK] 설정 로드 완료: {self.settings_file}")
            return settings
        except OSError:
            print(f"[INFO] 설정 파일 없음, 기본값 반환")
            return self._get_default_settings()
        except Exception as e:
            print(f"[ERROR] 설정 로드 실패: {e}")
            return self._get_default_settings()
    
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
        """약물 데이터 저장"""
        try:
            with open(self.medication_file, 'w') as f:
                json.dump(medication_data, f)
            print(f"[OK] 약물 데이터 저장 완료: {self.medication_file}")
            return True
        except Exception as e:
            print(f"[ERROR] 약물 데이터 저장 실패: {e}")
            return False
    
    def load_medication_data(self):
        """약물 데이터 로드"""
        try:
            with open(self.medication_file, 'r') as f:
                medication_data = json.load(f)
            print(f"[OK] 약물 데이터 로드 완료: {self.medication_file}")
            return medication_data
        except OSError:
            print(f"[INFO] 약물 데이터 파일 없음, 기본값 반환")
            return self._get_default_medication_data()
        except Exception as e:
            print(f"[ERROR] 약물 데이터 로드 실패: {e}")
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
                # WiFi 매니저를 통해 한국 시간 사용
                wifi_mgr = get_wifi_manager()
                current_time = wifi_mgr.get_kst_time()
                timestamp = f"{current_time[0]:04d}-{current_time[1]:02d}-{current_time[2]:02d}T{current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"
            
            # 기존 로그 로드
            logs = self.load_dispense_logs()
            
            # 새 로그 추가
            wifi_mgr = get_wifi_manager()
            current_time = wifi_mgr.get_kst_time()
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
            with open(self.dispense_log_file, 'w') as f:
                json.dump(logs, f)
            
            print(f"[OK] 배출 기록 저장: 일정 {dose_index + 1}, 성공: {success}")
            return True
            
        except Exception as e:
            print(f"[ERROR] 배출 기록 저장 실패: {e}")
            return False
    
    def load_dispense_logs(self):
        """배출 기록 로드"""
        try:
            with open(self.dispense_log_file, 'r') as f:
                logs = json.load(f)
            return logs
        except OSError:
            return []
        except Exception as e:
            print(f"[ERROR] 배출 기록 로드 실패: {e}")
            return []
    
    def get_today_dispense_logs(self):
        """오늘 배출 기록만 반환"""
        try:
            logs = self.load_dispense_logs()
            today = date.today().strftime("%Y-%m-%d")
            today_logs = [log for log in logs if log.get("date") == today]
            return today_logs
        except Exception as e:
            print(f"[ERROR] 오늘 배출 기록 로드 실패: {e}")
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
            print(f"[ERROR] 오늘 배출 확인 실패: {e}")
            return False
    
    # ===== 약물 수량 관리 =====
    
    def update_disk_count(self, disk_num, new_count):
        """디스크 약물 수량 업데이트"""
        try:
            medication_data = self.load_medication_data()
            disk_key = str(disk_num)
            
            if disk_key in medication_data["disks"]:
                # 현재 시간 가져오기 (한국 시간)
                wifi_mgr = get_wifi_manager()
                current_time = wifi_mgr.get_kst_time()
                
                medication_data["disks"][disk_key]["current_count"] = new_count
                medication_data["disks"][disk_key]["last_refill"] = f"{current_time[0]:04d}-{current_time[1]:02d}-{current_time[2]:02d}T{current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}"
                
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
                
                return self.save_medication_data(medication_data)
            else:
                print(f"[ERROR] 디스크 {disk_num} 데이터 없음")
                return False
                
        except Exception as e:
            print(f"[ERROR] 디스크 수량 업데이트 실패: {e}")
            return False
    
    def get_disk_count(self, disk_num):
        """디스크 약물 수량 조회"""
        try:
            medication_data = self.load_medication_data()
            disk_key = str(disk_num)
            
            if disk_key in medication_data["disks"]:
                return medication_data["disks"][disk_key]["current_count"]
            else:
                return 0
        except Exception as e:
            print(f"[ERROR] 디스크 수량 조회 실패: {e}")
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
            print(f"[ERROR] 디스크 부족 확인 실패: {e}")
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
            
            for file_path in files_to_clear:
                try:
                    os.remove(file_path)
                    print(f"[OK] 파일 삭제: {file_path}")
                except OSError:
                    # 파일이 없으면 무시
                    pass
            
            print("[OK] 모든 데이터 삭제 완료")
            return True
        except Exception as e:
            print(f"[ERROR] 데이터 삭제 실패: {e}")
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
            print(f"[ERROR] 데이터 요약 생성 실패: {e}")
            return None
