import requests
import json
import urllib3
import sys

# Configure stdout to use UTF-8
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    url = "https://m.stock.naver.com/api/index/KOSPI/investorTrend?pageSize=30"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Referer": "https://m.stock.naver.com/"
    }
    
    print(f"Fetching: {url}")
    # The agent sandbox is not firewalled, so we can make direct external requests
    try:
        res = requests.get(url, headers=headers, verify=False, timeout=15)
        print(f"Status: {res.status_code}")
        try:
            data = res.json()
            print("Successfully parsed JSON!")
            print(f"Response (first 1000 chars): {json.dumps(data, indent=2, ensure_ascii=False)[:1000]}")
        except Exception as e:
            print("Failed to parse JSON!")
            print(f"Response text: {res.text[:500]}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    main()
