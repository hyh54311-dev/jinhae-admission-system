# -*- coding: utf-8 -*-
"""
Global All Weather Asset Allocation Rebalancing & Savings Bot (Option A - US-listed ETFs)
Target Account: KIS Dedicated All Weather Stock Account (Cano defined in KIS_ALL_WEATHER_CANO)
Asset Allocation (Ray Dalio Classic):
  1. Equities (30%): VOO (Vanguard S&P 500 ETF)
  2. Long-term Bonds (40%): TLT (iShares 20+ Year Treasury Bond ETF)
  3. Intermediate Bonds (15%): IEF (iShares 7-10 Year Treasury Bond ETF)
  4. Gold (7.5%): GLD (SPDR Gold Shares)
  5. Commodities (7.5%): PDBC (Invesco Optimum Yield Diversified Commodity ETF)
"""
import os
import sys
import time
import datetime
import requests
import json
from dotenv import load_dotenv
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ensure UTF-8 console output on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Global settings
KIS_MOCK = False
KIS_DRY_RUN = False
KIS_TEST_MODE = False
APP_KEY = ""
APP_SECRET = ""
URL_BASE = ""
CANO = ""
PRDT_CD = "01" # Regular Stock Account / Sub-Account
TELEGRAM_TOKEN = ""
TELEGRAM_CHAT_ID = ""
REBALANCE_THRESHOLD = 0.03 # 3% Dynamic Band Threshold
ANNUAL_REBALANCE_DATE = "01-02" # January 2nd
MIN_INFLOW_USD = 100.0 # Minimum USD cash to trigger monthly savings investment

# Portfolio targets (Option A)
TARGET_WEIGHTS = {
    "VOO": 0.300,  # Vanguard S&P 500 ETF (Equities)
    "TLT": 0.400,  # iShares 20+ Year Treasury Bond ETF (Long-term Bonds)
    "IEF": 0.150,  # iShares 7-10 Year Treasury Bond ETF (Int-term Bonds)
    "GLD": 0.075,  # SPDR Gold Shares (Gold)
    "PDBC": 0.075  # Invesco Optimum Yield Diversified Commodity ETF (Commodities)
}

TICKER_NAMES = {
    "VOO": "VOO (S&P 500)",
    "TLT": "TLT (20+ Yr Treasury)",
    "IEF": "IEF (7-10 Yr Treasury)",
    "GLD": "GLD (Gold)",
    "PDBC": "PDBC (Commodities)"
}

# KIS OpenAPI Overseas Trading Exchange Codes
ORDER_EXCHANGE_CODES = {
    "VOO": "AMEX",
    "TLT": "NASD",
    "IEF": "NASD",
    "GLD": "AMEX",
    "PDBC": "NASD"
}

# KIS OpenAPI Overseas Price Exchange Codes
PRICE_EXCHANGE_CODES = {
    "VOO": "AMS",
    "TLT": "NAS",
    "IEF": "NAS",
    "GLD": "AMS",
    "PDBC": "NAS"
}

def init_config():
    global KIS_MOCK, KIS_DRY_RUN, KIS_TEST_MODE, APP_KEY, APP_SECRET, URL_BASE, CANO, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
    
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()

    KIS_MOCK = os.getenv("KIS_MOCK", "False").lower() in ("true", "1", "yes")
    KIS_DRY_RUN = os.getenv("KIS_DRY_RUN", "False").lower() in ("true", "1", "yes")
    
    if "--dry-run" in sys.argv:
        KIS_DRY_RUN = True
    if "--test" in sys.argv:
        KIS_TEST_MODE = True
        KIS_DRY_RUN = True
        
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    if KIS_MOCK:
        APP_KEY = os.getenv("KIS_MOCK_APP_KEY", "")
        APP_SECRET = os.getenv("KIS_MOCK_APP_SECRET", "")
        URL_BASE = "https://openapivts.koreainvestment.com:29443"
        CANO = os.getenv("KIS_MOCK_CANO1", "")
    else:
        APP_KEY = os.getenv("KIS_ALL_WEATHER_APP_KEY", "")
        if not APP_KEY:
            APP_KEY = os.getenv("KIS_APP_KEY", "")
        APP_SECRET = os.getenv("KIS_ALL_WEATHER_APP_SECRET", "")
        if not APP_SECRET:
            APP_SECRET = os.getenv("KIS_APP_SECRET", "")
        URL_BASE = "https://openapi.koreainvestment.com:9443"
        
        # Load dedicated sub-account for All Weather (Option A)
        CANO = os.getenv("KIS_ALL_WEATHER_CANO", "")
        if not CANO:
            CANO = os.getenv("KIS_STOCK_CANO", "")
            
    if not CANO:
        CANO = os.getenv("KIS_PENSION_CANO", "")

