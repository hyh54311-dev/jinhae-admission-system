import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1.5절 도입부의 독자 읽기 가이드 상자 삭제
sec15_target_header = """### 1.5 확장되는 교육 자동화: NFC·음성 웹앱부터 제미나이와 에이전트 AI까지

> 💡 **[독자 읽기 가이드]**  
> *"이 파트는 퀀트 자동화 봇을 통해 되찾은 시간으로 구축한 '교사 에듀테크 및 무상 Open API 자원' 소개입니다. 퀀트 투자의 구체적인 계좌 개설(2부) 및 듀얼모멘텀 매매 알고리즘(3부)을 먼저 공부하고 싶으신 독자께서는 2부로 곧바로 이동하셔도 무방합니다."*

퀀트 봇을 만들기 훨씬 전부터"""

sec15_repl_header = """### 1.5 확장되는 교육 자동화: NFC·음성 웹앱부터 제미나이와 에이전트 AI까지

퀀트 봇을 만들기 훨씬 전부터"""

if sec15_target_header in text:
    text = text.replace(sec15_target_header, sec15_repl_header)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY REMOVED DUPLICATE READER GUIDE BOX FROM SECTION 1.5!")
else:
    print("CHECKING IF SECTION 1.5 ALREADY CLEAN")
    # 전체 텍스트에서 [독자 읽기 가이드]가 몇 개 있는지 체크
    count = text.count("독자 읽기 가이드")
    print(f"Total count of '독자 읽기 가이드' in manuscript: {count}")
    if count > 1:
        # 1.4절에만 남기고 1.5절 것은 삭제
        parts = text.split("### 1.5 확장되는 교육 자동화")
        part1 = parts[0]
        part2 = parts[1]
        part2_cleaned = part2.replace("""> 💡 **[독자 읽기 가이드]**  
> *"이 파트는 퀀트 자동화 봇을 통해 되찾은 시간으로 구축한 '교사 에듀테크 및 무상 Open API 자원' 소개입니다. 퀀트 투자의 구체적인 계좌 개설(2부) 및 듀얼모멘텀 매매 알고리즘(3부)을 먼저 공부하고 싶으신 독자께서는 2부로 곧바로 이동하셔도 무방합니다."*""", "").strip()
        text = part1 + "### 1.5 확장되는 교육 자동화\n\n" + part2_cleaned
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print("CLEANED UP SECTION 1.5 DUPLICATE BOX PERFECTLY!")
