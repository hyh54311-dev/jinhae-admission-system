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
  4. **010-3622-1564**
     * **상담 내용:** 입학 관련 일반 상담 접수.
  5. **010-2981-8077**
     * **출신/내신:** 출신 중학교 미공개, 의대 진학 희망 최상위권 추정.
     * **고민 사항:** 의대 진학률/실적, 기숙사 선발 규정 및 환경, **[핵심] 기숙사에 들어가지 않아도 기숙사생 대상 개설 수업이나 프로그램에 참여할 수 있는지 여부**.
     * **상담 대응 전략:** **기숙사 정독실(면학실)과 개인 침실을 제외한 기숙사생 대상 대부분의 심화 학습/특색 프로그램에 통학생도 100% 동일하게 참여 가능**함을 명쾌하게 안내, 2026학년도 의예과 3명 등 실적 및 10.22(목) 18:30 입학설명회 참석 안내.

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



## 72. 진해고 총동창회 장학증서 수여식 날짜 확정(9월 21일 월요일 6교시) 및 수여 대상(최신 2학기 장학생 6명) 한정 지침 (2026-09-05)
- **개요**: 진해고등학교 총동창회장님과의 일정 조율 결과, **2026년 9월 21일(월)**에 참석이 가능하시다는 회신을 확인함. 이번 수여식은 1학기 선발자가 아닌 **가장 최근(8월 26일 심의·추천)에 올린 2학기 총동창회 장학생 6명만을 단독 대상**으로 진행함.
- **수여 대상 장학생 (최신 2학기 선발 6명 전원)**:
  * **2학년 (3명)**: 이성민(2-5), 서용준(2-3), 김동희(2-4)
  * **3학년 (3명)**: 박형주(3-1), 김도윤(3-8), 고규원(3-9)
  * *(장학 금액: 1인당 50만 원, 총 3,000,000원)*
- **수여식 확정 추진 안**:
  * **일시**: **2026년 9월 21일(월) 6교시** (장학담당 황요한 교사 월요일 6교시 공강 시간대로 완벽 일치)
  * **장소**: **본관 1층 홈베이스** (사전 쿨메신저 점검 완료, 사용 가능)
  * **참석 대상**: 총동창회장님, 교장, 교감, 교무기획부장, 장학담당 교사(황요한), 2학기 수혜 장학생 6명
- **2026년 9월 7일(월) 아침 교장선생님 보고 지침**:
  * **보고 요지**: "교장선생님, 출장 잘 다녀오셨습니까. 총동창회 장학증서 수여식 관련하여 총동창회장님과 일정을 조율한 결과, 9월 21일(월)에 참석이 가능하시다고 연락을 받았습니다. 이에 따라 **가장 최근에 추천 올린 2학기 장학생 6명**을 대상으로 **9월 21일(월) 6교시 본관 1층 홈베이스**에서 수여식을 진행하고자 하는데, 교장선생님 일정과 학교 일정상 이렇게 추진해도 괜찮으실지 여쭙고자 합니다."
  * **컨펌 후 후속 조치**: 교장선생님 최종 재가 후 총동창회 사무간사님께 확정 일자 통보, 수혜 학생 6명 및 해당 학급 담임교사에게 수여식 참석 안내, 수여식 세부 식순 및 시나리오 준비.


## 73. 2026학년도 2학기 1차 지필평가 출제 유의사항, 과목코드 및 시험원안 표준 지침 (2026-09-07)
- **개요:** 2026학년도 2학기 1차 지필평가(중간고사) 시험원안 출제, 이원목적분류표(문항정보표), 서·논술형 답안지 및 채점기준표 작성, 나이스 추정분할점수 산출에 관한 진해고등학교 공식 지침 총괄 요약입니다.
- **원본 폴더:** `D:\OneDrive - 경상남도교육청\바탕 화면\1-3. 2학기 1차 시험 원안 양식`
- **핵심 2학기 과목코드 (국어과 중심)**:
  * **1학년:** `공통국어2` ➔ **01** (공통수학2: 02, 공통영어2: 03, 한국사2: 04, 통합사회2: 05, 통합과학2: 06)
  * **2학년:** **`화법과 언어` ➔ 01** (문학과 영상: 02, 미적분Ⅰ: 03, 기하: 04, 경제 수학: 05, 영어Ⅱ: 06)
  * **3학년:** **`심화 국어` ➔ 01** (심화 수학Ⅰ: 02, 심화 수학Ⅱ: 03, 인공지능 수학: 04, 심화 영어 독해Ⅰ: 05)
- **시험원안 작성 5대 필수 서식 규칙**:
  1. **과목명 정식 표기:** 교육과정에 명시된 과목명 그대로 기재 (예: '화법과 언어' O, '화언' X).
  2. **100점 만점 및 역배점 금지:** 총점은 반드시 100점 만점이어야 하며, 문항 수준(난이도)이 높은 문항에 높은 배점을 부여하고 난이도 낮은 문항에 높은 점수를 주는 **역배점 절대 금지**.
  3. **문항별 배점 표기:** 문제지 문항 끝에 한 칸 띄우고 `... 한 것은? [3.2점]` 형식으로 명시. 배점만 다음 줄로 넘어갈 경우 행 오른쪽 끝에 배치.
  4. **쪽수 및 머리말 표기:** `진해고등학교 2학기 1차 시험 2학년 화법과 언어 총 O쪽 중 O쪽` 형식 준수.
  5. **전체 문항수 및 배점 구분:** 표두에 `선택형 ( )문항 (00점), 서·논술형 ( )문항 (00점), 총점 100점` 명확히 구분 기재.
- **출제 및 보안 7대 엄격 수칙 (감사 지적 및 재시험 방지)**:
  1. **기출문제 및 시판 참고서 전재 금지:** 인근 학원 DB화 및 저작권·공정성 문제로 기출문제 및 시판 문제집 문제 그대로 전재 또는 단순 변형 출제 절대 금지.
  2. **수업 미지도 내용 출제 금지:** 수업 중 가르치지 않은 내용 출제 금지. 학급별 진도 격차 없도록 사전 조율.
  3. ★ **평가 전 문항 외부 AI 입력 금지:** 평가 전 평가 문항 관련 정보를 SNS에 게시하거나 **ChatGPT 등 생성형 AI에 입력·점검하는 행위 일체 금지 (보안 유출 위험)**.
  4. **종교·정치적 중립성:** 특정 종교나 정치적 편향성을 띤 문항 출제 엄금.
  5. **동일 교과 교차 검토:** 동일 학년/교과 교사가 1인인 경우, 타 학년 동일 교과 교사와 교차 검토 의무화.
  6. **오류 문항 임의 처리 금지:** 출제 오류 발생 시 교사 임의로 삭제/무효 처리 불가하며, 학업성적관리위원회 심의 및 공식 이의신청 절차를 거쳐야 함.
- **발문 및 문법 표기 정밀 원칙**:
  * **부정형 발문:** 밑줄 표기 필수 ➔ `... 하지 <u>않은</u> 것은?`, `... 적절하지 <u>않은</u> 것은?`
  * **품사별 올바른 용언 표기:**
    - 형용사 '알맞다' ➔ `알맞지 <u>않은</u> 것은?` ('알맞지 않는' X)
    - 동사 '맞다' ➔ `맞지 <u>않는</u> 것은?` ('맞지 않은' X)
  * **합답형 문두:** 선지 구성 항목 수가 다를 때 ➔ `<보기>에서 옳은 것만을 <u>있는 대로</u> 고른 것은?`
  * **기호 사용 표준:**
    - 학생 선택 요구 항목: `ㄱ, ㄴ, ㄷ, ㄹ`
    - 단순 내용 제시/불릿: `◎`, `•`
    - 밑줄 구절/단어 지칭: `㉠, ㉡, ㉢`
    - 그림 특정 부위: `A, B, C`
    - 표 내부 항목: `(가), (나), (다)`
  * **세트 문항:** `[1~2] 다음 글을 읽고 물음에 답하시오.` (대괄호 + 두루높임체 + 굵은 글꼴).
- **서·논술형 답안지 및 채점기준표 양식 규격**:
  * **답안지 3종 양식:** 인쇄 및 제본 방식에 따라 `단면`, `양면(상철)`, `양면(좌철)` 중 선택 사용.
  * **채점기준표 필수 항목:** 문항별 정답, 배점, 유사 정답 인정 범위, 부분점수 부여 기준(단계별 득점 요건 및 구체적 감점 기준) 필수 명시.
- **나이스(NEIS) 추정분할점수 산출 공식 절차**:
  * **경로:** `교과담임 ➔ 정기시험 ➔ 문항정보표관리 ➔ 조회 ➔ 내용영역, 성취기준, 난이도, 배점, 정답 입력 ➔ 저장 ➔ 마감(신중) ➔ 정기시험분할점수산정 ➔ 라운드별 점수 조정 ➔ 최종 입력마감`.


## 74. 황요한 교사 1학기 2차고사(기말고사) 문학 출제 및 거둠자료 분석 표준 (2026-09-07)
- **개요:** 2026학년도 1학기 2차 지필평가(기말고사) 2학년 문학 과목에서 황요한 교사가 직접 출제 및 제출했던 나이스 문항정보표, 서·논술형 채점기준표, 지필평가 원안, 학생 답안지 4종 거둠자료 정밀 분석 기록입니다.
- **보관 폴더:** `D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 거둠작업\2학년 1학기고사\기말고사\2학년(황요한)`
- **출제 기본 체계**:
  * **과목명 및 코드:** `문학(01)_일반` (코드: **01**)
  * **공동 출제 교사:** 강지영, 강필성, 이병의, **황요한** (4인 공동 출제)
  * **전체 배점 구조:** 총점 100점 만점 / 총 24문항 (선택형 18문항 55점 + 서답형 6문항 45점)
  * **서답형 공통 감점 조건 (표준 원칙):**
    1. 완결된 문장 형식(~다.)을 갖추지 않은 경우: **1점 감점**
    2. 핵심어가 맞춤법에 어긋난 경우: **1점 감점**
