import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 3.4절 및 4.1절 정밀 보수적 수치 교정
target_text_1 = "Gemini Flash 모델 일 1,000회 이상, Pro 모델 일 50~100회 내외"
repl_text_1 = "Gemini Flash 모델 일 1,000회 내외, Pro 모델 일 50회 내외"

target_text_2 = "하루 10~20회 대화로도 충분하므로"
repl_text_2 = "하루 20회 대화로도 충분하므로"

target_text_3 = "Pro 모델 일 50100회"
repl_text_3 = "Pro 모델 일 50회"

target_text_4 = "하루 1020회"
repl_text_4 = "하루 20회"

text = text.replace(target_text_1, repl_text_1)
text = text.replace(target_text_2, repl_text_2)
text = text.replace(target_text_3, repl_text_3)
text = text.replace(target_text_4, repl_text_4)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESSFULLY CORRECTED PRO MODEL & DIALOGUE NUMBERS TO CONSERVATIVE STANDARDS!")
