import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

sec34_policy_history_entry = """

---

### 📍 항목 5.2: 구글 안티그래비티(Antigravity) 무료 플랜 무상 사용량 팩트 및 미래 정책 변동성 경고 안내 수록 (2026-08-02 확정 반영)
* **원고 위치:** `3부 3.4절 도입부` (Line 662 부근)
* **수정 이유:** 
  1. 2026년 현시점 기준 신용카드 등록 없이 구글 계정으로 무상 이용 가능한 기본 사용 한도(Gemini Flash 일 1,000회 이상, Pro 일 50~100회) 팩트 수록.
  2. 저자의 지시에 따라, "평생 무조건 무료"라는 안일한 과장 서술을 경계하고, 빅테크 기업의 클라우드/AI 무상 한도 정책이 향후 개정될 수 있다는 **객관적이고 신중한 저자의 정책 변동성 유의사항** 수록.

```diff
+ 💡 [저자의 신중한 안내] 현재(2026년 기준) 무상 사용 한도와 향후 정책 변동성
+ ⚠️ 향후 정책 변동 가능성 안내: 독자 여러분께서는 책을 읽고 실행하시는 시점의 구글 안티그래비티 공식 서비스 약관을 함께 확인해 주시기 바랍니다.
```
"""

if "구글 안티그래비티(Antigravity) 무료 플랜 무상 사용량 팩트 및 미래 정책 변동성" not in content:
    content += sec34_policy_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH POLICY WARNING!")
