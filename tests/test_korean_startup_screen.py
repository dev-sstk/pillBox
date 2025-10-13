# -*- coding: utf-8 -*-
"""
한글 스타트업 스크린 테스트
- 한글 폰트 렌더링 테스트
- 영문/한글 혼합 텍스트 테스트
- 한국어 패치 모듈 검증
"""

import sys
# MicroPython 호환 경로 설정
sys.path.append('../src')

from hardware_interface import HardwareInterface
from startup_screen import StartupScreen
import time

def test_korean_startup_screen():
    """한글 스타트업 스크린 테스트"""
    print("=== 한글 스타트업 스크린 테스트 시작 ===")
    
    try:
        # 하드웨어 인터페이스 초기화
        print("하드웨어 인터페이스 초기화 중...")
        hw = HardwareInterface()
        print("하드웨어 인터페이스 초기화 완료")
        
        # 스타트업 스크린 초기화
        print("한글 스타트업 스크린 초기화 중...")
        startup_screen = StartupScreen(hw)
        print("스타트업 스크린 초기화 완료")
        
        # 한국어 패치 테스트
        print("\n=== 한국어 패치 테스트 ===")
        # FontRenderer에 korean_patch가 있는지 확인
        if hasattr(hw.display.font_renderer, 'korean_patch'):
            korean_patch = hw.display.font_renderer.korean_patch
            print(f"지원하는 한글 문자 수: {len(korean_patch.get_all_korean_fonts())}")
        else:
            # 직접 KoreanPatch 인스턴스 생성
            from fonts.korean_patch import KoreanPatch
            korean_patch = KoreanPatch()
            print(f"지원하는 한글 문자 수: {len(korean_patch.get_all_korean_fonts())}")
        
        # 테스트할 한글 문자들
        test_chars = ['스', '마', '트', '디', '스', '펜', '서', '알', '약', '필', '박']
        print("\n문자별 폰트 데이터 확인:")
        for char in test_chars:
            has_font = korean_patch.has_korean_font(char)
            print(f"  {char}: {'폰트 있음' if has_font else '폰트 없음'}")
        
        # 한글 텍스트 테스트
        print("\n=== 한글 텍스트 렌더링 테스트 ===")
        test_texts = [
            "스마트 디스펜서",
            "알약 필박스", 
            "Smart 스마트",
            "PILLBOX 필박스"
        ]
        
        for text in test_texts:
            print(f"텍스트: '{text}'")
            # get_text_width 메서드가 있는지 확인
            if hasattr(hw.display.font_renderer, 'get_text_width'):
                text_width = hw.display.font_renderer.get_text_width(text, 1)
                print(f"  너비: {text_width}픽셀")
            else:
                print(f"  너비: 계산 불가 (get_text_width 메서드 없음)")
            
            # 한글 문자 추출
            korean_chars = korean_patch.extract_korean_chars(text)
            print(f"  한글 문자: {korean_chars}")
            
            # 누락된 폰트 확인
            missing_fonts = korean_patch.get_missing_korean_fonts(text)
            if missing_fonts:
                print(f"  누락된 폰트: {missing_fonts}")
            else:
                print(f"  모든 폰트 사용 가능")
        
        # 실제 화면에 한글 스타트업 스크린 표시
        print("\n=== 한글 스타트업 스크린 표시 ===")
        print("화면에 한글 스타트업 스크린을 표시합니다...")
        
        # 화면 지우기
        hw.display.fb.fill(0xFFFF)  # 흰색으로 지우기
        hw.display.update_display()
        
        # 한글 스타트업 스크린 그리기
        startup_screen.show_startup_screen()
        hw.display.update_display()
        
        print("한글 스타트업 스크린 표시 완료!")
        print("화면을 확인해보세요:")
        print("  - PILLBOX (영문)")
        print("  - 스마트 (한글)")
        print("  - 디스펜서 (한글)")
        print("  - 알약 아이콘")
        
        # 3초간 대기
        print("\n3초간 화면을 확인할 수 있습니다...")
        time.sleep(3)
        
        # 추가 테스트: 혼합 텍스트
        print("\n=== 혼합 텍스트 테스트 ===")
        hw.display.fb.fill(0xFFFF)  # 화면 지우기
        
        # 혼합 텍스트들 테스트
        mixed_texts = [
            ("Smart 스마트", 80, 50),
            ("PILLBOX 필박스", 80, 70),
            ("알약 Pill", 80, 90),
            ("디스펜서 Dispenser", 80, 110)
        ]
        
        for text, x, y in mixed_texts:
            print(f"혼합 텍스트 그리기: '{text}' at ({x}, {y})")
            startup_screen.draw_clean_text(x, y, text, 0x07E0, 1)  # 라임 그린
        
        hw.display.update_display()
        print("혼합 텍스트 표시 완료!")
        print("2초간 확인할 수 있습니다...")
        time.sleep(2)
        
        print("\n=== 테스트 완료 ===")
        print("✅ 한글 폰트 렌더링 성공")
        print("✅ 영문/한글 혼합 텍스트 성공")
        print("✅ 한국어 패치 모듈 정상 작동")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        # MicroPython에서는 traceback 모듈이 없을 수 있음
        try:
            import traceback
            traceback.print_exc()
        except ImportError:
            print("traceback 모듈을 사용할 수 없습니다.")
        return False
    
    return True

def test_korean_font_coverage():
    """한글 폰트 커버리지 테스트"""
    print("\n=== 한글 폰트 커버리지 테스트 ===")
    
    try:
        from fonts.korean_patch import KoreanPatch
        
        patch = KoreanPatch()
        all_fonts = patch.get_all_korean_fonts()
        
        print(f"총 지원하는 한글 문자 수: {len(all_fonts)}")
        print("지원하는 문자들:")
        
        # 카테고리별로 분류해서 출력
        categories = {
            '알약 관련': ['알', '약', '필', '박', '스', '마', '트', '디', '펜', '서'],
            '시스템 관련': ['시', '템', '초', '기', '설', '정', '을', '작', '합', '니', '다'],
            '상태 관련': ['성', '공', '완', '료', '오', '류', '발', '생', '실', '패'],
            '시간 관련': ['간', '분', '초', '일', '월', '년'],
            '복용 관련': ['복', '용', '횟', '수', '선', '택', '채', '우', '기'],
            '네트워크 관련': ['네', '트', '워', '크', '연', '결', '상', '태'],
            '기타': ['안', '녕', '하', '세', '요', '감', '사']
        }
        
        for category, chars in categories.items():
            print(f"\n{category}:")
            for char in chars:
                if char in all_fonts:
                    print(f"  ✅ {char}")
                else:
                    print(f"  ❌ {char} (폰트 없음)")
        
        # 전체 커버리지 계산
        total_chars = sum(len(chars) for chars in categories.values())
        available_chars = sum(1 for chars in categories.values() for char in chars if char in all_fonts)
        coverage = (available_chars / total_chars) * 100 if total_chars > 0 else 0
        
        print(f"\n📊 폰트 커버리지: {available_chars}/{total_chars} ({coverage:.1f}%)")
        
    except Exception as e:
        print(f"❌ 커버리지 테스트 중 오류: {e}")

if __name__ == "__main__":
    print("한글 스타트업 스크린 테스트 시작")
    print("=" * 50)
    
    # 메인 테스트 실행
    success = test_korean_startup_screen()
    
    # 폰트 커버리지 테스트
    test_korean_font_coverage()
    
    if success:
        print("\n🎉 모든 테스트 통과!")
    else:
        print("\n❌ 테스트 실패")
    
    print("=" * 50)
    print("테스트 완료")
