# -*- coding: utf-8 -*-
"""
K-Dual Momentum Multi-Account Rebalancing Bot
Supports: Personal Stock Account (01) & Retirement Savings Account (22)
Enhanced with KIS_MOCK and KIS_DRY_RUN for institutional-grade safety.
"""
import os
import sys
import time
import datetime
import requests
import json
from dotenv import load_dotenv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Windows 콘솔 유니코드/이모지 출력 지원 설정 (cp949 인코딩 에러 방지)
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# .env 파일에서 계좌 정보 및 API 키 로드용 전역 변수 기본 설정
KIS_MOCK = False
KIS_DRY_RUN = False
MAX_ORDER_AMOUNT = 100000000
APP_KEY = ""
APP_SECRET = ""
URL_BASE = ""
ACCOUNTS = []
TELEGRAM_TOKEN = ""
TELEGRAM_CHAT_ID = ""

# 포트폴리오 티커 설정
TICKER_KOSPI = "069500"   # KODEX 200 (한국 대표 주식)
TICKER_SP500 = "360750"   # TIGER 미국S&P500 (미국 대표 주식)
TICKER_GOLD  = "411060"   # ACE KRX금현물 (금 현물)
TICKER_TLT   = "476760"   # ACE 미국30년국채액티브 (미국 장기채)
TICKER_SAFE  = "304580"   # KODEX 미국달러단기채권 (안전자산 피신처)

TICKER_NAMES = {
    TICKER_KOSPI: "KODEX 200 (한국 대표 주식)",
    TICKER_SP500: "TIGER 미국S&P500 (미국 대표 주식)",
    TICKER_GOLD: "ACE KRX금현물 (금 현물)",
    TICKER_TLT: "ACE 미국30년국채액티브 (미국 장기채)",
    TICKER_SAFE: "KODEX 미국달러단기채권 (안전자산 피신처)"
}

def init_config():
    """실행 직전 최신 환경 변수를 읽어 동적 전역 변수를 완벽히 바인딩하는 함수"""
    global KIS_MOCK, KIS_DRY_RUN, MAX_ORDER_AMOUNT, APP_KEY, APP_SECRET, URL_BASE, ACCOUNTS, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
    
    # 절대 경로 기준 env 로드 안전장치
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()

    KIS_MOCK = os.getenv("KIS_MOCK", "False").lower() in ("true", "1", "yes")
    KIS_DRY_RUN = os.getenv("KIS_DRY_RUN", "False").lower() in ("true", "1", "yes")
    MAX_ORDER_AMOUNT = int(os.getenv("MAX_ORDER_AMOUNT", "100000000"))
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    if KIS_MOCK:
        APP_KEY = os.getenv("KIS_MOCK_APP_KEY", "")
        APP_SECRET = os.getenv("KIS_MOCK_APP_SECRET", "")
        URL_BASE = "https://openapivts.koreainvestment.com:29443"
        
        ACCOUNTS = []
        mock_cano1 = os.getenv("KIS_MOCK_CANO1", "")
        mock_cano2 = os.getenv("KIS_MOCK_CANO2", "")
        if mock_cano1:
            ACCOUNTS.append({"name": "모의_주식계좌1", "cano": mock_cano1, "prdt_cd": "01"})
        if mock_cano2:
            ACCOUNTS.append({"name": "모의_주식계좌2", "cano": mock_cano2, "prdt_cd": "01"})
        if not ACCOUNTS:
            pension_cano = os.getenv("KIS_PENSION_CANO", "")
            stock_cano = os.getenv("KIS_STOCK_CANO", "")
            if pension_cano: ACCOUNTS.append({"name": "모의_연금대체계좌", "cano": pension_cano, "prdt_cd": "01"})
            if stock_cano: ACCOUNTS.append({"name": "모의_개인주식계좌", "cano": stock_cano, "prdt_cd": "01"})
    else:
        # [핵심 보완] 올웨더 Key와 섞이지 않도록 K-모멘텀용 오리지널 변수 명을 먼저 명시적으로 로드
        # 만약 없으면 기존 KIS_APP_KEY를 읽어오도록 순서 보장
        APP_KEY = os.getenv("KIS_MOMENTUM_APP_KEY", os.getenv("KIS_APP_KEY", ""))
        APP_SECRET = os.getenv("KIS_MOMENTUM_APP_SECRET", os.getenv("KIS_APP_SECRET", ""))
        
        # [안전 마진 수동 고정] 에러 방지를 위해 실제 발급받으신 K-모멘텀 전용 Key가 로드되었는지 체크
        if not APP_KEY or APP_KEY.startswith("PS62MHdg"): # 만약 올웨더용 키가 잡혀있다면
            # .env 파일에 적어두신 K-모멘텀용 오리지널 실전 키를 강제로 꽂아줍니다.
            APP_KEY = "PS2f8MYQli4WCOEbp4I2zvNwAu6tAJhQV0k2"
            APP_SECRET = "CemVPz0LmntpqrSVxCAnxCFUQhImWsy6tPIATyon+Gnm5TVbi1vvJvm8j9y+37hmrdu2R2EJYNQUialuBOITOdtB5QAKjxanwmTpABp2Tx93wxDDRpeyvmgh/NR5MXDJZKb0R2H0nvQbpu1GIRWS6KHYL+SfNUKTRH/BWofkU8+BmLBu4hA="

        URL_BASE = "https://openapi.koreainvestment.com:9443"
        ACCOUNTS = [
            {"name": "연금저축계좌", "cano": os.getenv("KIS_PENSION_CANO", "63183004").strip(), "prdt_cd": "22"},
            {"name": "개인주식계좌", "cano": os.getenv("KIS_STOCK_CANO", "63183004").strip(), "prdt_cd": "01"}
        ]

