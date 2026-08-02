import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

sec41_first_person_history_entry = """

---

### 📍 항목 5.1: 4부 4.1절 및 4.3절 구글 안티그래비티(Antigravity) 활용법 황요한 저자 1인칭 현장 교사 어조 전면 개편 (2026-08-02 확정 반영)
* **원고 위치:** `4부 4.1절 및 4.3절 개발 에세이` (Line 870 부근)
* **수정 이유:** 
  1. 저자의 지시에 따라 딱딱하고 로봇 같은 AI 3인칭 문체("저자 황요한 선생님께서 완성하신 방식대로...")를 전면 제거함.
  2. 황요한 저자가 육아휴직 밤샘 개발과 복직 후 에듀테크 앱(`jinhae-bot2`)을 완성하며 느낀 진솔하고 따뜻한 **현장 1인칭 어조("제가 육아휴직 기간 동안 직접 체득했던 구글 안티그래비티 활용법을 이야기해 드리겠습니다...")**로 100% 개편 수록.

```diff
+ ### 4.1 구글 안티그래비티(Antigravity) 시작 가이드 및 100% 무상 혜택 활용법
+ 제가 육아휴직 기간 밤을 새우며 퀀트 자동매매 봇과 교직 에듀테크 앱을 직접 개발할 때 가장 큰 은인을 꼽으라면 단연 구글 안티그래비티(Google Antigravity)입니다.
```
"""

if "4.1절 및 4.3절 구글 안티그래비티(Antigravity) 활용법 황요한 저자 1인칭" not in content:
    content += sec41_first_person_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH SECTION 4.1 FIRST-PERSON TONE!")
