import os

path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\daily_news.py"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the broken strftime calls
content = content.replace('now.strftime("%Y??%m??%d??)', 'now.strftime("%Y년 %m월 %d일")')
content = content.replace('now.strftime("%Y??%m??%d??)', 'now.strftime("%Y년 %m월 %d일")') # Double check

# Fix some common corrupted markers seen in logs
content = content.replace('??뒛??', '오늘')
content = content.replace('??뒛', '오늘')
content = content.replace('??寃쎌????', '거시경제')
content = content.replace('?뱀???', '당신은')
content = content.replace('?뱀떊?€', '당신은')

# Standardize the strftime line just in case there are variations
import re
content = re.sub(r'now\.strftime\("%Y\?\?%m\?\?%d\?\?\)', 'now.strftime("%Y년 %m월 %d일")', content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("daily_news.py has been repaired.")
