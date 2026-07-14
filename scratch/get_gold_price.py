# -*- coding: utf-8 -*-
import sys
import requests
import json
import urllib3
import pandas as pd
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

def get_gold_history():
    # Fetch 1 year of daily gold price data
    url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=1d&range=1y"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, verify=False, timeout=10)
    if res.status_code != 200:
        raise Exception(f"Failed to fetch Gold data: {res.text}")
        
    data = res.json()
    result = data["chart"]["result"][0]
    timestamps = result["timestamp"]
    closes = result["indicators"]["quote"][0]["close"]
    
    df = pd.DataFrame({
        "Timestamp": timestamps,
        "Close": closes
    })
    df["Date"] = pd.to_datetime(df["Timestamp"], unit="s")
    df = df.dropna().sort_values("Date").reset_index(drop=True)
    
    start_price = df.iloc[0]["Close"]
    start_date = df.iloc[0]["Date"].strftime('%Y-%m-%d')
    end_price = df.iloc[-1]["Close"]
    end_date = df.iloc[-1]["Date"].strftime('%Y-%m-%d')
    
    high_price = df["Close"].max()
    high_row = df[df["Close"] == high_price].iloc[0]
    high_date = high_row["Date"].strftime('%Y-%m-%d')
    
    low_price = df["Close"].min()
    low_row = df[df["Close"] == low_price].iloc[0]
    low_date = low_row["Date"].strftime('%Y-%m-%d')
    
    change = end_price - start_price
    change_percent = (change / start_price) * 100
    
    # Let's get monthly average prices to show the trend
    df['YearMonth'] = df['Date'].dt.strftime('%Y-%m')
    monthly = df.groupby('YearMonth')['Close'].mean().reset_index()
    
    print("=== Gold Price Analysis (GC=F) ===")
    print(f"Start Date: {start_date} | Price: ${start_price:,.2f}")
    print(f"End Date: {end_date} | Price: ${end_price:,.2f}")
    print(f"Change: ${change:,.2f} ({change_percent:+.2f}%)")
    print(f"Yearly High: ${high_price:,.2f} on {high_date}")
    print(f"Yearly Low: ${low_price:,.2f} on {low_date}")
    print("\nMonthly Average Prices:")
    for _, row in monthly.iterrows():
        print(f"- {row['YearMonth']}: ${row['Close']:,.2f}")
        
    return {
        "start_date": start_date, "start_price": start_price,
        "end_date": end_date, "end_price": end_price,
        "change_percent": change_percent,
        "high_price": high_price, "high_date": high_date,
        "low_price": low_price, "low_date": low_date,
        "monthly": monthly.to_dict(orient="records")
    }

try:
    get_gold_history()
except Exception as e:
    print(f"Error: {e}")
