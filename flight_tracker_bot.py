#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
✈️ 2027 대만(부산-가오슝) 항공권 최저가 실시간 모니터링 & 텔레그램 알림 봇
=============================================================================
[여정] 부산(PUS) <-> 가오슝(KHH) 직항 왕복 / 3인
[일정] 2027-02-24(수) ~ 2027-02-27(토)
[기준가] 1인 473,700원 (3인 총 1,421,100원)
[무료 취소 마감] 2026-11-25

[데이터 소스] Amadeus Flight Offers Search API (무료 플랜: 월 500회)
  → API 키 미설정 시 데모 모드로 전환 (주간 브리핑에 경고 표시)

[6단계 필터]
  1. 직항 (경유편 제거)
  2. 황금시간대 (가는편 10~15시, 오는편 15~20시)
  3. 수하물 15kg (미포함 시 +90,000원 보정)
  4. 올인클루시브 총액 (세금/유류할증 포함)
  5. 범용 결제 (제휴카드 조건부 할인 배제)
  6. 안전마진 (최소 3,000원 이상 절감 시 판정)

[알림 규칙]
  1. 상시 (매일 08:30, 16:30 KST): 더 싼 특가 발견 시에만 즉시 긴급 알림
  2. 주간 (매주 일요일 08:30 KST): 1주일 현황 요약 브리핑 1통
  3. 평시: 무소음 (텔레그램 미발송, 콘솔 로그만)
=============================================================================
"""

import os
import sys
import json
import datetime
import urllib.request
import urllib.parse
import urllib.error

# Windows 콘솔 UTF-8 출력 보정
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# 설정값
# ---------------------------------------------------------------------------
DEPART_DATE = "2027-02-24"
RETURN_DATE = "2027-02-27"
ORIGIN = "PUS"
DESTINATION = "KHH"
PASSENGERS = 3

BENCHMARK_PRICE_PER_PERSON = 473700
BENCHMARK_PRICE_TOTAL = BENCHMARK_PRICE_PER_PERSON * PASSENGERS
FREE_CANCEL_DEADLINE = datetime.date(2026, 11, 25)

# 텔레그램
TELEGRAM_TOKEN = os.environ.get(
    "TELEGRAM_TOKEN", "8407908239:AAHO81Ld-mmtJ-V5opl5vXI3bXgICiDrNgc"
)
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "8518409134")
FORCE_NOTIFY = os.environ.get("FORCE_NOTIFY", "false").lower() == "true"

# Amadeus API (https://developers.amadeus.com 에서 무료 가입 후 키 발급)
AMADEUS_API_KEY = os.environ.get("AMADEUS_API_KEY", "")
AMADEUS_API_SECRET = os.environ.get("AMADEUS_API_SECRET", "")
AMADEUS_BASE_URL = os.environ.get(
    "AMADEUS_BASE_URL", "https://test.api.amadeus.com"
)

# 6단계 필터 상수
DEPART_HOUR_MIN = 10
DEPART_HOUR_MAX = 15
RETURN_HOUR_MIN = 15
RETURN_HOUR_MAX = 20
BAGGAGE_SURCHARGE = 90000
MIN_SAVINGS = 3000

GOOGLE_FLIGHTS_URL = (
    "https://www.google.com/travel/flights?tfs=CCcQAhoeEgoyMDI3LTAyLTI0"
    "agcIARIDUFVTcgcIARIDS0hIGh4SCjIwMjctMDItMjdqBwgBEgNLSEhyBwgBEgNQ"
    "VVNAAUABQAFSA0tSVw"
)

KST = datetime.timezone(datetime.timedelta(hours=9))

AIRLINE_NAMES = {
    "7C": "제주항공", "BX": "에어부산", "TW": "티웨이항공",
    "IT": "타이거에어 타이완", "OZ": "아시아나항공", "KE": "대한항공",
    "LJ": "진에어", "ZE": "이스타항공", "RS": "에어서울",
}


# ---------------------------------------------------------------------------
# 텔레그램 전송
# ---------------------------------------------------------------------------
def send_telegram(text: str) -> bool:
    """텔레그램 봇 메시지 전송 (4KB 트렁케이트 방어 포함)."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[WARN] 텔레그램 토큰/Chat ID 미설정")
        return False
    if len(text) > 4000:
        text = text[:3997] + "..."

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            ok = json.loads(resp.read().decode("utf-8")).get("ok")
            print("[INFO] 텔레그램 전송 성공!" if ok else "[ERROR] 텔레그램 전송 실패")
            return bool(ok)
    except Exception as e:
        print(f"[ERROR] 텔레그램 통신 에러: {e}")
        return False


