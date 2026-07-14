# -*- coding: utf-8 -*-
import os
import sys
import json
import re
import requests
import urllib3
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Disable insecure warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ensure UTF-8 output on Windows
if sys.platform.startswith('win'):
    try:
        if sys.stdout is not None:
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stderr is not None:
            sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Load environment variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
STATE_FILE = os.path.join(BASE_DIR, "scratch", "halt_monitor_state.json")

def send_telegram(msg):
    print(f"[TELEGRAM] {msg}")
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, verify=False, timeout=10)
        except Exception as e:
            print(f"텔레그램 발송 실패: {e}")

def get_market_indices():
    indices = {
        "KOSPI": "^KS11",
        "KOSDAQ": "^KQ11"
    }
    results = {}
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for name, symbol in indices.items():
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        try:
            res = requests.get(url, headers=headers, verify=False, timeout=10)
            if res.status_code == 200:
                data = res.json()
                meta = data["chart"]["result"][0]["meta"]
                current_price = meta.get("regularMarketPrice")
                prev_close = meta.get("chartPreviousClose")
                if current_price and prev_close:
                    pct = (current_price - prev_close) / prev_close * 100
                    results[name] = {
                        "price": current_price,
                        "prev_close": prev_close,
                        "pct": pct
                    }
        except Exception as e:
            print(f"지수 조회 오류 ({name}): {e}")
            
    return results

def check_news_for_halt(keyword):
    url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sort=1"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    articles = []
    
    try:
        res = requests.get(url, headers=headers, verify=False, timeout=10)
        res.encoding = 'utf-8'
        if res.status_code != 200:
            return []
            
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Class-agnostic extraction of news links and their text
        url_groups = {}
        for a in soup.find_all("a"):
            href = a.get("href", "").strip()
            text = a.get_text(strip=True)
            
            if not href or href.startswith("#") or href.startswith("javascript:") or len(text) < 3:
                continue
                
            # Filter out search options and helper links
            if "search.naver.com" in href or "help.naver.com" in href or "policy.naver.com" in href or "keep.naver.com" in href:
                continue
            if "ssc=" in href or "where=" in href:
                continue
            if not href.startswith("http"):
                continue
                
            if href not in url_groups:
                url_groups[href] = []
            if text not in url_groups[href]:
                url_groups[href].append(text)
            
        # Group and find titles + timestamps
        for href, texts in url_groups.items():
            cleaned_texts = [t for t in texts if t not in ["네이버뉴스", "동영상", "뉴스", "언론사 선정"]]
            if not cleaned_texts:
                continue
                
            # Define title exactly as the first text element
            title = cleaned_texts[0].strip()
            
            # Check keywords in TITLE only to prevent false positives from snippet matches
            # Must also contain "속보" to ensure it's a real-time breaking news alert
            has_sidecar = ("사이드카" in title and any(x in title for x in ["발동", "일시정지", "효력정지", "중단"]) and "속보" in title)
            has_cb = ("서킷브레이커" in title and any(x in title for x in ["발동", "일시정지", "효력정지", "중단"]) and "속보" in title)
            
            # Exclude retrospective, recap, weekly summary, or explanation articles
            exclusions = ["지난주", "지지난주", "어제", "역사", "정리", "기자수첩", "주간", "월간", "분석", "전망", "잦아진", "의미", "이란?", "대처", "방법", "가능성", "우려"]
            is_excluded = any(ex in title for ex in exclusions)
            
            if is_excluded:
                has_sidecar = False
                has_cb = False
            
            # Find the time string by traversing the DOM near this a tag
            time_str = ""
            a_tag = soup.find("a", href=href)
            if a_tag:
                curr = a_tag
                found = False
                for _ in range(4):
                    curr = curr.parent
                    if not curr:
                        break
                    text_block = curr.get_text()
                    match = re.search(r'(\d+분\s*전|\d+시간\s*전|방금\s*전|\d+초\s*전|\d{4}\.\d{2}\.\d{2}\.)', text_block)
                    if match:
                        time_str = match.group(1)
                        found = True
                        break
                        
            articles.append({
                "title": title,
                "link": href,
                "time": time_str,
                "has_sidecar": has_sidecar,
                "has_cb": has_cb
            })
            
    except Exception as e:
        print(f"뉴스 크롤링 오류 ({keyword}): {e}")
        
    return articles

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "alerted_links": [],
        "alerted_dates": {}
    }

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    try:
        if len(state.get("alerted_links", [])) > 100:
            state["alerted_links"] = state["alerted_links"][-100:]
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"상태 저장 오류: {e}")

