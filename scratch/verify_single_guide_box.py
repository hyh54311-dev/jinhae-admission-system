import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

count = text.count("독자 읽기 가이드")
print(f"VERIFICATION: Total count of '독자 읽기 가이드' in manuscript: {count}")
assert count == 1, f"Expected 1, got {count}"
print("VERIFICATION SUCCESSFUL: EXACTLY ONE GUIDE BOX IN SECTION 1.4!")
