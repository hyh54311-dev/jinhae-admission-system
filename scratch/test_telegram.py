# -*- coding: utf-8 -*-
import os
import sys
import requests
from dotenv import load_dotenv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(parent_dir, ".env")
load_dotenv(dotenv_path)

TOKEN = os.getenv("TELEGRAM_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

print(f"■ 텔레그램 설정:")
print(f"   - Token: {TOKEN[:10]}...{TOKEN[-5:] if len(TOKEN) > 5 else ''}")
print(f"   - Chat ID: {CHAT_ID}")

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": "🤖 [Antigravity 테스트] 텔레그램 연동 테스트 메시지입니다."
}

try:
    res = requests.post(url, json=payload, timeout=10, verify=False)
    print(f"HTTP Status Code: {res.status_code}")
    print(f"Response Body: {res.text}")
except Exception as e:
    print(f"오류 발생: {e}")
