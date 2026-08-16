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

## 10. 생활기록부 세특 기재 금지 및 명칭 치환 규칙
- **지역명 및 특정 지명:** '진해' 등 특정 지역명, 구체적 지명은 **'우리 지역'**으로 변경.
- **기업명 및 특정 기관명:** 특정 기업명/브랜드명/기관명은 '관련 기업', '주요 기업', '관련 기관' 등으로 일반화하여 작성.
- **학교 식별 정보 및 고유 명칭:** '장복', '장복제' 등 학교 식별 가능 고유 명칭은 **'축제'**, **'교내 행사'**로 변경.
- **대회 관련 표현 금지:** '대회' 단어 절대 금지 → **'활동'**, **'프로그램'**, **'탐구'** 등으로 변경.

## 11. 1학기 생활기록부 세특 기재 지침 및 유의사항 (공식 안내)
- **작성 시한 및 용량:** 1학기 세특은 개학 이전 작성을 원칙으로 함. 1학년 공통과목은 1500바이트를 한 학기에 모두 쓰지 않고 1, 2학기 나눠서 작성.
- **기재 금지 사항:** 공인어학시험, 모의고사 성적, 논문 발표 사실, 도서 출간 사실(ISBN 미부여 학급문고는 가능), 장학생/장학금, 자격증, 특정 대학명, 사기업 상호명/기관명(삼성전자, UN, 유네스코, 유튜브 등), 강사명(직접 들은 수업 강사 제외), 재학 고등학교 알 수 있는 정보.
- **기재 가능 사항:** 
  * 교육관련기관 기관명(학교장 결재 후 참여한 행사 한정).
  * 랜드마크, 지역명(경남, 영남루 등), 유적지명, 관광지명, 프로그램명(파이썬 등), 63빌딩 등.
  * 도서 제목 및 저자명은 영문/기관명 제한 없이 있는 그대로 표기 가능 (예: '기적의 서울대 쌍둥이 공부법(여호원 외 1명)', 'EBS 다큐 프라임 자본주의(EBS 자본주의 제작팀)').
- **언어 표기:** 비전공자도 알 수 있는 널리 쓰이는 용어(SNS, AI, PPT 등) 외에는 가급적 한글로 기재.

## 12. 1학기 국어 교과부장 세특 공통 문구 및 대상 학생 목록
- **공통 삽입 문구:** `국어 교과부장으로서 수업이 원활하게 진행되도록 돕고, 급우들의 참여를 유도하며 협력적인 학습 분위기를 이끎.` (약 143 Bytes)
- **대상 학생 목록:**
  * 1반 정은준
  * 2반 박준제
  * 3반 박지호
  * 4반 유지훈
  * 5반 신근찬
  * 6반 정지운
  * 7반 이시형
  * 8반 한현욱
  * 9반 김태준
  * 10반 정원호
- **비고:** 해당 10명 학생의 문학 세특을 작성할 때 위 공통 문구의 용량(바이트)을 사전에 차감/고려하여 전체 세특이 500자(NEIS 바이트 기준)를 초과하지 않도록 안배함.

## 13. K-듀얼 모멘텀 봇 공휴일/휴장일 이월 미비 트러블슈팅 및 배포 이력 (2026-07-20)
- **증상:** 2026년 7월 20일(월) 리밸런싱 알림 미수신 및 봇 자동 가동 중단.
- **원인 분석:**
  1. 2026년 7월 17일(금)은 복원된 법정 공휴일(제헌절)로 **KRX 증시 휴장일**이었음. 17일 트리거 시 KIS API 현재가 조회(0원) 및 주문 통신 에러(`IGW00014: 주문 금액을 확인해주세요`)로 리밸런싱 실패.
  2. Cloud Scheduler는 매일 15:15에 정상 트리거되었으나, `kis_bot_multi.py` 날짜 비교 로직이 단순 `today == actual_rebalance_date` 형태로 되어 있어 18일~20일 실행 시 "오늘은 17일이 아님"으로 간주하고 즉시 중단(Exit)됨. (미집행 시 다음 첫 영업일로 자동 이월되는 처리 미비)
- **해결 방안 및 반영 코드:**
  1. `get_actual_rebalance_date()` 함수에서 매월 17일 기준 공휴일(2026 제헌절 포함) 및 주말(토/일)일 경우 다음 첫 영업일(Trading Day)로 예정일을 자동 이월(+1일씩 연장)하도록 검증.
  2. 7월 17일 미집행분 처리를 위해 **2026년 7월 21일(화)** 일회성 예외 강제 가동 로직(`is_special_july_21 = (today == datetime.date(2026, 7, 21))`)을 `kis_bot_multi.py`에 추가.
  3. 로컬 `kis_bot_multi.py` 수정 완료 후 GCP Cloud Run (`k-momentum-rebalancer`) 서비스 세부정보 소스 탭에 성공적으로 재배포(빌드/버전 생성 완료)함.

