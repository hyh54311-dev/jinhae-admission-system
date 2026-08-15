# 한국투자증권 Open API 공식 전체 명세 종합 정리 (2026.08 기준 정본)

본 문서는 한국투자증권 공식 엑셀 명세서(`한국투자증권_오픈API_전체문서_20260815_030000.xlsx`, 총 339개 API)를 전수 분석하여, 퀀트 자동매매 봇 개발 및 유지보수 시 즉시 활용할 수 있도록 핵심 규격을 카테고리별로 집대성한 정본 레퍼런스 문서입니다.

---

## 📌 1. 서버 인프라 및 기본 통신 규격

* **실전투자 Base URL:** `https://openapi.koreainvestment.com:9443`
* **모의투자 Base URL:** `https://openapivts.koreainvestment.com:29443` (※ 포트 `:29443` 주의)
* **웹소켓(WebSocket) URL:** `ws://ops.koreainvestment.com:21000` (모의투자: `ws://openapivts.koreainvestment.com:31000`)
* **공통 필수 헤더 규격:**
  * `content-type`: `application/json; charset=utf-8`
  * `authorization`: `Bearer [Access_Token]` (24시간 유효)
  * `appkey`: KIS Developers 발급 App Key
  * `appsecret`: KIS Developers 발급 App Secret
  * `tr_id`: 거래 ID (하단 명세 참조)
  * `custtype`: `P` (개인 고객 필수 / 법인은 `B`)

* **초당 유량 제한 (Rate Limits):**
  * 일반 계정: 실전 초당 20건 / 모의 초당 5건
  * **신규 가입 첫 3일 계정:** 초당 3건으로 엄격 제한 (2026.04 개정, `EGW00201` 에러 수신 시 백오프 재시도 필수)

---

## 📌 2. 핵심 퀀트 자동매매 API 상세 명세 (Top 10)

### 📍 [접근토큰폐기(P)] 토큰 즉시 폐기 (/oauth2/revokeP)

```text
접근토큰폐기(P)
API 통신방식 | REST
메뉴 위치 | OAuth인증
API 명 | 접근토큰폐기(P)
API ID | 인증-002
실전 TR_ID
모의 TR_ID
기본정보
HTTP Method | POST
실전 Domain | https://openapi.koreainvestment.com:9443
모의 Domain | https://openapivts.koreainvestment.com:29443
URL 명 | /oauth2/revokeP
개요
개요 | 부여받은 접큰토큰을 더 이상 활용하지 않을 때 사용합니다.
Layout
구분 | Element | 한글명 | Type | Required | Length | Description
Request Header
Request Body | appkey | 고객 앱Key | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
appsecret | 고객 앱Secret | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appsecret (절대 노출되지 않도록 주의해주세요.)
token | 접근토큰 | string | Y | 286 | OAuth 토큰이 필요한 API 경우 발급한 Access token
일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용)
법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용)
Response Header
Response Body | code | 응답코드 | string | N | 8 | HTTP 응답코드
message | 응답메세지 | string | N | 450 | 응답메세지
Example
Request Example (Python) | {
  "appkey" : "PSw2UvBQCpoZFc7nZpIfIrOttmXXXXXXXXXX",
  "appsecret" : "/g84gaZp7W3DJEZhamiTH8ZdJkUJ8603rjo3HcOm5PvIc1YC3YmyJOQoW1H0kNjo4IbHwGUdi3+9oEbH4RKKl8GnEu3n/khxm0OrwHkQur+wbA74fcFXxaUnEbftu0X72Eaw9dEBMuK3rODeeOanrsJ1kZ9oKWykIG04F0nmgdXXXXXXXXXX",
  "token" : "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjZmNDgxMjBiLTlmMDItNGI5ZS05MGExLTRiNDk2MGM5ZWY2MyIsImlzcyI6InVub2d3IiwiZXhwIjoxNjQzMjg2MDUzLCJpYXQiOjE2NDMxOTk2NTMsImp0aSI6IlBTdzJVdkJRQ3dvWkZhOG5acElmSXJPdHRtZUtLUGZCclNKcyJ9.6Z-UvArobBfXbnpSFbFhd9WPVEM3ZQa5NEpqfmQ6rrZBISCi-P9CEamfVReIduTVYbafF02Pl6EPXXXXXXXXXX"
}
Response Example | {
  "code" : 200,
  "message" : "접근토큰 폐기에 성공하였습니다"
}
```

### 📍 [접근토큰발급(P)] OAuth 2.0 토큰 발급 (/oauth2/tokenP)

```text
접근토큰발급(P)
API 통신방식 | REST
메뉴 위치 | OAuth인증
API 명 | 접근토큰발급(P)
API ID | 인증-001
실전 TR_ID
모의 TR_ID
기본정보
HTTP Method | POST
실전 Domain | https://openapi.koreainvestment.com:9443
모의 Domain | https://openapivts.koreainvestment.com:29443
URL 명 | /oauth2/tokenP
개요
개요 | 본인 계좌에 필요한 인증 절차로, 인증을 통해 접근 토큰을 부여받아 오픈API 활용이 가능합니다.

1. 접근토큰(access_token)의 유효기간은 24시간 이며(1일 1회발급 원칙) 
   갱신발급주기는 6시간 입니다.(6시간 이내는 기존 발급키로 응답)

2. 접근토큰발급(/oauth2/tokenP) 시 접근토큰값(access_token)과 함께 수신되는 
   접근토큰 유효기간(acess_token_token_expired)을 이용해 접근토큰을 관리하실 수 있습니다.


[참고]

'23.4.28 이후 지나치게 잦은 토큰 발급 요청건을 제어 하기 위해 신규 접근토큰발급 이후 일정시간 이내에 재호출 시에는 직전 토큰값을 리턴하게 되었습니다. 일정시간 이후 접근토큰발급 API 호출 시에는 신규 토큰값을 리턴합니다. 
접근토큰발급 API 호출 및 코드 작성하실 때 해당 사항을 참고하시길 바랍니다.

※ 참고 : 포럼 &gt; 공지사항 &gt;  [수정] [중요] 접근 토큰 발급 변경 안내
Layout
구분 | Element | 한글명 | Type | Required | Length | Description
Request Header
Request Body | grant_type | 권한부여 Type | string | Y | 18 | client_credentials
appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appsecret (절대 노출되지 않도록 주의해주세요.)
Response Header
Response Body | access_token | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token
ex) "eyJ0eXUxMiJ9.eyJz…..................................."

 - 일반개인고객/일반법인고객
  . Access token 유효기간 1일
  .. 일정시간(6시간) 이내에 재호출 시에는 직전 토큰값을 리턴
  . OAuth 2.0의 Client Credentials Grant 절차를 준용

 - 제휴법인
  . Access token 유효기간 3개월
  . Refresh token 유효기간 1년
  . OAuth 2.0의 Authorization Code Grant 절차를 준용
token_type | 접근토큰유형 | string | Y | 20 | 접근토큰유형 : "Bearer"
※ API 호출 시, 접근토큰유형 "Bearer" 입력. ex) "Bearer eyJ...."
expires_in | 접근토큰 유효기간 | number | Y | 10 | 유효기간(초)
ex) 7776000
access_token_token_expired | 접근토큰 유효기간(일시표시) | string | Y | 50 | 유효기간(년:월:일 시:분:초)
ex) "2022-08-30 08:10:10"
Example
Request Example (Python) | {
  "grant_type": "client_credentials",
  "appkey": "PSg5dctL9dKPo727J13Ur405OSXXXXXXXXXX",
  "appsecret":  "yo2t8zS68zpdjGuWvFyM9VikjXE0i0CbgPEamnqPA00G0bIfrdfQb2RUD1xP7SqatQXr1cD1fGUNsb78MMXoq6o4lAYt9YTtHAjbMoFy+c72kbq5owQY1Pvp39/x6ejpJlXCj7gE3yVOB/h25Hvl+URmYeBTfrQeOqIAOYc/OIXXXXXXXXXX"
}
Response Example | {
	"access_token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6ImMwNzM1NTYzLTA1MjctNDNhZS05ODRiLTJiNWI1ZWZmOWYyMyIsImlzcyI6InVub2d3IiwiZXhwIjoxNjQ5NzUxMTAwLCJpYXQiOjE2NDE5NzUxMDAsImp0aSI6IkJTZlM0QUtSSnpRVGpmdHRtdXZlenVQUTlKajc3cHZGdjBZVyJ9.Oyt_C639yUjWmRhymlszgt6jDo8fvIKkkxH1mMngunV1T15SCC4I3Xe6MXxcY23DXunzBfR1uI0KXXXXXXXXXX",
	"access_token_token_expired":"2023-12-22 08:16:59",
	"token_type":"Bearer",
	"expires_in":86400
}
```

### 📍 [신용매수가능조회] 실시간 주문가능현금 (TTTC8908R)

