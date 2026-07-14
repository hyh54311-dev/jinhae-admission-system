import requests
import json
import socket

# ----------------- ?ㅼ젙 ----------------- #
TELEGRAM_TOKEN = "8799464748:AAE5vGid7_UOfE9Q0h9kL_3uI0gVOfYOnmU" # Antigravity 遊??좏겙
TELEGRAM_CHAT_ID = "8518409134"             # ?ъ슜??ID
MESSAGE = "?뵒 [Antigravity 由щ쭏?몃뜑] ?숆탳 而댄벂?곗뿉???붾젅洹몃옩 遊??뚯븙 諛??먮룞 ?쒖옉 ?ㅼ젙???꾨즺?댁빞 ?⑸땲??\n\n?뱧 ?묒뾽: 'Setup_Autostart_on_SchoolPC.ps1' ?뚯씪??留덉슦???고겢由?븯???ㅽ뻾?섏꽭??"
# ---------------------------------------- #

def send_reminder():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": MESSAGE
    }
    try:
        response = requests.post(url, json=payload, timeout=10, verify=False)
        if response.status_code == 200:
            print("??由щ쭏?몃뜑 諛쒖넚 ?깃났")
        else:
            print(f"??諛쒖넚 ?ㅽ뙣: {response.text}")
    except Exception as e:
        print(f"?좑툘 ?ㅻ쪟 諛쒖깮: {e}")

if __name__ == "__main__":
    send_reminder()
