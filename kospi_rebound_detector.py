# -*- coding: utf-8 -*-
"""
KOSPI Rebound Signal Detector
Detects:
1. 우상향 쌍바닥 (Higher Low Double Bottom)
2. FTD (Follow-Through Day) - Day 4-10 rally day with +1.5% return and higher volume.
Saves notification state in scratch/rebound_state.json to prevent duplicate alerts.
"""
import os
import sys
import json
import requests
import urllib3
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scratch", "rebound_state.json")

def send_telegram(msg):
    print(f"[TELEGRAM] {msg}")
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, verify=False, timeout=10)
        except Exception as e:
            print(f"텔레그램 발송 실패: {e}")

def fetch_kospi_data():
    # Fetch past 90 days of KOSPI daily data
    url = "https://query1.finance.yahoo.com/v8/finance/chart/^KS11?interval=1d&range=90d"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, verify=False, timeout=15)
    if res.status_code != 200:
        raise Exception(f"KOSPI 데이터 수신 실패: {res.text}")
    
    data = res.json()
    result = data["chart"]["result"][0]
    timestamps = result["timestamp"]
    closes = result["indicators"]["quote"][0]["close"]
    volumes = result["indicators"]["quote"][0]["volume"]
    
    df = pd.DataFrame({
        "Timestamp": timestamps,
        "Close": closes,
        "Volume": volumes
    })
    df["Date"] = pd.to_datetime(df["Timestamp"], unit="s").dt.strftime('%Y-%m-%d')
    df = df.dropna().sort_values("Date").reset_index(drop=True)
    return df

def check_double_bottom(df):
    """
    우상향 쌍바닥 검출 로직:
    1. 최근 60일 내 로컬 미니멈(최저점 후보)들을 찾는다.
    2. 이전 저점(M1)과 이후 저점(M2)이 존재하고, M2 > M1 (우상향)인지 확인.
    3. M1과 M2 사이의 기간이 5일~30일 사이여야 함.
    4. M1과 M2 사이에 최소 3% 이상의 반등(Peak)이 존재했어야 함.
    5. 오늘(마지막 행)이 M2 근처(최근 3일 이내)이면서 상승 흐름이어야 함.
    """
    n = len(df)
    if n < 40:
        return False, "데이터 부족"
        
    closes = df["Close"].values
    dates = df["Date"].values
    
    # 최근 60일 데이터 대상
    start_idx = max(0, n - 60)
    
    # 로컬 미니멈 찾기 (3일 윈도우 기준 최저점)
    minima = []
    for i in range(start_idx + 1, n - 1):
        if closes[i] < closes[i-1] and closes[i] < closes[i+1]:
            minima.append(i)
            
    if len(minima) < 2:
        return False, "저점 후보 부족"
        
    # 뒤에서부터 우상향 쌍바닥 조건에 맞는 쌍을 찾음
    for j in range(len(minima) - 1, 0, -1):
        idx2 = minima[j]
        m2_val = closes[idx2]
        
        for k in range(j - 1, -1, -1):
            idx1 = minima[k]
            m1_val = closes[idx1]
            
            # 조건 1: 기간 (5일 ~ 30일 사이)
            dist = idx2 - idx1
            if dist < 5 or dist > 30:
                continue
                
            # 조건 2: 우상향 (M2가 M1보다 높아야 함, 단 과도하지 않게 4% 이내)
            if m2_val > m1_val and m2_val <= m1_val * 1.04:
                # 조건 3: 중간 반등 (M1 대비 중간 최고점이 3% 이상 반등)
                mid_prices = closes[idx1:idx2+1]
                peak_val = max(mid_prices)
                if peak_val >= m1_val * 1.03:
                    # 조건 4: 오늘이 M2 이후 3일 이내이면서 하락세를 멈추고 턴어라운드 중
                    # 오늘 종가가 어제 종가보다 높거나 횡보
                    today_idx = n - 1
                    if today_idx - idx2 <= 3 and closes[today_idx] >= closes[today_idx - 1]:
                        reason = f"쌍바닥 감지: 1차 저점 {dates[idx1]}({m1_val:,.1f}) -> 2차 저점 {dates[idx2]}({m2_val:,.1f}) [우상향 저점 차이: {((m2_val-m1_val)/m1_val*100):.2f}%]"
                        return True, reason
    return False, "조건 미충족"

