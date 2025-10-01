"""
mpremote를 사용하여 ESP32 보드에 파일을 업로드하는 스크립트

업로드 규칙:
- src 폴더의 .py 파일들 → ESP32 루트(/)
- src/screens 폴더의 파일들 → ESP32 /screens/
- src/wav 폴더는 제외 (업로드하지 않음)
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# 업로드할 디렉토리 설정
SRC_DIR = "src"
SCREENS_DIR = "src/screens"
EXCLUDE_DIRS = ["wav", "docs", "__pycache__"]  # 제외할 디렉토리

def get_files_to_upload():
    """업로드할 파일 목록 가져오기"""
    src_files = []  # src 루트의 .py 파일들
    screen_files = []  # src/screens 폴더의 파일들
    
    # src 폴더의 .py 파일들 (하위 디렉토리 제외)
    src_path = Path(SRC_DIR)
    if src_path.exists():
        for file in src_path.glob("*.py"):
            src_files.append(file)
    
    # src/screens 폴더의 모든 파일들
    screens_path = Path(SCREENS_DIR)
    if screens_path.exists():
        for file in screens_path.glob("*.py"):
            screen_files.append(file)
    
    return src_files, screen_files

def find_serial_port():
    """사용 가능한 시리얼 포트 찾기"""
    import serial.tools.list_ports
    
    ports = list(serial.tools.list_ports.comports())
    
    print("사용 가능한 시리얼 포트:")
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port.device} - {port.description}")
    
    if not ports:
        print("시리얼 포트를 찾을 수 없습니다")
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
    print(f"디렉토리 생성: {dir_path}")
    return run_mpremote_command(port, f'fs mkdir :{dir_path}')

def upload_file(port, local_path, remote_path, current=None, total=None):
    """파일 업로드"""
    if not os.path.exists(local_path):
        print(f"파일 없음: {local_path}")
        return False
    
    # 진행 상황 표시
    if current is not None and total is not None:
        progress = f"[{current}/{total}]"
        file_size = os.path.getsize(local_path)
        size_kb = file_size / 1024
        print(f"{progress} 업로드 중: {os.path.basename(local_path)} ({size_kb:.1f} KB) -> {remote_path}")
    else:
        print(f"업로드: {local_path} -> {remote_path}")
    
    # mpremote fs cp 명령 사용
    return run_mpremote_command(port, f'fs cp "{local_path}" :{remote_path}', show_progress=False)

def show_upload_plan():
    """업로드 계획 표시"""
    src_files, screen_files = get_files_to_upload()
    
    print("\n업로드 계획:")
    print("-" * 60)
    
    print(f"\n[ESP32 루트 /] - {len(src_files)}개 파일")
    for file in sorted(src_files):
        print(f"  - {file.name}")
    
    print(f"\n[ESP32 /screens/] - {len(screen_files)}개 파일")
    for file in sorted(screen_files):
        print(f"  - {file.name}")
    
    print(f"\n[제외] - src/wav, src/docs, src/__pycache__")
    print("-" * 60)
    
    return src_files, screen_files

def get_esp32_files(port):
    """ESP32의 파일 목록 가져오기"""
    files = {"root": [], "screens": []}
    
    # 루트 디렉토리 파일 목록
    try:
        cmd = f"mpremote connect {port} fs ls /"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if line and '.py' in line:
                    # "ls :/" 출력 형식 처리
                    parts = line.split()
                    if parts:
                        filename = parts[-1]  # 마지막 부분이 파일명
                        if filename.endswith('.py') and '/' not in filename:
                            files["root"].append(filename)
    except Exception:
        pass
    
    # screens 디렉토리 파일 목록
    try:
        cmd_screens = f"mpremote connect {port} fs ls /screens"
        result_screens = subprocess.run(
            cmd_screens,
            shell=True,
            capture_output=True,
            text=True
        )
        if result_screens.stdout:
            for line in result_screens.stdout.strip().split('\n'):
                line = line.strip()
                if line and '.py' in line:
                    parts = line.split()
                    if parts:
                        filename = parts[-1]
                        if filename.endswith('.py'):
                            # /screens/파일명 형태에서 파일명만 추출
                            filename = filename.split('/')[-1]
                            files["screens"].append(filename)
    except Exception:
        pass
    
    return files

def compare_files(local_src_files, local_screen_files, esp32_files):
    """로컬 파일과 ESP32 파일 비교"""
    missing_src = []
    missing_screens = []
    
    # src 루트 파일 비교
    for file in local_src_files:
        if file.name not in esp32_files["root"]:
            missing_src.append(file)
    
    # screens 파일 비교
    for file in local_screen_files:
        if file.name not in esp32_files["screens"]:
            missing_screens.append(file)
    
    return missing_src, missing_screens

def list_files(port):
    """보드의 파일 목록 확인"""
    print("\n보드의 파일 목록:")
    print("-" * 60)
    cmd = f"mpremote connect {port} fs ls /"
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        
        # screens 폴더도 확인
        print("\n/screens 폴더:")
        cmd_screens = f"mpremote connect {port} fs ls /screens"
        result_screens = subprocess.run(
            cmd_screens,
            shell=True,
            capture_output=True,
            text=True
        )
        if result_screens.stdout:
            print(result_screens.stdout)
        else:
            print("  (비어있음)")
    except Exception as e:
        print(f"파일 목록 가져오기 실패: {e}")

def main():
    """메인 함수"""
    print("=" * 60)
    print("ESP32 파일 업로드 스크립트 (mpremote 사용)")
    print("=" * 60)
    
    # mpremote 설치 확인
    mpremote_installed = False
    
    # 명령줄에서 실행 확인
    try:
        result = subprocess.run(
            "mpremote --help",
            shell=True,
            capture_output=True
        )
        if result.returncode == 0 or b"usage" in result.stdout.lower() or b"usage" in result.stderr.lower():
            mpremote_installed = True
            print("mpremote 확인됨")
    except Exception:
        pass
    
    if not mpremote_installed:
        print("\nmpremote가 설치되어 있지 않거나 실행할 수 없습니다.")
        print("설치 명령: pip install mpremote")
        print("\n설치 후에도 문제가 있다면 다음을 확인하세요:")
        print("  1. pip list | findstr mpremote  <- mpremote 설치 확인")
        print("  2. Python Scripts 폴더가 PATH에 있는지 확인")
        return
    
    # 업로드 계획 표시
    src_files, screen_files = show_upload_plan()
    
    if not src_files and not screen_files:
        print("\n업로드할 파일이 없습니다.")
        return
    
    # 시리얼 포트 찾기
    port = find_serial_port()
    if not port:
        return
    
    print(f"\n선택된 포트: {port}")
    print("=" * 60)
    
    # 업로드 옵션 선택
    print("\n업로드 옵션:")
    print("  1. 전체 업로드 (src 루트 + screens)")
    print("  2. src 루트 파일만 업로드")
    print("  3. screens 폴더만 업로드")
    print("  4. 개별 파일 선택")
    print("  5. ESP32에 없는 파일만 업로드 (누락된 파일)")
    
    choice = input("\n선택 (1-5, Enter=1): ").strip()
    if choice == "":
        choice = "1"
    
    upload_count = 0
    
    if choice == "1":
        # 전체 업로드
        total_files = len(src_files) + len(screen_files)
        current_file = 0
        
        print(f"\n전체 파일 업로드 시작... (총 {total_files}개)")
        
        # screens 디렉토리 생성
        if screen_files:
            create_directory(port, "/screens")
            time.sleep(0.5)
        
        # src 루트 파일들 업로드
        print(f"\n[1단계] src 루트 파일 업로드")
        print("-" * 60)
        for file in src_files:
            current_file += 1
            if upload_file(port, str(file), f"/{file.name}", current_file, total_files):
                upload_count += 1
            time.sleep(0.2)
        
        # screens 파일들 업로드
        print(f"\n[2단계] screens 폴더 파일 업로드")
        print("-" * 60)
        for file in screen_files:
            current_file += 1
            if upload_file(port, str(file), f"/screens/{file.name}", current_file, total_files):
                upload_count += 1
            time.sleep(0.2)
    
    elif choice == "2":
        # src 루트만
        total_files = len(src_files)
        print(f"\nsrc 루트 파일 업로드 (총 {total_files}개)")
        print("-" * 60)
        for idx, file in enumerate(src_files, 1):
            if upload_file(port, str(file), f"/{file.name}", idx, total_files):
                upload_count += 1
            time.sleep(0.2)
    
    elif choice == "3":
        # screens만
        create_directory(port, "/screens")
        time.sleep(0.5)
        
        total_files = len(screen_files)
        print(f"\nscreens 폴더 파일 업로드 (총 {total_files}개)")
        print("-" * 60)
        for idx, file in enumerate(screen_files, 1):
            if upload_file(port, str(file), f"/screens/{file.name}", idx, total_files):
                upload_count += 1
            time.sleep(0.2)
    
    elif choice == "4":
        # 개별 파일 선택
        all_files = list(src_files) + list(screen_files)
        print("\n업로드할 파일 선택:")
        for i, file in enumerate(all_files):
            location = "/" if file in src_files else "/screens/"
            file_size = os.path.getsize(str(file))
            size_kb = file_size / 1024
            print(f"  {i+1}. {file.name} ({size_kb:.1f} KB) -> {location}")
        
        selections = input("\n파일 번호 입력 (쉼표로 구분, 예: 1,2,3): ").strip()
        if selections:
            try:
                # screens 디렉토리가 필요한지 확인
                need_screens = False
                indices = [int(x.strip()) - 1 for x in selections.split(",")]
                selected_files = []
                
                for idx in indices:
                    if 0 <= idx < len(all_files):
                        selected_files.append(all_files[idx])
                        if all_files[idx] in screen_files:
                            need_screens = True
                
                if need_screens:
                    create_directory(port, "/screens")
                    time.sleep(0.5)
                
                # 파일 업로드
                total_files = len(selected_files)
                print(f"\n선택한 파일 업로드 (총 {total_files}개)")
                print("-" * 60)
                
                for current, file in enumerate(selected_files, 1):
                    if file in src_files:
                        if upload_file(port, str(file), f"/{file.name}", current, total_files):
                            upload_count += 1
                    else:
                        if upload_file(port, str(file), f"/screens/{file.name}", current, total_files):
                            upload_count += 1
                    time.sleep(0.2)
            except ValueError:
                print("올바른 형식이 아닙니다")
    
    elif choice == "5":
        # ESP32에 없는 파일만 업로드
        print("\nESP32 파일 목록 확인 중...")
        esp32_files = get_esp32_files(port)
        
        print(f"ESP32 루트: {len(esp32_files['root'])}개 파일")
        print(f"ESP32 /screens: {len(esp32_files['screens'])}개 파일")
        
        # 누락된 파일 찾기
        missing_src, missing_screens = compare_files(src_files, screen_files, esp32_files)
        
        if not missing_src and not missing_screens:
            print("\n모든 파일이 ESP32에 있습니다. 업로드할 파일이 없습니다.")
        else:
            print("\n누락된 파일:")
            print("-" * 60)
            
            if missing_src:
                print(f"\n[루트 /] - {len(missing_src)}개 누락")
                for file in missing_src:
                    file_size = os.path.getsize(str(file))
                    size_kb = file_size / 1024
                    print(f"  - {file.name} ({size_kb:.1f} KB)")
            
            if missing_screens:
                print(f"\n[/screens/] - {len(missing_screens)}개 누락")
                for file in missing_screens:
                    file_size = os.path.getsize(str(file))
                    size_kb = file_size / 1024
                    print(f"  - {file.name} ({size_kb:.1f} KB)")
            
            # 업로드 확인
            confirm = input("\n누락된 파일을 업로드하시겠습니까? (y/N): ").strip().lower()
            if confirm == 'y':
                total_files = len(missing_src) + len(missing_screens)
                current_file = 0
                
                print(f"\n누락된 파일 업로드 시작... (총 {total_files}개)")
                
                # screens 디렉토리가 필요한 경우 생성
                if missing_screens:
                    create_directory(port, "/screens")
                    time.sleep(0.5)
                
                # 누락된 src 파일 업로드
                if missing_src:
                    print(f"\n[1단계] src 루트 파일 업로드")
                    print("-" * 60)
                    for file in missing_src:
                        current_file += 1
                        if upload_file(port, str(file), f"/{file.name}", current_file, total_files):
                            upload_count += 1
                        time.sleep(0.2)
                
                # 누락된 screens 파일 업로드
                if missing_screens:
                    print(f"\n[2단계] screens 폴더 파일 업로드")
                    print("-" * 60)
                    for file in missing_screens:
                        current_file += 1
                        if upload_file(port, str(file), f"/screens/{file.name}", current_file, total_files):
                            upload_count += 1
                        time.sleep(0.2)
            else:
                print("업로드를 취소했습니다.")
    
    # 업로드 완료 후 파일 목록 확인
    print(f"\n업로드 완료: {upload_count}개 파일")
    
    list_choice = input("\n업로드된 파일 목록을 확인하시겠습니까? (y/N): ").strip().lower()
    if list_choice == 'y':
        list_files(port)
    
    print("\n" + "=" * 60)
    print("업로드 완료")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n중단되었습니다")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()

