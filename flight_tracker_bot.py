#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
✈️ 2027 대만(부산-가오슝) 항공권 최저가 실시간 모니터링 & 텔레그램 알림 봇 v3.3
=============================================================================
[여정 정보]
  - 출발지 / 도착지: 김해국제공항(PUS) ↔ 가오슝국제공항(KHH)
  - 일정: 2027-02-24(수) ~ 2027-02-27(토) [3박 4일 왕복]
  - 인원: 성인 3인
  - 기준 예매가: 1인 473,700원 (3인 총 1,421,100원, 제주항공 직항)
  - 무료 취소 마감일: 2026-11-25

[동작 원칙 (최우선 수칙)]
  - "틀린 알림을 보내는 것이 알림을 안 보내는 것보다 훨씬 나쁘다."
  - 판정에 확신이 없거나 모호하면 후보에서 제외하고 로그만 남김.
  - Fail-Closed: 출발시각, 직항 여부, 가격 단서 중 하나라도 식별 불가 시 제외.
  - 가짜 Fallback 피드 완전 배제: 실패는 실패로 기록하고 2회 연속 실패 시 장애 알림 발송.

[실시간 파싱 & 검증 엔진]
  - TFS Protobuf URL 동적 생성 (상수 기반 실시간 인코딩)
  - Playwright Headless Chromium 개별 카드 격리 파싱 (`ul li` 카드 단위)
  - 직항 엄격 검증 ("직항" 존재 AND "경유" 부재, "경유 없음" 오탐 방어)
  - 황금시간대 검증 (가는 편 10:00 ~ 15:59 출발, 소요시간 오인 및 AM/PM 교차 오염 방어)
  - 다중 가격 파서 & 1인당/총액 쌍 식별 엔진 (수수료 제외 및 중복 나누기 방지)
  - HTML 서식 및 오류 복구 (HTML 이스케이프, 400 에러 시 평문 재시도)
  - 상태 보존 (`state.json`): 7일 만료/반등 래칫 리셋, 실측 통계 기반 동적 주간 브리핑
