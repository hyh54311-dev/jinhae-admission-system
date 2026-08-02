import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# '직투' ➔ '직접 투자' 치환
text = text.replace("해외 직투가 가능한", "해외 직접 투자가 가능한")
text = text.replace("미국 직투 ETF", "미국 상장 직접 투자 ETF")
text = text.replace("해외 직투 시", "해외 직접 투자 시")
text = text.replace("미국 현지 직투 주식", "미국 현지 직접 투자 주식")
text = text.replace("해외 직투", "해외 직접 투자")
text = text.replace("미국 직투", "미국 직접 투자")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESSFULLY REPLACED ALL '직투' WITH '직접 투자' IN MANUSCRIPT!")
