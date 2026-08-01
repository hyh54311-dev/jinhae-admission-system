import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_str = """* **② [2단계] 나만의 봇 만들기 (`/newbot` 명령어 전송):**
  * 하단 **[시작(Start)]** 버튼을 누르거나 채팅창에 **`/newbot`** 을 입력해 보냅니다.
  * **봇 별명(Name) 입력:** 내가 알아보기 쉬운 이름 입력 (예: `요한의 연금 퀀트봇`)
  * **봇 아이디(Username) 입력:** 반드시 끝이 `bot`으로 끝나는 영문 아이디 입력 (예: `yohan_quant_bot`)"""

replacement_str = """* **② [2단계] 나만의 봇 만들기 (`/newbot` 명령어 전송):**
  * 하단 **[시작(Start)]** 버튼을 누르거나 채팅창에 **`/newbot`** 을 입력해 보냅니다.
  * **봇 별명(Name) 입력:** 내가 알아보기 쉬운 이름 입력 (예: `안티 제어 대화창` 또는 `요한의 연금 퀀트봇`)
  * **봇 아이디(Username) 입력:** 반드시 끝이 `bot`으로 끝나는 영문 아이디 입력 (예: `anti_control_yohan_bot`)"""

if target_str in text:
    new_text = text.replace(target_str, replacement_str)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("SUCCESSFULLY UPDATED BOT NAME AND USERNAME EXAMPLES IN MANUSCRIPT!")
else:
    print("TARGET STR NOT FOUND")