def main():
    now = datetime.now()
    
    # 1. trading day & hours check
    if now.weekday() >= 5:
        print("주말이므로 모니터링을 종료합니다.")
        return
        
    current_time = now.hour * 100 + now.minute
    if current_time < 850 or current_time > 1545:
        print("정규 장 시간(08:50 ~ 15:45)이 아니므로 모니터링을 종료합니다.")
        return
        
    today_str = now.strftime("%Y-%m-%d")
    state = load_state()
    
    # Initialize today's alerted list in state
    if "alerted_dates" not in state:
        state["alerted_dates"] = {}
    if today_str not in state["alerted_dates"]:
        state["alerted_dates"][today_str] = []
        
    # If 2 or more alerts were already sent today, skip monitoring to prevent duplicates
    if len(state["alerted_dates"][today_str]) >= 2:
        print("오늘 이미 2건 이상의 시장조치 알림을 발송했으므로 오늘 하루 동안 모니터링을 종료합니다.")
        return
        
    alerts = []
    
    # 2. Check market indices for massive drop (Circuit Breaker thresholds)
    indices = get_market_indices()
    for name, data in indices.items():
        pct = data["pct"]
        price = data["price"]
        
        for level, threshold in [("3단계", -20.0), ("2단계", -15.0), ("1단계", -8.0)]:
            alert_key = f"cb_{name.lower()}_{level}"
            if pct <= threshold and alert_key not in state["alerted_dates"][today_str]:
                if len(state["alerted_dates"][today_str]) >= 2:
                    continue
                alerts.append(
                    f"⚠️ [시장조치] {name} 지수 {level} 서킷브레이커 발동 조건 감지!\n"
                    f"현재가: {price:,.2f} ({pct:+.2f}%)"
                )
                state["alerted_dates"][today_str].append(alert_key)
                break
                
    # 3. Check Naver News for Sidecar or Circuit Breaker activation
    keywords = ["사이드카 발동", "서킷브레이커 발동"]
    for kw in keywords:
        articles = check_news_for_halt(kw)
        for art in articles:
            title = art["title"]
            link = art["link"]
            time_str = art["time"]
            has_sidecar = art.get("has_sidecar", False)
            has_cb = art.get("has_cb", False)
            
            is_recent = any(r_kw in time_str for r_kw in ["분 전", "초 전", "방금 전"])
            
            if "alerted_links" not in state:
                state["alerted_links"] = []
                
            if is_recent and link not in state["alerted_links"]:
                if has_sidecar or has_cb:
                    if len(state["alerted_dates"][today_str]) >= 2:
                        continue
                    event_type = "사이드카" if has_sidecar else "서킷브레이커"
                    alerts.append(
                        f"🚨 [속보] 실시간 {event_type} 발동 감지!\n\n"
                        f"제목: {title}\n"
                        f"시간: {time_str}\n"
                        f"링크: {link}"
                    )
                    state["alerted_links"].append(link)
                    state["alerted_dates"][today_str].append(f"news_{event_type}")
                    
    # 4. Send telegram alert if any
    if alerts:
        for alert in alerts:
            send_telegram(alert)
        save_state(state)
        print(f"알림 발송 완료: {len(alerts)}건")
    else:
        print("특이사항이 없으므로 알림을 보내지 않고 종료합니다.")

if __name__ == "__main__":
    main()
