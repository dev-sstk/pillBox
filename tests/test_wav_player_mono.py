# The MIT License (MIT)
# Copyright (c) 2020 Mike Teachman
# https://opensource.org/licenses/MIT
# Modified for Mono WAV playback with MAX98357A

# Purpose:
# - read 16-bit audio samples from a mono formatted WAV file 
#   stored in the internal MicroPython filesystem
# - write audio samples to an I2S amplifier (MAX98357A)
#
# Sample WAV file:
#   "리필모드를_선택하셨습니다_선택버튼을_tts_메이커_AI보민.wav"
#
# Hardware tested:
# - MAX98357A I2S amplifier module
#
# The WAV file will play continuously until a keyboard interrupt is detected or
# the ESP32 is reset

from machine import I2S
from machine import Pin
import gc

def main():
    """메인 함수 - WAV 파일 재생"""
    
    # 사용 가능한 WAV 파일 목록
    WAV_FILES = [
        'refill_mode_selected_bomin.wav',
        'refill_mode_selected_bomin_compressed.wav'
    ]
    
    # 대화형 파일 선택
    print("🎵 재생할 WAV 파일을 선택하세요:")
    for i, filename in enumerate(WAV_FILES, 1):
        print(f"   {i}. {filename}")
    
    while True:
        try:
            choice = input("선택 (1-2): ").strip()
            if choice in ['1', '2']:
                WAV_FILE = WAV_FILES[int(choice) - 1]
                print(f"✅ 선택된 파일: {WAV_FILE}")
                break
            else:
                print("❌ 1 또는 2를 입력해주세요.")
        except KeyboardInterrupt:
            print("\n❌ 취소되었습니다.")
            return
        except:
            print("❌ 잘못된 입력입니다. 1 또는 2를 입력해주세요.")
    
    # 샘플레이트는 WAV 파일에서 자동으로 읽어옴
    
    # MAX98357A I2S 핀 설정 (config.py 기준)
    bck_pin = Pin(6)     # I2S_BCLK
    ws_pin = Pin(7)      # I2S_LRCLK  
    sdout_pin = Pin(5)   # I2S_DIN
    
    # WAV 파일을 먼저 읽어서 샘플레이트 확인
    try:
        wav = open(WAV_FILE, 'rb')
        
        # WAV 파일 헤더 정보 읽기
        try:
            wav.seek(0)
            riff_header = wav.read(12)
            fmt_chunk = wav.read(24)
            
            # 샘플레이트 확인
            import struct
            sample_rate = struct.unpack('<I', fmt_chunk[12:16])[0]
            channels = struct.unpack('<H', fmt_chunk[10:12])[0]
            bits_per_sample = struct.unpack('<H', fmt_chunk[22:24])[0]
            
            print(f'📁 WAV 파일 정보:')
            print(f'   샘플레이트: {sample_rate}Hz')
            print(f'   채널: {channels} ({"모노" if channels == 1 else "스테레오"})')
            print(f'   비트: {bits_per_sample}bit')
            
            # Data 섹션으로 이동 (44바이트)
            wav.seek(44)
            
        except Exception as header_error:
            print(f'❌ WAV 헤더 읽기 오류: {header_error}')
            print('📁 기본 설정으로 진행...')
            sample_rate = 16000
            channels = 1
            bits_per_sample = 16
            wav.seek(44)  # 기본 44바이트 오프셋
        
        # WAV 파일 닫기 (나중에 다시 열기)
        wav.close()
        
    except Exception as e:
        print(f'❌ WAV 파일 열기 실패: {e}')
        # 기본값 사용
        sample_rate = 16000
        channels = 1
        bits_per_sample = 16
    
    # I2S는 16비트만 지원하므로 8비트는 16비트로 변환
    i2s_bits = 16  # I2S는 항상 16비트 사용
    if bits_per_sample == 8:
        print("📝 8비트 WAV 파일을 16비트로 변환하여 재생합니다.")
    
    # 모노 WAV 파일용 I2S 설정 (16비트로 고정)
    try:
        # ESP32C6용 I2S 설정 (큰 버퍼 사용)
        audio_out = I2S(0,
                        sck=bck_pin, 
                        ws=ws_pin, 
                        sd=sdout_pin,
                        mode=I2S.TX,
                        bits=i2s_bits,  # 항상 16비트 사용
                        format=I2S.MONO,
                        rate=sample_rate,  # WAV 파일에서 읽은 샘플레이트 사용
                        ibuf=8192)  # 버퍼 크기 증가
        print(f"✅ I2S 초기화 성공 (큰 버퍼, {sample_rate}Hz, {i2s_bits}bit)")
    except Exception as e:
        print(f"❌ I2S 초기화 실패 (큰 버퍼): {e}")
        try:
            # 중간 버퍼로 재시도
            audio_out = I2S(0,
                           sck=bck_pin, 
                           ws=ws_pin, 
                           sd=sdout_pin,
                           mode=I2S.TX,
                           bits=i2s_bits,  # 항상 16비트 사용
                           format=I2S.MONO,
                           rate=sample_rate,  # WAV 파일에서 읽은 샘플레이트 사용
                           ibuf=4096)  # 중간 버퍼
            print(f"✅ I2S 초기화 성공 (중간 버퍼, {sample_rate}Hz, {i2s_bits}bit)")
        except Exception as e2:
            print(f"❌ I2S 초기화 실패 (중간 버퍼): {e2}")
            try:
                # 기본 버퍼로 재시도
                audio_out = I2S(0,
                               sck=bck_pin, 
                               ws=ws_pin, 
                               sd=sdout_pin,
                               mode=I2S.TX,
                               bits=i2s_bits,  # 항상 16비트 사용
                               format=I2S.MONO,
                               rate=sample_rate,  # WAV 파일에서 읽은 샘플레이트 사용
                               ibuf=2048)  # 기본 버퍼
                print(f"✅ I2S 초기화 성공 (기본 버퍼, {sample_rate}Hz, {i2s_bits}bit)")
            except Exception as e3:
                print(f"❌ I2S 초기화 실패 (기본 버퍼): {e3}")
                raise Exception("I2S 초기화 실패")
    
    print(f'🎵 모노 WAV 파일 재생 시작: {WAV_FILE}')
    
    try:
        wav = open(WAV_FILE, 'rb')
        
        # Data 섹션으로 이동 (44바이트)
        wav.seek(44)
        
        # 프레임 크기 계산 (모노 16bit → 2바이트)
        FRAME_SIZE = channels * (bits_per_sample // 8)  # 모노16bit → 2
        BUFFER_SIZE = 4096  # 충분히 크게
        
        # 샘플 배열 할당 (프레임 단위 보장)
        wav_samples = bytearray(BUFFER_SIZE)
        wav_samples_mv = memoryview(wav_samples)
        
        print(f'🎵 재생 시작... (프레임 크기: {FRAME_SIZE}바이트)')
        
        # WAV 파일에서 오디오 샘플을 연속적으로 읽어서 I2S DAC에 쓰기
        print('🎵 재생 루프 시작...')
        
        while True:
            try:
                # 작은 청크로 읽기 (더 안전한 방식)
                data = wav.read(512)  # readinto 대신 read 사용
                
                # WAV 파일 끝?
                if not data:
                    print('🔄 파일 재생 완료, 다시 시작...')
                    wav.seek(44)
                    continue
                
                # 프레임 단위로 보정 (내림)
                num_read = len(data)
                num_read = (num_read // FRAME_SIZE) * FRAME_SIZE
                
                if num_read == 0:
                    continue  # 프레임이 완성되지 않았으면 건너뛰기
                
                # 8비트를 16비트로 변환 (필요한 경우)
                if bits_per_sample == 8:
                    # 8비트 데이터를 16비트로 변환
                    converted_data = bytearray(num_read * 2)
                    for i in range(num_read):
                        # 8비트 값을 16비트로 확장 (부호 있는 정수로 변환)
                        sample_8bit = data[i]
                        if sample_8bit >= 128:
                            sample_16bit = (sample_8bit - 128) * 256
                        else:
                            sample_16bit = sample_8bit * 256
                        
                        # 리틀 엔디안으로 16비트 저장
                        converted_data[i*2] = sample_16bit & 0xFF
                        converted_data[i*2+1] = (sample_16bit >> 8) & 0xFF
                    
                    # 변환된 데이터를 I2S에 쓰기
                    bytes_written = 0
                    while bytes_written < len(converted_data):
                        try:
                            written = audio_out.write(converted_data[bytes_written:])
                            if written and written > 0:
                                bytes_written += written
                            else:
                                # 버퍼가 가득 찬 경우, 잠시 대기
                                import time
                                time.sleep_ms(10)
                        except Exception as write_error:
                            print(f'❌ I2S 쓰기 오류: {write_error}')
                            break
                else:
                    # 16비트 데이터는 그대로 사용
                    bytes_written = 0
                    while bytes_written < num_read:
                        try:
                            written = audio_out.write(data[bytes_written:num_read])
                            if written and written > 0:
                                bytes_written += written
                            else:
                                # 버퍼가 가득 찬 경우, 잠시 대기
                                import time
                                time.sleep_ms(10)
                        except Exception as write_error:
                            print(f'❌ I2S 쓰기 오류: {write_error}')
                            break
                        
            except (KeyboardInterrupt, Exception) as e:
                print(f'❌ 예외 발생: {type(e).__name__} {e}')
                break
        
        wav.close()
        
    except OSError as e:
        if "No such file" in str(e) or "ENOENT" in str(e):
            print(f'❌ 파일을 찾을 수 없습니다: {WAV_FILE}')
        else:
            print(f'❌ 파일 읽기 오류: {e}')
    except Exception as e:
        print(f'❌ 오류 발생: {e}')
    finally:
        # 리소스 정리
        try:
            audio_out.deinit()
            print('🎵 I2S 정리 완료')
        except:
            pass
        
        # 메모리 정리
        gc.collect()
        print('🧹 메모리 정리 완료')
        print('✅ 재생 종료')

if __name__ == "__main__":
    main()