def send_telegram(msg):
    prefix = ""
    if KIS_TEST_MODE:
        prefix = "🧪 [All Weather Test] "
    elif KIS_DRY_RUN:
        prefix = "⚠️ [All Weather Dry-run] "
    elif KIS_MOCK:
        prefix = "🧪 [All Weather Mock] "
    else:
        prefix = "🛡️ [All Weather Real] "
        
    full_msg = f"{prefix}{msg}"
    print(f"[TELEGRAM] {full_msg}")
    
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        try:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": full_msg}, timeout=5, verify=False)
        except Exception as e:
            print(f"텔레그램 발송 에러: {e}")

def kis_api_request(method, url, headers, params=None, data=None, max_retries=3, initial_backoff=1.0):
    backoff = initial_backoff
    last_res = None
    for attempt in range(max_retries):
        time.sleep(0.2)
        try:
            if method.upper() == "GET":
                res = requests.get(url, headers=headers, params=params, timeout=6, verify=False)
            else:
                res = requests.post(url, headers=headers, data=data, timeout=6, verify=False)
            
            last_res = res
            if res.status_code == 200:
                try:
                    res_data = res.json()
                    msg_cd = res_data.get("msg_cd", "")
                    rt_cd = res_data.get("rt_cd", "")
                    
                    if rt_cd != "0" and msg_cd in ("EGW00215", "EGW00201"):
                        print(f"⚠️ KIS 빈도 초과/오류 ({msg_cd}). {backoff}초 후 재시도. (시도 {attempt+1}/{max_retries})")
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                except Exception:
                    pass
                return res
            elif res.status_code in (429, 500, 502, 503, 504):
                print(f"⚠️ KIS HTTP 오류 ({res.status_code}). {backoff}초 후 재시도. (시도 {attempt+1}/{max_retries})")
                time.sleep(backoff)
                backoff *= 2
                continue
            else:
                return res
        except requests.exceptions.RequestException as e:
            print(f"⚠️ KIS 네트워크 통신 에러: {e}. {backoff}초 후 재시도. (시도 {attempt+1}/{max_retries})")
            time.sleep(backoff)
            backoff *= 2
            
    if last_res is not None:
        return last_res
    raise Exception(f"KIS API 최대 재시도 초과 ({max_retries}회)")

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
        raise Exception(f"토큰 발급 실패: {res.text}")

def get_orderable_cash(token):
    """[보완] KIS 국내 예수금/주문가능금액 조회 API (통합증거금용 원화 예수금 확인용)"""
    if KIS_TEST_MODE:
        return 64893948.0
    
    url = f"{URL_BASE}/uapi/domestic-stock/v1/trading/inquire-psbl-order"
    is_mock = KIS_MOCK or "openapim" in URL_BASE
    tr_id = "VTTC8435R" if is_mock else "TTTC8435R"
    
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": PRDT_CD,
        "PDNO": "005930", # 기본값으로 삼성전자 지정
        "ORD_UNPR": "0",
        "ORD_DVSN": "01",
        "CMA_EVLU_AMT_IF_YN": "N",
        "OVRS_ICNT_FND_YN": "N"
    }
    try:
        res = kis_api_request("GET", url, headers=headers, params=params)
        if res.status_code == 200:
            res_data = res.json()
            if res_data.get("rt_cd") == "0":
                # nst4_dlsl_amt (현금주문가능금액) 반환
                return float(res_data.get("output", {}).get("nst4_dlsl_amt", 0.0))
    except Exception as e:
        print(f"⚠️ 국내 주문가능 원화 조회 실패(해외 예수금만 사용): {e}")
    return 0.0

