# -*- coding: utf-8 -*-
import sys
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

def get_premarket_quotes(symbols):
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbols}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, verify=False, timeout=10)
    print(f"[Quote Response] Status: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        results = []
        for quote in data["quoteResponse"]["result"]:
            symbol = quote.get("symbol")
            name = quote.get("longName", symbol)
            reg_price = quote.get("regularMarketPrice")
            reg_change_pct = quote.get("regularMarketChangePercent")
            
            pre_price = quote.get("preMarketPrice")
            pre_change = quote.get("preMarketChange")
            pre_change_pct = quote.get("preMarketChangePercent")
            
            market_state = quote.get("marketState")
            
            results.append({
                "symbol": symbol,
                "name": name,
                "regular_price": reg_price,
                "regular_change_percent": reg_change_pct,
                "pre_price": pre_price,
                "pre_change": pre_change,
                "pre_change_percent": pre_change_pct,
                "market_state": market_state
            })
        return results
    else:
        print(f"Raw Response: {res.text[:500]}")
        raise Exception("Failed to fetch quotes")

try:
    print("Fetching pre-market quotes...")
    quotes = get_premarket_quotes("SOXX,SMH")
    print(json.dumps(quotes, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