# 최초 임포트 시점 초기화 실행
init_config()

def send_telegram(msg):
    prefix = ""
    if KIS_DRY_RUN:
        prefix = "[Dry-run 시뮬레이션] "
    elif KIS_MOCK:
        prefix = "[모의투자 테스트] "
    else:
        prefix = "[실전 리밸런싱] "
        
    full_msg = f"{prefix}{msg}"
    print(f"[TELEGRAM] {full_msg}")
    
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": full_msg}, timeout=5, verify=False)
        except Exception as e:
            print(f"텔레그램 메시지 발송 실패: {e}")

def kis_api_request(method, url, headers, params=None, data=None, max_retries=5, initial_backoff=1.5):
    """
    KIS API 전용 안전 요청 함수.
    초당 거래건수 초과(EGW00215) 및 일시적 서버 오류에 대한 지수 백오프(Exponential Backoff) 재시도를 처리합니다.
    """
    backoff = initial_backoff
    last_res = None
    for attempt in range(max_retries):
        # API 요청 간 최소 0.2초 대기하여 선제적 TPS 조절
        time.sleep(0.2)
        try:
            if method.upper() == "GET":
                res = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
            else:
                res = requests.post(url, headers=headers, data=data, timeout=10, verify=False)
            
            last_res = res
            if res.status_code == 200:
                try:
                    res_data = res.json()
                    msg_cd = res_data.get("msg_cd", "")
                    rt_cd = res_data.get("rt_cd", "")
                    
                    # EGW00215: 초당 거래건수 초과, EGW00201: 시스템 오류
                    if rt_cd != "0" and msg_cd in ("EGW00215", "EGW00201"):
                        print(f"⚠️ KIS API 빈도 제한/일시 오류 감지 (코드: {msg_cd}, 내용: {res_data.get('msg1')}). {backoff}초 후 재시도합니다. (시도 {attempt+1}/{max_retries})")
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                except Exception:
                    pass
                return res
            elif res.status_code in (429, 500, 502, 503, 504):
                print(f"⚠️ KIS API HTTP 오류 감지 (상태 코드: {res.status_code}). {backoff}초 후 재시도합니다. (시도 {attempt+1}/{max_retries})")
                time.sleep(backoff)
                backoff *= 2
                continue
            else:
                return res
        except requests.exceptions.RequestException as e:
            print(f"⚠️ KIS API 네트워크 통신 에러: {e}. {backoff}초 후 재시도합니다. (시도 {attempt+1}/{max_retries})")
            time.sleep(backoff)
            backoff *= 2
            
    if last_res is not None:
        return last_res
    raise Exception(f"KIS API 요청 실패 (최대 재시도 {max_retries}회 초과)")

def is_market_open():
    """주식시장 정규장 운영 시간 여부 판단 (평일 09:00 ~ 15:30 KST)"""
    # KST (UTC+9) 타임존 적용하여 서버가 UTC 환경이어도 한국 시간으로 판단
    kst_tz = datetime.timezone(datetime.timedelta(hours=9))
    now = datetime.datetime.now(kst_tz)
    # 요일 검사: 월요일(0) ~ 금요일(4)
    if now.weekday() >= 5:
        return False
    # 시간 검사: 09:00 ~ 15:30 (KST 기준)
    start_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
    end_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return start_time <= now <= end_time

def get_access_token():
    url = f"{URL_BASE}/oauth2/tokenP"
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    res = kis_api_request("POST", url, headers=headers, data=json.dumps(body))
    if res.status_code == 200:
        return res.json()["access_token"]
    else:
        raise Exception(f"토큰 발급 오류 (모드_모의={KIS_MOCK}): {res.text}")

def get_orderable_cash(token, cano, prdt_cd, ticker="069500"):
    url = f"{URL_BASE}/uapi/domestic-stock/v1/trading/inquire-psbl-order"
    is_mock = KIS_MOCK or "openapim" in URL_BASE
    tr_id = "VTTC8908R" if is_mock else "TTTC8908R"
    
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id,
        "custtype": "P"
    }
    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": prdt_cd,
        "PDNO": ticker,
        "ORD_UNPR": "140000",
        "ORD_DVSN": "01",
        "CMA_EVLU_AMT_IF_YN": "N",
        "OVRS_ICLD_YN": "N"
    }
    try:
        res = kis_api_request("GET", url, headers=headers, params=params)
        if res.status_code == 200:
            data = res.json()
            if data.get("rt_cd") == "0":
                output = data.get("output", {})
                cash = int(output.get("ord_psbl_cash", 0))
                print(f"   - [TTTC8908R] 주문가능현금 조회 성공: {cash:,}원")
                return cash
            else:
                err_msg = f"⚠️ [TTTC8908R - {prdt_cd}] 주문가능현금 조회 실패 ({data.get('msg_cd')}): {data.get('msg1')}"
                print(err_msg)
                send_telegram(err_msg)
        else:
            err_msg = f"⚠️ [TTTC8908R - {prdt_cd}] HTTP 오류: {res.status_code}"
            print(err_msg)
            send_telegram(err_msg)
    except Exception as e:
        err_msg = f"⚠️ [TTTC8908R - {prdt_cd}] API 호출 에러: {e}"
        print(err_msg)
        send_telegram(err_msg)
    return None

