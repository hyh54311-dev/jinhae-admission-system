import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

remove_img_history_entry = """

---

### 📍 항목 2.8: 1.4절 진해고 챗봇 단독 이미지 및 캡처 주석 제거 (2026-08-02 확정 반영)
* **원고 위치:** `1부 1.4절 1번 진해고 챗봇 항목 하단` (Line 118 부근)
* **수정 이유:** 챗봇 단독 이미지만 수록되어 있던 시각적 미관상 불균형을 해소하기 위해 저자의 지시로 캡처 이미지 및 캡션 주석을 전면 제거하여 깔끔한 텍스트로 정돈.

```diff
-  ![진해고등학교 입학 상담 챗봇 v2.0 라이브 구동 화면](jinhae_bot2_hd.png)
- > 📸 [도서 실전 캡처 이미지 1] 진해고등학교 입학 상담 챗봇 v2.0 (`jinhae-bot2`) 라이브 구동 화면
+ (이미지 및 주석 제거 완료 - 깔끔한 텍스트로 정돈)
```
"""

if "1.4절 진해고 챗봇 단독 이미지 및 캡처 주석 제거" not in content:
    content += remove_img_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH JINHAE BOT IMAGE REMOVAL!")