def get_account_balance_overseas(token):
    if KIS_TEST_MODE:
        mock_holdings = {
            "VOO": {"qty": 52, "price": 505.20, "eval_amt": 26270.40},
            "TLT": {"qty": 200, "price": 93.40, "eval_amt": 18680.00},
            "IEF": {"qty": 50, "price": 92.50, "eval_amt": 4625.00}
        }
        mock_cash_usd = 100.0
        mock_cash_krw = 64893948.0 
        ex_rate = 1380.0
        total_cash_usd = mock_cash_usd + (mock_cash_krw / ex_rate)
        print(f"   - [TEST MODE] 모의 해외 계좌 잔고 데이터를 설정합니다 (USD 잔고: ${mock_cash_usd:.2f}, 원화 잔고: {mock_cash_krw:,}원, 환율: {ex_rate}원)")
        return total_cash_usd, mock_holdings

    url = f"{URL_BASE}/uapi/overseas-stock/v1/trading/inquire-balance"
    is_mock = KIS_MOCK or "openapim" in URL_BASE
    tr_id = "VTTS3012R" if is_mock else "TTTS3012R"
    
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id
    }
    
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": PRDT_CD,
        "OVRS_EXCG_CD": "NASD",
        "TR_CRCY_CD": "USD",
        "TR_RSLT_CLS_CODE": "02",
        "CTX_AREA_FK200": "",
        "CTX_AREA_NK200": ""
    }
    
    res = kis_api_request("GET", url, headers=headers, params=params)
    if res.status_code != 200:
        raise Exception(f"해외 잔고 조회 실패: {res.text}")
        
    data = res.json()
    if data.get("rt_cd") != "0":
        raise Exception(f"해외 잔고 조회 API 실패 ({data.get('msg_cd')}): {data.get('msg1')}")
        
    cash_usd = 0.0
    ex_rate = 1380.0
    if "output2" in data:
        summary = data["output2"]
        cash_usd = float(summary.get("frcr_dnca_amt_2", 0.0))
        try:
            val_ex = float(summary.get("frst_bltn_exrt", 1380.0))
            if val_ex > 0:
                ex_rate = val_ex
        except ValueError:
            pass
            
    cash_krw = 0.0
    try:
        psbl_cash_krw = get_orderable_cash(token)
        if psbl_cash_krw is not None:
            cash_krw = float(psbl_cash_krw)
    except Exception:
        pass
        
    total_cash_usd = cash_usd + (cash_krw / ex_rate)
    
    if cash_krw > 0:
        print(f"   - [통합증거금 감지] 원화 예수금 {cash_krw:,.0f}원을 달러화 환산(${cash_krw/ex_rate:,.2f} USD, 적용환율: {ex_rate:,.2f}원)하여 통합 합산합니다.")
        
    holdings = {}
    for item in data.get("output1", []):
        ticker = item["ovrs_pdno"]
        qty = int(item["hldg_qty"])
        if qty > 0:
            holdings[ticker] = {
                "qty": qty,
                "price": float(item["last_prc"]),
                "eval_amt": float(item["ovrs_tot_eval_amt"])
            }
    return total_cash_usd, holdings

