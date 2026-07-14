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

# .env 파일에서 계좌 정보 및 API 키 로드
load_dotenv()

# KIS 모의투자 여부 판단 (True: 모의투자, False: 실전투자)
KIS_MOCK = os.getenv("KIS_MOCK", "False").lower() in ("true", "1", "yes")

# KIS Dry-run 여부 판단 (True: 실제 주문 제출 제외, 시뮬레이션 및 검증 로깅만 수행)
KIS_DRY_RUN = os.getenv("KIS_DRY_RUN", "False").lower() in ("true", "1", "yes")

# Fat Finger 방지 최대 단일 주문 금액 제한 (기본값: 1억 원)
MAX_ORDER_AMOUNT = int(os.getenv("MAX_ORDER_AMOUNT", "100000000"))

# 모의투자 모드 여부에 따른 KIS 인증키 및 접속 주소 설정
if KIS_MOCK:
    APP_KEY = os.getenv("KIS_MOCK_APP_KEY", "")
    APP_SECRET = os.getenv("KIS_MOCK_APP_SECRET", "")
    URL_BASE = "https://openapivts.koreainvestment.com:29443"
else:
    APP_KEY = os.getenv("KIS_APP_KEY", "")
    APP_SECRET = os.getenv("KIS_APP_SECRET", "")
    URL_BASE = "https://openapi.koreainvestment.com:9443"

# 포트폴리오 티커 설정
TICKER_KOSPI = "069500"   # KODEX 200 (한국 대표 주식)
TICKER_SP500 = "360750"   # TIGER 미국S&P500 (미국 대표 주식)
TICKER_SAFE  = "304580"   # KODEX 미국달러단기채권 (안전자산 피신처)

TICKER_NAMES = {
    TICKER_KOSPI: "KODEX 200 (한국 대표 주식)",
    TICKER_SP500: "TIGER 미국S&P500 (미국 대표 주식)",
    TICKER_SAFE: "KODEX 미국달러단기채권 (안전자산 피신처)"
}

# 계좌 정의 및 동적 매핑
ACCOUNTS = []
if KIS_MOCK:
    mock_cano1 = os.getenv("KIS_MOCK_CANO1", "")
    mock_cano2 = os.getenv("KIS_MOCK_CANO2", "")
    if mock_cano1:
        ACCOUNTS.append({"name": "모의_주식계좌1", "cano": mock_cano1, "prdt_cd": "01"})
    if mock_cano2:
        ACCOUNTS.append({"name": "모의_주식계좌2", "cano": mock_cano2, "prdt_cd": "01"})
    
    # 별도 모의계좌 변수가 세팅되지 않은 경우, 기존 실전 변수를 재활용하되 상품코드를 01로 맵핑
    if not ACCOUNTS:
        pension_cano = os.getenv("KIS_PENSION_CANO", "")
        stock_cano = os.getenv("KIS_STOCK_CANO", "")
        if pension_cano:
            ACCOUNTS.append({"name": "모의_연금대체계좌", "cano": pension_cano, "prdt_cd": "01"})
        if stock_cano:
            ACCOUNTS.append({"name": "모의_개인주식계좌", "cano": stock_cano, "prdt_cd": "01"})
else:
    ACCOUNTS = [
        {"name": "연금저축계좌", "cano": os.getenv("KIS_PENSION_CANO", ""), "prdt_cd": "22"},
        {"name": "개인주식계좌", "cano": os.getenv("KIS_STOCK_CANO", ""), "prdt_cd": "01"}
    ]

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

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

def is_market_open():
    """주식시장 정규장 운영 시간 여부 판단 (평일 09:00 ~ 15:30)"""
    now = datetime.datetime.now()
    # 요일 검사: 월요일(0) ~ 금요일(4)
    if now.weekday() >= 5:
        return False
    # 시간 검사: 09:00 ~ 15:30
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
    res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10, verify=False)
    if res.status_code == 200:
        return res.json()["access_token"]
    else:
        raise Exception(f"토큰 발급 오류 (모드_모의={KIS_MOCK}): {res.text}")

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
    res = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
    if res.status_code != 200:
        raise Exception(f"잔고 조회 API 호출 실패: {res.text}")
        
    data = res.json()
    if data.get("rt_cd") != "0":
        raise Exception(f"잔고 조회 API 실패 ({data.get('msg_cd')}): {data.get('msg1')}")
    
    try:
        cash = int(data["output2"][0]["dnca_tot_amt"])
    except (KeyError, IndexError, TypeError):
        try:
            cash = int(data["output2"][0]["prvs_rcvb_evt_amt"])
        except Exception:
            cash = 0
            
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
    - order_type: BUY(매수, 지정가 권장), SELL(매도, 시장가 권장)
    - ord_dvsn: 00(시장가), 01(지정가)
    - price: 지정가(01) 주문 시 적용할 가격
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
    
    unpr = "0" if ord_dvsn == "00" else str(int(price))
    
    body = {
        "CANO": cano,
        "ACNT_PRDT_CD": prdt_cd,
        "PDNO": ticker,
        "ORD_DVSN": ord_dvsn,
        "ORD_QTY": str(qty),
        "ORD_UNPR": unpr
    }
    
    res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10, verify=False)
    if res.status_code != 200:
        raise Exception(f"주문 통신 오류: {res.text}")
        
    return res.json()

