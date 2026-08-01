import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

move_guide_history_entry = """

---

### 📍 항목 2.9: 독자 읽기 가이드 상자 위치 1.4절 도입부로 이동 (2026-08-02 확정 반영)
* **원고 위치:** `1부 1.4절 도입부` (Line 107 부근)
* **수정 이유:** 에듀테크 결실 및 AI 웹앱 소개가 시작되는 1.4절 도입부로 읽기 가이드 상자를 이동하여 재테크 전용 독자의 동선 가독성을 대폭 향상.

```diff
+ 💡 [독자 읽기 가이드]
+ "이 파트는 퀀트 자동화 봇을 통해 되찾은 시간으로 구축한 '교사 에듀테크 및 무상 Open API 자원' 소개입니다. 퀀트 투자의 구체적인 계좌 개설(2부) 및 듀얼모멘텀 매매 알고리즘(3부)을 먼저 공부하고 싶으신 독자께서는 2부로 곧바로 이동하셔도 무방합니다."
```
"""

if "독자 읽기 가이드 상자 위치 1.4절 도입부로 이동" not in content:
    content += move_guide_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH READER GUIDE BOX MOVE TO SEC 1.4!")