## 14. GCP 서버리스 수동 배포 괴리 해결 및 주간 이월 예외 확장 (2026-07-22)
- **증상:** 2026년 7월 21일(화) 15시 15분 스케줄러 트리거 시 "오늘은 실전 리밸런싱 실행일이 아닙니다 (예정일: 2026-07-17)" 로그가 출력되며 리밸런싱 미집행.
- **원인 분석:**
  1. GCP Cloud Run 실행 로그 분석 결과, 서버에서 구 버전 코드(`krx_holidays`에 `2026-07-17` 미포함 및 `is_special_july` 미적용)가 호출되고 있었음.
  2. 로컬 프로젝트 저장소(`jinhae-admission-system`)가 GCP Cloud Run 자동 빌드 트리거(Auto-Deploy)와 연동되어 있지 않아, `git push`만으로는 GCP 라이브 펑션 코드가 변경되지 않는 구조적 이유 때문이었음.
- **해결 방안 및 최종 배포:**
  1. `kis_bot_multi.py` 내 일회성 예외 실행 조건을 `is_special_july = (datetime.date(2026, 7, 21) <= today <= datetime.date(2026, 7, 25))`로 수정하여 7월 22일(수)~25일 기간 중 가동 시 7월 미집행분이 정상 집행되도록 확장.
  2. 최신 전체 소스 코드를 GCP Cloud Run 콘솔 소스 탭에 수동으로 덮어쓴 뒤 [배포 (DEPLOY)]를 실행하여 오전 06:44 자로 최신 라이브 버전 반영 완료함.

## 15. Cloud Run 버전(Revision) 이력 기반 퀀트 봇 디버깅 패턴 분류 (2026-07-23)
- **개요:** GCP Cloud Run 콘솔의 배포 리비전 이력(`00001`~`00020-v46`)을 분석하여 퀀트 자동매매 개발/운용 시 발생하는 오류 유형과 진화 과정을 4가지 핵심 집필 목차로 체계화함.
- **4대 커리큘럼 아키텍처:**
  1. **네트워크/인프라 (Rev 01~05):** 서버리스 파이프라인 형성, KIS 포트 `:9443` 유지 및 IP 차단 회피 백오프.
  2. **API/계좌 파라미터 (Rev 06~10):** KIS 잔고/주문 TR_ID(`TTTC8434R`, `TTTC8908R`) 매핑 및 예수금 교차 검증.
  3. **데이터/티커 검증 (Rev 11~15):** 가짜 종목코드(`304580`) 환각 분석 및 KRX 공시 데이터 기준 실시간 교차 검증.
  4. **날짜/이월/CI-CD (Rev 16~20):** 제헌절 증시 휴장일 이월 알고리즘, 주간 예외 범위 확장, GCP 수동 배포 괴리 해결.

## 16. 올웨더 자산배분 봇 스케줄 개편 (매달 25일 적립 / 1월 2일 연간 리밸런싱) (2026-07-23)
- **개편 배경:** 기존 매일 밤 가동되던 방식을 효율화하여 **매달 1회 (25일 기준)** 적립식 매수를 집행하도록 변경.
- **날짜 이월 알고리즘 적용:**
  1. **월별 가동일 (`get_actual_monthly_run_date`):** 매달 25일을 기본 가동일로 하되, 25일이 주말(토/일)이거나 증시 공휴일인 경우 **다음 첫 영업일(Trading Day)**로 자동 이월.
  2. **연간 정기 리밸런싱일 (`get_actual_annual_rebalance_date`):** 매년 1월 2일을 기본 리밸런싱일로 하되, 주말/공휴일 시 **다음 첫 영업일**로 자동 이월.
  3. **클라우드 스케줄러:** 매달 25일~31일 밤 23:00 KST(`0 23 25-31 * *`) 트리거 후 내부 Python 실행 게이트로 판정하여 집행.

## 17. 안전자산 종목코드 환각(`304580`) 규명 및 KRX 공식 데이터 교차 검증 (2026-07-23)
- **증상:** K-듀얼모멘텀 매매 시 주문 거부 또는 유효하지 않은 종목코드 에러 발생.
- **원인 분석:**
  1. 초기 스크립트 작성 시 안전자산(`TICKER_SAFE`) 종목코드로 미상장 무효 코드인 `304580`이 잘못 입력되어 있었음.
  2. 표기 명칭은 `KODEX 미국달러단기채권`으로 되어 있었으나, 실제 해당 자산군의 정식 상장 ETF는 `TIGER 미국달러단기채권액티브`(`329750`)였음.
- **해결 방안 및 최종 반영:**
  1. 한국거래소(KRX) 상장 공시 전산망 및 각 자산운용사(삼성 KODEX, 미래에셋 TIGER, 한투 ACE) 데이터베이스를 바탕으로 5대 ETF 티커 전수 실시간 교차 검증 수행.
  2. `TICKER_SAFE` 종목코드를 KRX 정식 상장 코드인 **`329750` (`TIGER 미국달러단기채권액티브`)**로 완벽히 교체 및 소스 싱크 동기화 완료.

## 18. KIS API 매수가능조회 파라미터 오기(`CMA_EVLU_AMT_ICLD_YN`) 및 전일 결제 미정산 예수금 초과 에러 해결 (2026-07-23)
- **증상:** 2026년 7월 23일 15:15 정기 리밸런싱 중 1차 종목(`069500`) 1주 매수 성공 후, 2차 종목(`329750`) 34주 매수 시 "주문가능금액을 초과 했습니다" 오류로 매수 실패.
- **원인 분석:**
  1. `get_orderable_cash()` (TR_ID: `TTTC8908R`) 파라미터 중 `CMA_EVLU_AMT_IF_YN`으로 오기되어 있어 KIS API 통신 실패 (`OPSQ2001: ERROR : INPUT_FIELD_NAME CMA_EVLU_AMT_ICLD_YN`).
  2. 매수가능조회 API 실패로 잔고조회(`TTTC8434R`)의 D+2 예수금(`dnca_tot_amt`: 627,902원)이 그대로 예수금으로 산정됨.
  3. 그러나 전일 매수 결제 미정산금(`bfdy_buy_amt`: 108,965원)이 D+2 예수금에서 차감되지 않아, 실제 당일 매수 가능금액(518,933원)보다 큰 금액(582,640원)으로 주문 수량이 산정되는 문제 발생.
