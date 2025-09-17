"""
음성 안내 시스템
안내 멘트와 효과음을 관리하는 시스템
"""

import time
import os
from machine import Pin, I2S
from audio_files_info import audio_files_info

class AudioSystem:
    """음성 안내 시스템 클래스"""
    
    def __init__(self):
        """음성 안내 시스템 초기화"""
        self.audio_enabled = True
        self.volume = 80  # 0-100
        self.current_audio = None
        self.audio_queue = []
        
        # I2S 오디오 설정 (MAX98357A)
        self.i2s = None
        self._init_audio_hardware()
        
        # 오디오 파일 정보 사용
        self.audio_files_info = audio_files_info
        
        print("✅ AudioSystem 초기화 완료")
    
    def _init_audio_hardware(self):
        """오디오 하드웨어 초기화"""
        try:
            # I2S 설정 (MAX98357A) - wav_player_mono.py 설정 사용
            # BCLK: GPIO 6, LRCLK: GPIO 7, DIN: GPIO 5
            self.i2s = I2S(
                0,
                sck=Pin(6),      # Bit Clock
                ws=Pin(7),       # Left/Right Clock  
                sd=Pin(5),       # Data Input
                mode=I2S.TX,
                bits=16,
                format=I2S.MONO,
                rate=16000,
                ibuf=2048
            )
            print("✅ I2S 오디오 하드웨어 초기화 완료")
        except Exception as e:
            print(f"⚠️ I2S 오디오 하드웨어 초기화 실패: {e}")
            self.audio_enabled = False
    
    def play_voice(self, audio_file, blocking=False):
        """안내 음성 재생"""
        if not self.audio_enabled:
            print(f"🔇 오디오 비활성화: {audio_file}")
            return
        
        file_info = self.audio_files_info.get_file_info(audio_file)
        if not file_info:
            print(f"❌ 알 수 없는 오디오 파일: {audio_file}")
            return
        
        print(f"🔊 안내 음성 재생: {file_info['description']}")
        
        if blocking:
            self._play_audio_blocking(audio_file)
        else:
            self._play_audio_async(audio_file)
    
    def play_effect(self, audio_file):
        """효과음 재생"""
        if not self.audio_enabled:
            return
        
        print(f"🔔 효과음 재생: {audio_file}")
        self._play_audio_async(audio_file)
    
    def _play_audio_blocking(self, audio_file):
        """블로킹 방식으로 오디오 재생"""
        try:
            file_path = self.audio_files_info.get_full_path(audio_file)
            if not self._file_exists(file_path):
                print(f"❌ 오디오 파일 없음: {file_path}")
                return
            
            file_info = self.audio_files_info.get_file_info(audio_file)
            duration = file_info["duration"] if file_info else 1000
            
            print(f"🎵 {audio_file} 재생 시작...")
            
            # I2S가 초기화되었는지 확인
            if self.i2s is None:
                print(f"⚠️ I2S 미초기화, 시뮬레이션 재생")
                time.sleep_ms(duration)
                return
            
            # WAV 파일 재생 시뮬레이션 (실제 구현 시 wav_player.py 로직 사용)
            self._play_wav_file(file_path, duration)
            
            print(f"🎵 {audio_file} 재생 완료")
            
        except Exception as e:
            print(f"❌ 오디오 재생 실패: {e}")
    
    def _play_wav_file(self, file_path, duration):
        """WAV 파일 재생 (wav_player_mono.py 방식)"""
        try:
            # 파일이 존재하지 않으면 시뮬레이션
            if not self._file_exists(file_path):
                print(f"📁 파일 없음, 시뮬레이션: {file_path}")
                time.sleep_ms(duration)
                return
            
            print(f"🎵 WAV 파일 재생: {file_path}")
            
            # TODO: 실제 WAV 파일 재생 로직
            # wav_player_mono.py의 play_wav_file() 함수 로직을 여기에 구현
            # 현재는 시뮬레이션으로 대체
            time.sleep_ms(duration)
            
        except Exception as e:
            print(f"❌ WAV 재생 실패: {e}")
            time.sleep_ms(duration)  # 시뮬레이션으로 대체
    
    def _play_audio_async(self, audio_file):
        """비동기 방식으로 오디오 재생"""
        try:
            # 오디오 큐에 추가
            self.audio_queue.append(audio_file)
            
            # TODO: 백그라운드에서 오디오 재생
            print(f"🎵 {audio_file} 큐에 추가됨")
            
        except Exception as e:
            print(f"❌ 오디오 큐 추가 실패: {e}")
    
    def _file_exists(self, file_path):
        """파일 존재 여부 확인"""
        try:
            with open(file_path, 'r') as f:
                return True
        except:
            return False
    
    def _get_audio_duration(self, audio_file):
        """오디오 파일 재생 시간 반환 (ms)"""
        file_info = self.audio_files_info.get_file_info(audio_file)
        return file_info["duration"] if file_info else 1000
    
    def set_volume(self, volume):
        """볼륨 설정 (0-100)"""
        self.volume = max(0, min(100, volume))
        print(f"🔊 볼륨 설정: {self.volume}%")
    
    def get_volume(self):
        """현재 볼륨 반환"""
        return self.volume
    
    def enable_audio(self):
        """오디오 활성화"""
        self.audio_enabled = True
        print("🔊 오디오 활성화")
    
    def disable_audio(self):
        """오디오 비활성화"""
        self.audio_enabled = False
        print("🔇 오디오 비활성화")
    
    def stop_all_audio(self):
        """모든 오디오 중지"""
        self.audio_queue.clear()
        self.current_audio = None
        print("⏹️ 모든 오디오 중지")
    
    def update(self):
        """오디오 시스템 업데이트"""
        # 오디오 큐 처리
        if self.audio_queue and not self.current_audio:
            next_audio = self.audio_queue.pop(0)
            self.current_audio = next_audio
            self._play_audio_blocking(next_audio)
            self.current_audio = None
    
    def get_audio_info(self):
        """오디오 시스템 정보 반환"""
        return {
            'enabled': self.audio_enabled,
            'volume': self.volume,
            'current_audio': self.current_audio,
            'queue_length': len(self.audio_queue),
            'available_files': self.audio_files_info.list_all_files(),
            'total_files': self.audio_files_info.get_file_count()
        }
