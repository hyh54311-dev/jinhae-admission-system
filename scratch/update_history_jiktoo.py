import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

jiktoo_history_entry = """

---

### 📍 항목 3.3: 원고 전체 줄임말 '직투' ➔ 정식 용어 '직접 투자'로 전량 치환 (2026-08-02 확정 반영)
* **원고 위치:** `원고 전체 (Line 229, Line 277, Line 309, Line 476 등)`
* **수정 이유:** '직투'라는 구어체 속어/줄임말 대신 '직접 투자'라는 정제되고 정돈된 정식 단어로 교정하여 독자의 이해도와 도서의 품질을 향상.

```diff
- 연금저축 계좌에서는 관련 법상 미국 현지 주식이나 미국 직투 ETF(예: VOO, TLT)를 직접 매수할 수 없습니다.
+ 연금저축 계좌에서는 관련 법상 미국 현지 주식이나 미국 상장 직접 투자 ETF(예: VOO, TLT)를 직접 매수할 수 없습니다.
```
"""

if "원고 전체 줄임말 '직투' ➔ 정식 용어 '직접 투자'로 전량 치환" not in content:
    content += jiktoo_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH '직접 투자' REPLACEMENT!")
