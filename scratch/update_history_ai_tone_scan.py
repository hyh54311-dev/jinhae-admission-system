import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

ai_tone_scan_history_entry = """

---

### 📍 항목 5.5: 원고 전체(2,228 라인) AI 로봇/상투적 어투 및 3인칭 과장 표현 전수 교정 (71개 문장 100% 저자 1인칭 현장 교사 어조 치환) (2026-08-02 확정 반영)
* **원고 위치:** `원고 전체 (1부 ~ 4부 및 에필로그 부록)`
* **수정 이유:** 
  1. 저자의 지시에 따라, "AI가 대신 쓰는 것 같은 3인칭 로봇 말투"("저자 황요한 선생님은...", "~에 주목할 필요가 있습니다", "~를 선사합니다", "경이로운", "대혁신", "철통 보안", "피바다가 되어", "줍줍", "물타기" 등 AI 상투어 및 과장 조어) 총 71개 문장을 전수 스캔함.
  2. 황요한 저자가 직접 집필한 **자연스럽고 소박하며 따뜻한 1인칭 현장 교사 어조("제가 교직 생활을 하면서...", "저 역시 처음에...", "~해 드립니다", "~해 보았습니다")**로 100% 깔끔하게 교정 수록 완료함.

```diff
- 저자 황요한 선생님께서 / 저자 황요한 선생님은 / 황요한 저자의 / 저자(황요한)가
+ 제가 / 저는 / 저의 / 제가
- 경이로운 혁신을 경험했습니다 / 대혁신을 만났고 / 피바다가 되어 / 줍줍 / 물타기
+ 마음이 한결 가벼워지고 편안해졌습니다 / 큰 변화를 경험했고 / 큰 하락장이 와서 / 매수 / 추가 매수
```
"""

if "원고 전체(2,228 라인) AI 로봇/상투적 어투 및 3인칭 과장 표현 전수 교정" not in content:
    content += ai_tone_scan_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH FULL AI TONE SCAN!")
