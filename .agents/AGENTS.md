# All Weather Bot Debugging and Deployment History

## 1. Issue: Connection Port & Timeout
- **Symptom:** GCP Cloud Functions triggered connection timeouts when calling the Korea Investment & Securities (KIS) API.
- **Root Cause:** A logic block that removed port `:9443` from the KIS Base URL (`https://openapi.koreainvestment.com:9443`) was present, causing requests to be routed incorrectly through port `443` which got blocked by GCP network security policies or firewall restrictions.
- **Resolution:** Removed the port-stripping logic to preserve the explicit `:9443` port configuration.

## 2. Issue: KIS Overseas Balance Query Parameter Errors
- **Symptom:** API calls to `TTTS3012R` (Overseas Balance) failed with error: `해외 잔고 조회 API 실패 (OPSQ2001): ERROR : INPUT_FIELD_NAME TR_CRCY_CD`.
- **Root Cause:** KIS API updated its parameters, requiring `TR_CRCY_CD` (set to `USD`) and context search condition flags to be explicitly passed in the query parameters.
- **Resolution:** Modified `get_account_balance_overseas()` in `all_weather_quant_bot.py` to include `TR_CRCY_CD="USD"`, `CTX_AREA_FK200=""`, and `CTX_AREA_NK200=""` parameters.
- **Follow-up:** Added `SLL_TYPE="00"` to `submit_order_overseas()` for `SELL` orders to align with similar KIS API mandatory parameters.

## 3. Issue: Missing Domestic Cash Inquirer Helper
- **Symptom:** NameError occurred during balance queries when trying to invoke `get_orderable_cash()`.
- **Root Cause:** The `get_orderable_cash(token)` domestic cash inquirer helper was referenced but not actually defined/implemented in the script.
- **Resolution:** Implemented `get_orderable_cash(token)` using KIS domestic stock API `TTTC8435R` / `VTTC8435R` (`inquire-psbl-order`) to return domestic cash limits for supporting integrated margins.

## 4. Issue: Serverless State and Concurrency
- **Symptom:** Global variable contamination and sys.argv modifications could lead to race conditions in stateless Cloud Functions (Gen 2 concurrent execution).
- **Resolution:** Updated `gcp_deploy_all_weather.sh` to generate a `main.py` wrapper that runs the bot under isolation using `importlib.reload(all_weather_quant_bot)` and mock patches (`unittest.mock.patch.object(sys, 'argv', mock_argv)`).

## 5. Issue: OpenAPI Account Enrollment (`INVALID_CHECK_ACNO`)
- **Symptom:** Balance inquiry failed with: `해외 잔고 조회 API 실패 (OPSQ2000): ERROR : INPUT INVALID_CHECK_ACNO`.
- **Root Cause:** The newly created sub-account `72394127` was not enrolled in the OpenAPI service list under KIS, making it invalid for use with the AppKey.
- **Resolution:** Added the account to the OpenAPI enrollment list and updated the workspace configuration `.env` and GCP Cloud Run environment variables with the newly generated KIS AppKey and AppSecret.

## 6. 진해고등학교 현수막 규격 (Banner Sizes)
- **강당 현수막:** `9m * 0.6m` (가로 9미터, 세로 0.6미터)
- **본관 벽면 현수막:** `1.5m * 10m` (세로형 - 가로 1.5미터, 세로 10미터)
- **정문 게시대 현수막:** `5m * 0.9m` (가로 5미터, 세로 0.9미터)
- **설명:** 진해고등학교 내 주요 위치별 현수막 표준 규격 정보입니다. 관련 작업 시 이 규격을 참조하십시오.

## 7. 글로컬 학우상 시상 및 장학금 지급 공문 규칙
- **규칙:** '글로컬 학우상 시상 및 장학금 지급' 관련 공문을 작성하거나 관련 안내를 처리할 때, 장학금을 **'상품권'**으로 지급한다는 내용을 반드시 포함해야 합니다.
- **설명:** 이전 공문들에는 이 내용이 누락되어 있었으나, 향후 관련 공문 작성 및 상담 시 이 지급 방식을 명시하여 진행하도록 합니다.

## 8. 2026학년도 자율교육과정 탐구보고서 미제출 사유
- **A반 30213 박건:** 현장체험학습으로 결석함
- **A반 30420 이승우:** 결석함
- **B반 30316 문상현:** 도움반으로 활동 안함
- **B반 30908 김재형:** 결석함
- **설명:** 3학년 자율적 교육과정 쉬었음 청년 탐구보고서 미제출자 4명의 공식 결석 및 제외 사유입니다. 향후 나이스 입력 또는 출결 처리 시 참고하십시오.

## 9. 진해고등학교 입학 상담 챗봇 v2.0 배포 및 지식 베이스 관리 규칙
- **설명:** 진해고등학교 입학 상담 챗봇 v2.0(jinhae-bot2) 소스 코드 및 지식 베이스 파일 관리와 배포를 위한 규칙입니다.
- **챗봇 소스 및 DB 위치:**
  * 챗봇의 핵심 로직과 지식 베이스는 로컬 `jinhae-bot/jinhae-bot-main` 폴더에 위치합니다.
  * 지식 베이스 파일: `jinhae-bot/jinhae-bot-main/api/knowledge.txt`
- **배포 및 연동 규칙:**
  * Vercel 라이브 배포(`https://jinhae-bot2.vercel.app`)는 별도의 깃허브 저장소인 `https://github.com/hyh54311-dev/jinhae-bot2.git`와 연동되어 있습니다. (루트 저장소인 `jinhae-admission-system`과 연동되어 있지 않으므로 루트에서 푸시하면 배포되지 않습니다.)
  * 따라서 챗봇의 코드 또는 지식 베이스(`knowledge.txt`)를 수정한 뒤 라이브에 반영하려면 반드시 `jinhae-bot/jinhae-bot-main` 경로에서 로컬 git 저장소를 사용하여 `hyh54311-dev/jinhae-bot2.git`로 푸시해야 합니다.
- **지식 베이스 작성 규칙:**
  * 중학교별 신입생 분포 통계를 최신화하거나 추가할 때는 사용자가 대화방에서 축약어로 질문해도 100% 매칭할 수 있도록 중학교 명칭 옆에 괄호로 축약어 별칭을 명시해야 합니다. (예: `진해냉천중학교 (냉천중): 53명`, `진해남중학교 (진해남중): 51명` 등)

