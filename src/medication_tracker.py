"""
약물 추적 시스템
디스크별 약물 수량 관리 및 소진 알림
"""

import time

class MedicationTracker:
    """약물 추적 및 관리 클래스"""
    
    def __init__(self, data_manager):
        """약물 추적기 초기화"""
        self.data_manager = data_manager
        self.low_stock_threshold = 3  # 부족 임계값
        self.critical_threshold = 1   # 위험 임계값
        
        # 알림 상태
        self.notifications = {
            "low_stock": [],      # 부족 알림
            "critical": [],       # 위험 알림
            "empty": []          # 소진 알림
        }
        
        print("[OK] MedicationTracker 초기화 완료")
    
    def check_all_disks(self):
        """모든 디스크 상태 확인"""
        try:
            status = {
                "disks": {},
                "alerts": [],
                "summary": {
                    "total_disks": 3,
                    "low_stock_count": 0,
                    "critical_count": 0,
                    "empty_count": 0
                }
            }
            
            for disk_num in [1, 2, 3]:
                disk_status = self.check_disk_status(disk_num)
                status["disks"][disk_num] = disk_status
                
                # 요약 정보 업데이트
                if disk_status["status"] == "empty":
                    status["summary"]["empty_count"] += 1
                elif disk_status["status"] == "critical":
                    status["summary"]["critical_count"] += 1
                elif disk_status["status"] == "low_stock":
                    status["summary"]["low_stock_count"] += 1
                
                # 알림 생성
                if disk_status["alert"]:
                    status["alerts"].append(disk_status["alert"])
            
            return status
            
        except Exception as e:
            print(f"[ERROR] 디스크 상태 확인 실패: {e}")
            return None
    
    def check_disk_status(self, disk_num):
        """특정 디스크 상태 확인"""
        try:
            current_count = self.data_manager.get_disk_count(disk_num)
            medication_data = self.data_manager.load_medication_data()
            
            # 디스크 정보 가져오기
            disk_info = medication_data.get("disks", {}).get(str(disk_num), {})
            disk_name = disk_info.get("name", f"디스크 {disk_num}")
            
            print(f"[DEBUG] 디스크 {disk_num} 상태 확인: {current_count}개, 임계값={self.low_stock_threshold}, 위험값={self.critical_threshold}")
            
            # 상태 결정
            if current_count <= 0:
                status = "empty"
                alert = {
                    "type": "empty",
                    "disk": disk_num,
                    "message": f"{disk_name} 소진됨 - 즉시 충전 필요",
                    "priority": "critical"
                }
                print(f"[DEBUG] 디스크 {disk_num}: 소진 상태 (0개)")
            elif current_count <= self.critical_threshold:
                status = "critical"
                alert = {
                    "type": "critical",
                    "disk": disk_num,
                    "message": f"{disk_name} 위험 수준 ({current_count}개 남음)",
                    "priority": "high"
                }
                print(f"[DEBUG] 디스크 {disk_num}: 위험 상태 ({current_count}개)")
            elif current_count <= self.low_stock_threshold:
                status = "low_stock"
                alert = {
                    "type": "low_stock",
                    "disk": disk_num,
                    "message": f"{disk_name} 부족 ({current_count}개 남음)",
                    "priority": "medium"
                }
                print(f"[DEBUG] 디스크 {disk_num}: 부족 상태 ({current_count}개)")
            else:
                status = "normal"
                alert = None
                print(f"[DEBUG] 디스크 {disk_num}: 정상 상태 ({current_count}개)")
            
            return {
                "disk_num": disk_num,
                "disk_name": disk_name,
                "current_count": current_count,
                "status": status,
                "alert": alert,
                "last_refill": disk_info.get("last_refill"),
                "medication_type": disk_info.get("medication_type", "unknown")
            }
            
        except Exception as e:
            print(f"[ERROR] 디스크 {disk_num} 상태 확인 실패: {e}")
            return {
                "disk_num": disk_num,
                "disk_name": f"디스크 {disk_num}",
                "current_count": 0,
                "status": "error",
                "alert": {
                    "type": "error",
                    "disk": disk_num,
                    "message": f"디스크 {disk_num} 상태 확인 오류",
                    "priority": "high"
                },
                "last_refill": None,
                "medication_type": "unknown"
            }
    
    def get_disk_medication_info(self, disk_num):
        """디스크 약물 정보 조회"""
        try:
            medication_data = self.data_manager.load_medication_data()
            disk_info = medication_data.get("disks", {}).get(str(disk_num), {})
            
            return {
                "name": disk_info.get("name", f"디스크 {disk_num}"),
                "total_capacity": disk_info.get("total_capacity", 15),
                "current_count": self.data_manager.get_disk_count(disk_num),
                "last_refill": disk_info.get("last_refill"),
                "medication_type": disk_info.get("medication_type", "unknown"),
                "refill_count": len([r for r in medication_data.get("refill_history", []) if r.get("disk") == disk_num])
            }
            
        except Exception as e:
            print(f"[ERROR] 디스크 {disk_num} 약물 정보 조회 실패: {e}")
            return None
    
    def update_disk_medication(self, disk_num, new_count, medication_name=None):
        """디스크 약물 수량 업데이트"""
        try:
            # 수량 업데이트
            success = self.data_manager.update_disk_count(disk_num, new_count)
            
            if success and medication_name:
                # 약물 이름 업데이트
                medication_data = self.data_manager.load_medication_data()
                disk_key = str(disk_num)
                
                if disk_key in medication_data["disks"]:
                    medication_data["disks"][disk_key]["name"] = medication_name
                    self.data_manager.save_medication_data(medication_data)
                    print(f"[OK] 디스크 {disk_num} 약물 이름 업데이트: {medication_name}")
            
            return success
            
        except Exception as e:
            print(f"[ERROR] 디스크 {disk_num} 약물 정보 업데이트 실패: {e}")
            return False
    
    def get_refill_history(self, disk_num=None, limit=10):
        """리필 기록 조회"""
        try:
            medication_data = self.data_manager.load_medication_data()
            refill_history = medication_data.get("refill_history", [])
            
            # 특정 디스크 필터링
            if disk_num is not None:
                refill_history = [r for r in refill_history if r.get("disk") == disk_num]
            
            # 최신 순으로 정렬 및 제한
            refill_history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return refill_history[:limit]
            
        except Exception as e:
            print(f"[ERROR] 리필 기록 조회 실패: {e}")
            return []
    
    def get_dispense_history(self, disk_num=None, days=7):
        """배출 기록 조회"""
        try:
            all_logs = self.data_manager.load_dispense_logs()
            
            # 특정 디스크 필터링 (일정 인덱스 = 디스크 번호 - 1)
            if disk_num is not None:
                dose_index = disk_num - 1
                all_logs = [log for log in all_logs if log.get("dose_index") == dose_index]
            
            # 최근 N일 필터링 (MicroPython time 모듈 사용)
            current_time = time.time()
            cutoff_time = current_time - (days * 24 * 60 * 60)  # N일 전 시간
            cutoff_date = time.localtime(cutoff_time)
            cutoff_date_str = f"{cutoff_date[0]:04d}-{cutoff_date[1]:02d}-{cutoff_date[2]:02d}"
            recent_logs = [log for log in all_logs if log.get("date", "") >= cutoff_date_str]
            
            return recent_logs
            
        except Exception as e:
            print(f"[ERROR] 배출 기록 조회 실패: {e}")
            return []
    
    def get_medication_summary(self):
        """약물 상태 요약"""
        try:
            status = self.check_all_disks()
            if not status:
                return None
            
            summary = {
                "total_disks": 3,
                "normal_disks": 0,
                "low_stock_disks": 0,
                "critical_disks": 0,
                "empty_disks": 0,
                "alerts": status["alerts"],
                "disk_details": {}
            }
            
            for disk_num, disk_status in status["disks"].items():
                summary["disk_details"][disk_num] = {
                    "name": disk_status["disk_name"],
                    "count": disk_status["current_count"],
                    "status": disk_status["status"],
                    "alert": disk_status["alert"]
                }
                
                # 상태별 카운트
                if disk_status["status"] == "normal":
                    summary["normal_disks"] += 1
                elif disk_status["status"] == "low_stock":
                    summary["low_stock_disks"] += 1
                elif disk_status["status"] == "critical":
                    summary["critical_disks"] += 1
                elif disk_status["status"] == "empty":
                    summary["empty_disks"] += 1
            
            return summary
            
        except Exception as e:
            print(f"[ERROR] 약물 상태 요약 생성 실패: {e}")
            return None
    
    def check_low_stock_alerts(self):
        """부족 알림 확인"""
        try:
            alerts = []
            status = self.check_all_disks()
            
            if status:
                for disk_num, disk_status in status["disks"].items():
                    if disk_status["alert"]:
                        alerts.append(disk_status["alert"])
            
            return alerts
            
        except Exception as e:
            print(f"[ERROR] 부족 알림 확인 실패: {e}")
            return []
    
    def get_next_refill_reminder(self):
        """다음 리필 알림 시간 계산"""
        try:
            # 오늘 배출된 약물 확인
            today_logs = self.data_manager.get_today_dispense_logs()
            dispensed_disks = set()
            
            for log in today_logs:
                if log.get("success"):
                    dispensed_disks.add(log.get("dose_index") + 1)  # 일정 인덱스를 디스크 번호로 변환
            
            # 배출된 디스크 중 부족한 것들 확인
            low_stock_disks = []
            for disk_num in dispensed_disks:
                if self.data_manager.is_disk_low_stock(disk_num):
                    low_stock_disks.append(disk_num)
            
            return {
                "dispensed_today": list(dispensed_disks),
                "low_stock_disks": low_stock_disks,
                "needs_refill": len(low_stock_disks) > 0
            }
            
        except Exception as e:
            print(f"[ERROR] 다음 리필 알림 계산 실패: {e}")
            return None
    
    def generate_medication_report(self):
        """약물 상태 보고서 생성"""
        try:
            summary = self.get_medication_summary()
            if not summary:
                return None
            
            report = {
                "timestamp": time.time(),
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "summary": summary,
                "recommendations": []
            }
            
            # 권장사항 생성
            if summary["empty_disks"] > 0:
                report["recommendations"].append("즉시 약물 충전이 필요한 디스크가 있습니다.")
            
            if summary["critical_disks"] > 0:
                report["recommendations"].append("위험 수준의 디스크가 있습니다. 곧 충전하세요.")
            
            if summary["low_stock_disks"] > 0:
                report["recommendations"].append("부족한 디스크가 있습니다. 충전을 준비하세요.")
            
            if summary["normal_disks"] == 3:
                report["recommendations"].append("모든 디스크가 충분합니다.")
            
            return report
            
        except Exception as e:
            print(f"[ERROR] 약물 보고서 생성 실패: {e}")
            return None
