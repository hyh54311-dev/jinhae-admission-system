import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

sec22_scope_history_entry = """

---

### 📍 항목 3.2: 2.2절 도서 전용 범위 명시 (연금저축/IRP 한정) 및 부부 듀얼 연금저축/증여세 비과세 수록 (2026-08-02 확정 반영)
* **원고 위치:** `2부 2.2절 도입부` (Line 245 부근)
* **수정 이유:** 
  1. 1억 이상 목돈 및 일반 계좌 퀀트는 후속작 **'올웨더 자산배분 자동 투자 봇'** 도서로 이관하고, 본 도서는 오롯이 **'연금저축 & IRP 계좌'만을 대상으로 100% 집중**한다는 범위 명시.
  2. 본인과 배우자 각각 연금계좌 개설 ➔ 부부 합산 연 1,200만 원(월 100만 원) 투자 확장 수록.
  3. 무소득 배우자 납입 시 상속세 및 증여세법 제53조(배우자 10년 6억 비과세) 적용으로 증여세 0원 안심 Q&A 박스 수록.

```diff
+ > 💡 [도서 범위 안내: 이 책은 오롯이 '연금저축 & IRP 계좌' 전용 퀀트 가이드입니다]
+ > *"1억 원 이상의 대형 목돈이나 일반 주식 계좌를 활용한 자동 투자 전략은 저자의 후속작인 '올웨더 자산배분 자동 투자 봇' 도서에서 깊이 있게 다룰 예정입니다."*
+ 
+ #### 💑 [부부 듀얼 절세 꿀팁] 부부 각각 연금계좌 개설 시 연 1,200만 원까지 절세 투자 확장!
+ > 🛡️ [세무 Q&A] 소득이 없는 아내 명의로 연금저축을 넣어주면 증여세가 나오나요? (10년 6억 비과세 팩트)
```
"""

if "2.2절 도서 전용 범위 명시 (연금저축/IRP 한정)" not in content:
    content += sec22_scope_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH SECTION 2.2 SCOPE & COUPLE PENSION!")
