import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

epilogue_lines = []
for idx, line in enumerate(lines):
    if "에필로그" in line:
        epilogue_lines.append((idx + 1, line.strip()))

print(f"Total 'epilogue' occurrences: {len(epilogue_lines)}")
for line_no, content in epilogue_lines:
    print(f"Line {line_no}: {content.encode('utf-8')}")
