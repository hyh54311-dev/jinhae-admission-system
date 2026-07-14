# -*- coding: utf-8 -*-
"""
KOSPI Long-Term Bear Market Detector
Detects if KOSPI is entering a long-term bear market based on 4 indicators:
1. Absolute Momentum: KOSPI Close < KOSPI Close 250 trading days ago.
2. Moving Average: KOSPI Close < 200-day Moving Average.
3. Drawdown: KOSPI Drawdown from 250-day peak <= -20%.
4. USD/KRW Exchange Rate: USD/KRW Exchange Rate >= 1560 KRW.

Alerts via Telegram if 2 or more conditions are satisfied.
Runs daily at 14:30 via Task Scheduler.
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
STATE_FILE = os.path.join(BASE_DIR, "scratch", "bear_state.json")

def send_telegram(msg):
    print(f"[TELEGRAM] {msg}")
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, verify=False, timeout=10)
        except Exception as e:
            print(f"텔레그램 발송 실패: {e}")

def fetch_kospi_data():
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

def fetch_usdkrw_rate():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/USDKRW=X?interval=1d&range=5d"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, verify=False, timeout=15)
    if res.status_code != 200:
        # Fallback to alternative symbol KRW=X if USDKRW=X fails
        url = "https://query1.finance.yahoo.com/v8/finance/chart/KRW=X?interval=1d&range=5d"
        res = requests.get(url, headers=headers, verify=False, timeout=15)
        if res.status_code != 200:
            raise Exception("환율 데이터 수신 실패")
            
    data = res.json()
    result = data["chart"]["result"][0]
    closes = result["indicators"]["quote"][0]["close"]
    # return the latest non-NaN close
    for val in reversed(closes):
        if val is not None and not np.isnan(val):
            return val
    raise Exception("유효한 환율 데이터가 없음")

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
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] KOSPI 장기 하락장 신호 분석 시작...")
    
    today_weekday = datetime.now().weekday()
    if today_weekday >= 5:
        print("주말이므로 모니터링을 종료합니다.")
        return

    try:
        df = fetch_kospi_data()
        n = len(df)
        if n < 250:
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
            
        # 1. 절대 모멘텀 (1년 전 종가와 비교)
        close_250 = closes[-250] # 250거래일 전 종가
        cond_abs_mom = today_close < close_250
        
        # 2. 200일 이동평균 계산
        ma_200 = df["Close"].rolling(window=200).mean().iloc[-1]
        cond_ma_200 = today_close < ma_200
        
        # 3. 고점 대비 낙폭 (-20% 이하인지)
        peak_250 = np.max(closes[-250:])
        dd = (today_close - peak_250) / peak_250 * 100
        cond_drawdown = dd <= -20.0
        
        # 4. 원/달러 환율 (1560원 이상인지)
        usd_krw = fetch_usdkrw_rate()
        cond_exchange = usd_krw >= 1560.0
        
        print(f"오늘 날짜: {today_date} (종가: {today_close:,.2f} | 환율: {usd_krw:.2f}원)")
        print(f" - [신호 1] 절대 모멘텀: 1년 전 종가 {close_250:,.2f} 대비 현재 {today_close:,.2f} (결과: {cond_abs_mom})")
        print(f" - [신호 2] 200일 이동평균선: {ma_200:,.2f} 대비 현재 {today_close:,.2f} (결과: {cond_ma_200})")
        print(f" - [신호 3] 고점 대비 낙폭: {dd:.2f}% (기준: -20% 이하, 결과: {cond_drawdown})")
        print(f" - [신호 4] 원/달러 환율: {usd_krw:.2f}원 (기준: 1,560원 이상, 결과: {cond_exchange})")
        
        # 만족하는 조건 개수 계산
        conditions = [
            ("절대 모멘텀 음수 (1년 전 대비 하락)", cond_abs_mom, f"현재 {today_close:,.1f} < 1년 전 {close_250:,.1f}"),
            ("200일 장기 이동평균선 하회", cond_ma_200, f"현재 {today_close:,.1f} < 200일선 {ma_200:,.1f}"),
            ("대세 하락장 낙폭 도달 (-20% 이하)", cond_drawdown, f"고점 대비 낙폭 {dd:.2f}%"),
            ("원/달러 환율 임계치 돌파 (1,560원 이상)", cond_exchange, f"현재 환율 {usd_krw:.2f}원")
        ]
        
        satisfied_list = [c for c in conditions if c[1]]
        satisfied_count = len(satisfied_list)
        print(f"만족하는 조건 개수: {satisfied_count}개 / 4개")
        
        if satisfied_count >= 2:
            state = load_state()
            if state.get("last_notified_date") != today_date:
                detail_str = "\n".join([f" - ✅ {c[0]}: {c[2]}" for c in satisfied_list])
                unsatisfied_list = [c for c in conditions if not c[1]]
                undetail_str = "\n".join([f" - ❌ {c[0]}: {c[2]}" for c in unsatisfied_list])
                
                msg = (
                    f"🚨 [KOSPI 장기 대세 하락장 경보 발송]\n"
                    f"오늘({today_date}) 코스피 시장의 대세 하락장 판단 지표 4개 중 {satisfied_count}개가 만족되어 위험 단계에 진입했습니다.\n\n"
                    f"[충족된 위험 지표]\n{detail_str}\n\n"
                    f"[미충족된 지표]\n{undetail_str}\n\n"
                    f"주식 비중 축소 및 연금 자산의 대피(안전자산 리밸런싱)를 적극 검토하십시오."
                )
                send_telegram(msg)
                state["last_notified_date"] = today_date
                save_state(state)
        else:
            print("만족하는 조건이 2개 미만이므로 알림을 보내지 않았습니다.")
            
    except Exception as e:
        err_msg = f"🚨 KOSPI 대세 하락장 감지 봇 실행 실패: {e}"
        print(err_msg)
        send_telegram(err_msg)

if __name__ == "__main__":
    main()
