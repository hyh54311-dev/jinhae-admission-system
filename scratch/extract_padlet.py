import re, json

with open(r'C:\Users\요한T\.gemini\antigravity\brain\7a82df81-3c3f-49ab-aa25-d1655b5a4e5e\.system_generated\steps\63\content.md', 'r', encoding='utf-8') as f:
    text = f.read()

title = re.search(r'<title>(.*?)</title>', text)
wishes_url = re.search(r'href="(/api/\d+/wishes\?[^"]+)"', text)

print('Title:', title.group(1) if title else 'N/A')
print('Wishes URL:', wishes_url.group(1) if wishes_url else 'N/A')
