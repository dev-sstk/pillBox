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
        """메모리 할당 전 체크 - I2S 초기화 전 특별 체크"""
        memory_info = self.get_memory_info()
        if not memory_info:
            return False
        
        free_memory = memory_info['free']
        usage_percent = memory_info['usage_percent']
        
        print(f"[SEARCH] 메모리 할당 체크 [{context}]:")
        print(f"   요청: {required_bytes:,} bytes")
        print(f"   여유: {free_memory:,} bytes")
        print(f"   사용률: {usage_percent:.1f}%")
        
        # I2S 초기화를 위한 특별 체크
        if "I2S" in context or "오디오" in context:
            # I2S는 최소 50KB 여유 메모리가 필요
            i2s_minimum = 50000
            if free_memory < i2s_minimum:
                print(f"   [ERROR] I2S 초기화 불가! 최소 {i2s_minimum:,} bytes 필요, 현재 {free_memory:,} bytes")
                return False
            elif usage_percent > 85:
                print(f"   [WARN] I2S 초기화 위험! 사용률 {usage_percent:.1f}% > 85%")
                return False
            else:
                print(f"   [OK] I2S 초기화 가능")
                return True
        
        # 일반 메모리 할당 체크
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
    
    def ensure_memory_usage_below_threshold(self, max_usage_percent=80, context=""):
        """메모리 사용률을 지정된 임계값 이하로 유지"""
        memory_info = self.get_memory_info()
        if not memory_info:
            return False
        
        current_usage = memory_info['usage_percent']
        
        print(f"[MEMORY] 메모리 사용률 체크 [{context}]:")
        print(f"   현재 사용률: {current_usage:.1f}%")
        print(f"   목표 사용률: {max_usage_percent}% 이하")
        
        if current_usage <= max_usage_percent:
            print(f"   [OK] 메모리 사용률 정상 ({current_usage:.1f}% ≤ {max_usage_percent}%)")
            return True
        
        print(f"   [WARN] 메모리 사용률 초과! 정리 필요")
        
        # 메모리 정리 수행
        attempts = 0
        max_attempts = 3
        
        while current_usage > max_usage_percent and attempts < max_attempts:
            attempts += 1
            print(f"   [INFO] 메모리 정리 시도 {attempts}/{max_attempts}")
            
            # 강제 정리 수행
            self.force_cleanup(f"{context}_attempt_{attempts}")
            
            # 메모리 상태 재확인
            memory_info = self.get_memory_info()
            if memory_info:
                current_usage = memory_info['usage_percent']
                print(f"   [INFO] 정리 후 사용률: {current_usage:.1f}%")
            
            # 잠시 대기
            time.sleep(0.1)
        
        if current_usage <= max_usage_percent:
            print(f"   [OK] 메모리 사용률 목표 달성 ({current_usage:.1f}% ≤ {max_usage_percent}%)")
            return True
        else:
            print(f"   [ERROR] 메모리 사용률 목표 미달성 ({current_usage:.1f}% > {max_usage_percent}%)")
            return False
    
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

def ensure_memory_usage_below_threshold(max_usage_percent=80, context=""):
    """메모리 사용률을 지정된 임계값 이하로 유지 (편의 함수)"""
    return memory_monitor.ensure_memory_usage_below_threshold(max_usage_percent, context)
