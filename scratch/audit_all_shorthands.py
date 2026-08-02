import os
import re

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

keywords = ['개별주', '단기채', '미국채', '국내주', '해외주', '주식창', '생기부', '세특', '행특', '공모주', '우량주']

print("=== MANUSCRIPT SHORTHAND AUDIT REPORT ===")
for kw in keywords:
    matches = [(i + 1, line) for i, line in enumerate(text.split('\n')) if kw in line]
    print(f"\n[Keyword: '{kw}'] Found {len(matches)} occurrences:")
    for line_num, line_content in matches[:5]:  # show first 5
        print(f"  Line {line_num}: {line_content.strip()}")
    if len(matches) > 5:
        print(f"  ... and {len(matches) - 5} more.")
