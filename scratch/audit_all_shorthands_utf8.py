import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

keywords = ['개별주', '단기채', '미국채', '국내주', '해외주', '주식창', '생기부', '세특', '행특']

results = []
results.append("=== MANUSCRIPT SHORTHAND AUDIT REPORT ===\n")

for kw in keywords:
    matches = [(i + 1, line) for i, line in enumerate(text.split('\n')) if kw in line]
    results.append(f"[Keyword: '{kw}'] Found {len(matches)} occurrences:")
    for line_num, line_content in matches[:10]:
        results.append(f"  Line {line_num}: {line_content.strip()}")
    if len(matches) > 10:
        results.append(f"  ... and {len(matches) - 10} more.")
    results.append("")

out_file = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\scratch\shorthand_audit_results.txt'
with open(out_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))

print(f"SUCCESSFULLY SAVED SHORTHAND AUDIT REPORT TO {out_file}")