```text
신용매수가능조회
API 통신방식 | REST
메뉴 위치 | [국내주식] 주문/계좌
API 명 | 신용매수가능조회
API ID | v1_국내주식-042
실전 TR_ID | TTTC8909R
모의 TR_ID | 모의투자 미지원
기본정보
HTTP Method | GET
실전 Domain | https://openapi.koreainvestment.com:9443
모의 Domain | 모의투자 미지원
URL 명 | /uapi/domestic-stock/v1/trading/inquire-credit-psamount
개요
개요 | 신용매수가능조회 API입니다.
신용매수주문 시 주문가능수량과 금액을 확인하실 수 있습니다.
Layout
구분 | Element | 한글명 | Type | Required | Length | Description
Request Header | content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8
authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token 
일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) 
법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용)
appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키
tr_id | 거래ID | string | Y | 13 | TTTC8909R
tr_cont | 연속 거래 여부 | string | N | 1 | tr_cont를 이용한 다음조회 불가 API
custtype | 고객 타입 | string | Y | 1 | B : 법인 
P : 개인
seq_no | 일련번호 | string | N | 2 | [법인 필수] 001
mac_address | 맥주소 | string | N | 12 | 법인고객 혹은 개인고객의 Mac address 값
phone_number | 핸드폰번호 | string | N | 12 | [법인 필수] 제휴사APP을 사용하는 경우 사용자(회원) 핸드폰번호 
ex) 01011112222 (하이픈 등 구분값 제거)
ip_addr | 접속 단말 공인 IP | string | N | 12 | [법인 필수] 사용자(회원)의 IP Address
gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함
Request Query Parameter | CANO | 종합계좌번호 | string | Y | 8 | 계좌번호 체계(8-2)의 앞 8자리
ACNT_PRDT_CD | 계좌상품코드 | string | Y | 2 | 계좌번호 체계(8-2)의 뒤 2자리
PDNO | 상품번호 | string | Y | 12 | 종목코드(6자리)
ORD_UNPR | 주문단가 | string | Y | 19 | 1주당 가격 
* 장전 시간외, 장후 시간외, 시장가의 경우 1주당 가격을 공란으로 비우지 않음 "0"으로 입력 권고
ORD_DVSN | 주문구분 | string | Y | 2 | 00 : 지정가 
01 : 시장가 
02 : 조건부지정가 
03 : 최유리지정가 
04 : 최우선지정가 
05 : 장전 시간외 
06 : 장후 시간외 
07 : 시간외 단일가  등
CRDT_TYPE | 신용유형 | string | Y | 2 | 21 : 자기융자신규 
23 : 유통융자신규 
26 : 유통대주상환 
28 : 자기대주상환 
25 : 자기융자상환 
27 : 유통융자상환 
22 : 유통대주신규 
24 : 자기대주신규
```

### 📍 [퇴직연금 매수가능조회] 실시간 주문가능현금 (TTTC8908R)

```text
퇴직연금 매수가능조회
API 통신방식 | REST
메뉴 위치 | [국내주식] 주문/계좌
API 명 | 퇴직연금 매수가능조회
API ID | v1_국내주식-034
실전 TR_ID | TTTC0503R
모의 TR_ID | 모의투자 미지원
기본정보
HTTP Method | GET
실전 Domain | https://openapi.koreainvestment.com:9443
모의 Domain | 모의투자 미지원
URL 명 | /uapi/domestic-stock/v1/trading/pension/inquire-psbl-order
개요
개요 | ​※ 55번 계좌(DC가입자계좌)의 경우 해당 API 이용이 불가합니다.
KIS Developers API의 경우 HTS ID에 반드시 연결되어있어야만 API 신청 및 앱정보 발급이 가능한 서비스로 개발되어서 실물계좌가 아닌 55번 계좌는 API 이용이 불가능한 점 양해 부탁드립니다.
Layout
구분 | Element | 한글명 | Type | Required | Length | Description
Request Header | content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8
authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token 
일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) 
법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용)
appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키
tr_id | 거래ID | string | Y | 13 | TTTC0503R
tr_cont | 연속 거래 여부 | string | N | 1 | tr_cont를 이용한 다음조회 불가 API
custtype | 고객 타입 | string | Y | 1 | B : 법인 
P : 개인
seq_no | 일련번호 | string | N | 2 | [법인 필수] 001
mac_address | 맥주소 | string | N | 12 | 법인고객 혹은 개인고객의 Mac address 값
phone_number | 핸드폰번호 | string | N | 12 | [법인 필수] 제휴사APP을 사용하는 경우 사용자(회원) 핸드폰번호 
ex) 01011112222 (하이픈 등 구분값 제거)
ip_addr | 접속 단말 공인 IP | string | N | 12 | [법인 필수] 사용자(회원)의 IP Address
gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함
Request Query Parameter | CANO | 종합계좌번호 | string | Y | 8
ACNT_PRDT_CD | 계좌상품코드 | string | Y | 2 | 29
PDNO | 상품번호 | string | Y | 12
ACCA_DVSN_CD | 적립금구분코드 | string | Y | 2 | 00
CMA_EVLU_AMT_ICLD_YN | CMA평가금액포함여부 | string | Y | 1
ORD_DVSN | 주문구분 | string | Y | 2 | 00 : 지정가 / 01 : 시장가
```

### 📍 [주식잔고조회] 계좌 보유종목 및 평가금액 (TTTC8434R)

```text
주식잔고조회
API 통신방식 | REST
메뉴 위치 | [국내주식] 주문/계좌
API 명 | 주식잔고조회
API ID | v1_국내주식-006
실전 TR_ID | TTTC8434R
모의 TR_ID | VTTC8434R
기본정보
HTTP Method | GET
실전 Domain | https://openapi.koreainvestment.com:9443
모의 Domain | https://openapivts.koreainvestment.com:29443
URL 명 | /uapi/domestic-stock/v1/trading/inquire-balance
개요
개요 | 주식 잔고조회 API입니다. 
실전계좌의 경우, 한 번의 호출에 최대 50건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다. 
모의계좌의 경우, 한 번의 호출에 최대 20건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다. 

* 당일 전량매도한 잔고도 보유수량 0으로 보여질 수 있으나, 해당 보유수량 0인 잔고는 최종 D-2일 이후에는 잔고에서 사라집니다.

※ 중요 
1) 해당 API는 제공 정보량이 많아 조회속도가 느린 API입니다. 주문 준비를 위해서는 주식매수/매도가능수량 조회 TR 사용을 권장 드립니다.
2) 해당 API는 과도한 트래픽이 몰릴 시 당사 시스템에 큰 제약사항을 줄 수 있는 TR로 원장 유량정책에 의거, 개인 고객 유량 무관하게 초당 120 TPS로 제한되어 있습니다.
   "EGW00215 원장에서 허용 가능한 초당 거래건수를 초과하였습니다." 메시지는 해당 사유에 의해 발생한 건이오니, 이 경우에는 재시도 처리 부탁드리겠습니다.
   * 원장 언급이 없는 "초당 거래건수를 초과하였습니다." 메시지는 개인 유량 초과 시 발생하는 메시지로 착오 없으시길 바랍니다.
Layout
구분 | Element | 한글명 | Type | Required | Length | Description
Request Header | content-type | 컨텐츠타입 | string | N | 40 | application/json; charset=utf-8
authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token
일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용)
법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용)
appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appsecret (절대 노출되지 않도록 주의해주세요.)
personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키
tr_id | 거래ID | string | Y | 13 | [실전투자]
TTTC8434R : 주식 잔고 조회

[모의투자]
VTTC8434R : 주식 잔고 조회
tr_cont | 연속 거래 여부 | string | N | 1 | 공백 : 초기 조회
N : 다음 데이터 조회 (output header의 tr_cont가 M일 경우)
custtype | 고객타입 | string | N | 1 | B : 법인
P : 개인
seq_no | 일련번호 | string | N | 2 | [법인 필수] 001
mac_address | 맥주소 | string | N | 12 | 법인고객 혹은 개인고객의 Mac address 값
phone_number | 핸드폰번호 | string | N | 12 | [법인 필수] 제휴사APP을 사용하는 경우 사용자(회원) 핸드폰번호
ex) 01011112222 (하이픈 등 구분값 제거)
ip_addr | 접속 단말 공인 IP | string | N | 12 | [법인 필수] 사용자(회원)의 IP Address
gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함
Request Query Parameter | CANO | 종합계좌번호 | string | Y | 8 | 계좌번호 체계(8-2)의 앞 8자리
ACNT_PRDT_CD | 계좌상품코드 | string | Y | 2 | 계좌번호 체계(8-2)의 뒤 2자리
AFHR_FLPR_YN | 시간외단일가, 거래소여부 | string | Y | 1 | N : 기본값,
Y : 시간외단일가,
X : NXT 정규장 (프리마켓, 메인, 애프터마켓)
※ NXT 선택 시 : NXT 거래종목만 시세 등 정보가 NXT 기준으로 변동됩니다. KRX 종목들은 그대로 유지
OFL_YN | 오프라인여부 | string | N | 1 | 공란(Default)
INQR_DVSN | 조회구분 | string | Y | 2 | 01 : 대출일별
UNPR_DVSN | 단가구분 | string | Y | 2 | 01 : 기본값
```

