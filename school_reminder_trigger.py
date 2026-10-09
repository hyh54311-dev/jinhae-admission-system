try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

import requests
import json
import socket

# ----------------- 설정 ----------------- #
TELEGRAM_TOKEN = "8799464748:AAE5vGid7_UOfE9Q0h9kL_3uI0gVOfYOnmU" # Antigravity 봇 토큰
TELEGRAM_CHAT_ID = "8518409134"             # 사용자 ID
MESSAGE = "⏰ [Antigravity 리마인더] 학교 컴퓨터에서 텔레그램 봇 도약 및 자동 시작 설정을 완료해야 합니다.\n\n📌 작업: 'Setup_Autostart_on_SchoolPC.ps1' 파일을 마우스 우클릭하여 실행하세요."
# ---------------------------------------- #

def send_reminder():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": MESSAGE
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("??由щ쭏?몃뜑 諛쒖넚 ?깃났")
        else:
            print(f"??諛쒖넚 ?ㅽ뙣: {response.text}")
    except Exception as e:
        print(f"?좑툘 ?ㅻ쪟 諛쒖깮: {e}")

if __name__ == "__main__":
    send_reminder()
