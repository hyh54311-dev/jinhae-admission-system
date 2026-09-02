import os
import time
import urllib.request
import urllib.parse
import ssl
from playwright.sync_api import sync_playwright

# 로그 파일 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "flight_alert_history.log")

# ===== 설정 =====
EMAIL_ADDRESS = "hyh54311@gmail.com"  
EMAIL_APP_PASSWORD = "obpv abgy acyh evho" 
TO_EMAIL = "hyh54311@gmail.com" 

# 구글 항공권 검색 URL (오키나와행)
URL = "https://www.google.com/travel/flights?q=Flights%20to%20OKA%20from%20PUS%20on%202026-09-24%20through%202026-09-27%20with%202%20adults%201%20child%20nonstop"

TELEGRAM_TOKEN = "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY"
TELEGRAM_CHAT_ID = "8518409134"
# ================

def log_message(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_message + "\n")
    except Exception as e:
        print(f"로그 기록 실패: {e}")

def send_telegram_alert():
    try:
        text = f"✈️ [항공권 발견 자동 알림]\n\n부산-오키나와 직항 예약이 오픈되었습니다!\n\n바로가기 링크: {URL}"
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': TELEGRAM_CHAT_ID, 'text': text}).encode('utf-8')
        req = urllib.request.Request(telegram_url, data=data)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        urllib.request.urlopen(req, context=ctx)
        log_message("텔레그램 항공권 알림 전송 완료!")
    except Exception as e:
        log_message(f"텔레그램 전송 실패: {e}")

def check_flights():
    log_message("항공권 상태 확인 시작...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(locale='ko-KR')
        page = context.new_page()
        
        try:
            page.goto(URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(10000) 
            content = page.locator("html").inner_text()
            
            no_result_msg = "반환된 결과가 없습니다."
            error_msg = "오류가 발생했습니다."
            price_symbol = "₩" # 원화 기호 확인
            
            if no_result_msg not in content and error_msg not in content and price_symbol in content:
                log_message("항공권 예약이 가능합니다! 알림을 발송합니다.")
                send_telegram_alert()
            else:
                log_message("아직 예약 가능한 항공권이 없거나 조건에 부합하지 않습니다.")
        except Exception as e:
            log_message(f"항공권 확인 중 오류 발생: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    log_message("항공권 감지 자동화가 사용자에 의해 임시 중단되었습니다. (다시 실행하려면 아래 check_flights() 주석을 해제하세요)")
    # check_flights()
