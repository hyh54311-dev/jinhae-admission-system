import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

sec15_history_entry = """

---

### 📍 항목 2.6: 1.5절 독자 읽기 가이드 및 세특 AI 기재요령 규정 박스 보완 (2026-08-02 확정 반영)
* **원고 위치:** `1부 1.5절 도입부 및 하단 규정 상자` (Line 140 부근)
* **수정 이유:** 
  1. 매형 피드백("재테크 독자를 위한 읽기 가이드 제공") 반영.
  2. 매형 지적("AI 세특 기재 시 교사의 최종 검토 및 지침 준수 명시")을 반영하여 교육부 및 경남교육청 2026 기재요령 준수 팩트(AI는 초안 보조일 뿐, 교사의 100% 직접 관찰 확인 및 보완 필수)를 명확히 수록.

```diff
+ 💡 [독자 읽기 가이드]
+ "이 파트는 퀀트 자동화 봇을 통해 되찾은 시간으로 구축한 '교사 에듀테크 및 무상 Open API 자원' 소개입니다. 퀀트 투자의 구체적인 계좌 개설(2부) 및 듀얼모멘텀 매매 알고리즘(3부)을 먼저 공부하고 싶으신 독자께서는 2부로 곧바로 이동하셔도 무방합니다."

- 🛡️ [필수 체크] 에듀테크 웹앱 개발 시 학생·교사 개인정보 보호 4대 수칙...
+ 🛡️ [필수 체크] 세특 작성 시 생성형 AI 활용 가이드라인 & 개인정보 보호 4대 수칙
+ [교육부 및 경상남도교육청 2026 학교생활기록부 기재요령 준수 팩트]
+ 생성형 AI는 교사의 직접 관찰 기록을 매끄럽게 정리하는 '기초 초안(Draft) 보조 도구'일 뿐입니다. AI가 생성한 결과물을 교사의 검토 없이 나이스(NEIS)에 그대로 옮겨 적는 행위는 엄격히 금지되며, 반드시 담당 교사가 평소 직접 관찰한 수행 사실과 일치하는지 100% 확인, 보완, 수정 및 최종 승인 절차를 거쳐 기재해야 합니다.
```
"""

if "1.5절 독자 읽기 가이드 및 세특 AI 기재요령 규정 박스 보완" not in content:
    content += sec15_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH SECTION 1.5 GUIDELINES!")
