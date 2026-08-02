import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_sec42_error_text = """##### 1. 안티그래비티 10초 에러 해결법
* 터미널 창에 빨간색 에러 메시지가 뜨면, 그 메시지 전체를 복사해서 안티그래비티 대화창에 그대로 붙여넣고 아래처럼 지시하세요.
> **"지금 이 에러가 발생했어. 원인을 분석하고 소스 코드를 바로 고쳐줘."**"""

repl_sec42_error_text = """##### 1. 안티그래비티 10초 에러 해결법 (텍스트 복사 & 화면 캡처 이미지 첨부)
* **방법 A [텍스트 복사]:** 터미널 창에 빨간색 에러 메시지가 뜨면, 그 메시지 전체를 복사해서 안티그래비티 대화창에 그대로 붙여넣고 지시하세요.
  > **"지금 이 에러가 발생했어. 원인을 분석하고 소스 코드를 바로 고쳐줘."**
* **방법 B [화면 캡처 이미지 첨부 📸]:** 텍스트 복사가 번거롭다면, **에러가 발생한 터미널 창이나 화면 전체를 캡처(윈도우: `Win + Shift + S`)하여 안티그래비티 대화창에 이미지로 첨부(붙여넣기)**하고 지시하세요.
  > **"이 캡처 화면에 보이는 오류를 분석해서 문제를 바로 해결해 줘."**  
  안티그래비티의 멀티모달(Vision) AI가 캡처 이미지 속의 에러 문장을 0.1초 만에 시각적으로 읽어내어 완벽한 교정 코드를 뚝딱 만들어 냅니다."""

if target_sec42_error_text in text:
    text = text.replace(target_sec42_error_text, repl_sec42_error_text)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY APPLIED VISION SCREENSHOT DEBUGGING TIP TO SECTION 4.2!")
else:
    print("TARGET SECTION 4.2 ERROR TEXT NOT FOUND EXACTLY - CHECKING TEXT")
