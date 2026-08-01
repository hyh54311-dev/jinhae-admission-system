import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

found_matches = []
for idx, line in enumerate(lines):
    if "15시 15분" in line or "15:15" in line:
        found_matches.append((idx + 1, line.strip()))

print(f"Total matches found: {len(found_matches)}")
for line_no, content in found_matches:
    print(f"Line {line_no}: {content.encode('utf-8')}")
