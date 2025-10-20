"""
mpy 빌드 후 mpremote로 ESP32에 업로드하는 스크립트

기능:
1. Python 파일을 mpy로 컴파일 (boot.py, main.py 제외)
2. boot.py와 main.py는 .py 파일로 직접 업로드 (자동 실행용)
3. mpremote를 사용하여 ESP32에 업로드
4. ESP32 파일 목록 확인
5. ESP32 파일 전체 삭제
6. 디스크 상태 초기화 (disk_states.json 업로드)
7. 오디오 파일 업로드 (dispense_medicine.wav, take_medicine.wav)
8. 기존 upload_to_esp32.py의 모든 기능 포함
"""

import os
import sys
import subprocess
import time
import shutil
from pathlib import Path

# mpy-cross 경로 (시스템 PATH에 있거나 현재 디렉토리에 있어야 함)
MPY_CROSS = "mpy-cross"

# 업로드할 디렉토리 설정
SRC_DIR = "src"
SCREENS_DIR = "src/screens"
BUILD_DIR = "build"
EXCLUDE_DIRS = ["wav", "docs", "__pycache__"]

def check_mpy_cross():
    """mpy-cross 설치 확인"""
    try:
        result = subprocess.run(
            f"{MPY_CROSS} --help",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0 or "usage" in result.stdout.lower() or "usage" in result.stderr.lower():
            print("✅ mpy-cross 확인됨")
            return True
    except Exception:
        pass
    
    print("❌ mpy-cross를 찾을 수 없습니다.")
    print("설치 방법:")
    print("  1. pip install mpy-cross")
    print("  2. 또는 MicroPython 공식 저장소에서 다운로드")
    print("  3. 또는 현재 디렉토리에 mpy-cross 실행 파일 배치")
    return False

def check_mpremote():
    """mpremote 설치 확인"""
    try:
        result = subprocess.run(
            "mpremote --help",
            shell=True,
            capture_output=True
        )
        if result.returncode == 0 or b"usage" in result.stdout.lower() or b"usage" in result.stderr.lower():
            print("✅ mpremote 확인됨")
            return True
    except Exception:
        pass
    
    print("❌ mpremote가 설치되어 있지 않습니다.")
    print("설치 명령: pip install mpremote")
    return False

def create_build_directory():
    """빌드 디렉토리 생성"""
    build_path = Path(BUILD_DIR)
    
    # 기존 디렉토리가 있으면 안전하게 정리
    if build_path.exists():
        print(f"🧹 기존 빌드 디렉토리 정리: {BUILD_DIR}")
        try:
            shutil.rmtree(build_path)
        except (PermissionError, OSError):
            # 권한 오류나 파일 사용 중 오류는 무시하고 계속 진행
            print(f"⚠️  기존 디렉토리 정리 실패 (계속 진행)")
    
    # 빌드 디렉토리 생성
    try:
        build_path.mkdir(exist_ok=True)
        (build_path / "screens").mkdir(exist_ok=True)
        print(f"📁 빌드 디렉토리 생성: {BUILD_DIR}")
    except Exception as e:
        print(f"❌ 빌드 디렉토리 생성 실패: {e}")
        raise
    
    return build_path

def compile_py_to_mpy(py_file, output_dir):
    """Python 파일을 mpy로 컴파일"""
    try:
        py_path = Path(py_file)
        mpy_name = py_path.stem + ".mpy"
        mpy_path = output_dir / mpy_name
        
        print(f"🔨 컴파일: {py_path.name} -> {mpy_name}")
        
        cmd = f'{MPY_CROSS} -o "{mpy_path}" "{py_path}"'
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            file_size = mpy_path.stat().st_size
            size_kb = file_size / 1024
            print(f"  ✅ 성공 ({size_kb:.1f} KB)")
            return True
        else:
            print(f"  ❌ 실패: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ❌ 예외 발생: {e}")
        return False

def get_files_to_build():
    """빌드할 파일 목록 가져오기"""
    src_files = []  # src 루트의 .py 파일들
    screen_files = []  # src/screens 폴더의 파일들
    
    # src 폴더의 .py 파일들 (하위 디렉토리 제외)
    src_path = Path(SRC_DIR)
    if src_path.exists():
        for file in src_path.glob("*.py"):
            # boot.py와 main.py는 자동 실행을 위해 .py 파일로 유지
            if file.name not in ["boot.py", "main.py"]:
                src_files.append(file)
    
    # src/screens 폴더의 모든 파일들
    screens_path = Path(SCREENS_DIR)
    if screens_path.exists():
        for file in screens_path.glob("*.py"):
            screen_files.append(file)
    
    return src_files, screen_files

def build_all_files():
    """모든 파일을 mpy로 빌드"""
    print("\n" + "=" * 60)
    print("MPY 빌드 시작")
    print("=" * 60)
    
    # 기존 빌드 디렉토리 정리
    print("🧹 기존 빌드 디렉토리 정리 중...")
    cleanup_build_directory()
    
    # 빌드 디렉토리 생성
    build_path = create_build_directory()
    
    # 빌드할 파일 목록 가져오기
    src_files, screen_files = get_files_to_build()
    
    if not src_files and not screen_files:
        print("❌ 빌드할 파일이 없습니다.")
        return None, None
    
    print(f"\n빌드 계획:")
    print(f"  📁 src 루트: {len(src_files)}개 파일")
    print(f"  📁 src/screens: {len(screen_files)}개 파일")
    print(f"  📁 출력: {BUILD_DIR}/")
    
    # 빌드 통계
    total_files = len(src_files) + len(screen_files)
    success_count = 0
    failed_files = []
    
    # src 루트 파일들 빌드
    print(f"\n[1단계] src 루트 파일 빌드")
    print("-" * 40)
    for file in src_files:
        if compile_py_to_mpy(file, build_path):
            success_count += 1
        else:
            failed_files.append(file)
    
    # screens 파일들 빌드
    print(f"\n[2단계] screens 폴더 파일 빌드")
    print("-" * 40)
    for file in screen_files:
        if compile_py_to_mpy(file, build_path / "screens"):
            success_count += 1
        else:
            failed_files.append(file)
    
    # 빌드 결과 요약
    print(f"\n" + "=" * 60)
    print("빌드 완료")
    print("=" * 60)
    print(f"✅ 성공: {success_count}/{total_files}개 파일")
    
    if failed_files:
        print(f"❌ 실패: {len(failed_files)}개 파일")
        for file in failed_files:
            print(f"  - {file.name}")
    
    if success_count == 0:
        print("❌ 빌드된 파일이 없습니다.")
        return None, None
    
    # 빌드된 파일 목록
    built_src_files = list(build_path.glob("*.mpy"))
    built_screen_files = list((build_path / "screens").glob("*.mpy"))
    
    return built_src_files, built_screen_files

def build_individual_file():
    """개별 파일 빌드 후 업로드"""
    print("\n" + "=" * 60)
    print("개별 파일 빌드 후 업로드")
    print("=" * 60)
    
    # 빌드할 파일 목록 가져오기
    src_files, screen_files = get_files_to_build()
    all_files = []
    
    # 파일 목록 구성
    for file in src_files:
        all_files.append(("루트", file))
    for file in screen_files:
        all_files.append(("screens", file))
    
    if not all_files:
        print("❌ 빌드할 파일이 없습니다.")
        return
    
    # 파일 선택 메뉴
    print(f"\n빌드할 파일을 선택하세요:")
    for i, (category, file) in enumerate(all_files, 1):
        print(f"  {i}. [{category}] {file.name}")
    
    try:
        choice = input(f"\n선택 (1-{len(all_files)}, 복수선택 가능: 1,3,5 또는 1-5): ").strip()
        if not choice:
            print("❌ 선택이 취소되었습니다.")
            return
        
        # 선택된 파일 인덱스들 파싱
        selected_indices = []
        
        # 쉼표로 구분된 선택 처리
        if ',' in choice:
            parts = choice.split(',')
            for part in parts:
                part = part.strip()
                if '-' in part:
                    # 범위 선택 (예: 1-5)
                    start, end = map(int, part.split('-'))
                    selected_indices.extend(range(start-1, end))
                else:
                    # 단일 선택
                    selected_indices.append(int(part) - 1)
        elif '-' in choice:
            # 범위 선택 (예: 1-5)
            start, end = map(int, choice.split('-'))
            selected_indices = list(range(start-1, end))
        else:
            # 단일 선택
            selected_indices = [int(choice) - 1]
        
        # 유효성 검사
        valid_indices = []
        for idx in selected_indices:
            if 0 <= idx < len(all_files):
                valid_indices.append(idx)
            else:
                print(f"⚠️ 잘못된 선택: {idx + 1} (범위: 1-{len(all_files)})")
        
        if not valid_indices:
            print("❌ 유효한 선택이 없습니다.")
            return
        
        # 선택된 파일들 표시
        print(f"\n선택된 파일들 ({len(valid_indices)}개):")
        for idx in valid_indices:
            category, file = all_files[idx]
            print(f"  - [{category}] {file.name}")
        
        # 기존 빌드 디렉토리 정리
        print("\n🧹 기존 빌드 디렉토리 정리 중...")
        cleanup_build_directory()
        
        # 빌드 디렉토리 생성
        build_path = create_build_directory()
        
        # 선택된 파일들 빌드
        built_files = []
        for idx in valid_indices:
            category, selected_file = all_files[idx]
            print(f"\n[빌드] {selected_file.name}")
            print("-" * 40)
            
            if category == "루트":
                success = compile_py_to_mpy(selected_file, build_path)
                built_file = build_path / f"{selected_file.stem}.mpy"
                remote_path = f"/{selected_file.stem}.mpy"
            else:  # screens
                success = compile_py_to_mpy(selected_file, build_path / "screens")
                built_file = build_path / "screens" / f"{selected_file.stem}.mpy"
                remote_path = f"/screens/{selected_file.stem}.mpy"
            
            if success:
                print(f"✅ {selected_file.name} 빌드 완료")
                built_files.append((built_file, remote_path, selected_file.name, category))
            else:
                print(f"❌ {selected_file.name} 빌드 실패")
        
        if not built_files:
            print("❌ 빌드된 파일이 없습니다.")
            return
        
        # 시리얼 포트 찾기
        port = find_serial_port()
        if not port:
            return
        
        print(f"\n선택된 포트: {port}")
        
        # screens 디렉토리 생성 (필요한 경우)
        has_screens = any(category == "screens" for _, _, _, category in built_files)
        if has_screens:
            create_directory(port, "/screens")
            time.sleep(0.5)
        
        # 파일들 업로드
        print(f"\n[업로드] {len(built_files)}개 파일")
        print("-" * 40)
        
        success_count = 0
        for built_file, remote_path, file_name, category in built_files:
            print(f"\n[업로드] {file_name}")
            if upload_file(port, str(built_file), remote_path):
                print(f"✅ {file_name} 업로드 완료")
                success_count += 1
            else:
                print(f"❌ {file_name} 업로드 실패")
        
        print(f"\n📊 업로드 결과: {success_count}/{len(built_files)} 성공")
        
        # 빌드 디렉토리 자동 정리
        print("\n🧹 빌드 디렉토리 자동 정리 중...")
        cleanup_build_directory()
        
        print("\n✅ 모든 작업이 완료되었습니다.")
    
    except ValueError:
        print("❌ 잘못된 입력입니다. 숫자를 입력해주세요.")
    except KeyboardInterrupt:
        print("\n❌ 사용자가 취소했습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def find_serial_port():
    """사용 가능한 시리얼 포트 찾기"""
    import serial.tools.list_ports
    
    ports = list(serial.tools.list_ports.comports())
    
    print("\n사용 가능한 시리얼 포트:")
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port.device} - {port.description}")
    
    if not ports:
        print("❌ 시리얼 포트를 찾을 수 없습니다")
        return None
    
    # 사용자 선택
    while True:
        try:
            choice = input(f"\n포트 선택 (1-{len(ports)}) 또는 Enter (1번 선택): ").strip()
            if choice == "":
                choice = "1"
            idx = int(choice) - 1
            if 0 <= idx < len(ports):
                return ports[idx].device
            else:
                print(f"1부터 {len(ports)} 사이의 숫자를 입력하세요")
        except ValueError:
            print("올바른 숫자를 입력하세요")
        except KeyboardInterrupt:
            print("\n중단되었습니다")
            return None

def run_mpremote_command(port, command, retry=3, show_progress=True):
    """mpremote 명령 실행"""
    cmd = f"mpremote connect {port} {command}"
    
    for attempt in range(retry):
        try:
            if show_progress:
                print(f"실행: {command}")
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.lower() if e.stderr else ""
            if "exists" in error_msg or "oserror" in error_msg:
                # 이미 존재하는 경우는 무시
                return True
            print(f"오류 발생: {e.stderr}")
            if attempt < retry - 1:
                print(f"재시도 중... ({attempt + 1}/{retry})")
                time.sleep(1)
            else:
                print(f"실패: {command}")
                return False
        except Exception as e:
            print(f"예외 발생: {e}")
            return False
    
    return False

def create_directory(port, dir_path):
    """보드에 디렉토리 생성"""
    print(f"📁 디렉토리 생성: {dir_path}")
    return run_mpremote_command(port, f'fs mkdir :{dir_path}')

def upload_file(port, local_path, remote_path, current=None, total=None):
    """파일 업로드"""
    if not os.path.exists(local_path):
        print(f"❌ 파일 없음: {local_path}")
        return False
    
    # 진행 상황 표시
    if current is not None and total is not None:
        progress = f"[{current}/{total}]"
        file_size = os.path.getsize(local_path)
        size_kb = file_size / 1024
        print(f"{progress} 📤 업로드: {os.path.basename(local_path)} ({size_kb:.1f} KB) -> {remote_path}")
    else:
        print(f"📤 업로드: {local_path} -> {remote_path}")
    
    # mpremote fs cp 명령 사용
    return run_mpremote_command(port, f'fs cp "{local_path}" :{remote_path}', show_progress=False)

def upload_built_files(port, built_src_files, built_screen_files):
    """빌드된 파일들을 ESP32에 업로드"""
    print("\n" + "=" * 60)
    print("ESP32 업로드 시작")
    print("=" * 60)
    
    upload_count = 0
    total_files = len(built_src_files) + len(built_screen_files)
    current_file = 0
    
    # boot.py와 main.py 파일 추가 (자동 실행을 위해 .py 파일로 업로드)
    boot_file = Path(SRC_DIR) / "boot.py"
    main_file = Path(SRC_DIR) / "main.py"
    
    py_files_count = 0
    if boot_file.exists():
        py_files_count += 1
    if main_file.exists():
        py_files_count += 1
    
    if py_files_count > 0:
        total_files += py_files_count
        print(f"📤 업로드 계획: {total_files}개 파일 (boot.py, main.py 포함)")
    else:
        print(f"📤 업로드 계획: {total_files}개 파일")
    
    print(f"  📁 루트: {len(built_src_files)}개")
    print(f"  📁 /screens: {len(built_screen_files)}개")
    if boot_file.exists():
        print(f"  📁 boot.py: 1개 (자동 실행용)")
    if main_file.exists():
        print(f"  📁 main.py: 1개 (자동 실행용)")
    
    # screens 디렉토리 생성
    if built_screen_files:
        create_directory(port, "/screens")
        time.sleep(0.5)
    
    # boot.py와 main.py 먼저 업로드 (자동 실행을 위해)
    if boot_file.exists():
        print(f"\n[0단계] boot.py 업로드 (자동 실행용)")
        print("-" * 40)
        current_file += 1
        if upload_file(port, str(boot_file), "/boot.py", current_file, total_files):
            upload_count += 1
            print("  ✅ boot.py 업로드 완료 (자동 실행 가능)")
        time.sleep(0.2)
    
    if main_file.exists():
        print(f"\n[0.5단계] main.py 업로드 (자동 실행용)")
        print("-" * 40)
        current_file += 1
        if upload_file(port, str(main_file), "/main.py", current_file, total_files):
            upload_count += 1
            print("  ✅ main.py 업로드 완료 (자동 실행 가능)")
        time.sleep(0.2)
    
    # src 루트 파일들 업로드
    if built_src_files:
        print(f"\n[1단계] 루트 파일 업로드")
        print("-" * 40)
        for file in built_src_files:
            current_file += 1
            if upload_file(port, str(file), f"/{file.name}", current_file, total_files):
                upload_count += 1
            time.sleep(0.2)
    
    # screens 파일들 업로드
    if built_screen_files:
        print(f"\n[2단계] screens 폴더 파일 업로드")
        print("-" * 40)
        for file in built_screen_files:
            current_file += 1
            if upload_file(port, str(file), f"/screens/{file.name}", current_file, total_files):
                upload_count += 1
            time.sleep(0.2)
    
    return upload_count

def list_esp32_files(port):
    """ESP32의 파일 목록 확인"""
    print("\n📋 ESP32 파일 목록:")
    print("-" * 60)
    
    # 루트 디렉토리
    cmd = f"mpremote connect {port} fs ls /"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print("📁 루트 (/):")
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if line and ('.py' in line or '.mpy' in line):
                    # 파일 크기가 앞에 있는 경우 파싱 (예: "9795 audio_files_info.py")
                    parts = line.split(' ', 1)
                    if len(parts) == 2 and parts[0].isdigit():
                        # 파일 크기 + 파일명 형식
                        size = parts[0]
                        filename = parts[1]
                        print(f"  {filename} ({size} bytes)")
                    else:
                        # 파일명만 있는 형식
                        print(f"  {line}")
    except Exception as e:
        print(f"  오류: {e}")
    
    # screens 디렉토리
    cmd_screens = f"mpremote connect {port} fs ls /screens"
    try:
        result_screens = subprocess.run(cmd_screens, shell=True, capture_output=True, text=True)
        print("\n📁 /screens:")
        if result_screens.stdout:
            for line in result_screens.stdout.strip().split('\n'):
                line = line.strip()
                if line and ('.py' in line or '.mpy' in line):
                    # 파일 크기가 앞에 있는 경우 파싱 (예: "7841 base_screen.py")
                    parts = line.split(' ', 1)
                    if len(parts) == 2 and parts[0].isdigit():
                        # 파일 크기 + 파일명 형식
                        size = parts[0]
                        filename = parts[1]
                        print(f"  {filename} ({size} bytes)")
                    else:
                        # 파일명만 있는 형식
                        print(f"  {line}")
        else:
            print("  (비어있음)")
    except Exception as e:
        print(f"  오류: {e}")

def delete_esp32_file(port, file_path):
    """ESP32에서 파일 삭제"""
    print(f"🗑️  삭제: {file_path}")
    return run_mpremote_command(port, f'fs rm :{file_path}', show_progress=False)

def delete_esp32_directory(port, dir_path):
    """ESP32에서 디렉토리 삭제 (재귀적)"""
    print(f"🗑️  디렉토리 삭제: {dir_path}")
    return run_mpremote_command(port, f'fs rmdir :{dir_path}', show_progress=False)

def get_esp32_files_list(port):
    """ESP32의 모든 파일 목록을 가져오기"""
    files = []
    
    # 루트 디렉토리 파일들
    cmd = f"mpremote connect {port} fs ls /"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if line and ('.py' in line or '.mpy' in line):
                    # 파일 크기가 앞에 있는 경우 파싱 (예: "9795 audio_files_info.py")
                    parts = line.split(' ', 1)
                    if len(parts) == 2 and parts[0].isdigit():
                        # 파일 크기 + 파일명 형식
                        filename = parts[1]
                    else:
                        # 파일명만 있는 형식
                        filename = line
                    files.append(f"/{filename}")
    except Exception as e:
        print(f"  루트 디렉토리 스캔 오류: {e}")
    
    # screens 디렉토리 파일들
    cmd_screens = f"mpremote connect {port} fs ls /screens"
    try:
        result_screens = subprocess.run(cmd_screens, shell=True, capture_output=True, text=True)
        if result_screens.stdout:
            for line in result_screens.stdout.strip().split('\n'):
                line = line.strip()
                if line and ('.py' in line or '.mpy' in line):
                    # 파일 크기가 앞에 있는 경우 파싱 (예: "7841 base_screen.py")
                    parts = line.split(' ', 1)
                    if len(parts) == 2 and parts[0].isdigit():
                        # 파일 크기 + 파일명 형식
                        filename = parts[1]
                    else:
                        # 파일명만 있는 형식
                        filename = line
                    files.append(f"/screens/{filename}")
    except Exception as e:
        print(f"  screens 디렉토리 스캔 오류: {e}")
    
    return files

def delete_all_esp32_files(port):
    """ESP32의 모든 파일 삭제"""
    print("\n" + "=" * 60)
    print("ESP32 파일 전체 삭제")
    print("=" * 60)
    
    # 현재 파일 목록 확인
    print("📋 현재 ESP32 파일 목록:")
    files = get_esp32_files_list(port)
    
    if not files:
        print("✅ 삭제할 파일이 없습니다.")
        return True
    
    print(f"발견된 파일: {len(files)}개")
    for file in files:
        print(f"  - {file}")
    
    # 삭제 확인
    print(f"\n⚠️  경고: ESP32의 모든 파일이 삭제됩니다!")
    confirm = input("정말로 모든 파일을 삭제하시겠습니까? (yes 입력): ").strip().lower()
    
    if confirm != "yes":
        print("❌ 삭제가 취소되었습니다.")
        return False
    
    # 파일 삭제 실행
    print(f"\n🗑️  파일 삭제 시작...")
    deleted_count = 0
    failed_files = []
    
    for file in files:
        if delete_esp32_file(port, file):
            deleted_count += 1
            time.sleep(0.1)  # 삭제 간격
        else:
            failed_files.append(file)
    
    # screens 디렉토리 삭제 (파일이 모두 삭제된 후)
    if files and any('/screens/' in f for f in files):
        print(f"\n🗑️  screens 디렉토리 삭제...")
        delete_esp32_directory(port, "/screens")
        time.sleep(0.5)
    
    # 결과 출력
    print(f"\n" + "=" * 60)
    print("삭제 완료")
    print("=" * 60)
    print(f"✅ 삭제된 파일: {deleted_count}개")
    
    if failed_files:
        print(f"❌ 삭제 실패: {len(failed_files)}개")
        for file in failed_files:
            print(f"  - {file}")
    
    # 삭제 후 파일 목록 확인
    print(f"\n📋 삭제 후 ESP32 파일 목록:")
    remaining_files = get_esp32_files_list(port)
    if remaining_files:
        print("남은 파일:")
        for file in remaining_files:
            print(f"  - {file}")
    else:
        print("✅ 모든 파일이 삭제되었습니다.")
    
    return deleted_count > 0

def upload_audio_files(port):
    """오디오 파일들 업로드 (dispense_medicine.wav, take_medicine.wav)"""
    print("\n" + "=" * 60)
    print("오디오 파일 업로드")
    print("=" * 60)
    
    try:
        # 업로드할 오디오 파일들
        audio_files = [
            ("src/wav/dispense_medicine.wav", "/wav/dispense_medicine.wav"),
            ("src/wav/take_medicine.wav", "/wav/take_medicine.wav")
        ]
        
        # wav 디렉토리 생성
        print("📁 /wav 디렉토리 생성 중...")
        if not create_directory(port, "/wav"):
            print("⚠️  /wav 디렉토리 생성 실패 (이미 존재할 수 있음)")
        
        time.sleep(0.5)
        
        # 파일 업로드
        success_count = 0
        for local_path, remote_path in audio_files:
            local_file = Path(local_path)
            
            if not local_file.exists():
                print(f"❌ 파일을 찾을 수 없습니다: {local_path}")
                continue
            
            print(f"\n📤 업로드: {local_file.name} -> {remote_path}")
            
            # 파일 크기 표시
            file_size = local_file.stat().st_size
            size_kb = file_size / 1024
            print(f"  📊 파일 크기: {size_kb:.1f} KB")
            
            # mpremote로 파일 업로드
            if upload_file(port, str(local_file), remote_path):
                print(f"  ✅ {local_file.name} 업로드 완료")
                success_count += 1
            else:
                print(f"  ❌ {local_file.name} 업로드 실패")
            
            time.sleep(0.2)
        
        # 결과 요약
        print(f"\n" + "=" * 60)
        print("오디오 파일 업로드 완료")
        print("=" * 60)
        print(f"✅ 성공: {success_count}/{len(audio_files)}개 파일")
        
        if success_count == len(audio_files):
            print("🎵 모든 오디오 파일이 성공적으로 업로드되었습니다!")
            print("📋 업로드된 파일:")
            for _, remote_path in audio_files:
                print(f"  - {remote_path}")
            return True
        else:
            print("⚠️  일부 파일 업로드에 실패했습니다.")
            return False
            
    except Exception as e:
        print(f"❌ 오디오 파일 업로드 중 오류 발생: {e}")
        return False

def reset_disk_states(port):
    """디스크 상태 초기화 (disk_states.json 업로드)"""
    print("\n" + "=" * 60)
    print("디스크 상태 초기화")
    print("=" * 60)
    
    try:
        # disk_states.json 파일 경로 확인
        disk_states_file = Path("src/data/disk_states.json")
        
        if not disk_states_file.exists():
            print(f"❌ disk_states.json 파일을 찾을 수 없습니다: {disk_states_file}")
            return False
        
        print(f"📁 초기화 파일: {disk_states_file}")
        print(f"🔄 모든 디스크의 충전 상태가 0으로 초기화됩니다.")
        
        # mpremote로 파일 업로드
        print(f"\n📤 disk_states.json 업로드 중...")
        import subprocess
        
        cmd = ["mpremote", "connect", port, "cp", ".\\src\\disk_states.json", "/data/disk_states.json"]
        print(f"실행 명령: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ 디스크 상태 초기화 완료!")
            print(f"📋 업로드된 파일: /data/disk_states.json")
            print(f"🔄 모든 디스크의 충전 상태가 0으로 초기화되었습니다.")
            return True
        else:
            print(f"❌ 디스크 상태 초기화 실패")
            print(f"오류: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ 업로드 시간 초과 (30초)")
        return False
    except Exception as e:
        print(f"❌ 디스크 상태 초기화 중 오류 발생: {e}")
        return False

def cleanup_build_directory():
    """빌드 디렉토리 정리 (안전한 방식)"""
    build_path = Path(BUILD_DIR)
    if not build_path.exists():
        print(f"📁 빌드 디렉토리가 존재하지 않음: {BUILD_DIR}")
        return
    
    print(f"🧹 빌드 디렉토리 정리: {BUILD_DIR}")
    
    try:
        # 먼저 개별 파일들을 삭제 (권한 오류 무시)
        deleted_files = 0
        for file_path in build_path.rglob("*"):
            if file_path.is_file():
                try:
                    file_path.unlink()
                    deleted_files += 1
                except (PermissionError, OSError):
                    # 권한 오류나 파일 사용 중 오류는 무시
                    pass
                except Exception:
                    # 기타 오류도 무시
                    pass
        
        if deleted_files > 0:
            print(f"  🗑️  {deleted_files}개 파일 삭제 완료")
        
        # 빈 디렉토리들을 삭제 (하위 디렉토리부터, 여러 방법 시도)
        deleted_dirs = 0
        
        # 방법 1: 일반적인 rmdir() 시도
        for dir_path in sorted(build_path.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if dir_path.is_dir() and dir_path != build_path:
                try:
                    dir_path.rmdir()
                    deleted_dirs += 1
                except (OSError, PermissionError):
                    # 방법 2: shutil.rmtree()로 강제 삭제 시도
                    try:
                        import shutil
                        shutil.rmtree(dir_path, ignore_errors=True)
                        deleted_dirs += 1
                    except Exception:
                        pass
                except Exception:
                    pass
        
        # 방법 3: 남은 디렉토리들 강제 삭제
        remaining_dirs = []
        for dir_path in build_path.rglob("*"):
            if dir_path.is_dir() and dir_path != build_path:
                remaining_dirs.append(dir_path)
        
        for dir_path in remaining_dirs:
            try:
                import shutil
                shutil.rmtree(dir_path, ignore_errors=True)
                deleted_dirs += 1
            except Exception:
                pass
        
        if deleted_dirs > 0:
            print(f"  🗑️  {deleted_dirs}개 디렉토리 삭제 완료")
        
        # 마지막으로 루트 빌드 디렉토리 삭제 (여러 방법 시도)
        dir_deleted = False
        
        # 방법 1: rmdir() 시도
        try:
            build_path.rmdir()
            dir_deleted = True
            print(f"✅ 빌드 디렉토리 정리 완료: {BUILD_DIR}")
        except (OSError, PermissionError):
            # 방법 2: shutil.rmtree() 시도 (강제 삭제)
            try:
                import shutil
                shutil.rmtree(build_path, ignore_errors=True)
                dir_deleted = True
                print(f"✅ 빌드 디렉토리 강제 정리 완료: {BUILD_DIR}")
            except Exception:
                # 방법 3: 개별 파일과 디렉토리 강제 삭제
                try:
                    for item in build_path.rglob("*"):
                        try:
                            if item.is_file():
                                item.unlink()
                            elif item.is_dir():
                                item.rmdir()
                        except:
                            pass
                    build_path.rmdir()
                    dir_deleted = True
                    print(f"✅ 빌드 디렉토리 개별 정리 완료: {BUILD_DIR}")
                except Exception:
                    pass
        
        if not dir_deleted:
            print(f"⚠️  빌드 디렉토리 일부 정리 완료 (일부 파일 사용 중)")
            
    except Exception:
        print(f"⚠️  빌드 디렉토리 정리 중 일부 오류 발생 (계속 진행)")

def main():
    """메인 함수"""
    print("=" * 60)
    print("ESP32 MPY 빌드 & 업로드 스크립트")
    print("=" * 60)
    
    # 필수 도구 확인
    if not check_mpy_cross():
        return
    
    if not check_mpremote():
        return
    
    # 빌드 옵션 선택
    print("\n빌드 옵션:")
    print("  1. Python 파일을 mpy로 빌드 후 업로드 (권장)")
    print("  2. Python 파일을 그대로 업로드 (기존 방식)")
    print("  3. 빌드만 수행 (업로드 안함)")
    print("  4. 개별 파일 빌드 후 업로드")
    print("  5. ESP32 파일 목록 확인")
    print("  6. ESP32 파일 전체 삭제")
    print("  7. 디스크 상태 초기화 (disk_states.json 업로드)")
    print("  8. 오디오 파일 업로드 (dispense_medicine.wav, take_medicine.wav)")
    
    choice = input("\n선택 (1-8, Enter=1): ").strip()
    if choice == "":
        choice = "1"
    
    if choice in ["1", "3"]:
        # mpy 빌드 수행
        built_src_files, built_screen_files = build_all_files()
        
        if not built_src_files and not built_screen_files:
            print("❌ 빌드할 파일이 없습니다.")
            return
        
        if choice == "3":
            print("\n✅ 빌드만 완료되었습니다.")
            
            # 빌드 디렉토리 자동 정리
            print("\n🧹 빌드 디렉토리 자동 정리 중...")
            cleanup_build_directory()
            
            print("\n✅ 모든 작업이 완료되었습니다.")
            return
    
    if choice == "4":
        # 개별 파일 빌드 후 업로드
        build_individual_file()
        return
    
    if choice in ["1", "2"]:
        # 업로드 수행
        if choice == "1":
            # mpy 파일 업로드
            if not built_src_files and not built_screen_files:
                print("❌ 빌드된 파일이 없습니다.")
                return
        else:
            # Python 파일 직접 업로드 (기존 방식)
            from upload_to_esp32 import get_files_to_upload
            built_src_files, built_screen_files = get_files_to_upload()
            if not built_src_files and not built_screen_files:
                print("❌ 업로드할 파일이 없습니다.")
                return
        
        # 시리얼 포트 찾기
        port = find_serial_port()
        if not port:
            return
        
        print(f"\n선택된 포트: {port}")
        
        # 업로드 실행
        upload_count = upload_built_files(port, built_src_files, built_screen_files)
        
        # 업로드 완료
        print(f"\n" + "=" * 60)
        print("업로드 완료")
        print("=" * 60)
        print(f"✅ 업로드된 파일: {upload_count}개")
        
        # 빌드 디렉토리 자동 정리
        print("\n🧹 빌드 디렉토리 자동 정리 중...")
        cleanup_build_directory()
        
        print("\n✅ 모든 작업이 완료되었습니다.")
    
    elif choice == "5":
        # ESP32 파일 목록 확인
        port = find_serial_port()
        if not port:
            return
        
        print(f"\n선택된 포트: {port}")
        list_esp32_files(port)
    
    elif choice == "6":
        # ESP32 파일 전체 삭제
        port = find_serial_port()
        if not port:
            return
        
        print(f"\n선택된 포트: {port}")
        delete_all_esp32_files(port)
    
    elif choice == "7":
        # 디스크 상태 초기화
        port = find_serial_port()
        if not port:
            return
        
        print(f"\n선택된 포트: {port}")
        reset_disk_states(port)
    
    elif choice == "8":
        # 오디오 파일 업로드
        port = find_serial_port()
        if not port:
            return
        
        print(f"\n선택된 포트: {port}")
        upload_audio_files(port)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n중단되었습니다")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()

