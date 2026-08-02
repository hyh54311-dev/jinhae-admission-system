import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

clean_stars_history_entry = """

---

### 📍 항목 5.6: 원고 전체 불필요한 별표(*) 기호 제거 및 출판용 굵은 글씨 서식 정문화 (152개 라인 정제) (2026-08-02 확정 반영)
* **원고 위치:** `원고 전체 (1부 ~ 4부 및 에필로그 부록)`
* **수정 이유:** 
  1. 저자의 지시에 따라, 원고 문장 내에 난잡하게 들어간 불필요한 단일 별표(`*`) 이탈릭체 및 삼중 별표(`***`) 기호를 깔끔하게 제거함.
  2. 강조가 필요한 핵심 항목 및 제목은 출판 편집 규격에 적합한 깔끔한 **굵은 글씨체(`**내용**`)** 서식으로 정제 완료함.

```diff
- ***강조 내용*** / *단일 이탈릭 기호*
+ **강조 내용** / 깔끔한 텍스트 서식
```
"""

if "불필요한 별표(*) 기호 제거 및 출판용 굵은 글씨 서식" not in content:
    content += clean_stars_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH STARS CLEANING!")
