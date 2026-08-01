import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target1 = """3. 저장소 이름(예: `my-k-momentum-bot`)을 입력하고 `Create repository`를 누르면, 독자의 깃허브 계정에 무인 봇 환경이 100% 자동 세팅됩니다."""

repl1 = """3. 저장소 이름(예: `my-k-momentum-bot`)을 입력하고 `Create repository`를 누르면, 독자의 깃허브 계정에 무인 봇 환경이 100% 자동 세팅됩니다.

> 🔘 **[독자 필수 체크 1초 조치] GitHub Actions 무인 스케줄러 스위치 켜기:**  
> 깃허브 보안 정책상 템플릿으로 복사해 온 저장소의 자동 매매 스케줄러는 처음에 잠겨 있습니다. 복사된 본인 저장소 상단 **[Actions]** 탭을 클릭하고, 초록색 **`[I understand my workflows, go ahead and enable them]`** 버튼을 1초 만에 눌러 스위치를 켜주셔야 매월 무인 매매가 작동합니다!"""

if target1 in text:
    text = text.replace(target1, repl1)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY ENHANCED MANUSCRIPT WITH ACTIONS ENABLE GUIDE!")
else:
    print("TARGET NOT FOUND")