- **황요한 교사 전담 출제 문항 및 심층 분석**:
  1. **선택형 13번 (3.8점 / 난이도: 어려움 / 정답: ④):**
     - 지문: 이범선, 「오발탄」
     - 발문: 철호가 치과에서 사랑니/충치를 한목에 다 뽑아달라고 고집하는 행위의 상징적 의미 파악.
     - 정답 취지: 가혹한 전후 현실에 굴복하는 무기력함과 자기 파괴적인 심리 표출 분석.
  2. **선택형 14번 (2.7점 / 난이도: 쉬움 / 정답: ②):**
     - 지문: 이범선, 「오발탄」
     - 발문: 학생들의 조별 발표 요약 내용 중 적절하지 않은 것 (배경, 오발탄의 의미, 비판적 리얼리즘, 상이군인의 현실, 결말의 의미).
     - 오답 선지: 오발탄의 의미가 '병원'의 모습을 뜻한다는 설명은 부적절.
  3. **서술형 5번 (총 8점 / 난이도: 보통 / 5-1 4점 + 5-2 4점):**
     - 발문: 등장인물이 처한 상황을 고려하여 "가자"가 가지는 상징적 의미를 각각 30자 이내(띄어쓰기 제외)로 서술.
     - **5-1 어머니의 "가자" (4점):** 고향(전쟁 전의 평화로운 삶/과거)으로 돌아가고 싶다는 절규이자 비극적 현실을 부정하려는 심리 상태 표출.
     - **5-2 철호/영호의 "가자" (4점):** 삶의 방향성을 잃어버린 절망과 좌절, 고통스러운 현실에서 벗어나고 싶다는 절박한 심리 상태의 표출.
     - **세부 채점/감점 기준:**
       * 의미가 통하는 경우 정답 인정.
       * 글자 수 30자 초과 시(한글 기준, 띄어쓰기 제외): **각 1점 감점**.
       * 종결어미 '~다.' 누락 시: **1점 감점**.
  4. **선택형 15번 (2.3점 / 난이도: 쉬움 / 정답: ④):**
     - 지문: 최두석 「대설주의보」 & 황지우 「새들도 세상을 뜨는구나」
     - 발문: 권력의 공간화 양상 비교 (공간의 성격, 억압의 주체, 시대적 알레고리 비교표 분석).
- **출제 시사점 및 2학기 화법과 언어 적용 지침**:
  * 지문과 문항을 유기적으로 결합하여 세트화([13~14, 서술형 5])하는 수능형 문항 배치 선호.
  * 서술형 채점 기준 시 '핵심 키워드', '글자 수 제한', '문장 완결성(~다.)', '유사 정답 인정 범위'를 명문화하여 채점 분쟁 사전 차단.
  * 역배점 금지 원칙 철저 준수 (13번 난이도 '어려움'에 3.8점 고배점, 14·15번 '쉬움'에 2.7점, 2.3점 저배점 안배).

## 75. 2026학년도 2학기 9월 9일(수) 오후 특별 일과 운영 및 황요한 교사 수업·마감 일정 (2026-09-07)
- **개요:** 2026년 9월 9일(수) 1·2학년 대학 학과 체험 행사 및 3학년 진로탐구활동 실시에 따라 오후 일과 시간이 변동 운영됨.
- **9/9(수) 특별 일과 운영 시간표:**
  * **6교시:** 14:35 ~ 15:25 (※ 6교시와 7교시 사이 쉬는 시간 없이 연강 운영)
  * **7교시:** 15:25 ~ 16:15
  * **청소시간:** 16:15 ~ 16:30 (15분간)
  * **8교시:** 16:40 ~ 17:30 (50분간)
- **황요한 교사 핵심 일정 및 유의사항:**
  1. **6~7교시 (14:35~16:15):** 1·2학년 대학 학과 체험(1학년 계명대, 2학년 동아대) 시 황요한 교사는 배정된 강좌 없음(공강/연구실 교무 행정 및 시험 출제 집중). 3학년은 쉬는 시간 없이 6·7교시 연강으로 진로탐구활동 진행됨.
  2. **8교시 당김수업 (16:40~17:30):** 3학년 4반 심화국어 (수능 후 11/27 금요일 5교시분 당김). 기존 15:30이 아닌 **16:40**에 시작하므로 시간 착오 없도록 유의.
  3. **공문 발송 마감 (16:30까지):** 경남과고 면접문항 검토교사 추천 공문 발송 마감이 16:30이므로, 8교시 수업(16:40 시작) 들어가기 전인 청소시간(16:15~16:30) 이전에 최종 결재 및 발송을 마쳐야 함.
  4. **2학년 문법 중간고사 출제 마감:** 9월 9일(수)까지 본인 출제 문항 완성 및 동료 교사 출제본 취합 후 B4 마스터 시험지 편집 총괄 진행.

## 76. 2026학년도 2학기 진해고 교원 인사 변동 및 챗봇 기숙사 운영 규정 갱신 (2026-09-07)
- **교원 인사 현황 (2026-09-01 자):**
  * **교장:** 오길환 교장 선생님
  * **교감:** **손세민** 교감 선생님 (※ 2026년 9월 1일 자로 손세민 교감 선생님 부임/변경 완료)
  * **챗봇 지식 베이스 탑재 원칙:** 교장 및 교감 선생님 성함은 챗봇 지식 베이스(`knowledge.txt`)에 일체 등재하지 않으며, 관련 문의 시 교무실(055-546-2260)로 안내하는 보안 원칙 유지.
- **기숙사(송학관/동백관) 학기별 선발 및 유지 규정:**
  * **1학년 1학기 (신입생):** **중학교 내신 성적(석차백분율)** 100% 기준 선발 (진해 관내 5% 이내, 관외 30% 이내 우선 선발 쿼터).
  * **1학년 2학기 이후 (재학생):** **직전(전) 학기 고교 내신 성적 + 전국연합학력평가(모의고사) 성적**을 합산하여 정기 선발.
- **기숙사 시설 리모델링 계획 방침:**
  * 현재 기숙사 리모델링 계획은 수립되어 있지 않음.
  * 향후 대대적인 시설 리모델링이나 환경 개선 사업 추진 시 **학교 누리집(홈페이지) 공지사항에 게시**하고, **학생 및 학부모님께 가정통신문 등을 통해 별도로 상세 안내**함.


## 76. 황요한 교사 나이스(NEIS) 개인번호 영구 등록 (2026-09-07)
- **교원 성명:** 황요한 (진해고등학교 교사)
- **나이스(NEIS) 개인번호:** S101087780
- **설명:** 황요한 선생님의 나이스(NEIS) 교원 개인번호 정보입니다. 지필평가 문항정보표 등록, 분할점수 산출, 학교생활기록부 세특 및 출결 마감, 연수 및 교원인사 행정 서식 처리 등 나이스 전산 및 교무 행정 업무 처리 시 즉각 조회하여 활용할 수 있도록 영구 메모리에 기록함.

## 77. 2026년 9월 8일(화) 아침 브리핑 필수 상기 지침 (애향삼품 행정실 정미정 계장님 집행 & 감사편지 우편 발송) (2026-09-07)
- **개요:** 2026년 9월 8일(화) 출근 직후 황요한 선생님께 브리핑드릴 때 반드시 포함해야 할 애향삼품 2대 마감 업무.
- **아침 필수 브리핑 항목:**
  1. **행정실 정미정 계장님께 애향삼품 장학금 지급 집행 요청:**
     * 기안문 「2026학년도 1학기 애향삼품 장학금 지급」 결재 완료 확인.
     * 행정실 정미정 계장님(발전기금/지출 담당)께 발전기금 통장에서 장학생 4명 계좌로 입금 집행 요청:
       - 2-4 김지호 (800,000원)
       - 2-6 정서윤 (800,000원)
       - 3-6 정하윤 (800,000원)
       - 3-8 윤영 (800,000원) / 총 3,200,000원
  2. **기탁자 댁 감사편지 및 추천서 우편(등기) 발송:**
     * 동봉 서류: 장학생 4명의 자필 감사편지 4부 + 담임교사 추천서 4부 (총 8쪽 원본/출력본).
     * 봉투 라벨: 바탕화면 애향삼품 장학금 감사편지 우편발송 라벨.hwp 출력 후 대봉투 부착.
     * 수취인: 조카며느리 **이경자 님 귀하** (창원시 진해구 천자로 386 마린푸르지오 111동 1901호, 우편번호 51628, ☎ 010-8538-3080).
     * 팁: 행정실 정미정 계장님께 장학금 입금 요청 시 행정실 우편 발송함에 함께 전달하면 원스톱 처리 가능.
  3. **업무용 컴퓨터에서 주간 대입 알리미 v4.1 클로드 최종 재검증 및 가동 완료:**
     * **사유:** 9월 7일 밤 원격 접속 환경의 가상 데스크톱 마우스 락 제약으로 미뤄둔 클로드 최종 검토 작업을 학교 업무용 PC에서 원클릭 완료.
     * **실행 절차:** 학교 업무용 PC에서 클로드 대화창을 열고 다음 한 줄 입력:
        `admission_v40_review/입시봇_v41_최종검증_의뢰서.md 파일을 읽고 최종 재검증해줘`
     * **후속 조치:** 클로드의 최종 승인 확인 후, 실전 발송 테스트(python admission_news.py run_now) 또는 매주 수요일 11:00 정기 스케줄 무인 자동화 상태 확인.

