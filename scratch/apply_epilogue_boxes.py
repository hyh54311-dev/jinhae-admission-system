import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_epilogue_end = """**- 저자 황요한 올림**"""

repl_epilogue_with_boxes = """**- 저자 황요한 올림**

---

### 🛡️ [특집 부록] 교사·공무원·직장인 독자를 위한 개인정보 보호 4대 수칙 & 7대 무상 Open API 자원 가이드

독자 여러분께서 본서의 퀀트 봇 제작을 넘어, 본업에서의 업무 자동화와 AI 에이전트 활용으로 사고를 확장하실 때 반드시 지켜야 할 **보안 수칙**과 **100% 무상 Open API 자원 모음**입니다.

---

#### 🔒 [필독 안전 수칙] AI 업무 자동화 시 개인정보 보호 4대 수칙

| 번호 | 핵심 개인정보 보호 수칙 | 구체적 현장 실천 가이드 💡 |
| :---: | :--- | :--- |
| **1** | **학생 및 민원인 이름 익명화 (Anonymization)** | AI 대화창에 학생 실명, 주민번호, 전화번호를 절대 직접 입력하지 않고 `학생 A`, `민원인 B` 형태의 식별 코드로 치환하여 사용합니다. |
| **2** | **대화 데이터 AI 학습 제외 설정 (Opt-out)** | Antigravity, ChatGPT, Claude 등 AI 서비스 설정 메뉴에서 `Model Training / Data Sharing` 옵션을 **`OFF(비활성화)`**로 설정하여 데이터 재학습을 차단합니다. |
| **3** | **API 키 및 계좌 보안 암호화 (GitHub Secrets)** | 한국투자증권 API 키, 텔레그램 토큰 등 민감한 키는 소스 코드에 하드코딩하지 않고, 반드시 깃허브 **`Secrets`** 보안 영역에 암호화 저장합니다. |
| **4** | **결재된 정식 공공 API 플랫폼만 연동 (Authorized APIs)** | 출처가 불분명한 외부 3사 웹사이트 대신, 정부 및 공식 기관에서 승인한 정식 Open API 서비스만 연동하여 개인정보 유출 리스크를 0%로 유지합니다. |

---

#### 🌐 [알짜 활용 자원] 교사·공무원이 100% 무상으로 활용 가능한 7대 Open API 모음집

| 자원명 | 주요 구체적 제공 서비스 | 교사·공무원·직장인 추천 활용 분야 💡 |
| :--- | :--- | :--- |
| **1. 한국투자증권 Open API** | 국내/해외 주식·ETF 실시간 시세, 계좌 잔고, 주식 자동 주문 | 본서의 메인 퀀트 자동매매 봇 및 자산 관리 자동화 |
| **2. 텔레그램 Bot API** | 실시간 텍스트/이미지 메신저 무료 발송, 그룹 알림 | 정기 매매 결과 수신, 학급/업무 긴급 알림 무인 발송 |
| **3. 커리어넷 Open API** | 전국 대학 학과 정보, 직업 진로 정보, 적성검사 데이터 | 진로 진학 상담 챗봇(`jinhae-bot2`), 학생 맞춤형 진로 지도 |
| **4. NEIS Open API** | 전국 초·중·고 학사일정, 오늘의 급식 식단, 학교 기본 정보 | 학급 스마트 학사일정 대시보드, 학교 홈페이지 자동 연동 |
| **5. 공공데이터포털 (data.go.kr)** | 전국 지자체 공공데이터, 법령, 날씨, 통계, 교통 데이터 | 행정 업무 자동화, 수업 연구 데이터 분석 웹앱 개발 |
| **6. 한국은행 ECOS Open API** | 기준금리, 환율, 주요 경제 통계, 통화량 시계열 데이터 | 퀀트 거시경제(Macro) 조건 분석, 거시 경제 수업 자료 |
| **7. 깃허브 Actions (CI/CD)** | 월 2,000분 서버리스 무료 무인 실행 스케줄러 환경 | 24시간 내 컴퓨터 켜두지 않는 무인 퀀트 봇 & 자동화 배포 |

---"""

if target_epilogue_end in text:
    text = text.replace(target_epilogue_end, repl_epilogue_with_boxes)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY APPLIED EPILOGUE PRIVACY & OPEN API GUIDES TO MANUSCRIPT!")
else:
    print("TARGET EPILOGUE END TEXT NOT FOUND EXACTLY - CHECKING TEXT")