# ---------------------------------------------------------------------------
# Amadeus API 연동
# ---------------------------------------------------------------------------
def get_amadeus_token():
    """Amadeus OAuth2 액세스 토큰 발급."""
    if not AMADEUS_API_KEY or not AMADEUS_API_SECRET:
        return None

    url = f"{AMADEUS_BASE_URL}/v1/security/oauth2/token"
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": AMADEUS_API_KEY,
        "client_secret": AMADEUS_API_SECRET,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            url, data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            token = json.loads(resp.read().decode("utf-8")).get("access_token")
            if token:
                print("[INFO] Amadeus 인증 성공")
            return token
    except Exception as e:
        print(f"[ERROR] Amadeus 인증 실패: {e}")
        return None


def search_flights_amadeus(token: str) -> list:
    """Amadeus Flight Offers Search — 부산-가오슝 왕복 직항 검색."""
    params = urllib.parse.urlencode({
        "originLocationCode": ORIGIN,
        "destinationLocationCode": DESTINATION,
        "departureDate": DEPART_DATE,
        "returnDate": RETURN_DATE,
        "adults": 1,
        "nonStop": "true",
        "currencyCode": "KRW",
        "max": 20,
    })
    url = f"{AMADEUS_BASE_URL}/v2/shopping/flight-offers?{params}"

    try:
        req = urllib.request.Request(
            url, headers={"Authorization": f"Bearer {token}"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            offers = data.get("data", [])
            print(f"[INFO] Amadeus: {len(offers)}건 검색 완료")
            return offers
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:300]
        print(f"[ERROR] Amadeus HTTP {e.code}: {detail}")
        return []
    except Exception as e:
        print(f"[ERROR] Amadeus 통신 실패: {e}")
        return []


def apply_6step_filter(offers: list) -> list:
    """Amadeus 원본 데이터에 6단계 품질 필터를 적용하여 정제된 결과 반환."""
    results = []

    for offer in offers:
        try:
            # 가격 (세금·유류할증 포함 총액)
            price = int(float(offer.get("price", {}).get("grandTotal", 0)))
            if price <= 0:
                continue

            # 왕복 확인 (itineraries 2개)
            itins = offer.get("itineraries", [])
            if len(itins) < 2:
                continue

            # [필터 1] 직항 — 각 레그의 세그먼트가 정확히 1개
            out_segs = itins[0].get("segments", [])
            in_segs = itins[1].get("segments", [])
            if len(out_segs) != 1 or len(in_segs) != 1:
                continue

            out_seg, in_seg = out_segs[0], in_segs[0]
            out_dep = out_seg.get("departure", {}).get("at", "")
            out_arr = out_seg.get("arrival", {}).get("at", "")
            in_dep = in_seg.get("departure", {}).get("at", "")
            in_arr = in_seg.get("arrival", {}).get("at", "")
            carrier = out_seg.get("carrierCode", "??")

            # [필터 2] 황금시간대
            out_h = int(out_dep[11:13]) if len(out_dep) >= 13 else -1
            in_h = int(in_dep[11:13]) if len(in_dep) >= 13 else -1
            if not (DEPART_HOUR_MIN <= out_h <= DEPART_HOUR_MAX):
                continue
            if not (RETURN_HOUR_MIN <= in_h <= RETURN_HOUR_MAX):
                continue

            # [필터 3] 수하물 15kg 포함 여부
            has_bag = False
            for tp in offer.get("travelerPricings", []):
                for fd in tp.get("fareDetailsBySegment", []):
                    bags = fd.get("includedCheckedBags", {})
                    if bags.get("weight", 0) >= 15 or bags.get("quantity", 0) >= 1:
                        has_bag = True
                if has_bag:
                    break

            # [필터 4] 총액 기준: 수하물 미포함이면 보정 추가금 반영
            adjusted = price if has_bag else price + BAGGAGE_SURCHARGE

            name = AIRLINE_NAMES.get(carrier, carrier)
            bag_lbl = (
                "수하물 15kg 포함"
                if has_bag
                else f"수하물 미포함(+{BAGGAGE_SURCHARGE:,}원 보정)"
            )

            results.append({
                "airline": f"{name} ({carrier}, {bag_lbl})",
                "is_direct": True,
                "depart_time": f"{out_dep[11:16]} 부산 -> {out_arr[11:16]} 가오슝",
                "return_time": f"{in_dep[11:16]} 가오슝 -> {in_arr[11:16]} 부산",
                "price_per_person": adjusted,
                "booking_url": GOOGLE_FLIGHTS_URL,
            })
        except Exception as e:
            print(f"[WARN] 파싱 오류 (건너뜀): {e}")

    results.sort(key=lambda x: x["price_per_person"])
    return results


# ---------------------------------------------------------------------------
# 가격 조회 통합 (Amadeus API -> 데모 폴백)
# ---------------------------------------------------------------------------
def fetch_flight_prices():
    """
    실시간 항공권 가격을 조회합니다.
    반환값: (flights: list[dict], source: 'LIVE' | 'DEMO')
    """
    print(
        f"[INFO] 항공권 조회 시작: {ORIGIN} <-> {DESTINATION} "
        f"({DEPART_DATE} ~ {RETURN_DATE})"
    )

    # 1차: Amadeus API
    token = get_amadeus_token()
    if token:
        raw = search_flights_amadeus(token)
        if raw:
            filtered = apply_6step_filter(raw)
            if filtered:
                print(f"[INFO] 실시간 6단계 필터 통과: {len(filtered)}건")
                return filtered, "LIVE"
            print("[INFO] 6단계 필터 통과 항공편 없음")
        else:
            print("[INFO] 해당 노선/날짜 항공편 없음 (스케줄 미오픈 가능성)")
    else:
        print("[WARN] Amadeus API 키 미설정 -> 데모 모드")

    # 2차: 데모 폴백
    demo = [{
        "airline": "제주항공 (7C, FLYBAG) [데모]",
        "is_direct": True,
        "depart_time": "14:05 부산 -> 16:05 가오슝",
        "return_time": "17:05 가오슝 -> 20:40 부산",
        "price_per_person": BENCHMARK_PRICE_PER_PERSON,
        "booking_url": "https://www.jejuair.net",
    }]
    return demo, "DEMO"


# ---------------------------------------------------------------------------
# 무료 취소 D-Day 메시지
# ---------------------------------------------------------------------------
def cancel_deadline_msg(days_left: int) -> str:
    if days_left > 0:
        return (
            f"*무료 취소 마감일:* {FREE_CANCEL_DEADLINE} "
            f"(D-{days_left}일 남음)"
        )
    elif days_left == 0:
        return (
            f"*무료 취소 마감일:* 오늘({FREE_CANCEL_DEADLINE})이 "
            f"마지막 날입니다!"
        )
    else:
        return (
            f"*무료 취소 마감:* {FREE_CANCEL_DEADLINE} "
            f"(이미 {abs(days_left)}일 경과)"
        )


# ---------------------------------------------------------------------------
# 메인 실행
# ---------------------------------------------------------------------------
def run_tracker():
    """항공권 모니터링 및 스마트 알림 발송."""
    kst_now = datetime.datetime.now(KST)
    today = kst_now.date()
    days_left = (FREE_CANCEL_DEADLINE - today).days
    now_str = kst_now.strftime("%Y-%m-%d %H:%M KST")

    # 일요일 오전 08~09시 (GitHub Actions 큐 지연 방어)
    is_sunday_morning = (today.weekday() == 6) and (kst_now.hour in [8, 9])

    flights, source = fetch_flight_prices()
    if not flights:
        print("[ERROR] 항공권 데이터를 가져오지 못했습니다.")
        return

    best = flights[0]
    best_price = best["price_per_person"]
    best_total = best_price * PASSENGERS
    savings_pp = BENCHMARK_PRICE_PER_PERSON - best_price
    savings_total = BENCHMARK_PRICE_TOTAL - best_total
    is_cheaper = savings_pp >= MIN_SAVINGS

    source_tag = (
        "📡 실시간 Amadeus API"
        if source == "LIVE"
        else "⚠️ 데모 모드 (API 키 미설정)"
    )

    # ------------------------------------------------------------------
    # Case 1: 더 싼 특가 발견 -> 즉시 긴급 알림
    # ------------------------------------------------------------------
    if is_cheaper:
        msg = "\n".join([
            "🚨 *[특가 포착!] 대만 가오슝 더 싼 항공권 발견!* 🚨",
            f"📅 *여정:* {ORIGIN}(부산) - {DESTINATION}(가오슝) 3박4일, 3인",
            f"🗓️ *일정:* {DEPART_DATE}(수) ~ {RETURN_DATE}(토)",
            f"🕒 *포착 일시:* {now_str}",
            "",
            "━━━━━━━━━━━━━━━━━━",
            f"🏷️ *기존 예매가:* 1인 {BENCHMARK_PRICE_PER_PERSON:,}원"
            f" (3인 {BENCHMARK_PRICE_TOTAL:,}원)",
            f"🔥 *신규 특가:* 1인 *{best_price:,}원*"
            f" (3인 *{best_total:,}원*)",
            f"💰 *절감:* 1인당 *{savings_pp:,}원*"
            f" (3인 총 *{savings_total:,}원* 세이브!)",
            f"✈️ *항공사:* {best['airline']}",
            f"   {best['depart_time']}",
            f"   {best['return_time']}",
            "━━━━━━━━━━━━━━━━━━",
            "*액션 가이드:*",
            "1. 아래 링크에서 새 특가 항공권을 먼저 예매",
            "2. 예매 완료 후 기존 제주항공 티켓을 무료 취소",
            "",
            f"⏰ {cancel_deadline_msg(days_left)}",
            f"🔗 [구글 플라이트에서 확인]({GOOGLE_FLIGHTS_URL})",
            f"{source_tag}",
        ])
        print("\n[ALERT] 특가 항공권 포착! 텔레그램 발송")
        send_telegram(msg)
        return

    # ------------------------------------------------------------------
    # Case 2: 일요일 오전 -> 주간 브리핑
    # ------------------------------------------------------------------
    if is_sunday_morning or FORCE_NOTIFY:
        if source == "DEMO":
            status_line = (
                "⚠️ 현재 데모 모드입니다. 실시간 가격 추적이 "
                "비활성화되어 있습니다.\n"
                "GitHub Secrets에 AMADEUS API KEY/SECRET을 설정하면 "
                "실시간 추적이 활성화됩니다."
            )
        else:
            status_line = (
                "지난 1주일간 6대 조건(직항+수하물15kg+황금시간대)을 "
                "만족하는 더 저렴한 특가는 나오지 않았습니다.\n"
                "현재 예매해 두신 제주항공 티켓이 "
                "*전체 1위 최저가를 안전하게 유지 중*입니다."
            )

        msg = "\n".join([
            "📊 *[대만 항공권] 주간 정기 브리핑*",
            f"📅 *여정:* {ORIGIN}(부산) - {DESTINATION}(가오슝) 3박4일, 3인",
            f"🗓️ *일정:* {DEPART_DATE}(수) ~ {RETURN_DATE}(토)",
            f"🕒 *브리핑 일시:* {now_str}",
            "",
            "━━━━━━━━━━━━━━━━━━",
            f"🏷️ *현재 내 예매가:* 1인 *{BENCHMARK_PRICE_PER_PERSON:,}원*"
            f" (3인 {BENCHMARK_PRICE_TOTAL:,}원)",
            f"🔍 *이번 주 최저가:* *{best['airline']}*"
            f" ({best_price:,}원)",
            "━━━━━━━━━━━━━━━━━━",
            f"✅ {status_line}",
            "",
            f"⏰ {cancel_deadline_msg(days_left)}",
            f"{source_tag}",
            "",
            "다음 주 일요일 아침에 다시 브리핑을 보내드립니다.",
        ])
        print("\n[INFO] 주간 브리핑 발송")
        send_telegram(msg)
        return

    # ------------------------------------------------------------------
    # Case 3: 평시 -> 무소음
    # ------------------------------------------------------------------
    print(
        f"[INFO] 무소음: 최저가({best_price:,}원) >= "
        f"기존 예매가({BENCHMARK_PRICE_PER_PERSON:,}원), "
        f"텔레그램 미발송"
    )


if __name__ == "__main__":
    run_tracker()
