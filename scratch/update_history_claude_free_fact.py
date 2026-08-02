import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

claude_free_fact_history_entry = """

---

### 📍 항목 5.3: Claude 무료 플랜 모델 팩트 정밀 교정 (Claude Sonnet 무상 이용 명시) (2026-08-02 확정 반영)
* **원고 위치:** `4부 4.2절 디버깅 팁`
* **수정 이유:** 
  1. 앤스로픽(Anthropic) 공식 플랜 팩트에 따라, 가장 최고 성능 모델인 **Opus 모델은 유료 요금제 전용**이며, 웹(`claude.ai`) 및 무상 플랜에서 독자가 결제 없이 100% 무료로 사용할 수 있는 최상위 모델은 **Claude Sonnet** 모델임을 팩트 체크하여 명확히 교정 수록함.
  2. 독자들에게 혼선을 주지 않도록 **'Claude Sonnet (무료 플랜 기본 모델)'**로 명확히 표기함.

```diff
- 클로드(Claude 3.5 Sonnet 또는 Opus)
+ 클로드(Claude Sonnet)
```
"""

if "Claude 무료 플랜 모델 팩트 정밀 교정" not in content:
    content += claude_free_fact_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH CLAUDE FREE FACT!")
