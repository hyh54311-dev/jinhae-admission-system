# -*- coding: utf-8 -*-
"""
Monthly Global Economic Calendar Telegram Notifier
Runs on the 1st of every month. Fetches the current month's key US/Global economic schedules,
analyzes them using Gemini API, and sends a professional Korean briefing to Telegram.
Configured with 'StartWhenAvailable' to execute immediately when the PC turns on if the scheduled time was missed.
"""
import os
import sys
import json
import re
import requests
import urllib3
from datetime import datetime
from dotenv import load_dotenv
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Load environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def send_telegram(msg):
    print(f"[TELEGRAM] {msg}")
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML"
        }
        try:
            res = requests.post(url, json=payload, verify=False, timeout=15)
            if res.status_code != 200:
                print(f"텔레그램 발송 실패: {res.status_code} - {res.text}")
        except Exception as e:
            print(f"텔레그램 발송 오류: {e}")

def fetch_search_results(query):
    url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        res = requests.get(url, headers=headers, verify=False, timeout=15)
        if res.status_code != 200:
            return "Search failed"
        
        # Parse titles and snippets
        text = res.text
        titles = re.findall(r'class="result__title"[^>]*>(.*?)</h2>', text, re.DOTALL)
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', text, re.DOTALL)
        
        results = []
        for i in range(min(len(titles), len(snippets), 6)):
            title = re.sub(r'<[^>]+>', '', titles[i]).replace('\n', ' ').strip()
            snippet = re.sub(r'<[^>]+>', '', snippets[i]).replace('\n', ' ').strip()
            title = title.replace('&amp;', '&').replace('&quot;', '"').replace('&#x27;', "'")
            snippet = snippet.replace('&amp;', '&').replace('&quot;', '"').replace('&#x27;', "'")
            results.append(f"- {title}: {snippet}")
        return "\n".join(results)
    except Exception as e:
        return f"Search error: {e}"

def generate_calendar_via_gemini(month_str, search_data):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY가 환경 변수에 설정되어 있지 않습니다.")
        
    model_name = "gemini-3.1-flash-lite"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    prompt = (
        f"당신은 글로벌 매크로 투자 전문가이자 수석 이코노미스트입니다. 현재 기준 월은 **{month_str}**입니다.\n"
        f"아래는 이번 달 주요 미국 경제 지표 일정과 관련된 최신 검색 자료입니다.\n"
        f"--------------------\n{search_data}\n--------------------\n\n"
        f"위 정보와 당신의 최신 지식을 바탕으로 이번 달 **{month_str}**에 발표 예정인 핵심 경제 지표 및 일정 리스트를 작성해 주세요.\n"
        f"포함되어야 할 필수 일정:\n"
        f"- 미국 소비자물가지수 (CPI)\n"
        f"- 미국 생산자물가지수 (PPI)\n"
        f"- 미국 연준 FOMC 금리 결정\n"
        f"- 미국 개인소비지출 (PCE) 물가지수\n"
        f"- 미국 소매판매 (Retail Sales)\n"
        f"- 미국 GDP 발표 일정 등\n\n"
        f"형식 및 요구사항:\n"
        f"1. HTML 형식으로 작성해 주십시오. (주의: 텔레그램 전송용이므로 <b>, <i>, <code>, <pre> 태그와 <a> 링크만 사용 가능하며, <html>, <body>, <div>, <p>, <span>, <br> 등의 문서 구조 및 개행 태그는 절대 사용하지 마십시오. 마크다운 문법인 ** 또는 - 기호는 절대 사용하면 안 됩니다. <b> 태그를 사용해 텍스트를 볼드로 만들고 줄바꿈은 일반적인 텍스트 줄바꿈(엔터)만 사용하세요.)\n"
        f"2. 각 일정마다 발표 날짜(한국 시간 기준 추정일 포함)와 시간, 그리고 각 이벤트가 한국 시장(코스피)에 미칠 영향(인사이트)을 짧고 날카롭게 분석해 주세요.\n"
        f"3. 텔레그램 화면에서 읽기 편하도록 이모지를 적극적으로 활용하고 문단을 잘 쪼개어 구성해 주세요.\n"
        f"4. 맨 앞에는 이번 달의 종합적인 매크로 관전 포인트를 2-3줄 요약해 주십시오."
    )
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2}
    }
    headers = {"Content-Type": "application/json"}
    
    res = requests.post(url, headers=headers, json=payload, timeout=45)
    res.raise_for_status()
    json_data = res.json()
    parts = json_data.get("candidates", [])[0].get("content", {}).get("parts", [])
    return "".join([p.get("text", "") for p in parts])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Dry-run test mode without sending Telegram")
    args = parser.parse_args()
    
    now = datetime.now()
    month_str = now.strftime("%Y년 %m월")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Monthly Economic Calendar for {month_str}...")
    
    try:
        # Search query for the current month's US economic schedule
        query = f"US economic calendar {now.strftime('%B %Y')} fed fomc cpi pce ppi releases schedule"
        print(f"Searching: '{query}'...")
        search_data = fetch_search_results(query)
        
        print("Generating calendar content via Gemini API...")
        calendar_msg = generate_calendar_via_gemini(month_str, search_data)
        
        # Format title
        header = f"📅 <b>[{month_str} 글로벌 주요 경제 일정 캘린더]</b>\n\n"
        full_msg = header + calendar_msg
        
        # Clean unsupported Telegram HTML tags defensively
        unsupported_tags = ["<html>", "</html>", "<body>", "</body>", "<p>", "</p>", "<div>", "</div>"]
        for tag in unsupported_tags:
            full_msg = full_msg.replace(tag, "")
            full_msg = full_msg.replace(tag.upper(), "")
            
        # Replace br tags with newlines
        full_msg = full_msg.replace("<br/>", "\n").replace("<br>", "\n")
        full_msg = full_msg.replace("<BR/>", "\n").replace("<BR>", "\n")
            
        if not args.test:
            send_telegram(full_msg)
            print("Monthly economic calendar notification sent successfully.")
        else:
            print("[TEST MODE] Telegram transmission skipped. Output content:\n", full_msg)
        
    except Exception as e:
        err_msg = f"🚨 <b>[{month_str} 월간 캘린더 봇] 실행 중 오류 발생</b>\n사유: {e}"
        print(err_msg)
        send_telegram(err_msg)

if __name__ == "__main__":
    main()
