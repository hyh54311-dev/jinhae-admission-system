import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

sec42_complete_history_entry = """

---

### 📍 항목 5.2: 4.2절 3대 바이브 코딩 프롬프트 템플릿, 화면 캡처 디버깅 및 클로드(Claude) 교차 디버깅 팁 수록 (2026-08-02 확정 반영)
* **원고 위치:** `4부 4.2절` (Line 915 부근)
* **수정 이유:** 
  1. 초보 독자가 그대로 복사해 쓸 수 있는 3대 바이브 코딩 프롬프트 템플릿(KIS 계좌 잔고, AMS 12개월 모멘텀 계산, 텔레그램 및 GitHub Actions 무인 배포)과 팩트 체크포인트 수록.
  2. 에러 발생 시 텍스트 복사 및 **터미널/화면 캡처 이미지 첨부(Vision 멀티모달 디버깅)** 팁 반영.
  3. 저자의 현장 실전 노하우에 따라, 파이썬 코드 전체 문맥 파악 및 오류 수정 능력이 뛰어난 **클로드(Claude 3.5 Sonnet / Opus) 모델을 안티그래비티 IDE 내 모델 교체 또는 `claude.ai` 웹 접속으로 활용하는 교차 디버깅(Double Check) 꿀팁** 수록.

```diff
+ #### 💬 [프롬프트 템플릿 1~3] 실전 바이브 코딩 명령어 상자
+ ##### 1. 안티그래비티 10초 에러 해결법 (텍스트 복사 & 화면 캡처 이미지 첨부 📸)
+ ##### 2. 💡 [저자의 강력 추천] 클로드(Claude 3.5 Sonnet / Opus) 모델 교차 디버깅 활용법
```
"""

if "4.2절 3대 바이브 코딩 프롬프트 템플릿, 화면 캡처 디버깅 및 클로드" not in content:
    content += sec42_complete_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH SECTION 4.2 COMPLETE TIPS!")
