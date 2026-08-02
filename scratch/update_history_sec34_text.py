import os

history_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\author_edits_history.md'

with open(history_path, 'r', encoding='utf-8') as f:
    content = f.read()

sec34_text_history_entry = """

---

### 📍 항목 4.3: 3.4절 글 기준 텔레그램 봇 생성 3단계 절차 및 5대 무결점 안전장치 팩트 수록 (2026-08-02 확정 반영)
* **원고 위치:** `3부 3.4절 도입부` (Line 660 부근)
* **수정 이유:** 
  1. 본 도서의 본질(퀀트 자산배분 & 무인 자동매매 도서)에 부합하도록 불필요한 캡처 화면 대신, 독자가 글로만 읽어도 스마트폰에서 10초 만에 알림 봇을 생성할 수 있는 **글 중심 3단계 순서(BotFather ➔ 토큰 발급 ➔ userinfobot 챗ID 획득)** 가이드 수록.
  2. 파이썬 봇 소스 코드에 내장된 **5대 무결점 안전장치(휴장일 필터링, 영업일 자동 이월, 가용 현금 캡 추적, 텔레그램 4KB 트렁케이트 예방, KRX 종목 교차 검증)** 팩트를 명시하여 독자 안심성 확보.

```diff
+ #### 📱 [글로 따라 하는 3단계] 10초 만에 스마트폰 텔레그램 알림 봇 생성 가이드
+ #### 🛡️ [저자 팩트 보장] 실전 퀀트 봇에 완벽 내장된 5대 무결점 안전장치
```
"""

if "3.4절 글 기준 텔레그램 봇 생성 3단계 절차" not in content:
    content += sec34_text_history_entry

with open(history_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESSFULLY UPDATED AUTHOR EDITS HISTORY WITH SECTION 3.4 TEXT TELEGRAM GUIDE!")
