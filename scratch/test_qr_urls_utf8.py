import sys
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

urls_to_test = [
    ("QR 1 (1-Click 템플릿/공개 저장소)", "https://github.com/hyh54311-dev/jinhae-admission-system"),
    ("QR 2 (한투 KIS Developers 포털)", "https://apiportal.koreainvestment.com"),
    ("QR 3 (한투 메인 포털 레퍼런스)", "https://apiportal.koreainvestment.com"),
    ("QR 4 (한투 공식 발급 가이드)", "https://apiportal.koreainvestment.com/intro"),
    ("QR 5 (한투 공식 open-trading-api 깃허브)", "https://github.com/koreainvestment/open-trading-api")
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

results = []
print("=== 5개 QR 코드 대상 URL 실시간 접속 검증 시작 ===")
for label, url in urls_to_test:
    try:
        res = requests.get(url, headers=headers, timeout=10, verify=False)
        status = res.status_code
        if status in (200, 301, 302):
            results.append((label, url, status, "SUCCESS (정상 접속 가능)"))
        else:
            results.append((label, url, status, f"FAIL (HTTP Status: {status})"))
    except Exception as e:
        results.append((label, url, "ERR", f"FAIL (Error: {e})"))

for label, url, status, result_str in results:
    print(f"[{label}]\n  - URL: {url}\n  - Status Code: {status}\n  - 결과: {result_str}\n")