def get_account_balance(token, cano, prdt_cd):
    url = f"{URL_BASE}/uapi/domestic-stock/v1/trading/inquire-balance"
    is_mock = KIS_MOCK or "openapim" in URL_BASE
    tr_id = "VTTC8434R" if is_mock else "TTTC8434R"
    
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id
    }
    params = {
        "CANO": cano,
        "ACNT_PRDT_CD": prdt_cd,
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "01",
        "ORD_QTY_DVSN": "00",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    res = kis_api_request("GET", url, headers=headers, params=params)
    if res.status_code != 200:
        raise Exception(f"잔고 조회 API 호출 실패: {res.text}")
        
    data = res.json()
    if data.get("rt_cd") != "0":
        raise Exception(f"잔고 조회 API 실패 ({data.get('msg_cd')}): {data.get('msg1')}")
    
    cash = 0
    if "output2" in data and len(data["output2"]) > 0:
        summary = data["output2"][0]
        
        # 텔레그램 디버깅 메시지 발송
        debug_msg = (
            f"🔍 [계좌 잔고 API 디버깅 - {prdt_cd}]\n"
            f"- ord_psbl_cash(주문가능현금): {summary.get('ord_psbl_cash')} 원\n"
            f"- dnca_tot_amt(D+2예수금): {summary.get('dnca_tot_amt')} 원\n"
            f"- prvs_rcvb_evt_amt(D+2전일재수금): {summary.get('prvs_rcvb_evt_amt')} 원\n"
            f"- tot_evlu_amt(총평가금액): {summary.get('tot_evlu_amt')} 원\n"
            f"- raw_summary: {json.dumps(summary, ensure_ascii=False)}"
        )
        send_telegram(debug_msg)
        
        # 주문가능현금(ord_psbl_cash)을 최우선으로 적용하여 묶인 금액 제외
        for field in ["ord_psbl_cash", "dnca_tot_amt", "prvs_rcvb_evt_amt"]:
            if field in summary and summary[field] is not None:
                try:
                    val = int(summary[field])
                    if val > 0:
                        cash = val
                        print(f"   - 예수금으로 {field} 적용: {cash:,}원")
                        break
                except (ValueError, TypeError):
                    pass
            
    # 매수가능조회 API(TTTC8908R)를 통해 실제 주문 가능 현금 교차 검증 및 반영
    psbl_cash = get_orderable_cash(token, cano, prdt_cd)
    if psbl_cash is not None:
        print(f"   - [교차검증] TTTC8908R 주문가능현금: {psbl_cash:,}원 (기존 잔고조회 cash: {cash:,}원)")
        send_telegram(f"🔍 [{cano}-{prdt_cd}] 실제 매수주문 가능현금(TTTC8908R): {psbl_cash:,} 원")
        cash = psbl_cash

    holdings = {}
    for item in data.get("output1", []):
        ticker = item["pdno"]
        qty = int(item["hldg_qty"])
        if qty > 0:
            holdings[ticker] = {
                "qty": qty,
                "price": float(item["prpr"]),
                "eval_amt": int(item["evlu_amt"])
            }
    return cash, holdings

def submit_order(token, cano, prdt_cd, ticker, qty, order_type="BUY", price=0, ord_dvsn="00"):
    """
    K-듀얼모멘텀 통합 안전 주문 처리 API
    - order_type: BUY(매수), SELL(매도)
    - ord_dvsn: 00(지정가 - Limit), 01(시장가 - Market)
    - price: 지정가(00) 주문 시 적용할 가격
    """
    is_mock = KIS_MOCK or "openapim" in URL_BASE
    
    # 최신 규격 TR_ID 매핑
    if order_type == "BUY":
        tr_id = "VTTC0012U" if is_mock else "TTTC0012U"
    else:
        tr_id = "VTTC0011U" if is_mock else "TTTC0011U"
        
    url = f"{URL_BASE}/uapi/domestic-stock/v1/trading/order-cash"
    
    # Dry-run(모의 실행) 처리
    if KIS_DRY_RUN:
        dry_msg = f"[DRY-RUN 시뮬레이션] {order_type} | 티커: {ticker} | 수량: {qty}주 | 구분: {ord_dvsn} | 지정가: {price:,}원 | 계좌: {cano}"
        print(dry_msg)
        return {
            "rt_cd": "0",
            "msg1": "[Dry-run] 시뮬레이션 주문이 정상 검증되었습니다.",
            "msg_cd": "DRY00000",
            "output": {"ODNO": "999999", "ORD_TMD": "090000"}
        }
        
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id
    }
    
    # 01 (시장가) 이면 단가 0 전달, 00 (지정가) 이면 실제 지정단가 전달
    unpr = "0" if ord_dvsn == "01" else str(int(price))
    
    body = {
        "CANO": cano,
        "ACNT_PRDT_CD": prdt_cd,
        "PDNO": ticker,
        "ORD_DVSN": ord_dvsn,
        "ORD_QTY": str(qty),
        "ORD_UNPR": unpr
    }
    
    print(f">> KIS 주문 요청: Headers={headers}, Body={body}")
    
    res = kis_api_request("POST", url, headers=headers, data=json.dumps(body))
    if res.status_code != 200:
        safe_headers = headers.copy()
        if "appkey" in safe_headers: safe_headers["appkey"] = "MASKED"
        if "appsecret" in safe_headers: safe_headers["appsecret"] = "MASKED"
        if "authorization" in safe_headers: safe_headers["authorization"] = "Bearer MASKED"
        
        err_msg = (
            f"🚨 [주문 API 에러 (HTTP {res.status_code})]\n"
            f"- 응답내용: {res.text}\n"
            f"- Headers: {json.dumps(safe_headers, ensure_ascii=False)}\n"
            f"- Body: {json.dumps(body, ensure_ascii=False)}"
        )
        send_telegram(err_msg)
        raise Exception(f"주문 통신 오류: {res.text}")
        
    return res.json()

