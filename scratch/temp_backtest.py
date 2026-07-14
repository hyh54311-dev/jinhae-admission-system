import pandas as pd
import numpy as np
import requests
import urllib3
import io

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Download KOSPI data directly from Yahoo Finance CSV endpoint
url = "https://query1.finance.yahoo.com/v7/finance/download/^KS11?period1=1559347200&period2=1779110400&interval=1d&events=history&includeAdjustedClose=true"
headers = {"User-Agent": "Mozilla/5.0"}
try:
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    kospi = pd.read_csv(io.StringIO(response.text))
    kospi['Date'] = pd.to_datetime(kospi['Date'])
    kospi.set_index('Date', inplace=True)
except Exception as e:
    print(f"Failed to get data: {e}")
    exit()

if kospi.empty:
    print("Failed to get data")
    exit()

close_col = 'Close'

monthly = kospi[[close_col]].resample('ME').last().copy()
monthly.columns = ['Close']

# 6-month momentum
monthly['Mom_6M'] = monthly['Close'].pct_change(6)

# Signal based on previous month's momentum (Avoid look-ahead bias)
monthly['Signal'] = np.where(monthly['Mom_6M'].shift(1) > 0, 1, 0)

# Monthly returns
monthly['K_Ret'] = monthly['Close'].pct_change()

# Cash return (assume 2% annual)
cash_ret = 0.02 / 12

# Strategy Return
monthly['S_Ret'] = np.where(monthly['Signal'] == 1, monthly['K_Ret'], cash_ret)

# Backtest from 2020-01-01
bt = monthly['2020-01-01':].copy()

# Cumulative returns
bt['Cum_K'] = (1 + bt['K_Ret']).cumprod()
bt['Cum_S'] = (1 + bt['S_Ret']).cumprod()

seed = 100000000
final_k = seed * bt['Cum_K'].iloc[-1]
final_s = seed * bt['Cum_S'].iloc[-1]

mdd_k = (bt['Cum_K'] / bt['Cum_K'].cummax() - 1).min() * 100
mdd_s = (bt['Cum_S'] / bt['Cum_S'].cummax() - 1).min() * 100

print(f"기간: 2020년 1월 ~ 2026년 5월")
print(f"시드 머니: 100,000,000 원")
print(f"--- 3번 전략 (한국형 절대 모멘텀) ---")
print(f"최종 자산: {final_s:,.0f} 원")
print(f"최대 낙폭(MDD): {mdd_s:.2f}%")
print(f"--- 단순 존버 (코스피 그대로 들고 있기) ---")
print(f"최종 자산: {final_k:,.0f} 원")
print(f"최대 낙폭(MDD): {mdd_k:.2f}%")
