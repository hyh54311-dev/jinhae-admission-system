import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

sec14_history_entry = """

---

### 📍 항목 2.5: 1.4절 교사 AI 챗봇 연결 징검다리 서사 확정 반영 (2026-08-02 완료)
* **원고 위치:** `1부 1.4절 도입부 문단` (Line 106 부근)
* **수정 이유:** 주식 퀀트 봇 이야기에서 1.4절 교사 AI 챗봇(`jinhae-bot2`) 이야기로 넘어갈 때의 맥락 단절을 완벽히 해결하는 징검다리 서사 반영.

```diff
- [수정 전]: 첫 발령을 받고 교직에 나설 때부터, 저는 직접 돈을 벌기 시작하면서 경제와 관련된 공부를 깊이 있게 해야겠다고 다짐했습니다... 교사에게 주어진 시간 자원은 한정되어 있었고, 그 시간들을 무작정 쪼개 쓰는 방식에는 명확한 한계가 존재했습니다...
+ [수정 후]: 매달 1회 텔레그램 메시지 1줄로 계좌 리밸런싱이 깔끔하게 완결되자, 주식 차트를 들여다보고 매일 경제 소식을 쫓느라 소모하던 수많은 시간과 에너지가 완벽히 절약되었습니다. 그렇게 되찾은 매월 수십 시간의 소중한 여유는 제 삶에 커다란 변화를 가져왔습니다. 저는 이 되찾은 소중한 시간을 헛되이 보내지 않고, 안티그래비티 AI와 대화하며 퀀트 봇을 구축했던 개발 노하우를 '교사로서 가장 의미 있는 본업, 즉 아이들을 위한 수업과 교직 업무 자동화(에듀테크)'로 확장해 나가기 시작했습니다.
```
"""

if "1.4절 교사 AI 챗봇 연결 징검다리 서사 확정 반영" not in content:
    content += sec14_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH SECTION 1.4 BRIDGING TEXT!")
