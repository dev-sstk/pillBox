"""
음성 안내 시스템
안내 멘트와 효과음을 관리하는 시스템
"""

import time
import os
from machine import Pin, I2S
from audio_files_info import get_audio_files_info

class AudioSystem:
    """음성 안내 시스템 클래스"""
    
    def __init__(self):
        """음성 안내 시스템 초기화 (지연 초기화)"""
        self.audio_enabled = True
        self.volume = 80  # 0-100
        self.current_audio = None
        self.audio_queue = []
        
        # I2S 오디오 설정 (지연 초기화)
        self.i2s = None
        self.i2s_initialized = False
        
        # 오디오 파일 정보 사용 (지연 로딩)
        self.audio_files_info = None
        
        print("[OK] AudioSystem 초기화 완료 (지연 초기화)")
    
    def _ensure_i2s_initialized(self):
        """I2S 하드웨어 지연 초기화"""
        if self.i2s_initialized:
            return True
            
        try:
            # 메모리 정리 후 I2S 초기화 시도
            import gc
            gc.collect()
            print("[INFO] I2S 지연 초기화 시작 - 메모리 정리 완료")
            
            # I2S 설정 (MAX98357A) - 메모리 사용량 최적화
            # BCLK: GPIO 6, LRCLK: GPIO 7, DIN: GPIO 5
            # 버퍼 크기를 줄여서 메모리 사용량 감소
            self.i2s = I2S(
                0,
                sck=Pin(6),      # Bit Clock
                ws=Pin(7),       # Left/Right Clock  
                sd=Pin(5),       # Data Input
                mode=I2S.TX,
                bits=16,
                format=I2S.MONO,
                rate=16000,
                ibuf=1024        # 2048 → 1024로 줄여서 메모리 절약
            )
            self.i2s_initialized = True
            print("[OK] I2S 오디오 하드웨어 지연 초기화 완료 (메모리 최적화)")
            return True
        except Exception as e:
            print(f"[WARN] I2S 오디오 하드웨어 지연 초기화 실패: {e}")
            # 메모리 부족 시 더 작은 버퍼로 재시도
            try:
                print("[INFO] 작은 버퍼로 I2S 재시도...")
                import gc
                gc.collect()
                self.i2s = I2S(
                    0,
                    sck=Pin(6),
                    ws=Pin(7),
                    sd=Pin(5),
                    mode=I2S.TX,
                    bits=16,
                    format=I2S.MONO,
                    rate=16000,
                    ibuf=512      # 더 작은 버퍼로 재시도
                )
                self.i2s_initialized = True
                print("[OK] I2S 오디오 하드웨어 지연 초기화 완료 (작은 버퍼)")
                return True
            except Exception as e2:
                print(f"[WARN] I2S 재시도도 실패: {e2}")
                self.audio_enabled = False
                self.i2s = None
                self.i2s_initialized = False
                return False
    
    def play_voice(self, audio_file, blocking=False):
        """안내 음성 재생"""
        if not self.audio_enabled:
            print(f"🔇 오디오 비활성화: {audio_file}")
            return
        
        if self.audio_files_info is None:
            self.audio_files_info = get_audio_files_info()
        file_info = self.audio_files_info.get_file_info(audio_file)
        if not file_info:
            print(f"[ERROR] 알 수 없는 오디오 파일: {audio_file}")
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
            if self.audio_files_info is None:
                self.audio_files_info = get_audio_files_info()
            file_path = self.audio_files_info.get_full_path(audio_file)
            if not self._file_exists(file_path):
                print(f"[ERROR] 오디오 파일 없음: {file_path}")
                return
            
            if self.audio_files_info is None:
                self.audio_files_info = get_audio_files_info()
            file_info = self.audio_files_info.get_file_info(audio_file)
            duration = file_info["duration"] if file_info else 1000
            
            print(f"[NOTE] {audio_file} 재생 시작...")
            
            # I2S 지연 초기화 시도
            if not self._ensure_i2s_initialized():
                print(f"[WARN] I2S 초기화 실패, 시뮬레이션 재생")
                time.sleep_ms(duration)
                return
            
            # WAV 파일 재생 시뮬레이션 (실제 구현 시 wav_player.py 로직 사용)
            self._play_wav_file(file_path, duration)
            
            print(f"[NOTE] {audio_file} 재생 완료")
            
        except Exception as e:
            print(f"[ERROR] 오디오 재생 실패: {e}")
    
    def _play_wav_file(self, file_path, duration):
        """WAV 파일 재생 (wav_player_mono.py 방식)"""
        try:
            # 파일이 존재하지 않으면 시뮬레이션
            if not self._file_exists(file_path):
                print(f"📁 파일 없음, 시뮬레이션: {file_path}")
                time.sleep_ms(duration)
                return
            
            print(f"[NOTE] WAV 파일 재생: {file_path}")
            
            # TODO: 실제 WAV 파일 재생 로직
            # wav_player_mono.py의 play_wav_file() 함수 로직을 여기에 구현
            # 현재는 시뮬레이션으로 대체
            time.sleep_ms(duration)
            
        except Exception as e:
            print(f"[ERROR] WAV 재생 실패: {e}")
            time.sleep_ms(duration)  # 시뮬레이션으로 대체
    
    def _play_audio_async(self, audio_file):
        """비동기 방식으로 오디오 재생"""
        try:
            # 오디오 큐에 추가
            self.audio_queue.append(audio_file)
            
            # TODO: 백그라운드에서 오디오 재생
            print(f"[NOTE] {audio_file} 큐에 추가됨")
            
        except Exception as e:
            print(f"[ERROR] 오디오 큐 추가 실패: {e}")
    
    def _file_exists(self, file_path):
        """파일 존재 여부 확인"""
        try:
            with open(file_path, 'r') as f:
                return True
        except:
            return False
    
    def _get_audio_duration(self, audio_file):
        """오디오 파일 재생 시간 반환 (ms)"""
        if self.audio_files_info is None:
            self.audio_files_info = get_audio_files_info()
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
    
    def play_alarm_sound(self):
        """알람 소리 재생"""
        try:
            print("🔊 알람 소리 재생 시작")
            
            # I2S 초기화 시도 (실패해도 부저는 사용 가능)
            self._ensure_i2s_initialized()
            
            # 부저 알람 톤 재생 (I2S 실패해도 동작)
            self._play_alarm_tone()
                
        except Exception as e:
            print(f"[ERROR] 알람 소리 재생 실패: {e}")
            # 실패 시 기본 톤으로 대체
            self._play_alarm_tone()
    
    def stop_alarm_sound(self):
        """알람 소리 정지"""
        try:
            print("🔇 알람 소리 정지")
            self.stop_all_audio()
        except Exception as e:
            print(f"[ERROR] 알람 소리 정지 실패: {e}")
    
    def _play_alarm_tone(self):
        """기본 알람 톤 재생 (부저 또는 I2S)"""
        try:
            print("🔔 기본 알람 톤 재생")
            
            # 부저 핀을 사용한 실제 알람 톤 재생
            self._play_buzzer_alarm()
                
        except Exception as e:
            print(f"[ERROR] 알람 톤 재생 실패: {e}")
            time.sleep_ms(500)  # 시뮬레이션으로 대체
    
    def _play_buzzer_alarm(self):
        """부저를 사용한 알람 톤 재생"""
        try:
            from machine import Pin
            
            # 부저 핀 (GPIO 18 사용 - HARDWARE.md 참조)
            buzzer_pin = Pin(18, Pin.OUT)
            
            # 알람 패턴: 3번의 짧은 비프음
            for i in range(3):
                # 1000Hz 톤 (0.2초)
                self._generate_tone(buzzer_pin, 1000, 200)
                time.sleep_ms(100)  # 0.1초 간격
            
            print("🔔 부저 알람 톤 재생 완료")
            
        except Exception as e:
            print(f"[ERROR] 부저 알람 톤 재생 실패: {e}")
            print("📢 알람 톤 재생 (시뮬레이션)")
            time.sleep_ms(1000)
    
    def _generate_tone(self, pin, frequency, duration_ms):
        """부저로 톤 생성"""
        try:
            # 간단한 톤 생성 (PWM 사용)
            from machine import PWM
            
            pwm = PWM(pin)
            pwm.freq(frequency)
            pwm.duty(512)  # 50% 듀티 사이클
            
            time.sleep_ms(duration_ms)
            pwm.deinit()
            
        except Exception as e:
            print(f"[ERROR] 톤 생성 실패: {e}")
            # PWM이 실패하면 단순히 핀을 토글
            for _ in range(frequency * duration_ms // 2000):
                pin.value(1)
                time.sleep_us(500000 // frequency)
                pin.value(0)
                time.sleep_us(500000 // frequency)
    
    def _play_tone_i2s(self, frequency, duration_ms):
        """I2S로 톤 재생"""
        try:
            # 간단한 사인파 생성 및 재생
            # TODO: 실제 I2S 톤 재생 로직 구현
            print(f"🎵 I2S 톤 재생: {frequency}Hz, {duration_ms}ms")
            time.sleep_ms(duration_ms)
        except Exception as e:
            print(f"[ERROR] I2S 톤 재생 실패: {e}")
            time.sleep_ms(duration_ms)
    
    def get_audio_info(self):
        """오디오 시스템 정보 반환"""
        return {
            'enabled': self.audio_enabled,
            'volume': self.volume,
            'current_audio': self.current_audio,
            'queue_length': len(self.audio_queue),
            'available_files': self.audio_files_info.list_all_files() if self.audio_files_info else [],
            'total_files': self.audio_files_info.get_file_count() if self.audio_files_info else 0
        }
