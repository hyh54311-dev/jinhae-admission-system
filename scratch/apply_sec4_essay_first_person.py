import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_sec4_essay = """#### 2. [2차 시도] Google Antigravity와 바이브 코딩(Vibe Coding)과의 운명적 만남
그러던 중 AI가 스스로 환경을 분석하고 코드를 작성하는 Google Antigravity(AGY) 에이전트를 접하게 되었습니다. 문법 하나하나로 씨름하는 대신 "한국투자증권 API 통신 예외 처리를 보완해 줘"라는 자연어 명령만으로 문제를 해결하는 '바이브 코딩(Vibe Coding)'의 대혁신을 만났고, 오랫동안 막혀 있던 핵심 매매 알고리즘을 비로소 완성할 수 있었습니다."""

repl_sec4_essay = """#### 2. [2차 시도] 구글 안티그래비티(Google Antigravity)와 바이브 코딩(Vibe Coding)과의 운명적 만남
그러던 중 구글 딥마인드 팀이 만든 최첨단 AI 에이전트인 **구글 안티그래비티(Google Antigravity)**를 만났습니다. 이것은 제 투자 인생과 교직 생활을 송두리째 바꾼 운명적인 만남이었습니다. 

어려운 문법 하나하나로 씨름하며 밤을 새우는 대신, **"한국투자증권 API에서 12개월 모멘텀 스코어 계산해서 안전자산 비중 조절해 줘"**라는 한글 자연어 지시만으로 코드가 척척 작성되고 에러까지 AI가 스스로 잡는 **'바이브 코딩(Vibe Coding)'**의 경이로운 세계를 경험했습니다. 오랫동안 저를 괴롭혔던 핵심 매매 알고리즘과 텔레그램 연동을 단 몇 시간 만에 완성해 냈을 때의 그 짜릿함은 지금도 잊을 수 없습니다."""

if target_sec4_essay in text:
    text = text.replace(target_sec4_essay, repl_sec4_essay)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY APPLIED SECTION 4 AUTHOR ESSAY NATURAL FIRST-PERSON TONE!")
else:
    print("TARGET SECTION 4 ESSAY TEXT NOT FOUND EXACTLY - CHECKING TEXT")
