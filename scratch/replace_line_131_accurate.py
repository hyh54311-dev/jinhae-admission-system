import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_str_old = "15시 15분, 텔레그램"
target_str_new = "낮 12시 30분, 텔레그램"

if target_str_old in text:
    new_text = text.replace(target_str_old, target_str_new)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("SUCCESSFULLY REPLACED LINE 131 TIME!")
else:
    print("TARGET STR OLD NOT FOUND")