- **해결 방안 및 반영 코드:**
  1. `TTTC8908R` 파라미터 명칭을 `CMA_EVLU_AMT_ICLD_YN`으로 교정하여 매수가능금액 조회가 에러 없이 정확한 실시간 주문가능현금을 반환하도록 수정.
  2. `get_account_balance()`의 예수금 fallback 우선순위에 `prvs_rcdl_excc_amt` 및 `nxdy_excc_amt`를 추가하여 API 교차검증 실패 시에도 미정산 차감액을 안전 반영.
  3. `rebalance_account()` 매수 주문 루프 내에서 매 주문 직전 남은 가용 예수금을 실시간 차감 추적하고, 필요 시 수량을 안전 범위 내로 자동 조절하는 동적 캡(Cap) 로직 추가.

## 19. 퀀트 봇 5대 잠재 예외(Edge Cases) 허점 차단 및 최종 안전 아키텍처 수립 (2026-07-23)
  3. **[예수금 0원 최우선 인정]** `ord_psbl_cash`가 0원 반환 시 `val > 0` 조건으로 스킵하지 않고 0원 인정 ➔ D+2 예수금 오인에 따른 과다 주문 방지.
  4. **[동적 실시간 잔여 현금 캡]** 매 주문 성공 시 `current_avail_cash -= amount` 실시간 차감 ➔ 1차 매수 후 남아있는 현금 범위 내로 2차 매수 수량 동적 자동 조율.
  5. **[텔레그램 4KB 트렁케이트]** `len(full_msg) > 4000` 트렁케이트 ➔ 긴 잔고 디버깅 로그 수신 시 텔레그램 HTTP 400 API 실패 예방.

## 22. 황요한 저자 실화 기반 퀀트 자산배분 도서 원고 집필 및 에듀테크 연계 체계 수립 (2026-07-25)
- **개요:** 현직 경남 고등학교 교사 황요한 저자의 실전 경험과 에듀테크 웹앱 연계 서사를 담은 정식 종이책(ISBN 등록) 원고 (`retirement_savings_dual_momentum_guide.md`) 완성.
- **핵심 서사 및 기술 구성:**
  1. **실제 손실 실화:** 2026년 4월 21일 바이오주 51주(8,098만 원) 매수(생물보안법, 4/5/6공장, 제미나이 딥리서치 수행) ➔ 삼성전자 급등장 속 6월 8일 전량 매도(-1,734만 원 손실, -21.4%) ➔ 상대적 박탈감 및 수업/22개월 아기 육아의 고통 ➔ 과거 인베스팅닷컴 엑셀 수동 퀀트 한계 극복 ➔ 2025년 말 육아휴직 중 Google Antigravity 접함 ➔ 2026년 6월 파이썬 봇 완성(감정/노동 0).
  2. **실제 교직 에듀테크 웹앱 결실 (1.4~1.5절):**
     - 진해고 입학 상담 AI 챗봇 v2.0 (`jinhae-bot2.vercel.app`)
     - 교수-평가-기록(교수평기) 및 세특 자동화 웹앱 (`script.google.com`)
     - 리로스쿨 (`jinhaeh.riroschool.kr`) & 경남 EVPN (`evpn.gne.go.kr`) 학사 서포터
     - 나이스(NEIS) Open API, 커리어넷 API 연동 및 교사 사고 확장 프레임워크.
  3. **초보 교사 눈높이 퀀트 심화 (3.1~3.2절):** 성적 루브릭 평가 비유, 5대 퀀트 전략(밸류, 퀄리티, 모멘텀, 마법공식/소형주, 동적자산배분 VAA/DAA), 4대 지표(CAGR, MDD, 샤프지수, 리밸런싱).
  4. **텔레그램 실시간 알림 엔진 & GCP 무료 배포 스케줄러:** 매달 17~25일 15시 15분 KST 자동 트리거 및 7월 27일(월) 가동 준비 마감.

