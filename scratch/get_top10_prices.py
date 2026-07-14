# -*- coding: utf-8 -*-
import sys
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

# Tickermap for KOSPI Top 10 and indices
tickers = {
    "^KS11": "코스피 지수",
    "^KQ11": "코스닥 지수",
    "005930.KS": "삼성전자",
    "000660.KS": "SK하이닉스",
    "373220.KS": "LG에너지솔루션",
    "207940.KS": "삼성바이오로직스",
    "005380.KS": "현대차",
    "000270.KS": "기아",
    "068270.KS": "셀트리온",
    "105560.KS": "KB금융",
    "005490.KS": "POSCO홀딩스",
    "035420.KS": "NAVER"
}

def get_ticker_info(ticker):
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
            
            # Extract high/low from intraday quotes if available
            quote = result["indicators"]["quote"][0]
            highs = [h for h in quote.get("high", []) if h is not None]
            lows = [l for l in quote.get("low", []) if l is not None]
            closes = [c for c in quote.get("close", []) if c is not None]
            
            if highs:
                high = max(highs)
            else:
                high = meta.get("regularMarketDayHigh", current_price)
                
            if lows:
                low = min(lows)
            else:
                low = meta.get("regularMarketDayLow", current_price)
                
            if closes:
                current_price = closes[-1]
            
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100
            
            return {
                "name": tickers[ticker],
                "current": current_price,
                "high": high,
                "low": low,
                "prev_close": prev_close,
                "change": change,
                "change_percent": change_percent
            }
        except Exception as e:
            return {"error": f"Parsing failed for {ticker}: {e}"}
    else:
        return {"error": f"HTTP error {res.status_code} for {ticker}"}

results = {}
for ticker in tickers:
    info = get_ticker_info(ticker)
    results[ticker] = info

print(json.dumps(results, indent=2, ensure_ascii=False))
