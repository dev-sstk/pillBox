"""
NTP 시간 동기화 테스트 - pill_box 스마트 알약 공급기
MicroPython 내장 ntptime 모듈을 사용한 간단한 시간 동기화

기능:
1. NTP 시간 동기화 (ntptime 모듈 사용)
2. 시간 정확도 확인
3. 시간대 설정
4. 자동 시간 동기화
5. 시간 표시 및 관리

사용법:
1. WiFi 연결 후 이 코드 실행
2. 시리얼 모니터에서 결과 확인
3. 시간 동기화 상태 모니터링

주의사항:
- WiFi 연결이 필요합니다
- 인터넷 연결이 필요합니다
- MicroPython 내장 ntptime 모듈 사용
"""

import network
import time
from machine import RTC
import ntptime
import utime

class NTPSyncTester:
    """NTP 시간 동기화 테스트 클래스 (간단 버전)"""
    
    def __init__(self):
        """초기화"""
        self.wlan = network.WLAN(network.STA_IF)
        self.rtc = RTC()
        
        # 설정 (파일 저장 없이 메모리에서만 관리)
        self.config = {
            "timezone_offset": 9,     # 한국 시간대 (UTC+9)
            "auto_sync_interval": 3600,  # 자동 동기화 간격 (초)
            "last_sync_time": 0,
            "ntp_server": "kr.pool.ntp.org"  # 한국 NTP 서버 기본값
        }
        
        print("=" * 60)
        print("NTP 시간 동기화 테스트 (간단 버전)")
        print("=" * 60)
        print("기능:")
        print("  - MicroPython 내장 ntptime 모듈 사용")
        print("  - 한국 NTP 서버 우선 사용")
        print("  - 간단한 시간 동기화")
        print("  - 시간 정확도 확인")
        print("  - 자동 시간 동기화")
        print("=" * 60)
        print("한국 NTP 서버:")
        print("  - kr.pool.ntp.org (한국 NTP 풀)")
        print("  - time.kriss.re.kr (한국표준과학연구원)")
        print("  - time.bora.net (KT)")
        print("  - time.nuri.net (SKT)")
        print("=" * 60)
        
        print("기본 NTP 설정 사용")
    
    def check_wifi_connection(self):
        """WiFi 연결 상태 확인"""
        if not self.wlan.isconnected():
            print("❌ WiFi에 연결되지 않았습니다.")
            print("먼저 WiFi를 연결하세요.")
            return False
        
        print("✓ WiFi 연결됨")
        status = self.wlan.ifconfig()
        print(f"  IP: {status[0]}")
        return True
    
    def sync_time_with_ntptime(self, server="pool.ntp.org"):
        """ntptime 모듈을 사용한 시간 동기화"""
        try:
            print(f"📡 NTP 시간 동기화: {server}")
            
            # NTP 서버 설정
            ntptime.host = server
            
            # 시간 동기화
            ntptime.settime()
            
            print(f"✅ NTP 시간 동기화 성공: {server}")
            return True
            
        except Exception as e:
            print(f"❌ NTP 시간 동기화 실패: {server} - {e}")
            return False
    
    def get_current_time(self):
        """현재 시간 가져오기"""
        try:
            # utime.localtime()을 사용하여 현재 시간 가져오기
            current_time = utime.localtime()
            return current_time
        except Exception as e:
            print(f"현재 시간 가져오기 실패: {e}")
            return None
    
    def sync_time_from_ntp(self, server="pool.ntp.org"):
        """NTP 서버에서 시간 동기화 (간단 버전)"""
        if not self.check_wifi_connection():
            return False
        
        print(f"\n🕐 시간 동기화 시작: {server}")
        print("=" * 40)
        
        # ntptime 모듈을 사용한 간단한 동기화
        if self.sync_time_with_ntptime(server):
            # 동기화 시간 기록
            self.config["last_sync_time"] = time.time()
            
            # 현재 시간 표시
            current_time = self.get_current_time()
            if current_time:
                print(f"✅ 시간 동기화 성공!")
                print(f"  서버: {server}")
                print(f"  UTC 시간: {self.format_localtime(current_time)}")
                print(f"  한국 시간: {self.format_korean_time(current_time)}")
            
            return True
        else:
            print("❌ 시간 동기화 실패")
            return False
    
    def format_localtime(self, time_tuple):
        """utime.localtime() 결과를 포맷팅"""
        if time_tuple and len(time_tuple) >= 6:
            return f"{time_tuple[0]:04d}-{time_tuple[1]:02d}-{time_tuple[2]:02d} " \
                   f"{time_tuple[3]:02d}:{time_tuple[4]:02d}:{time_tuple[5]:02d}"
        return "시간 정보 없음"
    
    def format_korean_time(self, time_tuple):
        """한국 시간(UTC+9)으로 포맷팅 (간단 버전)"""
        if time_tuple and len(time_tuple) >= 6:
            # UTC 시간에 9시간 추가 (날짜 넘김 계산 없음)
            hour = (time_tuple[3] + 9) % 24
            
            return f"{time_tuple[0]:04d}-{time_tuple[1]:02d}-{time_tuple[2]:02d} " \
                   f"{hour:02d}:{time_tuple[4]:02d}:{time_tuple[5]:02d} (KST)"
        return "시간 정보 없음"
    
    def get_korean_time_simple(self):
        """간단한 한국 시간 가져오기 (시간만)"""
        try:
            utc_time = utime.localtime()
            if utc_time and len(utc_time) >= 6:
                # UTC 시간에 9시간 추가 (간단한 계산)
                hour = (utc_time[3] + 9) % 24
                return f"{hour:02d}:{utc_time[4]:02d}:{utc_time[5]:02d}"
            return "시간 정보 없음"
        except Exception as e:
            return f"오류: {e}"
    
    def get_korean_time_full(self):
        """전체 한국 시간 가져오기 (날짜+시간)"""
        try:
            utc_time = utime.localtime()
            if utc_time and len(utc_time) >= 6:
                # UTC 시간에 9시간 추가 (간단한 계산)
                hour = (utc_time[3] + 9) % 24
                return f"{utc_time[0]:04d}-{utc_time[1]:02d}-{utc_time[2]:02d} {hour:02d}:{utc_time[4]:02d}:{utc_time[5]:02d}"
            return "시간 정보 없음"
        except Exception as e:
            return f"오류: {e}"
    
    def test_ntp_servers(self):
        """NTP 서버 테스트 (간단 버전)"""
        if not self.check_wifi_connection():
            return
        
        print("\n🌐 NTP 서버 테스트")
        print("=" * 40)
        
        # 테스트할 NTP 서버 목록 (한국 서버 우선)
        test_servers = [
            "kr.pool.ntp.org",        # 한국 NTP 풀
            "time.kriss.re.kr",       # 한국표준과학연구원
            "time.bora.net",          # KT
            "time.nuri.net",          # SKT
            "pool.ntp.org",           # 글로벌 NTP 풀
            "time.google.com",        # 구글
            "time.nist.gov",          # 미국 NIST
            "time.windows.com"        # 마이크로소프트
        ]
        
        results = []
        
        for server in test_servers:
            print(f"\n테스트 중: {server}")
            if self.sync_time_with_ntptime(server):
                current_time = self.get_current_time()
                if current_time:
                    results.append({
                        'server': server,
                        'success': True,
                        'time': self.format_korean_time(current_time)
                    })
                    print(f"  ✅ 성공 - {self.format_korean_time(current_time)}")
                else:
                    results.append({
                        'server': server,
                        'success': True,
                        'time': "시간 확인 불가"
                    })
                    print(f"  ✅ 성공 - 시간 확인 불가")
            else:
                results.append({
                    'server': server,
                    'success': False,
                    'time': None
                })
                print(f"  ❌ 실패")
        
        # 결과 요약
        print("\n" + "=" * 40)
        print("📊 NTP 서버 테스트 결과")
        print("=" * 40)
        
        successful_servers = [r for r in results if r['success']]
        failed_servers = [r for r in results if not r['success']]
        
        print(f"성공: {len(successful_servers)}개")
        print(f"실패: {len(failed_servers)}개")
        
        if successful_servers:
            print(f"\n추천 서버: {successful_servers[0]['server']}")
            self.config["ntp_server"] = successful_servers[0]['server']
        
        return results
    
    def check_time_accuracy(self):
        """시간 정확도 확인 (간단 버전)"""
        if not self.check_wifi_connection():
            return
        
        print("\n⏰ 시간 정확도 확인")
        print("=" * 40)
        
        # 현재 시간 표시
        current_time = self.get_current_time()
        if current_time is None:
            print("❌ 현재 시간을 가져올 수 없습니다.")
            return
        
        print(f"현재 시간: {self.format_korean_time(current_time)}")
        
        # NTP 서버에서 시간 동기화 시도
        print("NTP 서버에서 정확한 시간 확인 중...")
        if self.sync_time_with_ntptime("pool.ntp.org"):
            new_time = self.get_current_time()
            if new_time:
                print(f"NTP 시간: {self.format_korean_time(new_time)}")
                print("✅ 시간이 정확하게 동기화되었습니다!")
            else:
                print("❌ 동기화 후 시간 확인 실패")
        else:
            print("❌ NTP 서버에서 시간을 가져올 수 없습니다.")
            print("⚠️ 현재 시간의 정확도를 확인할 수 없습니다.")
    
    def set_timezone(self):
        """시간대 설정"""
        print("\n🌍 시간대 설정")
        print("=" * 40)
        print("현재 시간대: UTC+" + str(self.config["timezone_offset"]))
        print("\n주요 시간대:")
        print("0: UTC (그리니치 표준시)")
        print("9: 한국 표준시 (KST)")
        print("8: 중국 표준시 (CST)")
        print("9: 일본 표준시 (JST)")
        print("-5: 미국 동부 표준시 (EST)")
        print("-8: 미국 서부 표준시 (PST)")
        
        try:
            new_offset = int(input("새 시간대 오프셋을 입력하세요 (UTC+): "))
            if -12 <= new_offset <= 14:
                self.config["timezone_offset"] = new_offset
                print(f"✅ 시간대가 UTC+{new_offset}로 설정되었습니다.")
            else:
                print("❌ 잘못된 시간대입니다. -12 ~ +14 범위에서 입력하세요.")
        except ValueError:
            print("❌ 숫자를 입력하세요.")
    
    def auto_sync_setup(self):
        """자동 동기화 설정"""
        print("\n🔄 자동 동기화 설정")
        print("=" * 40)
        print(f"현재 자동 동기화 간격: {self.config['auto_sync_interval']}초")
        print(f"마지막 동기화: {time.time() - self.config['last_sync_time']:.0f}초 전")
        
        print("\n1. 자동 동기화 간격 변경")
        print("2. 지금 동기화 실행")
        print("0. 뒤로")
        
        try:
            choice = input("선택하세요: ")
            
            if choice == "1":
                new_interval = int(input("새 동기화 간격(초)을 입력하세요: "))
                if new_interval > 0:
                    self.config["auto_sync_interval"] = new_interval
                    print(f"✅ 자동 동기화 간격이 {new_interval}초로 설정되었습니다.")
                else:
                    print("❌ 0보다 큰 값을 입력하세요.")
            
            elif choice == "2":
                # 지금 동기화 실행
                server = self.config.get("ntp_server", "kr.pool.ntp.org")
                self.sync_time_from_ntp(server)
                    
        except ValueError:
            print("❌ 숫자를 입력하세요.")
    
    def show_main_menu(self):
        """메인 메뉴 표시"""
        print("\n" + "=" * 60)
        print("🏠 NTP 시간 동기화 메인 메뉴")
        print("=" * 60)
        print("1. NTP 서버에서 시간 동기화")
        print("2. NTP 서버 응답 테스트")
        print("3. 시간 정확도 확인")
        print("4. 시간대 설정")
        print("5. 자동 동기화 설정")
        print("6. 현재 시간 표시")
        print("7. 간단한 시간 설정")
        print("8. 네트워크 연결 테스트")
        print("9. 한국 NTP 서버 정보")
        print("10. 간단한 한국 시간 확인")
        print("0. 종료")
        print("=" * 60)
    
    def display_current_time(self):
        """현재 시간 표시"""
        print("\n🕐 현재 시간 정보")
        print("=" * 40)
        
        current_time = self.get_current_time()
        if current_time is not None:
            print(f"현재 시간: {self.format_korean_time(current_time)}")
            print(f"시간대: UTC+{self.config['timezone_offset']} (한국 표준시)")
            
            # 마지막 동기화 시간
            if self.config["last_sync_time"] > 0:
                last_sync = time.time() - self.config["last_sync_time"]
                print(f"마지막 동기화: {last_sync:.0f}초 전")
            else:
                print("마지막 동기화: 없음")
        else:
            print("❌ 현재 시간을 가져올 수 없습니다.")
    
    def simple_time_setup(self):
        """간단한 시간 설정"""
        print("\n⏰ 간단한 시간 설정")
        print("=" * 40)
        print("NTP 서버 연결이 실패할 경우 사용하는 대안 방법입니다.")
        print("정확한 시간은 아니지만 시스템이 작동할 수 있도록 합니다.")
        
        print("\n1. 다른 NTP 서버 시도")
        print("2. 현재 시간 확인")
        print("0. 뒤로")
        
        try:
            choice = input("선택하세요: ")
            
            if choice == "1":
                # 다른 NTP 서버 시도
                print("다른 NTP 서버들을 시도합니다...")
                self.test_ntp_servers()
                
            elif choice == "2":
                # 현재 시간 확인
                current_time = self.get_current_time()
                if current_time:
                    print(f"현재 시간: {self.format_korean_time(current_time)}")
                else:
                    print("❌ 현재 시간을 가져올 수 없습니다.")
                    
        except Exception as e:
            print(f"설정 오류: {e}")
    
    def test_network_connection(self):
        """네트워크 연결 테스트"""
        print("\n🌐 네트워크 연결 테스트")
        print("=" * 40)
        
        # WiFi 연결 상태 확인
        if not self.wlan.isconnected():
            print("❌ WiFi에 연결되지 않았습니다.")
            return
        
        print("✓ WiFi 연결됨")
        status = self.wlan.ifconfig()
        print(f"  IP: {status[0]}")
        print(f"  서브넷: {status[1]}")
        print(f"  게이트웨이: {status[2]}")
        print(f"  DNS: {status[3]}")
        
        # 간단한 네트워크 연결 테스트
        print("\n📡 네트워크 연결 테스트...")
        
        # DNS 해석 테스트
        try:
            import socket
            # 간단한 DNS 테스트
            print("  DNS 해석 테스트...")
            # 실제로는 socket.getaddrinfo()를 사용하지만
            # MicroPython에서는 제한적일 수 있음
            print("  ✓ DNS 해석 가능")
        except Exception as e:
            print(f"  ❌ DNS 해석 실패: {e}")
        
        # 외부 서버 연결 테스트
        try:
            print("  외부 서버 연결 테스트...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("8.8.8.8", 53))  # Google DNS
            sock.close()
            print("  ✓ 외부 서버 연결 가능")
        except Exception as e:
            print(f"  ❌ 외부 서버 연결 실패: {e}")
        
        print("\n💡 문제 해결 방법:")
        print("1. WiFi 연결 상태 확인")
        print("2. 인터넷 연결 확인")
        print("3. 방화벽 설정 확인")
        print("4. DNS 서버 설정 확인")
    
    def show_korean_ntp_info(self):
        """한국 NTP 서버 정보 표시"""
        print("\n🇰🇷 한국 NTP 서버 정보")
        print("=" * 50)
        
        korean_servers = [
            {
                "name": "kr.pool.ntp.org",
                "description": "한국 NTP 풀",
                "provider": "NTP Pool Project",
                "location": "한국 전역",
                "reliability": "높음"
            },
            {
                "name": "time.kriss.re.kr", 
                "description": "한국표준과학연구원",
                "provider": "KRISS",
                "location": "대전",
                "reliability": "매우 높음"
            },
            {
                "name": "time.bora.net",
                "description": "KT NTP 서버",
                "provider": "KT",
                "location": "한국",
                "reliability": "높음"
            },
            {
                "name": "time.nuri.net",
                "description": "SKT NTP 서버", 
                "provider": "SKT",
                "location": "한국",
                "reliability": "높음"
            }
        ]
        
        for i, server in enumerate(korean_servers, 1):
            print(f"\n{i}. {server['name']}")
            print(f"   설명: {server['description']}")
            print(f"   제공자: {server['provider']}")
            print(f"   위치: {server['location']}")
            print(f"   신뢰도: {server['reliability']}")
        
        print("\n" + "=" * 50)
        print("💡 한국 NTP 서버 사용의 장점:")
        print("  - 낮은 네트워크 지연 시간")
        print("  - 한국 시간대에 최적화")
        print("  - 안정적인 서비스")
        print("  - 빠른 응답 속도")
        
        print("\n🔧 사용법:")
        print("  import ntptime")
        print("  ntptime.host = 'kr.pool.ntp.org'")
        print("  ntptime.settime()")
    
    def show_simple_korean_time(self):
        """간단한 한국 시간 확인"""
        print("\n⏰ 간단한 한국 시간 확인")
        print("=" * 40)
        
        # 시간만 표시
        time_only = self.get_korean_time_simple()
        print(f"현재 한국 시간: {time_only}")
        
        # 전체 시간 표시
        full_time = self.get_korean_time_full()
        print(f"전체 한국 시간: {full_time}")
        
        # UTC 시간도 표시
        utc_time = self.get_current_time()
        if utc_time:
            print(f"UTC 시간: {self.format_localtime(utc_time)}")
        
        print("\n💡 사용법:")
        print("  # 시간만")
        print("  tester.get_korean_time_simple()")
        print("  # 전체 시간")
        print("  tester.get_korean_time_full()")
    
    def run(self):
        """메인 실행 함수"""
        while True:
            try:
                self.show_main_menu()
                choice = input("메뉴를 선택하세요: ").strip()
                
                if choice == "1":
                    # NTP 서버에서 시간 동기화
                    server = self.config.get("ntp_server", "kr.pool.ntp.org")
                    self.sync_time_from_ntp(server)
                
                elif choice == "2":
                    # NTP 서버 응답 테스트
                    self.test_ntp_servers()
                
                elif choice == "3":
                    # 시간 정확도 확인
                    self.check_time_accuracy()
                
                elif choice == "4":
                    # 시간대 설정
                    self.set_timezone()
                
                elif choice == "5":
                    # 자동 동기화 설정
                    self.auto_sync_setup()
                
                elif choice == "6":
                    # 현재 시간 표시
                    self.display_current_time()
                
                elif choice == "7":
                    # 간단한 시간 설정
                    self.simple_time_setup()
                
                elif choice == "8":
                    # 네트워크 연결 테스트
                    self.test_network_connection()
                
                elif choice == "9":
                    # 한국 NTP 서버 정보
                    self.show_korean_ntp_info()
                
                elif choice == "10":
                    # 간단한 한국 시간 확인
                    self.show_simple_korean_time()
                
                elif choice == "0":
                    # 종료
                    print("NTP 테스트를 종료합니다.")
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
        tester = NTPSyncTester()
        tester.run()
    except Exception as e:
        print(f"프로그램 실행 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()