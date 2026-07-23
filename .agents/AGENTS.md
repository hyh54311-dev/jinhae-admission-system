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
- **개요:** 실전 자동매매 환경에서 발생 가능한 5가지 잠재 예외 상황(예수금 0원 오판, 휴장일 정규장 오판, 키 노출, 텔레그램 4KB 초과, 시장가 조회 단가 오기)을 분석하고 완벽 조치.
- **5대 안전 강화 조치:**
  1. **예수금 0원 판정 허점 차단:** `get_account_balance()`의 `val > 0` 스킵 로직 제거. `ord_psbl_cash`가 0원일 경우 0원 그대로 인정하여 D+2 예수금 오인 매수 차단.
  2. **휴장일 정규장 오판 방지:** `is_market_open()`에 `KRX_HOLIDAYS` 검사를 추가하여 공휴일 스케줄러 실행 차단.
  3. **하드코딩 키 제거 및 강제 검증:** `init_config()` 내 하드코딩 대체 키를 제거하고 `.env` 미설정 시 예외 발생.
  4. **텔레그램 길이 초과 방지:** `send_telegram()` 4,000자 자동 자름(Truncate) 적용.
  5. **매수가능조회 파라미터 교정:** `TTTC8908R` 시장가(01) 조회 시 `ORD_UNPR="0"` 전달 규격 준수.






