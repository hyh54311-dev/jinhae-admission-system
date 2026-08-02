import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

sec32_rubric_history_entry = """

---

### 📍 항목 4.2: 3.2절 5대 퀀트 전략(밸류, 퀄리티, 모멘텀, 마법공식, 동적자산배분) 교사·공무원 맞춤 학교 루브릭 비교표 수록 (2026-08-02 확정 반영)
* **원고 위치:** `3부 3.2절 도입부` (Line 505 부근)
* **수정 이유:** 저자의 지시에 따라, 5대 퀀트 전략을 교사와 공무원 독자가 날마다 접하는 '학생 성적 루브릭 평가 및 인사평가' 비유(숨은 진주 학생, 전교 1등 모범생, 최근 상승세 주자, 지필+수행 합산 1등, 재난 대피소 대피)로 풀어낸 **5대 퀀트 투자 전략 현실 루브릭 비교표** 수록.

```diff
+ #### 🏫 [교사·공무원 맞춤] 5대 퀀트 투자 전략 현실 루브릭 비교표
+ | 퀀트 전략 명칭 | 교사 & 공무원 현장 직관 비유 🏫 | 퀀트 투자에서의 실제 작동 원리 💡 | 봇에서의 실제 활용 & 장점 🚀 |
```
"""

if "3.2절 5대 퀀트 전략(밸류, 퀄리티, 모멘텀, 마법공식, 동적자산배분) 교사·공무원 맞춤 학교 루브릭 비교표" not in content:
    content += sec32_rubric_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH SECTION 3.2 RUBRIC TABLE!")
