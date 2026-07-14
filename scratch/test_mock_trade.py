# -*- coding: utf-8 -*-
"""
KIS Mock Trading API Verification Script
Tests Authentication -> Balance -> Price Query -> BUY -> Reconciliation -> SELL -> Final Balance
"""
import os
import sys
import time
import requests
import json
from dotenv import load_dotenv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# UTF-8 Console Support for Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Load .env from parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(parent_dir, ".env")
print(f">> 로딩할 .env 경로: {dotenv_path}")
load_dotenv(dotenv_path)

APP_KEY = os.getenv("KIS_MOCK_APP_KEY", "")
APP_SECRET = os.getenv("KIS_MOCK_APP_SECRET", "")
CANO = os.getenv("KIS_MOCK_CANO1", "")
PRDT_CD = "01" # Mock is always 01 (General Stock Account)
URL_BASE = "https://openapivts.koreainvestment.com:29443"

# Target Stock: Samsung Electronics (005930)
TICKER_TEST = "005930"

print(f"■ 검증 설정 확인:")
print(f"   - API Key: {APP_KEY[:10]}...")
print(f"   - CANO: {CANO}")
print(f"   - URL Base: {URL_BASE}")
print(f"   - 테스트 종목: {TICKER_TEST} (삼성전자)")

if not APP_KEY or not APP_SECRET or not CANO:
    print("🚨 [에러] .env 파일에 모의투자 키(KIS_MOCK_APP_KEY, KIS_MOCK_APP_SECRET, KIS_MOCK_CANO1)가 올바르게 설정되어 있지 않습니다!")
    sys.exit(1)

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
        token = res.json()["access_token"]
        print("✅ [1단계 통과] OAuth2 토큰 발급 성공")
        return token
    else:
        raise Exception(f"토큰 발급 실패: {res.text}")

def get_account_balance(token):
    url = f"{URL_BASE}/uapi/domestic-stock/v1/trading/inquire-balance"
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "VTTC8434R"
    }
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": PRDT_CD,
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
        raise Exception(f"잔고 조회 통신 실패: {res.text}")
    data = res.json()
    if data.get("rt_cd") != "0":
        raise Exception(f"잔고 조회 API 실패 ({data.get('msg_cd')}): {data.get('msg1')}")
    
    cash = int(data["output2"][0]["dnca_tot_amt"])
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
    print(f"✅ [2단계 통과] 잔고 조회 성공 (예수금: {cash:,}원, 보유 자산 종류: {list(holdings.keys())})")
    return cash, holdings

def get_current_price(token, ticker):
    url = f"{URL_BASE}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST01010100"
    }
    params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": ticker}
    res = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
    if res.status_code != 200:
        raise Exception(f"현재가 조회 통신 실패: {res.text}")
    data = res.json()
    if data.get("rt_cd") != "0":
        raise Exception(f"현재가 조회 API 실패: {data.get('msg1')}")
    curr_price = float(data["output"]["stck_prpr"])
    print(f"✅ [3단계 통과] {ticker} 현재가 조회 성공: {curr_price:,}원")
    return curr_price

def submit_order(token, ticker, qty, order_type="BUY", price=0, ord_dvsn="00"):
    """
    모의투자 주문 발행
    - BUY TR_ID: VTTC0012U
    - SELL TR_ID: VTTC0011U
    - ord_dvsn: 00 (시장가), 01 (지정가)
    """
    tr_id = "VTTC0012U" if order_type == "BUY" else "VTTC0011U"
    url = f"{URL_BASE}/uapi/domestic-stock/v1/trading/order-cash"
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id
    }
    
    unpr = "0" if ord_dvsn == "00" else str(int(price))
    
    body = {
        "CANO": CANO,
        "ACNT_PRDT_CD": PRDT_CD,
        "PDNO": ticker,
        "ORD_DVSN": ord_dvsn,
        "ORD_QTY": str(qty),
        "ORD_UNPR": unpr
    }
    res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10, verify=False)
    if res.status_code != 200:
        raise Exception(f"주문 통신 실패: {res.text}")
    data = res.json()
    if data.get("rt_cd") == "0":
        odno = data.get("output", {}).get("ODNO")
        print(f"✅ [주문 성공] {order_type} | 종목: {ticker} | 수량: {qty}주 | 구분: {ord_dvsn} | 가격: {unpr}원 | 주문번호: {odno}")
        return data
    else:
        raise Exception(f"주문 API 실패: {data.get('msg1')} (에러코드: {data.get('rt_cd')}/{data.get('msg_cd')})")

