# -*- coding: utf-8 -*-
import os
import sys
import requests
import json
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

KIS_MOCK = os.getenv("KIS_MOCK", "False").lower() in ("true", "1", "yes")

if KIS_MOCK:
    APP_KEY = os.getenv("KIS_MOCK_APP_KEY", "")
    APP_SECRET = os.getenv("KIS_MOCK_APP_SECRET", "")
    URL_BASE = "https://openapim.koreainvestment.com:29443"
else:
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
    res = requests.post(url, headers=headers, data=json.dumps(body), verify=False, timeout=10)
    print(f"[Token Response] Status: {res.status_code}")
    try:
        return res.json()["access_token"]
    except Exception as je:
        print(f"Token parsing error: {je}")
        print(f"Raw Response: {res.text[:500]}")
        raise Exception("Token fetch failed")

def get_price_info(token, ticker):
    url = f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FBDT00010000" if (KIS_MOCK or "openapim" in URL_BASE) else "FHPST01010000"
    }
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": ticker
    }
    res = requests.get(url, headers=headers, params=params, verify=False, timeout=10)
    print(f"[Price Response] Status: {res.status_code}")
    try:
        return res.json()
    except Exception as je:
        print(f"Price parsing error: {je}")
        print(f"Raw Response: {res.text[:500]}")
        raise Exception("Price fetch failed")

try:
    print(f"Connecting to KIS API (Mock Mode: {KIS_MOCK})...")
    token = get_access_token()
    data = get_price_info(token, "207940")
    print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error occurred: {e}")
