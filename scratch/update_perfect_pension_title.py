import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_title_perfect = "# 100% 완벽 자동화! 초보자도 쉬운 교사·공무원 연금계좌 퀀트 투자\n## 수업이나 업무 중에도 AI 봇이 알아서 굴리는 연금저축 & K-듀얼모멘텀 가이드\n\n"

# 첫 번째 # 타이틀 찾아서 교체
idx_h1 = -1
for i, l in enumerate(lines[:10]):
    if l.startswith("# "):
        idx_h1 = i
        break

if idx_h1 != -1:
    remainder = lines[idx_h1+1:]
    if remainder and remainder[0].startswith("## "):
        remainder = remainder[1:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_title_perfect + "".join(remainder))
    print("SUCCESSFULLY UPDATED MANUSCRIPT TITLE TO FINAL PERFECT VERSION!")
else:
    print("H1 TITLE NOT FOUND")
