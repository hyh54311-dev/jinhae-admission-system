import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_visual_block = """#### 🗺️ [3초 한눈에 파악하는 시각 자료] 주식 투자 5대 계좌 지형도

![주식·ETF 투자 5대 핵심 계좌 지형도 인포그래픽](5_core_investment_accounts_map.png)
> 📸 [도서 실전 시각 자료] 주식·ETF 투자 5대 핵심 계좌 카드 지형도 (내 투자 목적과 기간에 딱 맞는 최적의 계좌를 한눈에 선택)"""

repl_visual_block = """#### 🗺️ [종이책 출판용 1도 마인드맵] 주식 투자 5대 핵심 계좌 지형도

![주식·ETF 투자 5대 핵심 계좌 1도 마인드맵](5_core_investment_accounts_mindmap_mono.png)
> 📸 [도서 실전 1도 마인드맵 시각 자료] 주식·ETF 투자 5대 핵심 계좌 마인드맵 (내 투자 목적과 기간에 딱 맞는 최적의 계좌 구조를 한눈에 선택)"""

if target_visual_block in text:
    text = text.replace(target_visual_block, repl_visual_block)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY REPLACED WITH MONO MINDMAP IMAGE IN SECTION 2.1!")
else:
    print("TARGET VISUAL BLOCK NOT FOUND EXACTLY - CHECKING ALTERNATIVE")
