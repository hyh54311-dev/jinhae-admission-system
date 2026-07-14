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

# Try to find class="result__snippet"
snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', text, re.DOTALL)
print(f"Found {len(snippets)} snippets")
for i, snip in enumerate(snippets[:5], 1):
    clean_snip = re.sub(r'<[^>]+>', '', snip)
    clean_snip = clean_snip.replace('\n', ' ').strip()
    print(f"{i}: {clean_snip}")