def check_ftd(df):
    """
    팔로우스루 데이(FTD) 검출 로직:
    1. 최근 60일 내의 최저점(마디 저점)을 찾는다.
    2. 최저점 날짜를 Day 0으로 설정.
    3. 최저점 이후 지수가 종가 기준 최저점을 하회하지 않는 상태에서 랠리 시도 지속.
    4. 랠리 4일 차 ~ 10일 차 사이에 아래 조건 충족 시 FTD 선언:
       - 당일 지수 상승률 >= 1.5%
       - 당일 거래량 > 전일 거래량
    """
    n = len(df)
    if n < 20:
        return False, "데이터 부족"
        
    closes = df["Close"].values
    volumes = df["Volume"].values
    dates = df["Date"].values
    
    # 1. 최근 60일 중 최저점 탐색
    start_idx = max(0, n - 60)
    low_idx = start_idx
    for i in range(start_idx, n):
        if closes[i] < closes[low_idx]:
            low_idx = i
            
    # 2. 최저점 이후 랠리 계산
    # low_idx 날이 Day 0, 그 다음 거래일이 Day 1
    # 만약 오늘(n-1)이 최저점 자체라면 랠리 진행 불가
    if low_idx == n - 1:
        return False, f"오늘({dates[low_idx]}) 최저점 갱신 (FTD 리셋)"
        
    rally_days = []
    for i in range(low_idx + 1, n):
        # 만약 중간에 최저점 아래로 종가가 떨어지면 랠리 무효화 (실패)
        if closes[i] < closes[low_idx]:
            return False, f"최저점 이탈로 랠리 실패 ({dates[i]} 종가 {closes[i]:,.1f} < {closes[low_idx]:,.1f})"
        rally_days.append(i)
        
    rally_count = len(rally_days)  # 오늘이 랠리 몇 일 차인가?
    
    # 3. FTD 조건 체크 (4일 차 ~ 10일 차)
    if rally_count < 4 or rally_count > 10:
        return False, f"현재 랠리 {rally_count}일 차 (FTD 판단 범위인 4~10일 차가 아님)"
        
    today_idx = n - 1
    today_return = (closes[today_idx] - closes[today_idx - 1]) / closes[today_idx - 1] * 100
    today_vol = volumes[today_idx]
    prev_vol = volumes[today_idx - 1]
    
    # 조건 A: 상승률 1.5% 이상
    # 조건 B: 거래량이 전날보다 많아야 함
    if today_return >= 1.5 and today_vol > prev_vol:
        reason = f"FTD 감지 (랠리 {rally_count}일 차): 오늘 상승률 {today_return:.2f}% (기준 1.5% 이상) | 오늘 거래량 {today_vol:,} > 전일 거래량 {prev_vol:,}"
        return True, reason
        
    return False, f"현재 랠리 {rally_count}일 차 진행 중 (오늘 상승률 {today_return:.2f}%, 거래량 증감 {((today_vol-prev_vol)/prev_vol*100):+.1f}%)"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "notified_either_date": None,
        "notified_both_date": None,
        "last_pivot_low_date": None
    }

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] KOSPI 반등 신호 분석 시작...")
    
    try:
        df = fetch_kospi_data()
        today_date = df.iloc[-1]["Date"]
        today_close = df.iloc[-1]["Close"]
        
        # 최저점 날짜 찾기
        n = len(df)
        start_idx = max(0, n - 60)
        low_idx = start_idx
        for i in range(start_idx, n):
            if df.iloc[i]["Close"] < df.iloc[low_idx]["Close"]:
                low_idx = i
        pivot_low_date = df.iloc[low_idx]["Date"]
        
        # 신호 체크
        db_ok, db_reason = check_double_bottom(df)
        ftd_ok, ftd_reason = check_ftd(df)
        
        print(f"오늘 날짜: {today_date} (종가: {today_close:,.2f})")
        print(f"최근 60일 최저점 날짜: {pivot_low_date} (종가: {df.iloc[low_idx]['Close']:,.2f})")
        print(f"1. 우상향 쌍바닥 결과: {db_ok} ({db_reason})")
        print(f"2. 팔로우스루 데이 결과: {ftd_ok} ({ftd_reason})")
        
        # 상태 로드
        state = load_state()
        
        # 만약 새로운 최저점이 갱신되었다면 기존 알림 상태 리셋
        if state.get("last_pivot_low_date") != pivot_low_date:
            print(f">> 최저점이 기존 {state.get('last_pivot_low_date')}에서 {pivot_low_date}로 변경되어 알림 기록을 리셋합니다.")
            state["notified_either_date"] = None
            state["notified_both_date"] = None
            state["last_pivot_low_date"] = pivot_low_date
            
        # 알림 조건 판단
        both_detected = db_ok and ftd_ok
        
        # 두 신호가 동시에 만족되었을 때만 알림 발송
        if both_detected:
            if state.get("notified_both_date") != today_date:
                msg = f"🔥 [KOSPI 강력 반등 신호 감지]\n오늘({today_date}) 코스피 반등 신호 2개가 모두 충족되었습니다!\n\n1. {db_reason}\n2. {ftd_reason}\n\n시스템 진입 여부를 검토하십시오."
                send_telegram(msg)
                state["notified_both_date"] = today_date
                
        save_state(state)
        print("분석 및 상태 저장 완료.")
        
    except Exception as e:
        err_msg = f"🚨 KOSPI 반등 신호 감지 봇 실행 실패: {e}"
        print(err_msg)
        send_telegram(err_msg)

if __name__ == "__main__":
    main()
