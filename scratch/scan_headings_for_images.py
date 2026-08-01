import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

headers = []
for idx, line in enumerate(lines):
    if line.startswith("#"):
        headers.append((idx + 1, line.strip()))

print(f"Total Headers: {len(headers)}")
for line_no, h in headers:
    print(f"Line {line_no}: {h.encode('utf-8')}")
