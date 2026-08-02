import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_sec34_start = """### 3.4 Antigravity Vibe Coding 기반 K-듀얼모멘텀 파이썬 소스 코드 해설"""

repl_sec34_text = """### 3.4 Antigravity Vibe Coding 기반 K-듀얼모멘텀 파이썬 소스 코드 해설

Google Antigravity AI를 활용한 '바이브 코딩(Vibe Coding)'의 가장 뛰어난 점은, 복잡한 파이썬 코딩을 몰라도 내가 원하는 투자 로직을 자연어 대화로 지시하여 완전 무인 자동화 봇을 완성할 수 있다는 것입니다.

---

#### 📱 [글로 따라 하는 3단계] 10초 만에 스마트폰 텔레그램 알림 봇 생성 가이드

본 도서는 텔레그램 전용 설명서가 아니므로 복잡한 캡처 화면 대신, 독자 여러분이 글로 읽고 스마트폰에서 10초 만에 알림 봇을 만들 수 있도록 가장 쉽고 정돈된 3단계 절차를 안내합니다.

##### 1단계: 텔레그램 앱 실행 및 BotFather 접속
* 스마트폰에서 텔레그램 앱을 켜고 상단 돋보기(검색창)에 **`@BotFather`**를 검색하여 파란색 인증 마크가 붙은 공식 봇 대화방에 입장한 뒤 하단의 `시작` 버튼을 누릅니다.

##### 2단계: 신규 봇 생성 및 토큰(`TELEGRAM_TOKEN`) 획득
* 대화창에 **`/newbot`**을 입력해 메시지를 보냅니다.
* 봇의 이름을 입력하라는 안내가 나오면 **`MyQuantBot`** (원하는 이름)을 입력합니다.
* 봇의 사용자 아이디(Username)를 입력하라는 안내가 나오면 끝이 `bot`으로 끝나는 이름(예: **`jinhae_quant_bot`**)을 입력합니다.
* 생성이 완료되면 화면에 `HTTP API:` 문구 뒤에 매우 긴 영문+숫자 조합 문자열(예: `8407908239:AAHgWACsaJ9y4JMkxI...`)이 나옵니다. 이것이 바로 **`TELEGRAM_TOKEN`**이므로 복사해 둡니다.

##### 3단계: 내 개인 챗 ID(`TELEGRAM_CHAT_ID`) 획득
* 텔레그램 검색창에 **`@userinfobot`**을 검색하여 대화방에 입장한 뒤 **`/start`**를 입력합니다.
* 봇이 답장으로 내 계정의 `Id: 8518409134` 형태의 9~10자리 숫자를 보여줍니다. 이 숫자가 바로 내 개인 챗 ID인 **`TELEGRAM_CHAT_ID`**입니다.

> 💡 **이 두 가지만 알면 끝입니다!**  
> 획득한 **`TELEGRAM_TOKEN`**과 **`TELEGRAM_CHAT_ID`**를 봇 설정에 넣어두기만 하면, 매달 장 마감 전 내 스마트폰으로 실시간 매수 신호 리포트가 자동으로 날아오게 됩니다.

---

#### 🛡️ [저자 팩트 보장] 실전 퀀트 봇에 완벽 내장된 5대 무결점 안전장치

저자가 Antigravity AI와 대화하며 구축한 K-듀얼모멘텀 파이썬 소스 코드에는 실전 자동매매 시 일어날 수 있는 예외 상황을 100% 차단하는 **5대 무결점 안전장치**가 이미 완벽하게 내장되어 있습니다.

1. **평일 증시 휴장일 자동 필터링:** 제헌절, 설날, 추석 등 평일 공휴일 가동 시 KIS API 주문 거부 에러를 미리 방지하고 실행을 자동 일시 중단합니다.
2. **다음 첫 영업일 자동 이월 연장:** 공휴일로 정기 가동일(17일)에 집행되지 못한 경우, 다음 주 첫 거래일(영업일)에 봇이 스스로 판정하여 미집행분을 100% 자동 집행합니다.
3. **실시간 가용 현금 캡(Cap) 추적:** 1차 종목 매수 후 남아있는 실시간 가용 예수금을 추적하여, 2차 매수 시 잔고 부족으로 주문이 튕기는 에러를 원천 차단합니다.
4. **텔레그램 4KB 자름(Truncate) 보호:** 긴 디버깅 로그 수신 시 텔레그램 API 4,000자 제한 오류(HTTP 400)를 방지하도록 메시지를 자동으로 안전 분할 발송합니다.
5. **KRX 전산망 실시간 종목 교차 검증:** 가짜 종목코드나 미상장 코드가 입력되는 환각(Hallucination) 현상을 차단하고 정식 상장 ETF만 매수합니다.

---"""

if target_sec34_start in text:
    text = text.replace(target_sec34_start, repl_sec34_text)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY APPLIED SECTION 3.4 TEXT-BASED TELEGRAM GUIDE & 5 SAFETY GUARDS!")
else:
    print("TARGET SECTION 3.4 HEADER NOT FOUND EXACTLY - CHECKING TEXT")