### 📍 [매수가능조회] 실시간 주문가능현금 (TTTC8908R)

```text
매수가능조회
API 통신방식 | REST
메뉴 위치 | [국내주식] 주문/계좌
API 명 | 매수가능조회
API ID | v1_국내주식-007
실전 TR_ID | TTTC8908R
모의 TR_ID | VTTC8908R
기본정보
HTTP Method | GET
실전 Domain | https://openapi.koreainvestment.com:9443
모의 Domain | https://openapivts.koreainvestment.com:29443
URL 명 | /uapi/domestic-stock/v1/trading/inquire-psbl-order
개요
개요 | 매수가능 조회 API입니다. 
실전계좌/모의계좌의 경우, 한 번의 호출에 최대 1건까지 확인 가능합니다.


1) 매수가능금액 확인
 . 미수 사용 X: nrcvb_buy_amt(미수없는매수금액) 확인
 . 미수 사용 O: max_buy_amt(최대매수금액) 확인


2) 매수가능수량 확인
 . 특정 종목 전량매수 시 가능수량을 확인하실 경우 ORD_DVSN:00(지정가)는 종목증거금율이 반영되지 않습니다. 
   따라서 "반드시" ORD_DVSN:01(시장가)로 지정하여 종목증거금율이 반영된 가능수량을 확인하시기 바랍니다. 

   (다만, 조건부지정가 등 특정 주문구분(ex.IOC)으로 주문 시 가능수량을 확인할 경우 주문 시와 동일한 주문구분(ex.IOC) 입력하여 가능수량 확인)

 . 미수 사용 X: ORD_DVSN:01(시장가) or 특정 주문구분(ex.IOC)로 지정하여 nrcvb_buy_qty(미수없는매수수량) 확인
 . 미수 사용 O: ORD_DVSN:01(시장가) or 특정 주문구분(ex.IOC)로 지정하여 max_buy_qty(최대매수수량) 확인
Layout
구분 | Element | 한글명 | Type | Required | Length | Description
Request Header | content-type | 컨텐츠타입 | string | N | 40 | application/json; charset=utf-8
authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token
일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용)
법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용)
appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appsecret (절대 노출되지 않도록 주의해주세요.)
personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키
tr_id | 거래ID | string | Y | 13 | [실전투자]
TTTC8908R : 매수 가능 조회

[모의투자]
VTTC8908R : 매수 가능 조회
tr_cont | 연속 거래 여부 | string | N | 1 | tr_cont를 이용한 다음조회 불가 API
custtype | 고객타입 | string | N | 1 | B : 법인
P : 개인
seq_no | 일련번호 | string | N | 2 | [법인 필수] 001
mac_address | 맥주소 | string | N | 12 | 법인고객 혹은 개인고객의 Mac address 값
phone_number | 핸드폰번호 | string | N | 12 | [법인 필수] 제휴사APP을 사용하는 경우 사용자(회원) 핸드폰번호
ex) 01011112222 (하이픈 등 구분값 제거)
ip_addr | 접속 단말 공인 IP | string | N | 12 | [법인 필수] 사용자(회원)의 IP Address
gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함
Request Query Parameter | CANO | 종합계좌번호 | string | Y | 8 | 계좌번호 체계(8-2)의 앞 8자리
ACNT_PRDT_CD | 계좌상품코드 | string | Y | 2 | 계좌번호 체계(8-2)의 뒤 2자리
PDNO | 상품번호 | string | Y | 12 | 종목번호(6자리)
* PDNO, ORD_UNPR 공란 입력 시, 매수수량 없이 매수금액만 조회됨
ORD_UNPR | 주문단가 | string | Y | 19 | 1주당 가격
* 시장가(ORD_DVSN:01)로 조회 시, 공란으로 입력
* PDNO, ORD_UNPR 공란 입력 시, 매수수량 없이 매수금액만 조회됨
ORD_DVSN | 주문구분 | string | Y | 2 | * 특정 종목 전량매수 시 가능수량을 확인할 경우
    00:지정가는 증거금율이 반영되지 않으므로
    증거금율이 반영되는 01: 시장가로 조회
* 다만, 조건부지정가 등 특정 주문구분(ex.IOC)으로 주문 시 가능수량을 확인할 경우 주문 시와 동일한 주문구분(ex.IOC) 입력하여 가능수량 확인
* 종목별 매수가능수량 조회 없이 매수금액만 조회하고자 할 경우 임의값(00) 입력
00 : 지정가
01 : 시장가
02 : 조건부지정가
03 : 최유리지정가
04 : 최우선지정가
05 : 장전 시간외
06 : 장후 시간외
07 : 시간외 단일가
08 : 자기주식
09 : 자기주식S-Option
10 : 자기주식금전신탁
11 : IOC지정가 (즉시체결,잔량취소)
12 : FOK지정가 (즉시체결,전량취소)
13 : IOC시장가 (즉시체결,잔량취소)
14 : FOK시장가 (즉시체결,전량취소)
15 : IOC최유리 (즉시체결,잔량취소)
16 : FOK최유리 (즉시체결,전량취소)
51 : 장중대량
52 : 장중바스켓
62 : 장개시전 시간외대량
63 : 장개시전 시간외바스켓
67 : 장개시전 금전신탁자사주
69 : 장개시전 자기주식
72 : 시간외대량
77 : 시간외자사주신탁
79 : 시간외대량자기주식
80 : 바스켓
CMA_EVLU_AMT_ICLD_YN | CMA평가금액포함여부 | string | Y | 1 | Y : 포함
N : 포함하지 않음
```

### 📍 [주식주문(현금)] 신규 주문 TR (구TR 폐기 대비)

```text
주식주문(현금)
API 통신방식 | REST
메뉴 위치 | [국내주식] 주문/계좌
API 명 | 주식주문(현금)
API ID | v1_국내주식-001
실전 TR_ID | (매도) TTTC0011U (매수) TTTC0012U
모의 TR_ID | (매도) VTTC0011U (매수) VTTC0012U
기본정보
HTTP Method | POST
실전 Domain | https://openapi.koreainvestment.com:9443
모의 Domain | https://openapivts.koreainvestment.com:29443
URL 명 | /uapi/domestic-stock/v1/trading/order-cash
개요
개요 | 국내주식주문(현금) API 입니다. 

※ TTC0012U(현금매수) 사용하셔서 미수매수 가능합니다. 단, 거래하시는 계좌가 증거금40%계좌로 신청이 되어있어야 가능합니다. 
※ 신용매수는 별도의 API가 준비되어 있습니다.

※ ORD_QTY(주문수량), ORD_UNPR(주문단가) 등을 String으로 전달해야 함에 유의 부탁드립니다.

※ ORD_UNPR(주문단가)가 없는 주문은 상한가로 주문금액을 선정하고 이후 체결이되면 체결금액로 정산됩니다.

※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
   (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)

※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
   https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
Layout
구분 | Element | 한글명 | Type | Required | Length | Description
Request Header | content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8
authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token 
일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) 
법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용)

※ 토큰 지정시 토큰 타입("Bearer") 지정 필요. 즉, 발급받은 접근토큰 앞에 앞에 "Bearer" 붙여서 호출
EX) "Bearer eyJ..........8GA"
appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키
tr_id | 거래ID | string | Y | 13 | '※ 구TR은 사전고지 없이 막힐 수 있으므로 반드시 신TR로 변경이용 부탁드립니다.
[실전투자]
국내주식주문 매도 : (구)TTTC0801U → (신)TTTC0011U
국내주식주문 매도(모의투자) : (구)VTTC0801U → (신)VTTC0011U
국내주식주문 매수 : (구)TTTC0802U → (신)TTTC0012U
국내주식주문 매수(모의투자) : (구)VTTC0802U → (신)VTTC0012U'
tr_cont | 연속 거래 여부 | string | N | 1 | tr_cont를 이용한 다음조회 불가 API
custtype | 고객 타입 | string | Y | 1 | B : 법인 
P : 개인
seq_no | 일련번호 | string | N | 2 | [법인 필수] 001
mac_address | 맥주소 | string | N | 12 | 법인고객 혹은 개인고객의 Mac address 값
phone_number | 핸드폰번호 | string | N | 12 | [법인 필수] 제휴사APP을 사용하는 경우 사용자(회원) 핸드폰번호 
ex) 01011112222 (하이픈 등 구분값 제거)
ip_addr | 접속 단말 공인 IP | string | N | 12 | [법인 필수] 사용자(회원)의 IP Address
gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함
Request Body | CANO | 종합계좌번호 | string | Y | 8 | 종합계좌번호
ACNT_PRDT_CD | 계좌상품코드 | string | Y | 2 | 상품유형코드
PDNO | 상품번호 | string | Y | 12 | 종목코드(6자리) , ETN의 경우 7자리 입력
SLL_TYPE | 매도유형 (매도주문 시) | string | N | 2 | 01@일반매도
02@임의매매
05@대차매도
→ 미입력시 01 일반매도로 진행
ORD_DVSN | 주문구분 | string | Y | 2 | [KRX]
00 : 지정가
01 : 시장가
02 : 조건부지정가
03 : 최유리지정가
04 : 최우선지정가
05 : 장전 시간외
06 : 장후 시간외
07 : 시간외 단일가
11 : IOC지정가 (즉시체결,잔량취소)
12 : FOK지정가 (즉시체결,전량취소)
13 : IOC시장가 (즉시체결,잔량취소)
14 : FOK시장가 (즉시체결,전량취소)
15 : IOC최유리 (즉시체결,잔량취소)
16 : FOK최유리 (즉시체결,전량취소)
21 : 중간가
22 : 스톱지정가
23 : 중간가IOC
24 : 중간가FOK

[NXT]
00 : 지정가
03 : 최유리지정가
04 : 최우선지정가
11 : IOC지정가 (즉시체결,잔량취소)
12 : FOK지정가 (즉시체결,전량취소)
13 : IOC시장가 (즉시체결,잔량취소)
14 : FOK시장가 (즉시체결,전량취소)
15 : IOC최유리 (즉시체결,잔량취소)
16 : FOK최유리 (즉시체결,전량취소)
21 : 중간가
22 : 스톱지정가
23 : 중간가IOC
24 : 중간가FOK

[SOR]
00 : 지정가
01 : 시장가
03 : 최유리지정가
04 : 최우선지정가
11 : IOC지정가 (즉시체결,잔량취소)
12 : FOK지정가 (즉시체결,전량취소)
13 : IOC시장가 (즉시체결,잔량취소)
14 : FOK시장가 (즉시체결,전량취소)
15 : IOC최유리 (즉시체결,잔량취소)
16 : FOK최유리 (즉시체결,전량취소)
ORD_QTY | 주문수량 | string | Y | 10 | 주문수량
```