def get_historical_prices_kis(ticker, token):
    url = f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST03010100"
    }
    
    # Calculate dates
    kst_tz = datetime.timezone(datetime.timedelta(hours=9))
    today = datetime.datetime.now(kst_tz)
    date_2 = today.strftime("%Y%m%d")
    # Go back 2 years (approx 730 days) to get enough monthly data points
    date_1 = (today - datetime.timedelta(days=730)).strftime("%Y%m%d")
    
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": ticker,
        "FID_INPUT_DATE_1": date_1,
        "FID_INPUT_DATE_2": date_2,
        "FID_PERIOD_DIV_CODE": "M",
        "FID_ORG_ADPR_YN": "Y"
    }
    
    res = kis_api_request("GET", url, headers=headers, params=params)
    if res.status_code == 200:
        data = res.json()
        if data.get("rt_cd") == "0":
            output2 = data.get("output2", [])
            prices = []
            for item in output2:
                clpr = item.get("stck_clpr")
                if clpr:
                    prices.append(float(clpr))
            
            # KIS API returns newest first, we reverse it to oldest first
            prices.reverse()
            
            if len(prices) >= 13:
                print(f"   - [KIS API] 시세 조회 성공: {ticker} -> {len(prices)}개 데이터 확보 (최근가: {prices[-1]:,}원)")
                return prices[-13:]
            else:
                raise Exception(f"KIS API 월별 데이터 개수 부족: {len(prices)}개")
        else:
            raise Exception(f"KIS API 응답 에러 ({data.get('msg_cd')}): {data.get('msg1')}")
    else:
        raise Exception(f"KIS HTTP 에러: {res.status_code}")

