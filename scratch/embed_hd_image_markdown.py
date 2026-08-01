import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

placeholder_str = "> 📸 **[도서 포함 예정 이미지 1: 진해고등학교 입학 상담 챗봇 v2.0 (`jinhae-bot2`) 실제 라이브 구동 화면]**"
image_markdown = """![진해고등학교 입학 상담 챗봇 v2.0 라이브 구동 화면](jinhae_bot2_hd.png)
> 📸 **[도서 실전 캡처 이미지 1] 진해고등학교 입학 상담 챗봇 v2.0 (`jinhae-bot2`) 라이브 구동 화면**"""

if placeholder_str in text:
    new_text = text.replace(placeholder_str, image_markdown)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("SUCCESSFULLY EMBEDDED HIGH RES IMAGE MARKDOWN INTO MANUSCRIPT!")
else:
    print("PLACEHOLDER STR NOT FOUND")
