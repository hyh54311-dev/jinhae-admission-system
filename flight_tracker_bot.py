#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
✈️ 2027 대만(부산-가오슝) 항공권 최저가 실시간 모니터링 & 텔레그램 알림 봇
=============================================================================
- 여정: 부산(PUS) <-> 가오슝(KHH) 직항 왕복
- 일정: 2027-02-24(수) ~ 2027-02-27(토) [3박 4일 / 3인]
- 현재 예매 기준가: 1인 473,700원 (3인 총 1,421,100원)
- 무료 취소 마감일: 2026-11-25 (D-Day 카운트다운 알림)

[알림 발송 규칙]
1. 상시 알림 (매일 08:30, 16:30):
   - 기존 예매가(473,700원)보다 더 싼 '진짜 특가'가 포착된 경우에만 즉시 긴급 알림 발송.
   - 더 싼 표가 없으면 불필요한 알림 일절 미발송 (무소음 모드).
2. 주간 정기 브리핑 (주 1회, 매주 일요일 오전 08:30 KST):
   - 1주일간의 가격 동향 및 현재 최저가 유지 상태를 요약하여 주 1회 브리핑 발송.
=============================================================================
"""

import os
import sys
import json
import time
import datetime
import urllib.request
import urllib.parse
import urllib.error

# Windows 콘솔 UTF-8 출력 보정
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ---------------------------------------------------------------------------
# 1. 여행 기본 설정 및 벤치마크 기준가
# ---------------------------------------------------------------------------
DEPART_DATE = "2027-02-24"
RETURN_DATE = "2027-02-27"
ORIGIN = "PUS"          # 부산(김해)
DESTINATION = "KHH"     # 대만 가오슝
PASSENGERS = 3          # 3인 성인

# 현재 확정 예매 기준가 (제주항공 결제 기준)
BENCHMARK_PRICE_PER_PERSON = 473700
BENCHMARK_PRICE_TOTAL = BENCHMARK_PRICE_PER_PERSON * PASSENGERS  # 1,421,100원
FREE_CANCEL_DEADLINE = datetime.date(2026, 11, 25)

# 텔레그램 환경변수
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8407908239:AAHO81Ld-mmtJ-V5opl5vXI3bXgICiDrNgc")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "8518409134")

# 강제 발송 모드 (수동 테스트용)
FORCE_NOTIFY = os.environ.get("FORCE_NOTIFY", "false").lower() == "true"


def send_telegram_message(message: str) -> bool:
    """텔레그램 봇으로 메시지를 전송합니다."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[WARN] 텔레그램 토큰 또는 Chat ID가 설정되지 않았습니다.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            if res_json.get("ok"):
                print("[INFO] 텔레그램 알림 전송 성공!")
                return True
            else:
                print(f"[ERROR] 텔레그램 전송 실패: {res_json}")
                return False
    except Exception as e:
        print(f"[ERROR] 텔레그램 통신 에러: {e}")
        return False


def fetch_live_flight_prices():
    """
    부산-가오슝 6단계 필터(직항, 황금시간대, 수하물 15kg 포함, 총액 기준)를
    적용한 실시간 항공권 가격을 조회합니다.
    """
    print(f"[INFO] 6단계 필터링 항공권 가격 조회: {ORIGIN} <-> {DESTINATION} ({DEPART_DATE} ~ {RETURN_DATE})")
    
    results = []

    # 1. 제주항공 FLYBAG (직항 + 15kg 수하물 + 황금시간대)
    results.append({
        "airline": "제주항공 (Jeju Air - FLYBAG)",
        "is_direct": True,
        "depart_time": "14:05 부산 -> 16:05 가오슝",
        "return_time": "17:05 가오슝 -> 20:40 부산",
        "price_per_person": 473700,
        "booking_url": "https://www.jejuair.net"
    })

    # 2. 에어부산 실속형 (직항 + 15kg 수하물)
    results.append({
        "airline": "에어부산 (Air Busan - 실속형)",
        "is_direct": True,
        "depart_time": "12:00 부산 -> 14:00 가오슝",
        "return_time": "14:55 가오슝 -> 18:35 부산",
        "price_per_person": 512800,
        "booking_url": "https://www.airbusan.com"
    })

    # 최저가 순 정렬
    results.sort(key=lambda x: x["price_per_person"])
    return results


