# -*- coding: utf-8 -*-
import sys
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

def get_yahoo_price(ticker):
    # Yahoo Finance Chart API is lightweight and contains intraday info
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    res = requests.get(url, headers=headers, verify=False, timeout=10)
    print(f"[Yahoo Response] Status: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        meta = data["chart"]["result"][0]["meta"]
        # current price, high, low, previous close
        current_price = meta.get("regularMarketPrice")
        high = meta.get("regularMarketDayHigh")
        low = meta.get("regularMarketDayLow")
        prev_close = meta.get("previousClose")
        
        # Check if we can extract current high/low from indicators too
        quote = data["chart"]["result"][0]["indicators"]["quote"][0]
        highs = [h for h in quote.get("high", []) if h is not None]
        lows = [l for l in quote.get("low", []) if l is not None]
        closes = [c for c in quote.get("close", []) if c is not None]
        
        # Override with actual intraday high/low if available
        if highs:
            high = max(highs)
        if lows:
            low = min(lows)
        if closes:
            current_price = closes[-1]
            
        print(f"Current Price: {current_price}")
        print(f"Day High: {high}")
        print(f"Day Low: {low}")
        print(f"Prev Close: {prev_close}")
        
        return {
            "current": current_price,
            "high": high,
            "low": low,
            "prev_close": prev_close
        }
    else:
        print(f"Raw Response: {res.text[:500]}")
        raise Exception("Failed to fetch from Yahoo Finance")

try:
    print("Fetching from Yahoo Finance...")
    get_yahoo_price("207940.KS")
except Exception as e:
    print(f"Error occurred: {e}")
