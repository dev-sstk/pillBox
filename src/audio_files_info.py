"""
오디오 파일 정보 관리
필박스에서 사용하는 모든 오디오 파일의 정보를 관리
"""

class AudioFilesInfo:
    """오디오 파일 정보 클래스"""
    
    def __init__(self):
        """오디오 파일 정보 초기화"""
        self.audio_files = {
            # 효과음 파일들
            "wav_select.wav": {
                "description": "선택 효과음",
                "duration": 200,
                "category": "effect",
                "priority": "medium"
            },
            "wav_alarm.wav": {
                "description": "알림 효과음",
                "duration": 1000,
                "category": "effect",
                "priority": "high"
            },
            "wav_adjust.wav": {
                "description": "조정 효과음",
                "duration": 150,
                "category": "effect",
                "priority": "low"
            },
            
            # 음성 파일들 (안내 멘트)
            "wav_startup_hello.wav": {
                "description": "시작 안내 음성",
                "duration": 3000,
                "category": "voice",
                "priority": "high"
            },
            "wav_wifi_scan_prompt.wav": {
                "description": "Wi-Fi 스캔 안내 음성",
                "duration": 2500,
                "category": "voice",
                "priority": "high"
            },
            "wav_wifi_password_prompt.wav": {
                "description": "Wi-Fi 비밀번호 입력 안내 음성",
                "duration": 2800,
                "category": "voice",
                "priority": "high"
            },
            "wav_dose_count_prompt.wav": {
                "description": "복용량 설정 안내 음성",
                "duration": 2200,
                "category": "voice",
                "priority": "high"
            },
            "wav_dose_time_prompt.wav": {
                "description": "복용 시간 설정 안내 음성",
                "duration": 2400,
                "category": "voice",
                "priority": "high"
            },
            "wav_main_screen.wav": {
                "description": "메인 화면 안내 음성",
                "duration": 2000,
                "category": "voice",
                "priority": "medium"
            },
            "wav_take_pill_prompt.wav": {
                "description": "복용 알림 안내 음성",
                "duration": 3500,
                "category": "voice",
                "priority": "high"
            },
            "wav_settings_prompt.wav": {
                "description": "설정 화면 안내 음성",
                "duration": 1800,
                "category": "voice",
                "priority": "medium"
            },
            "wav_pill_loading_prompt.wav": {
                "description": "알약 로딩 안내 음성",
                "duration": 2600,
                "category": "voice",
                "priority": "medium"
            },
            "wav_pill_dispense_prompt.wav": {
                "description": "알약 배출 안내 음성",
                "duration": 2200,
                "category": "voice",
                "priority": "medium"
            },
            "wav_success.wav": {
                "description": "성공 효과음",
                "duration": 800,
                "category": "effect",
                "priority": "high"
            },
            "wav_error.wav": {
                "description": "오류 효과음",
                "duration": 1200,
                "category": "effect",
                "priority": "high"
            },
            "wav_button_click.wav": {
                "description": "버튼 클릭 효과음",
                "duration": 100,
                "category": "effect",
                "priority": "low"
            },
            "take_medicine.wav": {
                "description": "복용 안내 음성",
                "duration": 3000,
                "category": "voice",
                "priority": "high"
            }
        }
        
        # 오디오 파일 디렉토리 구조
        self.audio_directories = {
            "voice": "/wav/",
            "effect": "/wav/",
            "alarm": "/wav/",
            "system": "/wav/"
        }
        
        print("[OK] AudioFilesInfo 초기화 완료")
    
    def get_file_info(self, filename):
        """특정 오디오 파일 정보 반환"""
        return self.audio_files.get(filename)
    
    def get_file_description(self, filename):
        """파일 설명 반환"""
        info = self.get_file_info(filename)
        return info["description"] if info else "알 수 없는 파일"
    
    def get_file_duration(self, filename):
        """파일 재생 시간 반환 (ms)"""
        info = self.get_file_info(filename)
        return info["duration"] if info else 1000
    
    def get_file_category(self, filename):
        """파일 카테고리 반환"""
        info = self.get_file_info(filename)
        return info["category"] if info else "effect"
    
    def get_file_priority(self, filename):
        """파일 우선순위 반환"""
        info = self.get_file_info(filename)
        return info["priority"] if info else "low"
    
    def is_voice_file(self, filename):
        """음성 파일인지 확인"""
        return self.get_file_category(filename) == "voice"
    
    def is_effect_file(self, filename):
        """효과음 파일인지 확인"""
        return self.get_file_category(filename) == "effect"
    
    def get_voice_files(self):
        """음성 파일 목록 반환"""
        return [filename for filename, info in self.audio_files.items() 
                if info["category"] == "voice"]
    
    def get_effect_files(self):
        """효과음 파일 목록 반환"""
        return [filename for filename, info in self.audio_files.items() 
                if info["category"] == "effect"]
    
    def get_files_by_priority(self, priority):
        """우선순위별 파일 목록 반환"""
        return [filename for filename, info in self.audio_files.items() 
                if info["priority"] == priority]
    
    def get_total_duration(self, filenames):
        """여러 파일의 총 재생 시간 반환 (ms)"""
        total = 0
        for filename in filenames:
            info = self.get_file_info(filename)
            if info:
                total += info["duration"]
        return total
    
    def get_directory_path(self, filename):
        """파일의 디렉토리 경로 반환"""
        info = self.get_file_info(filename)
        if info:
            category = info["category"]
            return self.audio_directories.get(category, "/wav/")
        return "/wav/"
    
    def get_full_path(self, filename):
        """파일의 전체 경로 반환"""
        directory = self.get_directory_path(filename)
        return directory + filename
    
    def list_all_files(self):
        """모든 오디오 파일 목록 반환"""
        return list(self.audio_files.keys())
    
    def get_file_count(self):
        """총 오디오 파일 개수 반환"""
        return len(self.audio_files)
    
    def get_voice_file_count(self):
        """음성 파일 개수 반환"""
        return len(self.get_voice_files())
    
    def get_effect_file_count(self):
        """효과음 파일 개수 반환"""
        return len(self.get_effect_files())
    
    def get_high_priority_files(self):
        """높은 우선순위 파일 목록 반환"""
        return self.get_files_by_priority("high")
    
    def get_medium_priority_files(self):
        """중간 우선순위 파일 목록 반환"""
        return self.get_files_by_priority("medium")
    
    def get_low_priority_files(self):
        """낮은 우선순위 파일 목록 반환"""
        return self.get_files_by_priority("low")
    
    def print_file_info(self, filename):
        """파일 정보 출력"""
        info = self.get_file_info(filename)
        if info:
            print(f"파일: {filename}")
            print(f"설명: {info['description']}")
            print(f"재생시간: {info['duration']}ms")
            print(f"카테고리: {info['category']}")
            print(f"우선순위: {info['priority']}")
            print(f"전체경로: {self.get_full_path(filename)}")
        else:
            print(f"파일을 찾을 수 없습니다: {filename}")
    
    def print_all_files(self):
        """모든 파일 정보 출력"""
        print("=== 모든 오디오 파일 정보 ===")
        for filename in self.list_all_files():
            self.print_file_info(filename)
            print("-" * 40)
    
    def print_summary(self):
        """요약 정보 출력"""
        print("=== 오디오 파일 요약 ===")
        print(f"총 파일 수: {self.get_file_count()}")
        print(f"음성 파일: {self.get_voice_file_count()}")
        print(f"효과음 파일: {self.get_effect_file_count()}")
        print(f"높은 우선순위: {len(self.get_high_priority_files())}")
        print(f"중간 우선순위: {len(self.get_medium_priority_files())}")
        print(f"낮은 우선순위: {len(self.get_low_priority_files())}")
        
        print("\n=== 디렉토리 구조 ===")
        for category, path in self.audio_directories.items():
            print(f"{category}: {path}")

# 전역 인스턴스 (지연 초기화)
audio_files_info = None

def get_audio_files_info():
    """오디오 파일 정보 인스턴스 반환 (지연 초기화)"""
    global audio_files_info
    if audio_files_info is None:
        audio_files_info = AudioFilesInfo()
    return audio_files_info