## 78. 주간 대입 입시 알리미 v4.1 멀티에이전트 오케스트레이션 개편 및 클로드 3중 정밀 감사 완결 (2026-09-08)
- **개요:** 주간 대입 입시 정보 큐레이션 및 팩트 알리미(`admission_news.py`)를 5단계 멀티에이전트 시스템(리서처 -> 병렬 감사관 2A/2B -> 내용 검토관 -> 레이아웃 에디터 -> 구글 드라이브 퍼블리셔 -> 텔레그램 카드 전송관)으로 전면 개편하고, 클로드 독립 3중 감사를 통해 P0 2건, P1 7건, P2 8건, F 3건, G 1건을 100% 완벽 해결함.
- **핵심 기술 조치 및 보안 확립**:
  1. **보안 및 인증 (P0-1, P0-2, G-1):** 소스 내 텔레그램 토큰 평문 하드코딩 완전 삭제(`.env` 일원화), `verify=False` 및 `CERT_NONE` 영구 퇴출. Python 3.10+ 공식 표준 `truststore`(`truststore.inject_into_ssl()`)를 적용하여 Windows OS 공식 인증서 저장소(스쿨넷 루트 CA 포함)와 직결, 무결한 TLS 검증 달성.
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



## 72. 진해고 총동창회 장학증서 수여식 날짜 확정(9월 21일 월요일 6교시) 및 수여 대상(최신 2학기 장학생 6명) 한정 지침 (2026-09-05)
- **개요**: 진해고등학교 총동창회장님과의 일정 조율 결과, **2026년 9월 21일(월)**에 참석이 가능하시다는 회신을 확인함. 이번 수여식은 1학기 선발자가 아닌 **가장 최근(8월 26일 심의·추천)에 올린 2학기 총동창회 장학생 6명만을 단독 대상**으로 진행함.
- **수여 대상 장학생 (최신 2학기 선발 6명 전원)**:
  * **2학년 (3명)**: 이성민(2-5), 서용준(2-3), 김동희(2-4)
  * **3학년 (3명)**: 박형주(3-1), 김도윤(3-8), 고규원(3-9)
  * *(장학 금액: 1인당 50만 원, 총 3,000,000원)*
- **수여식 확정 추진 안**:
  * **일시**: **2026년 9월 21일(월) 6교시** (장학담당 황요한 교사 월요일 6교시 공강 시간대로 완벽 일치)
  * **장소**: **본관 1층 홈베이스** (사전 쿨메신저 점검 완료, 사용 가능)
  * **참석 대상**: 총동창회장님, 교장, 교감, 교무기획부장, 장학담당 교사(황요한), 2학기 수혜 장학생 6명
- **2026년 9월 7일(월) 아침 교장선생님 보고 지침**:
  * **보고 요지**: "교장선생님, 출장 잘 다녀오셨습니까. 총동창회 장학증서 수여식 관련하여 총동창회장님과 일정을 조율한 결과, 9월 21일(월)에 참석이 가능하시다고 연락을 받았습니다. 이에 따라 **가장 최근에 추천 올린 2학기 장학생 6명**을 대상으로 **9월 21일(월) 6교시 본관 1층 홈베이스**에서 수여식을 진행하고자 하는데, 교장선생님 일정과 학교 일정상 이렇게 추진해도 괜찮으실지 여쭙고자 합니다."
  * **컨펌 후 후속 조치**: 교장선생님 최종 재가 후 총동창회 사무간사님께 확정 일자 통보, 수혜 학생 6명 및 해당 학급 담임교사에게 수여식 참석 안내, 수여식 세부 식순 및 시나리오 준비.


## 73. 2026학년도 2학기 1차 지필평가 출제 유의사항, 과목코드 및 시험원안 표준 지침 (2026-09-07)
- **개요:** 2026학년도 2학기 1차 지필평가(중간고사) 시험원안 출제, 이원목적분류표(문항정보표), 서·논술형 답안지 및 채점기준표 작성, 나이스 추정분할점수 산출에 관한 진해고등학교 공식 지침 총괄 요약입니다.
- **원본 폴더:** `D:\OneDrive - 경상남도교육청\바탕 화면\1-3. 2학기 1차 시험 원안 양식`
- **핵심 2학기 과목코드 (국어과 중심)**:
  * **1학년:** `공통국어2` ➔ **01** (공통수학2: 02, 공통영어2: 03, 한국사2: 04, 통합사회2: 05, 통합과학2: 06)
  * **2학년:** **`화법과 언어` ➔ 01** (문학과 영상: 02, 미적분Ⅰ: 03, 기하: 04, 경제 수학: 05, 영어Ⅱ: 06)
  * **3학년:** **`심화 국어` ➔ 01** (심화 수학Ⅰ: 02, 심화 수학Ⅱ: 03, 인공지능 수학: 04, 심화 영어 독해Ⅰ: 05)
- **시험원안 작성 5대 필수 서식 규칙**:
  1. **과목명 정식 표기:** 교육과정에 명시된 과목명 그대로 기재 (예: '화법과 언어' O, '화언' X).
  2. **100점 만점 및 역배점 금지:** 총점은 반드시 100점 만점이어야 하며, 문항 수준(난이도)이 높은 문항에 높은 배점을 부여하고 난이도 낮은 문항에 높은 점수를 주는 **역배점 절대 금지**.
  3. **문항별 배점 표기:** 문제지 문항 끝에 한 칸 띄우고 `... 한 것은? [3.2점]` 형식으로 명시. 배점만 다음 줄로 넘어갈 경우 행 오른쪽 끝에 배치.
  4. **쪽수 및 머리말 표기:** `진해고등학교 2학기 1차 시험 2학년 화법과 언어 총 O쪽 중 O쪽` 형식 준수.
  5. **전체 문항수 및 배점 구분:** 표두에 `선택형 ( )문항 (00점), 서·논술형 ( )문항 (00점), 총점 100점` 명확히 구분 기재.
- **출제 및 보안 7대 엄격 수칙 (감사 지적 및 재시험 방지)**:
  1. **기출문제 및 시판 참고서 전재 금지:** 인근 학원 DB화 및 저작권·공정성 문제로 기출문제 및 시판 문제집 문제 그대로 전재 또는 단순 변형 출제 절대 금지.
  2. **수업 미지도 내용 출제 금지:** 수업 중 가르치지 않은 내용 출제 금지. 학급별 진도 격차 없도록 사전 조율.
  3. ★ **평가 전 문항 외부 AI 입력 금지:** 평가 전 평가 문항 관련 정보를 SNS에 게시하거나 **ChatGPT 등 생성형 AI에 입력·점검하는 행위 일체 금지 (보안 유출 위험)**.
  4. **종교·정치적 중립성:** 특정 종교나 정치적 편향성을 띤 문항 출제 엄금.
  5. **동일 교과 교차 검토:** 동일 학년/교과 교사가 1인인 경우, 타 학년 동일 교과 교사와 교차 검토 의무화.
  6. **오류 문항 임의 처리 금지:** 출제 오류 발생 시 교사 임의로 삭제/무효 처리 불가하며, 학업성적관리위원회 심의 및 공식 이의신청 절차를 거쳐야 함.
- **발문 및 문법 표기 정밀 원칙**:
  * **부정형 발문:** 밑줄 표기 필수 ➔ `... 하지 <u>않은</u> 것은?`, `... 적절하지 <u>않은</u> 것은?`
  * **품사별 올바른 용언 표기:**
    - 형용사 '알맞다' ➔ `알맞지 <u>않은</u> 것은?` ('알맞지 않는' X)
    - 동사 '맞다' ➔ `맞지 <u>않는</u> 것은?` ('맞지 않은' X)
  * **합답형 문두:** 선지 구성 항목 수가 다를 때 ➔ `<보기>에서 옳은 것만을 <u>있는 대로</u> 고른 것은?`
  * **기호 사용 표준:**
    - 학생 선택 요구 항목: `ㄱ, ㄴ, ㄷ, ㄹ`
    - 단순 내용 제시/불릿: `◎`, `•`
    - 밑줄 구절/단어 지칭: `㉠, ㉡, ㉢`
    - 그림 특정 부위: `A, B, C`
    - 표 내부 항목: `(가), (나), (다)`
  * **세트 문항:** `[1~2] 다음 글을 읽고 물음에 답하시오.` (대괄호 + 두루높임체 + 굵은 글꼴).
- **서·논술형 답안지 및 채점기준표 양식 규격**:
  * **답안지 3종 양식:** 인쇄 및 제본 방식에 따라 `단면`, `양면(상철)`, `양면(좌철)` 중 선택 사용.
  * **채점기준표 필수 항목:** 문항별 정답, 배점, 유사 정답 인정 범위, 부분점수 부여 기준(단계별 득점 요건 및 구체적 감점 기준) 필수 명시.
- **나이스(NEIS) 추정분할점수 산출 공식 절차**:
  * **경로:** `교과담임 ➔ 정기시험 ➔ 문항정보표관리 ➔ 조회 ➔ 내용영역, 성취기준, 난이도, 배점, 정답 입력 ➔ 저장 ➔ 마감(신중) ➔ 정기시험분할점수산정 ➔ 라운드별 점수 조정 ➔ 최종 입력마감`.


## 74. 황요한 교사 1학기 2차고사(기말고사) 문학 출제 및 거둠자료 분석 표준 (2026-09-07)
- **개요:** 2026학년도 1학기 2차 지필평가(기말고사) 2학년 문학 과목에서 황요한 교사가 직접 출제 및 제출했던 나이스 문항정보표, 서·논술형 채점기준표, 지필평가 원안, 학생 답안지 4종 거둠자료 정밀 분석 기록입니다.
- **보관 폴더:** `D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\수업\2026학년도 거둠작업\2학년 1학기고사\기말고사\2학년(황요한)`
- **출제 기본 체계**:
  * **과목명 및 코드:** `문학(01)_일반` (코드: **01**)
  * **공동 출제 교사:** 강지영, 강필성, 이병의, **황요한** (4인 공동 출제)
  * **전체 배점 구조:** 총점 100점 만점 / 총 24문항 (선택형 18문항 55점 + 서답형 6문항 45점)
  * **서답형 공통 감점 조건 (표준 원칙):**
    1. 완결된 문장 형식(~다.)을 갖추지 않은 경우: **1점 감점**
    2. 핵심어가 맞춤법에 어긋난 경우: **1점 감점**
