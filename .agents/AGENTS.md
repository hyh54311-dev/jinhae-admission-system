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

## 9. 진해고등학교 입학 상담 챗봇 v2.0 연간 지속 운영 및 지식 베이스 관리 규칙
- **설명:** 진해고등학교 입학 상담 챗봇(jinhae-bot2) 소스 코드, 지식 베이스 파일 관리, 매년 연속 운영(Next-Year Continuity)을 위한 표준 운영 지침입니다.
- **챗봇 소스 및 DB 위치:**
  * 챗봇의 핵심 로직과 지식 베이스: 로컬 `jinhae-bot/jinhae-bot-main`
  * 핵심 지식 베이스 파일: `jinhae-bot/jinhae-bot-main/api/knowledge.txt`
  * 백엔드 API & 헬스체크: `jinhae-bot/jinhae-bot-main/api/index.py`
- **배포 및 연동 규칙:**
  * Vercel 라이브 배포(`https://jinhae-bot2.vercel.app`)는 별도의 깃허브 저장소인 `https://github.com/hyh54311-dev/jinhae-bot2.git`와 연동되어 있습니다. (루트 저장소인 `jinhae-admission-system`과 연동되어 있지 않으므로 루트에서 푸시하면 배포되지 않습니다.)
  * 배포 방법: `scratch/deploy_via_github_api.py`를 실행하여 GitHub REST API를 통해 원클릭 자동 배포하거나, `jinhae-bot/jinhae-bot-main` 경로에서 git push를 수행합니다.
- **연도별 지속 운영(Next-Year Continuity) 5대 필수 갱신 체크리스트:**
  1. **신입생 모집 전형 일정:** 당해 연도 12월 원서접수 기간, 합격자 발표일, 등록확인서 제출 기한 갱신.
  2. **입학설명회 일정:** 당해 연도 10월 설명회 일시(통상 18:30 시작) 및 장소(강당/체육관), 기숙사 견학 안내.
  3. **전년도 합격선 및 충원 현황:** 직전 학년도 합격자 커트라인(석차백분율) 및 미달 여부(정상 충원 여부) 갱신.
  4. **최신 대입 진학 실적:** 재학생 및 졸업생(재수생/N수생)을 포함한 서울대, 의예과, 수도권 주요대, 거점국립대, 사관학교 최신 실적 갱신.
  5. **교내 동아리 현황:** 당해 연도 확정된 창체 동아리(약 40~45개) 및 자율 동아리 목록 동기화.
- **지식 베이스 작성 규칙:**
  * 중학교별 신입생 분포 통계를 최신화하거나 추가할 때는 사용자가 대화방에서 축약어로 질문해도 100% 매칭할 수 있도록 중학교 명칭 옆에 괄호로 축약어 별칭을 명시해야 합니다. (예: `진해냉천중학교 (냉천중): 53명`, `진해남중학교 (진해남중): 51명` 등)
  * 신입생 예비소집일, 배치고사 등 미실시 항목은 학생/학부모의 불안감을 덜 수 있도록 순화된 문장으로 안내합니다.

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

## 35. 소크라틱 수업 설계 웹앱 v2.4 아키텍처 및 7대 개발 규칙 (2026-08-17)
- **개요:** 외부 코드 리뷰 2차 지적사항을 반영한 소크라틱 수업 설계 웹앱의 핵심 아키텍처 및 영구 개발 수칙.
- **7대 핵심 개발 규칙**:
  1. **LLM 모델명 하드코딩 금지:** `AiRouter.gs`의 `routeAiRequest()`를 반드시 경유하여 런타임에 ListModels API로 활성 모델을 동적 탐지 및 6시간 캐시 활용.
  2. **학습 데이터 API 스펙 과신 금지:** Gemini 3.x에서 `temperature`는 deprecated이므로 2.x 계열에만 조건부 전달. Gemini 3.x 사고 토큰을 위해 `maxOutputTokens: 4096` 설정. Upstage 정식 모델명은 `solar-mini`, `solar-pro2`, `solar-pro3` 사용.
  3. **단계별 API 응답 파싱:** `promptFeedback` 및 `finishReason`을 사전 검증하여 안전 필터 차단 시 TypeError 방지.
  4. **XSS 및 마크다운 안전 처리:** `escapeHtml()`과 `formatAiText()`를 경유하여 HTML 주입 방어 및 별표 노출 방지.
  5. **Placeholder 실데이터 오염 방지:** contenteditable 내부에 텍스트 대신 `data-placeholder` 속성과 CSS `:empty:before` 가상 요소 사용.
  6. **지원 형식 엄격 제한:** 교과서 파일 업로드 시 `.txt`, `.md` 등 실제 처리 가능한 확장자만 허용.
  7. **교육과정 성취기준 날조 절대 금지 (최우선):** DB 미등록 과목에 대해 가짜 코드를 생성하거나 출처를 NCIC로 위장하지 말 것. 미등록 시 `STANDARD_UNREGISTERED_CODE`(`'(미등록)'`)를 반환하고, 마스터 캐시 시트에 쓰지 않으며, AI 프롬프트에 성취기준 날조 금지 가드레일을 유지할 것.

## 36. 2026학년도 창체 동아리 '대신해 AI' 축제 부스(AI 안면분석·동물상·인쇄) 운영 계획 및 하드웨어/수업 로드맵 (2026-08-19)
- **개요:** 2026학년도 교내 축제(교내 행사)에서 창체 동아리 '대신해 AI'가 운영할 AI 체험 부스 마스터 플랜.
- **핵심 파일 위치:** `2026_창체동아리_대신해AI_축제부스_운영계획.md`
- **핵심 운영 및 보안 원칙:**
  1. **개인정보 완전 보호:** 이름/신원 수집 0%, 촬영 사진 서버 미저장(메모리 분석 후 즉시 휘발), 부스 전면 안심 안내문 부착.
  2. **1장 캡처(3초 타이머):** 대기시간/네트워크 지연 방지 및 재미 요소 극대화.
  3. **UX 흐름:** [홈 화면 2분기 (동물상 / 기분인식)] ➔ [3초 카운트다운 촬영] ➔ [AI 분석 (Gemini Vision)] ➔ [결과 카드 출력] ➔ [학교 프린터 즉석 인쇄(굿즈화)].
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

## 34. 8월 24일(월) 학생회 주관 멘토링 행사 (홈베이스) (2026-08-21)
- **일시:** 2026년 8월 24일(월) 6~7교시
- **내용:** 학생회 주관 멘토링 행사 진행
- **장소:** 교내 홈베이스 (부서별 행사 및 교과 수업 사전 조율 완료)

## 35. 소크라틱 수업 설계 웹앱 v2.4 아키텍처 및 7대 개발 규칙 (2026-08-17)
- **개요:** 외부 코드 리뷰 2차 지적사항을 반영한 소크라틱 수업 설계 웹앱의 핵심 아키텍처 및 영구 개발 수칙.
- **7대 핵심 개발 규칙**:
  1. **LLM 모델명 하드코딩 금지:** `AiRouter.gs`의 `routeAiRequest()`를 반드시 경유하여 런타임에 ListModels API로 활성 모델을 동적 탐지 및 6시간 캐시 활용.
  2. **학습 데이터 API 스펙 과신 금지:** Gemini 3.x에서 `temperature`는 deprecated이므로 2.x 계열에만 조건부 전달. Gemini 3.x 사고 토큰을 위해 `maxOutputTokens: 4096` 설정. Upstage 정식 모델명은 `solar-mini`, `solar-pro2`, `solar-pro3` 사용.
  3. **단계별 API 응답 파싱:** `promptFeedback` 및 `finishReason`을 사전 검증하여 안전 필터 차단 시 TypeError 방지.
  4. **XSS 및 마크다운 안전 처리:** `escapeHtml()`과 `formatAiText()`를 경유하여 HTML 주입 방어 및 별표 노출 방지.
  5. **Placeholder 실데이터 오염 방지:** contenteditable 내부에 텍스트 대신 `data-placeholder` 속성과 CSS `:empty:before` 가상 요소 사용.
  6. **지원 형식 엄격 제한:** 교과서 파일 업로드 시 `.txt`, `.md` 등 실제 처리 가능한 확장자만 허용.
  7. **교육과정 성취기준 날조 절대 금지 (최우선):** DB 미등록 과목에 대해 가짜 코드를 생성하거나 출처를 NCIC로 위장하지 말 것. 미등록 시 `STANDARD_UNREGISTERED_CODE`(`'(미등록)'`)를 반환하고, 마스터 캐시 시트에 쓰지 않으며, AI 프롬프트에 성취기준 날조 금지 가드레일을 유지할 것.

