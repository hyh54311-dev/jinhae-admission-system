import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

sec24_health_history_entry = """

---

### 📍 항목 3.6: 2.4절 국민건강보험법 건보료 0원 팩트 및 연 1,500만 원(부부 3,000만 원) 분리과세 안심 가이드 수록 (2026-08-02 확정 반영)
* **원고 위치:** `2부 2.4절 3대 절세 핵심 혜택 하단` (Line 333 부근)
* **수정 이유:** 
  1. 국민건강보험법 시행령 제41조 팩트에 근거하여 사적연금(연금저축/IRP) 인출금은 건보료 부과 대상 소득에서 **100% 전액 제외(건보료 0원)**된다는 법적 사실 수록.
  2. 2024년 대폭 개정된 **연간 1,500만 원(부부 합산 연 3,000만 원 / 월 250만 원) 분리과세**로 공무원연금이나 다른 소득과 일절 합산 없이 3.3%~5.5% 저율 과세로 완결된다는 안심 가이드 강화.
  3. 저자의 지시에 따라 `(건보료 인상률 0.0%)` 소괄호 표현 깔끔히 제거.

```diff
+ 🛡️ [법적 팩트 1] 연금저축/IRP 인출금은 건강보험료 부과 소득에서 '100% 전액 제외(건보료 0원)'됩니다!
+ 💰 [법적 팩트 2] 2024년 대폭 개정! '연 1,500만 원(월 125만 원) 분리과세'로 세금 폭탄 원천 차단
+ 💑 [부부 합산 팁] 부부 각각 수령 시 연 3,000만 원(월 250만 원)까지 분리과세 혜택!
```
"""

if "2.4절 국민건강보험법 건보료 0원 팩트 및 연 1,500만 원" not in content:
    content += sec24_health_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH SECTION 2.4 HEALTH INSURANCE & TAX FACTS!")
