import json, sys, os

sys.stdout.reconfigure(encoding='utf-8')

# Load Step 71 wishes (2기 패들렛)
file_path_2 = r'C:\Users\요한T\.gemini\antigravity\brain\7a82df81-3c3f-49ab-aa25-d1655b5a4e5e\.system_generated\steps\71\content.md'
with open(file_path_2, 'r', encoding='utf-8') as f:
    text2 = f.read()

data2 = json.loads(text2[text2.find('{'):])
posts2 = data2.get('data', [])

pdf_files = []

for idx, p in enumerate(posts2):
    attr = p.get('attributes', {})
    headline = attr.get('headline', '')
    link_info = attr.get('attachment_link', {}) or {}
    link_title = link_info.get('title', '')
    link_url = link_info.get('url', '') or attr.get('attachment', '')
    
    if link_url and ('.pdf' in link_url.lower() or '.pdf' in link_title.lower() or '특강' in headline or '원고' in headline):
        pdf_files.append({
            'headline': headline,
            'title': link_title if link_title else headline,
            'url': link_url
        })

print(f'Total PDF/Lecture Files found in 2nd Padlet: {len(pdf_files)}')
for item in pdf_files:
    print(f"- [{item['headline']}] {item['title']} -> {item['url'][:100]}...")

with open(r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\scratch\pdf_list.json', 'w', encoding='utf-8') as f:
    json.dump(pdf_files, f, ensure_ascii=False, indent=2)
