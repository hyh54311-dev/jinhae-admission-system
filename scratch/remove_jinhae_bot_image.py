import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_image_block = """  ![진해고등학교 입학 상담 챗봇 v2.0 라이브 구동 화면](jinhae_bot2_hd.png)
> 📸 [도서 실전 캡처 이미지 1] 진해고등학교 입학 상담 챗봇 v2.0 (`jinhae-bot2`) 라이브 구동 화면"""

if target_image_block in text:
    text = text.replace(target_image_block, "")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY REMOVED JINHAE BOT IMAGE FROM SECTION 1.4!")
else:
    print("TARGET IMAGE BLOCK NOT FOUND EXACTLY - CHECKING ALTERNATIVE PATTERN")
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        if "jinhae_bot2_hd.png" in line or "[도서 실전 캡처 이미지 1] 진해고등학교 입학 상담 챗봇" in line:
            continue
        new_lines.append(line)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print("SUCCESSFULLY FILTERED OUT JINHAE BOT IMAGE LINES!")
