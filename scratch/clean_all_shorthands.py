import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 정밀 단어 치환
text = text.replace("해외주식 및 개별주 매매의", "해외 주식 및 개별 주식 매매의")
text = text.replace("미국채권", "미국 채권")
text = text.replace("국내주식", "국내 주식")
text = text.replace("해외주식", "해외 주식")
text = text.replace("과정 중심의 생기부 평가가", "과정 중심의 학교생활기록부 평가가")
text = text.replace("(세특·행특)", "(세부능력 및 특기사항·행동특성 및 종합의견)")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESSFULLY CLEANED UP ALL SHORTHAND TERMS IN MANUSCRIPT!")