- **황요한 교사 전담 출제 문항 및 심층 분석**:
  1. **선택형 13번 (3.8점 / 난이도: 어려움 / 정답: ④):**
     - 지문: 이범선, 「오발탄」
     - 발문: 철호가 치과에서 사랑니/충치를 한목에 다 뽑아달라고 고집하는 행위의 상징적 의미 파악.
     - 정답 취지: 가혹한 전후 현실에 굴복하는 무기력함과 자기 파괴적인 심리 표출 분석.
  2. **선택형 14번 (2.7점 / 난이도: 쉬움 / 정답: ②):**
     - 지문: 이범선, 「오발탄」
     - 발문: 학생들의 조별 발표 요약 내용 중 적절하지 않은 것 (배경, 오발탄의 의미, 비판적 리얼리즘, 상이군인의 현실, 결말의 의미).
     - 오답 선지: 오발탄의 의미가 '병원'의 모습을 뜻한다는 설명은 부적절.
  3. **서술형 5번 (총 8점 / 난이도: 보통 / 5-1 4점 + 5-2 4점):**
     - 발문: 등장인물이 처한 상황을 고려하여 "가자"가 가지는 상징적 의미를 각각 30자 이내(띄어쓰기 제외)로 서술.
     - **5-1 어머니의 "가자" (4점):** 고향(전쟁 전의 평화로운 삶/과거)으로 돌아가고 싶다는 절규이자 비극적 현실을 부정하려는 심리 상태 표출.
     - **5-2 철호/영호의 "가자" (4점):** 삶의 방향성을 잃어버린 절망과 좌절, 고통스러운 현실에서 벗어나고 싶다는 절박한 심리 상태의 표출.
     - **세부 채점/감점 기준:**
       * 의미가 통하는 경우 정답 인정.
       * 글자 수 30자 초과 시(한글 기준, 띄어쓰기 제외): **각 1점 감점**.
       * 종결어미 '~다.' 누락 시: **1점 감점**.
  4. **선택형 15번 (2.3점 / 난이도: 쉬움 / 정답: ④):**
     - 지문: 최두석 「대설주의보」 & 황지우 「새들도 세상을 뜨는구나」
     - 발문: 권력의 공간화 양상 비교 (공간의 성격, 억압의 주체, 시대적 알레고리 비교표 분석).
- **출제 시사점 및 2학기 화법과 언어 적용 지침**:
  * 지문과 문항을 유기적으로 결합하여 세트화([13~14, 서술형 5])하는 수능형 문항 배치 선호.
  * 서술형 채점 기준 시 '핵심 키워드', '글자 수 제한', '문장 완결성(~다.)', '유사 정답 인정 범위'를 명문화하여 채점 분쟁 사전 차단.
  * 역배점 금지 원칙 철저 준수 (13번 난이도 '어려움'에 3.8점 고배점, 14·15번 '쉬움'에 2.7점, 2.3점 저배점 안배).

## 75. 2026학년도 2학기 9월 9일(수) 오후 특별 일과 운영 및 황요한 교사 수업·마감 일정 (2026-09-07)
- **개요:** 2026년 9월 9일(수) 1·2학년 대학 학과 체험 행사 및 3학년 진로탐구활동 실시에 따라 오후 일과 시간이 변동 운영됨.
- **9/9(수) 특별 일과 운영 시간표:**
  * **6교시:** 14:35 ~ 15:25 (※ 6교시와 7교시 사이 쉬는 시간 없이 연강 운영)
  * **7교시:** 15:25 ~ 16:15
  * **청소시간:** 16:15 ~ 16:30 (15분간)
  * **8교시:** 16:40 ~ 17:30 (50분간)
- **황요한 교사 핵심 일정 및 유의사항:**
  1. **6~7교시 (14:35~16:15):** 1·2학년 대학 학과 체험(1학년 계명대, 2학년 동아대) 시 황요한 교사는 배정된 강좌 없음(공강/연구실 교무 행정 및 시험 출제 집중). 3학년은 쉬는 시간 없이 6·7교시 연강으로 진로탐구활동 진행됨.
  2. **8교시 당김수업 (16:40~17:30):** 3학년 4반 심화국어 (수능 후 11/27 금요일 5교시분 당김). 기존 15:30이 아닌 **16:40**에 시작하므로 시간 착오 없도록 유의.
  3. **공문 발송 마감 (16:30까지):** 경남과고 면접문항 검토교사 추천 공문 발송 마감이 16:30이므로, 8교시 수업(16:40 시작) 들어가기 전인 청소시간(16:15~16:30) 이전에 최종 결재 및 발송을 마쳐야 함.
  4. **2학년 문법 중간고사 출제 마감:** 9월 9일(수)까지 본인 출제 문항 완성 및 동료 교사 출제본 취합 후 B4 마스터 시험지 편집 총괄 진행.

## 76. 2026학년도 2학기 진해고 교원 인사 변동 및 챗봇 기숙사 운영 규정 갱신 (2026-09-07)
- **교원 인사 현황 (2026-09-01 자):**
  * **교장:** 오길환 교장 선생님
  * **교감:** **손세민** 교감 선생님 (※ 2026년 9월 1일 자로 손세민 교감 선생님 부임/변경 완료)
  * **챗봇 지식 베이스 탑재 원칙:** 교장 및 교감 선생님 성함은 챗봇 지식 베이스(`knowledge.txt`)에 일체 등재하지 않으며, 관련 문의 시 교무실(055-546-2260)로 안내하는 보안 원칙 유지.
- **기숙사(송학관/동백관) 학기별 선발 및 유지 규정:**
  * **1학년 1학기 (신입생):** **중학교 내신 성적(석차백분율)** 100% 기준 선발 (진해 관내 5% 이내, 관외 30% 이내 우선 선발 쿼터).
  * **1학년 2학기 이후 (재학생):** **직전(전) 학기 고교 내신 성적 + 전국연합학력평가(모의고사) 성적**을 합산하여 정기 선발.
- **기숙사 시설 리모델링 계획 방침:**
  * 현재 기숙사 리모델링 계획은 수립되어 있지 않음.
  * 향후 대대적인 시설 리모델링이나 환경 개선 사업 추진 시 **학교 누리집(홈페이지) 공지사항에 게시**하고, **학생 및 학부모님께 가정통신문 등을 통해 별도로 상세 안내**함.


## 76. 황요한 교사 나이스(NEIS) 개인번호 영구 등록 (2026-09-07)
- **교원 성명:** 황요한 (진해고등학교 교사)
- **나이스(NEIS) 개인번호:** S101087780
- **설명:** 황요한 선생님의 나이스(NEIS) 교원 개인번호 정보입니다. 지필평가 문항정보표 등록, 분할점수 산출, 학교생활기록부 세특 및 출결 마감, 연수 및 교원인사 행정 서식 처리 등 나이스 전산 및 교무 행정 업무 처리 시 즉각 조회하여 활용할 수 있도록 영구 메모리에 기록함.

## 77. 2026년 9월 8일(화) 아침 브리핑 필수 상기 지침 (애향삼품 행정실 정미정 계장님 집행 & 감사편지 우편 발송) (2026-09-07)
- **개요:** 2026년 9월 8일(화) 출근 직후 황요한 선생님께 브리핑드릴 때 반드시 포함해야 할 애향삼품 2대 마감 업무.
- **아침 필수 브리핑 항목:**
  1. **행정실 정미정 계장님께 애향삼품 장학금 지급 집행 요청:**
     * 기안문 「2026학년도 1학기 애향삼품 장학금 지급」 결재 완료 확인.
     * 행정실 정미정 계장님(발전기금/지출 담당)께 발전기금 통장에서 장학생 4명 계좌로 입금 집행 요청:
       - 2-4 김지호 (800,000원)
       - 2-6 정서윤 (800,000원)
       - 3-6 정하윤 (800,000원)
       - 3-8 윤영 (800,000원) / 총 3,200,000원
  2. **기탁자 댁 감사편지 및 추천서 우편(등기) 발송:**
     * 동봉 서류: 장학생 4명의 자필 감사편지 4부 + 담임교사 추천서 4부 (총 8쪽 원본/출력본).
     * 봉투 라벨: 바탕화면 애향삼품 장학금 감사편지 우편발송 라벨.hwp 출력 후 대봉투 부착.
     * 수취인: 조카며느리 **이경자 님 귀하** (창원시 진해구 천자로 386 마린푸르지오 111동 1901호, 우편번호 51628, ☎ 010-8538-3080).
     * 팁: 행정실 정미정 계장님께 장학금 입금 요청 시 행정실 우편 발송함에 함께 전달하면 원스톱 처리 가능.
  3. **업무용 컴퓨터에서 주간 대입 알리미 v4.1 클로드 최종 재검증 및 가동 완료:**
     * **사유:** 9월 7일 밤 원격 접속 환경의 가상 데스크톱 마우스 락 제약으로 미뤄낸 클로드 최종 검토 작업을 학교 업무용 PC에서 원클릭 완료.
     * **실행 절차:** 학교 업무용 PC에서 클로드 대화창을 열고 다음 한 줄 입력:
        `admission_v40_review/입시봇_v41_최종검증_의뢰서.md 파일을 읽고 최종 재검증해줘`
     * **후속 조치:** 클로드의 최종 승인 확인 후, 실전 발송 테스트(python admission_news.py run_now) 또는 매주 수요일 11:00 정기 스케줄 무인 자동화 상태 확인.