### 📍 [주식잔고조회_실현손익] 계좌 보유종목 및 평가금액 (TTTC8434R)

```text
주식잔고조회_실현손익
API 통신방식 | REST
메뉴 위치 | [국내주식] 주문/계좌
API 명 | 주식잔고조회_실현손익
API ID | v1_국내주식-041
실전 TR_ID | TTTC8494R
모의 TR_ID | 모의투자 미지원
기본정보
HTTP Method | GET
실전 Domain | https://openapi.koreainvestment.com:9443
모의 Domain | 모의투자 미지원
URL 명 | /uapi/domestic-stock/v1/trading/inquire-balance-rlz-pl
개요
개요 | 주식잔고조회_실현손익 API입니다.
한국투자 HTS(eFriend Plus) [0800] 국내 체결기준잔고 화면을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
(참고: 포럼 - 공지사항 - 신규 API 추가 안내(주식잔고조회_실현손익 외 1건))
Layout
구분 | Element | 한글명 | Type | Required | Length | Description
Request Header | content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8
authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token 
일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) 
법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용)
appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키
tr_id | 거래ID | string | Y | 13 | TTTC8494R
tr_cont | 연속 거래 여부 | string | N | 1 | F or M : 다음 데이터 있음
D or E : 마지막 데이터
custtype | 고객 타입 | string | Y | 1 | B : 법인 
P : 개인
seq_no | 일련번호 | string | N | 2 | [법인 필수] 001
mac_address | 맥주소 | string | N | 12 | 법인고객 혹은 개인고객의 Mac address 값
phone_number | 핸드폰번호 | string | N | 12 | [법인 필수] 제휴사APP을 사용하는 경우 사용자(회원) 핸드폰번호 
ex) 01011112222 (하이픈 등 구분값 제거)
ip_addr | 접속 단말 공인 IP | string | N | 12 | [법인 필수] 사용자(회원)의 IP Address
gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함
Request Query Parameter | CANO | 종합계좌번호 | string | Y | 8 | 계좌번호 체계(8-2)의 앞 8자리
ACNT_PRDT_CD | 계좌상품코드 | string | Y | 2 | 계좌번호 체계(8-2)의 뒤 2자리
AFHR_FLPR_YN | 시간외단일가여부 | string | Y | 1 | 'N : 기본값 
Y : 시간외단일가'
OFL_YN | 오프라인여부 | string | Y | 1 | 공란
INQR_DVSN | 조회구분 | string | Y | 2 | 00 : 전체
UNPR_DVSN | 단가구분 | string | Y | 2 | 01 : 기본값
```

### 📍 [주식현재가 시세] 실시간 호가/현재가 (FHKST01010100)

```text
주식현재가 시세
API 통신방식 | REST
메뉴 위치 | [국내주식] 기본시세
API 명 | 주식현재가 시세
API ID | v1_국내주식-008
실전 TR_ID | FHKST01010100
모의 TR_ID | FHKST01010100
기본정보
HTTP Method | GET
실전 Domain | https://openapi.koreainvestment.com:9443
모의 Domain | https://openapivts.koreainvestment.com:29443
URL 명 | /uapi/domestic-stock/v1/quotations/inquire-price
개요
개요 | 주식 현재가 시세 API입니다. 실시간 시세를 원하신다면 웹소켓 API를 활용하세요.

※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
   https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info
Layout
구분 | Element | 한글명 | Type | Required | Length | Description
Request Header | content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8
authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token 
일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) 
법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용)
appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키
tr_id | 거래ID | string | Y | 13 | FHKST01010100
tr_cont | 연속 거래 여부 | string | N | 1 | tr_cont를 이용한 다음조회 불가 API
custtype | 고객 타입 | string | Y | 1 | B : 법인 
P : 개인
seq_no | 일련번호 | string | N | 2 | [법인 필수] 001
mac_address | 맥주소 | string | N | 12 | 법인고객 혹은 개인고객의 Mac address 값
phone_number | 핸드폰번호 | string | N | 12 | [법인 필수] 제휴사APP을 사용하는 경우 사용자(회원) 핸드폰번호 
ex) 01011112222 (하이픈 등 구분값 제거)
ip_addr | 접속 단말 공인 IP | string | N | 12 | [법인 필수] 사용자(회원)의 IP Address
gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함
Request Query Parameter | FID_COND_MRKT_DIV_CODE | 조건 시장 분류 코드 | string | Y | 2 | J:KRX, NX:NXT, UN:통합
FID_INPUT_ISCD | 입력 종목코드 | string | Y | 12 | 종목코드 (ex 005930 삼성전자)  // ETN은 종목코드 6자리 앞에 Q 입력 필수
Response Header | content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8
tr_id | 거래ID | string | Y | 13 | 요청한 tr_id
tr_cont | 연속 거래 여부 | string | N | 1 | tr_cont를 이용한 다음조회 불가 API
gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함
```

### 📍 [주식현재가 시세2] 실시간 호가/현재가 (FHKST01010100)

```text
주식현재가 시세2
API 통신방식 | REST
메뉴 위치 | [국내주식] 기본시세
API 명 | 주식현재가 시세2
API ID | v1_국내주식-054
실전 TR_ID | FHPST01010000
모의 TR_ID | 모의투자 미지원
기본정보
HTTP Method | GET
실전 Domain | https://openapi.koreainvestment.com:9443
모의 Domain | 모의투자 미지원
URL 명 | /uapi/domestic-stock/v1/quotations/inquire-price-2
개요
개요 | 주식현재가 시세2 API입니다.
Layout
구분 | Element | 한글명 | Type | Required | Length | Description
Request Header | content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8
authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token 
일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) 
법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용)
appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키
tr_id | 거래ID | string | Y | 13 | FHPST01010000
tr_cont | 연속 거래 여부 | string | N | 1 | tr_cont를 이용한 다음조회 불가 API
custtype | 고객 타입 | string | Y | 1 | B : 법인 
P : 개인
seq_no | 일련번호 | string | N | 2 | [법인 필수] 001
mac_address | 맥주소 | string | N | 12 | 법인고객 혹은 개인고객의 Mac address 값
phone_number | 핸드폰번호 | string | N | 12 | [법인 필수] 제휴사APP을 사용하는 경우 사용자(회원) 핸드폰번호 
ex) 01011112222 (하이픈 등 구분값 제거)
ip_addr | 접속 단말 공인 IP | string | N | 12 | [법인 필수] 사용자(회원)의 IP Address
gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함
Request Query Parameter | FID_COND_MRKT_DIV_CODE | FID 조건 시장 분류 코드 | string | Y | 2 | J:KRX, NX:NXT, UN:통합
FID_INPUT_ISCD | FID 입력 종목코드 | string | Y | 12 | 000660
Response Header | content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8
tr_id | 거래ID | string | Y | 13 | 요청한 tr_id
tr_cont | 연속 거래 여부 | string | N | 1 | tr_cont를 이용한 다음조회 불가 API
gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함
```

### 📍 [국내휴장일조회] 연간 개장일 일괄 판정 (CTCA0903R)

