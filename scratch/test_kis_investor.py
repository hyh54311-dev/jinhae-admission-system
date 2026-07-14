# -*- coding: utf-8 -*-
import os
import requests
import json
import urllib3
from dotenv import load_dotenv

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load .env
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
    res = requests.post(url, headers=headers, json=body, timeout=10, verify=False)
    print(f"Token Status Code: {res.status_code}")
    print(f"Token Response Text: {res.text[:500]}")
    if res.status_code == 200:
        return res.json()["access_token"]
    else:
        raise Exception(f"Token error: {res.text}")

def test_api(token, params, tr_id="FHPTJ04040000"):
    url = f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-investor-daily-by-market"
    headers = {
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id,
        "custtype": "P"
    }
    print(f"\n--- Testing with params: {params} ---")
    res = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text[:500]}")

def main():
    try:
        token = get_access_token()
        print("Successfully obtained KIS Access Token.")
        
        # Test Case 1: Original parameter set with both ISCD and ISCD_1
        params1 = {
            "FID_COND_MRKT_DIV_CODE": "U",
            "FID_INPUT_ISCD": "0001",
            "FID_INPUT_ISCD_1": "0001",
            "FID_INPUT_DATE_1": "20260501",
            "FID_INPUT_DATE_2": "20260610",
            "FID_PERIOD_DIV_CODE": "D"
        }
        test_api(token, params1)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
