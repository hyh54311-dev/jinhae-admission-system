import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_str = "* **② [2단계] 나만의 봇 만들기 (`/newbot` 명령어 전송):**"
replacement_str = """![텔레그램 BotFather 봇 생성 및 비밀키 발급 화면](telegram_botfather_hd.png)
> 📸 **[도서 실전 캡처 이미지 3] 텔레그램 `@BotFather` 봇 토큰 발급 대화 화면 (보안 암호 마스크 완료)**

* **② [2단계] 나만의 봇 만들기 (`/newbot` 명령어 전송):**"""

if target_str in text:
    new_text = text.replace(target_str, replacement_str)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("SUCCESSFULLY EMBEDDED TELEGRAM BOTFATHER MASKED IMAGE INTO MANUSCRIPT!")
else:
    print("TARGET STR NOT FOUND")
