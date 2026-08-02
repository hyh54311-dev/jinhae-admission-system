import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

numbers_conservative_history_entry = """

---

### 📍 항목 5.3: 안티그래비티 Pro 모델 일 50회 및 대화 20회 보수적 수치 정밀 교정 (2026-08-02 확정 반영)
* **원고 위치:** `3부 3.4절 및 4부 4.1절`
* **수정 이유:** 저자의 지시에 따라, 안티그래비티 Pro 모델 제공량을 보수적으로 **'일 50회 내외'**, ETF 종목 교체/테스트 대화 횟수를 **'하루 20회 대화'**로 선명하게 교정 수록함.

```diff
- Gemini Flash 모델 일 1,000회 이상, Pro 모델 일 50~100회 내외
+ Gemini Flash 모델 일 1,000회 내외, Pro 모델 일 50회 내외
- 하루 10~20회 대화로도 충분하므로
+ 하루 20회 대화로도 충분하므로
```
"""

if "Pro 모델 일 50회 및 대화 20회 보수적 수치 정밀 교정" not in content:
    content += numbers_conservative_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH CONSERVATIVE NUMBERS!")