## 36. 2026학년도 창체 동아리 '대신해 AI' 축제 부스(AI 안면분석·동물상·인쇄) 운영 계획 및 하드웨어/수업 로드맵 (2026-08-19)
- **개요:** 2026학년도 교내 축제(교내 행사)에서 창체 동아리 '대신해 AI'가 운영할 AI 체험 부스 마스터 플랜.
- **핵심 파일 위치:** `2026_창체동아리_대신해AI_축제부스_운영계획.md`
- **핵심 운영 및 보안 원칙:**
  1. **개인정보 완전 보호:** 이름/신원 수집 0%, 촬영 사진 서버 미저장(메모리 분석 후 즉시 휘발), 부스 전면 안심 안내문 부착.
  2. **1장 캡처(3초 타이머):** 대기시간/네트워크 지연 방지 및 재미 요소 극대화.
  3. **UX 흐름:** [홈 화면 2분기 (동물상 / 기분인식)] ➔ [3초 카운트다운 촬영] ➔ [AI 분석 (Gemini Vision)] ➔ [결과 카드 출력] ➔ [학교 프린터 즉석 인쇄(굿즈화)].
- **하드웨어 및 예산 구성 (20만 원 한도 / 실지출 198,000원, 잔여 2,000원):**
  1. **구매 품목 (3종):** 카멜 CPM1530IT 터치 포터블 모니터(159,000원, 무료배송), MT-VIKI HDMI 1:2 분배기(19,000원, 배송비 3천원 포함), ipTIME N704E Plus 유무선 공유기(20,000원).
  2. **학교 시설/보유분 활용 (예산 0원):** 흰색 칠판(배경천 대체), 벽걸이 TV (공중 설치 완료, 바닥 스탠드 불필요), 유휴 PC(폐PC 서버), 웹캠 & 삼각대, 노트북, 일반 학교 프린터, 케이블류.
  3. **배선 연결:** 노트북 HDMI ➔ 1:2 분배기 ➔ [벽걸이 TV (관람용)] + [터치모니터 (참가자용)], 터치 입력은 USB 직결, 폐PC는 공유기에 유선 직결.

## 37. 8월 24일(월) 학생회 주관 멘토링 행사 (홈베이스) (2026-08-21)
- **일시:** 2026년 8월 24일(월) 6~7교시
- **내용:** 학생회 주관 멘토링 행사 진행
- **장소:** 교내 홈베이스 (부서별 행사 및 교과 수업 사전 조율 완료)

## 38. 2027학년도 전국연합학력평가 및 대학수학능력시험 시행 일정 (2026-08-24)
- **근거:** 서울특별시교육청 중등교육과-28326(2026. 8. 21.) 사전 안내
- **전체 시행 일정 요약 (구글 캘린더 등록 완료)**:
  1. **2027. 03. 24.(수):** 3월 전국연합학력평가 (1·2·3학년 / 서울시교육청 주관)
  2. **2027. 05. 11.(화):** 5월 전국연합학력평가 (3학년 / 경기도교육청 주관)
  3. **2027. 06. 02.(수):** 6월 모의평가(3학년 평가원) / 학력평가(1·2학년 부산시교육청) (예정안)
  4. **2027. 07. 08.(목):** 7월 전국연합학력평가 (3학년 / 인천시교육청 주관)
  5. **2027. 08. 25.(수):** 8월 모의평가(3학년 평가원) / 학력평가(1·2학년 인천시교육청) (예정안)
  6. **2027. 10. 19.(화):** 10월 전국연합학력평가 (3학년 서울시교육청 / 1·2학년 경기도교육청)
  7. **2027. 11. 18.(목):** 2028학년도 대학수학능력시험 (수능 본시험 / 한국교육과정평가원)

## 39. 주간 육아시간 전수 교차검증 및 금요일 08:30 텔레그램 자동 발송 규칙 (2026-08-24)
- **개요:** 교사의 주간 육아시간(1일 최대 2시간) 산정 시, 정규 시간표뿐만 아니라 일과에 영향을 미치는 모든 변동 요소를 100% 교차 검증하여 신청 가이드를 제공함.
- **5대 교차 검증 요소:**
  1. **정규 시간표:** 2학기 확정시간표 (2학년 화법과 언어, 3학년 심화국어)
  2. **수업 교체 및 대강:** 교사 간 수업 맞교환 (예: 김수민 교사와의 2-8반 교환) 및 결보강/대강 내역
  3. **3학년 당김수업:** 수능 이전 오후 7·8교시에 진행되는 「3학년 수업 시수 확보 계획」(총 19회)
  4. **동아리 및 방과후:** 「AI 동행 프로젝트(책임안전AI)」 6~8교시(14:35~17:35) 컴퓨터실 분과교육 등
  5. **학사 일정:** 전국연합학력평가, 고사(지필평가), 현장체험학습 등 교내 행사
- **자동화 스케줄러 등록:**
  - **작업명:** `Jinhae_Friday_ParentingLeave_Notifier` (Windows Task Scheduler 등록 완료)
  - **발송 시점:** **매주 금요일 오전 8시 30분(08:30 KST)**
  - **발송 내용:** 다음 주(월~금)의 요일별 수업 종료 시점, 당김/동아리 여부, 추천 육아시간 활용 방식 및 조기 퇴근 시간 안내
  - **운영 방식:** Antigravity 채팅창 UI에 백그라운드 태스크 배너가 뜨지 않도록 **Windows OS 독립 백그라운드 스케줄러**로 완전 무인 실행됨.

## 38. 2026학년도 2학기 확정시간표 (2026-08-21 기준) 표준 데이터소스 적용 규칙
- **개요:** 2026년 8월 21일 자로 새롭게 확정된 2학기 시간표 파일들을 모든 시간표 분석 및 교체/대강 작업의 표준 데이터소스로 사용함.
- **공식 파일 위치:**
  * 전체 시간표 (엑셀): `D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\시간표\2학기\확정시간표\2026. 2학기 전체시간표(8.21).xlsx`
  * 주간 시간표 (엑셀): `D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\시간표\2학기\확정시간표\2026. 2학기 주간시간표(8.21).xlsx`
  * 교사/학급 시간표 (한글): `2026. 2학기 교사시간표(8.21).hwp`, `2026. 2학기 학급시간표(8,21).hwp`
  * **수요일:** 1교시(308 심국), 2교시(207 화법), 4교시(208 화법), 5교시(303 심국)
  * **목요일:** 2교시(305 심국), 4교시(304 A_교육), 5교시(301 심국)
  * **금요일:** 2교시(307 심국), 5교시(304 심국)

## 39. 진해고등학교 컴퓨터실 자물쇠 및 학생 PC 로그인 비밀번호 규칙 (2026-08-24)
- **컴퓨터실 자물쇠 비밀번호:** `8133` (출입문 자물쇠 개방용)
- **학생 PC 로그인 비밀번호:** `정보쌤1!` (윈도우 부팅 로그인용)
- **설명:** 진해고등학교 컴퓨터실 출입문 자물쇠 비밀번호(`8133`)와 학생용 PC의 윈도우 로그인 비밀번호(`정보쌤1!`) 정보입니다. 향후 컴퓨터실 실습, 방과후 수업, 창체 동아리 실습 진행 및 교내 시설 이용 안내 시 최우선 상기 및 활용하십시오.

## 40. 2027학년도 신입생 입학 전화 상담 학부모 및 학생 관리 대장 (2026-08-24)
- **개요:** 교무실로 인입된 2027학년도 예비 신입생 학부모 전화 상담 핵심 내역을 기록·보존하여, 후속 상담 및 입학 지원 시 맞춤형 정보를 제공함.
- **상담 기록 명부:**
  1. **010-4878-7882 (부친)**
     * **출신/내신:** 웅천중 성적 2%대 (극상위권)
     * **고민 사항:** 거창대성고와 진해고등학교 사이에서 최종 진학처 비교 고민 중.
     * **희망 진로:** 의예과(의대) 진학 희망 (특히 '지역의사제도' 및 '지역인재전형' 적극 활용 목표).
     * **핵심 선호:** 면학 분위기가 잡힌 기숙사 완비 학교 강력 선호.
     * **상담 대응 전략:** 2%대 내신으로 기숙사(동백관 1실 3인, 전용 면학실) 우선 선발 확실, 2026학년도 의예과 3명/서울대 1명 등 지역인재 의대 진학 강점 및 진해인재스쿨 1:1 심화 관리 적극 안내.
  2. **010-2108-4365 (모친)**
     * **출신/내신:** 반송중 성적 40%대
     * **고민 사항:** 진해고 기숙사 입소를 강력 희망하나, 관외 기숙사 우선 선발 쿼터(내신 30% 이내) 대비 성적이 다소 애매하여 합격 및 입소 여부 고민.
     * **후속 조치:** 가정 내에서 학생과 추가로 상의한 뒤 다시 학교로 연락 주기로 함.
  3. **010-2576-9377 (모친)**
     * **출신/거주지:** 반송중학교 (창원시 성산구 반송동 거주 추정, 진해 관외)
     * **고민 사항:** 학생이 기숙사가 있는 일반고 진학을 적극 희망 중이나, 1학기에 기숙사에 입소하더라도 2학기에 내신 성적이 떨어지면 퇴소되어 반송동에서 원거리 통학을 해야 하는지 여부 및 기숙사 유지/재선발 기준 문의.
     * **상담 대응 전략:** 기숙사 학기별 운영 및 관외 원거리 학생 안배 규정, 10.22(목) 18:30 설명회 및 기숙사 시설 견학 안내.
