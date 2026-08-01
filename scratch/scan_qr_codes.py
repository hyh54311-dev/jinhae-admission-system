import sys

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

qr_matches = []
for i, line in enumerate(lines, 1):
    if 'QR' in line or 'qr' in line:
        qr_matches.append((i, line.strip()))

print(f"Total lines containing 'QR': {len(qr_matches)}")
for idx, text in qr_matches:
    print(f"Line {idx}: {text}")