=============================================================================
"""

import os
import sys
import json
import time
import re
import html
import base64
import datetime
import argparse
import urllib.request
import urllib.parse
import urllib.error
from collections import Counter

# Windows 콘솔 UTF-8 출력 보정
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# 핵심 여정 상수
# ---------------------------------------------------------------------------
DEPART_DATE = "2027-02-24"
RETURN_DATE = "2027-02-27"
ORIGIN = "PUS"          # 부산(김해)
DESTINATION = "KHH"     # 대만 가오슝
PASSENGERS = 3          # 성인 3명

BENCHMARK_PRICE_PER_PERSON = 473700
BENCHMARK_PRICE_TOTAL = BENCHMARK_PRICE_PER_PERSON * PASSENGERS  # 1,421,100원
FREE_CANCEL_DEADLINE = datetime.date(2026, 11, 25)
MIN_SAVINGS = 3000      # 최소 3,000원 이상 절감 시에만 특가 판정

# 파일 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "state.json")

# 텔레그램 환경변수 (하드코딩 기본값 절대 금지)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

KST = datetime.timezone(datetime.timedelta(hours=9))


# ---------------------------------------------------------------------------
# Protobuf Varint 및 TFS URL 생성기 (A-2)
# ---------------------------------------------------------------------------
def _encode_varint(value: int) -> bytes:
    bits = value & 0x7F
    value >>= 7
    ret = bytearray()
    while value:
        ret.append(0x80 | bits)
        bits = value & 0x7F
        value >>= 7
    ret.append(bits)
    return bytes(ret)

def _encode_tag(field_num: int, wire_type: int) -> bytes:
    return _encode_varint((field_num << 3) | wire_type)

def _encode_string(field_num: int, val: str) -> bytes:
    b = val.encode("utf-8")
    return _encode_tag(field_num, 2) + _encode_varint(len(b)) + b

def _encode_submessage(field_num: int, sub_bytes: bytes) -> bytes:
    return _encode_tag(field_num, 2) + _encode_varint(len(sub_bytes)) + sub_bytes

def generate_google_flights_tfs(origin: str, dest: str, depart_date: str, return_date: str, passengers: int, currency: str = "KRW") -> str:
    """Google Flights Protobuf TFS 파라미터를 동적으로 직렬화하여 생성."""
    # Leg 1: Going flight
    leg1 = bytearray()
    leg1.extend(_encode_string(2, depart_date))
    orig_entity = _encode_tag(1, 0) + _encode_varint(1) + _encode_string(2, origin)
    leg1.extend(_encode_submessage(13, orig_entity))
    dest_entity = _encode_tag(1, 0) + _encode_varint(1) + _encode_string(2, dest)
    leg1.extend(_encode_submessage(14, dest_entity))

    # Leg 2: Return flight
    leg2 = bytearray()
    leg2.extend(_encode_string(2, return_date))
    ret_orig_entity = _encode_tag(1, 0) + _encode_varint(1) + _encode_string(2, dest)
    leg2.extend(_encode_submessage(13, ret_orig_entity))
    ret_dest_entity = _encode_tag(1, 0) + _encode_varint(1) + _encode_string(2, origin)
    leg2.extend(_encode_submessage(14, ret_dest_entity))

    msg = bytearray()
    msg.extend(_encode_tag(1, 0) + _encode_varint(39))
    msg.extend(_encode_tag(2, 0) + _encode_varint(2))  # Round-trip
    msg.extend(_encode_submessage(3, bytes(leg1)))
    msg.extend(_encode_submessage(3, bytes(leg2)))
    for _ in range(passengers):
        msg.extend(_encode_tag(8, 0) + _encode_varint(1))  # Adults
    msg.extend(_encode_string(10, currency))

    return base64.urlsafe_b64encode(bytes(msg)).decode("ascii").rstrip("=")

def decode_google_flights_tfs(tfs_str: str) -> dict:
    """TFS Protobuf 문자열을 역직렬화하여 파라미터 복원 (--self-test 검증용)."""
    pad = (4 - len(tfs_str) % 4) % 4
    raw = base64.urlsafe_b64decode(tfs_str + "==="[:pad])

    def parse_raw(data):
        fields = {}
        i = 0
        while i < len(data):
            tag_byte = data[i]
            field_num = tag_byte >> 3
            wire_type = tag_byte & 7
            i += 1
            if wire_type == 0:
                val = 0
                shift = 0
                while True:
                    byte = data[i]
                    i += 1
                    val |= (byte & 0x7F) << shift
                    if not (byte & 0x80):
                        break
                    shift += 7
                fields.setdefault(field_num, []).append(("varint", val))
            elif wire_type == 2:
                length = 0
                shift = 0
                while True:
                    byte = data[i]
                    i += 1
                    length |= (byte & 0x7F) << shift
                    if not (byte & 0x80):
                        break
                    shift += 7
                sub = data[i:i+length]
                i += length
                fields.setdefault(field_num, []).append(("bytes", sub))
            else:
                break
        return fields

    root = parse_raw(raw)
    legs = []
    for _, leg_bytes in root.get(3, []):
        leg_fields = parse_raw(leg_bytes)
        date_str = leg_fields.get(2, [(None, b"")])[0][1].decode("utf-8", errors="ignore")
        orig_bytes = leg_fields.get(13, [(None, b"")])[0][1]
        orig_code = parse_raw(orig_bytes).get(2, [(None, b"")])[0][1].decode("utf-8", errors="ignore")
        dest_bytes = leg_fields.get(14, [(None, b"")])[0][1]
        dest_code = parse_raw(dest_bytes).get(2, [(None, b"")])[0][1].decode("utf-8", errors="ignore")
        legs.append({"date": date_str, "origin": orig_code, "destination": dest_code})

    passengers = len(root.get(8, []))
    currency = root.get(10, [(None, b"")])[0][1].decode("utf-8", errors="ignore")
    return {
        "trip_type": root.get(2, [(None, 0)])[0][1],
        "legs": legs,
        "passengers": passengers,
        "currency": currency,
    }

def get_search_url() -> str:
    """현재 상수를 반영한 구글 플라이트 실시간 검색 URL 생성."""
    tfs = generate_google_flights_tfs(ORIGIN, DESTINATION, DEPART_DATE, RETURN_DATE, PASSENGERS, "KRW")
    return f"https://www.google.com/travel/flights?tfs={tfs}&hl=ko&gl=kr&curr=KRW"


# ---------------------------------------------------------------------------
# 개별 카드 파싱 & 가격 해석 엔진 (A-1, A-2, S-3, S-4, H-5~H-9)
# ---------------------------------------------------------------------------
def interpret_price(raw_price: int, card_text: str, global_page_text: str = "") -> tuple:
    """
    단일 가격과 텍스트 단서를 바탕으로 1인당 요금을 엄격하게 판정합니다. (S-4, 규칙 2.5 완전 해결)
    반환값: (price_per_person: int | None, reason: str)
    """
    card_has_per_person = bool(re.search(r"(1인당|인당\s*요금|인당|per\s*passenger|/\s*인|per\s*person)", card_text, re.IGNORECASE))
    card_has_total = bool(re.search(r"(총\s*요금|총액|전체\s*요금|합계|total|왕복\s*총)", card_text, re.IGNORECASE))

    page_has_per_person = bool(re.search(r"(1인당|인당\s*요금|per\s*passenger|/\s*인|per\s*person)", global_page_text, re.IGNORECASE))
    page_has_total = bool(re.search(r"(총\s*요금|총액|전체\s*요금|합계|total|성인\s*\d+명\s*총|성인\s*\d+명의\s*필수\s*세금)", global_page_text, re.IGNORECASE))

    # 1. 카드에 직접 명시된 단서 우선
    if card_has_per_person and not card_has_total:
        return (raw_price, "카드 1인당 명시 요금")
    if card_has_total and not card_has_per_person:
        return (round(raw_price / PASSENGERS), f"카드 총 요금 명시 ({PASSENGERS}인 총액 ÷ {PASSENGERS})")
    if card_has_per_person and card_has_total:
        return (None, "카드 내 1인당/총액 단서 충돌로 판정 불가")

    # 2. 카드에 단서가 없을 때 전역 페이지 단서 확인
    if page_has_total and not page_has_per_person:
        return (round(raw_price / PASSENGERS), f"페이지 총 요금 명시 ({PASSENGERS}인 총액 ÷ {PASSENGERS})")
    if page_has_per_person and not page_has_total:
        return (raw_price, "페이지 1인당 명시 요금")
    if page_has_total and page_has_per_person:
        return (None, "페이지 내 1인당/총액 단서 충돌 및 카드 단서 부재로 판정 불가")

    # 3. 단서가 전혀 없는 경우 -> 임의의 휴리스틱 완전 배제 및 안전 탈락 (S-4 완전 해결)
    return (None, "1인당/총액 단서 부재로 판정 불가")


def parse_card_text(card_text: str, global_page_text: str = "") -> dict:
    """
    단일 항공편 카드의 텍스트만 읽어 검증 및 파싱을 수행합니다.
    조건에 미달하거나 모호하면 ValueError 예외를 발생시켜 제외합니다.
    """
    # [H-5 검증] '경유 없음', '0회 경유' 사전 마스킹 후 직항/경유 엄격 판정
    clean_text = re.sub(r"(경유\s*없음|경유지\s*없음|0회\s*경유|0\s*stops?|no\s*stops?)", "[DIRECT_CONFIRMED]", card_text, flags=re.IGNORECASE)
    has_direct = bool(re.search(r"(직항|Nonstop|non-stop|\[DIRECT_CONFIRMED\])", clean_text, re.IGNORECASE))
    has_stop = bool(re.search(r"(\d+회\s*경유|\d+\s*stops?|경유)", clean_text, re.IGNORECASE))

    if has_stop:
        raise ValueError("경유편 포함으로 제외 (1회 이상 경유 확인)")
    if not has_direct:
        raise ValueError("직항 여부 미확인으로 제외")

    # [항공사 식별]
    airline = None
    known_airlines = [
        ("제주항공", "제주항공 (Jeju Air)"),
        ("에어부산", "에어부산 (Air Busan)"),
        ("티웨이", "티웨이항공 (T'way Air)"),
        ("타이거에어", "타이거에어 타이완"),
        ("중화항공", "중화항공 (China Airlines)"),
        ("에바항공", "에바항공 (EVA Air)"),
        ("아시아나", "아시아나항공"),
        ("대한항공", "대한항공"),
        ("진에어", "진에어"),
        ("이스타", "이스타항공"),
        ("에어서울", "에어서울"),
    ]
    for pattern, name in known_airlines:
        if pattern in card_text:
            airline = name
            break
    if not airline:
        match = re.search(r"([가-힣A-Za-z\s]+(?:항공|Air|Airlines))", card_text)
        if match:
            airline = match.group(1).strip()
        else:
            airline = "기타 항공사"

    # [S-3, H-7, H-8 검증] 출발시각 파싱 & 황금시간대(10:00 ~ 15:59)
    time_match = None

    # 범위 패턴 (출발시각 - 도착시각) 우선 탐색
    range_match = re.search(
        r"(?:(?:(오전|오후)\s*)?(\d{1,2}):(\d{2})\s*(AM|PM)?)\s*[-~–]\s*(?:(?:(오전|오후)\s*)?(\d{1,2}):(\d{2})\s*(AM|PM)?)",
        card_text,
        re.IGNORECASE,
    )
    if range_match:
        time_match = (range_match.group(1), range_match.group(2), range_match.group(3), range_match.group(4))
    else:
        # 단일 한국어 포맷 (오전/오후 HH:MM)
        kr_match = re.search(r"(오전|오후)\s*(\d{1,2}):(\d{2})", card_text)
        if kr_match:
            time_match = (kr_match.group(1), kr_match.group(2), kr_match.group(3), None)
        else:
            # 단일 영문 포맷 (HH:MM AM/PM)
            en_match = re.search(r"(\d{1,2}):(\d{2})\s*(AM|PM)", card_text, re.IGNORECASE)
            if en_match:
                time_match = (None, en_match.group(1), en_match.group(2), en_match.group(3))
            else:
                # 소요시간(소요/시간/분)이 뒤따르지 않는 단순 24시제 포맷
                raw_match = re.search(r"(\d{1,2}):(\d{2})(?!\s*(?:소요|시간|분|h|m|hours|mins))", card_text)
                if raw_match:
                    time_match = (None, raw_match.group(1), raw_match.group(2), None)

    # [S-3 Fail-Closed] 출발 시각을 못 찾으면 무조건 제외
    if not time_match:
        raise ValueError("출발 시각을 식별할 수 없어 황금시간대 검증 불가로 제외")

    ampm_kr, h_str, m_str, ampm_en = time_match
    hour = int(h_str)

    if ampm_kr == "오후" and hour < 12:
        hour += 12
    elif ampm_kr == "오전" and hour == 12:
        hour = 0
    elif ampm_en and ampm_en.upper() == "PM" and hour < 12:
        hour += 12
    elif ampm_en and ampm_en.upper() == "AM" and hour == 12:
        hour = 0

    if not (10 <= hour <= 15):
        raise ValueError(f"황금시간대(10~15시) 이탈로 제외 (출발시각: {h_str}:{m_str})")

    # [회귀 ② 방어 및 정밀 가격 파싱]
    price_matches = re.finditer(
        r"(?:(수수료|세금|추가|할인|좌석지정)\s*)?₩\s*([\d,]+)|(?:(수수료|세금|추가|할인|좌석지정)\s*)?([\d,]+)\s*원",
        card_text,
    )
    candidate_prices = []
    for m in price_matches:
        is_fee = bool(m.group(1) or m.group(3))
        val_str = (m.group(2) or m.group(4)).replace(",", "")
        val = int(val_str)
        if 50000 <= val <= 10000000 and not is_fee:
            candidate_prices.append(val)

    candidate_prices = sorted(list(set(candidate_prices)))

    if not candidate_prices:
        raise ValueError("유효한 가격 정보를 찾을 수 없어 제외")

    # 카드 내 2개 이상의 가격이 있을 때 관계식 검증
    if len(candidate_prices) >= 2:
        p_min, p_max = candidate_prices[0], candidate_prices[-1]
        # p_max가 p_min * 3과 일치하는 경우 (1인당/총액 쌍)
        if abs(p_max - (p_min * PASSENGERS)) <= 600:
            price_per_person = p_min
            price_total = p_max
            price_reason = f"카드 내 1인당/총액 쌍 식별 ({p_min:,}원 / {p_max:,}원)"
            return {
                "airline": airline,
                "is_direct": True,
                "raw_price": p_max,
                "raw_price_str": f"{p_max:,}원",
                "price_per_person": price_per_person,
                "price_total": price_total,
                "price_reason": price_reason,
            }
        else:
            raise ValueError(f"카드 내 다중 가격({candidate_prices}) 식별 불가로 제외")

    # 단일 가격 후보인 경우 interpret_price 호출
    chosen_price = candidate_prices[0]
    price_per_person, price_reason = interpret_price(chosen_price, card_text, global_page_text)
    if price_per_person is None:
        raise ValueError(f"가격 판정 모호함으로 제외 ({price_reason}, 원본: {chosen_price:,}원)")

    return {
        "airline": airline,
        "is_direct": True,
        "raw_price": chosen_price,
        "raw_price_str": f"{chosen_price:,}원",
        "price_per_person": price_per_person,
        "price_total": price_per_person * PASSENGERS,
        "price_reason": price_reason,
    }


# ---------------------------------------------------------------------------
# Playwright 실시간 크롤링 엔진 (M-10, M-11, M-14, M-15, M-20)
# ---------------------------------------------------------------------------
def scrape_live_flights(url: str, dump_cards_file: str = None) -> tuple:
    """
    Playwright를 구동하여 개별 카드 단위로 구글 플라이트 실시간 데이터를 파싱합니다.
    반환값: (crawled_flights: list, total_cards_count: int, rejection_logs: list)
    """
    print(f"[INFO] 🌐 구글 플라이트 실시간 크롤링 시작: {ORIGIN} ↔ {DESTINATION} ({DEPART_DATE} ~ {RETURN_DATE})")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError("Playwright 패키지가 설치되지 않았습니다.")

    crawled_flights = []
    rejection_logs = []
    total_cards_count = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            locale="ko-KR",
            timezone_id="Asia/Seoul",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=45000)

            # [M-20 동의창 처리] '동의하지 않음'은 피하고 '동의/수락'만 클릭
            consent_buttons = page.query_selector_all(
                "button:has-text('모두 수락'), button:has-text('모두 동의'), button:has-text('Accept all'), button:has-text('I agree')"
            )
            for btn in consent_buttons:
                try:
                    if btn.is_visible():
                        btn.click()
                        time.sleep(1)
                        break
                except Exception:
                    pass

            # [M-15 동적 대기] 본문에 유효한 가격 정규식 패턴이 렌더링될 때까지 대기
            try:
                page.wait_for_function(
                    "() => /₩\\s*[\\d,]{4,}|[\\d,]{2,}\\s*000\\s*원/.test(document.body.innerText)",
                    timeout=20000
                )
            except Exception:
                body_snippet = page.inner_text("body")[:300].replace("\n", " ")
                raise RuntimeError(f"가격 렌더링 타임아웃 (화면 텍스트 요약: {body_snippet})")

            # [M-14 검증 가드] 출발지(부산/PUS), 도착지(가오슝/KHH), 날짜(2027-02-24 / 2월 24일) 확인
            body_text = page.inner_text("body")
            has_origin = ("부산" in body_text) or ("PUS" in body_text)
            has_dest = ("가오슝" in body_text) or ("KHH" in body_text)
            has_date = (DEPART_DATE in body_text) or ("2027. 2. 24" in body_text) or ("2월 24일" in body_text) or ("Feb 24" in body_text)

            if not (has_origin and has_dest and has_date):
                raise RuntimeError("검색 조건 미적용: 출발지/도착지/날짜가 페이지 본문에서 확인되지 않음")

            # 개별 카드 격리 쿼리
            cards = page.query_selector_all("ul[role='list'] > li, li.pIav2d, div[role='listitem']")
            if len(cards) < 2:
                cards = page.query_selector_all("ul.RLLof > li, ul li")

            total_cards_count = len(cards)
            print(f"[INFO] 발견된 카드 후보 요소: {total_cards_count}개")

            # M-19: 실물 덤프 옵션 처리
            if dump_cards_file:
                dump_data = {
                    "url": url,
                    "body_text": body_text,
                    "cards": [c.inner_text().strip() for c in cards]
                }
                with open(dump_cards_file, "w", encoding="utf-8") as f:
                    json.dump(dump_data, f, ensure_ascii=False, indent=2)
                print(f"[INFO] 💾 실물 카드 덤프 저장 완료: {dump_cards_file}")

            for card in cards:
                try:
                    card_text = card.inner_text().strip()
                    if len(card_text) > 2000 or len(card_text) < 10:
                        continue
                    if not ("₩" in card_text or "원" in card_text):
                        continue

                    parsed = parse_card_text(card_text, body_text)

                    # 중복 방지
                    if not any(f["airline"] == parsed["airline"] and f["price_per_person"] == parsed["price_per_person"] for f in crawled_flights):
                        crawled_flights.append(parsed)
                        print(f"  • [통과] {parsed['airline']}: 1인 {parsed['price_per_person']:,}원 (원본: {parsed['raw_price_str']}, 사유: {parsed['price_reason']})")
                except ValueError as ve:
                    rejection_logs.append(str(ve))
                    print(f"  • [카드 제외] {ve}")
                except Exception as ce:
                    rejection_logs.append(f"파싱 에러: {ce}")
                    print(f"  • [카드 파싱 에러] {ce}")

        finally:
            browser.close()

    crawled_flights.sort(key=lambda x: x["price_per_person"])
    return crawled_flights, total_cards_count, rejection_logs


# ---------------------------------------------------------------------------
# 상태 저장소 관리 (B-2, S-2, M-18)
# ---------------------------------------------------------------------------
def load_state() -> dict:
    """state.json을 안전하게 로드합니다."""
    default_state = {
        "version": 1,
        "last_updated": None,
        "consecutive_failures": 0,
        "last_outage_alert_ts": None,
        "last_alert_price_pp": BENCHMARK_PRICE_PER_PERSON,
        "last_alert_ts": None,
        "history": [],
    }
    if not os.path.exists(STATE_FILE):
        return default_state

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for k, v in default_state.items():
                data.setdefault(k, v)
            return data
    except Exception as e:
        print(f"[WARN] state.json 로드 실패, 초기화: {e}")
        return default_state

def save_state(state: dict, dry_run: bool = False):
    """state.json을 저장합니다 (dry_run일 때는 파일 쓰기 금지)."""
    if dry_run:
        return
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERROR] state.json 저장 실패: {e}")

def record_observation(state: dict, best_flight: dict, dry_run: bool = False):
    """관측 성공 이력 기록 및 연속 실패 카운트 리셋."""
    now_iso = datetime.datetime.now(KST).isoformat()
    state["last_updated"] = now_iso
    state["consecutive_failures"] = 0

    state["history"].append({
        "ts": now_iso,
        "price_pp": best_flight["price_per_person"],
        "airline": best_flight["airline"],
        "raw_price": best_flight["raw_price"],
        "price_reason": best_flight["price_reason"],
    })

    cutoff = (datetime.datetime.now(KST) - datetime.timedelta(days=30)).isoformat()
    state["history"] = [h for h in state["history"] if h.get("ts", "") >= cutoff]
    save_state(state, dry_run=dry_run)

def record_failure(state: dict, error_msg: str, dry_run: bool = False) -> bool:
    """실패 기록 및 2회 연속 실패 시 장애 알림 필요 여부 판정."""
    state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
    now = datetime.datetime.now(KST)
    state["last_updated"] = now.isoformat()
    should_alert = False

    if state["consecutive_failures"] >= 2:
        last_alert_str = state.get("last_outage_alert_ts")
        if not last_alert_str:
            should_alert = True
        else:
            try:
                last_alert_dt = datetime.datetime.fromisoformat(last_alert_str)
                if (now - last_alert_dt).total_seconds() >= 86400:
                    should_alert = True
            except Exception:
                should_alert = True

    if should_alert and not dry_run:
        state["last_outage_alert_ts"] = now.isoformat()

    save_state(state, dry_run=dry_run)
    return should_alert

def get_weekly_stats(state: dict) -> dict:
    """최근 7일간의 실측치 통계(최저/평균/최고/관측횟수)를 계산합니다."""
    history = state.get("history", [])
    if not history:
        return None

    cutoff = (datetime.datetime.now(KST) - datetime.timedelta(days=7)).isoformat()
    recent = [h for h in history if h.get("ts", "") >= cutoff and "price_pp" in h]

    if not recent:
        return None

    prices = [r["price_pp"] for r in recent]
    return {
        "min": min(prices),
        "max": max(prices),
        "avg": round(sum(prices) / len(prices)),
        "count": len(recent),
    }


# ---------------------------------------------------------------------------
# 텔레그램 발송 엔진 (C-1)
# ---------------------------------------------------------------------------
def send_telegram(text: str, dry_run: bool = False) -> bool:
    """HTML 모드로 텔레그램 메시지를 안전하게 발송합니다."""
    if dry_run:
        print("\n[DRY-RUN 텔레그램 출력]")
        print(text)
        return True

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[WARN] 텔레그램 토큰 또는 Chat ID 미설정")
        return False

    if len(text) > 4000:
        lines = text.split("\n")
        truncated = []
        cur_len = 0
        for line in lines:
            if cur_len + len(line) + 1 > 3800:
                truncated.append("... [내용 일부 생략]")
                break
            truncated.append(line)
            cur_len += len(line) + 1
        text = "\n".join(truncated)

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    def _post(payload_dict: dict) -> bool:
        data = json.dumps(payload_dict).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                ok = json.loads(resp.read().decode("utf-8")).get("ok")
                return bool(ok)
        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8", errors="replace")
            print(f"[ERROR] 텔레그램 HTTP {he.code}: {err_body}")
            if he.code == 400 and payload_dict.get("parse_mode") == "HTML":
                print("[INFO] HTML 서식 제거 후 평문으로 1회 재시도합니다.")
                plain_text = re.sub(r"<[^>]+>", "", payload_dict["text"])
                return _post({"chat_id": TELEGRAM_CHAT_ID, "text": plain_text, "disable_web_page_preview": True})
            return False
        except Exception as e:
            print(f"[ERROR] 텔레그램 통신 에러: {e}")
            return False

    success = _post({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    })
    if success:
        print("[INFO] 텔레그램 전송 성공!")
    return success


# ---------------------------------------------------------------------------
# 메시지 서식 헬퍼
# ---------------------------------------------------------------------------
def get_deadline_msg(days_left: int) -> str:
    if days_left > 0:
        return f"<b>무료 취소 마감일:</b> {FREE_CANCEL_DEADLINE} (D-{days_left}일 남음 - 취소 수수료 0원)"
    elif days_left == 0:
        return f"<b>무료 취소 마감일:</b> 오늘({FREE_CANCEL_DEADLINE})이 수수료 없는 무료 취소 마지막 날입니다!"
    else:
        return f"<b>무료 취소 마감일 경과:</b> {FREE_CANCEL_DEADLINE} (현재 취소 시 항공사/여행사 규정에 따라 취소 위약금이 발생할 수 있습니다)"

def get_cancellation_guide(days_left: int) -> str:
    if days_left >= 0:
        return "새 특가 항공권을 먼저 예매 완료한 후, 기존 제주항공 티켓을 무료 취소하세요."
    else:
        return "새 특가로 절감되는 금액과 기존 티켓 취소 위약금을 반드시 비교한 후 변경을 결정하세요."

def mask_error_reason(err_str: str) -> str:
    first_line = err_str.strip().split("\n")[0]
    first_line = re.sub(r"https?://[^\s]+", "[URL_MASKED]", first_line)
    first_line = re.sub(r"Call log:.*", "", first_line)
    return first_line[:200]


# ---------------------------------------------------------------------------
# 메인 실행 로직 (S-1, S-2, M-10, M-12, M-18, 0건 브리핑 지원)
# ---------------------------------------------------------------------------
def run_tracker(dry_run: bool = False, force_notify: bool = False, dump_cards_file: str = None):
    kst_now = datetime.datetime.now(KST)
    today = kst_now.date()
    days_left = (FREE_CANCEL_DEADLINE - today).days
    now_str = kst_now.strftime("%Y-%m-%d %H:%M KST")

    state = load_state()
    search_url = get_search_url()

    # 1. 크롤링 실행 (M-10)
    try:
        flights, total_cards, rejections = scrape_live_flights(search_url, dump_cards_file=dump_cards_file)
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] 크롤링 실패 (장애 발생): {error_msg}")
        should_alert = record_failure(state, error_msg, dry_run=dry_run)

        if should_alert:
            masked_reason = mask_error_reason(error_msg)
            outage_text = "\n".join([
                "⚠️ <b>[점검 필요] 대만 항공권 모니터링 봇 크롤링 연속 실패</b>",
                "",
                f"• <b>연속 실패 횟수:</b> {state['consecutive_failures']}회",
                f"• <b>발생 일시:</b> {now_str}",
                f"• <b>실패 사유:</b> <code>{html.escape(masked_reason)}</code>",
                "",
                "🔍 깃허브 액션 로그 또는 구글 플라이트 페이지 구조 변경 여부를 점검해 주세요.",
            ])
            send_telegram(outage_text, dry_run=dry_run)

        if not dry_run:
            sys.exit(1)
        return

    is_sunday = today.weekday() == 6
    is_sunday_briefing = is_sunday and (kst_now.hour < 14)

    # 2. 카드는 찾았으나 조건 맞는 항공편이 0건인 경우
    if not flights and total_cards > 0:
        print(f"[INFO] 카드 {total_cards}개 발견되었으나 직항/황금시간대 조건 만족 항공편 없음 (정상 대기)")
        state["consecutive_failures"] = 0
        save_state(state, dry_run=dry_run)

        # 0건이어도 일요일 브리핑 또는 강제 발송 시 누락 없이 브리핑 발송 (주간 최저가 비교 및 상위 탈락사유 요약 노출)
        if is_sunday_briefing or force_notify:
            stats = get_weekly_stats(state)
            if stats:
                stats_block = "\n".join([
                    f"📈 <b>최근 7일간 실측 통계 (총 {stats['count']}회 관측):</b>",
                    f"• <b>주간 최저가:</b> 1인 {stats['min']:,}원",
                    f"• <b>주간 평균가:</b> 1인 {stats['avg']:,}원",
                    f"• <b>주간 최고가:</b> 1인 {stats['max']:,}원",
                ])
            else:
                stats_block = "📈 <b>최근 7일간 실측 통계:</b> 최근 관측 데이터 없음"

            # 탈락 사유 상위 요약 추출
            rejection_summary_str = ""
            if rejections:
                counts = Counter(rejections)
                top_reasons = [f"{reason.split('(')[0].strip()} {cnt}건" for reason, cnt in counts.most_common(2)]
                rejection_summary_str = f" (주요 제외: {', '.join(top_reasons)})"

            if stats and stats["min"] < BENCHMARK_PRICE_PER_PERSON:
                report_summary = "\n".join([
                    f"• 이번 주 관측 중 한때 1인 {stats['min']:,}원의 특가가 포착된 적이 있으나, 현재 시점에는 조건을 만족하는 유효 직항이 마감/소진되었습니다.",
                    f"• 현재 확보해 두신 제주항공 티켓({BENCHMARK_PRICE_PER_PERSON:,}원)을 안전하게 유지하시는 것이 좋습니다.",
                ])
            else:
                report_summary = "\n".join([
                    "• 이번 주는 직항 및 황금시간대(10~15시) 조건을 만족하는 유효 항공편이 확인되지 않았습니다.",
                    f"• 기존에 확보하신 제주항공 티켓({BENCHMARK_PRICE_PER_PERSON:,}원)이 유일한 최적 대안입니다.",
                ])

            briefing_text = "\n".join([
                "📊 <b>[대만 항공권] 주간 정기 모니터링 브리핑</b>",
                f"📅 <b>여정:</b> {ORIGIN}(부산) ↔ {DESTINATION}(가오슝) [3박 4일, 3인 직항]",
                f"🗓️ <b>일정:</b> {DEPART_DATE}(수) ~ {RETURN_DATE}(토)",
                f"🕒 <b>브리핑 일시:</b> {now_str}",
                "",
                "━━━━━━━━━━━━━━━━━━",
                f"🏷️ <b>현재 내 예매가:</b> 1인 <b>{BENCHMARK_PRICE_PER_PERSON:,}원</b> (3인 {BENCHMARK_PRICE_TOTAL:,}원)",
                f"🔍 <b>현재 실시간 최저가:</b> 조건 만족 편 없음 (총 {total_cards}개 중 0건 통과){html.escape(rejection_summary_str)}",
                "━━━━━━━━━━━━━━━━━━",
                "",
                f"{stats_block}",
                "",
                "✅ <b>주간 종합 리포트:</b>",
                f"{report_summary}",
                "",
                f"⏰ {get_deadline_msg(days_left)}",
                f'🔗 <a href="{html.escape(search_url)}">구글 플라이트 실시간 확인</a>',
                "",
                "⚠️ <i>[주의] 수하물 15kg 및 귀국편 세부 규정은 예매 전 항공사 사이트에서 직접 확인 필요</i>",
            ])
            print("\n[INFO] 일요일 0건 정기 브리핑 발송")
            send_telegram(briefing_text, dry_run=dry_run)
        return

    best = flights[0]
    best_price = best["price_per_person"]
    best_total = best["price_total"]

    record_observation(state, best, dry_run=dry_run)

    # [S-2 개선] last_alert_price_pp 만료(7일) 및 반등 리셋
    last_alert_price = state.get("last_alert_price_pp", BENCHMARK_PRICE_PER_PERSON)
    last_alert_ts_str = state.get("last_alert_ts")

    if last_alert_ts_str:
        try:
            last_alert_dt = datetime.datetime.fromisoformat(last_alert_ts_str)
            if (kst_now - last_alert_dt).total_seconds() > 7 * 86400:
                last_alert_price = BENCHMARK_PRICE_PER_PERSON
        except Exception:
            last_alert_price = BENCHMARK_PRICE_PER_PERSON

    if best_price >= BENCHMARK_PRICE_PER_PERSON:
        state["last_alert_price_pp"] = BENCHMARK_PRICE_PER_PERSON
        state["last_alert_ts"] = None
        last_alert_price = BENCHMARK_PRICE_PER_PERSON
        save_state(state, dry_run=dry_run)

    savings_pp = BENCHMARK_PRICE_PER_PERSON - best_price
    savings_total = BENCHMARK_PRICE_TOTAL - best_total
    savings_vs_last_alert = last_alert_price - best_price

    # 새 특가 판정
    is_new_deal = (savings_pp >= MIN_SAVINGS) and (savings_vs_last_alert >= MIN_SAVINGS)

    # -----------------------------------------------------------------------
    # Case 1: 새로운 특가 포착 시 ➔ 즉시 긴급 알림 🚨
    # -----------------------------------------------------------------------
    if is_new_deal:
        deal_text = "\n".join([
            "🚨 <b>[특가 포착!] 대만 가오슝 더 싼 항공권 발견!</b> 🚨",
            f"📅 <b>여정:</b> {ORIGIN}(부산) ↔ {DESTINATION}(가오슝) [3박 4일, 3인 직항]",
            f"🗓️ <b>일정:</b> {DEPART_DATE}(수) ~ {RETURN_DATE}(토)",
            f"🕒 <b>포착 일시:</b> {now_str}",
            "",
            "━━━━━━━━━━━━━━━━━━",
            f"🏷️ <b>기존 예매가:</b> 1인 {BENCHMARK_PRICE_PER_PERSON:,}원 (3인 {BENCHMARK_PRICE_TOTAL:,}원)",
            f"🔥 <b>신규 특가가:</b> 1인 <b>{best_price:,}원</b> (3인 <b>{best_total:,}원</b>)",
            f"💰 <b>절감 금액:</b> 1인당 <b>{savings_pp:,}원</b> 절약 (3인 총 <b>{savings_total:,}원</b> 세이브!)",
            f"✈️ <b>최저가 항공사:</b> <b>{html.escape(best['airline'])}</b>",
            f"📊 <b>가격 판정 근거:</b> {html.escape(best['price_reason'])} (화면 표시: {html.escape(best['raw_price_str'])})",
            "━━━━━━━━━━━━━━━━━━",
            "",
            "👉 <b>액션 가이드:</b>",
            f"1. {get_cancellation_guide(days_left)}",
            "",
            f"⏰ {get_deadline_msg(days_left)}",
            f'🔗 <a href="{html.escape(search_url)}">구글 플라이트 실시간 확인 및 예매</a>',
            "",
            "⚠️ <i>[주의] 수하물 15kg 및 귀국편 세부 규정은 예매 전 항공사 사이트에서 직접 확인 필요</i>",
        ])
        print("\n[ALERT] 새로운 유효 특가 포착! 텔레그램 발송")
        send_telegram(deal_text, dry_run=dry_run)
        state["last_alert_price_pp"] = best_price
        state["last_alert_ts"] = kst_now.isoformat()
        save_state(state, dry_run=dry_run)
        return

    # -----------------------------------------------------------------------
    # Case 2: 일요일 정기 브리핑 또는 강제 발송 (S-1 판정 축 일치화 리포트) 📊
    # -----------------------------------------------------------------------
    if is_sunday_briefing or force_notify:
        stats = get_weekly_stats(state)
        week_min = stats["min"] if stats else best_price

        if stats:
            stats_block = "\n".join([
                f"📈 <b>최근 7일간 실측 통계 (총 {stats['count']}회 관측):</b>",
                f"• <b>주간 최저가:</b> 1인 {stats['min']:,}원",
                f"• <b>주간 평균가:</b> 1인 {stats['avg']:,}원",
                f"• <b>주간 최고가:</b> 1인 {stats['max']:,}원",
            ])
        else:
            stats_block = "📈 <b>최근 7일간 실측 통계:</b> 최근 관측 데이터 없음"

        # [S-1 수정] 실측 통계(week_min)와 현재 최저가(best_price)를 종합 비교
        if best_price < BENCHMARK_PRICE_PER_PERSON:
            report_summary = "\n".join([
                f"• 현재 실시간 최저가(1인 {best_price:,}원, {html.escape(best['airline'])})는 기존 예매가({BENCHMARK_PRICE_PER_PERSON:,}원)보다 {BENCHMARK_PRICE_PER_PERSON - best_price:,}원 저렴한 상태를 유지하고 있습니다.",
                "• 직전 알림가와 동일/유사 범위 내에 있어 추가 긴급 알림 대신 정기 주간 리포트로 현황을 보고합니다.",
            ])
        elif week_min < BENCHMARK_PRICE_PER_PERSON:
            report_summary = "\n".join([
                f"• 이번 주 관측 중 한때 1인 {week_min:,}원의 특가가 포착되었으나, 현재 시점 최저가는 1인 {best_price:,}원으로 기존 예매가({BENCHMARK_PRICE_PER_PERSON:,}원) 수준으로 복귀했습니다.",
                "• 현재 예매해 두신 제주항공 티켓을 안전하게 유지하시는 것이 좋습니다.",
            ])
        else:
            report_summary = "\n".join([
                f"• 지난 1주일간 실측 최저가(1인 {week_min:,}원)를 포함하여 기존 예매가({BENCHMARK_PRICE_PER_PERSON:,}원)보다 저렴한 신규 특가는 나오지 않았습니다.",
                "• 현재 예매해 두신 제주항공 티켓이 최저가를 안전하게 유지 중입니다.",
            ])

        briefing_text = "\n".join([
            "📊 <b>[대만 항공권] 주간 정기 모니터링 브리핑</b>",
            f"📅 <b>여정:</b> {ORIGIN}(부산) ↔ {DESTINATION}(가오슝) [3박 4일, 3인 직항]",
            f"🗓️ <b>일정:</b> {DEPART_DATE}(수) ~ {RETURN_DATE}(토)",
            f"🕒 <b>브리핑 일시:</b> {now_str}",
            "",
            "━━━━━━━━━━━━━━━━━━",
            f"🏷️ <b>현재 내 예매가:</b> 1인 <b>{BENCHMARK_PRICE_PER_PERSON:,}원</b> (3인 {BENCHMARK_PRICE_TOTAL:,}원)",
            f"🔍 <b>현재 실시간 최저가:</b> <b>{html.escape(best['airline'])}</b> (1인 {best_price:,}원, {html.escape(best['price_reason'])})",
            "━━━━━━━━━━━━━━━━━━",
            "",
            f"{stats_block}",
            "",
            "✅ <b>주간 종합 리포트:</b>",
            f"{report_summary}",
            "",
            f"⏰ {get_deadline_msg(days_left)}",
            f'🔗 <a href="{html.escape(search_url)}">구글 플라이트 실시간 확인</a>',
            "",
            "⚠️ <i>[주의] 수하물 15kg 및 귀국편 세부 규정은 예매 전 항공사 사이트에서 직접 확인 필요</i>",
        ])
        print("\n[INFO] 일요일 주간 정기 브리핑 발송")
        send_telegram(briefing_text, dry_run=dry_run)
        return

    # -----------------------------------------------------------------------
    # Case 3: 평시 특가 부재 시 ➔ 무소음 모드
    # -----------------------------------------------------------------------
    print(
        f"[INFO] 🔇 무소음 모드: 실시간 최저가({best_price:,}원, {best['price_reason']}) >= "
        f"기존 예매가({BENCHMARK_PRICE_PER_PERSON:,}원)\n"
        f"[INFO] 불필요한 알림 없이 조용히 대기합니다."
    )


# ---------------------------------------------------------------------------
# 자체 검증 스위트 (--self-test) (20대 테스트 전수 검증)
# ---------------------------------------------------------------------------
def run_self_tests() -> bool:
    """실물 픽스처 및 적대적 입력을 포함한 20대 단위 테스트를 전수 검증합니다."""
    print("==================================================")
    print("🧪 [Self-Test] 항공권 봇 정밀 단위 테스트 스위트 (20 Tests)")
    print("==================================================")
    all_passed = True

    # 1. 1회 경유가 적힌 카드는 결과에 포함되지 않는다
    f1 = "제주항공\n오후 2:05 - 오후 4:05\n1회 경유\n₩1,591,800"
    try:
        parse_card_text(f1)
        print("❌ [Test 1 FAILED] 1회 경유 카드가 제외되지 않음")
        all_passed = False
    except ValueError as e:
        if "경유" in str(e):
            print("✅ [Test 1 PASSED] 1회 경유 카드 정상 제외됨")
        else:
            print(f"❌ [Test 1 FAILED] 예외 사유 불일치: {e}")
            all_passed = False

    # 2. 실물 구글 플라이트 제주항공 카드 (M-19 실물 픽스처)
    real_card_jeju = "오후 2:052월 24일 (수), 오후 2:05 – 오후 4:052월 24일 (수), 오후 4:05제주항공3시간PUS김해국제공항–KHH가오슝 국제공항직항CO2e 420kg평균 배출량평균 배출량₩1,420,800왕복출발2월 24일 (수)CO2e 420kg평균 배출량평균 배출량항공편 선택₩1,420,800왕복오후 2:05PUS오후 4:05KHH₩1,420,800왕복직항직항3시간제주항공CO2e 420kg평균 배출량평균 배출량"
    real_page = "가격 및 편의성을 기준으로 한 순위가격에는 성인 3명의 필수 세금과 수수료가 포함됩니다."
    try:
        r_jeju = parse_card_text(real_card_jeju, real_page)
        assert r_jeju["airline"] == "제주항공 (Jeju Air)" and r_jeju["price_per_person"] == 473600
        print("✅ [Test 2 PASSED] [M-19 실물] 실제 구글 플라이트 제주항공 카드 정상 통과 (1인 473,600원)")
    except Exception as e:
        print(f"❌ [Test 2 FAILED] 실물 제주항공 카드 파싱 실패: {e}")
        all_passed = False

    # 3. 실물 구글 플라이트 에어부산 카드 (M-19 실물 픽스처)
    real_card_busan = "오후 12:002월 24일 (수), 오후 12:00 – 오후 2:002월 24일 (수), 오후 2:00에어부산3시간PUS김해국제공항–KHH가오슝 국제공항직항CO2e 437kg평균 배출량평균 배출량₩1,537,500왕복출발2월 24일 (수)CO2e 437kg평균 배출량평균 배출량항공편 선택₩1,537,500왕복오후 12:00PUS오후 2:00KHH₩1,537,500왕복직항직항3시간에어부산CO2e 437kg평균 배출량평균 배출량"
    try:
        r_busan = parse_card_text(real_card_busan, real_page)
        assert r_busan["airline"] == "에어부산 (Air Busan)" and r_busan["price_per_person"] == 512500
        print("✅ [Test 3 PASSED] [M-19 실물] 실제 구글 플라이트 에어부산 카드 정상 통과 (1인 512,500원)")
    except Exception as e:
        print(f"❌ [Test 3 FAILED] 실물 에어부산 카드 파싱 실패: {e}")
        all_passed = False

    # 4. 오전 6:05 출발 카드는 황금시간대 탈락으로 제외된다
    f4 = "티웨이항공\n오전 6:05 - 오전 8:05\n직항 2시간\n총 요금 ₩1,200,000"
    try:
        parse_card_text(f4)
        print("❌ [Test 4 FAILED] 오전 6:05 카드가 제외되지 않음")
        all_passed = False
    except ValueError as e:
        if "황금시간대" in str(e):
            print("✅ [Test 4 PASSED] 오전 6:05 출발 황금시간대(10~15시) 이탈 정상 제외됨")
        else:
            print(f"❌ [Test 4 FAILED] 예외 사유 불일치: {e}")
            all_passed = False

    # 5. 1인당 문구가 있는 표시가는 3으로 나누지 않는다
    f5 = "제주항공\n오후 2:05 - 오후 4:05\n직항\n1인당 요금 ₩473,700"
    try:
        r5 = parse_card_text(f5)
        assert r5["price_per_person"] == 473700, f"Expected 473700, got {r5['price_per_person']}"
        print("✅ [Test 5 PASSED] 1인당 명시 요금(473,700원) 3으로 나누지 않고 보존")
    except Exception as e:
        print(f"❌ [Test 5 FAILED] 1인당 명시 요금 해석 실패: {e}")
        all_passed = False

    # 6. 총액/1인당 판정이 모호한 금액은 채택하지 않는다
    f6 = "미식별항공\n오후 1:00\n직항\n₩450,000"
    try:
        parse_card_text(f6)
        print("❌ [Test 6 FAILED] 모호한 금액이 채택됨")
        all_passed = False
    except ValueError as e:
        if "단서 부재" in str(e) or "모호" in str(e):
            print("✅ [Test 6 PASSED] 판정 모호한 금액(450,000원, 단서 없음) 정상 제외됨")
        else:
            print(f"❌ [Test 6 FAILED] 예외 사유 불일치: {e}")
            all_passed = False

    # 7. 하한 아래(30만원 미만) 가격도 정상 인식된다
    f7 = "제주항공\n오후 2:05\n직항\n1인당 ₩250,000"
    try:
        r7 = parse_card_text(f7)
        assert r7["price_per_person"] == 250000
        print("✅ [Test 7 PASSED] 30만원 미만 특가(1인당 250,000원) 정상 인식")
    except Exception as e:
        print(f"❌ [Test 7 FAILED] 30만원 미만 특가 인식 실패: {e}")
        all_passed = False

    # 8. 생성한 tfs를 다시 디코드하면 날짜·공항 코드·성인 3명이 들어 있다
    try:
        tfs = generate_google_flights_tfs("PUS", "KHH", "2027-02-24", "2027-02-27", 3, "KRW")
        dec = decode_google_flights_tfs(tfs)
        assert dec["passengers"] == 3
        assert dec["legs"][0]["origin"] == "PUS" and dec["legs"][0]["destination"] == "KHH" and dec["legs"][0]["date"] == "2027-02-24"
        assert dec["legs"][1]["origin"] == "KHH" and dec["legs"][1]["destination"] == "PUS" and dec["legs"][1]["date"] == "2027-02-27"
        print("✅ [Test 8 PASSED] tfs Protobuf 날짜·공항코드·3인 검증 완료")
    except Exception as e:
        print(f"❌ [Test 8 FAILED] TFS Protobuf 인코딩/디코딩 실패: {e}")
        all_passed = False

    # 9. 항공사명에 <, & 가 있어도 HTML 이스케이프되어 들어간다
    try:
        raw_airline = "제주항공 & <특가Air>"
        escaped = html.escape(raw_airline)
        assert escaped == "제주항공 &amp; &lt;특가Air&gt;"
        assert "<" not in escaped and ">" not in escaped and "& " not in escaped
        print("✅ [Test 9 PASSED] HTML 특수문자(<, &) 이스케이프 검증 완료")
    except Exception as e:
        print(f"❌ [Test 9 FAILED] HTML 이스케이프 실패: {e}")
        all_passed = False

    # 10 [Case A]. 출발 시각 없는 직항 카드 -> Fail-Closed 제외 (S-3)
    f_a = "제주항공\n직항\n총 요금 ₩1,200,000"
    try:
        parse_card_text(f_a)
        print("❌ [Test 10 FAILED] 출발 시각 없는 카드가 통과됨 (Fail-Open 버그)")
        all_passed = False
    except ValueError as e:
        if "시각" in str(e):
            print("✅ [Test 10 PASSED] [Case A] 출발 시각 없는 직항 카드 Fail-Closed 정상 제외됨")
        else:
            print(f"❌ [Test 10 FAILED] 예외 사유 불일치: {e}")
            all_passed = False

    # 11 [Case B]. '직항 / 경유 없음' 카드 -> 정상 통과 (H-5)
    f_b = "제주항공\n오후 2:05 - 오후 4:05\n직항 / 경유 없음\n총 요금 ₩1,421,100"
    try:
        r_b = parse_card_text(f_b)
        assert r_b["is_direct"] and r_b["price_per_person"] == 473700
        print("✅ [Test 11 PASSED] [Case B] '직항 / 경유 없음' 카드 오탐 없이 정상 통과")
    except Exception as e:
        print(f"❌ [Test 11 FAILED] [Case B] '경유 없음' 오탐 발생: {e}")
        all_passed = False

    # 12 [Case C]. '1인당' 문구 없는 ₩1,200,000 + 페이지에 1인당 명시 있을 때 -> 1,200,000원으로 정확 판정 (H-9)
    f_c = "대한항공\n오후 2:05 - 오후 4:05\n직항\n₩1,200,000"
    page_c = "표시된 가격은 1인당 요금입니다."
    try:
        r_c = parse_card_text(f_c, global_page_text=page_c)
        assert r_c["price_per_person"] == 1200000, f"Expected 1200000, got {r_c['price_per_person']}"
        assert "페이지 1인당 명시 요금" in r_c["price_reason"]
        print("✅ [Test 12 PASSED] [Case C] 페이지 1인당 단서 반영하여 1인당 1,200,000원 정확 판정")
    except Exception as e:
        print(f"❌ [Test 12 FAILED] [Case C] 1인당 전역 단서 해석 실패: {e}")
        all_passed = False

    # 13 [Case D]. 페이지 하단 "성인 3명 총 요금" + 카드에 단서 없는 ₩1,421,100 -> 473,700원 계산 (H-9)
    f_d = "제주항공\n오후 2:05 - 오후 4:05\n직항\n₩1,421,100"
    page_d = "성인 3명의 필수 세금과 수수료가 포함됩니다."
    try:
        r_d = parse_card_text(f_d, global_page_text=page_d)
        assert r_d["price_per_person"] == 473700
        print("✅ [Test 13 PASSED] [Case D] 페이지 전역 총액 단서 기반 473,700원 정확 계산")
    except Exception as e:
        print(f"❌ [Test 13 FAILED] [Case D] 전역 총액 단서 해석 실패: {e}")
        all_passed = False

    # 14 [Case E]. "비즈니스 ₩3,900,000 / 일반석 ₩1,200,000" 다중 가격 -> 이코노미 식별 불가 시 안전 탈락 (회귀 ② 방어)
    f_e = "에어부산\n오전 11:30 - 오후 1:30\n직항\n비즈니스 ₩3,900,000 / 일반석 ₩1,537,500\n총 요금"
    try:
        parse_card_text(f_e)
        print("❌ [Test 14 FAILED] 다중 가격 불일치 카드가 제외되지 않음")
        all_passed = False
    except ValueError as e:
        if "식별 불가" in str(e):
            print("✅ [Test 14 PASSED] [Case E] 다중 가격 불일치 카드(비즈니스/일반석) 안전 제외")
        else:
            print(f"❌ [Test 14 FAILED] 예외 사유 불일치: {e}")
            all_passed = False

    # 15 [Case F]. "2:30 소요 / 오전 11:00 - 오후 1:30" -> 출발시각 오전 11:00으로 정확 파싱 (H-7)
    f_f = "에어부산\n2:30 소요\n오전 11:00 - 오후 1:30\n직항\n총 요금 ₩1,537,500"
    try:
        r_f = parse_card_text(f_f)
        assert r_f["price_per_person"] == 512500
        print("✅ [Test 15 PASSED] [Case F] '2:30 소요' 건너뛰고 출발시각(오전 11:00) 정확 파싱")
    except Exception as e:
        print(f"❌ [Test 15 FAILED] [Case F] 소요시간 오인 발생: {e}")
        all_passed = False

    # 16 [Case G]. "11:00 AM - 1:00 PM" 영문 표기 -> 출발시각 11시(오전)로 정확 파싱 (H-8)
    f_g = "Jeju Air\n11:00 AM - 1:00 PM\nNonstop\nTotal ₩1,421,100"
    try:
        r_g = parse_card_text(f_g)
        assert r_g["price_per_person"] == 473700
        print("✅ [Test 16 PASSED] [Case G] '11:00 AM - 1:00 PM' 출발시각 11:00 AM 정확 파싱")
    except Exception as e:
        print(f"❌ [Test 16 FAILED] [Case G] AM/PM 교차 오염 발생: {e}")
        all_passed = False

    # 17 [회귀 ② 케이스 1]. 카드에 1인당가와 총액이 함께 표시될 때 (쌍 식별)
    f_pair = "제주항공\n오후 2:05 - 오후 4:05\n직항\n₩473,700 / 왕복 총 ₩1,421,100"
    try:
        r_pair = parse_card_text(f_pair, global_page_text=real_page)
        assert r_pair["price_per_person"] == 473700, f"Expected 473700, got {r_pair['price_per_person']}"
        assert r_pair["price_total"] == 1421100
        print("✅ [Test 17 PASSED] [회귀 ②-1] 1인당/총액 동시 표시 카드에서 중복 나눔 없이 473,700원 정확 보존")
    except Exception as e:
        print(f"❌ [Test 17 FAILED] 1인당/총액 쌍 식별 실패: {e}")
        all_passed = False

    # 18 [회귀 ② 케이스 2]. 수수료가 섞인 카드
    f_fee = "제주항공\n오후 2:05 - 오후 4:05\n직항\n수수료 ₩55,000 / 왕복 ₩1,421,100"
    try:
        r_fee = parse_card_text(f_fee, global_page_text=real_page)
        assert r_fee["price_per_person"] == 473700, f"Expected 473700, got {r_fee['price_per_person']}"
        print("✅ [Test 18 PASSED] [회귀 ②-2] 수수료(55,000원) 제외하고 총액(1,421,100원 ÷ 3 = 473,700원) 정확 계산")
    except Exception as e:
        print(f"❌ [Test 18 FAILED] 수수료 제외 파싱 실패: {e}")
        all_passed = False

    # 19 [S-4 원 케이스]. 단서가 전혀 없는 ₩1,200,000 (휴리스틱 배제)
    f_no_cue = "대한항공\n오전 11:00 - 오후 1:00\n직항\n₩1,200,000"
    try:
        parse_card_text(f_no_cue, global_page_text="")
        print("❌ [Test 19 FAILED] 단서 없는 1,200,000원이 통과됨 (S-4 미해결)")
        all_passed = False
    except ValueError as e:
        if "단서 부재" in str(e):
            print("✅ [Test 19 PASSED] [S-4] 단서가 전혀 없는 1,200,000원은 임의로 나누지 않고 안전 제외")
        else:
            print(f"❌ [Test 19 FAILED] 예외 사유 불일치: {e}")
            all_passed = False

    # 20 [규칙 2.5 단서 충돌]. 페이지에 1인당과 총요금이 둘 다 있고 카드엔 단서 없음
    f_conflict = "제주항공\n오후 2:05 - 오후 4:05\n직항\n₩1,200,000"
    page_conflict = "가격은 1인당 요금 기준일 수 있습니다. 총 요금에는 세금이 포함됩니다."
    try:
        parse_card_text(f_conflict, global_page_text=page_conflict)
        print("❌ [Test 20 FAILED] 단서 충돌 카드가 통과됨 (규칙 2.5 오류)")
        all_passed = False
    except ValueError as e:
        if "단서 충돌" in str(e):
            print("✅ [Test 20 PASSED] [규칙 2.5] 단서 충돌 시 근거 없는 ÷3 배제하고 안전 제외")
        else:
            print(f"❌ [Test 20 FAILED] 예외 사유 불일치: {e}")
            all_passed = False

    print("==================================================")
    if all_passed:
        print("🎉 [결과] 20개 정밀 자체 검증 테스트 전원 통과! (100% SUCCESS)")
    else:
        print("❌ [결과] 일부 정밀 자체 검증 테스트 실패")
    print("==================================================")
    return all_passed


# ---------------------------------------------------------------------------
# CLI 엔트리포인트
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="✈️ Taiwan Flight Price Tracker Bot v3.3")
    parser.add_argument("--self-test", action="store_true", help="단위 테스트 스위트 실행 (네트워크/텔레그램 미사용)")
    parser.add_argument("--dry-run", action="store_true", help="크롤링 및 판정 수행 (텔레그램 및 state.json 쓰기 안 함)")
    parser.add_argument("--force", action="store_true", help="변동 없어도 주간 브리핑 강제 발송")
    parser.add_argument("--dump-cards", type=str, default=None, help="크롤링된 실물 카드 텍스트를 파일로 덤프 (예: dump.json)")
    args = parser.parse_args()

    # --self-test 실행
    if args.self_test:
        success = run_self_tests()
        sys.exit(0 if success else 1)

    # [D-1 보안 가드] 시크릿 환경변수 필수 검증
    if not args.dry_run:
        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
            print("[FATAL] TELEGRAM_TOKEN 또는 TELEGRAM_CHAT_ID 환경변수가 설정되지 않았습니다.", file=sys.stderr)
            print("[FATAL] GitHub Actions 환경에서는 Secrets를 등록하거나, 로컬 실행 시 --dry-run 옵션을 사용하세요.", file=sys.stderr)
            sys.exit(2)

    force_flag = args.force or (os.environ.get("FORCE_NOTIFY", "false").lower() == "true")
    run_tracker(dry_run=args.dry_run, force_notify=force_flag, dump_cards_file=args.dump_cards)


if __name__ == "__main__":
    main()
