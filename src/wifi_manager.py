"""
WiFi 관리 시스템
ESP32의 WiFi 기능을 활용한 네트워크 스캔, 연결, 관리
"""

import network
import time
import json
import ntptime

class WiFiManager:
    """WiFi 관리 클래스"""
    
    def __init__(self):
        """WiFi 관리자 초기화"""
        self.wifi = network.WLAN(network.STA_IF)
        self.wifi.active(True)
        
        # WiFi 초기화 대기 (빠른 부팅을 위해 짧게)
        # print("📡 WiFi 초기화 중... (0.5초 대기)")
        time.sleep(0.5)
        
        # WiFi 설정 저장 파일
        self.config_file = "/data/wifi_config.json"
        
        # 스캔된 네트워크 목록
        self.scanned_networks = []
        self.last_scan_time = 0
        self.scan_interval = 30000  # 30초마다 스캔
        
        # 연결 상태
        self.is_connected = False
        self.connected_ssid = None
        self.connection_attempts = 0
        self.max_connection_attempts = 3
        
        # NTP 서버 설정 (한국 시간용)
        self.ntp_servers = [
            'pool.ntp.org',
            'time.nist.gov',
            'kr.pool.ntp.org'
        ]
        self.time_synced = False
        
        # 자동 연결은 StartupScreen에서 처리 (부팅 속도 향상)
        # self._load_saved_config()  # 제거됨
        
        # print("[OK] WiFiManager 초기화 완료 (자동 연결 안함)")
    
    def scan_networks(self, force=False):
        """WiFi 네트워크 스캔"""
        current_time = time.ticks_ms()
        
        # 강제 스캔이 아니고 스캔 간격이 지나지 않았으면 기존 결과 반환
        if not force and (time.ticks_diff(current_time, self.last_scan_time) < self.scan_interval):
            # print(f"📡 캐시된 {len(self.scanned_networks)}개 네트워크 반환")
            return self.scanned_networks
        
        # print("📡 WiFi 네트워크 스캔 시작...")
        
        try:
            # WiFi 재초기화 (연결 실패 후 스캔을 위해 중요!)
            # print("  📡 WiFi 재초기화 시작...")
            self.wifi.active(False)
            time.sleep_ms(500)
            self.wifi.active(True)
            time.sleep_ms(2000)  # 초기화 대기 (중요!)
            
            # print(f"  📡 WiFi 활성 상태: {self.wifi.active()}")
            
            # WiFi 스캔 실행
            # print("  📡 스캔 실행 중...")
            scan_results = self.wifi.scan()
            # print(f"  📡 원시 스캔 결과: {len(scan_results) if scan_results else 0}개")
            
            self.scanned_networks = []
            
            if scan_results:
                for idx, result in enumerate(scan_results):
                    try:
                        ssid = result[0].decode('utf-8')
                        # print(f"    📡 스캔 결과 #{idx+1}: SSID={ssid}, RSSI={result[3]}, Auth={result[4]}")
                        
                        if ssid:  # 빈 SSID 제외
                            network_info = {
                                'ssid': ssid,
                                'signal': result[3],  # RSSI 값
                                'security': self._get_security_type(result[4]),  # 보안 타입
                                'channel': result[2],
                                'mac': ':'.join(['%02x' % b for b in result[1]])
                            }
                            self.scanned_networks.append(network_info)
                    except Exception as e:
                        # print(f"    [ERROR] 스캔 결과 #{idx+1} 파싱 실패: {e}")
                        continue
                
                # 신호 강도순으로 정렬 (높은 순)
                self.scanned_networks.sort(key=lambda x: x['signal'], reverse=True)
            else:
                # print("  [WARN] 스캔 결과가 비어있음")
                pass
            
            self.last_scan_time = current_time
            
            # print(f"[OK] {len(self.scanned_networks)}개 네트워크 스캔 완료")
            
            # 스캔 결과 출력
            for i, network in enumerate(self.scanned_networks):
                # print(f"  {i+1}. {network['ssid']} (신호: {network['signal']}dBm, 보안: {network['security']})")
                pass
            
            return self.scanned_networks
            
        except Exception as e:
            # print(f"[ERROR] WiFi 스캔 실패: {e}")
            import sys
            sys.print_exception(e)
            return []
            pass
    
    def _get_security_type(self, authmode):
        """보안 타입 문자열 변환"""
        security_map = {
            0: "Open",
            1: "WEP", 
            2: "WPA-PSK",
            3: "WPA2-PSK",
            4: "WPA/WPA2-PSK",
            5: "WPA2/WPA3-PSK",
            6: "WPA3-PSK"
        }
        return security_map.get(authmode, "Unknown")
    
    def connect_to_network(self, ssid, password="", timeout=10000):
        """WiFi 네트워크에 연결"""
        # print(f"🔗 WiFi 연결 시도: {ssid}")
        
        try:
            # 이전 연결 해제
            if self.wifi.isconnected():
                self.wifi.disconnect()
            
            # 연결 설정
            self.wifi.connect(ssid, password)
            
            # 연결 대기
            start_time = time.ticks_ms()
            while not self.wifi.isconnected():
                if time.ticks_diff(time.ticks_ms(), start_time) > timeout:
                    # print(f"[ERROR] WiFi 연결 타임아웃: {ssid}")
                    return False
                time.sleep_ms(100)
            
            # 연결 성공
            self.is_connected = True
            self.connected_ssid = ssid
            self.connection_attempts = 0
            
            # 연결 정보 출력
            ip_info = self.wifi.ifconfig()
            # print(f"[OK] WiFi 연결 성공: {ssid}")
            # print(f"   IP: {ip_info[0]}")
            # print(f"   Subnet: {ip_info[1]}")
            # print(f"   Gateway: {ip_info[2]}")
            # print(f"   DNS: {ip_info[3]}")
            
            # 설정 저장
            self._save_config(ssid, password)
            
            # NTP 시간 동기화 시도
            self._sync_ntp_time_internal()
            
            return True
            
        except Exception as e:
            # print(f"[ERROR] WiFi 연결 실패: {e}")
            self.connection_attempts += 1
            return False
    
    def disconnect(self):
        """WiFi 연결 해제"""
        if self.wifi.isconnected():
            self.wifi.disconnect()
            self.is_connected = False
            self.connected_ssid = None
            # print("🔌 WiFi 연결 해제됨")
    
    def get_connection_status(self):
        """연결 상태 정보 반환"""
        if self.wifi.isconnected():
            ip_info = self.wifi.ifconfig()
            return {
                'connected': True,
                'ssid': self.connected_ssid,
                'ip': ip_info[0],
                'signal': self._get_signal_strength(),
                'status': 'connected'
            }
        else:
            return {
                'connected': False,
                'ssid': None,
                'ip': None,
                'signal': 0,
                'status': 'disconnected'
            }
    
    def _get_signal_strength(self):
        """현재 연결된 네트워크의 신호 강도 반환"""
        if not self.wifi.isconnected():
            return 0
        
        # 현재 연결된 SSID로 스캔 결과에서 신호 강도 찾기
        for network in self.scanned_networks:
            if network['ssid'] == self.connected_ssid:
                return network['signal']
        return 0
    
    def _save_config(self, ssid, password):
        """WiFi 설정을 파일에 저장"""
        try:
            import os
            
            # /data 디렉토리 존재 확인 및 생성
            data_dir = "/data"
            try:
                if data_dir not in os.listdir("/"):
                    os.mkdir(data_dir)
                    # print(f"[INFO] /data 디렉토리 생성됨")
            except OSError as e:
                if e.errno == 17:  # EEXIST - 디렉토리가 이미 존재
                    # print(f"[INFO] /data 디렉토리가 이미 존재함")
                    pass
                else:
                    raise
            
            config = {
                'ssid': ssid,
                'password': password,
                'saved_at': time.time()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            
            # print(f"[SAVE] WiFi 설정 저장됨: {ssid}")
            
        except Exception as e:
            # print(f"[ERROR] WiFi 설정 저장 실패: {e}")
            pass
    
    def _load_saved_config(self):
        """저장된 WiFi 설정 불러오기"""
        try:
            import os
            
            # /data 디렉토리 존재 확인 및 생성
            data_dir = "/data"
            try:
                if data_dir not in os.listdir("/"):
                    os.mkdir(data_dir)
                    # print(f"[INFO] /data 디렉토리 생성됨")
            except OSError as e:
                if e.errno == 17:  # EEXIST - 디렉토리가 이미 존재
                    # print(f"[INFO] /data 디렉토리가 이미 존재함")
                    pass
                else:
                    raise
            
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            ssid = config.get('ssid', '')
            password = config.get('password', '')
            
            if ssid:
                # print(f"📂 저장된 WiFi 설정 발견: {ssid}")
                # 자동 연결 시도
                self.connect_to_network(ssid, password, timeout=5000)
            
        except Exception as e:
            # print(f"[WARN] 저장된 WiFi 설정 없음: {e}")
            pass
    
    def try_auto_connect(self, timeout=5000):
        """저장된 WiFi 설정으로 자동 연결 시도 (Public 메서드)"""
        try:
            import os
            
            # /data 디렉토리 존재 확인 및 생성
            data_dir = "/data"
            try:
                if data_dir not in os.listdir("/"):
                    os.mkdir(data_dir)
                    # print(f"[INFO] /data 디렉토리 생성됨")
            except OSError as e:
                if e.errno == 17:  # EEXIST - 디렉토리가 이미 존재
                    # print(f"[INFO] /data 디렉토리가 이미 존재함")
                    pass
                else:
                    raise
            
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            ssid = config.get('ssid', '')
            password = config.get('password', '')
            
            if ssid:
                # print(f"📂 저장된 WiFi 설정 발견: {ssid}")
                # 자동 연결 시도
                return self.connect_to_network(ssid, password, timeout=timeout)
            else:
                # print("[WARN] 저장된 WiFi 설정 없음")
                return False
            
        except Exception as e:
            # print(f"[WARN] 저장된 WiFi 설정 없음: {e}")
            return False
    
    def forget_network(self):
        """저장된 WiFi 설정 삭제"""
        try:
            import os
            os.remove(self.config_file)
            self.disconnect()
            # print("🗑️ WiFi 설정 삭제됨")
        except Exception as e:
            # print(f"[ERROR] WiFi 설정 삭제 실패: {e}")
            pass
    
    def forget_specific_network(self, ssid):
        """특정 네트워크의 연결 정보 삭제"""
        try:
            import os
            
            # /data 디렉토리 존재 확인 및 생성
            data_dir = "/data"
            try:
                if data_dir not in os.listdir("/"):
                    os.mkdir(data_dir)
                    # print(f"[INFO] /data 디렉토리 생성됨")
            except OSError as e:
                if e.errno == 17:  # EEXIST - 디렉토리가 이미 존재
                    # print(f"[INFO] /data 디렉토리가 이미 존재함")
                    pass
                else:
                    raise
            
            # 현재 저장된 설정 확인
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                saved_ssid = config.get('ssid', '')
                
                # 요청한 SSID와 저장된 SSID가 일치하면 삭제
                if saved_ssid == ssid:
                    os.remove(self.config_file)
                    self.disconnect()
                    # print(f"🗑️ {ssid} 네트워크 연결 정보 삭제됨")
                    return True
                else:
                    # print(f"[INFO] {ssid} 네트워크는 저장된 설정이 없습니다")
                    return False
            except FileNotFoundError:
                # print(f"[INFO] {ssid} 네트워크는 저장된 설정이 없습니다")
                return False
        except Exception as e:
            # print(f"[ERROR] {ssid} 네트워크 삭제 실패: {e}")
            return False
    
    def get_saved_password(self, ssid):
        """저장된 비밀번호 확인"""
        try:
            import os
            
            # /data 디렉토리 존재 확인 및 생성
            data_dir = "/data"
            try:
                if data_dir not in os.listdir("/"):
                    os.mkdir(data_dir)
                    # print(f"[INFO] /data 디렉토리 생성됨")
            except OSError as e:
                if e.errno == 17:  # EEXIST - 디렉토리가 이미 존재
                    # print(f"[INFO] /data 디렉토리가 이미 존재함")
                    pass
                else:
                    raise
            
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            saved_ssid = config.get('ssid', '')
            saved_password = config.get('password', '')
            
            # 요청한 SSID와 저장된 SSID가 일치하면 비밀번호 반환
            if saved_ssid == ssid:
                # print(f"[SAVE] 저장된 비밀번호 발견: {ssid}")
                return saved_password
            else:
                return None
        except Exception as e:
            # print(f"[WARN] 저장된 비밀번호 확인 실패: {e}")
            return None
    
    def get_network_list(self):
        """스캔된 네트워크 목록 반환 (신호 강도 포함)"""
        # 최신 스캔 결과가 없으면 스캔 실행
        if not self.scanned_networks:
            self.scan_networks()
        
        # 신호 강도를 퍼센트로 변환
        networks_with_percent = []
        for network in self.scanned_networks:
            signal_percent = self._rssi_to_percent(network['signal'])
            network_copy = network.copy()
            network_copy['signal_percent'] = signal_percent
            networks_with_percent.append(network_copy)
        
        return networks_with_percent
    
    def _rssi_to_percent(self, rssi):
        """RSSI 값을 퍼센트로 변환"""
        # RSSI 범위: -100dBm ~ -30dBm
        # 퍼센트 범위: 0% ~ 100%
        if rssi >= -30:
            return 100
        elif rssi <= -100:
            return 0
        else:
            return int((rssi + 100) * 100 / 70)
    
    
    def update(self):
        """WiFi 상태 업데이트 (주기적 호출)"""
        # 연결 상태 확인
        if self.wifi.isconnected():
            if not self.is_connected:
                self.is_connected = True
                # print("[OK] WiFi 재연결됨")
        else:
            if self.is_connected:
                self.is_connected = False
                self.connected_ssid = None
                # print("[ERROR] WiFi 연결 끊어짐")
        
        # 주기적 스캔
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_scan_time) > self.scan_interval:
            self.scan_networks()
    
    def sync_ntp_time(self):
        """NTP 서버에서 시간 동기화 (한국 시간) - 공개 메서드"""
        return self._sync_ntp_time_internal()
    
    def _sync_ntp_time_internal(self):
        """NTP 서버에서 시간 동기화 (한국 시간) - 내부 메서드"""
        if not self.is_connected:
            # print("[WARN] WiFi 연결 필요")
            return False
        
        # print("🕐 NTP 시간 동기화 시작...")
        
        for ntp_server in self.ntp_servers:
            try:
                # print(f"   NTP 서버 연결 시도: {ntp_server}")
                ntptime.host = ntp_server
                ntptime.settime()
                
                # NTP 시간 동기화 완료 (UTC 시간으로 설정됨)
                utc_time = time.localtime()
                # print(f"[OK] 시간 동기화 성공: {ntp_server}")
                # print(f"   NTP 동기화된 시간 (UTC): {utc_time}")
                
                # UTC 시간에 9시간 오프셋 적용하여 한국시간으로 변환하고 ESP32 시간 설정
                kst_timestamp = time.mktime(utc_time) + (9 * 3600)  # 9시간 추가
                kst_time = time.localtime(kst_timestamp)
                # print(f"   한국 시간 변환 후: {kst_time}")
                
                # ESP32의 시간을 한국시간으로 설정
                import machine
                machine.RTC().datetime((kst_time[0], kst_time[1], kst_time[2], kst_time[6], kst_time[3], kst_time[4], kst_time[5], 0))
                # print(f"   ESP32 시간을 한국시간으로 설정 완료")
                
                self.time_synced = True
                return True
                
            except Exception as e:
                # print(f"[ERROR] {ntp_server} 동기화 실패: {e}")
                continue
        
        # print("[ERROR] 모든 NTP 서버 동기화 실패")
        return False
    
    def get_kst_time(self):
        """현재 한국 시간 반환"""
        # ESP32의 time.localtime()이 이미 한국 시간으로 설정되어 있음
        return time.localtime()
    
    def get_formatted_time(self):
        """포맷된 한국 시간 문자열 반환"""
        kst_time = self.get_kst_time()
        return f"{kst_time[0]:04d}-{kst_time[1]:02d}-{kst_time[2]:02d} {kst_time[3]:02d}:{kst_time[4]:02d}:{kst_time[5]:02d}"
    
    def get_time_sync_status(self):
        """시간 동기화 상태 반환"""
        return {
            'synced': self.time_synced,
            'kst_time': self.get_formatted_time()
        }

# 전역 인스턴스 (지연 초기화)
wifi_manager = None

def get_wifi_manager():
    """WiFi 매니저 인스턴스 반환 (지연 초기화)"""
    global wifi_manager
    if wifi_manager is None:
        wifi_manager = WiFiManager()
    return wifi_manager