## 78. 주간 대입 입시 알리미 v4.1 멀티에이전트 오케스트레이션 개편 및 클로드 3중 정밀 감사 완결 (2026-09-08)
- **개요:** 주간 대입 입시 정보 큐레이션 및 팩트 알리미(`admission_news.py`)를 5단계 멀티에이전트 시스템(리서처 -> 병렬 감사관 2A/2B -> 내용 검토관 -> 레이아웃 에디터 -> 구글 드라이브 퍼블리셔 -> 텔레그램 카드 전송관)으로 전면 개편하고, 클로드 독립 3중 감사를 통해 P0 2건, P1 7건, P2 8건, F 3건, G 1건을 100% 완벽 해결함.
- **핵심 기술 조치 및 보안 확립**:
  1. **보안 및 인증 (P0-1, P0-2, G-1):** 소스 내 텔레그램 토큰 평문 하드코딩 완전 삭제(`.env` 일원화), `verify=False` 및 `CERT_NONE` 영구 퇴출. Python 3.10+ 공식 표준 `truststore`(`truststore.inject_into_ssl()`)를 적용하여 Windows OS 공식 인증서 저장소(스쿨넷 루트 CA 포함)와 직결, 무결한 TLS 검증 달성.
  2. **팩트 감사관 신뢰성 (P1-3, P1-4, P1-5):** 응답 파싱 실패 시 `audit_failed: True` 격리 및 경고 로그 출력, 복수 JSON 블록 중 마지막 블록 채택, 감사 이슈 발생 시 구글 문서 상단 및 텔레그램 카드에 경고 박스 자동 주입.
  3. **병렬 Fan-Out 및 문서 격리 (P1-6, P1-8, F-1):** `ThreadPoolExecutor` 기반 Step 2A/2B 동시 병렬 실행, 드라이런(`--dry-run`) 시 비공개 유지, 구버전 공개 문서의 `anyone` 권한 완전 회수.
  4. **텔레그램 전송 안정성 (P1-7, F-2, F-3):** 3,800자 단위 줄 기반 분할(Line-based chunking)로 구글 문서 URL 절단 0건 달성, 마크다운 별표 탈락 방지용 대괄호(`【 】`) 헤더 도입.
- **검증 및 실전 가동 결과**:
  * **25개 종합 테스트 하네스 (`test_admission_harness.py`):** 25/25 PASS (100% 통과).
  * **실전 라이브 발송:** 실제 8자리 봇 ID(`8821847852`) 및 Chat ID(`8518409134`)로 HTTP 200 OK 전송 성공 확인.
  * **스케줄링:** 매주 수요일 오전 11:00 무인 자동 가동 완비.

## 79. 2027학년도 진해고 신입생 입학설명회 사전신청 및 심층 입결 안내 지침 (2026-09-08)
- **입학설명회 사전 신청 운영 방침:**
  * **안내 및 발송 시기:** **9월 말 ~ 10월 초**에 각 중학교로 사전 신청 안내 공문 및 신청 링크를 발송하여 확인하실 수 있도록 안내 예정.
  * **당일 참석 원칙:** 사전 신청을 하지 않았다고 해서 참석하지 못하는 것이 절대 아니며, 진해고에 관심 있는 중3 학생과 학부모라면 **누구나 사전 신청 여부와 상관없이 당일(10월 22일 목요일 18:30) 100% 자유롭게 참석 가능한 열린 행사**임을 명시.
- **심층 입시 결과 및 등급별 지원 경향성 안내 지침:**
  * 우리 학교 학생들의 내신 등급별 대학 지원 경향성, 수시 전형별 상세 합격선, 학과별 진학 데이터 및 실제 합격 사례는 **10월 22일(목) 18:30 신입생 입학설명회 현장에서 전문적이고 심층적으로 다루어질 예정**임을 안내하여 설명회 참석을 자연스럽게 유도.


## 80. 2026년 복권기금 꿈사다리 SOS 장학금 교내 추천 접수 마감 및 후속 처리 지침 (2026-09-08)
- **교내 추천 접수 마감 일시:** **2026년 9월 10일(목) 13:35까지**
- **관련 공문 및 보관 위치:** 한국장학재단 접수 공문 (진해고등학교-11062)
  * 보관 경로: D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\업무(장학금 및 입학홍보)\2. 장학금\[한국장학재단] 2026년 복권기금 꿈사다리 SOS 장학금 선발 안내\
- **교내 수합 방식:** 각 학급 담임교사로부터 쿨메신저 쪽지로 [ 학년-반 / 번호 / 학생 성명 / 위기 사유(간략히 1~2줄) ] 수합.
- **장학담당자(황요한) 후속 처리 절차:**
  1. **학자금지원시스템 일괄 추천 등록:** 수합된 학생 명단을 바탕으로 한국장학재단 학자금지원시스템(`eduman.kosaf.go.kr`)에 추천 대상자 등록 (긴급구난 세부사유 선택 및 학교장 확인).
     * ※ 재단 공식 학교추천 마감: 2026. 9. 16.(수) 18:00
  2. **추천 학생 개별 안내:** 시스템 등록 완료 후 해당 학생에게 한국장학재단 누리집에서 직접 신청서(서식14) 업로드 및 보호자 온라인 전자서명 동의 완료하도록 안내 (재단 학생신청 마감: 2026. 9. 23.(수) 18:00).
     * ※ 학생 신청서 작성 시 학교명, 학생 성명 기재 금지(블라인드 평가 규칙 엄수).
  3. **취약계층 대리 신청 대응:** 조손가정, 방임, 부모 연락 두절 등으로 학생/보호자의 전자서명이 불가할 경우 '학교 대리 신청(붙임4 부록)' 트랙으로 교사가 직접 시스템에 서류 업로드 진행.
- **장학금 주요 조건:**
  * 지원 금액: 10개월간 매월 30만 원 (총 300만 원, 전 학년 공통, 선발 후 9~10월분 소급 지급, 카드포인트)
  * 자격 요건: 소득(수급자·차상위 무관) 및 성적·출결·봉사 무관, 긴급구난 위기 학생, 별도 증빙서류 불요(학교추천으로 갈음), 교원 멘토링 활동 없음, 추천 인원 무제한.


## 81. 2027 오키나와 항공권 감시 봇 v2.4 구축 및 클로드 6차 최종 승인 배포 이력 (2026-09-08)
- **개요:** 2027년 1월 부산(김해 PUS) ↔ 일본 오키나와(나하 OKA) 3인 가족(성인 2명 + 만 28개월 소아 1명) 왕복 직항 항공권 최저가/특가 모니터링 봇 및 GitHub Actions 무인 서버 워크플로우 구축 완료.
- **클로드(Claude) 1~6차 적대적 검토 및 최종 승인 완수:**
  * **Protobuf Wire Format TFS 인코더 & 다바이트 태그 varint 디코더 완비:** 	rip_type=1(ROUND_TRIP), cabin=1(ECONOMY), passenger_types=[1, 1, 2](성인2+소아1) 바이트 정합성 독립 재현 검증 통과.
  * **Dual-Query Ratio Solver (성인 1인 대조 척도):** 라벨 없는 실제 구글 플라이트 카드에서 성인 1인 최저가(521,000원) 대조를 통해 3인 총액 1,498,500원(비율 2.88배) 100% 자동 확정.
  * **단일 장애점(SPOF) 방어:** okinawa_state.json 내 7일 캐시 폴백 및 조회 실패 시 텔레그램 긴급 점검 통지 연동.
  * **출발 시간대 엄격 필터링:** 07:00 ~ 16:30 주간 직항만 수집하고, 시각 미식별 카드 Fail-Closed 배제 및 편도가 혼재 시 왕복 max 채택.
  * **순수 함수 리팩토링:** pick_reference_from_cards() 순수 함수 추출 및 단위 테스트 6대 스위트 100% 통과.
  * **페이지 로드 최적화:** 1순위 여정의 1인 대조가를 2순위 여정과 공유(shared_ref_1p)하여 로드 횟수 4회 ➔ 3회로 25% 절감.
- **저장소 및 운영 지침:**
  * **저장소:** https://github.com/hyh54311-dev/jinhae-admission-system.git
  * **핵심 파일:** okinawa_flight_tracker_bot.py, .github/workflows/okinawa_flight_price_tracker.yml, okinawa_state.json, 
equirements.txt
  * **100% 무인 자동 감시 활성화 완료:** 워크플로우의 cron 스케줄이 활성화되어 **매일 2회(한국시간 09:00 / 17:00 KST)** 완전 무인 자동 스캔이 실행되며, 필요한 경우 언제든 GitHub Actions 콘솔에서 workflow_dispatch 수동 실행도 병행 가능.


## 82. 2026년 9월 10일(목) 2학년 화법과 언어 2학기 1차 지필평가 문항 검토 협의회 (2026-09-09)
- **일시:** **2026년 9월 10일(목) 13:10 ~ 13:35** (점심시간)
- **장소:** **2학년실** (본관 3층 2학년 교무실)
- **대상 과목:** 2학년 화법과 언어 (2학기 1차 지필평가 출제 문항 상호 검토)
- **주요 내용:** 출제 문항 오류 검토, 정답 시비 소지 차단, 난이도 및 배점 교차 점검.
- **오후 연계 일정:**
  * **13:35:** 복권기금 SOS 장학금 교내 추천 접수 마감 (Rule 80, 쿨메신저 쪽지 수합 후 시스템 일괄 등록).
  * **13:35 (5교시):** 3학년 1반 심화국어 수업 이동.