## 23. 원고 Section 1.3, 1.4, 1.5 서사 완벽 개편 및 깃허브 실시간 푸시 동기화 마감 (2026-07-28)
- **개요:** 저자 실화(육아휴직, 주식/부동산/경매 독서, 소크라틱 AI 튜터 개발, NFC/음성 에듀테크, 7대 Open API, 개인정보 4대 수칙) 반영 및 1부 전체(1.1~1.5절) 완벽 개편.
- **주요 수정 반영 사항:**
  1. **1.3절:** 인베스팅닷컴 엑셀 수식 오기 피로 ➔ 퀀트 삼중고(손의 피로, 귀찮음, 마음의 고통) ➔ 2025년 11월 육아휴직 밤샘 제미나이/GAS 시작 ➔ Antigravity Vibe Coding으로 2026년 3월 봇 구축 ➔ GitHub Actions 무인 서버 전환 청사진 (`e23dcee`).
  2. **1.4절:** 교직 발령 후 재테크 독서 서사 ➔ 수업 준비/실행 자동화 필연성 ➔ 리로스쿨/EVPN 오기 삭제 ➔ 저자 직접 구축 소크라틱 AI 튜터 웹앱 2종 (3학년 자율교육과정 탐구 기록 & 2학년 2학기 문법 수업 맞춤형 챗봇) 수록 (`cccee04`).
  3. **1.5절:** 복직 후 3대 수업 자동화(NFC/QR 스마트 출석부 & 교과진도, 음성 기반 학생평가 & 진도기록) ➔ Agentic AI 시대 교사의 아이디어/사고 확장 철학 ➔ 교사·공무원 7대 무상 Open API 자원 수록 ➔ 학생·교사 개인정보 보호 4대 수칙 수록 (`5ad076d`).

## 23. GCP 퀀트 봇 ➔ GitHub Actions 100% 무료 자동화 및 CI/CD 전환 예정 (매일 아침 브리핑 필수 상기 규칙) (2026-07-27)
- **개요:** 기존 GCP Cloud Functions/Cloud Run 기반 스케줄러 및 수동 배포 체계를 **GitHub Actions (100% 무료 Cron 스케줄러 & git push 자동 배포 파이프라인)** 체계로 이전할 예정임.
- **아침 브리핑 규칙:** 매일 아침 일정/안내 브리핑을 드릴 때마다 **'GCP 퀀트 봇의 GitHub Actions 100% 무료 스케줄러 및 자동 배포 전환 작업'**을 필수 상기 항목으로 포함하여 함께 안내할 것.

## 24. 퀀트 봇 2종 GitHub Actions 100% 무료 무인 서버 이그레이션 및 실전 검증 완료 (2026-07-27)
- **개요:** GCP Cloud Run/Cloud Scheduler ➔ **GitHub Actions (100% 무료 서버리스 무인 스케줄러)** 이전을 완벽히 마감하고 텔레그램 실전 가동 테스트 완료.
- **저장소 및 계좌 정보 체계**:
  1. **K-듀얼 모멘텀 봇**:
     - **GitHub 저장소:** `https://github.com/hyh54311-dev/jinhae-k-momentum-bot`
     - **스케줄:** 매달 17일~31일 한국시간 12:30 KST (`cron: '30 3 17-31 * *'`) (장 마감 3시간 전 여유 실행)
     - **연동 계좌:** 연금저축펀드계좌 (`CANO: 63183004`, `prdt_cd: 22`) & 개인주식계좌 (`CANO: 63183004`, `prdt_cd: 01`)
     - **안전자산 교체 코드:** `329750` (`TIGER 미국달러단기채권액티브`)
     - **GitHub Secrets (6개):** `KIS_MOMENTUM_APP_KEY`, `KIS_MOMENTUM_APP_SECRET`, `KIS_PENSION_CANO` (`63183004`), `KIS_STOCK_CANO` (`63183004`), `TELEGRAM_TOKEN` (`8407908239:AAHO81Ld-mmtJ-V5opl5vXI3bXgICiDrNgc`), `TELEGRAM_CHAT_ID` (`8518409134`)
  2. **올웨더 자산배분 봇**:
     - **GitHub 저장소:** `https://github.com/hyh54311-dev/jinhae-all-weather-bot`
     - **스케줄:** 매달 25일~31일 한국시간 23:00 KST (`cron: '0 14 25-31 * *'`)
     - **연동 계좌:** 올웨더 전용 해외주식 서브계좌 (`CANO: 72394127`, `prdt_cd: 01`)
     - **포트폴리오 비중:** VOO 30%, TLT 40%, IEF 15%, GLD 7.5%, PDBC 7.5%
     - **GitHub Secrets (5개):** `KIS_APP_KEY`, `KIS_APP_SECRET`, `KIS_ALL_WEATHER_CANO` (`72394127`), `TELEGRAM_TOKEN` (`8407908239:AAHO81Ld-mmtJ-V5opl5vXI3bXgICiDrNgc`), `TELEGRAM_CHAT_ID` (`8518409134`)
- **GCP 인프라 조치 상태**:
  - GCP Cloud Scheduler (`k-momentum-rebalance-schedule`, `all-weather-daily-job`) **Paused (일시 중지 완료)**. 중복 매매 위험 0%.

