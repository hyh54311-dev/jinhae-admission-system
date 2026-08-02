import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

sec33_quant_table_history_entry = """

---

### 📍 항목 4.1: 3.3절 4대 퀀트 핵심 지표(CAGR, MDD, 샤프지수, 리밸런싱) 현실 직관 비교표 수록 (2026-08-02 확정 반영)
* **원고 위치:** `3부 3.3절 도입부` (Line 539 부근)
* **수정 이유:** 
  1. 매형의 피드백과 저자의 지시에 따라, 어렵고 딱딱한 수학/통계 용어(CAGR, MDD, 샤프지수, 리밸런싱)를 '마라톤 완주 속도', '지진 폭락장 고통 지수', '위험 대비 수익 가성비 지수', '계절별 옷장 정리 & 우등생 교체' 등 현장 친화적 현실 비유로 변환.
  2. 1도 흑백 출판에 완벽히 부합하는 **4대 퀀트 핵심 지표 현실 직관 비교표**로 구성하여 초보 독자의 학습 부담을 완전히 해소함.

```diff
+ #### 📊 [1도 출판 맞춤] 4대 퀀트 핵심 지표 현실 직관 비교표
+ | 지표명 (영문/한글) | 현실 직관 비유 💡 | 지표의 핵심 의미 & 목표 🎯 | K-듀얼모멘텀 봇에서의 실제 효과 🚀 |
```
"""

if "3.3절 4대 퀀트 핵심 지표(CAGR, MDD, 샤프지수, 리밸런싱) 현실 직관 비교표" not in content:
    content += sec33_quant_table_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH SECTION 3.3 QUANT TABLE!")