## 83. 2027학년도 진해고등학교 교육과정 편성표(2027 신입생, 현 1학년, 현 2학년) 확정 데이터 및 즉각 호출 규정 (2026-09-10)
- **개요:** 2026년 9월 확정된 진해고등학교의 2022 개정 교육과정 기반 3개년 교육과정 편성표 확정본에 관한 규정입니다.
- **문서 보관 위치:**
  * **교무기획부:** `D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\교무기획부\교육과정\2027학년도 학교교육과정 편성표(안)_진해고등학교.xlsx` 및 `2027학년도_진해고등학교_교육과정_편성표_마스터_가이드.md`
  * **입학홍보:** `D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\업무(장학금 및 입학홍보)\3. 홍보\입학설명회\2027학년도 학교교육과정 편성표(안)_진해고등학교.xlsx` 및 `2027학년도_진해고등학교_교육과정_편성표_마스터_가이드.md`
- **2022 개정 교육과정 총괄 이수 학점 (192학점 체계):**
  * **총 이수 학점:** 192학점 = 교과 174학점(학교지정 122 + 학생선택 52) + 창의적 체험활동 18학점.
  * **학기당 이수 학점:** 매 학기 **교과 29학점 + 창체 3학점 = 32학점** 균등 편성 (32학점 x 6학기 = 192학점).
- **학년별 학교 지정 공통과목 (전 학년 공통):**
  * **1학년 (매 학기 29학점 100% 학교 지정):**
    - 1학기: 공통국어1(4), 공통수학1(4), 공통영어1(4), 한국사1(3), 통합사회1(3), 통합과학1(3), 과학탐구실험1(1, A~C), 체육1(2, A~C), 음악(2, 미술과 교차), 한문(3, 정보와 교차)
    - 2학기: 공통국어2(4), 공통수학2(4), 공통영어2(4), 한국사2(3), 통합사회2(3), 통합과학2(3), 과학탐구실험2(1, A~C), 체육2(2, A~C), 미술(2, 음악과 교차), 정보(3, 한문과 교차)
  * **2학년 (매 학기 학교 지정 17학점 + 학생 선택 12학점 = 29학점):**
    - 1학기 학교 지정: 문학(4), 대수(4), 영어Ⅰ(4), 스포츠 생활1(2), 음악 연주와 창작↔미술 창작(3)
    - 2학기 학교 지정: 화법과 언어(4), 미적분Ⅰ(4), 영어Ⅱ(4), 스포츠 생활2(2), 미술 창작↔음악 연주와 창작(3)
  * **3학년 (매 학기 학교 지정 15학점 + 학생 선택 14학점 = 29학점):**
    - 1학기 학교 지정: 독서와 작문(4), 확률과 통계(4), 영어 독해와 작문(4), 스포츠 문화(1), 인간과 심리(2, 교양 P/F)
    - 2학기 학교 지정: 주제 탐구 독서(4), 실용 통계(4), 심화 영어 독해와 작문(4), 스포츠 과학(1), 논술(2, 교양)
- **코호트(대상 학년)별 학생 선택 과목군 및 핵심 차이점:**
  1. **2027학년도 신입생 (현 중3 / 2027학년도 1학년):**
     * 2-1: **선택군A** (사회/과학 일반 8과목 중 택3, 각 3학점 = 9) + **선택군B** (제2외국어/정보 4과목 중 택1: 일본어, 중국어, **언어생활과 한자**, **데이터 과학** ★신설 = 3) ➔ 12학점.
     * 2-2: **선택군C** (국수영외 진로 5과목 중 택1: 문학과 영상, 기하, 경제 수학, 세계 문화와 영어, **일본어 회화** = 3) + **선택군D** (사회/과학 진로 8과목 중 택3, 각 3학점 = 9) ➔ 12학점.
     * 3-1: **선택군E** (**기초·탐구 19과목 통합군 중 택4**, 각 3학점 = 12학점 ★자율성 극대화: 국어 독서 토론과 글쓰기, 수학 미적분Ⅱ, 영어 미디어 영어, 영어 **심화 영어**, 사회 6과목, 과학 9과목) + **선택군G** (교양 3과목 중 택1: 교육의 이해, 인간과 철학, 인간과 경제활동 = 2) ➔ 14학점.
     * 3-2: **선택군F** (융합탐구 5과목 중 택3, 각 4학점 = 12학점: 여행지리, 국제 관계의 이해, 윤리문제 탐구, 과학의 역사와 문화, 융합과학 탐구) + **선택군G** (교양 택1 연계 = 2) ➔ 14학점.
  2. **2026학년도 입학생 (현 1학년 / 2027학년도 2학년):**
     * 2-1: 선택군B가 **2과목**(일본어, 중국어) 중 택1.
     * 2-2: 선택군C에서 **일본어 회화** 개설 (심화 일본어 아님).
     * 3-1: **선택군E (국수영 4과목 중 택1: 독서 토론과 글쓰기, 미적분Ⅱ, 수학과 문화, 미디어 영어 = 3)** + **선택군F (탐구 15과목 중 택3 = 9)** 분리 편성.
     * 3-2: 선택군G (융합탐구 5과목 중 택3 = 12) + 선택군H (교양 = 2).
  3. **2025학년도 입학생 (현 2학년 / 2027학년도 3학년):**
     * 2-2: 선택군C에서 일본어 회화 대신 **심화 일본어** 개설.
     * 3-1: 선택군E에서 독서 토론과 글쓰기 대신 **매체 의사소통** 개설 (매체 의사소통, 미적분Ⅱ, 수학과 문화, 미디어 영어 중 택1).
     * 3-1: 선택군F 탐구 선택군에 **'과학과제 연구'가 포함되어 총 16과목** 중 택3.
     * 3-2: 선택군G (융합탐구 5과목 중 택3 = 12) + 선택군H (교양 = 2).
- **성적 산출 및 내신 평가 방식 (2028 대입 개편 연동):**
  * **성취도 5단계 + 석차 5등급 병기:** 공통국어/수학/영어/한국사/통사/통과 및 일반선택, 진로선택 전반.
  * **성취도 5단계 절대평가 (석차 미산출):** 여행지리, 역사로 탐구하는 현대 세계, 사회문제 탐구, 윤리문제 탐구, 과학의 역사와 문화, 융합과학 탐구 등 융합선택.
  * **성취도 3단계 (A/B/C):** 과학탐구실험1·2, 체육1·2, 스포츠 생활1·2, 스포츠 문화/과학, 음악/미술 창작.
  * **P/F (이수/미이수):** 인간과 심리, 논술, 교육의 이해, 인간과 철학, 인간과 경제활동.
- **즉각 호출(불러오기) 가이드:**
  * 진해고 교육과정, 특정 학년/학기 개설 과목, 학점 배분, 선택군 구성, 코호트 간 차이 질문 시 위 데이터베이스를 기반으로 즉시 단 하나의 오차도 없이 직관적 표와 함께 정확히 회신할 것.


## 84. 로타리클럽 장학금(300만 원) 기부 통화 재시도 필수 상기 (2026-09-11 금요일 아침 브리핑 필수 항목)
- **개요:** 2026년 9월 10일(목) 오후 로타리클럽 관계자(`010-8511-5415`)로부터 약 300만 원 규모의 장학금 기부 의사 연락이 왔으나, 통화 중으로 연결되지 않아 **2026년 9월 11일(금) 아침**에 재통화하기로 함.
- **연락처:** **`010-8511-5415`** (로타리클럽 담당자)
- **통화 시 필수 확인 5대 체크리스트:**
  1. **소속 단체 및 담당자 명확화:** 정확한 클럽 명칭(진해로타리, 진해중앙로타리 등), 직함, 성함.
  2. **수혜 인원 및 금액 배분:** 300만 원에 대한 배분안 (예: 100만 원 × 3명, 50만 원 × 6명 등).
  3. **선발 자격 요건:** 특정 학년 지정 여부, 저소득·취약계층 우선, 모범 학생 추천 등.
  4. **지급 및 영수증 방식:** 학교발전기금 기탁(기부금 영수증 발행) vs 학생 통장 직접 입금 vs 수여식 직접 전달.
  5. **추천 마감 시한:** 학교 측에서 명단/추천서를 보내야 하는 최종 기한.
- **필수 브리핑 규칙:** 2026년 9월 11일(금) 아침 선생님과의 첫 대화나 브리핑 시, 본 로타리클럽 통화 재시도 안내 및 번호(`010-8511-5415`)와 체크리스트를 최우선 안건으로 반드시 상기시켜 드릴 것.


## 85. 2026년 9월 11일(금) 2학년 화법과 언어 1차 지필평가 시험범위 당일(조기) 공지 (2026-09-11)
- **개요:** 기존 9월 16일(수) 공지 예정이었으나, 학생들의 충분한 시험 대비를 위해 **2026년 9월 11일(금) 오늘 수업 중 조기 공지**하는 것으로 일정 변경.
- **조치 사항:** 9월 16일 자 예약 알림 타이머(`task-9395`) 및 구글 캘린더 일정(`snm4np122ckn2i1bijadef016c`) 전면 취소/삭제 완료.
- **대상 및 내용:** 2학년 화법과 언어 수강 학급(9/10 문항검토 완료본 기준 교과서 단원, 학습지/프린트 범위, 선택형/서답형 배점 비율 등 공지).