```text
국내휴장일조회
API 통신방식 | REST
메뉴 위치 | [국내주식] 업종/기타
API 명 | 국내휴장일조회
API ID | 국내주식-040
실전 TR_ID | CTCA0903R
모의 TR_ID | 모의투자 미지원
기본정보
HTTP Method | GET
실전 Domain | https://openapi.koreainvestment.com:9443
모의 Domain | 모의투자 미지원
URL 명 | /uapi/domestic-stock/v1/quotations/chk-holiday
개요
개요 | (★중요) 국내휴장일조회(TCA0903R) 서비스는 당사 원장서비스와 연관되어 있어 
단시간 내 다수 호출시 서비스에 영향을 줄 수 있어 가급적 1일 1회 호출 부탁드립니다.

국내휴장일조회 API입니다.
영업일, 거래일, 개장일, 결제일 여부를 조회할 수 있습니다.
주문을 넣을 수 있는지 확인하고자 하실 경우 개장일여부(opnd_yn)을 사용하시면 됩니다.
Layout
구분 | Element | 한글명 | Type | Required | Length | Description
Request Header | content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8
authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token 
일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) 
법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용)
appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키
tr_id | 거래ID | string | Y | 13 | CTCA0903R
tr_cont | 연속 거래 여부 | string | N | 1 | tr_cont를 이용한 다음조회 불가 API
custtype | 고객 타입 | string | Y | 1 | B : 법인 
P : 개인
seq_no | 일련번호 | string | N | 2 | [법인 필수] 001
mac_address | 맥주소 | string | N | 12 | 법인고객 혹은 개인고객의 Mac address 값
phone_number | 핸드폰번호 | string | N | 12 | [법인 필수] 제휴사APP을 사용하는 경우 사용자(회원) 핸드폰번호 
ex) 01011112222 (하이픈 등 구분값 제거)
ip_addr | 접속 단말 공인 IP | string | N | 12 | [법인 필수] 사용자(회원)의 IP Address
gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함
Request Query Parameter | BASS_DT | 기준일자 | string | Y | 8 | 기준일자(YYYYMMDD)
CTX_AREA_NK | 연속조회키 | string | Y | 20 | 공백으로 입력
CTX_AREA_FK | 연속조회검색조건 | string | Y | 20 | 공백으로 입력
Response Header | content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8
tr_id | 거래ID | string | Y | 13 | 요청한 tr_id
tr_cont | 연속 거래 여부 | string | N | 1 | tr_cont를 이용한 다음조회 불가 API
```

### 📍 [장내채권 매수가능조회] 실시간 주문가능현금 (TTTC8908R)

```text
장내채권 매수가능조회
API 통신방식 | REST
메뉴 위치 | [장내채권] 주문/계좌
API 명 | 장내채권 매수가능조회
API ID | 국내주식-199
실전 TR_ID | TTTC8910R
모의 TR_ID | 모의투자 미지원
기본정보
HTTP Method | GET
실전 Domain | https://openapi.koreainvestment.com:9443
모의 Domain | 모의투자 미지원
URL 명 | /uapi/domestic-bond/v1/trading/inquire-psbl-order
개요
개요 | 장내채권 매수가능조회 API입니다. 
한국투자 HTS(eFriend Plus) &gt; [0978] 장내채권주문 화면의 "왼쪽 하단 증거금 사용가능 내역 / 주문가능금액 및 수량" 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다. 

※ (중요) 채권의 경우 주식과 달리, 매수가능수량(buy_psbl_qty) = 매수가능금액(buy_psbl_amt) / 채권주문단가2(bond_ord_unpr2) * 10 인 점 유의하시기 바랍니다.
Layout
구분 | Element | 한글명 | Type | Required | Length | Description
Request Header | content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8
authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token 
일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) 
법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용)
appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.)
personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키
tr_id | 거래ID | string | Y | 13 | TTTC8910R
tr_cont | 연속 거래 여부 | string | N | 1 | tr_cont를 이용한 다음조회 불가 API
custtype | 고객 타입 | string | Y | 1 | B : 법인 
P : 개인
seq_no | 일련번호 | string | N | 2 | [법인 필수] 001
mac_address | 맥주소 | string | N | 12 | 법인고객 혹은 개인고객의 Mac address 값
phone_number | 핸드폰번호 | string | N | 12 | [법인 필수] 제휴사APP을 사용하는 경우 사용자(회원) 핸드폰번호 
ex) 01011112222 (하이픈 등 구분값 제거)
ip_addr | 접속 단말 공인 IP | string | N | 12 | [법인 필수] 사용자(회원)의 IP Address
gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함
Request Query Parameter | CANO | 종합계좌번호 | string | Y | 8
ACNT_PRDT_CD | 계좌상품코드 | string | Y | 2
PDNO | 상품번호 | string | Y | 12
BOND_ORD_UNPR | 채권주문단가 | string | Y | 182
SAMT_MKET_PTCI_YN | 소액시장참여여부 | string | Y | 1 | Y(소액시장) N (일반시장)
Response Header | content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8
```

---

## 📌 3. 전체 339개 API 카테고리별 시트 색인 목록

