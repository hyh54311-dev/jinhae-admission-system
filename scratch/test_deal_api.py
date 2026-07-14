import urllib3
import requests

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# requests.Session.send의 verify 인자를 False로 고정하는 패치 (교육청 방화벽 SSL 복호화 우회)
original_send = requests.Session.send
def patched_send(self, request, **kwargs):
    kwargs['verify'] = False
    return original_send(self, request, **kwargs)
requests.Session.send = patched_send

url = "https://m.stock.naver.com/api/index/KOSPI/deal?pageSize=5"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://m.stock.naver.com/"
}

try:
    print("m.stock.naver.com KOSPI deal API 호출 시도...")
    res = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {res.status_code}")
    print("Response Content (첫 1000자):")
    print(res.text[:1000])
except Exception as e:
    print(f"호출 실패: {e}")
