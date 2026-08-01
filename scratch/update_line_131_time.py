import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_line_old = "매달 1회 15시 15분, 텔레그램 메시지로 도착하는 매매 보고서 1줄로 계좌 리밸런싱이 완결되자,"
target_line_new = "매달 1회 낮 12시 30분, 텔레그램 메시지로 도착하는 매매 보고서 1줄로 계좌 리밸런싱이 완결되자,"

if target_line_old in text:
    new_text = text.replace(target_line_old, target_line_new)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("SUCCESSFULLY UPDATED LINE 131 TO '낮 12시 30분'!")
else:
    print("TARGET LINE 131 OLD NOT FOUND")