def calculate_momentum_signals():
    """Yahoo Finance API를 이용한 12개월 모멘텀 지표 산출"""
    def get_12m_return(symbol):
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1mo&range=2y"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10, verify=False)
        if res.status_code != 200:
            raise Exception(f"Yahoo Finance API 연동 실패: {symbol}")
        result = res.json()["chart"]["result"][0]
        prices = result["indicators"]["quote"][0]["close"]
        prices = [p for p in prices if p is not None]
        if len(prices) < 13:
            raise Exception(f"충분한 데이터를 확보하지 못했습니다: {symbol}")
        return (prices[-1] - prices[-13]) / prices[-13]

    print(">> 글로벌 증시 12개월 수익률 분석 중...")
    ret_ko = get_12m_return("^KS11") # KOSPI 지수
    ret_us = get_12m_return("^GSPC") # S&P 500 지수
    
    print(f"■ 모멘텀 데이터 분석 결과:")
    print(f"   - KOSPI 200 12개월 모멘텀: {ret_ko*100:.2f}%")
    print(f"   - S&P 500   12개월 모멘텀: {ret_us*100:.2f}%")
    
    chosen_symbol = TICKER_SP500 if ret_us > ret_ko else TICKER_KOSPI
    chosen_ret = ret_us if ret_us > ret_ko else ret_ko
    
    if chosen_ret > 0:
        target = chosen_symbol
        reason = f"상승 추세 추종 (선택 자산 12m 수익률: {chosen_ret*100:.2f}%)"
    else:
        target = TICKER_SAFE
        reason = f"글로벌 대세 하락장 감지 안전자산 피신 (선택 자산 12m 수익률: {chosen_ret*100:.2f}%)"
        
    return target, reason

