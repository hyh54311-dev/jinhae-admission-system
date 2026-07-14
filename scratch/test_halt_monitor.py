# -*- coding: utf-8 -*-
import os
import sys
import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

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
    headers = {"User-Agent": "Mozilla/5.0"}
    articles = []
    try:
        res = requests.get(url, headers=headers, verify=False, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            bx_list = soup.select("ul.list_news > li.bx")
            if not bx_list:
                bx_list = soup.select(".news_wrap")
            for bx in bx_list:
                tit_el = bx.select_one(".news_tit")
                if not tit_el:
                    continue
                title = tit_el.get_text(strip=True)
                link = tit_el.get("href", "")
                time_str = ""
                info_list = bx.select(".info")
                for info in info_list:
                    txt = info.get_text(strip=True)
                    if "전" in txt or "방금" in txt or "." in txt:
                        if "선정" not in txt and "지면" not in txt:
                            time_str = txt
                            break
                articles.append({
                    "title": title,
                    "link": link,
                    "time": time_str
                })
    except Exception as e:
        print(f"뉴스 크롤링 오류 ({keyword}): {e}")
    return articles

print("--- 1. Yahoo Finance 지수 테스트 ---")
indices = get_market_indices()
for name, data in indices.items():
    print(f"{name}: 현재가 {data['price']:,.2f} / 전일대비 {data['pct']:+.2f}%")

print("\n--- 2. 네이버 뉴스 크롤링 테스트 ---")
for kw in ["사이드카 발동", "서킷브레이커 발동"]:
    print(f"\n키워드: [{kw}]")
    articles = check_news_for_halt(kw)[:3]  # 상위 3개만 출력
    for a in articles:
        print(f"- 제목: {a['title']}")
        print(f"  시간: {a['time']}")
        print(f"  링크: {a['link']}")
