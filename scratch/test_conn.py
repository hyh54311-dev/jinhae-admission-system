import os
import requests
import json

URL_MOCK = "https://openapivts.koreainvestment.com:29443/oauth2/tokenP"
URL_REAL = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"

print("Checking Mock API:")
try:
    res = requests.post(URL_MOCK, timeout=5, verify=False)
    print("Mock Status:", res.status_code)
    print("Mock Content (truncated):", res.text[:200])
except Exception as e:
    print("Mock Error:", e)

print("\nChecking Real API:")
try:
    res = requests.post(URL_REAL, timeout=5, verify=False)
    print("Real Status:", res.status_code)
    print("Real Content (truncated):", res.text[:200])
except Exception as e:
    print("Real Error:", e)
