"""
음성 안내 시스템
안내 멘트와 효과음을 관리하는 시스템
"""

import time

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
        
        
        # 지연 로딩을 위한 캐시
        self.audio_files_info = None
        self._machine_modules = {}  # machine 모듈 캐시
        self._file_cache = {}  # 파일 존재 여부 캐시
        self._last_file_check = {}
        
        # print("[OK] AudioSystem 초기화 완료 (지연 로딩 적용)")
    
    def _get_machine_module(self, module_name):
        """machine 모듈 지연 로딩"""
        if module_name not in self._machine_modules:
            try:
                if module_name == "Pin":
                    from machine import Pin
                    self._machine_modules[module_name] = Pin
                elif module_name == "I2S":
                    from machine import I2S
                    self._machine_modules[module_name] = I2S
                elif module_name == "PWM":
                    from machine import PWM
                    self._machine_modules[module_name] = PWM
                else:
                    # print(f"[WARN] 알 수 없는 machine 모듈: {module_name}")
                    return None
            except Exception as e:
                # print(f"[WARN] machine 모듈 로딩 실패: {module_name}, {e}")
                return None
        return self._machine_modules[module_name]
    
    def _clear_all_caches(self):
        """모든 캐시 정리 (메모리 절약)"""
        try:
            # 모듈 캐시 정리
            self._machine_modules.clear()
            
            # 파일 캐시 정리
            self._file_cache.clear()
            self._last_file_check.clear()
            
            # 오디오 파일 정보 캐시 정리
            self.audio_files_info = None
            
            # print("[INFO] AudioSystem 모든 캐시 정리 완료")
        except Exception as e:
            # print(f"[WARN] 캐시 정리 실패: {e}")
            pass
    
    def _emergency_memory_cleanup(self):
        """기본 메모리 정리 (I2S 초기화 전)"""
        try:
            # print("[INFO] 기본 메모리 정리 시작...")
            import gc
            
            # 1. 모든 캐시 정리
            self._clear_all_caches()
            
            # 2. 가비지 컬렉션 5회 반복
            for i in range(5):
                gc.collect()
                time.sleep_ms(50)
            
            # print("[OK] 기본 메모리 정리 완료")
            
        except Exception as e:
            # print(f"[ERROR] 기본 메모리 정리 실패: {e}")
            pass
    
    def _get_audio_files_info(self):
        """오디오 파일 정보 지연 로딩"""
        if self.audio_files_info is None:
            try:
                from audio_files_info import get_audio_files_info
                self.audio_files_info = get_audio_files_info()
            except Exception as e:
                # print(f"[WARN] 오디오 파일 정보 로딩 실패: {e}")
                return None
        return self.audio_files_info
    
    def _file_exists(self, file_path):
        """파일 존재 여부 확인 (캐싱 적용)"""
        try:
            current_time = time.ticks_ms()
            cache_key = file_path
            
            # 5초간 캐시 유지
            if (cache_key in self._last_file_check and 
                time.ticks_diff(current_time, self._last_file_check[cache_key]["timestamp"]) < 5000):
                return self._last_file_check[cache_key]["exists"]
        except AttributeError:
            # MicroPython에서 ticks_ms가 없는 경우
            pass
        
        try:
            with open(file_path, 'r'):
                pass
            exists = True
        except OSError:
            exists = False
        
        try:
            self._last_file_check[cache_key] = {
                "exists": exists,
                "timestamp": time.ticks_ms()
            }
        except AttributeError:
            # ticks_ms가 없는 경우 캐시 없이 반환
            pass
        
        return exists
    
    def _ensure_i2s_initialized(self):
        """I2S 하드웨어 지연 초기화"""
        if self.i2s_initialized:
            return True
            
        try:
            # print("[INFO] I2S 초기화 시작 - 메모리 제한 없음")
            
            # print("[INFO] I2S 지연 초기화 시작 - 메모리 관리 완료")
            
            # I2S 초기화 전 메모리 상태 확인
            pre_init_memory = self._check_memory_status("I2S 초기화 전")
            
            # I2S 설정 (MAX98357A) - 메모리 사용량 최적화 (지연 로딩)
            # BCLK: GPIO 6, LRCLK: GPIO 7, DIN: GPIO 5
            # 버퍼 크기를 극도로 줄여서 메모리 사용량 감소
            Pin = self._get_machine_module("Pin")
            I2S = self._get_machine_module("I2S")
            
            if Pin is None or I2S is None:
                raise Exception("machine 모듈 로딩 실패")
            
            # 단계별 I2S 초기화 시도
            self.i2s = self._try_i2s_initialization(Pin, I2S)
            self.i2s_initialized = True
            
            # I2S 초기화 직후 메모리 상태 확인
            post_init_memory = self._check_memory_status("I2S 초기화 직후")
            memory_used = pre_init_memory - post_init_memory
            # print(f"[MEMORY] I2S 초기화로 사용된 메모리: {memory_used:,} bytes")
            
            # print("[OK] I2S 오디오 하드웨어 지연 초기화 완료 (메모리 최적화)")
            return True
        except Exception as e:
            # print(f"[WARN] I2S 오디오 하드웨어 지연 초기화 실패: {e}")
            self.audio_enabled = False
            self.i2s = None
            self.i2s_initialized = False
            return False
    
    def _check_memory_status(self, context=""):
        """메모리 상태 확인"""
        try:
            import gc
            free_mem = gc.mem_free()
            alloc_mem = gc.mem_alloc()
            total_mem = free_mem + alloc_mem
            
            # 상태 표시 (간소화)
            if context:
                # print(f"[MEMORY] {context} - 여유: {free_mem:,} bytes, 사용률: {(alloc_mem/total_mem)*100:.1f}%")
                pass
            else:
                # print(f"[MEMORY] 사용 가능: {free_mem:,} bytes, 사용 중: {alloc_mem:,} bytes, 총: {total_mem:,} bytes, 사용률: {(alloc_mem/total_mem)*100:.1f}%")
                pass
            
            return free_mem
        except Exception as e:
            # print(f"[WARN] 메모리 상태 확인 실패: {e}")
            return 0
    
    def _get_wav_sample_rate(self):
        """WAV 파일에서 샘플레이트 읽기 (test_wav_player_mono.py와 동일)"""
        try:
            # 기본 WAV 파일 경로
            wav_file = "/wav/dispense_medicine.wav"
            
            with open(wav_file, 'rb') as f:
                # WAV 파일 헤더 정보 읽기
                f.seek(0)
                riff_header = f.read(12)
                fmt_chunk = f.read(24)
                
                # 샘플레이트 확인
                import struct
                sample_rate = struct.unpack('<I', fmt_chunk[12:16])[0]
                channels = struct.unpack('<H', fmt_chunk[10:12])[0]
                bits_per_sample = struct.unpack('<H', fmt_chunk[22:24])[0]
                
                # print(f'📁 WAV 파일 정보:')
                # print(f'   샘플레이트: {sample_rate}Hz')
                # print(f'   채널: {channels} ({"모노" if channels == 1 else "스테레오"})')
                # print(f'   비트: {bits_per_sample}bit')
                
                return sample_rate
                
        except Exception as e:
            # print(f'❌ WAV 파일 샘플레이트 읽기 실패: {e}')
            # print('📁 기본 설정으로 진행...')
            return 16000  # 기본값
    
    def _try_i2s_initialization(self, Pin, I2S):
        """I2S 초기화 시도 (test_wav_player_mono.py와 동일한 설정)"""
        # WAV 파일에서 샘플레이트 읽기
        sample_rate = self._get_wav_sample_rate()
        
        # I2S는 항상 16비트 사용
        i2s_bits = 16
        
        # test_wav_player_mono.py와 동일한 단계별 시도
        try:
            # 1단계: 큰 버퍼 시도 (8192)
            # print(f"[I2S] 큰 버퍼 설정 시도: rate={sample_rate}, bits={i2s_bits}, ibuf=8192")
            i2s = I2S(
                0,
                sck=Pin(6),
                ws=Pin(7),
                sd=Pin(5),
                mode=I2S.TX,
                bits=i2s_bits,
                format=I2S.MONO,
                rate=sample_rate,
                ibuf=8192
            )
            # print(f"[OK] I2S 초기화 성공 (큰 버퍼, {sample_rate}Hz, {i2s_bits}bit)")
            return i2s
            
        except Exception as e:
            # print(f"[WARN] I2S 초기화 실패 (큰 버퍼): {e}")
            try:
                # 2단계: 중간 버퍼 시도 (4096)
                # print(f"[I2S] 중간 버퍼 설정 시도: rate={sample_rate}, bits={i2s_bits}, ibuf=4096")
                i2s = I2S(
                    0,
                    sck=Pin(6),
                    ws=Pin(7),
                    sd=Pin(5),
                    mode=I2S.TX,
                    bits=i2s_bits,
                    format=I2S.MONO,
                    rate=sample_rate,
                    ibuf=4096
                )
                # print(f"[OK] I2S 초기화 성공 (중간 버퍼, {sample_rate}Hz, {i2s_bits}bit)")
                return i2s
                
            except Exception as e2:
                # print(f"[WARN] I2S 초기화 실패 (중간 버퍼): {e2}")
                try:
                    # 3단계: 기본 버퍼 시도 (2048)
                    # print(f"[I2S] 기본 버퍼 설정 시도: rate={sample_rate}, bits={i2s_bits}, ibuf=2048")
                    i2s = I2S(
                        0,
                        sck=Pin(6),
                        ws=Pin(7),
                        sd=Pin(5),
                        mode=I2S.TX,
                        bits=i2s_bits,
                        format=I2S.MONO,
                        rate=sample_rate,
                        ibuf=2048
                    )
                    # print(f"[OK] I2S 초기화 성공 (기본 버퍼, {sample_rate}Hz, {i2s_bits}bit)")
                    return i2s
                    
                except Exception as e3:
                    # print(f"[WARN] I2S 초기화 실패 (기본 버퍼): {e3}")
                    try:
                        # 4단계: 최소 버퍼 시도 (1024)
                        # print(f"[I2S] 최소 버퍼 설정 시도: rate={sample_rate}, bits={i2s_bits}, ibuf=1024")
                        i2s = I2S(
                            0,
                            sck=Pin(6),
                            ws=Pin(7),
                            sd=Pin(5),
                            mode=I2S.TX,
                            bits=i2s_bits,
                            format=I2S.MONO,
                            rate=sample_rate,
                            ibuf=1024
                        )
                        # print(f"[OK] I2S 초기화 성공 (최소 버퍼, {sample_rate}Hz, {i2s_bits}bit)")
                        return i2s
                        
                    except Exception as e4:
                        # print(f"[WARN] I2S 초기화 실패 (최소 버퍼): {e4}")
                        try:
                            # 5단계: 극소 버퍼 시도 (512)
                            # print(f"[I2S] 극소 버퍼 설정 시도: rate={sample_rate}, bits={i2s_bits}, ibuf=512")
                            i2s = I2S(
                                0,
                                sck=Pin(6),
                                ws=Pin(7),
                                sd=Pin(5),
                                mode=I2S.TX,
                                bits=i2s_bits,
                                format=I2S.MONO,
                                rate=sample_rate,
                                ibuf=512
                            )
                            # print(f"[OK] I2S 초기화 성공 (극소 버퍼, {sample_rate}Hz, {i2s_bits}bit)")
                            return i2s
                            
                        except Exception as e5:
                            # print(f"[ERROR] I2S 초기화 최종 실패 (모든 버퍼 크기 시도 완료): {e5}")
                            raise Exception("I2S 초기화 실패")
    
    def _emergency_memory_cleanup(self):
        """기본 메모리 정리 (I2S 초기화 전)"""
        try:
            import gc
            
            # print("[INFO] 기본 메모리 정리 시작")
            
            # 1. 모든 캐시 정리
            self._clear_all_caches()
            
            # 2. 기본 가비지 컬렉션
            for i in range(5):
                gc.collect()
                time.sleep_ms(50)
            
            # print("[OK] 기본 메모리 정리 완료")
            
        except Exception as e:
            # print(f"[ERROR] 기본 메모리 정리 실패: {e}")
            pass
    
    def play_voice(self, audio_file, blocking=False):
        """안내 음성 재생"""
        if not self.audio_enabled:
            # print(f"🔇 오디오 비활성화: {audio_file}")
            return
        
        audio_files_info = self._get_audio_files_info()
        if audio_files_info is None:
            # print(f"[ERROR] 오디오 파일 정보 로딩 실패: {audio_file}")
            return
        
        # 디버그: 사용 가능한 파일 목록 출력
        # print(f"[DEBUG] 요청된 오디오 파일: {audio_file}")
        if hasattr(audio_files_info, 'audio_files'):
            available_files = list(audio_files_info.audio_files.keys())
            # print(f"[DEBUG] 사용 가능한 오디오 파일들: {available_files}")
        
        file_info = audio_files_info.get_file_info(audio_file)
        if not file_info:
            # print(f"[ERROR] 알 수 없는 오디오 파일: {audio_file}")
            return
        
        # print(f"🔊 안내 음성 재생: {file_info['description']}")
        
        if blocking:
            self._play_audio_blocking(audio_file)
        else:
            self._play_audio_async(audio_file)
    
    def play_effect(self, audio_file):
        """효과음 재생"""
        if not self.audio_enabled:
            return
        
        # print(f"🔔 효과음 재생: {audio_file}")
        self._play_audio_async(audio_file)
    
    def _play_audio_blocking(self, audio_file):
        """블로킹 방식으로 오디오 재생"""
        try:
            audio_files_info = self._get_audio_files_info()
            if audio_files_info is None:
                # print(f"[ERROR] 오디오 파일 정보 로딩 실패: {audio_file}")
                return
                
            file_path = audio_files_info.get_full_path(audio_file)
            if not self._file_exists(file_path):
                # print(f"[ERROR] 오디오 파일 없음: {file_path}")
                return
            
            file_info = audio_files_info.get_file_info(audio_file)
            duration = file_info["duration"] if file_info else 1000
            
            # print(f"[NOTE] {audio_file} 재생 시작...")
            
            # I2S 지연 초기화 시도
            if not self._ensure_i2s_initialized():
                # print(f"[WARN] I2S 초기화 실패, 시뮬레이션 재생")
                time.sleep_ms(duration)
                return
            
            # WAV 파일 재생 시뮬레이션 (실제 구현 시 wav_player.py 로직 사용)
            self._play_wav_file(file_path, duration)
            
            # print(f"[NOTE] {audio_file} 재생 완료")
            
        except Exception as e:
            # print(f"[ERROR] 오디오 재생 실패: {e}")
            pass
    
    def _play_wav_file(self, file_path, duration):
        """WAV 파일 재생 (test_wav_player_mono.py 방식)"""
        try:
            # 파일이 존재하지 않으면 시뮬레이션
            if not self._file_exists(file_path):
                # print(f"📁 파일 없음, 시뮬레이션: {file_path}")
                time.sleep_ms(duration)
                return
            
            # print(f"🎵 WAV 파일 재생 시작: {file_path}")
            
            # I2S가 초기화되지 않았으면 시뮬레이션
            if not self.i2s_initialized or self.i2s is None:
                # print(f"📁 I2S 미초기화, 시뮬레이션: {file_path}")
                time.sleep_ms(duration)
                return
            
            # WAV 파일 열기
            wav = open(file_path, 'rb')
            
            # Data 섹션으로 이동 (44바이트)
            wav.seek(44)
            
            # 프레임 크기 계산 (모노 16bit → 2바이트)
            channels = 1  # 모노
            bits_per_sample = 16
            FRAME_SIZE = channels * (bits_per_sample // 8)  # 모노16bit → 2
            BUFFER_SIZE = 4096  # 충분히 크게
            
            # 샘플 배열 할당
            wav_samples = bytearray(BUFFER_SIZE)
            
            # print(f"🎵 재생 시작... (프레임 크기: {FRAME_SIZE}바이트)")
            
            # WAV 파일에서 오디오 샘플을 연속적으로 읽어서 I2S DAC에 쓰기
            while True:
                try:
                    # 작은 청크로 읽기 (test_wav_player_mono.py와 동일)
                    data = wav.read(512)  # readinto 대신 read 사용
                    
                    # WAV 파일 끝?
                    if not data:
                        # print('🔄 파일 재생 완료')
                        break
                    
                    # 프레임 단위로 보정 (내림)
                    num_read = len(data)
                    num_read = (num_read // FRAME_SIZE) * FRAME_SIZE
                    
                    if num_read == 0:
                        continue  # 프레임이 완성되지 않았으면 건너뛰기
                    
                    # I2S에 데이터 쓰기 (test_wav_player_mono.py와 동일)
                    bytes_written = 0
                    while bytes_written < num_read:
                        try:
                            written = self.i2s.write(data[bytes_written:num_read])
                            if written and written > 0:
                                bytes_written += written
                            else:
                                # 버퍼가 가득 찬 경우, 잠시 대기
                                time.sleep_ms(10)
                        except Exception as write_error:
                            # print(f'❌ I2S 쓰기 오류: {write_error}')
                            break
                        
                except Exception as e:
                    # print(f'❌ 재생 중 오류: {e}')
                    break
            
            wav.close()
            # print(f"🎵 WAV 파일 재생 완료: {file_path}")
            
        except Exception as e:
            # print(f"[ERROR] WAV 재생 실패: {e}")
            time.sleep_ms(duration)  # 시뮬레이션으로 대체
    
    def _play_audio_async(self, audio_file):
        """비동기 방식으로 오디오 재생"""
        try:
            # 오디오 큐에 추가
            self.audio_queue.append(audio_file)
            
            # TODO: 백그라운드에서 오디오 재생
            # print(f"[NOTE] {audio_file} 큐에 추가됨")
            
        except Exception as e:
            # print(f"[ERROR] 오디오 큐 추가 실패: {e}")
            pass
    
    
    def _get_audio_duration(self, audio_file):
        """오디오 파일 재생 시간 반환 (ms)"""
        audio_files_info = self._get_audio_files_info()
        if audio_files_info is None:
            return 1000  # 기본값 반환
        file_info = audio_files_info.get_file_info(audio_file)
        return file_info["duration"] if file_info else 1000
    
    
    def stop_all_audio(self):
        """모든 오디오 중지"""
        self.audio_queue.clear()
        self.current_audio = None
        # print("⏹️ 모든 오디오 중지")
    
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
            # print("🔊 알람 소리 재생 시작")
            
            # I2S 초기화 시도 (실패해도 부저는 사용 가능)
            self._ensure_i2s_initialized()
            
            # 부저 알람 톤 재생 (I2S 실패해도 동작)
            self._play_alarm_tone()
                
        except Exception as e:
            # print(f"[ERROR] 알람 소리 재생 실패: {e}")
            # 실패 시 기본 톤으로 대체
            self._play_alarm_tone()
    
    def stop_alarm_sound(self):
        """알람 소리 정지"""
        try:
            # print("🔇 알람 소리 정지")
            self.stop_all_audio()
        except Exception as e:
            # print(f"[ERROR] 알람 소리 정지 실패: {e}")
            pass
    
    def _play_alarm_tone(self):
        """기본 알람 톤 재생 (부저 또는 I2S)"""
        try:
            # print("🔔 기본 알람 톤 재생")
            
            # 부저 핀을 사용한 실제 알람 톤 재생
            self._play_buzzer_alarm()
                
        except Exception as e:
            # print(f"[ERROR] 알람 톤 재생 실패: {e}")
            time.sleep_ms(500)  # 시뮬레이션으로 대체
    
    def _play_buzzer_alarm(self):
        """부저를 사용한 알람 톤 재생"""
        try:
            Pin = self._get_machine_module("Pin")
            if Pin is None:
                raise Exception("Pin 모듈 로딩 실패")
            
            # 부저 핀 (GPIO 18 사용 - HARDWARE.md 참조)
            buzzer_pin = Pin(18, Pin.OUT)
            
            # 알람 패턴: 3번의 짧은 비프음
            for _ in range(3):
                # 1000Hz 톤 (0.2초)
                self._generate_tone(buzzer_pin, 1000, 200)
                time.sleep_ms(100)  # 0.1초 간격
            
            # print("🔔 부저 알람 톤 재생 완료")
            
        except Exception as e:
            # print(f"[ERROR] 부저 알람 톤 재생 실패: {e}")
            # print("📢 알람 톤 재생 (시뮬레이션)")
            time.sleep_ms(1000)
    
    def _generate_tone(self, pin, frequency, duration_ms):
        """부저로 톤 생성"""
        try:
            # 간단한 톤 생성 (PWM 사용)
            PWM = self._get_machine_module("PWM")
            if PWM is None:
                raise Exception("PWM 모듈 로딩 실패")
            
            pwm = PWM(pin)
            pwm.freq(frequency)
            pwm.duty(512)  # 50% 듀티 사이클
            
            time.sleep_ms(duration_ms)
            pwm.deinit()
            
        except Exception as e:
            # print(f"[ERROR] 톤 생성 실패: {e}")
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
            # print(f"🎵 I2S 톤 재생: {frequency}Hz, {duration_ms}ms")
            time.sleep_ms(duration_ms)
        except Exception as e:
            # print(f"[ERROR] I2S 톤 재생 실패: {e}")
            time.sleep_ms(duration_ms)
    
