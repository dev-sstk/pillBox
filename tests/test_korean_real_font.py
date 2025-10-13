# -*- coding: utf-8 -*-
"""
실제 한글 폰트 테스트
- 폰트 만들기 2.5로 만든 실제 한글 폰트 데이터 테스트
- 16x16 픽셀 실제 한글 모양 확인
"""

import time
from hardware_interface import HardwareInterface
from fonts.korean_font_renderer_real import KoreanFontRendererReal

def test_real_korean_fonts():
    """실제 한글 폰트 테스트"""
    print("=== 실제 한글 폰트 테스트 시작 ===")
    
    # 1. 하드웨어 초기화
    print("하드웨어 초기화 중...")
    hw = HardwareInterface()
    hw.display.fb.fill(0xFFFF)  # 흰색으로 초기화
    print("하드웨어 초기화 완료")

    # 2. 실제 한글 폰트 렌더러 초기화
    print("실제 한글 폰트 렌더러 초기화 중...")
    renderer = KoreanFontRendererReal(hw.display.fb)
    print(f"사용 가능한 폰트 개수: {renderer.get_font_count()}")
    print(f"사용 가능한 문자: {renderer.get_available_chars()}")

    # 3. 실제 한글 문자 테스트
    print("\n=== 실제 한글 문자 테스트 ===")
    test_chars = ['화', '면', '중', '앙', '을', '좌', '표', '로', '설', '정']
    
    x, y = 10, 10
    chars_per_row = 5
    
    for i, char in enumerate(test_chars):
        row = i // chars_per_row
        col = i % chars_per_row
        
        char_x = x + col * 18  # 16픽셀 + 2픽셀 간격
        char_y = y + row * 18  # 16픽셀 + 2픽셀 간격
        
        print(f"실제 한글 문자 '{char}' 그리기 at ({char_x}, {char_y})")
        
        if renderer.has_font(char):
            renderer.draw_font_16x16(char_x, char_y, char, 0x0000, 0xFFFF)
        else:
            print(f"❌ 폰트 없음: {char}")
    
    hw.display.update_display()
    print("실제 한글 문자 테스트 완료")
    print("3초간 화면을 확인할 수 있습니다...")
    time.sleep(3)
    
    return True

def test_real_korean_text():
    """실제 한글 텍스트 테스트"""
    print("\n=== 실제 한글 텍스트 테스트 ===")
    
    hw = HardwareInterface()
    renderer = KoreanFontRendererReal(hw.display.fb)
    
    # 화면 지우기
    hw.display.fb.fill(0xFFFF)
    
    # 테스트할 텍스트들
    test_texts = [
        "화면",
        "중앙", 
        "표로",
        "설정"
    ]
    
    y_start = 10
    line_height = 20
    
    for i, text in enumerate(test_texts):
        y = y_start + i * line_height
        print(f"실제 한글 텍스트 그리기: '{text}' at (10, {y})")
        
        renderer.draw_text_16x16(10, y, text, 0x0000, 0xFFFF)
    
    hw.display.update_display()
    print("실제 한글 텍스트 테스트 완료")
    print("3초간 화면을 확인할 수 있습니다...")
    time.sleep(3)
    
    return True

def test_font_scaling():
    """폰트 확대/축소 테스트"""
    print("\n=== 폰트 확대/축소 테스트 ===")
    
    hw = HardwareInterface()
    renderer = KoreanFontRendererReal(hw.display.fb)
    
    # 화면 지우기
    hw.display.fb.fill(0xFFFF)
    
    # 다양한 크기로 텍스트 그리기
    text = "화면"
    scales = [1, 2, 3]
    
    y_start = 10
    line_height = 20
    
    for i, scale in enumerate(scales):
        y = y_start + i * line_height * scale
        print(f"폰트 크기 {scale}배로 그리기: '{text}' at (10, {y})")
        
        renderer.draw_text_16x16(10, y, text, 0x0000, 0xFFFF, scale)
    
    hw.display.update_display()
    print("폰트 확대/축소 테스트 완료")
    print("3초간 화면을 확인할 수 있습니다...")
    time.sleep(3)
    
    return True

def test_center_alignment():
    """중앙 정렬 테스트"""
    print("\n=== 중앙 정렬 테스트 ===")
    
    hw = HardwareInterface()
    renderer = KoreanFontRendererReal(hw.display.fb)
    
    # 화면 지우기
    hw.display.fb.fill(0xFFFF)
    
    # 화면 중앙에 텍스트 그리기
    center_x = 80  # 160/2
    center_y = 64  # 128/2
    
    text = "화면"
    print(f"화면 중앙에 텍스트 그리기: '{text}' at ({center_x}, {center_y})")
    
    renderer.center_text_16x16(center_x, center_y, text, 0x0000, 0xFFFF)
    
    hw.display.update_display()
    print("중앙 정렬 테스트 완료")
    print("3초간 화면을 확인할 수 있습니다...")
    time.sleep(3)
    
    return True

def test_font_comparison():
    """폰트 비교 테스트"""
    print("\n=== 폰트 비교 테스트 ===")
    
    hw = HardwareInterface()
    renderer = KoreanFontRendererReal(hw.display.fb)
    
    # 화면 지우기
    hw.display.fb.fill(0xFFFF)
    
    # 상단: 실제 한글 폰트
    print("상단: 실제 한글 폰트")
    renderer.draw_text_16x16(10, 10, "화면", 0x0000, 0xFFFF)
    
    # 하단: 기존 8x8 폰트
    print("하단: 기존 8x8 폰트")
    from fonts.korean_patch import KoreanPatch
    kp = KoreanPatch()
    
    y = 50
    x = 10
    for char in "화면":
        font_data = kp.get_korean_font(char)
        if font_data:
            for row_idx, row_data in enumerate(font_data):
                for bit in range(8):
                    if (row_data >> (7-bit)) & 1:
                        hw.display.fb.fill_rect(
                            x + bit,
                            y + row_idx,
                            1, 1,
                            0x0000
                        )
            x += 9
        else:
            print(f"❌ 8x8 폰트 없음: {char}")
            x += 6
    
    hw.display.update_display()
    print("폰트 비교 완료")
    print("상단: 실제 16x16 한글 폰트, 하단: 기존 8x8 폰트")
    print("3초간 화면을 확인할 수 있습니다...")
    time.sleep(3)
    
    return True

def run_all_real_font_tests():
    """모든 실제 폰트 테스트 실행"""
    print("실제 한글 폰트 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("실제 한글 문자", test_real_korean_fonts),
        ("실제 한글 텍스트", test_real_korean_text),
        ("폰트 확대/축소", test_font_scaling),
        ("중앙 정렬", test_center_alignment),
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
    print("실제 폰트 테스트 결과 요약:")
    success_count = 0
    for test_name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"  {test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n총 {len(results)}개 테스트 중 {success_count}개 성공")
    
    if success_count == len(results):
        print("🎉 모든 실제 폰트 테스트 통과!")
    else:
        print("⚠️ 일부 테스트 실패")
    
    return success_count == len(results)

if __name__ == "__main__":
    # 개별 테스트 실행
    # test_real_korean_fonts()
    # test_real_korean_text()
    # test_font_scaling()
    # test_center_alignment()
    # test_font_comparison()
    
    # 모든 테스트 실행
    run_all_real_font_tests()


