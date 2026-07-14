import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://jinhae-bot2.vercel.app/api/chat"
payload = {"message": "테스트 질문입니다. 구글 시트 기록이 잘 되나요?"}
data = json.dumps(payload).encode('utf-8')

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

try:
    print(f"Sending test POST to {url}...")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
        print("Status Code:", response.status)
        print("Response stream:")
        while True:
            chunk = response.read(100)
            if not chunk:
                break
            print(chunk.decode('utf-8', errors='ignore'), end="")
        print("\nStream completed.")
except Exception as e:
    print("Request failed:", e)
