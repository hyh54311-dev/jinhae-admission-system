import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

jargon_removal_history_entry = """

---

### 📍 항목 3.7: 원고 내 인위적 조어 '부부 듀얼 연금저축 봇' 전면 삭제 및 자연스러운 쉬운 문장으로 전수 교정 (2026-08-02 확정 반영)
* **원고 위치:** `2부 2.2절 및 2.4절`
* **수정 이유:** 저자가 사용하지 않은 인위적인 억지 조어('부부 듀얼 연금저축 봇')를 전면 삭제하고, "부부가 각각 연금저축 계좌를 만들어 함께 활용할 때"라는 쉽고 직관적인 현장 언어로 전수 교정함.

```diff
- '부부 듀얼 연금저축 봇'을 통해 남편과 아내가 각각 연금을 타 쓰면
+ '부부가 각각 연금저축 계좌를 만들어 함께 활용할 때' 남편과 아내가 각각 연금을 타 쓰면
```
"""

if "원고 내 인위적 조어 '부부 듀얼 연금저축 봇' 전면 삭제" not in content:
    content += jargon_removal_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH JARGON REMOVAL!")
