# -*- coding: utf-8 -*-
import sys
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

tickers = {
    "^KS11": "코스피 지수",
    "^KQ11": "코스닥 지수",
    "207940.KS": "삼성바이오로직스",
    "005930.KS": "삼성전자"
}

def get_ticker_info(ticker):
    # Fetch 1d chart data with 1m interval
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, verify=False, timeout=10)
    if res.status_code == 200:
        data = res.json()
        try:
            result = data["chart"]["result"][0]
            meta = result["meta"]
            current_price = meta.get("regularMarketPrice")
            prev_close = meta.get("previousClose")
            
            quote = result["indicators"]["quote"][0]
            closes = [c for c in quote.get("close", []) if c is not None]
            if closes:
                current_price = closes[-1]
                
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100
            
            return {
                "name": tickers[ticker],
                "current": current_price,
                "prev_close": prev_close,
                "change": change,
                "change_percent": change_percent
            }
        except Exception as e:
            return {"error": f"Parsing failed: {e}"}
    else:
        return {"error": f"HTTP error {res.status_code}"}

results = {}
for ticker in tickers:
    results[ticker] = get_ticker_info(ticker)

print(json.dumps(results, indent=2, ensure_ascii=False))
