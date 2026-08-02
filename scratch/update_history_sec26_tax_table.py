import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

sec26_tax_table_history_entry = """

---

### 📍 항목 3.8: 2.6절 연 600만 원(월 50만 원) 기준 20년 연 10% 과세이연 복리 비교표 및 입증 수록 (2026-08-02 확정 반영)
* **원고 위치:** `2부 2.6절 과세 이연 파트` (Line 350 부근)
* **수정 이유:** 
  1. 독자 기준에 맞추어 연금저축 기본 세액공제 납입 기준인 **'월 50만 원(연 600만 원)'**으로 예시 수치를 통일 정동.
  2. 동일한 10% 복리 수익률 가정 시 일반 계좌(매년 15.4% 세금 차감)와 연금저축펀드 계좌(100% 과세이연 재투자)의 20년 자본 격차 및 인출 시나리오 비교표 수록.
  3. 최악의 상황인 16.5% 기타소득세를 떼고 일시금 수령(3억 1,560만 원)하더라도 불어난 세전 자본 덕분에 일반 계좌(3억 1,340만 원)보다 이득이며, 정상 연금 수령(5.5%) 시 +4,380만 원 이상 압승한다는 팩트 수치 입증 수록.

```diff
+ #### 📊 [월 50만 원 / 연 600만 원 기준] 20년 과세이연 복리 자본 격차 실측 비교표
+ | 구분 및 투자 시나리오 | 20년 후 최종 자산 (세전/세후) | 실질 세후 수령액 (내 손에 쥐는 현금) 💵 | 일반 계좌 대비 최종 수익 차이 💡 |
```
"""

if "2.6절 연 600만 원(월 50만 원) 기준 20년 연 10% 과세이연 복리 비교표" not in content:
    content += sec26_tax_table_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH SECTION 2.6 TAX TABLE!")