def get_current_price_overseas(token, ticker):
    price = 0.0
    if not KIS_TEST_MODE:
        try:
            url_price = f"{URL_BASE}/uapi/overseas-price/v1/quotations/price"
            headers = {
                "authorization": f"Bearer {token}",
                "appkey": APP_KEY,
                "appsecret": APP_SECRET,
                "tr_id": "HHDFS76200200"
            }
            exchange = PRICE_EXCHANGE_CODES.get(ticker, "NAS")
            params = {
                "AUTH": "",
                "EXCD": exchange,
                "SYMB": ticker
            }
            res_price = kis_api_request("GET", url_price, headers=headers, params=params)
            if res_price.status_code == 200:
                price_data = res_price.json()
                if price_data.get("rt_cd") == "0":
                    price = float(price_data.get("output", {}).get("last", 0))
        except Exception as e:
            print(f"⚠️ KIS 해외 현재가 조회 실패 ({ticker}): {e}")
            
    if price <= 0:
        try:
            # [보완] 야후 파이낸스 차단 우회를 위한 종합 헤더 구성
            url_yf = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
            headers_yf = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Connection": "keep-alive"
            }
            res_yf = requests.get(url_yf, headers=headers_yf, timeout=10, verify=False)
            if res_yf.status_code == 200:
                price = float(res_yf.json()["chart"]["result"][0]["meta"]["regularMarketPrice"])
                print(f"   - [Yahoo Finance] {ticker} 실시간가: {price:,} USD")
        except Exception as ye:
            print(f"⚠️ Yahoo Finance 현재가 조회 실패: {ye}")
            
    if price <= 0:
        fallbacks = {
            "VOO": 505.20,
            "TLT": 93.40,
            "IEF": 92.50,
            "GLD": 218.40,
            "PDBC": 13.50
        }
        price = fallbacks.get(ticker, 10.0)
        print(f"⚠️ 폴백 가격 적용: {ticker} -> {price:,} USD")
        
    return price

def submit_order_overseas(token, ticker, qty, order_type="BUY", current_price=0.0):
    is_mock = KIS_MOCK or "openapim" in URL_BASE
    
    if order_type == "BUY":
        tr_id = "VTTS3001U" if is_mock else "TTTS3001U"
    else:
        tr_id = "VTTS3002U" if is_mock else "TTTS3002U"
        
    url = f"{URL_BASE}/uapi/overseas-stock/v1/trading/order"
    
    if KIS_DRY_RUN:
        print(f"   [DRY-RUN 시뮬레이션] {order_type} | {TICKER_NAMES.get(ticker, ticker)} ({ticker}) -> {qty}주 | 계좌: {CANO}")
        return {
            "rt_cd": "0",
            "msg1": "[Dry-run] 해외 모의 주문 매칭에 성공했습니다.",
            "output": {"ODNO": "999999"}
        }
        
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id
    }
    
    margin = 1.01 if order_type == "BUY" else 0.99
    limit_price = current_price * margin
    
    body = {
        "CANO": CANO,
        "ACNT_PRDT_CD": PRDT_CD,
        "OVRS_EXCG_CD": ORDER_EXCHANGE_CODES.get(ticker, "NASD"),
        "PDNO": ticker,
        "ORD_QTY": str(qty),
        "ORD_UNPR": f"{limit_price:.2f}", # [보완] 호가 포맷 에러 방지를 위한 소수점 둘째자리 제한
        "ORD_DVSN": "00"
    }
    if order_type == "SELL":
        body["SLL_TYPE"] = "00"
    
    res = kis_api_request("POST", url, headers=headers, data=json.dumps(body))
    if res.status_code != 200:
        raise Exception(f"해외 주문 통신 에러: {res.text}")
        
    return res.json()