## 86. 로타리클럽 장학금(300만 원) 1~2개월 후 진행 및 특정 학생(2학년 방지원) 선발 배제 규정 (2026-09-11)
- **개요:** 2026년 9월 11일(금) 로타리클럽(`010-8511-5415`)과 통화 완료 결과 및 향후 선발 시 필수 배제 규칙입니다.
- **진행 일정:** 로타리클럽 측도 중앙 본부(지구본부)에서 장학금을 배정받아 학교에 전달해야 하는 행정 절차가 있어, **1~2달 뒤(2026년 10월 하순 ~ 11월 초)** 학교로 다시 연락을 주기로 합의함.
- **핵심 선발 제한 규정 (Strict Exclusion Rule):**
  * **로타리클럽 관계자는 장학금 수여 대상자가 될 수 없음** (클럽 자체의 이해충돌 방지 규정).
  * 이에 따라 **2학년 방지원 학생은 본 로타리클럽 장학금 선발 대상자에서 반드시 영구 제외**해야 함.
  * 향후 10~11월 추천 공지, 담임 추천 취합, 장학생선발심의위원회 협의록 작성 시 방지원 학생이 포함되지 않도록 사전 필터링 철저히 수행할 것.


## 87. 2026학년도 애향 삼품 장학생(4명) 감사편지 우편 발송 지침 (2026-09-11)
- **개요:** 2026년 9월 11일(금) 애향 삼품 장학생 감사편지 및 추천서 우편 발송 업무 일정 반영.
- **수혜 학생 (4명):** 2학년 김지호(2-4), 정서윤(2-6) / 3학년 정하윤(3-6), 윤영(3-8).
- **실제 우편물 수취인 및 발송 주소 (필수 준수 사항):**
  * **수취인:** **이경자 님** (기탁자 이흥순 할머니의 조카며느리)
  * **주소:** **경상남도 창원시 진해구 천자로 386 마린푸르지오 아파트 111동 1901호**
  * **우편번호:** **51628**
  * **연락처:** **010-8538-3080**
  * *(주의: 여좌동 기탁자 원주소가 아닌 마린푸르지오 이경자 님께 발송해야 정상 수령 및 전달 가능)*
- **관련 파일 위치:**
  * 우편 라벨: `.... 장학금\애향삼품 장학금\애향삼품 장학금 감사편지 우편발송 라벨.hwp`
  * 추천서 및 감사편지: `.... 장학금\애향삼품 장학금6학년도 애향 삼품 장학생 추천서 및 감사편지.pdf`


## 88. 2학기 이병의 선생님과의 2학년 화법과 언어 맞교환(1~5반 vs 6~10반) 및 복무/육아시간 판정 절대 규칙 (2026-09-03 시행)
- **개요:** 2026년 9월 3일부터 황요한 선생님과 이병의 선생님은 2학년 '화법과 언어' 수업을 전격 맞교환하여 수업을 진행하고 있음.
- **수업 담당 학급 맞교환 현황:**
  * **황요한 선생님 실제 담당 (2학년 1~5반, 총 5시간):**
    - 월요일 4교시: 2학년 5반 (205 화법)
    - 화요일 7교시: 2학년 4반 (204 화법)
    - 목요일 1교시: **2학년 2반 (202 화법)**
    - 목요일 6교시: **2학년 3반 (203 화법)**
    - 금요일 1교시: **2학년 1반 (201 화법)**
  * **이병의 선생님 실제 담당 (2학년 6~10반, 총 5시간):**
    - 월요일 4교시: 2학년 10반 (210 화법)
    - 화요일 2교시: 2학년 9반 (209 화법)
    - 화요일 6교시: 2학년 6반 (206 화법)
    - 수요일 2교시: 2학년 7반 (207 화법)
    - 수요일 4교시: 2학년 8반 (208 화법)
- **복무(육아시간/출장/대강) 및 시간표 검증 3대 절대 원칙:**
  1. **사적 맞교환 특성 반영 (나이스 공식 vs 실제 입실의 이원화):** 나이스 전산상 공식 시간표와 상관없이, 황요한 선생님은 이병의 선생님의 기존 시간표(2학년 1~5반)에 실제로 입실하셔야 하므로 수업 결손이 발생하지 않도록 실제 수업을 최우선 기준으로 판정해야 함.
  2. **목·금 1교시 및 목 6교시 수업 확인:** 
     - **목요일 1교시(2-2 화법, 08:50~09:40)** 및 **금요일 1교시(2-1 화법, 08:50~09:40)**는 실제 입실 수업이므로 **아침 육아시간(08:30~10:30) 사용 절대 불가**.
     - **목요일 6교시(2-3 화법, 14:45~15:35)** 역시 실제 입실 수업이므로 **목요일 오후 육아시간(14:30~16:30) 조기 퇴근 절대 불가**.
  3. **다음 주(9/14~9/18) 최종 육아시간 사용 가능일:**
     - **월요일(9/14) 오후(14:30~16:30)**: 가능 (5교시 306 심국 종료 후 6·7·8교시 실제 공강)
     - **화요일(9/15)**: 불가 (7교시 204 화법 실제수업 + 8교시 3-9 당김수업)
     - **수요일(9/16) 오후(14:30~16:30)**: 가능 (5교시 303 심국 종료 후 8교시 당김수업 없음)
     - **목요일(9/17)**: 불가 (1교시 202 화법, 6교시 203 화법 실제수업)
     - **금요일(9/18) 오후(14:30~16:30)**: 가능 (1교시 201 화법 실제수업 후, 5교시 304 심국 종료 후 6교시 공강)


## 89. 2026. 9. 16.(수) 창의적 체험활동 동아리활동(6~7교시) 지도 및 수요일 육아시간 불가 규칙 (2026-09-11)
- **개요:** 2026년 9월 16일(수) 6~7교시는 2026학년도 2학기 창의적 체험활동(창체) **동아리활동(12~13차시)** 시간임.
- **황요한 교사 담당 동아리:**
  * **동아리명:** **'대신해 AI'** (지도교사: 황요한, 대상: 1·2학년, 대표학생: 10622 이승범)
  * **일시:** 2026. 9. 16.(수) 6~7교시 (14:35 ~ 16:30)
  * **활동 내용:** 12~13차시 '생기부 특화 프로젝트 (AI 활용 보고서 작성 지도)'
- **육아시간 및 복무 영향:**
  * 수요일 오후(14:30~16:30)는 6~7교시 동아리활동 지도가 필수 편성되어 있으므로 **오후 육아시간(조기퇴근) 사용이 전면 불가**함.
  * 수요일 오전은 1교시(3-8 심국) 수업이 있어 아침 육아시간 역시 불가.
  * 따라서 **9월 16일(수)은 전일 육아시간 사용 불가**함.


## 90. 2026학년도 진해고등학교 제규정 개정 (사무위임전결규정 - 교외체험학습 전결권 교감 지정) (2026-09-11)
- **공문 정보:** 시행 진해고등학교-11294 (2026. 9. 11.) / 기안 교사 박지환, **교무기획부장 최준호**, **교감 손세민 (전결 처리)** (교장 오길환 결재란은 교감 전결로 최종 처리 완료).
- **개정 목적 및 시행일:** 「행정업무의 운영 및 혁신에 관한 규정」 제10조 제2항에 따라 교외체험학습 전결권자를 명확히 규정하여 신속한 행정 처리 도모. **2026년 9월 11일부터 즉시 시행**.
- **핵심 개정 내용 (진해고 사무위임전결규정 - 교무실 위임전결사항):**
  * 단위업무 **6. 교외체험학습** 신설
  * 세부업무 및 전결권자:
    - **가. 교외체험학습 신청서:** 담당 ➔ 부장교사 ➔ **교감 전결 (○)**
    - **나. 교외체험학습 결과 보고서:** 담당 ➔ 부장교사 ➔ **교감 전결 (○)**
- **보관 위치:** D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\교무기획부\제규정\2026학년도 진해고등학교 제규정 개정(사무위임전결규정 개정)


## 91. 2027학년도 대입 전형 분석 및 입학설명회 전략 핵심 데이터 (클로드 교차 검증 반영) (2026-09-12)
- **개요:** 구글 드라이브(`2027_대입_교과전형_분석자료/모집요강`, Drive ID: `1pwA9ObzqvDoqhWEfpPQrzKZDC_msHn3B`) 내 45개 대학 요강 원문을 클로드와 교차 분석하여 입학설명회 및 진학지도 핵심 팩트를 정립함.
- **1. 2027학년도 9등급제 확정:**
  * 2027 대입(현 고2)은 1~9등급 체제 확정(5등급제는 2028학년도 고1 입학부터 적용). 중3(2030 대입) 설명회 시 "현재 고2 실증 데이터 기준"임을 명확히 구분하여 안내.
  * 2027 대교협 집계: 수시 277,583명(80.3%), 학생부교과 156,631명(45.3%), 지역인재 27,730명(+952명).
- **2. 부울경 의약계열 수능최저 원문 팩트:**
  * **경상국립대 의예과:** 일반교과 3합 4 vs **지역인재 3합 6** (지역인재가 2등급 완화되어 3개 2등급이면 충족, 경남 학생 절대적 호재).
  * **울산대 의예과:** 지역교과 3합 4(과탐 2과목 평균 소수점 첫째자리 **올림**) / 지역의사제 3합 5(과탐 **버림**). 일반교과 선발 0명.
  * **고신대 의예과:** 일반고/지역인재 모두 3합 4(확통 시 합 3으로 1등급 강화). 지역의사선발 3합 5(확통 합 4, **사탐 허용**).
  * **인제대 의예과:** 일반/지역인재Ⅰ·Ⅱ/지역의사 모두 **4개 영역 각 2등급 이내 (개별조건형)** (지역인재 완화 없음, 1개라도 3등급이면 탈락). 약학과 4합 9.
