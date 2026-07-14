import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_via_gas():
    gas_url = "https://script.google.com/macros/s/AKfycbyyb-twRpcch3HxeGDmlJ3CvdI8YlrBgMd995NHCaSNosBw4i3oQaIkN5BltNXkHKxk/exec"
    
    # We want to test different symbol codes for KOSPI index investor trend in Daum:
    # 1. symbolCode=U001
    # 2. symbolCode=KOSPI (some APIs use this)
    # 3. symbolCode=DJI (Dow Jones, for comparison)
    # 4. symbolCode=A005930 (Samsung Electronics, to see if stock works)
    
    targets = [
        ("U001", "https://finance.daum.net/api/investor/days?symbolCode=U001&page=1&perPage=5"),
        ("A005930", "https://finance.daum.net/api/investor/days?symbolCode=A005930&page=1&perPage=5")
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for name, target_url in targets:
        print(f"Testing {name} via GAS...")
        # If the GAS app is a general proxy, it will fetch target_url
        params = {"url": target_url}
        try:
            res = requests.get(gas_url, params=params, verify=False, timeout=15)
            print(f"Status Code: {res.status_code}")
            print(f"Response Length: {len(res.text)}")
            print(f"Start of response:\n{res.text[:1000]}")
            print("-" * 60)
        except Exception as e:
            print(f"Error for {name}: {e}")

if __name__ == "__main__":
    test_via_gas()
