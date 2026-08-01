import json, sys
sys.stdout.reconfigure(encoding='utf-8')

file_path = r'C:\Users\요한T\.gemini\antigravity\brain\7a82df81-3c3f-49ab-aa25-d1655b5a4e5e\.system_generated\steps\71\content.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('{')
data = json.loads(text[start:])

posts = data.get('data', [])
print(f'Total posts: {len(posts)}')
print('====================================================')

for idx, p in enumerate(posts):
    attr = p.get('attributes', {})
    headline = attr.get('headline', '')
    subject = attr.get('subject', '')
    body = attr.get('body', '')
    sec_id = attr.get('wall_section_id', '')
    link_info = attr.get('attachment_link', {}) or {}
    link_title = link_info.get('title', '')
    link_url = link_info.get('url', '') or attr.get('attachment', '')
    
    print(f'[{idx+1}] Headline: {headline} | Subject: {subject} | Title: {link_title}')
    if body and body.strip():
        print(f'     Body: {body.strip()[:300]}')
    if link_url:
        print(f'     Link: {link_url[:200]}')
    print('----------------------------------------------------')
