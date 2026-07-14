import os
import requests
import json
import urllib3
from datetime import datetime
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv(".env")

APP_KEY = os.getenv("KIS_APP_KEY", "")
APP_SECRET = os.getenv("KIS_APP_SECRET", "")
URL_BASE = "https://openapi.koreainvestment.com:9443"

def get_access_token():
    url = f"{URL_BASE}/oauth2/tokenP"
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10, verify=False)
    print(f"Token response status: {res.status_code}")
    print(f"Token response body: {res.text}")
    if res.status_code == 200:
        return res.json()["access_token"]
    else:
        raise Exception(f"Failed to get token: {res.text}")

def test_investor_daily():
    try:
        token = get_access_token()
        print("Successfully obtained access token!")
    except Exception as e:
        print(e)
        return

    url = f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-investor-daily-by-market"
    
    # Let's try different parameters to see which one works
    # Common markets: "J" (KOSPI?), "0000", "U0001", "0001", "001", "0", "KOSPI"
    candidates = [
        {"FID_COND_MRKT_DIV_CODE": "0000"},
        {"FID_COND_MRKT_DIV_CODE": "0001"},
        {"FID_COND_MRKT_DIV_CODE": "U"},
        {"FID_COND_MRKT_DIV_CODE": "J"}
    ]
    
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHPTJ04040000",
        "custtype": "P"
    }
    
    # We query for the last 5 days
    today = datetime.today().strftime("%Y%m%d")
    
    for params in candidates:
        query_params = {
            "FID_COND_MRKT_DIV_CODE": params["FID_COND_MRKT_DIV_CODE"],
            "FID_INPUT_DATE_1": "20260601",
            "FID_INPUT_DATE_2": today,
            "FID_PERIOD_DIV_CODE": "D"  # D: daily
        }
        
        try:
            print(f"Testing parameters: {query_params}...")
            res = requests.get(url, headers=headers, params=query_params, verify=False, timeout=10)
            print(f"Status: {res.status_code}")
            if res.status_code == 200:
                data = res.json()
                print(f"rt_cd: {data.get('rt_cd')}, msg1: {data.get('msg1')}")
                if data.get('rt_cd') == '0':
                    print("SUCCESS!")
                    print(json.dumps(data.get("output", [])[:3], indent=2, ensure_ascii=False))
                    break
                else:
                    print(f"Fail message: {data.get('msg1')}")
            else:
                print(f"Error: {res.text}")
        except Exception as e:
            print(f"Request failed: {e}")
        print("-" * 50)

if __name__ == "__main__":
    test_investor_daily()