def calculate_momentum_signals(token):
    """Yahoo Finance API 및 KIS API를 이용한 4자산 상대 모멘텀 및 1·3·5개월 평균 모멘텀 스코어(AMS) 산출"""
    def get_historical_prices(symbol, ticker):
        # 1. KIS API 우선 사용 (GCP IP 차단 회피용)
        try:
            return get_historical_prices_kis(ticker, token)
        except Exception as ke:
            print(f"⚠️ KIS API 과거 시세 조회 실패 ({ticker}): {ke}. Yahoo Finance 폴백을 실행합니다.")
            
        # 2. Yahoo Finance 폴백
        # We request 2y to ensure we have at least 13 months of non-null monthly prices
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1mo&range=2y"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(url, headers=headers, timeout=10, verify=False)
        if res.status_code != 200:
            raise Exception(f"Yahoo Finance API 연동 실패: {symbol} (HTTP {res.status_code})")
        result = res.json()["chart"]["result"][0]
        timestamps = result.get("timestamp", [])
        closes = result["indicators"]["quote"][0]["close"]
        
        monthly_data = {}
        kst_tz = datetime.timezone(datetime.timedelta(hours=9))
        for ts, close in zip(timestamps, closes):
            if close is not None:
                dt_str = datetime.datetime.fromtimestamp(ts, tz=kst_tz).strftime("%Y-%m")
                monthly_data[dt_str] = close
                
        sorted_months = sorted(monthly_data.keys())
        prices = [monthly_data[m] for m in sorted_months]
        
        if len(prices) < 13:
            raise Exception(f"충분한 데이터를 확보하지 못했습니다: {symbol} (수집된 데이터 개수: {len(prices)})")
        return prices[-13:]

    print(">> 글로벌 증시 역사적 가격 데이터 분석 중...")
    ETF_TICKERS = {
        "KOSPI200": f"{TICKER_KOSPI}.KS",  # 069500.KS
        "SP500": f"{TICKER_SP500}.KS",      # 360750.KS
        "GOLD": f"{TICKER_GOLD}.KS",        # 411060.KS
        "TLT": f"{TICKER_TLT}.KS"           # 476760.KS
    }
    
    SHORT_SYMBOLS = {
        "KOSPI200": TICKER_KOSPI,
        "SP500": TICKER_SP500,
        "GOLD": TICKER_GOLD,
        "TLT": TICKER_TLT
    }
    
    prices_dict = {}
    returns_12m = {}
    
    for name, symbol in ETF_TICKERS.items():
        try:
            ticker = SHORT_SYMBOLS[name]
            prices = get_historical_prices(symbol, ticker)
            prices_dict[name] = prices
            returns_12m[name] = (prices[-1] - prices[-13]) / prices[-13]
        except Exception as e:
            raise Exception(f"🚨 모멘텀 계산 중 {name}({symbol}) 분석 실패: {e}")
        time.sleep(0.5)  # API 요청 간 간격
        
    print(f"■ 모멘텀 데이터 분석 결과 (12개월 수익률):")
    for name, ret in returns_12m.items():
        print(f"   - {name}: {ret*100:.2f}%")
        
    # 1. 상대 모멘텀 필터 (4개 중 1위 선정)
    best_asset = max(returns_12m, key=returns_12m.get)
    chosen_symbol = SHORT_SYMBOLS[best_asset]
    chosen_prices = prices_dict[best_asset]
    chosen_name = TICKER_NAMES[chosen_symbol]
    chosen_ret = returns_12m[best_asset]
    
    print(f">> 상대 모멘텀 1위 선정 자산: {chosen_name} ({chosen_symbol})")
    
    # 2. 1·3·5개월 평균 모멘텀 스코어 (AMS) 계산
    curr_price = chosen_prices[-1]
    p_1m = chosen_prices[-2]
    p_3m = chosen_prices[-4]
    p_5m = chosen_prices[-6]
    
    score = 0
    if curr_price > p_1m: score += 1
    if curr_price > p_3m: score += 1
    if curr_price > p_5m: score += 1
    
    ams_score = score / 3.0
    
    # 3. 비중 결정 (선정 자산 비중: AMS 스코어 비율, 대피 자산 비중: 1 - AMS)
    target_weights = {}
    if ams_score > 0:
        target_weights[chosen_symbol] = ams_score
    if ams_score < 1.0:
        target_weights[TICKER_SAFE] = target_weights.get(TICKER_SAFE, 0.0) + (1.0 - ams_score)
        
    reason = f"상대 모멘텀 우수 자산: {chosen_name} (12m 수익률: {chosen_ret*100:.2f}%), " \
             f"1·3·5 AMS 스코어: {score}점/3점 (선정 자산 비중: {ams_score*100:.1f}% / 안전 자산 비중: {(1-ams_score)*100:.1f}%)"
             
    return target_weights, reason