- **3. 사립대 vs 국립대 최저 분기 및 진해고 중위권 '스위트 스팟':**
  * **사립대(경남대, 동의대 등):** 간호/물치/사범 등 특수학과 제외한 일반 공학·인문계열 **수능최저 전면 없음** (동의대 요강: "수능 미응시자도 지원 가능").
  * **국립대:** 최저가 대부분 있으나 기준이 매우 낮음 (부경대 자연계 **수학포함 2합 9**, 한국해양대 해양과기융합대 **1개 영역 5등급 이내**, 경상국립대 IT/공대/경영 **2합 10**).
  * **진해고 유리성 프레이밍:** 타 일반고 중위권은 수능을 포기하여 2합 8~10도 미충족 탈락하지만, 진해고는 면학·기숙사 분위기로 3~4등급 2개를 안정 확보하므로 **내신 3~4등급도 국립대에 안착하는 완벽한 합격 필터**로 작용함.
- **4. 정식 전형 명칭 복원:**
  * 부경대: **'학생부교과(지역혁신인재전형)'** (글로컬 명칭 아님)
  * 한국해양대: **학생부교과(교과성적우수자전형)**, **(지역인재전형)**
  * 동의대: **학생부교과(일반고교과전형)**, **(지역인재교과전형)**
- **5. 성취도별 분포비율 실제 반영 대학 확인:**
  * **서강대:** 교과 10%를 '환산성취비율' 산식(`취득성취비율/2 + 하단성취비율합계`)으로 100% 정량 반영.
  * **고려대:** 석차등급, 성취도, 성취도별 분포비율을 합산한 **변환석차등급** 적용.
  * **성균관대:** 정성평가 20% 내에서 성취도별 분포비율 종합 평가.
- **6. 서울 주요대 교과전형 정성평가(서류) 확대:**
  * 8개교 중 6개교가 서류/정성평가 10~30% 반영 (경희대 30%, 서울시립대 20%, 성균관대 20%, 고려대 10%, 한양대 10%). 순수 교과 100%는 연세대, 서강대 2곳뿐 ➔ 진해고 생기부 세특/탐구보고서의 역전 기회.
- **7. 자료 보완 과제 (안티그래비티 실행 예정):**
  * **부산대:** 수시요강 재수집(기존 파일이 정시요강이거나 표 깨짐).
  * **동아대 & 국립창원대:** 이미지 PDF 텍스트 레이어 부재 ➔ 텍스트 추출 및 OCR 정리본 탑재.

## 92. 매일 아침 브리핑 필수 상기 규칙: 신입생 입학설명회 PPT 제작본 반영 (2026-09-13)
- **개요:** 매일 아침 일정 및 학사 브리핑을 드릴 때마다 **'신입생 입학설명회 PPT 제작본 반영 건'**을 필수 상기 항목으로 포함하여 안내할 것.
- **핵심 점검 내용:**
  1. **슬라이드 배치:** `2027입학설명회_문구완성.pptx`의 Part 4 [우리 학교 중위권 학생 진학 사례] 내 기존 Slide 27(단순 수능최저 정의)을 대체하거나 `[S29-B]`(창원대 3.8등급 사례 직후)에 신규 배치.
  2. **핵심 실증 데이터 (1장 완성형):** 
     - **부경대:** 2.8~3.5등급 합격률 **63.2%** (최저미충족 단 9.6%)
     - **창원대:** 3.5~4.2등급 및 4등급대 다수 합격 (지역인재 100% 활용)
     - **경상국립대:** 4.2~5.0등급 합격률 **54.5%** (합격자 78.2% 충원합격 대역전)
  3. **디자인 통일성:** `00_공통_바나나nl_컨설팅_스타일_프롬프트.txt` 규격(화이트 #FFFFFF, 딥네이비 #1B3A6B, 세일블루 #3B82C4, 맥킨지/BCG 3단 카드, 우측 하단 20% 발표자 여백 유지) 엄수.



## 93. 진해고등학교 「질문하는 학교」 선도학교 운영 및 교사동아리 질문수업 연구 (2026-09-13)
- **사업 개요:** 진해고등학교는 학생 주도적 탐구 역량과 비판적 사고력을 함양하기 위한 **'질문하는 학교' 선도학교**로 지정·운영 중이며, 수업 현장 적용을 위한 교사 동아리(전문적 학습공동체)를 활발히 운영하고 있음.
- **교내 연수 이력:** **2026년 9월 11일(금)** 교사 동아리 주관으로 **강필성 선생님**의 **'질문 수업' 교내 교사 연수**를 성공적으로 실시함.
- **질문수업 정착 및 교과별 실현 방안(Feasibility) 4대 핵심 연구 축:**
  1. **질문 생성 프레임워크(루틴) 구축:** 학생들이 수동적 수용자가 아닌 질문 생성자가 되도록 돕는 QFT(Question Formulation Technique), 온라인 질문 보드(패들렛 등), 소크라틱 AI 질문 튜터 등 체계적 도구 도입.
  2. **수업 부담 최소화 및 진도 조화:** 교과 진도 압박을 덜고 부담 없이 정착시킬 수 있는 '5분 질문 열기/닫기' 미니 루틴 및 핵심 개념 중심 질문 수업 설계.
  3. **국어과(심화국어·화법과작문) 접목:** 텍스트 비판적 독해, 논증적 글쓰기, 토론 수업에서 학생 질문 기반 탐구보고서 및 학생부 세특 기록 연계.
  4. **교사동아리 적용 사례 공유:** 차기 동아리 모임을 통한 교과별 적용 가능성 검토 결과 공유 및 수업 모델 확산.


## 94. 2027학년도 신입생 입학홍보 기숙사 영상 제작(AI 모션 및 필모라 편집) 착수 일정 (2026-09-15 화요일 착수)
- **작업 개시일:** **2026년 9월 15일(화)**부터 본격 작업 개시 (일정 관리 및 아침 브리핑 상기 항목 포함).
- **소프트웨어 및 에셋 방침:**
  * **편집 툴:** **필모라(Filmora) 유료 라이선스** 사용 (워터마크 없음).
  * **비용 원칙:** 유료 에셋/효과 스토어 결제 일체 배제 (**추가 비용 0원**). 필모라 내장 속도 곡선(Speed Ramping), 광학 흐름(Optical Flow), 2단 고딕 자막, 기본 디졸브(0.5초), 오디오 덕킹(-50%) 기능만 활용.
- **AI 영상 생성(Image-to-Video) 5대 필수 고려사항 (사전 검증 완료):**
  1. **사전 크롭(Pre-Cropping):** 원본 항공사진(3501×1880)을 AI 업로드 전 필히 `16:9 (1920×1080)`로 사전 크롭하여 업로드할 것 (AI 자체 리사이징에 따른 교사 건물 왜곡 원천 차단).
  2. **모션 강도(Motion Intensity):** 3~4 이내로 절제 (과도한 수치 시 창문·외벽 직선이 물결처럼 뒤틀리는 젤로 현상 발생).
  3. **인물/얼굴 AI화 지양:** 학생/인물 사진은 AI 모션화 시 얼굴·손가락이 기괴하게 일그러지므로 배제하고, AI는 **교정 전경(항공뷰)·독서실 새벽 불빛 타임랩스·야경 전경** 3대 풍경에만 한정 적용.
  4. **네거티브 프롬프트 엄수:** `distortion, blur, warped architecture, ugly, extra limbs, shaking` 필수 삽입.
  5. **필모라 감속 연계:** AI가 생성한 5초 클립을 필모라 속도 곡선(0.6~0.7x)으로 부드럽게 늘려 8초 분량의 웅장한 시네마틱으로 완성.


## 95. 「AI 활용 공무원 재해예방 콘텐츠 공모전」 영상 제작 및 필모라 편집 추진 계획 (2026-09-15 화요일 오후)
- **공모전 개요:** 공무원연금공단 재해보상1실 주관, 공모기간 '26.9.14.(월)~10.16.(금) 18:00, 누리집(https://contest.ieumgil.com).
- **시상 규모:** 대상 100만 원, 최우수 50만 원, 우수 3편 각 20만 원, 참가상(본선 진출작 중 미수상작) 20편 각 5만 원 상당 상품권 (전문가 70% + 전국 공무원 선호도 투표 30%).
- **필수 제한 및 규격:**
  * **영상 분량 제한:** 공문상 재생 시간(초/분) 제한 없음. 단, 선호도 투표 및 시청 완주율 고려 시 **45초~1분 30초 내외 숏폼** 강력 권장.
  * **블라인드 심사:** 영상 내 성명, 소속 학교/기관명, 지역명 등 개인 식별 정보 일체 포함 금지.
  * **온라인 접수 시스템 제한:** 파일 업로드 용량 **최대 100MB 이하** (비트레이트 8~10Mbps 조절, 70~80MB 렌더링 권장). 작품 설명 300자 이내, AI 도구 활용 내용 300자 이내 기재.
  * **출품 수량:** 1인(팀)당 최대 2개 작품.
- **추진 로드맵 및 필모라 구독 마일스톤:**
  1. **이번 주 주말 (9월 19~20일):** 기획, 시나리오 콘티 작성, 핵심 예방 메시지(300자) 확정, 프롬프트 설계.
  2. **에셋 생성 (9월 21일 ~ 10월 1일):** AI 이미지(Midjourney/DALL-E) 및 영상(Runway Gen-3/Kling/Luma) 생성, AI 음성(Typecast/Vrew) 추출, 상업적 무료 BGM/효과음 아카이빙.
  3. **필모라 구독 및 본 편집 (10월 2일 ~ 10월 12일):** **2026년 10월 2일 필모라(Filmora) 유료 구독 시작** ➔ 워터마크 없는 컷 편집, 스피드 램핑, 2단 강조 자막, 사운드 믹싱, 100MB 이하 고화질 FHD 렌더링.
  4. **최종 접수 (10월 13일 ~ 10월 14일):** 블라인드 검수 후 마감(10/16 18:00) 2일 전 contest.ieumgil.com 여유 접수 완료.
- **관련 파일 보관 경로:** D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\업무 이외\2026_AI활용_공무원_재해예방_콘텐츠_공모전\
