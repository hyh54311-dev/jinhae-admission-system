# -*- coding: utf-8 -*-
import sys
import requests
import json
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

def get_premarket_data(ticker):
    # includePrePost=true is required to get pre-market and after-hours data
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d&includePrePost=true"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, verify=False, timeout=10)
    if res.status_code == 200:
        data = res.json()
        try:
            result = data["chart"]["result"][0]
            meta = result["meta"]
            
            # The previous close of the regular market
            prev_close = meta.get("previousClose")
            
            # Extract last timestamp and close price (including pre-market)
            timestamps = result.get("timestamp", [])
            quote = result["indicators"]["quote"][0]
            closes = quote.get("close", [])
            
            # Find the last valid close price
            last_price = None
            last_time = None
            for i in range(len(closes) - 1, -1, -1):
                if closes[i] is not None:
                    last_price = closes[i]
                    last_time = timestamps[i]
                    break
                    
            if last_price is None:
                last_price = meta.get("regularMarketPrice")
                
            change = last_price - prev_close
            change_percent = (change / prev_close) * 100
            
            time_str = ""
            if last_time:
                time_str = datetime.fromtimestamp(last_time).strftime('%Y-%m-%d %H:%M:%S')
                
            return {
                "name": "iShares 반도체 ETF (SOXX)" if ticker == "SOXX" else "VanEck 반도체 ETF (SMH)",
                "last_price": last_price,
                "prev_close": prev_close,
                "change": change,
                "change_percent": change_percent,
                "last_time": time_str
            }
        except Exception as e:
            return {"error": f"Parsing failed: {e}"}
    else:
        return {"error": f"HTTP error {res.status_code}"}

results = {}
for ticker in ["SOXX", "SMH"]:
    results[ticker] = get_premarket_data(ticker)

print(json.dumps(results, indent=2, ensure_ascii=False))
