import os
import sys
import requests
import io
from dotenv import load_dotenv

# Force UTF-8 for stdout/stderr
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

# Load environmental variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8518409134")

reminder_text = (
    "📞 [Antigravity 예약 리마인더]\n\n"
    "선생님, 오늘 오전 11시는 내일(화요일) 교무부 회식 장소인 **진해 푸름각**의 예약 전화를 하실 시간입니다.\n\n"
    "■ 매장 정보:\n"
    "- 매장명: 푸름각 (진해 소재 중식당)\n"
    "- 전화번호: 055-546-5557\n"
    "- 오픈 시간: 오전 11:00 (월요일 휴무)\n\n"
    "평일에도 인기 메뉴인 탕수육찜 등을 맛보러 오는 손님들로 12시 전후나 퇴근 직후 시간대에 자리가 빠르게 만석이 됩니다.\n"
    "지금 전화하셔서 교무부 단체 인원과 예약 시간 조율을 완료하시는 것을 추천합니다!"
)

def send_telegram():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": reminder_text,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload, timeout=15, verify=False)
        if r.status_code == 200:
            print("Telegram message sent successfully.")
        else:
            print(f"Failed to send Telegram: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Telegram error: {e}")

if __name__ == '__main__':
    send_telegram()