def rebalance_account(token, acc, target_ticker):
    name, cano, prdt_cd = acc["name"], acc["cano"], acc["prdt_cd"]
    print(f"\n=========================================")
    print(f"🔄 [{name}] 자산 리밸런싱 시작 ({cano}-{prdt_cd})")
    print(f"=========================================")
    
    # 2중 보안 검증: 연금저축계좌(22) 및 모의 연금대체계좌(이름에 '연금' 포함)에서는 당사 3대 ETF 외의 매수 거래가 발생하지 않도록 원천 격리
    valid_tickers = [TICKER_KOSPI, TICKER_SP500, TICKER_SAFE]
    if (prdt_cd == "22" or "연금" in name) and target_ticker not in valid_tickers:
        raise ValueError(f"🚨 [보안 침해 예방] 연금계좌[{name}]에서 유효하지 않은 자산 매수 시도 차단: {target_ticker}")
    
    cash, holdings = get_account_balance(token, cano, prdt_cd)
    print(f">> 예수금 현황: {cash:,} 원 | 보유 자산 종류: {list(holdings.keys())}")
    
    # 1. 포지션 정리 (타겟 자산이 아닌 보유 자산 전량 매도)
    sold_any = False
    for ticker, info in holdings.items():
        if ticker != target_ticker:
            print(f"➔ [청산 매도] 비타겟 자산 전량 시장가 매도 집행: {ticker} (수량: {info['qty']})")
            # 매도 주문은 청산의 즉시성 및 확실성을 위해 시장가(ord_dvsn="00")로 집행
            res = submit_order(token, cano, prdt_cd, ticker, info["qty"], "SELL", ord_dvsn="00")
            
            # Fail-Fast 메커니즘: 매도 주문 중 하나라도 실패 시 즉시 거래 전체 중단 (미수금 및 보유 비율 파괴 방지)
            if res.get("rt_cd") != "0":
                err_msg = f"🚨 [Fail-Fast 매도 실패] {ticker} 청산 매도 주문이 실패했습니다! (사유: {res.get('msg1')})"
                raise Exception(err_msg)
                
            print(f"   결과: 성공 | 주문번호: {res.get('output', {}).get('ODNO')}")
            sold_any = True
            time.sleep(1.5) # 과도한 API 호출 방지
            
    if sold_any:
        print(">> 매도 정산 및 예수금 갱신 대기 (10초)...")
        time.sleep(10)
        cash, holdings = get_account_balance(token, cano, prdt_cd)
        
    # 2. 타겟 자산 비중 조율 (현 예수금을 기반으로 지정가 매수 집행)
    # 현재 가격 조회 API 호출
    url_price = f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST01010100"
    }
    params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": target_ticker}
    res_price = requests.get(url_price, headers=headers, params=params, timeout=10, verify=False)
    if res_price.status_code != 200:
        raise Exception(f"현재가 조회 API 통신 실패: {res_price.text}")
    
    price_data = res_price.json()
    if price_data.get("rt_cd") != "0":
        raise Exception(f"현재가 조회 API 실패: {price_data.get('msg1')}")
        
    curr_price = float(price_data["output"]["stck_prpr"])
    
    curr_eval = holdings.get(target_ticker, {}).get("eval_amt", 0)
    total_asset = cash + curr_eval
    
    # 이미 목표 비중에 도달했는지 검증 (95% 이상 보유 시 무주문 패스)
    if total_asset > 0 and curr_eval > (total_asset * 0.95):
        print(f">> [{name}] 이미 목표 자산({target_ticker})이 포트폴리오의 95% 이상을 차지하고 있어 거래를 생략합니다.")
        return f"🔄 [{name}] 현재 포지션 유지 ({target_ticker})"
        
    # 지정가 매수로 130% 마진 트랩 우회 (가용 예수금의 98% 수준을 타겟 단일가 주문금액으로 삼음)
    # 매수 잔량의 체결 안정성을 위해 가용 가중치를 98%로 미세 조율
    target_buy_fund = cash * 0.98
    buy_qty = int(target_buy_fund // curr_price)
    
    # Fat Finger 방지용 최종 안전 벨트 검증 (단일 주문 금액 상한 검사)
    estimated_buy_amount = buy_qty * curr_price
    if estimated_buy_amount > MAX_ORDER_AMOUNT:
        raise ValueError(
            f"🚨 [Fat Finger 차단] 계산된 주문 금액 {estimated_buy_amount:,}원이 "
            f"설정된 최대 주문 제한 금액 {MAX_ORDER_AMOUNT:,}원을 초과했습니다!"
        )
        
    if buy_qty > 0:
        print(f"➔ [포지션 진입] 타겟 자산 지정가 매수: {target_ticker} (수량: {buy_qty}주, 단가: {curr_price:,}원)")
        # 매수 주문은 130% 마진 체크 회피를 위해 지정가(ord_dvsn="01", price=curr_price)로 집행
        res = submit_order(token, cano, prdt_cd, target_ticker, buy_qty, "BUY", price=curr_price, ord_dvsn="01")
        
        if res.get("rt_cd") == "0":
            msg = f"✅ [{name}] 리밸런싱 수행 완료!\n매수 자산: {target_ticker}\n수량: {buy_qty}주 (단가: {curr_price:,}원)"
        else:
            msg = f"❌ [{name}] 리밸런싱 주문 실패!\n사유: {res.get('msg1')} (에러코드: {res.get('rt_cd')}/{res.get('msg_cd')})"
        print(msg)
        return msg
    else:
        print(f">> [{name}] 가용 예수금이 부족하여 주문을 발행하지 않습니다. (예수금: {cash:,}원)")
        return f"⚠️ [{name}] 예수금 부족 주문 취소"

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
    # 1. 실행일 판정 게이트 작동
    today = datetime.date.today()
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

    start_time = time.strftime("%Y-%m-%d %H:%M:%S")
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
        target_ticker, reason = calculate_momentum_signals()
        
        ticker_name = TICKER_NAMES.get(target_ticker, "알 수 없는 종목")
        summary_msg = f"📈 금월 투자 대상 선정: {target_ticker} ({ticker_name})\n판단 근거: {reason}\n"
        send_telegram(summary_msg)
        
        results = []
        for acc in ACCOUNTS:
            if not acc["cano"] or acc["cano"].startswith("YOUR_"):
                print(f">> 계좌 번호 미세팅 또는 예시 텍스트로 {acc['name']}를 생략합니다.")
                continue
            try:
                res_msg = rebalance_account(token, acc, target_ticker)
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