def main():
    global CANO
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] All Weather 자산배분 엔진 구동...")
    init_config()
    
    kst_tz = datetime.timezone(datetime.timedelta(hours=9))
    today = datetime.datetime.now(kst_tz)
    today_mmdd = today.strftime("%m-%d")
    
    is_rebalance_day = (today_mmdd == ANNUAL_REBALANCE_DATE)
    is_force = "--force" in sys.argv
    
    print(f"▶ 매년 정기 리밸런싱 실행 예정일: {ANNUAL_REBALANCE_DATE} | 오늘 날짜: {today_mmdd}")
    
    run_full_rebalance = is_rebalance_day or is_force
    
    if KIS_TEST_MODE:
        print("🧪 [TEST MODE] 테스트 모드로 가동합니다. KIS API 호출을 최소화하고 시뮬레이션을 수행합니다.")
        token = "MOCK_TOKEN_VALUE"
        if not CANO:
            CANO = "63183004_AW"
        if is_force:
            run_full_rebalance = True
        else:
            run_full_rebalance = False
    else:
        if not CANO or not APP_KEY:
            print("설정 오류: 올웨더 계좌번호(KIS_ALL_WEATHER_CANO 또는 KIS_STOCK_CANO) 또는 API키 누락. 실행을 중단합니다.")
            return
        try:
            token = get_access_token()
        except Exception as e:
            print(f"KIS 로그인 토큰 획득 에러: {e}")
            print("학교 방화벽으로 인해 토큰 획득에 실패했습니다. 테스트 모드로 전환하여 시뮬레이션을 완료하려면 스크립트 실행 시 '--test' 파라미터를 입력하세요.")
            return

    try:
        cash_usd, holdings = get_account_balance_overseas(token)
        
        holdings_eval = sum(info["eval_amt"] for info in holdings.values())
        total_asset = cash_usd + holdings_eval
        
        print(f"▶ 올웨더 계좌번호: {CANO}-{PRDT_CD}")
        print(f"▶ 총 평가자산: {total_asset:,.2f} USD (예수금: {cash_usd:,.2f} USD | 보유자산 가치: {holdings_eval:,.2f} USD)")
        
        if total_asset <= 0:
            print("계좌 총자산이 0원이므로 매매를 건너뜁니다.")
            return

        current_prices = {}
        for ticker in TARGET_WEIGHTS.keys():
            current_prices[ticker] = get_current_price_overseas(token, ticker)
            
        rebalance_needed = False
        
        print("\n=== [현재 포트폴리오 비중 점검] ===")
        for ticker, target_w in TARGET_WEIGHTS.items():
            name = TICKER_NAMES[ticker]
            curr_val = holdings.get(ticker, {}).get("eval_amt", 0)
            curr_w = curr_val / total_asset
            dev = curr_w - target_w
            
            print(f"• {name}: 현재 비중 {curr_w*100:.1f}% | 목표 비중 {target_w*100:.1f}% | 괴리율: {dev*100:+.1f}%p")
            
            if abs(dev) > REBALANCE_THRESHOLD:
                rebalance_needed = True
                
        leftovers = []
        for ticker in holdings.keys():
            if ticker not in TARGET_WEIGHTS:
                print(f"• [기타자산 감지] {ticker} (평가금액: {holdings[ticker]['eval_amt']:,.2f} USD) ➡️ 매도 대상")
                rebalance_needed = True
                leftovers.append(ticker)
                
        # Path 1: Full Rebalancing (Sells and Buys)
        if run_full_rebalance:
            print("\n🚨 [리밸런싱 모드] 연간 리밸런싱 실행일이거나 강제 실행 옵션이 활성화되었습니다. 매매를 진행합니다.")
            if not rebalance_needed:
                msg = "◎ 모든 자산 비중이 밴드 범위(3% 이내)에 있으므로 리밸런싱을 수행하지 않고 안전 종료합니다."
                print(msg)
                send_telegram(msg)
                return
                
            target_qtys = {}
            for ticker, target_w in TARGET_WEIGHTS.items():
                target_val = total_asset * target_w
                price = current_prices[ticker]
                target_qtys[ticker] = int(target_val // price)
                
            sells = []
            buys = []
            
            for ticker in leftovers:
                qty_to_sell = holdings[ticker]["qty"]
                sells.append({"ticker": ticker, "qty": qty_to_sell, "name": f"기타자산 ({ticker})"})
                
            for ticker, target_qty in target_qtys.items():
                curr_qty = holdings.get(ticker, {}).get("qty", 0)
                diff = target_qty - curr_qty
                
                if diff < 0:
                    sells.append({"ticker": ticker, "qty": abs(diff), "name": TICKER_NAMES[ticker]})
                elif diff > 0:
                    buys.append({"ticker": ticker, "qty": diff, "name": TICKER_NAMES[ticker]})
                    
            print("\n=== [1단계: 매도 주문 실행] ===")
            sell_report = []
            for s in sells:
                try:
                    res = submit_order_overseas(token, s["ticker"], s["qty"], order_type="SELL", current_price=current_prices.get(s["ticker"], 0.0))
                    if res.get("rt_cd") == "0":
                        msg = f"✓ 매도 성공: {s['name']} ({s['ticker']}) -> {s['qty']}주 매도 청구"
                        print(msg)
                        sell_report.append(msg)
                    else:
                        msg = f"✗ 매도 실패: {s['name']} -> {res.get('msg1')}"
                        print(msg)
                        sell_report.append(msg)
                except Exception as e:
                    msg = f"✗ 매도 오류: {s['name']} -> {e}"
                    print(msg)
                    sell_report.append(msg)
                    
            if sells:
                print("\n매도 주문 후 잔고 동기화를 위해 5초 대기합니다...")
                time.sleep(5)
                
            if KIS_TEST_MODE:
                sold_cash_usd = 0.0
                for s in sells:
                    price = current_prices.get(s["ticker"], 10.0)
                    sold_cash_usd += price * s["qty"]
                cash_usd += sold_cash_usd
                
            if not KIS_TEST_MODE:
                print("최신 해외 예수금을 재조회합니다...")
                cash_usd, holdings = get_account_balance_overseas(token)
            print(f"▶ 매도 후 사용 가능 USD 예수금: {cash_usd:,.2f} USD")
            
            print("\n=== [2단계: 매수 주문 실행] ===")
            buy_report = []
            for b in buys:
                price = current_prices[b["ticker"]]
                required_cash = price * b["qty"]
                
                qty_to_buy = b["qty"]
                if required_cash > cash_usd:
                    qty_to_buy = int(cash_usd // price)
                    required_cash = price * qty_to_buy
                    print(f"    ⚠️ [USD 예수금 부족 경고] {b['name']} 매수 수량 조정: {b['qty']}주 ➡️ {qty_to_buy}주")
                    
                if qty_to_buy <= 0:
                    msg = f"✗ 매수 건너뜀 (USD 예수금 부족): {b['name']}"
                    print(msg)
                    buy_report.append(msg)
                    continue
                    
                try:
                    res = submit_order_overseas(token, b["ticker"], qty_to_buy, order_type="BUY", current_price=price)
                    if res.get("rt_cd") == "0":
                        msg = f"✓ 매수 성공: {b['name']} ({b['ticker']}) -> {qty_to_buy}주 매수 청구"
                        print(msg)
                        buy_report.append(msg)
                        cash_usd -= required_cash # [보완] 리밸런싱 루프 내 예수금 차감 누락 해결
                    else:
                        msg = f"✗ 매수 실패: {b['name']} -> {res.get('msg1')}"
                        print(msg)
                        buy_report.append(msg)
                except Exception as e:
                    msg = f"✗ 매수 오류: {b['name']} -> {e}"
                    print(msg)
                    buy_report.append(msg)
                    
            report_lines = [
                "📊 <b>[All Weather 연간 리밸런싱 완료]</b>",
                "• 계좌: <code>" + str(CANO) + "</code>",
                "• 총자산: <code>$" + f"{total_asset:,.2f}" + " USD</code>",
                "",
                "<b>[매도 목록]</b>"
            ]
            report_lines.extend(sell_report if sell_report else ["- 매도 내역 없음"])
            report_lines.append("")
            report_lines.append("<b>[매수 목록]</b>")
            report_lines.extend(buy_report if buy_report else ["- 매수 내역 없음"])
            
            send_telegram("\n".join(report_lines))
            print("올웨더 리밸런싱 프로세스 완료.")
            
        # Path 2: Inflow Allocation (Buy-Only)
        elif cash_usd >= MIN_INFLOW_USD:
            print(f"\n🪙 [적립식 투자 모드] 신규 자금 감지 (${cash_usd:,.2f} USD >= ${MIN_INFLOW_USD:.2f} USD). 매수 전용 적립식 매매를 집행합니다.")
            
            gaps = {}
            under_weighted = []
            for ticker, target_w in TARGET_WEIGHTS.items():
                curr_val = holdings.get(ticker, {}).get("eval_amt", 0.0)
                target_val = total_asset * target_w
                gap = target_val - curr_val
                gaps[ticker] = gap
                if gap > 0:
                    under_weighted.append(ticker)
                    
            buys = []
            if not under_weighted:
                for ticker, target_w in TARGET_WEIGHTS.items():
                    price = current_prices[ticker]
                    alloc_cash = cash_usd * target_w
                    qty = int(alloc_cash // price)
                    if qty > 0:
                        buys.append({"ticker": ticker, "qty": qty, "name": TICKER_NAMES[ticker], "price": price})
            else:
                sum_positive_gaps = sum(gaps[t] for t in under_weighted)
                for ticker in under_weighted:
                    price = current_prices[ticker]
                    alloc_cash = cash_usd * (gaps[ticker] / sum_positive_gaps)
                    qty = int(alloc_cash // price)
                    if qty > 0:
                        buys.append({"ticker": ticker, "qty": qty, "name": TICKER_NAMES[ticker], "price": price})
                        
            if not buys:
                print("   - 적립식 매수 가능 최소 금액 미달로 주문을 집행하지 않습니다.")
                return
                
            print("\n=== [적립식 매수 주문 실행] ===")
            buy_report = []
            executed_any = False
            for b in buys:
                try:
                    res = submit_order_overseas(token, b["ticker"], b["qty"], order_type="BUY", current_price=b["price"])
                    if res.get("rt_cd") == "0":
                        msg = f"✓ 매수 성공: {b['name']} ({b['ticker']}) -> {b['qty']}주 매수 청구"
                        print(msg)
                        buy_report.append(msg)
                        executed_any = True
                    else:
                        msg = f"✗ 매수 실패: {b['name']} -> {res.get('msg1')}"
                        print(msg)
                        buy_report.append(msg)
                except Exception as e:
                    msg = f"✗ 매수 오류: {b['name']} -> {e}"
                    print(msg)
                    buy_report.append(msg)
                    
            if executed_any:
                report_lines = [
                    "📊 <b>[All Weather 적립식 투자 완료]</b>",
                    "• 계좌: <code>" + str(CANO) + "</code>",
                    "• 투입 신규 자금: <code>$" + f"{cash_usd:,.2f}" + " USD</code>",
                    "• 총자산: <code>$" + f"{total_asset:,.2f}" + " USD</code>",
                    "",
                    "<b>[매수 목록 (매도 없음)]</b>"
                ]
                report_lines.extend(buy_report)
                send_telegram("\n".join(report_lines))
            print("올웨더 적립식 투자 프로세스 완료.")
            
        else:
            print(f"\nℹ️ [모니터링 모드] 정기 리밸런싱 실행일이 아니며, 신규 자금 부족(${cash_usd:,.2f} USD < ${MIN_INFLOW_USD:.2f} USD)으로 매매 없이 작업을 종료합니다.")
            
    except Exception as e:
        err_msg = f"🚨 <b>All Weather 엔진 작동 실패</b>\n오류 내용: {e}"
        print(err_msg)
        send_telegram(err_msg)

if __name__ == "__main__":
    main()
