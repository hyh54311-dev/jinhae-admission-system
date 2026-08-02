import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

sec21_visual_history_entry = """

---

### 📍 항목 3.1: 2.1절 주식 투자 5대 핵심 계좌 시각자료 이미지 & 비교표 수록 (2026-08-02 확정 반영)
* **원고 위치:** `2부 2.1절 도입부` (Line 224 부근)
* **수정 이유:** 계좌 5종류(일반, ISA, 연금저축, IRP, CMA)를 설명할 때 텍스트만으로는 다소 헷갈린다는 매형의 피드백을 수용하여, **3초 만에 한눈에 들어오는 인포그래픽 시각자료 이미지(`5_core_investment_accounts_map.png`)**와 **5대 계좌 특징 종합 비교표**를 함께 수록.

```diff
+ #### 🗺️ [3초 한눈에 파악하는 시각 자료] 주식 투자 5대 계좌 지형도
+ ![주식·ETF 투자 5대 핵심 계좌 지형도 인포그래픽](5_core_investment_accounts_map.png)
+ > 📸 [도서 실전 시각 자료] 주식·ETF 투자 5대 핵심 계좌 카드 지형도 (내 투자 목적과 기간에 딱 맞는 최적의 계좌를 한눈에 선택)
+
+ #### 📊 [독자 맞춤형] 5대 핵심 계좌 특징 & 절세 혜택 종합 비교표
+ | 계좌 명칭 (상품코드) | 주요 매수 가능 종목 | 세금 & 절세 혜택 💡 | 건보료 영향 🛡️ | 이 계좌의 핵심 역할 & 퀀트 봇 연동 |
```
"""

if "2.1절 주식 투자 5대 핵심 계좌 시각자료 이미지 & 비교표 수록" not in content:
    content += sec21_visual_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH SECTION 2.1 VISUALS!")