def rebalance_account(token, acc, target_weights):
    name, cano, prdt_cd = acc["name"], acc["cano"], acc["prdt_cd"]
    print(f"\n=========================================")
    print(f"🔄 [{name}] 자산 리밸런싱 시작 ({cano}-{prdt_cd})")
    print(f"=========================================")
    
    # 2중 보안 검증: 연금저축계좌(22) 및 모의 연금대체계좌(이름에 '연금' 포함)에서는 당사 5대 ETF 외의 매수 거래가 발생하지 않도록 원천 격리
    valid_tickers = [TICKER_KOSPI, TICKER_SP500, TICKER_GOLD, TICKER_TLT, TICKER_SAFE]
    for ticker in target_weights.keys():
        if (prdt_cd == "22" or "연금" in name) and ticker not in valid_tickers:
            raise ValueError(f"🚨 [보안 침해 예방] 연금계좌[{name}]에서 유효하지 않은 자산 매수 시도 차단: {ticker}")
            
    cash, holdings = get_account_balance(token, cano, prdt_cd)
    print(f">> 예수금 현황: {cash:,} 원 | 보유 자산 종류: {list(holdings.keys())}")
    
    # 총자산 계산 (예수금 + 주식 평가금액 합산)
    total_holdings_eval = sum(info["eval_amt"] for info in holdings.values())
    total_asset = cash + total_holdings_eval
    print(f">> 총 평가 자산: {total_asset:,} 원 (보유 주식 평가금액 합계: {total_holdings_eval:,} 원)")
    
    if total_asset == 0:
        print(f">> [{name}] 계좌의 총자산이 0원이므로 리밸런싱을 건너뜁니다.")
        return f"⚠️ [{name}] 자산 없음 실행 스킵"

    # 각 종목별 현재가 조회를 위한 함수 정의
    def get_current_price(ticker):
        price = 0.0
        tick_size = 5  # 기본 호가단위
        try:
            url_price = f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price"
            headers = {
                "authorization": f"Bearer {token}",
                "appkey": APP_KEY,
                "appsecret": APP_SECRET,
                "tr_id": "FHKST01010100"
            }
            params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": ticker}
            res_price = kis_api_request("GET", url_price, headers=headers, params=params)
            if res_price.status_code == 200:
                price_data = res_price.json()
                if price_data.get("rt_cd") == "0":
                    output = price_data.get("output", {})
                    price = float(output.get("stck_prpr", 0))
                    aspr_unit = output.get("aspr_unit")
                    if aspr_unit:
                        try:
                            tick_size = int(aspr_unit)
                        except (ValueError, TypeError):
                            pass
        except Exception as e:
            print(f"⚠️ KIS 현재가 조회 실패 (폴백 시도): {e}")
            
        if price <= 0:
            print(f"⚠️ KIS 현재가가 0 이하({price})이므로 Yahoo Finance에서 현재가를 조회합니다.")
            try:
                yahoo_symbol = f"{ticker}.KS"
                url_yf = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}?interval=1m&range=1d"
                headers_yf = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Connection": "keep-alive"
                }
                res_yf = requests.get(url_yf, headers=headers_yf, timeout=10, verify=False)
                if res_yf.status_code == 200:
                    yf_data = res_yf.json()
                    price = float(yf_data["chart"]["result"][0]["meta"]["regularMarketPrice"])
                    print(f"   - Yahoo Finance 현재가 획득 성공: {ticker} -> {price:,}원")
            except Exception as ye:
                print(f"⚠️ Yahoo Finance 현재가 조회 실패: {ye}")
                
        if price <= 0:
            fallback_prices = {
                TICKER_KOSPI: 137000.0,
                TICKER_SP500: 18000.0,
                TICKER_GOLD: 140000.0,
                TICKER_TLT: 10000.0,
                TICKER_SAFE: 11000.0
            }
            price = fallback_prices.get(ticker, 10000.0)
            print(f"⚠️ 모든 API에서 현재가 획득 실패. 안전을 위해 기본 폴백 가격({price:,}원)을 적용합니다.")
            
        # 호가 단위(tick size) 보정 계산 (국내 주식 호가 단위 기준과 API 반환 단위 중 최댓값 적용)
        # 143,995원 같은 ETF 가격이 KIS API 주문 시 주식 호가단위(100원)로 필터링되는 현상 방지
        stock_tick = 5
        if price < 2000:
            stock_tick = 1
        elif price < 5000:
            stock_tick = 5
        elif price < 20000:
            stock_tick = 10
        elif price < 50000:
            stock_tick = 50
        elif price < 100000:
            stock_tick = 100
        elif price < 500000:
            stock_tick = 100
        else:
            stock_tick = 1000
            
        final_tick = max(tick_size, stock_tick)
        return price, final_tick

    # 1. 1단계: 초과 비중 포지션 매도 정리 (목표 비중보다 많이 가지고 있거나 타겟이 아닌 자산)
    sold_any = False
    target_qtys = {}
    prices = {}
    
    # 먼저 target_weights에 정의된 자산들의 가격과 목표 수량을 산출합니다.
    for ticker, weight in target_weights.items():
        price, tick_size = get_current_price(ticker)
        
        # KIS API 주문 호가단위 오류 방지를 위해 매수 지정가는 호가단위 배수로 올림 처리
        import math
        price = math.ceil(price / tick_size) * tick_size
        print(f"   - [{ticker}] 가격 보정 결과: 원래가격 -> {price:,}원 (호가단위: {tick_size}원)")
        
        prices[ticker] = price
        target_val = total_asset * weight
        target_qtys[ticker] = int(target_val // price)
        
    # 텔레그램 계산 상세 디버깅 발송
    calc_debug = (
        f"🔍 [계산 상세 디버깅 - {name}]\n"
        f"- total_asset: {total_asset:,} 원\n"
        f"- cash: {cash:,} 원\n"
        f"- total_holdings_eval: {total_holdings_eval:,} 원\n"
    )
    for t_ticker, t_weight in target_weights.items():
        t_price = prices[t_ticker]
        t_qty = target_qtys[t_ticker]
        t_curr = holdings.get(t_ticker, {}).get("qty", 0)
        calc_debug += f"📌 {t_ticker}: price={t_price:,}원 | weight={t_weight} | target_qty={t_qty}주 | curr_qty={t_curr}주\n"
    send_telegram(calc_debug)
        
    # 현재 보유 중인 모든 종목을 순회하며 매도 수량을 결정합니다.
    for ticker, info in holdings.items():
        curr_qty = info["qty"]
        target_qty = target_qtys.get(ticker, 0)
        
        # 1-A. 타겟 자산이 아니거나 목표 비중이 0%인 경우 전량 청산
        if target_qty == 0:
            print(f"➔ [전량 청산 매도] 비타겟 자산 시장가 매도 집행: {ticker} (수량: {curr_qty}주)")
            res = submit_order(token, cano, prdt_cd, ticker, curr_qty, "SELL", ord_dvsn="01")
            if res.get("rt_cd") != "0":
                raise Exception(f"🚨 [Fail-Fast 매도 실패] {ticker} 청산 매도 실패: {res.get('msg1')}")
            print(f"   결과: 성공 | 주문번호: {res.get('output', {}).get('ODNO')}")
            sold_any = True
            time.sleep(1.5)
            
        # 1-B. 타겟 자산이지만 현재 보유량이 목표 수량을 초과한 경우 초과분 부분 매도
        elif curr_qty > target_qty:
            sell_qty = curr_qty - target_qty
            print(f"➔ [초과분 부분 매도] 자산 비중 조율 매도 집행: {ticker} (현재: {curr_qty}주 -> 목표: {target_qty}주, 매도: {sell_qty}주)")
            res = submit_order(token, cano, prdt_cd, ticker, sell_qty, "SELL", ord_dvsn="01")
            if res.get("rt_cd") != "0":
                raise Exception(f"🚨 [Fail-Fast 매도 실패] {ticker} 비중 조율 매도 실패: {res.get('msg1')}")
            print(f"   결과: 성공 | 주문번호: {res.get('output', {}).get('ODNO')}")
            sold_any = True
            time.sleep(1.5)

    # 매도를 한 이력이 있다면 예수금 갱신을 위해 대기 및 잔고 재조회
    if sold_any:
        print(">> 매도 정산 및 예수금 갱신 대기 (15초)...")
        time.sleep(15)
        cash, holdings = get_account_balance(token, cano, prdt_cd)
        print(f">> 갱신된 예수금 현황: {cash:,} 원")

    # 2. 2단계: 부족 비중 포지션 매수 진입
    buys = []
    total_buy_needed = 0.0
    
    # 각 타겟 자산별로 매수할 수량과 필요한 금액을 계산합니다.
    for ticker, target_qty in target_qtys.items():
        curr_qty = holdings.get(ticker, {}).get("qty", 0)
        if target_qty > curr_qty:
            buy_qty = target_qty - curr_qty
            price = prices[ticker]
            needed = buy_qty * price
            buys.append((ticker, buy_qty, price, needed))
            total_buy_needed += needed

    # 가용 예수금 범위를 초과하지 않도록 98% 마진 비율을 적용하여 스케일링 조절
    max_buy_fund = cash * 0.98
    if total_buy_needed > max_buy_fund and total_buy_needed > 0:
        scale = max_buy_fund / total_buy_needed
        print(f"⚠️ [예수금 한도 초과 방지] 가용 예수금({max_buy_fund:,}원)이 필요 금액({total_buy_needed:,}원)보다 부족하여 매수 수량을 {scale*100:.1f}%로 축소 조정합니다.")
        
        # 다시 스케일 조절 후 주문 목록 재작성
        adjusted_buys = []
        for ticker, buy_qty, price, needed in buys:
            adj_qty = int(buy_qty * scale)
            if adj_qty > 0:
                adjusted_buys.append((ticker, adj_qty, price, adj_qty * price))
        buys = adjusted_buys

    # 매수 주문 실행
    buy_results = []
    for ticker, buy_qty, price, amount in buys:
        # Fat Finger 방지용 최종 안전 벨트 검증 (단일 주문 금액 상한 검사)
        if amount > MAX_ORDER_AMOUNT:
            raise ValueError(
                f"🚨 [Fat Finger 차단] 계산된 주문 금액 {amount:,}원이 "
                f"설정된 최대 주문 제한 금액 {MAX_ORDER_AMOUNT:,}원을 초과했습니다!"
            )
            
        print(f"➔ [비중 진입] 자산 지정가 매수 집행: {ticker} (수량: {buy_qty}주, 단가: {price:,}원, 금액: {amount:,}원)")
        # 매수 주문은 130% 마진 체크 회피를 위해 지정가(ord_dvsn="00", price=price)로 집행
        res = submit_order(token, cano, prdt_cd, ticker, buy_qty, "BUY", price=price, ord_dvsn="00")
        
        if res.get("rt_cd") == "0":
            buy_results.append(f"✅ {ticker} {buy_qty}주 매수 성공 (체결가: {price:,}원)")
        else:
            buy_results.append(f"❌ {ticker} {buy_qty}주 매수 실패! (사유: {res.get('msg1')})")
        time.sleep(1.5)

    # 최종 상태 요약 메시지 빌딩
    status_summary = []
    for ticker, weight in target_weights.items():
        curr_qty = holdings.get(ticker, {}).get("qty", 0)
        status_summary.append(f"{ticker}(목표비중 {weight*100:.0f}%, 현재수량 {curr_qty}주)")
        
    msg = f"🔄 [{name}] 리밸런싱 완료\n- 목표 분할: {', '.join(status_summary)}\n"
    if buy_results:
        msg += "- 매수 결과:\n  " + "\n  ".join(buy_results)
    else:
        msg += "- 추가 매수 거래 없음 (목표 비중 이미 충족)"
        
    print(msg)
    return msg

def get_actual_rebalance_date(year, month):
    """
    지정한 년/월의 실제 리밸런싱 실행일을 계산합니다.
    - 2026년 5월은 예외적으로 29일로 고정
    - 6월부터는 17일 기준 (주말/공휴일인 경우 다음 평일로 미룸)
    """
    if year == 2026 and month == 5:
        return datetime.date(2026, 5, 29)
        
    target_day = 17
    
    # 2026년~2027년 주식시장 주요 공휴일 및 대체휴일 리스트 (YYYY-MM-DD)
    krx_holidays = {
        # 2026년
        "2026-01-01", "2026-02-16", "2026-02-17", "2026-02-18",
        "2026-03-01", "2026-03-02", "2026-05-05", "2026-05-25",
        "2026-06-06", "2026-08-15", "2026-08-17", "2026-09-24",
        "2026-09-25", "2026-09-26", "2026-09-28", "2026-10-03",
        "2026-10-05", "2026-10-09", "2026-12-25", "2026-12-31",
        # 2027년
        "2027-01-01", "2027-02-05", "2027-02-06", "2027-02-07",
        "2027-02-08", "2027-03-01", "2027-05-05", "2027-05-13",
        "2027-06-06", "2027-06-07", "2027-08-15", "2027-08-16",
        "2027-10-03", "2027-10-04", "2027-10-09", "2027-10-11",
        "2027-12-25", "2027-12-31"
    }
    
    check_date = datetime.date(year, month, target_day)
    while True:
        # 주말인 경우 하루 뒤로 미룸
        if check_date.weekday() >= 5:
            check_date += datetime.timedelta(days=1)
            continue
        # 한국거래소 공휴일인 경우 하루 뒤로 미룸
        if check_date.strftime("%Y-%m-%d") in krx_holidays:
            check_date += datetime.timedelta(days=1)
            continue
        return check_date

def main():
    # 실행 시점에 환경 변수 구성을 강제 동기화
    init_config()
    
    # KST (UTC+9) 타임존 적용
    kst_tz = datetime.timezone(datetime.timedelta(hours=9))
    
    # 1. 실행일 판정 게이트 작동
    today = datetime.datetime.now(kst_tz).date()
    actual_rebalance_date = get_actual_rebalance_date(today.year, today.month)
    
    print(f">> [실행일 점검] 이번 달 리밸런싱 예정일은 {actual_rebalance_date} 입니다. (오늘: {today})")
    
    # 실전 실행 모드일 때만 날짜 필터링 적용 (Dry-run, Mock, --force 인자 입력 시 생략 허용)
    is_force = len(sys.argv) > 1 and sys.argv[1] == "--force"
    if today != actual_rebalance_date:
        if not (KIS_DRY_RUN or KIS_MOCK or is_force):
            msg = (
                f"ℹ️ [가동 즉시 중단] 오늘은 실전 리밸런싱 실행일이 아닙니다.\n"
                f"   - 이번 달 예정일: {actual_rebalance_date}\n"
                f"   - 오늘 날짜: {today}\n"
                f"   - 강제 가동을 원하시면 'python kis_bot_multi.py --force'로 실행하십시오."
            )
            print(msg)
            if __name__ == "__main__":
                sys.exit(0)
            else:
                return
        else:
            print("⚠️ [스케줄 우회] 오늘이 리밸런싱 날은 아니지만, 시뮬레이션/모의투자/강제실행 옵션이 활성화되어 진행합니다.")

    start_time = datetime.datetime.now(kst_tz).strftime("%Y-%m-%d %H:%M:%S")
    mode_str = "실전 자동 거래"
    if KIS_DRY_RUN:
        mode_str = "Dry-run 시뮬레이션"
    elif KIS_MOCK:
        mode_str = "모의투자 시뮬레이션"
        
    send_telegram(f"🤖 K-듀얼 모멘텀 통합 리밸런싱 로봇 가동 시작 ({mode_str})\n가동 시간: {start_time}")
    
    # 시장 영업일 및 운영시간 판단 게이트키퍼 작동
    # 드라이런(KIS_DRY_RUN) 및 모의투자(KIS_MOCK) 모드일 경우 영업시간 검증 생략 허용
    if not is_market_open():
        if not (KIS_DRY_RUN or KIS_MOCK):
            closed_msg = "🚨 [가동 즉시 중단] 현재 주식시장 정규 운영 시간(평일 09:00 ~ 15:30)이 아닙니다. 안전을 위해 실행을 즉시 중단합니다."
            print(closed_msg)
            send_telegram(closed_msg)
            if __name__ == "__main__":
                sys.exit(1)
            else:
                raise ValueError(closed_msg)
        else:
            print("⚠️ [영업시간 외 우회] 현재 시장이 닫혀 있으나, Dry-run/모의투자 모드이므로 정상 진행합니다.")

    try:
        token = get_access_token()
        target_weights, reason = calculate_momentum_signals(token)
        
        # Format weights summary
        weights_detail = [f"{TICKER_NAMES.get(t, t)} ({t}): {w*100:.0f}%" for t, w in target_weights.items()]
        summary_msg = f"📈 금월 투자 대상 및 비중 선정:\n- 비중: {', '.join(weights_detail)}\n- 판단 근거: {reason}\n"
        send_telegram(summary_msg)
        
        results = []
        for i, acc in enumerate(ACCOUNTS):
            if not acc["cano"] or acc["cano"].startswith("YOUR_"):
                print(f">> 계좌 번호 미세팅 또는 예시 텍스트로 {acc['name']}를 생략합니다.")
                continue
            
            # 여러 계좌 실행 시 계좌 간 간격을 두어 KIS API TPS 한도(EGW00215) 완충
            if i > 0:
                print(">> 다음 계좌 처리 전 대기 중 (3초)...")
                time.sleep(3)
                
            try:
                res_msg = rebalance_account(token, acc, target_weights)
                results.append(res_msg)
            except Exception as ae:
                err = f"❌ 계좌 리밸런싱 실패({acc['name']}): {ae}"
                print(err)
                results.append(err)
                # 계좌 하나라도 에러 발생 시 전량 즉각 전파 및 중지 유도
                raise ae
                
        if results:
            send_telegram("📊 [작업 수행 리포트]\n" + "\n".join(results))
            
    except Exception as e:
        error_msg = f"🚨 로봇 구동 전역 에러 발생: {e}"
        print(error_msg)
        send_telegram(error_msg)
        if __name__ == "__main__":
            sys.exit(1)
        else:
            raise e

if __name__ == "__main__":
    main()

