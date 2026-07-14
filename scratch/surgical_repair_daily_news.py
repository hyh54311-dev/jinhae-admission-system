import os
import re

path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\daily_news.py"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the broken weekday_str line
content = re.sub(r'weekday_str = ".*?" if weekday == 5 else ".*?"', 'weekday_str = "토요일" if weekday == 5 else "일요일"', content)

# Fix the strftime line again just in case
content = re.sub(r'today_str_full = now\.strftime\(.*?\)', 'today_str_full = now.strftime("%Y년 %m월 %d일")', content)

# Clean up any remaining double-quote issues at the end of strings
content = content.replace('?")', '")')
content = content.replace('??)', '")')

# Fix the main print statements one last time
content = content.replace('print("- [ָ 08:30] ָ \x80로벌 & ?산???커??ڵ  ?\x80??)', 'print("- [주말 08:30] 주말 글로벌 & 신산업 포커스 자동 생성 대기 중")')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("daily_news.py has been surgically repaired.")
