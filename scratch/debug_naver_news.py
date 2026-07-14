# -*- coding: utf-8 -*-
import requests
import urllib3
from bs4 import BeautifulSoup
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://search.naver.com/search.naver?where=news&query=사이드카+발동&sort=1"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
res = requests.get(url, headers=headers, verify=False, timeout=10)
res.encoding = 'utf-8'

soup = BeautifulSoup(res.text, 'html.parser')

articles = {}
for a in soup.find_all("a"):
    href = a.get("href", "").strip()
    text = a.get_text(strip=True)
    
    if not href or href.startswith("#") or len(text) < 10:
        continue
        
    # Filter out navigation / search helper links
    if "search.naver.com" in href or "help.naver.com" in href or "policy.naver.com" in href:
        continue
    if "ssc=" in href or "where=" in href:
        continue
        
    # Group by href
    if href not in articles:
        articles[href] = []
    articles[href].append(text)

print(f"Grouped articles count: {len(articles)}")

# Print details of found articles
count = 0
for href, texts in articles.items():
    count += 1
    # Sort texts by length. The shorter one is usually the title.
    sorted_texts = sorted(texts, key=len)
    title = sorted_texts[0]
    snippet = sorted_texts[1] if len(sorted_texts) > 1 else ""
    
    # Try to find publication time by searching near the link in the DOM
    # Let's find the original a tag in the document
    time_str = "Not Found"
    a_tag = soup.find("a", href=href)
    if a_tag:
        # Check parents up to 4 levels for time strings
        curr = a_tag
        found = False
        for _ in range(4):
            curr = curr.parent
            if not curr:
                break
            # Look for spans or text containing "분 전", "시간 전", "방금", etc.
            text_block = curr.get_text()
            # Regex to match: 1분 전, 10분 전, 방금 전, 1시간 전, 2시간 전, or dates like 2026.06.10.
            match = re.search(r'(\d+분\s*전|\d+시간\s*전|방금\s*전|\d{4}\.\d{2}\.\d{2}\.)', text_block)
            if match:
                time_str = match.group(1)
                found = True
                break
                
    print(f"\n[{count}] Title: {title.encode('utf-8', errors='replace').decode('utf-8')}")
    print(f"    Snippet: {snippet[:80].encode('utf-8', errors='replace').decode('utf-8')}...")
    print(f"    Time: {time_str}")
    print(f"    Href: {href}")
    if count >= 5:
        break
