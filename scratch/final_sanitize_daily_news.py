import os

path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\daily_news.py"

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

clean_lines = []
for line in lines:
    # Fix the specific broken print lines in main()
    if "08:30" in line and "print" in line:
        line = '    print("- [주말 08:30] 주말 글로벌 & 신산업 포커스 자동 생성 대기 중")\n'
    if "15:15" in line and "print" in line:
        line = '    print("- [평일 15:15] 데일리 코스피 포커스 경제 뉴스 생성 시작")\n'
    
    # Remove lines with invalid non-printable characters like U+0080
    if '\x80' in line:
        line = line.replace('\x80', '')
    
    clean_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(clean_lines)

print("daily_news.py has been sanitized.")
