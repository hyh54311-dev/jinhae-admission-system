import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_paxnet():
    url = "https://paxnet.co.kr/trading/investorTrend"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://paxnet.co.kr/"
    }
    
    try:
        print(f"Fetching Paxnet: {url}...")
        res = requests.get(url, headers=headers, verify=False, timeout=10)
        print(f"Status Code: {res.status_code}")
        print(f"Content Length: {len(res.text)}")
        print("Response text start:")
        print(res.text[:1000])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_paxnet()
