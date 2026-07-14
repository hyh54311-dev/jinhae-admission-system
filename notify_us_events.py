# -*- coding: utf-8 -*-
"""
US Economic Event Telegram Notifier (One-time Task)
Fetches the latest search results for CPI or FOMC and notifications to Telegram.
Automatically self-deletes from Windows Task Scheduler after execution.
"""
import os
import sys
import argparse
import requests
import urllib3
import re
import subprocess
from datetime import datetime
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def send_telegram(msg):
    print(f"[TELEGRAM] {msg}")
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, verify=False, timeout=10)
        except Exception as e:
            print(f"텔레그램 발송 실패: {e}")

def translate_via_gemini(news_text, event_type):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("[WARNING] GEMINI_API_KEY가 없어 번역을 생략하고 원문을 보냅니다.")
        return news_text
        
    model_name = "gemini-3.1-flash-lite"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    prompt = (
        f"당신은 엘리트 금융 분석가이자 전문 번역가입니다. 아래의 영어로 된 미국 경제 뉴스 속보(이벤트 유형: {event_type}) 리스트를 한국어로 번역하고 보기 좋게 요약해 주세요.\n"
        f"요구사항:\n"
        f"1. 각 뉴스 항목의 핵심 내용을 왜곡 없이 정확한 한국어 경제 금융 용어를 사용하여 친절하게 번역해 주세요.\n"
        f"2. 전체 요약이나 시장에 미칠 영향(코스피 영향 등)도 2-3줄 이내로 자연스럽게 덧붙여 주세요.\n"
        f"3. 가독성을 위해 문단과 볼드체(**) 등을 적절히 섞어 깔끔하게 포맷팅해 주세요.\n\n"
        f"--- 영어 뉴스 원문 ---\n{news_text}"
    )
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2}
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        res.raise_for_status()
        json_data = res.json()
        parts = json_data.get("candidates", [])[0].get("content", {}).get("parts", [])
        return "".join([p.get("text", "") for p in parts])
    except Exception as e:
        print(f"[ERROR] Gemini 번역 실패: {e}")
        return news_text

def fetch_latest_news(query):
    url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    res = requests.get(url, headers=headers, verify=False, timeout=15)
    if res.status_code != 200:
        raise Exception(f"News fetch failed: status {res.status_code}")
        
    text = res.text
    # Parse titles and snippets using regex
    titles = re.findall(r'class="result__title"[^>]*>(.*?)</h2>', text, re.DOTALL)
    snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', text, re.DOTALL)
    
    results = []
    for i in range(min(len(titles), len(snippets), 4)):
        title = re.sub(r'<[^>]+>', '', titles[i]).replace('\n', ' ').strip()
        snippet = re.sub(r'<[^>]+>', '', snippets[i]).replace('\n', ' ').strip()
        # Clean HTML entities
        title = title.replace('&amp;', '&').replace('&quot;', '"').replace('&#x27;', "'")
        snippet = snippet.replace('&amp;', '&').replace('&quot;', '"').replace('&#x27;', "'")
        results.append((title, snippet))
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True, choices=["cpi", "fomc", "ppi", "retail", "gdp", "pce"], help="Event type: cpi, fomc, ppi, retail, gdp, or pce")
    parser.add_argument("--task-name", required=True, help="Task name to self-delete")
    parser.add_argument("--test", action="store_true", help="Dry-run test mode without sending Telegram")
    args = parser.parse_args()
    
    event_type = args.event
    task_name = args.task_name
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] US Event Notifier Started: Event={event_type}, Task={task_name}")
    
    try:
        if event_type == "cpi":
            query = "US CPI May 2026 inflation rate results announced"
            title_prefix = "📅 [미국 5월 소비자물가지수(CPI) 발표 결과 브리핑]"
        elif event_type == "ppi":
            query = "US PPI May 2026 producer price index results announced"
            title_prefix = "🏭 [미국 5월 생산자물가지수(PPI) 발표 결과 브리핑]"
        elif event_type == "retail":
            query = "US May 2026 retail sales results announced"
            title_prefix = "🛍️ [미국 5월 소매판매(Retail Sales) 발표 결과 브리핑]"
        elif event_type == "gdp":
            query = "US Q1 2026 GDP third estimate revision announced"
            title_prefix = "📈 [미국 1분기 GDP 확정치 발표 결과 브리핑]"
        elif event_type == "pce":
            query = "US May 2026 PCE personal consumption expenditures price index announced"
            title_prefix = "💸 [미국 5월 개인소비지출(PCE) 물가지수 발표 결과 브리핑]"
        else:
            query = "FOMC June 2026 interest rate decision announcement"
            title_prefix = "🏛️ [미국 6월 FOMC 금리 결정 결과 브리핑]"
            
        print(f"Searching query: '{query}'...")
        news_items = fetch_latest_news(query)
        
        if not news_items:
            msg = f"{title_prefix}\n\n결과 정보를 인터넷에서 찾을 수 없습니다. 뉴스 확인이 필요합니다."
        else:
            briefing = [f"{title_prefix}\n\n미국 현지에서 발표된 최신 보도 및 주요 지표 정보입니다.\n"]
            for i, (title, snippet) in enumerate(news_items, 1):
                briefing.append(f"{i}. {title}\n  - {snippet}\n")
            raw_msg = "\n".join(briefing)
            print("Translating news content via Gemini API...")
            msg = translate_via_gemini(raw_msg, event_type)
            
        if not args.test:
            send_telegram(msg)
            print("Telegram notification sent successfully.")
        else:
            print("[TEST MODE] Telegram transmission skipped. Output content:\n", msg)
        
    except Exception as e:
        err_msg = f"🚨 [{event_type.upper()} 결과 알림 알리미] 실행 중 오류 발생: {e}"
        print(err_msg)
        send_telegram(err_msg)
        
    finally:
        # Self-delete this task from Windows Task Scheduler
        print(f"Self-deleting scheduled task: {task_name}...")
        try:
            # Run schtasks /delete
            cmd = f'schtasks /delete /tn "{task_name}" /f'
            subprocess.run(cmd, shell=True, check=True)
            print(f"Task '{task_name}' successfully deleted.")
        except Exception as se:
            print(f"Failed to delete scheduled task '{task_name}': {se}")

if __name__ == "__main__":
    main()
