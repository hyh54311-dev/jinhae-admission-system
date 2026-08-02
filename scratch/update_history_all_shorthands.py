import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

all_shorthands_history_entry = """

---

### 📍 항목 3.4: 원고 전체 줄임말/속어 전수 정밀 교정 (2026-08-02 확정 반영)
* **원고 위치:** `원고 전체`
* **수정 이유:** 저자의 지시에 따라 원고 전체를 전수 감사하여, '개별주', '생기부', '해외주식', '국내주식', '미국채권' 등 각종 줄임말 및 붙여쓴 용어들을 '개별 주식', '학교생활기록부', '해외 주식', '국내 주식', '미국 채권' 등 정제되고 품격 높은 정식 표기로 100% 교정함.

```diff
- 과정 중심의 생기부 평가가
+ 과정 중심의 학교생활기록부 평가가

- 해외주식 및 개별주 매매의
+ 해외 주식 및 개별 주식 매매의
```
"""

if "원고 전체 줄임말/속어 전수 정밀 교정" not in content:
    content += all_shorthands_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH ALL SHORTHAND CLEANUPS!")
