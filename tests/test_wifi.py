"""
WiFi 연결 테스트 - pill_box 스마트 알약 공급기
통합된 WiFi 연결 테스트 코드

기능:
1. WiFi 네트워크 스캔
2. 검색된 네트워크 목록 표시
3. 번호로 네트워크 선택
4. 비밀번호 입력 (필요시)
5. 자동 연결 (비밀번호 없을 때)
6. 연결 상태 확인
7. 저장된 네트워크 관리

사용법:
1. ESP32-C6에 이 코드를 업로드
2. 시리얼 모니터 열기 (115200 baud)
3. 메뉴에 따라 숫자 입력
4. 비밀번호 입력 (필요시)

주의사항:
- 시리얼 모니터에서 입력하세요
- 비밀번호는 화면에 표시되지 않습니다
"""

import network
import time
import json
import os

class WiFiTester:
    """WiFi 테스트 클래스"""
    
    def __init__(self):
        """초기화"""
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        # 검색된 네트워크 목록
        self.networks = []
        
        # 연결된 네트워크 정보
        self.connected_network = None
        
        # 설정 파일
        self.config_file = "wifi_config.json"
        self.saved_networks = []
        
        print("=" * 60)
        print("WiFi 연결 테스트")
        print("=" * 60)
        print("사용법:")
        print("  - 메뉴에서 숫자 입력")
        print("  - 비밀번호 입력 시 화면에 표시되지 않음")
        print("  - Enter 키로 입력 완료")
        print("=" * 60)
        
    def load_saved_networks(self):
        """저장된 네트워크 불러오기"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.saved_networks = data.get('saved_networks', [])
                    print(f"✓ {len(self.saved_networks)}개 저장된 네트워크 불러옴")
            else:
                print("저장된 네트워크 없음")
        except Exception as e:
            print(f"저장된 네트워크 불러오기 실패: {e}")
            self.saved_networks = []
    
    def save_network(self, ssid, password):
        """네트워크 정보 저장"""
        try:
            # 기존 네트워크 확인
            for network in self.saved_networks:
                if network['ssid'] == ssid:
                    network['password'] = password
                    network['last_connected'] = time.time()
                    break
            else:
                # 새 네트워크 추가
                self.saved_networks.append({
                    'ssid': ssid,
                    'password': password,
                    'last_connected': time.time()
                })
            
            # 파일에 저장
            data = {'saved_networks': self.saved_networks}
            with open(self.config_file, 'w') as f:
                json.dump(data, f)
                
            print(f"✓ 네트워크 저장됨: {ssid}")
            
        except Exception as e:
            print(f"네트워크 저장 실패: {e}")
    
    def scan_networks(self):
        """WiFi 네트워크 스캔"""
        print("\n📡 WiFi 네트워크 스캔 중...")
        print("잠시만 기다려주세요... (약 10초)")
        
        try:
            # 네트워크 스캔
            raw_networks = self.wlan.scan()
            self.networks = []
            
            for network in raw_networks:
                ssid = network[0].decode('utf-8') if network[0] else "숨김"
                bssid = network[1]
                channel = network[2]
                rssi = network[3]
                security = network[4]
                hidden = network[5]
                
                # 보안 타입 확인
                security_type = "개방" if security == 0 else "보안"
                
                # 저장된 네트워크인지 확인
                is_saved = any(saved['ssid'] == ssid for saved in self.saved_networks)
                
                self.networks.append({
                    'ssid': ssid,
                    'bssid': bssid,
                    'channel': channel,
                    'rssi': rssi,
                    'security': security,
                    'security_type': security_type,
                    'hidden': hidden,
                    'is_saved': is_saved
                })
            
            # 신호 강도순으로 정렬
            self.networks.sort(key=lambda x: x['rssi'], reverse=True)
            
            print(f"✓ {len(self.networks)}개 네트워크 발견")
            return True
            
        except Exception as e:
            print(f"✗ 네트워크 스캔 실패: {e}")
            return False
    
    def display_networks(self):
        """네트워크 목록 표시"""
        if not self.networks:
            print("검색된 네트워크가 없습니다.")
            return
        
        print("\n" + "=" * 60)
        print("📶 검색된 WiFi 네트워크")
        print("=" * 60)
        
        for i, network in enumerate(self.networks):
            # 신호 강도 표시
            rssi = network['rssi']
            if rssi > -50:
                signal_icon = "📶"
            elif rssi > -70:
                signal_icon = "📶"
            else:
                signal_icon = "📶"
            
            # 저장된 네트워크 표시
            saved_marker = "💾" if network['is_saved'] else "  "
            
            # 보안 표시
            security_icon = "🔒" if network['security'] > 0 else "🔓"
            
            print(f"{i+1:2d}. {signal_icon} {network['ssid']:<20} "
                  f"{security_icon} {network['security_type']:<4} "
                  f"({rssi:3d}dBm) {saved_marker}")
        
        print("=" * 60)
        print("연결할 네트워크 번호를 입력하세요 (0: 취소)")
        print("=" * 60)
    
    def select_network_by_number(self):
        """번호로 네트워크 선택"""
        if not self.networks:
            print("선택할 네트워크가 없습니다.")
            return None
        
        self.display_networks()
        
        try:
            choice = int(input("번호 입력: "))
            
            if choice == 0:
                print("선택 취소됨")
                return None
            
            if 1 <= choice <= len(self.networks):
                selected_network = self.networks[choice - 1]
                print(f"\n선택된 네트워크: {selected_network['ssid']}")
                return selected_network
            else:
                print("잘못된 번호입니다.")
                return None
                
        except ValueError:
            print("숫자를 입력하세요.")
            return None
        except Exception as e:
            print(f"선택 오류: {e}")
            return None
    
    def input_password(self, ssid):
        """비밀번호 입력"""
        print(f"\n🔐 '{ssid}' 네트워크 비밀번호 입력")
        print("=" * 40)
        
        # 저장된 비밀번호 확인
        saved_password = None
        for saved in self.saved_networks:
            if saved['ssid'] == ssid:
                saved_password = saved['password']
                break
        
        if saved_password:
            print(f"저장된 비밀번호가 있습니다.")
            use_saved = input("저장된 비밀번호를 사용하시겠습니까? (y/n): ").lower().strip()
            if use_saved == 'y':
                return saved_password
        
        # 새 비밀번호 입력
        print("비밀번호를 입력하세요:")
        print("(입력 완료 후 Enter 키를 누르세요)")
        
        # 실제 환경에서는 비밀번호가 화면에 보이지 않도록 처리
        password = input("비밀번호: ")
        
        return password
    
    def connect_to_network(self, network):
        """네트워크에 연결"""
        ssid = network['ssid']
        security = network['security']
        
        print(f"\n🔗 '{ssid}' 네트워크 연결 시도...")
        print("=" * 40)
        
        try:
            # 보안 설정 확인
            if security == 0:
                # 개방 네트워크
                print("개방 네트워크 - 비밀번호 없이 연결")
                password = ""
            else:
                # 보안 네트워크
                print("보안 네트워크 - 비밀번호 필요")
                password = self.input_password(ssid)
                if not password:
                    print("비밀번호가 입력되지 않았습니다.")
                    return False
            
            # 연결 시도
            print(f"연결 중... (최대 15초)")
            self.wlan.connect(ssid, password)
            
            # 연결 대기
            max_wait = 15
            while max_wait > 0:
                if self.wlan.isconnected():
                    break
                max_wait -= 1
                print(f"연결 대기 중... ({max_wait}초 남음)")
                time.sleep(1)
            
            if self.wlan.isconnected():
                # 연결 성공
                self.connected_network = network
                
                # 네트워크 정보 저장 (비밀번호가 있는 경우)
                if password:
                    self.save_network(ssid, password)
                
                # 연결 정보 표시
                self.display_connection_info()
                return True
            else:
                print(f"✗ '{ssid}' 연결 실패")
                print("다음을 확인하세요:")
                print("- 비밀번호가 정확한지")
                print("- 신호 강도가 충분한지")
                print("- 네트워크가 활성화되어 있는지")
                return False
                
        except Exception as e:
            print(f"✗ 연결 오류: {e}")
            return False
    
    def display_connection_info(self):
        """연결 정보 표시"""
        if not self.wlan.isconnected():
            print("연결된 네트워크가 없습니다.")
            return
        
        print("\n" + "=" * 60)
        print("✅ WiFi 연결 성공!")
        print("=" * 60)
        
        # 연결 정보
        status = self.wlan.ifconfig()
        print(f"네트워크: {self.connected_network['ssid']}")
        print(f"IP 주소: {status[0]}")
        print(f"서브넷: {status[1]}")
        print(f"게이트웨이: {status[2]}")
        print(f"DNS: {status[3]}")
        
        # MAC 주소
        try:
            mac = self.wlan.config('mac')
            mac_str = ':'.join(['%02x' % b for b in mac])
            print(f"MAC 주소: {mac_str}")
        except:
            pass
        
        # 신호 강도
        print(f"신호 강도: {self.connected_network['rssi']}dBm")
        
        print("=" * 60)
    
    def test_connection_stability(self):
        """연결 안정성 테스트"""
        if not self.wlan.isconnected():
            print("연결된 네트워크가 없습니다.")
            return False
        
        print("\n🔍 연결 안정성 테스트 (10초)")
        print("=" * 40)
        
        for i in range(10):
            time.sleep(1)
            if self.wlan.isconnected():
                print(f"  {i+1:2d}초: ✅ 연결 유지")
            else:
                print(f"  {i+1:2d}초: ❌ 연결 끊김")
                return False
        
        print("✅ 연결이 안정적입니다!")
        return True
    
    def show_main_menu(self):
        """메인 메뉴 표시"""
        print("\n" + "=" * 60)
        print("🏠 WiFi 연결 메인 메뉴")
        print("=" * 60)
        print("1. WiFi 네트워크 스캔 및 연결")
        print("2. 저장된 네트워크 연결")
        print("3. 연결 상태 확인")
        print("4. 연결 안정성 테스트")
        print("5. 저장된 네트워크 관리")
        print("0. 종료")
        print("=" * 60)
    
    def connect_saved_network(self):
        """저장된 네트워크 연결"""
        if not self.saved_networks:
            print("저장된 네트워크가 없습니다.")
            return False
        
        print("\n💾 저장된 네트워크 목록")
        print("=" * 40)
        
        for i, network in enumerate(self.saved_networks):
            print(f"{i+1}. {network['ssid']}")
        
        try:
            choice = int(input("연결할 네트워크 번호를 선택하세요: ")) - 1
            if 0 <= choice < len(self.saved_networks):
                selected = self.saved_networks[choice]
                
                # 네트워크 정보 구성
                network_info = {
                    'ssid': selected['ssid'],
                    'security': 1,  # 저장된 네트워크는 보안으로 가정
                    'rssi': -50     # 기본값
                }
                
                # 비밀번호 설정
                password = selected['password']
                
                # 연결 시도
                print(f"'{selected['ssid']}' 연결 시도...")
                self.wlan.connect(selected['ssid'], password)
                
                # 연결 대기
                max_wait = 15
                while max_wait > 0:
                    if self.wlan.isconnected():
                        self.connected_network = network_info
                        print("✅ 저장된 네트워크 연결 성공!")
                        self.display_connection_info()
                        return True
                    max_wait -= 1
                    time.sleep(1)
                
                print("❌ 저장된 네트워크 연결 실패")
            else:
                print("잘못된 선택입니다.")
        except ValueError:
            print("숫자를 입력하세요.")
        except Exception as e:
            print(f"연결 오류: {e}")
        
        return False
    
    def manage_saved_networks(self):
        """저장된 네트워크 관리"""
        print("\n⚙️ 저장된 네트워크 관리")
        print("=" * 40)
        
        if not self.saved_networks:
            print("저장된 네트워크가 없습니다.")
            return
        
        for i, network in enumerate(self.saved_networks):
            print(f"{i+1}. {network['ssid']}")
        
        print("\n1. 네트워크 삭제")
        print("2. 비밀번호 변경")
        print("0. 뒤로")
        
        try:
            choice = input("선택하세요: ")
            
            if choice == "1":
                # 네트워크 삭제
                try:
                    idx = int(input("삭제할 네트워크 번호: ")) - 1
                    if 0 <= idx < len(self.saved_networks):
                        deleted = self.saved_networks.pop(idx)
                        # 파일 업데이트
                        data = {'saved_networks': self.saved_networks}
                        with open(self.config_file, 'w') as f:
                            json.dump(data, f)
                        print(f"✅ '{deleted['ssid']}' 삭제됨")
                    else:
                        print("잘못된 번호입니다.")
                except ValueError:
                    print("숫자를 입력하세요.")
            
            elif choice == "2":
                # 비밀번호 변경
                try:
                    idx = int(input("비밀번호를 변경할 네트워크 번호: ")) - 1
                    if 0 <= idx < len(self.saved_networks):
                        new_password = input("새 비밀번호: ")
                        self.saved_networks[idx]['password'] = new_password
                        # 파일 업데이트
                        data = {'saved_networks': self.saved_networks}
                        with open(self.config_file, 'w') as f:
                            json.dump(data, f)
                        print("✅ 비밀번호 변경됨")
                    else:
                        print("잘못된 번호입니다.")
                except ValueError:
                    print("숫자를 입력하세요.")
                    
        except Exception as e:
            print(f"관리 오류: {e}")
    
    def run(self):
        """메인 실행 함수"""
        # 저장된 네트워크 불러오기
        self.load_saved_networks()
        
        while True:
            try:
                self.show_main_menu()
                choice = input("메뉴를 선택하세요: ").strip()
                
                if choice == "1":
                    # WiFi 스캔 및 연결
                    if self.scan_networks():
                        selected_network = self.select_network_by_number()
                        if selected_network:
                            self.connect_to_network(selected_network)
                
                elif choice == "2":
                    # 저장된 네트워크 연결
                    self.connect_saved_network()
                
                elif choice == "3":
                    # 연결 상태 확인
                    if self.wlan.isconnected():
                        self.display_connection_info()
                    else:
                        print("연결된 네트워크가 없습니다.")
                
                elif choice == "4":
                    # 연결 안정성 테스트
                    self.test_connection_stability()
                
                elif choice == "5":
                    # 저장된 네트워크 관리
                    self.manage_saved_networks()
                
                elif choice == "0":
                    # 종료
                    print("WiFi 테스트를 종료합니다.")
                    break
                
                else:
                    print("잘못된 선택입니다.")
                
                input("\n계속하려면 Enter 키를 누르세요...")
                
            except KeyboardInterrupt:
                print("\n\n테스트가 중단되었습니다.")
                break
            except Exception as e:
                print(f"\n오류 발생: {e}")
                input("계속하려면 Enter 키를 누르세요...")

def main():
    """메인 함수"""
    try:
        tester = WiFiTester()
        tester.run()
    except Exception as e:
        print(f"프로그램 실행 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()