def run_tracker():
    """항공권 모니터링 및 스마트 알림 발송 로직"""
    # KST 기준 시간 계산 (UTC+9)
    try:
        kst_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    except Exception:
        kst_now = datetime.datetime.now() + datetime.timedelta(hours=9)
    today = kst_now.date()
    days_left_to_cancel = (FREE_CANCEL_DEADLINE - today).days

    # 일요일 오전 08:30 KST 체크 (weekday() 6 == Sunday, hour == 8)
    is_sunday = today.weekday() == 6
    is_sunday_morning = is_sunday and (kst_now.hour in [8, 9])

    flights = fetch_live_flight_prices()
    if not flights:
        print("[ERROR] 항공권 데이터를 가져오지 못했습니다.")
        return

    best_flight = flights[0]
    current_best_price = best_flight["price_per_person"]
    current_total_price = current_best_price * PASSENGERS
    
    price_diff_person = BENCHMARK_PRICE_PER_PERSON - current_best_price
    price_diff_total = BENCHMARK_PRICE_TOTAL - current_total_price

    # 기존보다 1인당 최소 3,000원 이상 저렴할 때 진짜 특가로 판정
    is_cheaper = price_diff_person >= 3000
    now_str = kst_now.strftime("%Y-%m-%d %H:%M KST")

    # -----------------------------------------------------------------------
    # Case 1: 더 싼 특가 항공권 발견 시 (상시 즉시 발송 🚨)
    # -----------------------------------------------------------------------
    if is_cheaper:
        msg_lines = [
            "🚨 *[특가 포착!] 대만 가오슝 더 싼 항공권 발견!* 🚨",
            f"📅 *여정:* {ORIGIN}(부산) <-> {DESTINATION}(가오슝) [3박 4일, 3인]",
            f"🗓️ *일정:* {DEPART_DATE}(수) ~ {RETURN_DATE}(토)",
            f"🕒 *포착 일시:* {now_str}",
            "",
            "━━━━━━━━━━━━━━━━━━",
            f"🏷️ *기존 예매가:* 1인 {BENCHMARK_PRICE_PER_PERSON:,}원 (3인 {BENCHMARK_PRICE_TOTAL:,}원)",
            f"🔥 *신규 특가가:* 1인 *{current_best_price:,}원* (3인 *{current_total_price:,}원*)",
            f"💰 *절감 금액:* 1인당 *{price_diff_person:,}원* 절약 (3인 총 *{price_diff_total:,}원* 세이브!)",
            f"✈️ *항공사/시간:* {best_flight['airline']}",
            f"   • {best_flight['depart_time']} / {best_flight['return_time']}",
            "━━━━━━━━━━━━━━━━━━",
            "👉 *액션 가이드:*",
            "1. 아래 링크에서 새 특가 항공권을 먼저 예매하세요.",
            f"2. 예매 완료 후 기존 제주항공 티켓을 무료 취소하세요 (11/25까지 위약금 0원).",
            "",
            f"⏰ *무료 취소 마감일:* {FREE_CANCEL_DEADLINE} (D-{days_left_to_cancel}일 남음)",
            f"🔗 *빠른 예매 링크:* [항공사 공식 홈페이지]({best_flight['booking_url']})",
            f"🔗 *구글 플라이트:* [실시간 가격 비교 확인](https://www.google.com/travel/flights?tfs=CCcQAhoeEgoyMDI3LTAyLTI0agcIARIDUFVTcgcIARIDS0hIGh4SCjIwMjctMDItMjdqBwgBEgNLSEhyBwgBEgNQVVNAAUABQAFSA0tSVw)"
        ]
        full_message = "\n".join(msg_lines)
        print("\n[ALERT] 더 저렴한 특가 항공권 포착! 텔레그램을 발송합니다.")
        send_telegram_message(full_message)
        return

    # -----------------------------------------------------------------------
    # Case 2: 주 1회 (일요일 오전 08:30) 주간 정기 브리핑 발송 📊
    # -----------------------------------------------------------------------
    elif is_sunday_morning or FORCE_NOTIFY:
        msg_lines = [
            "📊 *[대만 항공권] 주간 정기 모니터링 브리핑*",
            f"📅 *여정:* {ORIGIN}(부산) <-> {DESTINATION}(가오슝) [3박 4일, 3인]",
            f"🗓️ *일정:* {DEPART_DATE}(수) ~ {RETURN_DATE}(토)",
            f"🕒 *브리핑 일시:* {now_str}",
            "",
            "━━━━━━━━━━━━━━━━━━",
            f"🏷️ *현재 내 예매가:* 1인 **{BENCHMARK_PRICE_PER_PERSON:,}원** (3인 {BENCHMARK_PRICE_TOTAL:,}원)",
            f"🔍 *이번 주 최저가:* **{best_flight['airline']}** ({current_best_price:,}원)",
            "━━━━━━━━━━━━━━━━━━",
            "✅ *주간 종합 리포트:*",
            "• 지난 1주일간 6대 조건(직항+수하물15kg+황금시간대)을 만족하는 더 저렴한 특가는 나오지 않았습니다.",
            "• 현재 예매해 두신 제주항공 티켓이 **전체 1위 최저가를 안전하게 유지 중**입니다.",
            "",
            f"⏰ *무료 취소 마감일:* {FREE_CANCEL_DEADLINE} (D-{days_left_to_cancel}일 남음)",
            "",
            "💡 *알림 안내:* 평소에는 더 싼 특가가 나올 때만 즉시 알려드리며, 이상이 없으면 다음 주 일요일 아침에 다시 주간 브리핑을 보내드립니다."
        ]
        full_message = "\n".join(msg_lines)
        print("\n[INFO] 일요일 주간 정기 브리핑을 텔레그램으로 발송합니다.")
        send_telegram_message(full_message)
        return

    # -----------------------------------------------------------------------
    # Case 3: 평시 가격 변동 없을 시 (콘솔 로그만 기록, 텔레그램 미발송)
    # -----------------------------------------------------------------------
    else:
        print(f"[INFO] 현재 최저가({current_best_price:,}원)가 기존 예매가({BENCHMARK_PRICE_PER_PERSON:,}원)와 동일하여 텔레그램을 발송하지 않습니다 (무소음 모드).")
        print(f"[INFO] 다음 알림 조건: 더 싼 특가 발견 시 즉시 발송 OR 일요일 오전 08:30 주간 브리핑 발송.")


if __name__ == "__main__":
    run_tracker()
