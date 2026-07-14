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

# Find all <a class="xxx" ...>
classes = re.findall(r'<a class="([^"]+)"', text)
print("Unique Classes:")
print(set(classes))

# Print first few matches of <a class="some_class" ...> ... </a>
print("\nFirst few <a> tags:")
for m in re.finditer(r'<a class="([^"]+)"[^>]*>(.*?)</a>', text, re.DOTALL):
    print(f"Class: {m.group(1)}")
    print(f"Content: {re.sub(r'<[^>]+>', '', m.group(2)).strip()[:100]}")
    print("-" * 20)