## 25. 경남대 마이크로디그리 6~7일차 연수 자료 수집 & 교과서 화면공유 ClassCast 분석 & 소시오그램 관계망 시각화 웹앱 구축 (2026-08-05)
- **개요:** 경남대 마이크로디그리 연수 6일차(김재현 강사) 패들렛(`joo.is/경남대803`)과 7일차(이상우 강사) 퀴즈앤(`quizn.show/pbd/info/board/1127454`) 전체 자료를 구글 드라이브(`2026. 지역 대학 연계 마이크로디그리형 연수 계획`) 폴더에 100% 저장 및 정리하고, 교과서 화면 공유 프로그램 `ClassCast.exe` 역분석 및 학급 소시오그램 관계망 시각화 웹앱(`jinhae_sociogram_app`) 단독 구축 완료.
- **주요 저장 및 분석 결과**:
  1. **구글 드라이브 6일차/7일차 폴더 동기화**:
     - 6일차 폴더 (`1gnU5vQwpTOtYgGPoKFcqAg6vhZY9tZp1`): 1부 생기부 연수, 2부 학급경영 A to Z, 3부 NotebookLM & Google AI Studio 바이브코딩 교안 PDF 및 정리본 10개 완필.
     - 7일차 폴더 (`1jt_mdwsSLs25272FzZUnTone_YBsbmF8`): 구글 워크스페이스 & Apps Script 교사 성적 대시보드 4회 시험 7개 과목 추이 그래프 바이브 코딩 프롬프트, 프레젠테이션 2종, ZoomIt 도구 수록.
  2. **ClassCast.exe 교과서 화면 공유 역분석**:
     - Electron + PDF.js(Scale 2.0 고화질 렌더링) + 트리플 레이어 Canvas (`pdfCanvas`, `annotCanvas` 판서 분리, `previewCanvas` 돋보기) + WebSocket 룸(Room) 기반 1초 동기화 레퍼런스 소스 코드(`scratch/classcast_extracted_source/classcast_instructor_script_5.js`) 도출.
  3. **우리 반 소시오그램 관계망 시각화 웹앱 (`jinhae_sociogram_app`) 독립 구축**:
     - 위치: `jinhae_sociogram_app` (`index.html`, `style.css`, `app.js`)
     - 기능: SheetJS 엑셀 파싱, Vis.js Physics Engine 관계망 렌더링, 1초 `[🎲 샘플 데이터 체험하기]`, 1초 익명화 토글, 5대 성격유형 컬러코딩 & 소외그룹 탐지, 양방향 지목 카드 팝업, 엑셀 샘플 다운로드 및 PNG 이미지 저장 지원.

## 26. 경남대 마이크로디그리 연수 6대 바이브 코딩 예제 마스터 청사진 & 커스텀 개발 가이드 보존 (2026-08-05)
- **개요:** 마이크로디그리 연수(6일차 김재현, 7일차 이상우 강사)에서 전수된 6가지 핵심 바이브코딩(Vibe Coding) 예제 프로젝트의 기술 구조, 소스 위치, 프롬프트 및 커스텀 구축 가이드를 완벽 정리 및 영구 보존함.
- **6대 바이브 코딩 마스터 청사진**:
  1. **ClassCast (교과서 화면 공유 & 판서 웹앱)**: Electron + PDF.js + 트리플 Canvas + WebSocket 동기화 (`scratch/classcast_extracted_source/classcast_instructor_script_5.js`).
  2. **우리 반 소시오그램 시각화 (Sociogram Network)**: SheetJS + Vis.js Physics Engine + 5대 성격유형 컬러코딩 & 소외그룹 탐지 (`jinhae_sociogram_app/index.html`).
  3. **교사용 360° 학생 성적 대시보드 (Grade Dashboard)**: 28명 4회 시험 7개 과목 꺾은선 추이 그래프 + 석차 시각화 바이브코딩 프롬프트 (7일차 마크다운 정리본 수록).
  4. **세이프버디 (SafeBuddy)**: GAS 백엔드 + HTML5 모바일 알림 학생 안전 & 카카오톡 케어 웹앱 (`세이프버디_GAS_웹앱_소스코드.txt`).
  5. **Google AI Studio & NotebookLM 바이브코딩 튜토리얼**: AI Studio `[Get Code]` 1초 Apps Script 변환 및 라이브 배포 교안 (`00_3부_노트북LM과바이브코딩_정리.md`).
  6. **AI 프렌즈 학급 경영 아이디어 발산 보드**: 학생 페르소나 프로필 및 문제 상황 해결 마인드맵 웹앱 (`AI프렌즈_아이디어발산보드.html`).

## 27. 범용 소크라틱 AI 챗봇 엔진 v3.2 (State-Hardened + Care-Aware) 표준 규칙 (2026-08-15)
- **개요:** 소크라틱 AI 챗봇이 탑재된 교육용 웹앱 개발 요청 시, `.agents/rules/socratic-ai-engine.md` 및 `.agents/skills/build_socratic_webapp.md`를 우선 참조하여 10대 핵심 아키텍처 규칙과 `references/backend_v32.js` 표준 백엔드를 100% 적용함.
- **10대 핵심 표준 아키텍처**:
  1. **위기 신호 3등급 분리 라우팅 (Care-Aware)**: 자살/자해 등 위기 신호는 비속어 필터에서 완전 분리. 잠금 없이 돌봄 응답 + 상담 창구 안내 + 교사 긴급 알림 + `유의신호_검토로그` 적재.
  2. **Stage 단조 증가 클램프**: `Math.min(4, Math.max(1, Math.max(prevStage, reportedStage)))`로 역행 원천 차단. 예외/차단 분기에서도 이전 Stage 완벽 유지.
  3. **RAG 수치 토큰 동적 추출**: 시트에서 수치·단위를 정규식으로 자동 추출(`extractFactTokens`). 하드코딩 제거로 과목 전환 100% 호환.
  4. **citedStats 서버 누적 & 1회 재생성**: 모델 자기보고를 텍스트 스캔으로 교차 검증. 재인용 감지 시 강화 지시로 1회만 재생성.
  5. **구조화된 JSON 스키마**: `responseSchema`로 `{ stage, citedStats, isHintMode, feedback }` 출력 강제.
  6. **장기 대화 컨텍스트 압축**: 12턴 초과 시 3항목(도달 결론, 다룬 논점, 미답변 지점) 요약 브리핑 생성 및 최근 6턴 원문 유지.
  7. **비속어 연속 카운터 & 영속 잠금 플래그**: 학생 발화(role: user)만 검사. 연속 2회 시 잠금 + 교사 1회성 알림 + 스프레드시트 잠금 해제 UI 제공.
  8. **대시보드 보안 인증 & 토큰 분리**: `Session.getActiveUser().getEmail()` 화이트리스트 검사 + 별도 배포 또는 접근 토큰(`?view=teacher&key=`) 병행.
  9. **드라이브 공유 범위 제한**: `DOMAIN_WITH_LINK`로 학교 도메인 내 제한 (개인 계정은 `PRIVATE` 폴백).
  10. **회귀 테스트 하니스 (`references/eval_harness.js`)**: 9대 assertion(`no_repeat_stat`, `no_stage_regression`, `must_hint`, `must_care` 등)으로 자동 검증.
