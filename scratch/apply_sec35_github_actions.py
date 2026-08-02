import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_sec35_end = """### 3.5 수익률 시나리오 및 20년·30년 정밀 백테스팅 성과 분석"""

repl_sec35_github = """### 3.5 GitHub Actions 100% 무료 무인 서버리스 자동 배포 세팅

자동투자 봇을 가동할 때 독자분들이 가장 많이 걱정하시는 2가지 질문이 있습니다.  
**"매달 장 마감 시간에 맞춰 내 컴퓨터를 켜두어야 하나요?"**, **"AWS나 GCP 같은 서버 비용이 매달 나가나요?"**

저자가 구축한 **GitHub Actions 무인 자동 배포 시스템**은 이 질문에 100% "아니오"라고 명쾌하게 답해 드립니다.

---

#### 💡 [서버 비용 0원] GCP/AWS 대신 GitHub Actions가 초보자에게 최고인 3대 이유

1. **신용카드 등록 없는 평생 100% 무료:**  
   AWS나 GCP 클라우드는 신용카드를 등록해야 하고 유료 전환 위험이 있지만, GitHub Actions는 **공개 및 개인 저장소에 서버리스 가동 시간을 평생 무료로 제공**합니다.
2. **내 컴퓨터가 꺼져 있어도 24시간 무인 가동:**  
   스마트폰이나 내 컴퓨터를 꺼두어도 깃허브의 무인 서포터 서버가 매달 정해진 날짜에 알아서 깨어나 파이썬 봇을 돌립니다.
3. **git push 명령어 한 번으로 배포 완료:**  
   복잡한 서버 설정 없이, 코드 파일만 깃허브에 푸시해 두면 CI/CD 무인 자동화 파이프라인이 100% 알아서 작동합니다.

---

#### 🔐 [보안 팩트] GitHub Secrets에 등록하는 6대 필수 보안 키 가이드

내 한국투자증권 API 키와 텔레그램 토큰이 유출되지 않도록, 깃허브 저장소 메뉴(`Settings ➔ Secrets and variables ➔ Actions`)에서 등록하는 6대 보안 키 목록입니다.

| GitHub Secrets 키 이름 | 해당 보안 키의 역할 및 입력할 값 💡 |
| :--- | :--- |
| **`KIS_MOMENTUM_APP_KEY`** | KIS Open API 개발자 포털에서 발급받은 정식 앱키 (AppKey) |
| **`KIS_MOMENTUM_APP_SECRET`** | KIS Open API 개발자 포털에서 발급받은 비밀키 (AppSecret) |
| **`KIS_PENSION_CANO`** | 내 연금저축펀드 계좌번호 앞 8자리 (예: `63183004`) |
| **`KIS_STOCK_CANO`** | (필요 시) 내 개인주식 계좌번호 앞 8자리 |
| **`TELEGRAM_TOKEN`** | 텔레그램 BotFather에서 발급받은 HTTP API 토큰 값 |
| **`TELEGRAM_CHAT_ID`** | 텔레그램 userinfobot에서 확인한 내 개인 챗 ID 숫자 |

---

#### ⚙️ 무인 자동 실행 파일(`.github/workflows/rebalance.yml`) 3대 작동 원리

`rebalance.yml` 파일은 깃허브 무인 서버에게 일할 시간을 지시하는 자동 작업지시서입니다.

1. **Cron 스케줄 자동 깨어남 (`cron: '30 3 17-31 * *'`):**  
   매달 17일~31일 한국시간 낮 12:30 KST(장 마감 3시간 전 여유 시점)에 깃허브 무인 서버가 자동으로 깨어납니다.
2. **독립된 파이썬 실행 환경 자동 구축:**  
   깃허브 서버가 파이썬을 자동 설치하고, KIS API 및 텔레그램에 필요한 필수 라이브러리를 0.1초 만에 세팅합니다.
3. **K-듀얼모멘텀 봇 실행 & 텔레그램 리포트 전송:**  
   `kis_bot_multi.py`를 실행하여 1등 자산 판정, 매수 주문, 텔레그램 실시간 리포트 발송까지 마친 후 스스로 클린 종료됩니다.

---

### 3.6 수익률 시나리오 및 20년·30년 정밀 백테스팅 성과 분석"""

if target_sec35_end in text:
    text = text.replace(target_sec35_end, repl_sec35_github)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY APPLIED SECTION 3.5 GITHUB ACTIONS FREE SERVER GUIDE!")
else:
    print("TARGET SECTION 3.5 HEADER NOT FOUND EXACTLY - CHECKING TEXT")
