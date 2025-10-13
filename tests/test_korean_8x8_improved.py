# -*- coding: utf-8 -*-
"""
개선된 8x8 한글 폰트 테스트
- 실제 한글 모양으로 개선된 8x8 폰트 테스트
- 도형이 아닌 구별 가능한 한글 모양 확인
"""

import time
from hardware_interface import HardwareInterface
from fonts.korean_patch import KoreanPatch

def test_improved_8x8_korean_fonts():
    """개선된 8x8 한글 폰트 테스트"""
    print("=== 개선된 8x8 한글 폰트 테스트 시작 ===")
    
    # 1. 하드웨어 초기화
    print("하드웨어 초기화 중...")
    hw = HardwareInterface()
    hw.display.fb.fill(0xFFFF)  # 흰색으로 초기화
    print("하드웨어 초기화 완료")

    # 2. 한글 패치 초기화
    print("한글 패치 초기화 중...")
    kp = KoreanPatch()
    print(f"지원하는 한글 문자 수: {len(kp.get_all_korean_fonts())}")

    # 3. 개선된 한글 문자 테스트
    print("\n=== 개선된 8x8 한글 문자 테스트 ===")
    test_chars = ['알', '약', '필', '박', '스', '마', '트', '디', '펜', '서']
    
    x, y = 10, 10
    chars_per_row = 5
    
    for i, char in enumerate(test_chars):
        row = i // chars_per_row
        col = i % chars_per_row
        
        char_x = x + col * 10  # 8픽셀 + 2픽셀 간격
        char_y = y + row * 12  # 8픽셀 + 4픽셀 간격
        
        print(f"개선된 8x8 문자 '{char}' 그리기 at ({char_x}, {char_y})")
        
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
    print("개선된 8x8 한글 문자 테스트 완료")
    print("3초간 화면을 확인할 수 있습니다...")
    time.sleep(3)
    
    return True

def test_improved_korean_text():
    """개선된 한글 텍스트 테스트"""
    print("\n=== 개선된 한글 텍스트 테스트 ===")
    
    hw = HardwareInterface()
    kp = KoreanPatch()
    
    # 화면 지우기
    hw.display.fb.fill(0xFFFF)
    
    # 테스트할 텍스트들
    test_texts = [
        "알약",
        "필박스", 
        "스마트",
        "디스펜서"
    ]
    
    y_start = 10
    line_height = 12
    
    for i, text in enumerate(test_texts):
        y = y_start + i * line_height
        print(f"개선된 한글 텍스트 그리기: '{text}' at (10, {y})")
        
        x = 10
        for char in text:
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
                x += 9  # 8픽셀 + 1픽셀 간격
            else:
                print(f"❌ 폰트 없음: {char}")
                x += 6  # 기본 간격
    
    hw.display.update_display()
    print("개선된 한글 텍스트 테스트 완료")
    print("3초간 화면을 확인할 수 있습니다...")
    time.sleep(3)
    
    return True

def test_font_comparison():
    """폰트 비교 테스트"""
    print("\n=== 폰트 비교 테스트 ===")
    
    hw = HardwareInterface()
    kp = KoreanPatch()
    
    # 화면 지우기
    hw.display.fb.fill(0xFFFF)
    
    # 비교할 텍스트
    text = "스마트"
    
    # 상단: 개선된 8x8 폰트
    print("상단: 개선된 8x8 폰트")
    x, y = 10, 10
    for char in text:
        font_data = kp.get_korean_font(char)
        if font_data:
            for row_idx, row_data in enumerate(font_data):
                for bit in range(8):
                    if (row_data >> (7-bit)) & 1:
                        hw.display.fb.fill_rect(
                            x + bit,
                            y + row_idx,
                            1, 1,
                            0x0000  # 검은색
                        )
            x += 9
    
    # 하단: 16x16 폰트 (도형)
    print("하단: 16x16 폰트 (도형)")
    from fonts.korean_font_renderer_16x16 import KoreanFontRenderer16x16
    renderer_16x16 = KoreanFontRenderer16x16(hw.display.fb)
    renderer_16x16.draw_text_16x16(10, 30, text, 0x0000, 1)
    
    hw.display.update_display()
    print("폰트 비교 완료")
    print("상단: 개선된 8x8 폰트, 하단: 16x16 도형 폰트")
    print("3초간 화면을 확인할 수 있습니다...")
    time.sleep(3)
    
    return True

def run_improved_tests():
    """모든 개선된 테스트 실행"""
    print("개선된 8x8 한글 폰트 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("개선된 8x8 한글 문자", test_improved_8x8_korean_fonts),
        ("개선된 한글 텍스트", test_improved_korean_text),
        ("폰트 비교", test_font_comparison)
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
    print("개선된 테스트 결과 요약:")
    success_count = 0
    for test_name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"  {test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n총 {len(results)}개 테스트 중 {success_count}개 성공")
    
    if success_count == len(results):
        print("🎉 모든 개선된 테스트 통과!")
    else:
        print("⚠️ 일부 테스트 실패")
    
    return success_count == len(results)

if __name__ == "__main__":
    # 개별 테스트 실행
    # test_improved_8x8_korean_fonts()
    # test_improved_korean_text()
    # test_font_comparison()
    
    # 모든 테스트 실행
    run_improved_tests()