| 번호 | 시트명 (API 기능) | 주요 내용 |
| :---: | :--- | :--- |
| 1 | `API 목록` | KIS Developers 공식 API 명세 |
| 2 | `실시간 (웹소켓) 접속키 발급` | KIS Developers 공식 API 명세 |
| 3 | `접근토큰폐기(P)` | KIS Developers 공식 API 명세 |
| 4 | `접근토큰발급(P)` | KIS Developers 공식 API 명세 |
| 5 | `기간별계좌권리현황조회` | KIS Developers 공식 API 명세 |
| 6 | `투자계좌자산현황조회` | KIS Developers 공식 API 명세 |
| 7 | `퇴직연금 예수금조회` | KIS Developers 공식 API 명세 |
| 8 | `주식예약주문정정취소` | KIS Developers 공식 API 명세 |
| 9 | `신용매수가능조회` | KIS Developers 공식 API 명세 |
| 10 | `주식통합증거금 현황` | KIS Developers 공식 API 명세 |
| 11 | `퇴직연금 미체결내역` | KIS Developers 공식 API 명세 |
| 12 | `기간별매매손익현황조회` | KIS Developers 공식 API 명세 |
| 13 | `주식주문(정정취소)` | KIS Developers 공식 API 명세 |
| 14 | `주식예약주문조회` | KIS Developers 공식 API 명세 |
| 15 | `퇴직연금 매수가능조회` | KIS Developers 공식 API 명세 |
| 16 | `주식잔고조회` | KIS Developers 공식 API 명세 |
| 17 | `퇴직연금 체결기준잔고` | KIS Developers 공식 API 명세 |
| 18 | `매수가능조회` | KIS Developers 공식 API 명세 |
| 19 | `기간별손익일별합산조회` | KIS Developers 공식 API 명세 |
| 20 | `주식주문(현금)` | KIS Developers 공식 API 명세 |
| 21 | `매도가능수량조회` | KIS Developers 공식 API 명세 |
| 22 | `주식일별주문체결조회` | KIS Developers 공식 API 명세 |
| 23 | `주식정정취소가능주문조회` | KIS Developers 공식 API 명세 |
| 24 | `주식예약주문` | KIS Developers 공식 API 명세 |
| 25 | `주식주문(신용)` | KIS Developers 공식 API 명세 |
| 26 | `퇴직연금 잔고조회` | KIS Developers 공식 API 명세 |
| 27 | `주식잔고조회_실현손익` | KIS Developers 공식 API 명세 |
| 28 | `주식현재가 일자별` | KIS Developers 공식 API 명세 |
| 29 | `주식현재가 시세` | KIS Developers 공식 API 명세 |
| 30 | `국내주식 시간외현재가` | KIS Developers 공식 API 명세 |
| 31 | `ETF 구성종목시세` | KIS Developers 공식 API 명세 |
| 32 | `주식현재가 시간외시간별체결` | KIS Developers 공식 API 명세 |
| 33 | `NAV 비교추이(종목)` | KIS Developers 공식 API 명세 |
| 34 | `주식현재가 시간외일자별주가` | KIS Developers 공식 API 명세 |
| 35 | `국내주식 시간외호가` | KIS Developers 공식 API 명세 |
| 36 | `주식현재가 당일시간대별체결` | KIS Developers 공식 API 명세 |
| 37 | `주식현재가 시세2` | KIS Developers 공식 API 명세 |
| 38 | `ETF 현재가 호가` | KIS Developers 공식 API 명세 |
| 39 | `주식일별분봉조회` | KIS Developers 공식 API 명세 |
| 40 | `국내주식기간별시세(일_주_월_년)` | KIS Developers 공식 API 명세 |
| 41 | `NAV 비교추이(일)` | KIS Developers 공식 API 명세 |
| 42 | `주식현재가 호가_예상체결` | KIS Developers 공식 API 명세 |
| 43 | `주식현재가 체결` | KIS Developers 공식 API 명세 |
| 44 | `주식현재가 회원사` | KIS Developers 공식 API 명세 |
| 45 | `NAV 비교추이(분)` | KIS Developers 공식 API 명세 |
| 46 | `주식현재가 투자자` | KIS Developers 공식 API 명세 |
| 47 | `ETF_ETN 현재가` | KIS Developers 공식 API 명세 |
| 48 | `국내주식 장마감 예상체결가` | KIS Developers 공식 API 명세 |
| 49 | `주식당일분봉조회` | KIS Developers 공식 API 명세 |
| 50 | `ELW 현재가 시세` | KIS Developers 공식 API 명세 |
| 51 | `ELW 신규상장종목` | KIS Developers 공식 API 명세 |
| 52 | `ELW 투자지표추이(일별)` | KIS Developers 공식 API 명세 |
| 53 | `ELW 민감도 순위` | KIS Developers 공식 API 명세 |
| 54 | `ELW 기초자산별 종목시세` | KIS Developers 공식 API 명세 |
| 55 | `ELW 종목검색` | KIS Developers 공식 API 명세 |
| 56 | `ELW 변동성 추이(분별)` | KIS Developers 공식 API 명세 |
| 57 | `ELW 변동성추이(체결)` | KIS Developers 공식 API 명세 |
| 58 | `ELW 당일급변종목` | KIS Developers 공식 API 명세 |
| 59 | `ELW 투자지표추이(분별)` | KIS Developers 공식 API 명세 |
| 60 | `ELW 기초자산 목록조회` | KIS Developers 공식 API 명세 |
| 61 | `ELW 변동성 추이(일별)` | KIS Developers 공식 API 명세 |
| 62 | `ELW 거래량순위` | KIS Developers 공식 API 명세 |
| 63 | `ELW 지표순위` | KIS Developers 공식 API 명세 |
| 64 | `ELW 투자지표추이(체결)` | KIS Developers 공식 API 명세 |
| 65 | `ELW 상승률순위` | KIS Developers 공식 API 명세 |
| 66 | `ELW 민감도 추이(일별)` | KIS Developers 공식 API 명세 |
| 67 | `ELW 비교대상종목조회` | KIS Developers 공식 API 명세 |
| 68 | `ELW 만기예정_만기종목` | KIS Developers 공식 API 명세 |
| 69 | `ELW LP매매추이` | KIS Developers 공식 API 명세 |
| 70 | `ELW 민감도 추이(체결)` | KIS Developers 공식 API 명세 |
| 71 | `ELW 변동성 추이(틱)` | KIS Developers 공식 API 명세 |
| 72 | `국내주식 예상체결지수 추이` | KIS Developers 공식 API 명세 |
| 73 | `국내주식업종기간별시세(일_주_월_년)` | KIS Developers 공식 API 명세 |
| 74 | `국내업종 시간별지수(분)` | KIS Developers 공식 API 명세 |
| 75 | `국내업종 구분별전체시세` | KIS Developers 공식 API 명세 |
| 76 | `업종 분봉조회` | KIS Developers 공식 API 명세 |
| 77 | `국내휴장일조회` | KIS Developers 공식 API 명세 |
| 78 | `국내주식 예상체결 전체지수` | KIS Developers 공식 API 명세 |
| 79 | `국내업종 현재지수` | KIS Developers 공식 API 명세 |
| 80 | `국내선물 영업일조회` | KIS Developers 공식 API 명세 |
| 81 | `국내업종 시간별지수(초)` | KIS Developers 공식 API 명세 |
| 82 | `국내업종 일자별지수` | KIS Developers 공식 API 명세 |
| 83 | `금리 종합(국내채권_금리)` | KIS Developers 공식 API 명세 |
| 84 | `변동성완화장치(VI) 현황` | KIS Developers 공식 API 명세 |
| 85 | `종합 시황_공시(제목)` | KIS Developers 공식 API 명세 |
| 86 | `상품기본조회` | KIS Developers 공식 API 명세 |
| 87 | `예탁원정보(상장정보일정)` | KIS Developers 공식 API 명세 |
| 88 | `예탁원정보(공모주청약일정)` | KIS Developers 공식 API 명세 |
| 89 | `국내주식 재무비율` | KIS Developers 공식 API 명세 |
| 90 | `예탁원정보(자본감소일정)` | KIS Developers 공식 API 명세 |
| 91 | `예탁원정보(무상증자일정)` | KIS Developers 공식 API 명세 |
| 92 | `국내주식 증권사별 투자의견` | KIS Developers 공식 API 명세 |
| 93 | `국내주식 당사 신용가능종목` | KIS Developers 공식 API 명세 |
| 94 | `예탁원정보(주식매수청구일정)` | KIS Developers 공식 API 명세 |
| 95 | `예탁원정보(액면교체일정)` | KIS Developers 공식 API 명세 |
| 96 | `예탁원정보(배당일정)` | KIS Developers 공식 API 명세 |
| 97 | `국내주식 종목투자의견` | KIS Developers 공식 API 명세 |
| 98 | `국내주식 안정성비율` | KIS Developers 공식 API 명세 |
| 99 | `국내주식 수익성비율` | KIS Developers 공식 API 명세 |
| 100 | `예탁원정보(실권주일정)` | KIS Developers 공식 API 명세 |
| 101 | `예탁원정보(의무예치일정)` | KIS Developers 공식 API 명세 |
| 102 | `국내주식 손익계산서` | KIS Developers 공식 API 명세 |
| 103 | `당사 대주가능 종목` | KIS Developers 공식 API 명세 |
| 104 | `주식기본조회` | KIS Developers 공식 API 명세 |
| 105 | `예탁원정보(유상증자일정)` | KIS Developers 공식 API 명세 |
| 106 | `예탁원정보(주주총회일정)` | KIS Developers 공식 API 명세 |
| 107 | `국내주식 성장성비율` | KIS Developers 공식 API 명세 |
| 108 | `국내주식 대차대조표` | KIS Developers 공식 API 명세 |
| 109 | `예탁원정보(합병_분할일정)` | KIS Developers 공식 API 명세 |
| 110 | `국내주식 종목추정실적` | KIS Developers 공식 API 명세 |
| 111 | `국내주식 기타주요비율` | KIS Developers 공식 API 명세 |
| 112 | `프로그램매매 종합현황(시간)` | KIS Developers 공식 API 명세 |
| 113 | `국내주식 신용잔고 일별추이` | KIS Developers 공식 API 명세 |
| 114 | `시장별 투자자매매동향(일별)` | KIS Developers 공식 API 명세 |
| 115 | `국내주식 공매도 일별추이` | KIS Developers 공식 API 명세 |
| 116 | `종목별 투자자매매동향(일별)` | KIS Developers 공식 API 명세 |
| 117 | `종목조건검색 목록조회` | KIS Developers 공식 API 명세 |
| 118 | `국내주식 상하한가 포착` | KIS Developers 공식 API 명세 |
| 119 | `프로그램매매 종합현황(일별)` | KIS Developers 공식 API 명세 |
| 120 | `종목별 일별 대차거래추이` | KIS Developers 공식 API 명세 |
| 121 | `종목조건검색조회` | KIS Developers 공식 API 명세 |
| 122 | `국내주식 매물대_거래비중` | KIS Developers 공식 API 명세 |
| 123 | `국내기관_외국인 매매종목가집계` | KIS Developers 공식 API 명세 |
| 124 | `관심종목 그룹별 종목조회` | KIS Developers 공식 API 명세 |
| 125 | `주식현재가 회원사 종목매매동향` | KIS Developers 공식 API 명세 |
| 126 | `종목별 프로그램매매추이(일별)` | KIS Developers 공식 API 명세 |
| 127 | `관심종목 그룹조회` | KIS Developers 공식 API 명세 |
| 128 | `종목별 외인기관 추정가집계` | KIS Developers 공식 API 명세 |
| 129 | `종목별일별매수매도체결량` | KIS Developers 공식 API 명세 |
| 130 | `국내주식 체결금액별 매매비중` | KIS Developers 공식 API 명세 |
| 131 | `프로그램매매 투자자매매동향(당일)` | KIS Developers 공식 API 명세 |
| 132 | `국내 증시자금 종합` | KIS Developers 공식 API 명세 |
| 133 | `국내주식 예상체결가 추이` | KIS Developers 공식 API 명세 |
| 134 | `회원사 실시간 매매동향(틱)` | KIS Developers 공식 API 명세 |
| 135 | `시장별 투자자매매동향(시세)` | KIS Developers 공식 API 명세 |
| 136 | `종목별 프로그램매매추이(체결)` | KIS Developers 공식 API 명세 |
| 137 | `외국계 매매종목 가집계` | KIS Developers 공식 API 명세 |
| 138 | `국내주식 시간외예상체결등락률` | KIS Developers 공식 API 명세 |
| 139 | `종목별 외국계 순매수추이` | KIS Developers 공식 API 명세 |
| 140 | `관심종목(멀티종목) 시세조회` | KIS Developers 공식 API 명세 |
| 141 | `국내주식 예상체결 상승_하락상위` | KIS Developers 공식 API 명세 |
| 142 | `국내주식 호가잔량 순위` | KIS Developers 공식 API 명세 |
| 143 | `국내주식 신용잔고 상위` | KIS Developers 공식 API 명세 |
| 144 | `국내주식 시간외거래량순위` | KIS Developers 공식 API 명세 |
| 145 | `국내주식 배당률 상위` | KIS Developers 공식 API 명세 |
| 146 | `국내주식 시간외잔량 순위` | KIS Developers 공식 API 명세 |
| 147 | `국내주식 공매도 상위종목` | KIS Developers 공식 API 명세 |
| 148 | `국내주식 이격도 순위` | KIS Developers 공식 API 명세 |
| 149 | `HTS조회상위20종목` | KIS Developers 공식 API 명세 |
| 150 | `거래량순위` | KIS Developers 공식 API 명세 |
| 151 | `국내주식 수익자산지표 순위` | KIS Developers 공식 API 명세 |
| 152 | `국내주식 신고_신저근접종목 상위` | KIS Developers 공식 API 명세 |
| 153 | `국내주식 우선주_괴리율 상위` | KIS Developers 공식 API 명세 |
| 154 | `국내주식 대량체결건수 상위` | KIS Developers 공식 API 명세 |
| 155 | `국내주식 재무비율 순위` | KIS Developers 공식 API 명세 |
| 156 | `국내주식 시가총액 상위` | KIS Developers 공식 API 명세 |
| 157 | `국내주식 당사매매종목 상위` | KIS Developers 공식 API 명세 |
| 158 | `국내주식 등락률 순위` | KIS Developers 공식 API 명세 |
| 159 | `국내주식 시장가치 순위` | KIS Developers 공식 API 명세 |
| 160 | `국내주식 관심종목등록 상위` | KIS Developers 공식 API 명세 |
| 161 | `국내주식 체결강도 상위` | KIS Developers 공식 API 명세 |
| 162 | `국내주식 시간외등락율순위` | KIS Developers 공식 API 명세 |
| 163 | `국내지수 실시간예상체결` | KIS Developers 공식 API 명세 |
| 164 | `국내주식 장운영정보 (통합)` | KIS Developers 공식 API 명세 |
| 165 | `국내주식 실시간회원사 (NXT)` | KIS Developers 공식 API 명세 |
| 166 | `국내주식 실시간체결통보` | KIS Developers 공식 API 명세 |
| 167 | `국내주식 시간외 실시간예상체결 (KRX)` | KIS Developers 공식 API 명세 |
| 168 | `국내주식 시간외 실시간호가 (KRX)` | KIS Developers 공식 API 명세 |
| 169 | `국내주식 실시간프로그램매매 (통합)` | KIS Developers 공식 API 명세 |
| 170 | `국내주식 실시간호가 (통합)` | KIS Developers 공식 API 명세 |
| 171 | `국내주식 실시간프로그램매매 (KRX)` | KIS Developers 공식 API 명세 |
| 172 | `국내주식 장운영정보 (KRX)` | KIS Developers 공식 API 명세 |
| 173 | `국내주식 실시간체결가 (KRX)` | KIS Developers 공식 API 명세 |
| 174 | `국내지수 실시간프로그램매매` | KIS Developers 공식 API 명세 |
| 175 | `국내주식 실시간회원사 (통합)` | KIS Developers 공식 API 명세 |
| 176 | `국내지수 실시간체결` | KIS Developers 공식 API 명세 |
| 177 | `국내주식 실시간예상체결 (KRX)` | KIS Developers 공식 API 명세 |
| 178 | `ELW 실시간호가` | KIS Developers 공식 API 명세 |
| 179 | `국내주식 실시간호가 (KRX)` | KIS Developers 공식 API 명세 |
| 180 | `국내주식 실시간체결가 (통합)` | KIS Developers 공식 API 명세 |
| 181 | `국내주식 실시간호가 (NXT)` | KIS Developers 공식 API 명세 |
| 182 | `국내주식 실시간프로그램매매 (NXT)` | KIS Developers 공식 API 명세 |
| 183 | `국내주식 실시간체결가 (NXT)` | KIS Developers 공식 API 명세 |
| 184 | `ELW 실시간체결가` | KIS Developers 공식 API 명세 |
| 185 | `ELW 실시간예상체결` | KIS Developers 공식 API 명세 |
| 186 | `국내주식 실시간예상체결 (NXT)` | KIS Developers 공식 API 명세 |
| 187 | `국내주식 실시간회원사 (KRX)` | KIS Developers 공식 API 명세 |
| 188 | `국내주식 실시간예상체결 (통합)` | KIS Developers 공식 API 명세 |
| 189 | `국내주식 장운영정보 (NXT)` | KIS Developers 공식 API 명세 |
| 190 | `국내ETF NAV추이` | KIS Developers 공식 API 명세 |
| 191 | `국내주식 시간외 실시간체결가 (KRX)` | KIS Developers 공식 API 명세 |
| 192 | `(야간)선물옵션 증거금 상세` | KIS Developers 공식 API 명세 |
| 193 | `선물옵션 총자산현황` | KIS Developers 공식 API 명세 |
| 194 | `선물옵션기간약정수수료일별` | KIS Developers 공식 API 명세 |
| 195 | `(야간)선물옵션 잔고현황` | KIS Developers 공식 API 명세 |
| 196 | `선물옵션 잔고현황` | KIS Developers 공식 API 명세 |
| 197 | `선물옵션 주문` | KIS Developers 공식 API 명세 |
| 198 | `선물옵션 잔고평가손익내역` | KIS Developers 공식 API 명세 |
| 199 | `선물옵션 증거금률` | KIS Developers 공식 API 명세 |
| 200 | `선물옵션 정정취소주문` | KIS Developers 공식 API 명세 |
| 201 | `선물옵션 주문체결내역조회` | KIS Developers 공식 API 명세 |
| 202 | `(야간)선물옵션 주문체결 내역조회` | KIS Developers 공식 API 명세 |
| 203 | `(야간)선물옵션 주문가능 조회` | KIS Developers 공식 API 명세 |
| 204 | `선물옵션 잔고정산손익내역` | KIS Developers 공식 API 명세 |
| 205 | `선물옵션 주문가능` | KIS Developers 공식 API 명세 |
| 206 | `선물옵션 기준일체결내역` | KIS Developers 공식 API 명세 |
| 207 | `선물옵션 시세` | KIS Developers 공식 API 명세 |
| 208 | `국내선물 기초자산 시세` | KIS Developers 공식 API 명세 |
| 209 | `선물옵션 일중예상체결추이` | KIS Developers 공식 API 명세 |
| 210 | `선물옵션기간별시세(일_주_월_년)` | KIS Developers 공식 API 명세 |
| 211 | `국내옵션전광판_선물` | KIS Developers 공식 API 명세 |
| 212 | `선물옵션 분봉조회` | KIS Developers 공식 API 명세 |
| 213 | `국내옵션전광판_옵션월물리스트` | KIS Developers 공식 API 명세 |
| 214 | `선물옵션 시세호가` | KIS Developers 공식 API 명세 |
| 215 | `국내옵션전광판_콜풋` | KIS Developers 공식 API 명세 |
| 216 | `주식옵션 실시간호가` | KIS Developers 공식 API 명세 |
| 217 | `선물옵션 실시간체결통보` | KIS Developers 공식 API 명세 |
| 218 | `KRX야간선물 실시간종목체결` | KIS Developers 공식 API 명세 |
| 219 | `KRX야간선물 실시간호가` | KIS Developers 공식 API 명세 |
| 220 | `KRX야간옵션 실시간체결가` | KIS Developers 공식 API 명세 |
| 221 | `KRX야간옵션실시간예상체결` | KIS Developers 공식 API 명세 |
| 222 | `지수선물 실시간체결가` | KIS Developers 공식 API 명세 |
| 223 | `주식선물 실시간예상체결` | KIS Developers 공식 API 명세 |
| 224 | `KRX야간옵션실시간체결통보` | KIS Developers 공식 API 명세 |
| 225 | `KRX야간선물 실시간체결통보` | KIS Developers 공식 API 명세 |
| 226 | `상품선물 실시간체결가` | KIS Developers 공식 API 명세 |
| 227 | `지수선물 실시간호가` | KIS Developers 공식 API 명세 |
| 228 | `지수옵션  실시간체결가` | KIS Developers 공식 API 명세 |
| 229 | `KRX야간옵션 실시간호가` | KIS Developers 공식 API 명세 |
| 230 | `상품선물 실시간호가` | KIS Developers 공식 API 명세 |
| 231 | `주식옵션 실시간예상체결` | KIS Developers 공식 API 명세 |
| 232 | `주식선물 실시간호가` | KIS Developers 공식 API 명세 |
| 233 | `주식옵션 실시간체결가` | KIS Developers 공식 API 명세 |
| 234 | `지수옵션 실시간호가` | KIS Developers 공식 API 명세 |
| 235 | `주식선물 실시간체결가` | KIS Developers 공식 API 명세 |
| 236 | `해외주식 잔고` | KIS Developers 공식 API 명세 |
| 237 | `해외주식 체결기준현재잔고` | KIS Developers 공식 API 명세 |
| 238 | `해외주식 지정가체결내역조회` | KIS Developers 공식 API 명세 |
| 239 | `해외주식 기간손익` | KIS Developers 공식 API 명세 |
| 240 | `해외주식 매수가능금액조회` | KIS Developers 공식 API 명세 |
| 241 | `해외주식 정정취소주문` | KIS Developers 공식 API 명세 |
| 242 | `해외주식 예약주문접수` | KIS Developers 공식 API 명세 |
| 243 | `해외주식 미체결내역` | KIS Developers 공식 API 명세 |
| 244 | `해외주식 미국주간정정취소` | KIS Developers 공식 API 명세 |
| 245 | `해외주식 주문체결내역` | KIS Developers 공식 API 명세 |
| 246 | `해외주식 결제기준잔고` | KIS Developers 공식 API 명세 |
| 247 | `해외주식 일별거래내역` | KIS Developers 공식 API 명세 |
| 248 | `해외주식 미국주간주문` | KIS Developers 공식 API 명세 |
| 249 | `해외주식 예약주문조회` | KIS Developers 공식 API 명세 |
| 250 | `해외주식 주문` | KIS Developers 공식 API 명세 |
| 251 | `해외주식 예약주문접수취소` | KIS Developers 공식 API 명세 |
| 252 | `해외주식 지정가주문번호조회` | KIS Developers 공식 API 명세 |
| 253 | `해외증거금 통화별조회` | KIS Developers 공식 API 명세 |
| 254 | `해외주식 체결추이` | KIS Developers 공식 API 명세 |
| 255 | `해외주식 기간별시세` | KIS Developers 공식 API 명세 |
| 256 | `해외결제일자조회` | KIS Developers 공식 API 명세 |
| 257 | `해외주식 현재체결가` | KIS Developers 공식 API 명세 |
| 258 | `해외주식 복수종목 시세조회` | KIS Developers 공식 API 명세 |
| 259 | `해외주식조건검색` | KIS Developers 공식 API 명세 |
| 260 | `해외주식 상품기본정보` | KIS Developers 공식 API 명세 |
| 261 | `해외지수분봉조회` | KIS Developers 공식 API 명세 |
| 262 | `해외주식분봉조회` | KIS Developers 공식 API 명세 |
| 263 | `해외주식 현재가상세` | KIS Developers 공식 API 명세 |
| 264 | `해외주식 업종별코드조회` | KIS Developers 공식 API 명세 |
| 265 | `해외주식 종목_지수_환율기간별시세(일_주_월_년)` | KIS Developers 공식 API 명세 |
| 266 | `해외주식 업종별시세` | KIS Developers 공식 API 명세 |
| 267 | `해외주식 현재가 호가` | KIS Developers 공식 API 명세 |
| 268 | `해외주식 거래증가율순위` | KIS Developers 공식 API 명세 |
| 269 | `해외주식 기간별권리조회` | KIS Developers 공식 API 명세 |
| 270 | `해외주식 가격급등락` | KIS Developers 공식 API 명세 |
| 271 | `해외주식 거래대금순위` | KIS Developers 공식 API 명세 |
| 272 | `해외주식 거래량급증` | KIS Developers 공식 API 명세 |
| 273 | `해외주식 신고_신저가` | KIS Developers 공식 API 명세 |
| 274 | `해외주식 매수체결강도상위` | KIS Developers 공식 API 명세 |
| 275 | `해외주식 거래회전율순위` | KIS Developers 공식 API 명세 |
| 276 | `해외뉴스종합(제목)` | KIS Developers 공식 API 명세 |
| 277 | `당사 해외주식담보대출 가능 종목` | KIS Developers 공식 API 명세 |
| 278 | `해외주식 시가총액순위` | KIS Developers 공식 API 명세 |
| 279 | `해외속보(제목)` | KIS Developers 공식 API 명세 |
| 280 | `해외주식 상승율_하락율` | KIS Developers 공식 API 명세 |
| 281 | `해외주식 권리종합` | KIS Developers 공식 API 명세 |
| 282 | `해외주식 거래량순위` | KIS Developers 공식 API 명세 |
| 283 | `해외주식 실시간호가` | KIS Developers 공식 API 명세 |
| 284 | `해외주식 지연호가(아시아)` | KIS Developers 공식 API 명세 |
| 285 | `해외주식 실시간지연체결가` | KIS Developers 공식 API 명세 |
| 286 | `해외주식 실시간체결통보` | KIS Developers 공식 API 명세 |
| 287 | `해외선물옵션 주문` | KIS Developers 공식 API 명세 |
| 288 | `해외선물옵션 정정취소주문` | KIS Developers 공식 API 명세 |
| 289 | `해외선물옵션 당일주문내역조회` | KIS Developers 공식 API 명세 |
| 290 | `해외선물옵션 미결제내역조회(잔고)` | KIS Developers 공식 API 명세 |
| 291 | `해외선물옵션 주문가능조회` | KIS Developers 공식 API 명세 |
| 292 | `해외선물옵션 기간계좌손익 일별` | KIS Developers 공식 API 명세 |
| 293 | `해외선물옵션 일별 체결내역` | KIS Developers 공식 API 명세 |
| 294 | `해외선물옵션 예수금현황` | KIS Developers 공식 API 명세 |
| 295 | `해외선물옵션 일별 주문내역` | KIS Developers 공식 API 명세 |
| 296 | `해외선물옵션 기간계좌거래내역` | KIS Developers 공식 API 명세 |
| 297 | `해외선물옵션 증거금상세` | KIS Developers 공식 API 명세 |
| 298 | `해외선물종목현재가` | KIS Developers 공식 API 명세 |
| 299 | `해외선물종목상세` | KIS Developers 공식 API 명세 |
| 300 | `해외선물 호가` | KIS Developers 공식 API 명세 |
| 301 | `해외선물 분봉조회` | KIS Developers 공식 API 명세 |
| 302 | `해외선물 체결추이(틱)` | KIS Developers 공식 API 명세 |
| 303 | `해외선물 체결추이(주간)` | KIS Developers 공식 API 명세 |
| 304 | `해외선물 체결추이(일간)` | KIS Developers 공식 API 명세 |
| 305 | `해외선물 체결추이(월간)` | KIS Developers 공식 API 명세 |
| 306 | `해외선물 상품기본정보` | KIS Developers 공식 API 명세 |
| 307 | `해외선물 미결제추이` | KIS Developers 공식 API 명세 |
| 308 | `해외옵션종목현재가` | KIS Developers 공식 API 명세 |
| 309 | `해외옵션종목상세` | KIS Developers 공식 API 명세 |
| 310 | `해외옵션 호가` | KIS Developers 공식 API 명세 |
| 311 | `해외옵션 분봉조회` | KIS Developers 공식 API 명세 |
| 312 | `해외옵션 체결추이(틱)` | KIS Developers 공식 API 명세 |
| 313 | `해외옵션 체결추이(일간)` | KIS Developers 공식 API 명세 |
| 314 | `해외옵션 체결추이(주간)` | KIS Developers 공식 API 명세 |
| 315 | `해외옵션 체결추이(월간)` | KIS Developers 공식 API 명세 |
| 316 | `해외옵션 상품기본정보` | KIS Developers 공식 API 명세 |
| 317 | `해외선물옵션 장운영시간` | KIS Developers 공식 API 명세 |
| 318 | `해외선물옵션 실시간체결가` | KIS Developers 공식 API 명세 |
| 319 | `해외선물옵션 실시간호가` | KIS Developers 공식 API 명세 |
| 320 | `해외선물옵션 실시간주문내역통보` | KIS Developers 공식 API 명세 |
| 321 | `해외선물옵션 실시간체결내역통보` | KIS Developers 공식 API 명세 |
| 322 | `장내채권 매수주문` | KIS Developers 공식 API 명세 |
| 323 | `장내채권 매도주문` | KIS Developers 공식 API 명세 |
| 324 | `장내채권 정정취소주문` | KIS Developers 공식 API 명세 |
| 325 | `채권정정취소가능주문조회` | KIS Developers 공식 API 명세 |
| 326 | `장내채권 주문체결내역` | KIS Developers 공식 API 명세 |
| 327 | `장내채권 잔고조회` | KIS Developers 공식 API 명세 |
| 328 | `장내채권 매수가능조회` | KIS Developers 공식 API 명세 |
| 329 | `장내채권현재가(호가)` | KIS Developers 공식 API 명세 |
| 330 | `장내채권현재가(시세)` | KIS Developers 공식 API 명세 |
| 331 | `장내채권현재가(체결)` | KIS Developers 공식 API 명세 |
| 332 | `장내채권현재가(일별)` | KIS Developers 공식 API 명세 |
| 333 | `장내채권 기간별시세(일)` | KIS Developers 공식 API 명세 |
| 334 | `장내채권 평균단가조회` | KIS Developers 공식 API 명세 |
| 335 | `장내채권 발행정보` | KIS Developers 공식 API 명세 |
| 336 | `장내채권 기본조회` | KIS Developers 공식 API 명세 |
| 337 | `일반채권 실시간체결가` | KIS Developers 공식 API 명세 |
| 338 | `일반채권 실시간호가` | KIS Developers 공식 API 명세 |
| 339 | `채권지수 실시간체결가` | KIS Developers 공식 API 명세 |