import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

sec26_loan_history_entry = """

---

### 📍 항목 3.10: 2.6절 연금저축 담보대출의 3대 금융 팩트(ETF 대출 불가, 반대매매시 16.5% 세금, DSR 포함) 주의 경고 수록 (2026-08-02 확정 반영)
* **원고 위치:** `2부 2.6절 하단` (Line 380 부근)
* **수정 이유:** 
  1. 실시간 3중 웹 검색을 통해, ETF는 연금저축 담보대출 대상에서 대부분 제외되며, 담보유지비율(140%) 미달 시 반대매매로 인한 16.5% 기타소득세 세금 폭탄 위험이 있음을 확인.
  2. 연금저축 담보대출 원리금도 DSR(총부채원리금상환비율) 산정에 포함되어 타 금융권 대출 한도를 줄이는 팩트 반영.
  3. 무리한 담보대출 대신 연금저축 계좌는 과세이연 복리 엔진으로 보존하고 긴급 비상금은 CMA/파킹통장으로 관리하라는 저자의 안전 주의 가이드 수록.

```diff
+ ⚠️ [저자의 금융 팩트 경고] 목돈 필요 시 '연금저축 담보대출'을 함부로 쓰면 안 되는 이유
```
"""

if "2.6절 연금저축 담보대출의 3대 금융 팩트" not in content:
    content += sec26_loan_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH SECTION 2.6 LOAN WARNING!")
