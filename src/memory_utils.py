"""
메모리 관리 유틸리티
모든 파일에서 일관되게 사용할 수 있는 표준화된 메모리 관리 함수들
"""

import gc
import time

def standard_garbage_collection(iterations=10, sleep_ms=100, context=""):
    """표준화된 가비지 컬렉션"""
    try:
        # print(f"[INFO] 표준 가비지 컬렉션 시작 [{context}]")
        
        for i in range(iterations):
            gc.collect()
            time.sleep_ms(sleep_ms)
            # print(f"[INFO] GC {i+1}/{iterations} 완료")
        
        # 메모리 상태 확인
        free_mem = gc.mem_free()
        alloc_mem = gc.mem_alloc()
        total_mem = free_mem + alloc_mem
        usage_percent = (alloc_mem / total_mem) * 100
        # print(f"[MEMORY] GC 후 메모리 상태: 여유 {free_mem:,} bytes, 사용률 {usage_percent:.1f}%")
        
        # print("[OK] 표준 가비지 컬렉션 완료")
        return {
            'free': free_mem,
            'allocated': alloc_mem,
            'usage_percent': usage_percent
        }
        
    except Exception as e:
        # print(f"[ERROR] 가비지 컬렉션 실패: {e}")
        pass
        return None

def quick_garbage_collection(context=""):
    """빠른 가비지 컬렉션 (5회 반복)"""
    return standard_garbage_collection(5, 50, f"빠른_{context}")

def aggressive_garbage_collection(context=""):
    """적극적인 가비지 컬렉션 (1회 반복 - 간소화)"""
    return standard_garbage_collection(1, 50, f"적극적_{context}")

def cleanup_references_and_gc(obj, context=""):
    """참조 정리 후 가비지 컬렉션"""
    try:
        # print(f"[INFO] 참조 정리 및 가비지 컬렉션 시작 [{context}]")
        
        # 참조 정리
        if hasattr(obj, '_cleanup_references'):
            obj._cleanup_references()
        elif hasattr(obj, 'cleanup_references'):
            obj.cleanup_references()
        
        # 가비지 컬렉션
        result = standard_garbage_collection(10, 100, context)
        
        # print("[OK] 참조 정리 및 가비지 컬렉션 완료")
        return result
        
    except Exception as e:
        # print(f"[ERROR] 참조 정리 및 가비지 컬렉션 실패: {e}")
        return None

def memory_aware_initialization(obj, context=""):
    """메모리 인식 초기화"""
    try:
        # print(f"[INFO] 메모리 인식 초기화 시작 [{context}]")
        
        # 초기화 전 메모리 상태
        before = standard_garbage_collection(3, 50, f"{context}_초기화전")
        
        # 객체 초기화
        if hasattr(obj, '__init__'):
            # 이미 초기화된 경우 스킵
            if hasattr(obj, '_initialized') and obj._initialized:
                # print("[INFO] 이미 초기화됨, 스킵")
                return True
        
        # 초기화 후 메모리 상태
        after = standard_garbage_collection(3, 50, f"{context}_초기화후")
        
        if before and after:
            memory_used = before['free'] - after['free']
            # print(f"[MEMORY] 초기화로 사용된 메모리: {memory_used:,} bytes")
            
            # 메모리 사용률이 85%를 초과하면 경고
            if after['usage_percent'] > 85:
                # print(f"[WARN] 메모리 사용률 높음: {after['usage_percent']:.1f}%")
                pass
        
        # print("[OK] 메모리 인식 초기화 완료")
        return True
        
    except Exception as e:
        # print(f"[ERROR] 메모리 인식 초기화 실패: {e}")
        return False
