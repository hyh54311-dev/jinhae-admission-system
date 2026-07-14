# -*- coding: utf-8 -*-
import requests
import urllib3
import re
import sys

urllib3.disable_warnings()
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
res = requests.get('https://html.duckduckgo.com/html/?q=US+CPI+May+2026', headers=headers, verify=False, timeout=10)
text = res.text

# Find all <h2>, <h3>, or class="result__title"
h2_tags = re.findall(r'<h2[^>]*>(.*?)</h2>', text, re.DOTALL)
print(f"H2 Tags found: {len(h2_tags)}")
for i, tag in enumerate(h2_tags[:5], 1):
    print(f"{i}: {re.sub(r'<[^>]+>', '', tag).strip()}")

print("\nSearch for result__title in text:")
result_titles = re.findall(r'class="result__title"[^>]*>(.*?)</h2>', text, re.DOTALL)
print(f"result__title found: {len(result_titles)}")
for i, tag in enumerate(result_titles[:5], 1):
    print(f"{i}: {re.sub(r'<[^>]+>', '', tag).strip()}")
