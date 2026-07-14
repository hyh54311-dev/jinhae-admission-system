# -*- coding: utf-8 -*-
import sys
import requests
import json
import urllib3
import pandas as pd

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

def analyze_historical_drops_2000s(ticker):
    # Fetch data since 2000-01-01 (Timestamp: 946684800)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1=946684800&period2=1780880000&interval=1d"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, verify=False, timeout=15)
    
    if res.status_code != 200:
        print(f"Failed to fetch data from Chart API: {res.text}")
        return
        
    data = res.json()
    result = data["chart"]["result"][0]
    timestamps = result["timestamp"]
    closes = result["indicators"]["quote"][0]["close"]
    
    # Create DataFrame
    df = pd.DataFrame({
        "Timestamp": timestamps,
        "Close": closes
    })
    df["Date"] = pd.to_datetime(df["Timestamp"], unit="s")
    df = df.dropna().sort_values("Date").reset_index(drop=True)
    
    # Calculate daily returns
    df['Return'] = df['Close'].pct_change() * 100
    
    # Filter for drops of 5% or more
    heavy_drops = df[df['Return'] <= -5.0].copy()
    
    results = []
    for idx in heavy_drops.index:
        if idx + 1 < len(df):
            drop_row = df.iloc[idx]
            next_row = df.iloc[idx + 1]
            results.append({
                "Drop_Date": drop_row['Date'].strftime('%Y-%m-%d'),
                "Drop_Return": round(drop_row['Return'], 2),
                "Next_Date": next_row['Date'].strftime('%Y-%m-%d'),
                "Next_Return": round(next_row['Return'], 2),
                "Rebounded": next_row['Return'] > 0
            })
            
    # Print results
    print(f"=== KOSPI 2000s Days with -5% or Worse Drop & Next Day Returns ===")
    rebound_count = sum(1 for r in results if r['Rebounded'])
    total_count = len(results)
    
    for r in results:
        status = "반등 성공 🟢" if r['Rebounded'] else "추가 하락 🔴"
        print(f"하락일: {r['Drop_Date']} ({r['Drop_Return']:.2f}%) -> 다음날: {r['Next_Date']} ({r['Next_Return']:.2f}%) [{status}]")
        
    if total_count > 0:
        print(f"\n총 발생 횟수 (2000년 이후): {total_count}번")
        print(f"다음날 반등 성공: {rebound_count}번 (비율: {rebound_count/total_count*100:.2f}%)")
        print(f"다음날 추가 하락: {total_count - rebound_count}번 (비율: {(total_count - rebound_count)/total_count*100:.2f}%)")
    else:
        print("No drops over 5% found in the dataset.")

try:
    analyze_historical_drops_2000s("^KS11")
except Exception as e:
    print(f"Error: {e}")
