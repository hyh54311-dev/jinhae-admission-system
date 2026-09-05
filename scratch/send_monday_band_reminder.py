import urllib.request
import urllib.parse

TELEGRAM_TOKEN = "8407908239:AAHO81Ld-mmtJ-V5opl5vXI3bXgICiDrNgc"
TELEGRAM_CHAT_ID = "8518409134"

def send_telegram():
    text = """🎸 <b>[진해고 축제 교직원 밴드 & 월요일 아침 브리핑 알림]</b>

선생님, 좋은 아침입니다! 오늘 행정실장님(일렉 기타)께 이번 축제 때 선생님(통기타)과 함께하는 밴드 공연 제안을 말씀 나눠보시기로 하신 날입니다.

📋 <b>월요일 추천 소통 포인트:</b>
1. <b>자연스러운 연결고리:</b> 오늘 애향삼품 장학금 발전기금 지출품의(320만 원) 기안 결재선에 행정실장님이 협조자로 들어가시므로, 결재 관련 말씀 나누시거나 모닝 차담 때 자연스럽게 꺼내시기 좋습니다.
2. <b>선곡 팁:</b>
   • 안전빵 & 떼창 폭발형: DAY6 〈한 페이지가 될 수 있게〉, YB 〈나는 나비〉
   • 감성곡: 태연 〈만찬가〉 (반 학생들에게 넌지시 반응 체크 후 결정)
3. <b>세션 구성:</b> 드럼/베이스 등 부족한 파트는 밴드부 학생을 투입하면 멋진 사제동행 밴드가 완성됩니다.

오늘도 활기차고 기분 좋은 한 주 시작하세요! 😊"""

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print("Telegram notification sent successfully:", resp.status)
    except Exception as e:
        print("Telegram error:", e)

if __name__ == "__main__":
    send_telegram()
