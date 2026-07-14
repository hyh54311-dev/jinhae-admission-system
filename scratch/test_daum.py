import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_daum_api():
    candidates = ["U001", "KOSPI", "U180180"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://finance.daum.net/"
    }
    
    for symbol in candidates:
        url = f"https://finance.daum.net/api/investor/days?symbolCode={symbol}&page=1&perPage=5"
        try:
            print(f"Testing Symbol: {symbol} at {url}...")
            res = requests.get(url, headers=headers, verify=False, timeout=10)
            print(f"Status Code: {res.status_code}")
            print(f"Content length: {len(res.text)}")
            print(f"Response text start: {res.text[:500]}")
            print("-" * 50)
        except Exception as e:
            print(f"Error for {symbol}: {e}")

if __name__ == "__main__":
    test_daum_api()
