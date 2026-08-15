# 한국투자증권 Open API (KIS Developers) 정본 연동 가이드 (2026.08 최신 규격)

본 문서는 한국투자증권 공식 Open API 전체 문서(`한국투자증권_오픈API_전체문서_20260815_030000.xlsx`)를 바탕으로 검증된 KIS Developers 핵심 연동 규격 지침서입니다.

---

## 1. 개요 및 공식 채널
* **공식 개발자 포털:** [KIS Developers](https://apiportal.koreainvestment.com)
* **공식 GitHub:** [한국투자증권 Open Trading API GitHub](https://github.com/koreainvestment/open-trading-api)
* **서버 환경별 Base URL & 포트:**
  * **실전투자 (Production):** `https://openapi.koreainvestment.com:9443`
  * **모의투자 (Testbed):** `https://openapivts.koreainvestment.com:29443` (※ 모의투자는 포트 `:29443` 사용)

---

## 2. 인증 및 토큰 발급 (OAuth 2.0)
* **엔드포인트:** `POST /oauth2/tokenP` (토큰 발급) / `POST /oauth2/revokeP` (토큰 폐기)
* **Request Body 규격:**
  ```json
  {
      "grant_type": "client_credentials",
      "appkey": "YOUR_APP_KEY",
      "appsecret": "YOUR_APP_SECRET"
  }
  ```
* **유효기간:** 발급 시점부터 **24시간** 유효. 프로그램 가동 시 1일 1회 발급/재활용 권장.

---

## 3. 공통 헤더(Headers) 규격
모든 REST API 호출 시 아래 6대 헤더를 필수로 포함합니다.
* `content-type`: `application/json; charset=utf-8`
* `authorization`: `Bearer [Access_Token]`
* `appkey`: `[YOUR_APP_KEY]`
* `appsecret`: `[YOUR_APP_SECRET]`
* `tr_id`: 거래 ID (하단 TR ID 명세 참조)
* `custtype`: `P` (개인 고객 필수 헤더 / 법인은 `B`)

---

## 4. 핵심 기능별 거래 ID (TR ID) 및 엔드포인트 명세

### ① 주식주문 (현금 매수 / 매도) — [★ 신TR 필수 적용]
> **공식 문서 경고:** "구TR은 사전고지 없이 막힐 수 있으므로 반드시 신TR로 변경 이용 부탁드립니다."

| 거래 구분 | 실전투자 신TR (권장) | 실전투자 구TR (폐기예정) | 모의투자 신TR (권장) | 엔드포인트 및 Method |
| :--- | :---: | :---: | :---: | :--- |
| **주식 현금 매도** | **`TTTC0011U`** | `TTTC0801U` | **`VTTC0011U`** | `POST /uapi/domestic-stock/v1/trading/order-cash` |
| **주식 현금 매수** | **`TTTC0012U`** | `TTTC0802U` | **`VTTC0012U`** | `POST /uapi/domestic-stock/v1/trading/order-cash` |

* **주요 파라미터 (Body):**
  * `CANO`: 종합계좌번호 (8자리)
  * `ACNT_PRDT_CD`: 계좌상품코드 (`22`: 연금저축펀드, `01`: 일반위탁)
  * `PDNO`: 종목코드 6자리 (예: `069500`)
  * `ORD_DVSN`: 주문구분 (`00`: 지정가, `01`: 시장가)
  * `ORD_QTY`: 주문수량 (문자열)
  * `ORD_UNPR`: 주문단가 (문자열, 시장가 주문 시 `"0"` 전달)

---

### ② 국내휴장일조회 (CTCA0903R) — [★ 하이브리드 자동 이월]
* **TR ID:** `CTCA0903R` (모의투자 미지원)
* **엔드포인트:** `GET /uapi/domestic-stock/v1/quotations/chk-holiday`
* **Query Params:** `BASS_DT` (기준일자 YYYYMMDD), `CTX_AREA_NK=""`, `CTX_AREA_FK=""`
* **주요 특징:** 기준일자로부터 **24일치 달력 데이터**를 1회 호출로 일괄 반환.
* **응답 필드:** `output` 배열 내 `bass_dt`(일자), `opnd_yn` ("Y": 개장일 / "N": 휴장일).
  * *공식 지침:* 주문 가능 여부 판단 시 `opnd_yn == "Y"`를 사용.
  * *호출 권장:* 원장 서비스 부하 방지를 위해 1일 1회 호출 준수.

---

### ③ 국내주식 잔고 및 매수가능금액 조회
* **실전 잔고 조회:** `TR_ID: TTTC8434R` (`GET /uapi/domestic-stock/v1/trading/inquire-balance`)
* **매수가능금액 조회:** `TR_ID: TTTC8908R` (`GET /uapi/domestic-stock/v1/trading/inquire-psbl-order`)
  * 필수 파라미터: `CMA_EVLU_AMT_ICLD_YN: "N"`, `ORD_UNPR: "0"`

---

### ④ 시세 데이터 조회
* **주식현재가 시세:** `TR_ID: FHKST01010100` (`GET /uapi/domestic-stock/v1/quotations/inquire-price`)
* **국내주식 기간별시세 (월봉/일봉):** `TR_ID: FHKST03010100` (`GET /uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice`)
  * `FID_PERIOD_DIV_CODE`: `"M"` (월봉), `"D"` (일봉)
  * `FID_ORG_ADJ_PRC`: `"0"` (수정주가 반영)