## 41. K-에듀파인 장학생 선발 심의위원회 개최 공문 표준 기안 형식 (2026-08-26)
- **개요:** 장학생 선발 심의위원회 개최 시 작성하는 K-에듀파인 내부결재 표준 기안 형식 및 줄바꿈/참석대상 표기 규칙.
- **표준 기안문 템플릿:**
  ```text
  1. 관련: [접수등록번호(일자, "접수공문제목")]
  2. [학년도] [장학재단/장학회명] 장학생 선발 심의위원회를 아래와 같이 개최하고자 합니다.
   가. 일시: YYYY년 M월 D일(요일) HH시 mm분
   나. 안건: [장학재단명] 장학생 추천에 대한 추인
   다. 장소: 2층 교무실
   라. 참석 대상: 위원장, 교무부장, [해당 학년부장], 간사.  끝.
  ```
- **핵심 작성 규칙:**
  1. **관련 공문 표기:** 학교 접수번호, 일자, 큰따옴표 공문제목을 정확히 기재 (예: `진해고-9576(2026. 8. 6., "2026년 장학생(학업성적우수자)추천의뢰")`).
  2. **참석 대상자 범위:** 전 학년 대상이 아닌 경우, **해당 장학금 수혜 대상 학년부장만 선별하여 기재** (예: 2·3학년 대상 장학금이면 1학년부장 제외 후 `위원장, 교무부장, 2학년부장, 3학년부장, 간사.  끝.`).
  3. **서식 및 여백:** 1항과 2항은 연속 번호로 배치하고, 하위 목록(가~라) 앞 1칸 들여쓰기 및 `끝.` 앞 2칸 공백 유지.
## 42. 2027학년도 신입생 교육과정 편성 및 선택과목 수요조사·폐강 분석 지침 (2026-08-26)
- **개요:** 2027학년도 신입생 교육과정 편성 시 교과협의회 논의 사항 및 1·2학년 선택과목 1·2차 수요조사 결과에 따른 개설/폐강 특이점.
- **학생 과목 선택 지도 시 3대 핵심 원칙:**
  1. **실제 개설 전제 편성:** 교육과정 편성표에 편성하는 과목은 실제 개설을 전제로 함 (사장 과목 방지).
  2. **소수 인원 내신 유불리 우려 완화:** 과목 세분화 시 동일 교과군 내 수강 인원 축소로 인한 학생들의 성적 유불리 불안 고려.
  3. **예측 가능성 확보 및 이탈 방지:** 1차 조사 후 과목 폐강/재조정 시 다른 교과군으로 연쇄 이탈하는 현상을 최소화하여 학생 진로 예측 가능 환경 보장.
- **선택과목 1·2차 조사 및 개설/폐강 통계:**
  * **2학년 2학기 (2-2):**
    - `문학과 영상`: 1차 34명 ➔ 2차 45명 (개설 확정)
    - `언어생활 탐구`: 1차 17명 ➔ **폐강**
    - `세계 문화와 영어`: 1차 44명 ➔ 2차 45명 (개설 확정)
    - `실생활 영어 회화`: 1차 16명 ➔ **폐강**
  * **3학년 1학기 (3-1):**
    - `독서 토론과 글쓰기`: 1차 28명 ➔ **폐강**
    - `매체 의사소통`: 1차 53명 ➔ 2차 84명 (개설 확정, 대폭 증가)
    - `미디어 영어`: 1차 20명 ➔ 2차 36명 (개설 확정)
    - `심화 영어`: 1차 13명 ➔ **폐강**
- **현재까지 취합된 공식 편성 삭제 과목 (2과목):**
  * `과학과제 연구` (3-1 / 과학)
  * `수학과 문화` (3-1 / 수학)
