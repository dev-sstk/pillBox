"""
메모리 모니터링 시스템
ESP32-C6에서 실시간 메모리 사용량을 추적하고 관리하는 시스템
"""

import gc
import micropython
import time

class MemoryMonitor:
    """메모리 모니터링 클래스"""
    
    def __init__(self):
        """메모리 모니터 초기화"""
        self.memory_history = []
        self.max_history = 50  # 최대 50개 기록 유지
        self.critical_threshold = 20000  # 20KB 이하 시 위험
        self.warning_threshold = 30000   # 30KB 이하 시 경고
        
    def get_memory_info(self):
        """현재 메모리 정보 반환"""
        try:
            # 가비지 컬렉션 실행
            gc.collect()
            
            # 메모리 정보 수집
            memory_info = {
                'timestamp': time.ticks_ms(),
                'free': gc.mem_free(),
                'allocated': gc.mem_alloc(),
                'total': gc.mem_free() + gc.mem_alloc(),
                'usage_percent': (gc.mem_alloc() / (gc.mem_free() + gc.mem_alloc())) * 100
            }
            
            # 스택 정보 (가능한 경우)
            try:
                memory_info['stack'] = micropython.stack_use()
            except:
                memory_info['stack'] = 0
            
            return memory_info
            
        except Exception as e:
            print(f"[ERROR] 메모리 정보 수집 실패: {e}")
            return None
    
    def log_memory_usage(self, context=""):
        """메모리 사용량 로깅"""
        memory_info = self.get_memory_info()
        if memory_info:
            # 히스토리에 추가
            memory_info['context'] = context
            self.memory_history.append(memory_info)
            
            # 히스토리 크기 제한
            if len(self.memory_history) > self.max_history:
                self.memory_history.pop(0)
            
            # 메모리 상태 출력
            status = self._get_memory_status(memory_info)
            print(f"[STATS] 메모리 상태 [{context}]: {status}")
            print(f"   [SAVE] 사용: {memory_info['allocated']:,} bytes ({memory_info['usage_percent']:.1f}%)")
            print(f"   🆓 여유: {memory_info['free']:,} bytes")
            if memory_info['stack'] > 0:
                print(f"   📚 스택: {memory_info['stack']:,} bytes")
            
            return memory_info
        return None
    
    def _get_memory_status(self, memory_info):
        """메모리 상태 판정"""
        free_memory = memory_info['free']
        
        if free_memory < self.critical_threshold:
            return "🔴 CRITICAL"
        elif free_memory < self.warning_threshold:
            return "🟡 WARNING"
        else:
            return "🟢 OK"
    
    def check_memory_before_allocation(self, required_bytes, context=""):
        """메모리 할당 전 체크"""
        memory_info = self.get_memory_info()
        if not memory_info:
            return False
        
        free_memory = memory_info['free']
        
        print(f"[SEARCH] 메모리 할당 체크 [{context}]:")
        print(f"   요청: {required_bytes:,} bytes")
        print(f"   여유: {free_memory:,} bytes")
        
        if free_memory < required_bytes:
            print(f"   [ERROR] 메모리 부족! {required_bytes - free_memory:,} bytes 부족")
            return False
        elif free_memory < required_bytes * 2:
            print(f"   [WARN] 메모리 부족 위험! 여유 공간 부족")
            return True
        else:
            print(f"   [OK] 메모리 할당 가능")
            return True
    
    def force_cleanup(self, context=""):
        """강제 메모리 정리"""
        print(f"🧹 강제 메모리 정리 시작 [{context}]")
        
        # 정리 전 메모리 상태
        before = self.get_memory_info()
        if before:
            print(f"   정리 전: {before['free']:,} bytes 여유")
        
        # 강화된 가비지 컬렉션
        for i in range(5):
            gc.collect()
            time.sleep(0.01)
        
        # 정리 후 메모리 상태
        after = self.get_memory_info()
        if after and before:
            freed = after['free'] - before['free']
            print(f"   정리 후: {after['free']:,} bytes 여유")
            print(f"   해제됨: {freed:,} bytes")
        
        print(f"[OK] 강제 메모리 정리 완료")
        return after
    
    def get_memory_trend(self):
        """메모리 사용량 트렌드 분석"""
        if len(self.memory_history) < 2:
            return "트렌드 분석 불가 (데이터 부족)"
        
        recent = self.memory_history[-5:]  # 최근 5개 기록
        oldest = recent[0]
        newest = recent[-1]
        
        trend = newest['free'] - oldest['free']
        
        if trend > 1000:
            return f"📈 메모리 개선 (+{trend:,} bytes)"
        elif trend < -1000:
            return f"📉 메모리 악화 ({trend:,} bytes)"
        else:
            return f"[STATS] 메모리 안정 ({trend:+,} bytes)"
    
    def print_memory_summary(self):
        """메모리 사용량 요약 출력"""
        print("=" * 50)
        print("[STATS] 메모리 사용량 요약")
        print("=" * 50)
        
        current = self.get_memory_info()
        if current:
            print(f"현재 상태: {self._get_memory_status(current)}")
            print(f"사용 중: {current['allocated']:,} bytes ({current['usage_percent']:.1f}%)")
            print(f"여유 공간: {current['free']:,} bytes")
            print(f"트렌드: {self.get_memory_trend()}")
        
        if self.memory_history:
            print(f"\n히스토리: {len(self.memory_history)}개 기록")
            print("최근 3개 기록:")
            for i, record in enumerate(self.memory_history[-3:]):
                print(f"  {i+1}. [{record['context']}] {record['free']:,} bytes 여유")
        
        print("=" * 50)

# 전역 메모리 모니터 인스턴스
memory_monitor = MemoryMonitor()

def log_memory(context=""):
    """메모리 사용량 로깅 (편의 함수)"""
    return memory_monitor.log_memory_usage(context)

def check_memory(required_bytes, context=""):
    """메모리 할당 전 체크 (편의 함수)"""
    return memory_monitor.check_memory_before_allocation(required_bytes, context)

def cleanup_memory(context=""):
    """강제 메모리 정리 (편의 함수)"""
    return memory_monitor.force_cleanup(context)

def print_memory_summary():
    """메모리 요약 출력 (편의 함수)"""
    memory_monitor.print_memory_summary()
