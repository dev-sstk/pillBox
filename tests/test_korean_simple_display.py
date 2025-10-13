# -*- coding: utf-8 -*-
"""
한글 간단 출력 테스트
- KoreanPatch와 HardwareInterface 사용
- 화면에 한글 텍스트 표시 테스트
- 다양한 한글 문자 테스트
"""

import time
from hardware_interface import HardwareInterface
from fonts.korean_patch import KoreanPatch

def draw_text_example():
    """기본 한글 텍스트 출력 예제"""
    print("=== 한글 간단 출력 테스트 시작 ===")
    
    # 1. 하드웨어 초기화
    print("하드웨어 초기화 중...")
    hw = HardwareInterface()
    hw.display.fb.fill(0xFFFF)  # 흰색으로 초기화
    print("하드웨어 초기화 완료")

    # 2. 한글 패치 초기화
    print("한글 패치 초기화 중...")
    kp = KoreanPatch()
    print(f"지원하는 한글 문자 수: {len(kp.get_all_korean_fonts())}")

    # 3. 표시할 텍스트들
    test_texts = [
        "안녕하세요",
        "스마트 디스펜서", 
        "알약 필박스",
        "시스템 초기화",
        "복용 횟수 선택"
    ]
    
    y_start = 10
    line_height = 12
    
    # 4. 각 텍스트를 화면에 그리기
    for i, text in enumerate(test_texts):
        x, y = 10, y_start + i * line_height
        print(f"텍스트 그리기: '{text}' at ({x}, {y})")
        
        # 글자 단위로 화면에 그리기
        for char in text:
            font_data = kp.get_korean_font(char)
            if font_data:
                # 8x8 폰트 렌더링
                for row_idx, row in enumerate(font_data):
                    for bit in range(8):
                        if (row >> (7-bit)) & 1:
                            hw.display.fb.fill_rect(
                                x + bit,
                                y + row_idx,
                                1, 1,
                                0x0000  # 검은색
                            )
                x += 9  # 글자 간격 (8픽셀 + 1픽셀)
            else:
                print(f"❌ 폰트 없음: {char}")
                x += 6  # 폰트가 없는 경우 기본 간격

    # 5. 화면 갱신
    hw.display.update_display()
    print("화면에 한글 텍스트 출력 완료")
    print("3초간 화면을 확인할 수 있습니다...")
    time.sleep(3)
    
    return True

def test_individual_characters():
    """개별 한글 문자 테스트"""
    print("\n=== 개별 한글 문자 테스트 ===")
    
    hw = HardwareInterface()
    kp = KoreanPatch()
    
    # 테스트할 문자들
    test_chars = ['스', '마', '트', '디', '스', '펜', '서', '알', '약', '필', '박']
    
    # 화면 지우기
    hw.display.fb.fill(0xFFFF)
    
    x, y = 10, 10
    chars_per_row = 8
    
    for i, char in enumerate(test_chars):
        row = i // chars_per_row
        col = i % chars_per_row
        
        char_x = x + col * 10
        char_y = y + row * 12
        
        print(f"문자 '{char}' 그리기 at ({char_x}, {char_y})")
        
        font_data = kp.get_korean_font(char)
        if font_data:
            # 8x8 폰트 렌더링
            for row_idx, row_data in enumerate(font_data):
                for bit in range(8):
                    if (row_data >> (7-bit)) & 1:
                        hw.display.fb.fill_rect(
                            char_x + bit,
                            char_y + row_idx,
                            1, 1,
                            0x0000  # 검은색
                        )
        else:
            print(f"❌ 폰트 없음: {char}")
    
    hw.display.update_display()
    print("개별 문자 테스트 완료")
    print("2초간 화면을 확인할 수 있습니다...")
    time.sleep(2)
    
    return True

