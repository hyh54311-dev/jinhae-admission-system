import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_mindmap_block = """#### 🗺️ [종이책 출판용 1도 마인드맵] 주식 투자 5대 핵심 계좌 지형도

![주식·ETF 투자 5대 핵심 계좌 1도 마인드맵](5_core_investment_accounts_mindmap_mono.png)
> 📸 [도서 실전 1도 마인드맵 시각 자료] 주식·ETF 투자 5대 핵심 계좌 마인드맵 (내 투자 목적과 기간에 딱 맞는 최적의 계좌 구조를 한눈에 선택)

---

"""

if target_mindmap_block in text:
    text = text.replace(target_mindmap_block, "")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY REMOVED MINDMAP IMAGE FROM SECTION 2.1!")
else:
    print("CHECKING ALTERNATIVE PATTERN FOR MINDMAP REMOVAL")
    lines = text.split('\n')
    new_lines = []
    skip = False
    for line in lines:
        if "5_core_investment_accounts_mindmap_mono.png" in line or "[종이책 출판용 1도 마인드맵]" in line or "[도서 실전 1도 마인드맵 시각 자료]" in line:
            continue
        new_lines.append(line)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print("SUCCESSFULLY FILTERED OUT MINDMAP LINES FROM SECTION 2.1!")
