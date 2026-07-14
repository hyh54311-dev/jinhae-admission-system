import os
import re

path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\daily_news.py"

with open(path, 'rb') as f:
    raw_content = f.read()

# Try to decode safely
content = raw_content.decode('utf-8', errors='replace')

# 1. Fix the specific SyntaxError line (318)
# We'll use a broad regex to find that whole industries block and replace it
industries_block = """industries = [
        "신재생에너지", "AI", "우주 산업", "전기차/자율주행", "SMR",
        "차세대 바이오/디지털 헬스케어", "로보틱스/에이전트", "양자 컴퓨팅", "차세대 반도체/스마트 팩토리"
    ]"""

# Find the messy industries list and replace it
content = re.sub(r'industries = \[\s+.*?\s+\]', industries_block, content, flags=re.DOTALL)

# 2. Fix the broken strftime from earlier attempt
content = content.replace('now.strftime("%Y??%m??%d??)', 'now.strftime("%Y년 %m월 %d일")')

# 3. Clean up other common corruption patterns
replacements = {
    "??뒛": "오늘",
    "??寃쎌????": "거시경제",
    "?뱀떊?€": "당신은",
    "二쇰쭚": "주말",
    "?댁뒪": "뉴스",
    "?앹꽦": "생성",
    "?먮룞": "자동",
    "?꾨즺": "완료",
    "?붾젅洹몃옩": "텔레그램",
    "?뚮┝": "알림",
    "留곹겕": "링크",
    "遺꾩꽍": "분석",
    "蹂듭궗": "복사",
    "?띿뒪??": "텍스트"
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("daily_news.py has been thoroughly cleaned and repaired.")
