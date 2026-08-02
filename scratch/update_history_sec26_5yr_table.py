import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

sec26_5yr_history_entry = """

---

### 📍 항목 3.9: 2.6절 5년 단위(5년, 10년, 15년, 20년) 복리 자산 및 과세이연 이자 격차 실측 표 수록 (2026-08-02 확정 반영)
* **원고 위치:** `2부 2.6절 과세 이연 파트` (Line 350 부근)
* **수정 이유:** 월 50만 원(연 600만 원) 적립 및 연 10% 복리 수익률 가정 시, 5년 단위로 자산과 이자가 불어나는 속도와 과세이연으로 인한 이자 수익금 격차(5년: +176만 ➔ 10년: +883만 ➔ 15년: +2,655만 ➔ 20년: +6,460만 원)를 눈으로 한눈에 입증하는 실측 비교표 수록.

```diff
+ #### 📈 [5년 단위 기간별 실측] 시간이 지날수록 폭발하는 과세이연 복리 이자 격차표
+ | 경과 기간 | 누적 투입 원금 | 일반 주식 계좌 자산<br>(누적 이자 수익금) | 연금저축펀드 자산<br>(누적 이자 수익금) | 과세이연으로 불어난<br>추가 이자(수익금) 격차 💡 |
```
"""

if "2.6절 5년 단위(5년, 10년, 15년, 20년) 복리 자산 및 과세이연 이자 격차" not in content:
    content += sec26_5yr_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH SECTION 2.6 5-YEAR STEP TABLE!")
