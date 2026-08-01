import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1.5절 도입부에 있던 독자 읽기 가이드 상자 삭제
sec15_guide_box = """> 💡 **[독자 읽기 가이드]**  
> *"이 파트는 퀀트 자동화 봇을 통해 되찾은 시간으로 구축한 '교사 에듀테크 및 무상 Open API 자원' 소개입니다. 퀀트 투자의 구체적인 계좌 개설(2부) 및 듀얼모멘텀 매매 알고리즘(3부)을 먼저 공부하고 싶으신 독자께서는 2부로 곧바로 이동하셔도 무방합니다."*

\n\n"""

if sec15_guide_box in text:
    text = text.replace(sec15_guide_box, "")

# 1.4절 도입부에 독자 읽기 가이드 상자 삽입
target_sec14_header = """### 1.4 주식 차트를 끄고 되찾은 본업: '수업 및 교직 업무 자동화'와 에듀테크 결실

매달 1회 텔레그램 메시지 1줄로 계좌 리밸런싱이 깔끔하게 완결되자"""

repl_sec14_header = """### 1.4 주식 차트를 끄고 되찾은 본업: '수업 및 교직 업무 자동화'와 에듀테크 결실

> 💡 **[독자 읽기 가이드]**  
> *"이 파트는 퀀트 자동화 봇을 통해 되찾은 시간으로 구축한 '교사 에듀테크 및 무상 Open API 자원' 소개입니다. 퀀트 투자의 구체적인 계좌 개설(2부) 및 듀얼모멘텀 매매 알고리즘(3부)을 먼저 공부하고 싶으신 독자께서는 2부로 곧바로 이동하셔도 무방합니다."*

매달 1회 텔레그램 메시지 1줄로 계좌 리밸런싱이 깔끔하게 완결되자"""

if target_sec14_header in text:
    text = text.replace(target_sec14_header, repl_sec14_header)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESSFULLY MOVED READER GUIDE BOX TO SECTION 1.4 INTRO!")
