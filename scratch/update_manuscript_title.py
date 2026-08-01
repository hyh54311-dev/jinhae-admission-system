import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_title = "# 교사·공무원을 위한 퇴직연금 무인 퀀트 투자\n## 수업이나 업무 중에도 AI 봇이 굴리는 연금저축 & K-듀얼모멘텀 자동화 가이드\n\n"

# 첫 번째 # 타이틀 찾아서 교체
idx_h1 = -1
for i, l in enumerate(lines[:10]):
    if l.startswith("# "):
        idx_h1 = i
        break

if idx_h1 != -1:
    # # 타이틀 이전 및 이후 결합
    remainder = lines[idx_h1+1:]
    # 만약 바로 밑에 ## 서브타이틀이 있다면 제거
    if remainder and remainder[0].startswith("## "):
        remainder = remainder[1:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_title + "".join(remainder))
    print("SUCCESSFULLY UPDATED MANUSCRIPT TITLE TO OPTION 1 PERFECT VERSION!")
else:
    print("H1 TITLE NOT FOUND")
