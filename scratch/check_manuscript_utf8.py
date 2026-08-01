import sys

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.split('\n')
print("=== 원고 세부 점검 결과 ===")
for i, line in enumerate(lines, 1):
    if 650 <= i <= 750:
        if "Open API" in line or "Actions" in line or "enable" in line.lower() or "신청" in line:
            print(f"Line {i}: {line.strip()}")