- **규칙 및 참조 파일 위치**:
  * 규칙: `.agents/rules/socratic-ai-engine.md`
  * 스킬: `.agents/skills/build_socratic_webapp.md` & `.agents/skills/socratic-ai-engine/SKILL.md`
  * 참조 구현체: `references/backend_v32.js` & `references/eval_harness.js` & `references/migration_v31_to_v32.md`
  * 글로벌 스킬: `C:/Users/요한T/.gemini/config/skills/socratic-ai-engine/SKILL.md`

## 28. [해커톤 대상 목표] 소크라티스 X (Socratis X) 마스터 청사진 및 보완 마일스톤 관리 (2026-08-15)
- **개요:** 대한민국 교사 에듀테크 해커톤 & Google Gemini API Competition 대상(Grand Prize) 수상을 목표로 하는 소크라티스 X 프로젝트 청사진을 저장 및 관리함.
- **청사진 위치**: [`socratic_ai_hackathon_blueprint.md`](file:///G:/%EB%8B%A4%EB%A5%B8%20%EC%BB%B4%ED%93%A8%ED%84%B0/%EB%82%B4%20%EC%BB%B4%ED%93%A8%ED%84%B0/%EC%A7%84%ED%95%B4%EA%B3%A0%EB%93%B1%ED%95%99%EA%B5%90/2026%ED%95%99%EB%85%84%EB%8F%84/antigravity_folder/socratic_ai_hackathon_blueprint.md).
- **향후 4대 보완 마일스톤**:
  1. **Phase 1 (UX/UI)**: 카카오톡 스타일 2지선다 카톡 버블 카드 UI 반영.
  2. **Phase 2 (대시보드)**: 교사용 '학생 사고 발달 지수(Scaffolding Index)' Chart.js 관제 시각화.
  3. **Phase 3 (보이스 AI)**: Web Speech API & Gemini Audio 기반 음성 소크라틱 튜터 모드 확장.
  4. **Phase 4 (해커톤 패키징)**: Public Repo, GIF 데모, 아키텍처 다이어그램 및 해커톤 출품서 완성.


## 29. 진해고등학교 3학년 자율교육과정 세특 기재 및 정리 구글 시트 주소 (2026-08-06)
- **개요:** 진해고등학교 3학년 전체 학생의 세부능력 및 특기사항(세특)을 기재할 최종 입력 시트 및 자율교육과정 세특 내용 정리 원본 시트 정보입니다.
- **주요 시트 정보**:
  1. **진해고 3학년 전체 학생 개인별 세특 입력 시트**:
     - **URL**: [`https://docs.google.com/spreadsheets/d/14oBXe4HmjyUQqlzIxiB32Xi4jakCg-UBR5D3jAJXjmM/edit?gid=249965728#gid=249965728`](https://docs.google.com/spreadsheets/d/14oBXe4HmjyUQqlzIxiB32Xi4jakCg-UBR5D3jAJXjmM/edit?gid=249965728#gid=249965728)
     - **목적**: 3학년 전체 학생의 개인별 세부능력 및 특기사항을 기재하는 공식 입력 시트. 향후 자율교육과정과 관련하여 정리한 내용을 이 시트에 기재/작성함.
  2. **자율교육과정 세특 정리 원본 시트**:
     - **URL**: [`https://docs.google.com/spreadsheets/d/1ihk43OB4WwaBzWH67lsXHufQwiMq6AQJ93Ekzk3wByk/edit?gid=583407139#gid=583407139`](https://docs.google.com/spreadsheets/d/1ihk43OB4WwaBzWH67lsXHufQwiMq6AQJ93Ekzk3wByk/edit?gid=583407139#gid=583407139)
     - **목적**: 선생님께서 자율교육과정 세특 내용을 미리 작성 및 정돈해 두신 원본 시트.

## 30. 국가교육위원회·교육부 중장기 대입제도 개편안 (수능/내신 절대평가 & 서·논술형 도입 및 AI 채점 체계) 요약 (2026-08-07)
- **개요:** 국가교육위원회(국교위) 및 교육부 '2026년 하반기 업무계획' 보고 내용. 현행 획일적 객관식·상대평가 위주의 수능 및 내신 체제를 대대적으로 개편하는 중장기 대입제도 개편 방안에 착수함.
- **핵심 개편 방향**:
  1. **수능 및 고교 내신 전 과목 절대평가 전환 검토:** 줄세우기 과열 경쟁을 완화하고, 고교학점제 등 2022 개정 교육과정과의 정합성 확보.
  2. **서·논술형 문항 본격 도입:** 단순 오지선다 정답 고르기에서 벗어나 비판적 사고력과 창의적 문제 해결 능력을 평가하는 서·논술형 문제 도입 (시험시간 연장에 따른 수능 2일간 실시 방안 포함 검토).
  3. **대입전형 일정 조정:** 고교 3학년 2학기 수업 파행을 막고 교육과정을 정상화하기 위한 대입 일정 통합/조정 검토.
- **AI 기반 채점·모니터링 인프라 구축 (2029년까지)**:
  1. **AI 평가지원시스템 구축:** 전국 17개 시도교육청에 도입. 서·논술형 답안 110만 건 학습 데이터 수집 후 AI 가채점 및 맞춤형 피드백 제공.
  2. **AI 내신평가 모니터링 체계 가동:** 학교별 성취평가제(절대평가) 분석 소요 기간을 기존 3~4개월에서 시험 직후 즉시 분석 및 맞춤형 컨설팅으로 대폭 단축.
- **추진 일정 및 구글(Google Account) 일정/태스크 알림 연동 내역**:
  1. **2026년 10월 25일 오전 9:00:** 대입제도 개편 주요 추진과제 시안 공개 및 온·오프라인 공론화/공청회 착수 발표 확인 알림 ([등록 링크](https://www.google.com/calendar/event?eid=NDNzbzBhMTVwZXE0NnBnaW1wdmNhdTUzZHMgaHloNTQzMTFAbQ)).
  2. **2027년 3월 1일 오전 9:00:** 대국민 숙의 과정을 거친 중장기 대입제도 개편 최종 확정안 발표 확인 알림 ([등록 링크](https://www.google.com/calendar/event?eid=Y24zc2E1azh2ZW82Nmdvc2Ftdm84NnYwYmMgaHloNTQzMTFAbQ)).
  3. **적용 대상:** 2026년 기준 초등학교 6학년이 대학에 입학하는 2033학년도 대입(2030년 고교 진학)부터 적용 유력 논의 중.
  4. **비고:** 별도의 웹 브라우저 인증 승인 절차 없이, 기존 인증된 구글 계정(`hyh54311@gmail.com`) 연동을 통해 구글 캘린더 및 구글 태스크(Google Tasks) 패널에 등록 완료함 (오전 9시 팝업/이메일 자동 알림 발송).

## 27. Gemini 및 Upstage AI API 키 통합 관리 규칙
- **Gemini API Key #1 (기존 기본 키):** `AQ.Ab8RN6***************************************`
- **Gemini API Key #2 (교육용/수업설계 추천 키):** `AQ.Ab8RN6***************************************`
- **Upstage Solar API Key:** `up_9O**************************`
- **설명:** 사용자(황요한 저자)가 API 키 문의 시 즉각 응답할 수 있도록 영구 메모리에 기록함.

## 28. 교사 주도형 소크라틱 수업 설계 웹앱 v2.2 라이브 배포 URL
- **배포 주소**: `https://script.google.com/macros/s/AKfycbw2NfbOPJ8dBfjDAwdzhfMP1WyvP1Jh4nN7IKDU3VRrkNGNEAyS-dCKT59ZgO74I7sRJw/exec`
- **설명:** 구글 앱스 스크립트(GAS)를 통해 성공적으로 라이브 배포된 웹앱의 공식 실행 URL입니다.

## 31. 다문화·이중언어교육 핵심 패러다임(상호문화주의 & 트랜스랜구이징) 및 현장 국어 수업 적용 지침 (2026-08-10)
- **개요:** 용광로(동화주의) 및 샐러드볼(소극적 공존) 이론의 한계를 극복한 최근 다문화/이중언어교육의 핵심 패러다임과 교과 수업 적용 지침을 상기·보존함.
- **핵심 이론 체계**:
  1. **상호문화주의 (Interculturalism):** 단순한 문화 나열/병존(샐러드볼)을 넘어, 공통의 시민적 규범을 바탕으로 주체 간 능동적 소통과 역동적 통합 지향.
  2. **트랜스랜구이징 (Translanguaging):** 모국어(L1)를 억제 대상(용광로)이나 보존 대상(샐러드볼)에 멈추지 않고, 인지적·정서적 발판이자 고차원 사고를 돕는 언어적 자산(Linguistic Repertoire)으로 유연하게 활용.
- **교실 현장(국어과) 실행 전략**:
  1. **교사의 역할:** 모국어 전문가/정답 감수자가 아닌 '메타언어적 질문자' 및 퍼실리테이터 (학생의 모국어 지식을 자원으로 끌어냄).
  2. **교사의 피드백/평가:** 정답 판별이 아닌 국어과 학습 목표(비교, 비판, 표현, 논리성) 도달 과정 및 사고의 궤적 점검. 에듀테크/번역기/동료 교차 교정 활용.
  3. **한국어 미숙/초기 입국자 지원:** KSL 학급/보충 수업 병행, 실시간 AI 번역/시각자료 중심 텍스트 최소화, 트랜스랜구이징 모국어 과제 허용, 짝(Buddy) 제도 및 대체 평가 적용.
  4. **수준차 교실 개별화 (Tiered Instruction):** 동일 주제에 대한 과제 목표/난이도 3~4단계 층위화, 비언어적 모둠 역할 분담, 에듀테크 코스웨어 기반 비동기식 개인별 맞춤 학습.

## 32. 바이브코딩 기반 학교 수업용 웹앱 학운위/개인정보 규제 준수 & 구글 생태계(GAS+시트) 개발 배포 표준 규칙 (2026-08-10)
- **개요:** 바이브코딩(자연어 코딩)으로 제작한 교육용 웹앱을 학생과 수업에서 활용할 때 발생하는 행정적·법적 규제(학운위 심의, 개인정보 수집 및 국외 이전)를 완벽히 준수하고 우회하기 위한 개발 및 배포 표준 지침.
- **법적·행정적 분석 핵심 요약**:
  1. **저작도구 vs 결과물(앱) 분리:** Canva, VSCode, Lovable 등 저작도구 플랫폼 심의와, 이를 통해 교사가 제작해 학생에게 배포하는 2차 저작물(웹앱)의 심의는 별개임. 학생 데이터 수집/로그인이 포함되면 별도 심의 대상.
  2. **학습지원소프트웨어 지정 범위:** Lovable, VSCode, Vercel, AWS, GitHub 등 범용 개발 도구는 교사의 개인 업무용으로는 학운위 심의 대상이 아니지만, 학생 배포용 앱으로 전환되는 순간 에듀테크 규제망 적용.
  3. **국외 이전 및 학부모 동의 리스크:** Vercel, Supabase, Firebase, AWS 등 해외 서버 기반 제3자 서비스에 학생 데이터(이름, 학번, 과제, 세특 반응 등)가 저장되면 '개인정보 수집 동의' 및 '국외 이전 고지/동의' 필수.
- **학운위 심의 면제 & 100% 합법 수업 활용 구글 생태계 완전 독립 아키텍처 (GAS + 구글 시트/드라이브)**:
  * **법적 지위:** 학교에 도입된 Google Workspace for Education(Google 계정)은 사전 인가망임. 따라서 외부 제3자 서버(AWS, Vercel, Firebase 등)를 100% 차단하고 **구글 앱스 스크립트(GAS, script.google.com)** 기반 웹앱으로 제작하여 구글 시트/드라이브에 저장할 경우 **'구글 설문지(Google Forms)'를 커스텀하여 활용하는 것과 법적·행정적으로 완벽히 동일한 지위**를 가짐.
  * **필수 개발 및 배포 규칙**:
    1. **배포 권한 설정:** Web App 배포 시 `Execute as: Me (교사 계정)`, `Who has access: Anyone within [학교 도메인]` 설정 (학교 구글 계정 사용자만 접근).
    2. **학생 신원 자동 식별:** 웹앱 화면에 이름/학번 입력폼을 만들지 않고, GAS 백엔드에서 `Session.getActiveUser().getEmail()`을 사용하여 접속 학생의 이메일을 구글 시트에 자동 수집/기록.
    3. **독립 실행형 코드 구조:** HTML/JS/CSS 전체를 GAS 프로젝트 내부에 포함하여 외부 CDN 및 외부 JS 연동 차단.

## 33. 2학년 문학 세특 재작성 및 공통 문구 기재 엄격 규칙 (2026-08-10)
- **개요:** 2학년 문학 세특 전면 재작성 시 적용할 3대 영역별 작성 규칙 및 분량 규정.
- **상세 작성 지침**:
  1. **수행평가와 탐구보고서 모두 제출한 학생 (유형 A):**
     - 문학 수행평가 내용 50% 반영.
     - 문학 탐구보고서 내용 50% 반영.
     - **영역 분리 서술 필수:** 두 영역의 내용을 뒤섞지 말고, 수행평가 영역과 탐구보고서 영역을 명확히 구분하여 서술할 것.
     - **분량 엄수:** NEIS 바이트 기준 **1,400바이트 ~ 1,500바이트**로 작성.
     - **국어 교과부장 공통 문구 삽입:** 1반 정은준, 2반 박준제, 3반 박지호 등 1학기 국어 교과부장 10명 대상 학생은 다음 공통 문구를 반드시 포함할 것 (`국어 교과부장으로서 수업이 원활하게 진행되도록 돕고, 급우들의 참여를 유도하며 협력적인 학습 분위기를 이끎.`). 해당 문구 바이트(약 143B)를 감안하여 전체가 1,500B를 초과하지 않도록 안배.
  2. **수행평가와 탐구보고서 중 하나만 제출한 학생 (유형 B):**
     - 제출한 해당 영역의 내용을 100% 반영.
     - **분량 엄수:** NEIS 바이트 기준 **1,100바이트 ~ 1,200바이트**로 작성.
  3. **하나도 제출하지 않은 학생 (유형 C):**
     - 지정된 500바이트 이내 공통 문구 적용 (`문학 수업에 성실히 참여하여...`).

## 34. 8월 12일(수) 일과 운영 안내 (2026-08-11)
- **개요:** 2026년 8월 12일 수요일의 교내 일과 운영 스케줄표입니다.
- **상세 일정**:
  * **1교시:** 창체(교내청소) - 담임교사
  * **2~5교시:** 정상수업 - 교과교사
  * **6교시:** 1교시 수업을 운영 - 교과교사
  * **7교시:** 창체(학급자치) - 담임교사
