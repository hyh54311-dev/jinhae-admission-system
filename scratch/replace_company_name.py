import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

count = text.count("삼성바이오로직스")
print(f"Found '삼성바이오로직스' {count} times in manuscript.")

new_text = text.replace("삼성바이오로직스", "국내 대표 바이오기업 종목")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_text)

print("SUCCESSFULLY REPLACED ALL '삼성바이오로직스' WITH '국내 대표 바이오기업 종목'!")
