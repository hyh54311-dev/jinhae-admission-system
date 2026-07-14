# -*- coding: utf-8 -*-
"""
KOSPI Medium-Term Correction Detector
Detects if KOSPI is currently in a medium-term correction based on 3 indicators:
1. Drawdown: Current close is -7% to -15% from the 250-day peak.
2. Moving Average: Current close is below the 60-day MA.
3. RSI: 14-day RSI is <= 35 (oversold).

Runs daily at 14:30 via Task Scheduler. Alerts via Telegram if all 3 are satisfied.
"""
import os
import sys
import json
import requests
import urllib3
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
STATE_FILE = os.path.join(BASE_DIR, "scratch", "correction_state.json")

def send_telegram(msg):
    print(f"[TELEGRAM] {msg}")
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, verify=False, timeout=10)
        except Exception as e:
            print(f"텔레그램 발송 실패: {e}")

def fetch_kospi_data():
    # Fetch past 250 trading days of KOSPI daily data (approx. 1 year)
    url = "https://query1.finance.yahoo.com/v8/finance/chart/^KS11?interval=1d&range=360d"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, verify=False, timeout=15)
    if res.status_code != 200:
        raise Exception(f"KOSPI 데이터 수신 실패: {res.text}")
    
    data = res.json()
    result = data["chart"]["result"][0]
    timestamps = result["timestamp"]
    closes = result["indicators"]["quote"][0]["close"]
    
    df = pd.DataFrame({
        "Timestamp": timestamps,
        "Close": closes
    })
    df["Date"] = pd.to_datetime(df["Timestamp"], unit="s").dt.strftime('%Y-%m-%d')
    df = df.dropna().sort_values("Date").reset_index(drop=True)
    return df

def calculate_rsi(prices, period=14):
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    if down == 0:
        down = 1e-5
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:period+1] = 100. - 100. / (1. + rs)

    for i in range(period+1, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        if down == 0:
            down = 1e-5

        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)

    return rsi

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_notified_date": None}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] KOSPI 중기 조정 신호 분석 시작...")
    
    # 주말에는 실행 조기 종료
    today_weekday = datetime.now().weekday()
    if today_weekday >= 5:
        print("주말이므로 모니터링을 종료합니다.")
        return

    try:
        df = fetch_kospi_data()
        n = len(df)
        if n < 120:
            print("데이터 부족으로 분석이 불가능합니다.")
            return
            
        closes = df["Close"].values
        dates = df["Date"].values
        today_date = dates[-1]
        today_close = closes[-1]
        
        # 오늘이 실제 개장일인지 확인 (야후 파이낸스 데이터의 마지막 날짜가 오늘 날짜와 같은지)
        current_date = datetime.now().strftime('%Y-%m-%d')
        if today_date != current_date:
            print(f"오늘({current_date})은 장이 열리지 않은 날(공휴일 또는 휴장일)입니다. 분석을 조기 종료합니다. (최근 거래일: {today_date})")
            return
            
        # 1. 250일 최고가 및 낙폭 계산
        peak_250 = np.max(closes[-250:])
        dd = (today_close - peak_250) / peak_250 * 100
        
        # 2. 60일 이동평균 계산
        ma_60 = df["Close"].rolling(window=60).mean().iloc[-1]
        
        # 3. 14일 RSI 계산
        rsi_values = calculate_rsi(closes, 14)
        today_rsi = rsi_values[-1]
        
        print(f"오늘 날짜: {today_date} (종가: {today_close:,.2f})")
        print(f" - 최근 250일 최고가: {peak_250:,.2f} | 고점 대비 낙폭: {dd:.2f}% (기준: -7% ~ -15%)")
        print(f" - 60일 이동평균선: {ma_60:,.2f} | 종가와의 괴리: {today_close - ma_60:,.2f} (기준: 60일선 하회)")
        print(f" - 14일 RSI: {today_rsi:.2f} (기준: 35 이하)")
        
        # 조건 검증
        cond_dd = -15.0 <= dd <= -7.0
        cond_ma = today_close < ma_60
        cond_rsi = today_rsi <= 35.0
        
        all_satisfied = cond_dd and cond_ma and cond_rsi
        print(f"조건 만족 여부 -> 낙폭: {cond_dd}, 60일선하회: {cond_ma}, RSI과매도: {cond_rsi} | 최종 결과: {all_satisfied}")
        
        if all_satisfied:
            state = load_state()
            if state.get("last_notified_date") != today_date:
                msg = (
                    f"⚠️ [KOSPI 중기 조정 진입 신호 감지]\n"
                    f"오늘({today_date}) 코스피가 중기 조정 영역에 진입하여 반등 대기 상태입니다.\n\n"
                    f"1. 고점 대비 낙폭: {dd:.2f}% (최고가 {peak_250:,.1f})\n"
                    f"2. 이동평균선 상태: 종가({today_close:,.1f}) < 60일선({ma_60:,.1f})\n"
                    f"3. 14일 RSI 지표: {today_rsi:.2f} (과매도권 진입)\n\n"
                    f"중기 조정 매수 진입 시점을 검토하십시오."
                )
                send_telegram(msg)
                state["last_notified_date"] = today_date
                save_state(state)
        else:
            print("모든 조건이 충족되지 않아 알림을 보내지 않았습니다.")
            
    except Exception as e:
        err_msg = f"🚨 KOSPI 중기 조정 감지 봇 실행 실패: {e}"
        print(err_msg)
        send_telegram(err_msg)

if __name__ == "__main__":
    main()