## 43. 2026학년도 2학기 학부모 초청 수업나눔의 날 (2026-10-29 목 1~3교시) (2026-08-26)
- **일시:** 2026년 10월 29일(목) 1~3교시 (08:50 ~ 11:40)
- **개요:** 2학기 학부모 초청 수업나눔의 날 (전 교사 예외 없이 1시간 수업공개 의무).
- **공개 과목 및 학반 입력 시트:** [`https://docs.google.com/spreadsheets/d/1PWBulEtgCtPk6IbStcCHamlattr6560g_XR8LsbBNIg/edit?usp=sharing`](https://docs.google.com/spreadsheets/d/1PWBulEtgCtPk6IbStcCHamlattr6560g_XR8LsbBNIg/edit?usp=sharing)
- **황요한 교사 목요일 1~3교시 시간표:**
  * 1교시: 공강
  * **2교시:** **3학년 5반 (심화국어)** ➔ 수업공개 대상 유력
  * 3교시: 공강
- **구글 캘린더 등록 완료:** [이벤트 링크](https://www.google.com/calendar/event?eid=MWF0MXJnaWc2b3VrY2Rkb2pqMWc5Zm02MGMgaHloNTQzMTFAbQ)
## 44. 해준이 등·하원 및 2학기 육아시간 구글 스프레드시트 관리 규칙 (2026-08-26)
- **스프레드시트 URL:** [`https://docs.google.com/spreadsheets/d/1XxcqgI7i5EKPzN9sxxqSfL2RKSz25YZAxv2sSDmB9Gk/edit?usp=sharing`](https://docs.google.com/spreadsheets/d/1XxcqgI7i5EKPzN9sxxqSfL2RKSz25YZAxv2sSDmB9Gk/edit?usp=sharing)
- **명칭 약어 정의:**
  * **"박":** 박지혜 (선생님 아내)
  * **"황":** 황요한 (선생님 본인)
- **박지혜 선생님 2026학년도 2학기 주간 시간표 (총 17시간):**
  * **월요일 (3시간):** 2교시(2-4 미적분I), 5교시(2-3 미적분I), 6교시(2-8 E경제수학)
  * **화요일 (3시간):** 2교시(2-7 미적분I), 4교시(3-9 B미적분), 6교시(2-8 E경제수학)
  * **수요일 (4시간):** 1교시(2-6 미적분I), 2교시(2-1 미적분I), 4교시(3-9 B미적분), 6교시(창체)
  * **목요일 (4시간):** 2교시(2-9 미적분I), 3교시(2-2 미적분I), 5교시(3-8 미적분), 6교시(2-5 미적분I)
  * **금요일 (3시간):** 1교시(2-8 E경제수학), 4교시(3-9 B미적분), 6교시(3-8 미적분)
- **시트 구조 (9월 시트 기준):**
  * Col A: 날짜 | Col B: 요일 | Col C: 육아시간 활용/특이사항
  * Col D: 등원 가능 여부 [박] (O/X) | Col E: 등원 가능 여부 [황] (O/X)
  * Col F: 하원 담당자 | Col G: 하원 가능 여부 [박] (O/X) | Col H: 하원 가능 여부 [황] (O/X)
- **작업 원칙:**
  * 사용자가 명시적으로 "0일부터 0일까지 입력해"라고 요청하기 전까지는 **임의로 시트에 쓰기/수정 작업을 절대 하지 않음**.
  * 등원 및 하원 담당 배정 지침이 주어지면 지정된 날짜 구간에 맞춰 정확히 기록함.
## 45. (재)진해고등학교동창회장학재단 / 총동창회 공식 연락처 및 담당자 명단 (2026-08-26)
- **재단 사무국 핵심 연락처:**
  * **사무간사:** **정경미** (`010-2875-1025`)
  * **사무국장:** **김형태** (`010-4559-0706`)
  * **상임이사:** 최상찬
  * **이사장:** 김종년
  * **재단 사무실 일반전화:** `055-546-9821`
  * **재단 팩스번호 (FAX):** `055-542-9822`
  * **재단 소재지:** 경남 창원시 진해구 충장로 82번길 12-1, 3층 (우 51679)
- **업무 처리 프로세스:** 장학생 추천 공문/서류 팩스 발송 ➔ 김형태 사무국장 또는 정경미 사무간사 유선 수신 확인.
## 46. 2027학년도 고입전형 지원 온라인시스템 업무담당자 연수 출장 (2026-09-22 화) (2026-08-27)
- **일시:** 2026년 9월 22일(화) 14:00 ~ 16:30 (등록 13:30 ~ 14:00 / 출장 이동 고려 13:00 출발)
- **장소:** 마산대학교 창의관 송원홀 (경남 창원시 마산회원구 내서읍 함마대로 2640)
- **참석 대상:** 진해고등학교 입학업무담당자 황요한 (학교당 1인 필수 참석)
- **행정 기한:** 참석자 명단 교육행정데이터통합관리시스템 **제출 완료 (2026-08-27 조기 제출)**.
- **당일(화요일) 시간표 및 대강/수업교체 대상:**
  * 2교시 (09:50~10:40): 2학년 9반 (화법과 언어) - 정상 수업
  * 3교시 (10:50~11:40): 2학년 9반 (화법과 언어) - 정상 수업
  * **★ 5교시 (13:40~14:30): 3학년 9반 (심화국어)** ➔ **출장으로 대강/수업교체 필수**
  * **★ 6교시 (14:40~15:30): 3학년 2반 (심화국어)** ➔ **출장으로 대강/수업교체 필수**
- **구글 캘린더 등록 완료:** [이벤트 링크](https://www.google.com/calendar/event?eid=dHFjc2YyZ3UxdmU4OXE1YmNmZ3J2bWJuYzggaHloNTQzMTFAbQ)
## 47. 9월 전국연합학력평가 및 9월 수능 모의평가 시행 지침 (2026-09-02 수) (2026-08-27)
- **일시:** 2026년 9월 2일(수) 08:40 ~ 17:10 (학교번호: `24118` 칠판 기재)
- **대상:** 1, 2학년(전국연합학력평가) / 3학년(9월 모의평가)
- **추가 시험실 4개소 현황:**
  1. **1층 홈베이스:** 졸업생(N수생) 응시
  2. **1층 지구과학실:** 졸업생(N수생) 응시
  3. **2층 도서실 옆 교실:** 도움반(특수학급) 학생 응시
  4. **4층 창의융합실:** 도움반(특수학급) 학생 응시
- **1, 2학년 4교시 탐구영역 감독 분담 및 인수인계 수칙 (노란색 하이라이트 변경안):**
  * `14:45 ~ 15:20`: **부담임** 입실 ➔ 한국사 본시험 감독 및 한국사 답안지 회수
  * ★ `15:20 ~ 15:35` (15분간): **부담임**이 **사회탐구 문답지 배부 진행**
  * `15:35 ~ 16:15`: **담임** 입실 ➔ 사회탐구 본시험 감독
  * `16:15 ~ 16:30`: 사회탐구 답안지 회수 및 과학탐구 문답지 배부 (담임)
  * `16:30 ~ 17:10`: 과학탐구 본시험 감독 (담임)
  * `17:10 ~ 17:20`: 청소 및 채점 (담임)
- **황요한 선생님(2-5 부담임) 9/2(수) 감독 교시:**
  * 1교시(국어): 1교시 교사(08:40~09:20) / 2교시 교사(09:20~10:00)
  * 2교시(수학): 4교시 교사(11:20~12:10)
  * 3교시(영어): 5교시 교사(13:10~14:00)
  * 4교시(탐구): **2-5반 부담임 감독(14:45~15:35: 한국사 감독 + 사회탐구 문답지 배부)**
## 48. 2학기말 시수 조정에 따른 9/2(수) 7교시 나이스 시간표 이동 안내 (김수진 선생님) (2026-08-27)
- **내용:** 개학일 1교시 수업 이동(6교시)에 따른 2027. 2. 3.(수) 1교시 수업의 나이스 시수 당김 누락분 보정을 위해, 해당 수업을 **2026년 9월 2일(수) 모의평가일 7교시**로 시간표상 이동 배치함.
- **실제 수업 여부:** 9월 2일(수)은 전교생 모의평가/전국연합 시험일이므로 **실제 수업은 없음(0시간)**.
- **유의 사항:** 9월 2일(수) 오후 조퇴, 외출, 출장 등 복무 신청 시 나이스 7교시 수업 결손 여부만 유의(조퇴/출장 계획이 없을 경우 별도 조치 불필요).

## 49. 시간표 수정/교체/대강 확정 시 구글 캘린더 자동 등록 및 아침 브리핑 연동 영구 규칙 (2026-08-28)
- **규칙:** 사용자가 시간표 수정, 수업 교환, 대강, 보강, 당김수업 조율 등을 요청하여 작업이 완료/확정되면, **모든 시간표 변경 내역을 즉시 구글 캘린더(Google Calendar API / `token_calendar.json`)에 등록**해야 함.
- **연동 목적:** 사용자가 매일 아침 제미나이(Gemini)로부터 "오늘의 일정" 아침 브리핑을 받을 때, 구글 캘린더에 등록된 수정 시간표(수업 교환/대강/보강 내역)를 자동으로 읽어 정확히 안내받을 수 있도록 함.
- **구글 캘린더 이벤트 등록 표준 양식:**
  * **이벤트 제목 (Summary):** `[수업교환] 2교시 208반 화법 (김수민T 미적분 교환)` 또는 `[대강] 2교시 305반 심화국어 (김승우T 대강)` 또는 `[당김수업] 8교시 306반 심화국어`
  * **이벤트 시간 (Start/End):** 학교 정규 교시 시간 (예: 1교시 08:50~09:40, 2교시 09:50~10:40, 3교시 10:50~11:40, 4교시 11:50~12:40, 5교시 13:40~14:30, 6교시 14:40~15:30, 7교시 15:40~16:30, 8교시 16:40~17:30).
  * **알림 설정:** 기본 팝업 알림 활성화.

## 50. Playwright 기반 항공권 최저가 실시간 모니터링 & 텔레그램 알림 봇 아키텍처 및 다구간 확장 가이드 (2026-08-31)
- **개요:** 구글 플라이트 실시간 화면을 크롤링하여 목표 기준가보다 저렴한 직항 특가를 실시간 포착하고, 일요일 정기 브리핑을 텔레그램으로 자동 발송하는 무인 모니터링 봇(`flight_tracker_bot.py` v3.3).
- **저장소 위치:**
  * 메인 스크립트: `flight_tracker_bot.py`
  * 깃허브 액션: `.github/workflows/flight_price_tracker.yml`
  * 상태 파일: `state.json`
  * 실물 덤프 픽스처: `fixtures/real_google_flights_dump.json`
- **핵심 아키텍처 및 7대 수칙:**
  1. **[최우선 원칙 - Fail-Closed]:** "틀린 알림을 보내는 것이 알림을 안 보내는 것보다 훨씬 나쁘다." 출발시각, 직항 여부, 가격 단서 중 하나라도 모호하거나 확신이 없으면 즉시 후보에서 제외.
  2. **[Protobuf TFS 동적 인코더]:** `generate_google_flights_tfs(origin, dest, depart_date, return_date, passengers, currency)`를 통해 구글 플라이트 바이너리 wire format을 실시간 생성하여 URL 동적 직렬화.
  3. **[카드 단위 격리 파싱]:** `page.query_selector_all("ul[role='list'] > li, li.pIav2d")`로 카드별 `inner_text()`를 격리 추출. `"경유 없음"`, `"0회 경유"`를 사전 마스킹한 뒤 직항 여부 엄격 판정.
  4. **[다중 가격 & 쌍 식별 파서]:** 카드 내 $P_{max} \approx P_{min} \times \text{PASSENGERS}$ 관계 성립 시 1인당/총액 쌍으로 자동 식별(중복 $\div 3$ 차단). 수수료 라벨 붙은 가격 제외. 비즈니스석 등 관계식 없는 다중 가격은 안전 탈락.
  5. **[Fail-Closed 황금시간대 검증]:** 출발 시각 미식별 시 탈락. "2:30 소요" 등 소요시간 배제, 매치된 출발 시각 토큰 자체의 AM/PM만 국소 바인딩.
  6. **[상태 관리 & 래칫 TTL]:** `state.json`에 관측 이력, 연속 실패수, 마지막 알림가(`last_alert_price_pp`), 알림 시각(`last_alert_ts`) 저장. 7일 경과 시 래칫 만료 및 기준가 반등 시 리셋. 2회 연속 실패 시 24시간 1회 장애 알림.
  7. **[CI/CD Git Rebase 순서]:** 워크플로에서 `git add state.json` ➔ `git diff --staged` ➔ `git commit` ➔ `git pull --rebase` ➔ `git push` 순서를 엄수하여 인덱스 충돌 원천 차단.
- **신규 노선 확장 가이드 (오키나와, 후쿠오카, 다낭 등):**
  * 스크립트 상단의 **여정 상수(6개 변수)**만 변경하면 즉시 동일한 100% 무인 특가 감시망 가동 가능:
    ```python
    ORIGIN = "PUS"                      # 출발 공항 (예: 부산 김해)
    DESTINATION = "OKA"                 # 도착 공항 (예: 일본 오키나와 나하)
    DEPART_DATE = "2027-01-14"          # 출발일 (YYYY-MM-DD)
    RETURN_DATE = "2027-01-17"          # 귀국일 (YYYY-MM-DD)
    PASSENGERS = 3                      # 탑승 인원수
    BENCHMARK_PRICE_PER_PERSON = 350000 # 기준 예매가 (이보다 쌀 때만 알림)
    FREE_CANCEL_DEADLINE = datetime.date(2026, 12, 1) # 무료 취소 마감일
    ```
  * 오키나와 노선은 진에어, 제주항공, 대한항공, 티웨이항공 등 국적 LCC/FSC 직항편이 주로 취항하며, 위 봇 구조 그대로 1인당 특가를 완벽히 추적할 수 있음.

## 51. 2026학년도 1학기 애향삼품 장학생 추천 및 서류 수합 일정 (2026-08-31)
- **개요:** 2026학년도 1학기 애향삼품 장학생(총 6명, 학년별 2명, 1인당 80만원, 총 480만원) 선발 및 서류 수합 공식 일정.
- **주요 일정 및 마감:**
  * **서류 제출 마감:** **2026년 9월 3일(목) 12:30까지**
  * **수합 방법:** 교무기획부 장학 담당(황요한 교사)이 각 학년 교무실을 직접 순회하여 수합.
  * **제출 서류 3종:**
    1. 장학생 추천서 1부 (담임교사 작성 - 바탕화면 `애향삼품_장학생_추천서_양식.hwp`)
    2. 장학생 감사편지 1부 (선발 학생 자필 작성 - 바탕화면 `애향삼품_장학생_감사편지_양식.hwpx`)
    3. 장학생선발소심의위원회 협의록 1부 (학년부별 작성 - 바탕화면 `애향삼품_장학생선발소심의위원회_협의록_양식.hwp`)
- **선발 및 추천 기준 요약:**
  * **추천 자격:** 1학기 내신 성적 3등급 이내의 성적 우수자 또는 체능·예술 분야 우수자 (학교생활 성실·모범 학생)
  * **선발 제한:** 교내봉사 이상의 징계 처분을 받은 학생, 휴학 중인 학생, 당해 연도(2026) 타 교내·외 장학금 기수혜자(중복 추천 제한 원칙)
  * **학년부 협의:** 학년부 내 다수 추천 시 학년부 협의회 거쳐 내신 성적 우수자 우선하여 학년당 최종 2명 선발.

## 52. 진해고등학교 2026학년도 학년별 사용 교과서 공식 목록 (2026-09-01)
- **공식 출처 파일:** `진해고등학교\2026학년도\수업\2026학년도 3학년 수업&수행&평가\2학기\[붙임3] 2026학년도 학년별 사용 교과서 목록 - 복사본.xlsx`
- **주요 교과별 공식 출판사 및 저자 정보:**
  1. **3학년 심화 국어:** **상문연구사** (저자: **석은동 외 4명**, 구분: 인정교과서, 웹사이트: `http://www.sangmunsa.co.kr/`)
  2. **3학년 화법과 작문:** **㈜천재교육** (저자: **박영목**, 구분: 검정)
  3. **3학년 교육학:** **천재교육** (저자: **강현석**, 구분: 인정)
  4. **3학년 철학 / 논술 / 심리학:** 천재교과서(홍윤기) / ㈜천재교육(박정하 외 7명) / 씨마스(김지경)
  5. **2학년 문학 / 화법과 언어:** ㈜비상교육(강호영) / ㈜비상교육(이관규)
  6. **1학년 공통국어1, 2:** 비상교육(박영민) [2022 개정 교육과정]

## 53. 교무기획부 경비 및 커피/다과/회식비 정산 구글 스프레드시트 (2026-09-01)
- **문서명:** `2026학년도 1학기 교무기획부 경비 정산부`
- **구글 스프레드시트 ID:** `1yHEJsvgtQ6crum5H3PuKZzoQzEOxUhs5tT1_WUJzGr8`
- **스프레드시트 링크:** `https://docs.google.com/spreadsheets/d/1yHEJsvgtQ6crum5H3PuKZzoQzEOxUhs5tT1_WUJzGr8/edit?usp=sharing`
- **대상 부서원 (6명):** 최준호 부장님, 박지환 선생님, 박승현 선생님, 이병의 선생님, 김현숙 주무관님, 황요한 선생님
- **주요 용도 및 관리 내역:**
  * 교무실 커피 원두 공동 구매, 카페 음료 및 다과, 부서 회식비 지출 내역 기록
  * 날짜별/품목별 참석 인원 체크박스 연동을 통한 실시간 1인당 1/N 자동 정산 및 개인별 누적 정산액/입금 관리.

## 54. 진해고등학교 2026학년도 9월 공식 월중행사계획 (2026-09-01)
- **개요:** 진해고등학교 2026년도 9월 월중 학사일정 및 부서별 주요 행사 공식 계획.
- **일자별 주요 학사일정 요약:**
  * **9. 2.(수):** `[교육평가부]` 1, 2학년 전국연합학력평가 / 3학년 9월 수능모의평가
  * **9. 3.(목):** *(장학 담당)* 2026-1학기 애향삼품 장학생 서류 수합 마감 (12:30 순회)
  * **9. 4.(금):** `[교육평가부]` 국가수준 학업성취도평가(표집학급) 실시 (1~4교시)
  * **9. 7.(월) ~ 9.17.(목):** `[교육과정부]` 과목 선택 상담 주간 운영
  * **9. 9.(수):** `[진로복지부]` 1, 2학년 대학학과체험 (6-7교시)
  * **9.10.(목):** `[진로복지부]` 일배움과정 체험활동 (도움 1&2반, 부산 기장)
  * **9.11.(금):** `[미래교육부]` 정보공시 3차 제출일 / `[교육연구부]` 전학공 연수 (7교시)
  * **9.14.(월) ~ 9.17.(목):** `[교육과정부]` 3차 선택과목 조사
  * **9.15.(화):** `[교육평가부]` **2학기 1차 지필평가 평가원안 제출 마감** ⚠️
  * **9.16.(수):** 
    - `[미래교육부]` 사이버 보안 진단의 날 (내PC지키미 실행일)
    - `[진로복지부]` 학교장과 학부모가 함께하는 소통 공감 마당 (10:00~12:00, 홈베이스)
    - `[교육연구부]` 창체 동아리 활동 (6-7교시)
  * **9.18.(금):** `[교육평가부]` 평가 연수
  * **9.24.(목) ~ 9.27.(일):** **추석 연휴** (24일 목, 25일 추석, 26일 토, 27일 일)
  * **9.29.(화) ~ 9.30.(수):** `[교육평가부]` **2학기 1차 정기시험 (중간고사)** 실시

## 55. 2026학년도 9월 2일(수) 1·2학년 학력평가 및 3학년 수능 모의평가 시행 지침 (2026-09-01)
- **개요:** 2026년 9월 2일(수) 시행 전국연합학력평가(1·2학년) 및 9월 수능모의평가(3학년, 졸업생) 운영 지침.
- **학교번호:** **`24118`** (칠판 필수 기재)
- **시험 중 방송:** **절대 금지**
- **영어 영역(3교시) 음원 안내:**
  * 5교시 담당 감독교사는 **13:05까지 시험지 배부 완료**
  * **영어듣기 평가 음원은 13:07부터 재생** (시험 시작 13:10)
- **특별 시험실 및 응시 현황:**
  * **졸업생 응시실:** **본관 1층 홈베이스 (총 36명)**
  * **도움반 응시실 1:** **4층 창의융합실 (3학년 1명 - 홍나견 학생, 시험시간 1.5배 연장)**
  * **도움반 응시실 2:** **2층 도서실 옆 교실 (3학년 2명)**
- **학년별 시험 및 감독 체계:**
  * **3학년:** 국어(08:40~10:00) ➔ 수학(10:30~12:10) ➔ 점심(12:10~13:05) ➔ 영어(13:10~14:20) ➔ 한국사(14:50~15:20, 부담임 회수) ➔ 탐구 1·2(15:35~16:37, 담임 감독) ➔ 채점(16:37~17:00)
  * **1·2학년:** 국어 ➔ 수학 ➔ 영어 ➔ 한국사(14:50~15:20, 부담임 회수) ➔ 사회탐구(15:35~16:15, 40분, 담임) ➔ 과학탐구(16:30~17:10, 40분, 담임) ➔ 채점(17:10~17:20)
- **파일 보관 위치:**
  * `진해고등학교6학년도\교육평가부6. 9월 모의평가 및 학력평가학년 9월 모의평가, 1,2학년 9월 전국연합학력평가 시간표(9월 2일(수)).hwp`

## 56. 2027학년도 경남과학고 입학전형 면접문항 검토교사 모집 공문 및 일정 (2026-09-01)
- **공문명:** `(진해고등학교-10604) [모집] 2027학년도 경남과학고등학교 입학전형 면접문항 검토교사 모집 안내`
- **모집 분야:** 수학 3명, 과학 3명 (총 6명)
- **자격 요건:** 중등교원자격증(수학/과학) 소지자 중 **최근 5년간 중학교 2년 이상 근무 경력자**
- **소집 기간:** 2026. 11. 21.(토) 08:30 ~ 11. 23.(월) 17:30 (합숙)
- **마감 일정:**
  * **교내 서류 마감:** **2026년 9월 7일(월) 16:30**
  * **경남과고 공문 마감:** **2026년 9월 9일(수) 16:30** (비공개 6호 전자공문)

## 57. 2026 AIEDAP 경남권역 AI융합수업 사례 공유 워크숍 안내 및 상기 규칙 (2026-09-01)
- **행사명:** 2026 AIEDAP 경남권역 AI융합수업 사례 공유 워크숍
- **일시:** 2026. 9. 11.(금) 15:30 ~ 17:30
- **장소:** 부산 벡스코(BEXCO) 제1전시장 214+215호, 217호
- **사전 신청 기한:** **2026년 9월 8일(화) 15:00까지**
- **주요 내용:** AIEDAP 마스터교원 AI 융합수업 실천 사례 21개 발표 및 토의
- **사전 신청 혜택:** 직무연수 2시간 인정, 부산대 AI융합연구원장 명의 참가 공문 발송, 기념품 증정
- **상기 지침:** **2026년 9월 2일(수) 아침 브리핑 시 필수 상기 항목으로 포함하여 사용자에게 안내할 것.**

## 58. 2026년 9월 18일(금) 아내 신촌 세브란스병원 검진 동행 및 대강 요청 상기 규칙 (2026-09-01)
- **개요:** 2026년 9월 18일(금) 아내 신촌 세브란스병원 검진 결과 확인 동행 예정.
- **필수 조치 사항:**
  1. 9월 18일(금) 본인 수업에 대해 동료 교사에게 **대강(보강 또는 수업 교체)** 사전 부탁 및 협조 구하기.
  2. 나이스(NEIS) 근무상황(연가/특별휴가 등) 사전 상신.
- **아침 브리핑 상기 지침:** **2026년 9월 2일(수) 아침 브리핑 시 최우선 필수 상기 항목으로 반드시 포함하여 사용자에게 안내할 것.**

## 59. 2026학년도 국가수준 학업성취도평가 실시 지침 (2026-09-02)
- **일시:** 2026년 9월 4일(금) 08:40 ~ 12:15 (1~4교시, 일과시간 동일)
- **평가 대상 학급 및 장소:**
  - 2학년 9반: 지구과학실
  - 2학년 10반: 1층 홈베이스
- **주요 교내 운영 지침:**
  1. **2학년 2교시 선택과목 이동수업 미실시:** 이동하지 않고 원반에서 자습 지도 (특수학급 학생도 원반 입실).
  2. **방송 통제:** 금요일 1교시~4교시 전체 교내 방송 자제.
  3. **공간 통제:** 9월 3일(목) 오전 노트북 설치 예정, 목요일~금요일 오전까지 지구과학실 및 홈베이스 출입 자제.
  4. **감독 교사:** 2학년 9반, 10반 금요일 1~4교시 교과담당교사가 감독 진행.
  5. **황요한 교사 해당 사항 분석:** 금요일 시간표상 2교시(3-7반 심화국어), 5교시(3-4반 심화국어)이므로 학업성취도 감독 대상이 아니며, 정상적으로 3학년 심화국어 수업 진행함.

## 60. 2026년 9월 3일(목) 2교시 3-5반 수업 조진희 선생님 입실 (2026-09-02)
- **일시:** 2026년 9월 3일(목) 2교시 (09:40 ~ 10:30)
- **대상 학급:** 3학년 5반
- **내용:** 조진희 선생님이 다음 주 수시 원서 접수 방법 시뮬레이션을 위해 해당 시간을 빌려 입실함.
- **황요한 교사 조치:** 3학년 5반 심화국어 수업에 들어가지 않으며, 연구/행정 업무 시간으로 활용. 내일(9/3) 아침 브리핑 시 상기할 것.

## 61. 2026학년도 2학기 평가계획서 수정 및 재제출 상기 규칙 (2026-09-02)
- **개요:** 2026학년도 2학기 교과 평가계획서(3학년 심화 국어 등) 수정 및 재제출 업무.
- **주요 내용:** 2학기 평가계획서 수정본을 보완하여 교육평가부(또는 주무 부서)에 재제출해야 함.
- **아침 브리핑 상기 지침:** **2026년 9월 3일(목) 아침 일정 브리핑 시 필수 상기 항목으로 반드시 포함하여 사용자에게 안내할 것.**

## 62. 쿨메신저 첨부파일 자동 저장 설정 및 아침 브리핑 상기 규칙 (2026-09-02)
- **개요:** 쿨메신저 환경설정에서 '파일 수신 시 묻지 않고 자동으로 저장' 옵션 체크 안내.
- **설정 목적:** 선생님이 메신저를 직접 열람하지 않아도 수신 파일이 `쿨메신져 다운로드 파일` 폴더에 즉시 저장되도록 하여, 퇴근 후 원격(스마트폰/노트북)에서도 AI가 첨부파일 내용을 즉시 열람·분석할 수 있도록 환경 구축.
- **아침 브리핑 상기 지침:** **2026년 9월 3일(목) 아침 출근 일정 브리핑 시 필수 상기 항목으로 포함하여 사용자에게 안내할 것.**

## 63. 2학년 화법과 언어 시간표 맞교환 (이병의 ↔ 황요한) 및 주간 확정 시간표 갱신 (2026-09-03)
- **개요:** 2026년 9월 3일(목)부터 2학년 화법과 언어 수업 학급을 이병의 선생님과 상호 맞교환하여 진행함.
- **담당 학급 변경:**
  * **황요한 교사:** 기존 2학년 6~10반(206~210) ➔ **2학년 1~5반(201~205) 화법과 언어** (총 5시간)
  * **이병의 교사:** 기존 2학년 1~5반(201~205) ➔ **2학년 6~10반(206~210) 화법과 언어** (총 5시간)
- **황요한 교사 주간 수업 시간표 (총 16시간 - 3학년 11시간 + 2학년 5시간):**
  * **월요일 (3시간):** 2교시(310 심국), **4교시(205 화법)**, 5교시(306 심국) [1, 3, 6교시 공강]
  * **화요일 (3시간):** 3교시(302 심국), 5교시(309 심국), **7교시(204 화법)** [1, 2, 4, 6교시 공강]
  * **수요일 (2시간):** 1교시(308 심국), 5교시(303 심국) [2, 3, 4교시 공강]
  * **목요일 (5시간):** **1교시(202 화법)**, 2교시(305 심국), 4교시(304 A_교육), 5교시(301 심국), **6교시(203 화법)** [3, 7교시 공강]
  * **금요일 (3시간):** **1교시(201 화법)**, 2교시(307 심국), 5교시(304 심국) [3, 4, 6교시 공강]
- **3학년 기존 수업 충돌 여부:** 3학년 심화국어 10개 반 및 A_교육 1개 반과의 충돌 0건 (100% 공강 슬롯에 안착).

## 64. 해준이 등·하원 시트 매주 금요일 09:30 자동 작성 및 안전 검증 영구 규칙 (2026-09-03)
- **개요:** 매주 금요일 오전 09:30, 차주(다음 주 월~금) 해준이 등·하원 및 육아시간 관리 구글 시트를 이전 정보와 시간표를 종합 분석하여 자동 작성함.
- **수정 허용 영역 엄격 격리:**
  * **절대 수정 금지 (Read-Only):** 사모님(박지혜 선생님) 영역인 **Col D (등원 가능 여부 [박])** 및 **Col G (하원 가능 여부 [박])**은 어떠한 경우에도 덮어쓰거나 수정하지 않음.
  * **수정 허용 영역:** 황요한 선생님 영역인 **Col E (등원 가능 여부 [황])**, **Col H (하원 가능 여부 [황])**, **Col C (등원 담당)**, **Col F (하원 담당)**만 입력.
- **기재 원칙:**
  * **'O' 표시:** 정규 시간표(1교시 공강, 오후 공강), 당김수업 없음, 교내외 행사 없음 등 **확실하게 등·하원이 가능한 경우에만** 기재.
  * **'X' 표시:** 1교시 수업 있음, 6~8교시 수업 있음, 3학년 당김수업, AI 동행 프로젝트(월 14:35~17:35), 출장, 시험 감독 등으로 **완전히 불가능한 경우에만** 기재.
  * **빈칸 유지 및 사전 동의:** 애매하거나 일정(출장/회의/협의회 등)이 불확실한 경우에는 임의로 O/X를 적지 않고 빈칸으로 두며, 시트 작성 전 사용자에게 먼저 상황을 설명하고 동의를 구한 뒤 입력함.
- **종합 분석 데이터소스 4대 축:**
  1. 2학기 주간 확정시간표 (Rule 63: 2-1~5 화법 반영본)
  2. 3학년 시수 확보 계획 (당김수업 일정표)
  3. AI 동행 프로젝트(월 14:35~17:35), 출장/연수 공문, 시험 감독 등 학교 고유 일정
  4. 구글 캘린더 등록 일정


## 64. Windows 11 클립보드 단축키 (Ctrl + Alt + V) 백그라운드 리스너 상시 운영 (2026-09-03)
- **환경 및 증상:** Windows 11 24H2, 로지텍 K580 키보드 사용 시 물리 `Win + V` 입력이 교내 키보드 보안(TouchEn NxKey) 및 K580 OS 매핑에 의해 시작 메뉴로 오작동하는 현상.
- **해결책:** 전역 단축키 `Ctrl + Alt + V` (보조: `Ctrl + \`)로 Windows 11 클립보드 기록 창(`ms-inputapp:clipboard`)을 0.1초 만에 호출하는 Win32 RegisterHotKey 백그라운드 리스너(`scripts/clipboard_hotkey_listener.py`)를 구축.
- **자동 시작 영구 등록:** 윈도우 시작프로그램(`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Clipboard_Hotkey.vbs`)에 등록하여 재부팅 시에도 CPU 0% 무음 상시 대기.

## 65. 2027학년도 진해고등학교 신입생 입학설명회 54슬라이드 마스터 합본 구축 완료 (2026-09-03)
- **개요:** 제미나이 노트북(NotebookLM) × 바나나nl STYLE #317 [컨설팅] 스타일로 생성된 11개 묶음 PPTX 파일을 분석하여 식순 및 기획안 순서에 맞춰 완벽한 54슬라이드 16:9 와이드스크린 마스터 발표자료로 통합 구축 완료함.
- **11개 묶음 매핑 및 슬라이드 구성 (총 54장):**
  1. `The_Architecture_of_Potential.pptx` (S01~S05, 5장): 행사 오프닝, 학교 비전, 설명회 식순, 학교장 인사말, 학생회장 학교소개
  2. `Jinhae_High_School_Strategic_Briefing.pptx` (S06~S10, 5장): 진해고 5대 강점, 남학생 다수 인원 경쟁력, 5등급제 내신표, 2학년 과목개설 실측표
  3. `New_Admissions_Strategy.pptx` (S11~S15, 5장): 2028 대입 개편 3대 축, 수시/정시 구조 분석
  4. `Jinhae_High_Two-Track_Strategy.pptx` (S16~S20, 5장): 수시·정시 동시 대비 투트랙(Two-Track) 로드맵
  5. `Jinhae_High_School_Admission_Success (1).pptx` (S21~S25, 5장): 2026학년도 대입 진학 실적 전수 공개 (서울대 1, 의약학 5, 부산대 23, 경북대 15, 지역국립대 114명, 사관학교 8개년 44명)
  6. `Jinhea_High_Personalized_Admission_Success.pptx` (S26~S30, 5장): 중위권 내신역전 성공 사례 (세종대 3.12, 경북대 2.85)
  7. `Jinhae_High_Innovation.pptx` (S31~S35, 5장): 자율형 공립고 2.0 및 기숙사 24시간 생활 일과표
  8. `Jinhae_High_School_Growth_Blueprint.pptx` (S36~S40, 5장): 45개 창체 동아리 및 학교장 삼품제
  9. `Woongbi-gwan_Success_Architecture.pptx` (S41~S45, 5장): 기숙사(웅비관) 시설 및 선발 요강 (관내 5%/관외 30%)
  10. `2027_Jinhae_High_School_Curriculum_Blueprint.pptx` (S46~S50, 5장): 2027학년도 신입생 교육과정 편성표 및 학생 선택권
  11. `2027_Jinhae_High_School_Strategic_Blueprint.pptx` (S51~S54, 4장): 신입생 모집 전형 일정, 입학상담 AI 챗봇(jinhae-bot2) 안내, Q&A, 클로징
- **최종 저장 위치:**
  * 바탕화면: `D:\OneDrive - 경상남도교육청\바탕 화면\2027학년도_진해고등학교_신입생_입학설명회(최종합본).pptx` (27.44 MB)
  * 입학설명회 업무폴더: `D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\업무(장학금 및 입학홍보)\3. 홍보\입학설명회\2027학년도_진해고등학교_신입생_입학설명회(최종합본).pptx`

## 66. 2026년 9월 4일(금) 3교시 1학년 8반 대강(대체수업) 배정 및 금요일 시간표 갱신 (2026-09-03)
- **일시:** 2026년 9월 4일(금) 3교시 (10:40 ~ 11:30)
- **대상 학급:** 1학년 8반 (108)
- **내용:** 동료 교사 결보강 요청에 따른 3교시 1학년 8반 대강(대체수업) 입실.
- **수업 충돌 분석:**
  * 기존 금요일 시간표상 3교시는 **공강** 슬롯이었으므로 기존 수업과의 **충돌 0건 (100% 정상 입실 가능)**.
  * 9월 4일(금) 황요한 교사 확정 시간표 (총 4시간):
    - **1교시 (08:40~09:30):** 2학년 1반 화법과 언어 (201)
    - **2교시 (09:40~10:30):** 3학년 7반 심화국어 (307)
    - **3교시 (10:40~11:30):** **1학년 8반 대강(대체수업)** (108) ★신규
    - **4교시 (11:40~12:30):** 공강 (점심시간 연계)
    - **5교시 (13:20~14:10):** 3학년 4반 심화국어 (304)
    - **6, 7교시:** 공강 / 행정 연구 업무
  * ※ 1교시부터 3교시까지 연속 수업(2학년 ➔ 3학년 ➔ 1학년 교실 순차 이동)이 진행되므로 수업 준비 및 동선 안배 유의.
- **아침 브리핑 상기 지침:** **2026년 9월 4일(금) 내일 아침 출근 일정 브리핑 시 3교시 1학년 8반 대강 수업을 최우선 상기 항목으로 포함하여 안내할 것.**

## 67. 2026년 9월 4일(금) 동창회 장학금 수여식 날짜 확정 교장선생님 컨펌 및 아침 브리핑 상기 지침 (2026-09-03)
- **일시:** 2026년 9월 4일(금) 아침 출근 직후 (08:20 ~ 08:40)
- **대상:** 교장선생님
- **안건:** 총동창회 장학금 수여식 날짜를 언제로 픽스(Fix)할지 최종 일정 컨펌 및 결재 보고.
- **수여식 업무 참고 사항:**
  * 장학금 지급 방식: '글로컬 학우상 시상 및 장학금 지급' 관련 공문/기안 작성 시 장학금을 **'상품권'**으로 지급한다는 내용을 반드시 포함 (Rule 7 필수 준수).
  * 1학기 애향삼품 장학생 서류(추천서, 감사편지, 소심의위 협의록) 수합 완료분 연계.
- **아침 브리핑 필수 상기 지침:**
  * 2026년 9월 4일(금) 아침 출근 브리핑 시 다음 2대 핵심 항목을 최우선 안내할 것:
    1. **교장선생님 컨펌:** 동창회 장학금 수여식 날짜 확정(Fix) 보고.
    2. **3교시 대강 수업:** 10:40~11:30 1학년 8반(108호) 대강 입실.

## 66. 육아시간 기안 시 나이스(NEIS) 공식 시간표와 실제 수업 시간표의 이중 검증(Dual Verification) 영구 규칙 (2026-09-04)
- **개요:** 이병의 선생님과의 2학년 화법과 언어 시간표 변경은 나이스 공식 시간표 반영이 아닌 교사 간 상호 맞교환이므로, 나이스 결재선 상의 적법성(결재 반려 방지)과 실제 물리적 교실 입실 가능성을 동시에 충족해야 함.
- **판정 원칙:** 육아시간 신청 가능 교시 = **[나이스 공식 등록 시간표상 공강]** AND **[실제 담당 수업상 공강]**.
- **핵심 유의 교시 가이드라인:**
  1. **화요일 오전 (08:30~09:30):** 실제로는 2교시에 이병의T가 209반에 들어가시지만, 나이스 시스템에는 황요한T의 2교시 수업으로 잡혀 있음. 따라서 나이스 결재선에서 수업 결손 경고 및 반려를 원천 방지하기 위해 **반드시 1교시 공강 시간대인 `08:30 ~ 09:30` (1시간)으로만 기안**해야 함.
  2. **금요일 오전:** 나이스 공식 시간표는 1교시 공강이나, 실제로는 2-1반 화법 수업에 들어가야 하므로 오전 육아시간 신청 절대 불가.
  3. **목요일 오전:** 나이스 공식 시간표는 1교시 공강이나, 실제로는 2-2반 화법 수업에 들어가야 하므로 오전 육아시간 신청 절대 불가.
  4. **금요일 오후 (14:30~16:30):** 나이스 공식 시간표(5교시 후 공강)와 실제 수업 시간표(14:30 전체 종료)가 완벽히 일치하므로 2시간 조기퇴근 육아시간 기안 최적.
  5. **수요일 오후 (14:30~16:30):** 나이스 공식 시간표상 14:30 이후 정규 수업이 없어 결재 통과는 문제없으나, 8교시 당김수업(3-4 심국)의 실제 입실 여부를 사전에 해결/조율한 상태에서만 기안해야 함.

## 67. 수업 맞교환 및 대강 후보 검증 하네스(Harness) & 하위 에이전트 다각도 검증 영구 규칙 (2026-09-04)
- **개요:** 시간표 맞교환 또는 대강 후보를 도출하거나 시간표를 조정할 때, 반드시 정밀 검증 하네스(Verification Harness)를 구성하고 하위 에이전트(Subagent)를 가동하여 사용자가 미처 생각하지 못한 부분(Edge Cases)까지 사전에 다각도로 분석·검증하여 최종 반영함.
- **하네스 5대 필수 검증 축 (Assertion Checks):**
  1. **[이동수업 불변 검증]:** 색칠된 셀(선택과목 이동수업 군)은 1:1 맞교환 대상에서 원천 배제.
  2. **[교사 피로도 및 연강 한계]:** 대강/교환 대상 교사의 당일 총 수업 시수(5시간 초과 여부) 및 3~4연강 발생 여부 점검.
  3. **[시기별 특수 상황 검증]:** 수시 원서 접수 기간(3학년 담임 업무 폭증), 수행평가 기간, 학교 행사 등 시기별 교사 업무 부하 고려.
  4. **[나이스 전산 정합성]:** 나이스 등록 시간표 기준 대강신청서/수업결체 신청 시 시스템 반려 또는 결손 오류 발생 여부 교차 검증.
  5. **[대강 vs 맞교환 다각도 트레이드오프]:** 1:1 맞교환 시 향후 황요한 선생님의 보충 시수 부하 vs 대강 시 상대 교사의 부담 및 동교과/친소관계 다각도 비교.

## 68. 2026학년도 외부 공모/추천 장학금 개인 신청자 선발 결과 확인 이력 (2026-09-04)
- **개요:** 외부 재단에서 학생 개인 계좌로 직접 입금되는 장학 사업 3건에 대해 담임교사 확인을 거쳐 실제 선정 및 수혜 여부를 파악함.
- **확인 결과 및 명부 반영 기준:**
  1. **2학년 6반 김주영 (서한성 선생님 반):** 한국아이티융합협회 다문화 장학회 장학생 (4월 추천 건) ➔ **최종 미선정 (장학금 미수혜 확인)** ➔ 2026학년도 장학생 명부 등재 대상 제외 완료.
  2. **2학년 7반 박주빈 (정순영 선생님 반):** 2026년 상반기(1학기) 대한적십자사 헌혈기부권 나눔장학금 100만 원 ➔ **최종 미선정 (장학금 미수혜 확인)** ➔ 2026학년도 장학생 명부 등재 대상 제외 완료.
  3. **1학년 1반 김선유 (김정화 선생님 반):** 2026년 하반기(2학기) 대한적십자사 헌혈기부권 나눔장학금 100만 원 (8월 19일 추천 접수) ➔ **현재 대한적십자사 심사 진행 및 발표 대기 중**.
- **폴더별 증빙 보관:** 각 장학금 사업별 해당 폴더(2026년 다문화장학회 장학금 지원 사업 안내, 2026년 상반기 헌혈기부권 나눔장학사업 장학생 선발\1학기)에 선정_결과_확인_메모.txt로 관리 기록 저장 완료.


## 69. 애향삼품 장학금 기탁자 및 감사편지 우편물 발송처 지침 (2026-09-04)
- **개요**: 애향삼품 장학금 수혜 학생들의 감사편지 및 추천서 등 우편물 발송 시 필요한 공식 수취인 정보 및 주소 규칙.
- **기탁자 정보 (참고)**:
  * 성명: 이흥순 할머니
  * 원주소: 창원시 진해구 여좌동 90-22
  * 연락처: 010-8538-3080
- **실제 우편물 발송 수취처 (필수 적용)**:
  * 수취인: 조카며느리 **이경자 님**
  * 우편물 발송 주소: **창원시 진해구 천자로 386 마린푸르지오 아파트 111동 1901호**
  * 우편번호: **51628**
  * 연락처: **010-8538-3080**
- **행정 발송 원칙**:
  * 장학생들이 자필로 작성한 선발 감사편지 및 추천서 등 일체의 대외 발송 우편물은 여좌동 본가가 아닌 **조카며느리 이경자 님 댁(마린푸르지오)**으로 발송하여야 수령 및 전달이 정상적으로 이루어짐.


## 70. 2026년 9월 7일(월) 아침 브리핑 필수 상기 지침 (애향삼품 장학금 협의록 결재 확인 및 발전기금 지급 기안) (2026-09-04)
- **개요**: 2026년 9월 4일(금) 상신한 애향삼품 장학생 선발 심의위원회 협의록 기안이 결재 진행 중이므로, 다음 주 월요일(9월 7일) 아침 일정 브리핑 시 다음 3대 후속 행정 절차를 필수 상기 항목으로 포함하여 안내할 것.
- **월요일 필수 브리핑 체크리스트**:
  1. **애향삼품 장학생 선발 심의위원회 협의록 결재 확인**:
     * 학교장 결재 완료 여부 확인 및 K-에듀파인 시행 공문 번호(진해고등학교-XXXXX) 확인.
  2. **2026학년도 1학기 애향삼품 장학금 지급 기안 상신 (발전기금 지출품의 연계)**:
     * 1단계에서 확인한 공문 번호를 본문 1번 관련에 기입.
     * K-에듀파인 [발전기금회계] -> [지출품의]에서 '2026학년도 1학기 애향삼품 장학금 지급(3,200,000원)' 품의 연계.
     * 대상: 4명 (김지호, 정서윤, 정하윤, 윤영 / 1인당 80만 원, 총 320만 원).
     * 결재선 협조자: **행정실 발전기금 담당 주무관, 행정실장** 필수 지정.
     * 기안문 HWP/PDF: 바탕 화면 및 애향삼품 폴더에 이미 완비되어 있음.
  3. **장학생 감사편지 및 추천서 우편 발송 준비**:
     * 수취인: 조카며느리 **이경자 님** 귀하 (창원시 진해구 천자로 386 마린푸르지오 111-1901, 우편번호 51628, ☎ 010-8538-3080).
     * 봉투 출력 라벨: 바탕 화면 애향삼품 장학금 감사편지 우편발송 라벨.hwp 활용.
  4. **진해고 동창회 장학금 수여식 일정 교장선생님 컨펌**:
     * 교장선생님께 9월 21일(월) 6교시 홈베이스 수여식 확정 구두 보고.
  5. **행정실장님 교직원 밴드 축제 공연 제안 (일렉 기타 & 통기타 합주)**:
     * 행정실장님(일렉 기타 연주)께 이번 교내 축제 때 황요한 선생님(통기타)과 함께 밴드 공연을 함께하자는 제안 드리기.
     * 애향삼품 장학금 발전기금 지출품의 협조 결재 또는 월요일 차담 시 자연스럽게 제안 및 곡/편성 의논.


## 71. 교내 축제 교직원 밴드 공연 기획 (행정실장님 일렉 기타 & 황요한 선생님 통기타 합주) (2026-09-04)
- **개요:** 교내 축제 무대에서 행정실장님과 함께하는 교직원 밴드 공연을 추진하기 위한 기획 메모 및 알림 지침.
- **악기 편성 및 참여자:**
  * **행정실장님:** 일렉 기타 (Electric Guitar)
  * **황요한 선생님:** 통기타 (Acoustic Guitar)
  * (추후 드럼, 베이스, 건반, 보컬 등 추가 멤버 섭외 확장 가능)
- **추진 방향 및 알림 지침:**
  * 2026년 9월 7일(월) 출근 아침 브리핑 시 필수 상기 항목으로 포함하여 리마인드.
  * 행정실 발전기금 지출품의 협조 결재 논의 또는 차담 시 편안하고 유쾌한 분위기에서 축제 무대 합주 제안을 드릴 수 있도록 조력.

