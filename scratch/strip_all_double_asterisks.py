import os
import sys

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 원고 전체에서 모든 '**' 별표 기호 완전 제거
count_double_stars = text.count('**')
text_cleaned = text.replace('**', '')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text_cleaned)

print(f"SUCCESSFULLY STRIPPED ALL {count_double_stars} '**' DOUBLE ASTERISKS FROM MANUSCRIPT!")