def test_mixed_text():
    """영문과 한글 혼합 텍스트 테스트"""
    print("\n=== 영문/한글 혼합 텍스트 테스트 ===")
    
    hw = HardwareInterface()
    kp = KoreanPatch()
    
    # 혼합 텍스트들
    mixed_texts = [
        "Smart 스마트",
        "PILLBOX 필박스", 
        "알약 Pill",
        "디스펜서 Dispenser"
    ]
    
    # 화면 지우기
    hw.display.fb.fill(0xFFFF)
    
    y_start = 20
    line_height = 15
    
    for i, text in enumerate(mixed_texts):
        x, y = 10, y_start + i * line_height
        print(f"혼합 텍스트 그리기: '{text}' at ({x}, {y})")
        
        for char in text:
            if kp.is_korean_char(char):
                # 한글 문자 처리
                font_data = kp.get_korean_font(char)
                if font_data:
                    # 8x8 폰트 렌더링
                    for row_idx, row_data in enumerate(font_data):
                        for bit in range(8):
                            if (row_data >> (7-bit)) & 1:
                                hw.display.fb.fill_rect(
                                    x + bit,
                                    y + row_idx,
                                    1, 1,
                                    0x0000  # 검은색
                                )
                    x += 9  # 한글 간격
                else:
                    print(f"❌ 한글 폰트 없음: {char}")
                    x += 6
            else:
                # 영문/숫자/기호 처리 (간단한 점으로 표시)
                hw.display.fb.fill_rect(x, y, 5, 8, 0x0000)
                x += 6  # 영문 간격
    
    hw.display.update_display()
    print("혼합 텍스트 테스트 완료")
    print("2초간 화면을 확인할 수 있습니다...")
    time.sleep(2)
    
    return True

def test_font_coverage():
    """폰트 커버리지 테스트"""
    print("\n=== 폰트 커버리지 테스트 ===")
    
    kp = KoreanPatch()
    all_fonts = kp.get_all_korean_fonts()
    
    print(f"총 지원하는 한글 문자 수: {len(all_fonts)}")
    
    # 카테고리별 테스트
    categories = {
        '알약 관련': ['알', '약', '필', '박', '스', '마', '트', '디', '펜', '서'],
        '시스템 관련': ['시', '템', '초', '기', '설', '정', '을', '작', '합', '니', '다'],
        '상태 관련': ['성', '공', '완', '료', '오', '류', '발', '생', '실', '패'],
        '시간 관련': ['간', '분', '초', '일', '월', '년'],
        '복용 관련': ['복', '용', '횟', '수', '선', '택', '채', '우', '기'],
        '네트워크 관련': ['네', '트', '워', '크', '연', '결', '상', '태'],
        '기타': ['안', '녕', '하', '세', '요', '감', '사']
    }
    
    total_chars = 0
    available_chars = 0
    
    for category, chars in categories.items():
        print(f"\n{category}:")
        for char in chars:
            total_chars += 1
            if char in all_fonts:
                print(f"  ✅ {char}")
                available_chars += 1
            else:
                print(f"  ❌ {char} (폰트 없음)")
    
    coverage = (available_chars / total_chars) * 100 if total_chars > 0 else 0
    print(f"\n📊 폰트 커버리지: {available_chars}/{total_chars} ({coverage:.1f}%)")
    
    return True

def run_all_tests():
    """모든 테스트 실행"""
    print("한글 간단 출력 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("기본 한글 텍스트", draw_text_example),
        ("개별 한글 문자", test_individual_characters),
        ("영문/한글 혼합", test_mixed_text),
        ("폰트 커버리지", test_font_coverage)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} 테스트 ---")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} 테스트 성공")
            else:
                print(f"❌ {test_name} 테스트 실패")
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 오류: {e}")
            results.append((test_name, False))
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("테스트 결과 요약:")
    success_count = 0
    for test_name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"  {test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n총 {len(results)}개 테스트 중 {success_count}개 성공")
    
    if success_count == len(results):
        print("🎉 모든 테스트 통과!")
    else:
        print("⚠️ 일부 테스트 실패")
    
    return success_count == len(results)

if __name__ == "__main__":
    # 개별 테스트 실행
    # draw_text_example()
    # test_individual_characters()
    # test_mixed_text()
    # test_font_coverage()
    
    # 모든 테스트 실행
    run_all_tests()