def main():
    print("\n==========================================")
    print("🧪 KIS 모의투자 매매 기능 전주기 검증 시작")
    print("==========================================")
    
    try:
        # 1단계: 토큰 발급
        token = get_access_token()
        
        # 2단계: 예수금 및 기존 잔고 조회
        initial_cash, initial_holdings = get_account_balance(token)
        
        # 기존 보유 수량 파악
        existing_qty = initial_holdings.get(TICKER_TEST, {}).get("qty", 0)
        print(f">> 기존 {TICKER_TEST} 보유 수량: {existing_qty}주")
        
        # 3단계: 현재가 조회
        curr_price = get_current_price(token, TICKER_TEST)
        
        # 예수금 부족 여부 체크
        if initial_cash < curr_price * 1.1:
            print(f"🚨 [에러] 예수금이 부족합니다. 현재가: {curr_price:,}원, 가용 예수금: {initial_cash:,}원")
            print("모의투자 신청 페이지에서 예수금을 재충전하거나 충분한 금액을 확보해야 합니다.")
            sys.exit(1)
            
        # 4단계: 모의 매수 주문 실행 (지정가 1주 - 실제 봇과 동일)
        print(f"\n➔ [매수 집행] 1주 지정가 매수 시작... (지정가: {curr_price:,}원)")
        submit_order(token, TICKER_TEST, 1, "BUY", price=curr_price, ord_dvsn="01")
        
        # 5단계: 매수 체결 완료 및 반영 대기 (5초)
        print(">> 지정가 매수 주문 체결 및 반영 대기 (5초)...")
        time.sleep(5)
        
        # 잔고 갱신 확인
        post_buy_cash, post_buy_holdings = get_account_balance(token)
        new_qty = post_buy_holdings.get(TICKER_TEST, {}).get("qty", 0)
        print(f">> 매수 후 {TICKER_TEST} 보유 수량: {new_qty}주 (증가량: {new_qty - existing_qty}주)")
        
        if new_qty > existing_qty:
            print("✅ [5단계 통과] 매수 체결 및 잔고 반영 확인 완료!")
        else:
            raise Exception("❌ [실패] 매수한 주식이 잔고에 반영되지 않았습니다. (체결 대기 시간 부족 또는 미체결)")
            
        # 6단계: 모의 매도 주문 실행 (지정가 1주 매도하여 청산)
        print(f"\n➔ [매도 집행] 1주 지정가 매도 청산 시작... (지정가: {curr_price:,}원)")
        submit_order(token, TICKER_TEST, 1, "SELL", price=curr_price, ord_dvsn="01")
        
        # 최종 반영 대기 (5초)
        print(">> 매도 정산 및 반영 대기 (5초)...")
        time.sleep(5)
        
        # 최종 잔고 갱신 확인
        final_cash, final_holdings = get_account_balance(token)
        final_qty = final_holdings.get(TICKER_TEST, {}).get("qty", 0)
        print(f">> 최종 {TICKER_TEST} 보유 수량: {final_qty}주 (감소량: {new_qty - final_qty}주)")
        
        if final_qty == existing_qty:
            print("✅ [6단계 통과] 매도 체결 및 잔고 청산 반영 확인 완료!")
            print("\n==========================================")
            print("🎉 [SUCCESS] KIS 모의투자 매수 및 매도 전주기 철저 검증 완료!")
            print("==========================================")
        else:
            raise Exception("❌ [실패] 매도 청산 후 수량이 일치하지 않습니다.")
            
    except Exception as e:
        print(f"\n🚨 [FAILURE] 검증 과정 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
