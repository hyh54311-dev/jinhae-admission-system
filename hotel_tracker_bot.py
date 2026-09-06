# -*- coding: utf-8 -*-
"""
=============================================================================
🏨 여수 더 호텔 수 (The Hotel Soo) 2026 개천절 연휴 취소표 실시간 감지 봇 v1.0
=============================================================================
[대상 정보]
  - 숙소: 여수 더 호텔 수 (The Hotel Soo)
  - 일정: 2026-10-03(토) ~ 2026-10-05(월) [2박 3일]
  - 타깃 객실: 프리미엄 온돌 (브릿지뷰, 79㎡, 방+거실 분리형)
  - 기준 인원: 성인 2인 (최대 4인)
  - 가동 환경: GitHub Actions (100% 무료 서버리스) & 로컬 겸용

[동작 원칙 (Fail-Closed)]
  - 대만 항공권 봇의 엄격한 원칙 준수:
    "틀린 알림을 보내는 것이 알림을 안 보내는 것보다 훨씬 나쁘다."
  - 객실명에 ("프리미엄" AND "온돌") 또는 ("79" AND "온돌")이 포함되고,
    "더블", "트윈", "싱글" 등의 침대 수식어가 없는 경우에만 타깃 온돌방으로 최종 승인.
  - 전 객실 매진(SOLD_OUT) 상태와 잔여 객실(AVAILABLE) 상태 전이 시에만 즉각 알림.
  - force_notify 플래그 활성화 시 현재 탐색 현황 브리핑 발송.
=============================================================================
"""

import os
import sys
import json
import time
import re
import html
import datetime
import argparse
import urllib.request
import urllib.parse
import urllib.error
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from playwright.sync_api import sync_playwright

# Windows 콘솔 UTF-8 출력 보정
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# 핵심 여정 및 타깃 상수
# ---------------------------------------------------------------------------
HOTEL_NAME = "여수 더 호텔 수 (The Hotel Soo)"
HOTEL_TEL = "061-681-1111"
CHECK_IN_DATE = "2026-10-03"
CHECK_OUT_DATE = "2026-10-05"
NIGHTS = 2
GUESTS = 2

TARGET_ROOM_NAME = "프리미엄 온돌 (브릿지뷰, 79㎡)"
TARGET_ROOM_TOKENS = ["프리미엄", "온돌", "premium", "ondol"]
EXCLUDED_TOKENS = ["더블", "트윈", "싱글", "double", "twin", "single"]

AGODA_URL = (
    f"https://www.agoda.com/ko-kr/the-hotel-soo/hotel/yeosu-si-kr.html"
    f"?checkin={CHECK_IN_DATE}&checkout={CHECK_OUT_DATE}&los={NIGHTS}&rooms=1&adults={GUESTS}"
)
WINGS_URL = (
    f"https://be4.wingsbooking.com/THEHTLSOO1111/rateSelect"
    f"?check_in={CHECK_IN_DATE}&check_out={CHECK_OUT_DATE}&rooms=1&adult={GUESTS}&children=0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "hotel_state.json")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

KST = datetime.timezone(datetime.timedelta(hours=9))


# ---------------------------------------------------------------------------
# 상태 보존 및 래칫 엔진 (hotel_state.json)
# ---------------------------------------------------------------------------
def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] 상태 파일 읽기 실패 ({e}), 초기 상태로 시작")
    return {
        "hotel": HOTEL_NAME,
        "check_in": CHECK_IN_DATE,
        "check_out": CHECK_OUT_DATE,
        "target_room": TARGET_ROOM_NAME,
        "status": "SOLD_OUT",
        "last_checked_kst": None,
        "last_alert_kst": None,
        "consecutive_failures": 0,
        "history": []
    }


def save_state(state: dict):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        print(f"[STATE] 상태 파일 저장 완료 -> {STATE_FILE}")
    except Exception as e:
        print(f"[ERROR] 상태 파일 저장 실패: {e}")


# ---------------------------------------------------------------------------
# 텔레그램 발송 엔진
# ---------------------------------------------------------------------------
def send_telegram(text: str, dry_run: bool = False) -> bool:
    if dry_run:
        print("\n[DRY-RUN 텔레그램 발송 가상 테스트]")
        print(text)
        return True

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[WARN] TELEGRAM_TOKEN 또는 TELEGRAM_CHAT_ID 미설정으로 알림 건너뜀")
        return False

    if len(text) > 4000:
        lines = text.split("\n")
        truncated = []
        cur_len = 0
        for line in lines:
            if cur_len + len(line) + 1 > 3800:
                truncated.append("... [내용 일부 축약됨]")
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
            err_body = he.read().decode("utf-8", errors="ignore")
            print(f"[WARN] 텔레그램 HTTP {he.code}: {err_body}")
            return False
        except Exception as e:
            print(f"[WARN] 텔레그램 네트워크 오류: {e}")
            return False

    # 1차 HTML 모드 시도
    success = _post({"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"})
    if not success:
        # 2차 평문 모드 재시도
        plain_text = re.sub(r"<[^>]+>", "", text)
        print("[INFO] 텔레그램 평문 모드로 재시도")
        success = _post({"chat_id": TELEGRAM_CHAT_ID, "text": plain_text})

    return success


# ---------------------------------------------------------------------------
# 실시간 크롤링 & 엄격 판정 엔진 (Playwright)
# ---------------------------------------------------------------------------
def crawl_agoda(headless: bool = True) -> dict:
    """
    아고다 실시간 페이지를 렌더링하여 여수 더 호텔 수의 객실 잔여 여부를 파싱합니다.
    Fail-Closed 원칙에 따라 확실한 근거가 있을 때만 객실 오픈을 선언합니다.
    """
    result = {
        "success": False,
        "is_sold_out": False,
        "target_room_found": False,
        "target_room_info": None,
        "other_rooms": [],
        "raw_text_length": 0,
        "error_message": None
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="ko-KR",
            timezone_id="Asia/Seoul",
            viewport={"width": 1400, "height": 1000}
        )
        page = context.new_page()

        # 브라우저 지문 위장 패치
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
        """)

        try:
            print(f"[CRAWL] 아고다 직행 딥링크 접속: {AGODA_URL}")
            response = page.goto(AGODA_URL, wait_until="domcontentloaded", timeout=40000)
            status_code = response.status if response else 0
            print(f"[CRAWL] 페이지 응답 코드: {status_code}")

            # AJAX 및 렌더링 대기
            page.wait_for_timeout(5000)

            # 스크롤하여 객실 섹션 로딩 유도
            page.evaluate("window.scrollBy(0, 1100)")
            page.wait_for_timeout(2500)

            body_text = page.locator("body").inner_text()
            result["raw_text_length"] = len(body_text)

            # [1단계: 글로벌 매진 검증 (Global Sold-Out Guard)]
            sold_out_signatures = [
                "판매 완료",
                "마지막 남은 객실이 이미 예약되었습니다",
                "선택하신 날짜에 예약 가능한 객실이 없습니다",
                "일치하는 객실이 없습니다",
                "예약 가능한 객실이 없습니다"
            ]
            has_sold_out_banner = any(sig in body_text for sig in sold_out_signatures)

            # [2단계: 개별 객실 카드 탐색 (H4 및 동적 styled-components 포함)]
            raw_candidates = page.locator(
                "h4, div[data-selenium='masterroom-title'], "
                "[class*='MasterRoom-title'], "
                "h3[class*='RoomTitle'], "
                "[class*='room-name']"
            ).all_inner_texts()

            ROOM_KEYWORDS = [
                "room", "객실", "온돌", "ondol", "더블", "double", "트윈", "twin",
                "스위트", "suite", "디럭스", "deluxe", "슈페리어", "superior",
                "스탠다드", "standard", "브릿지", "bridge", "오션", "ocean", "뷰", "view"
            ]

            cleaned_titles = []
            seen_titles = set()
            for c in raw_candidates:
                text = c.strip()
                if not text or len(text) > 120 or text.endswith("?") or "어떤" in text or "인가요" in text or "무엇" in text:
                    continue
                text_lower = text.lower()
                if any(k in text_lower for k in ROOM_KEYWORDS):
                    if text not in seen_titles:
                        seen_titles.add(text)
                        cleaned_titles.append(text)

            print(f"[CRAWL] 감지된 객실명 목록 (총 {len(cleaned_titles)}개): {cleaned_titles}")

            # 매진 배너가 존재하고 실질적 객실 카드가 없으면 확실한 매진으로 판정
            if has_sold_out_banner and len(cleaned_titles) == 0:
                print("[CRAWL] ✅ '판매 완료(마지막 남은 객실 예약됨)' 배너 확인 -> 전 객실 매진 상태")
                result["is_sold_out"] = True
                result["success"] = True
                return result

            # 객실 카드가 있는 경우 타깃 온돌방 여부 정밀 검증
            available_rooms = []
            for title in cleaned_titles:
                # 타깃 검증: '프리미엄' + '온돌' 포함 및 침대 단어 배제 (영문/한글 복합 Fail-Closed 가드레일)
                title_lower = title.lower()
                is_ondol = ("온돌" in title) or ("ondol" in title_lower)
                is_premium = ("프리미엄" in title) or ("premium" in title_lower) or ("79" in title)
                has_bed = any(bed.lower() in title_lower for bed in EXCLUDED_TOKENS)

                if is_ondol and is_premium and not has_bed:
                    print(f"[CRAWL] 🚨 타깃 객실 발견!! -> {title}")
                    result["target_room_found"] = True
                    result["target_room_info"] = title
                else:
                    available_rooms.append(title)

            result["other_rooms"] = available_rooms

            if result["target_room_found"]:
                result["is_sold_out"] = False
                result["success"] = True
            elif len(available_rooms) > 0:
                print(f"[CRAWL] ℹ️ 타깃 온돌은 없으나 다른 객실 오픈됨: {available_rooms}")
                result["is_sold_out"] = False
                result["success"] = True
            else:
                # 카드가 비어있고 매진 배너도 모호한 경우
                if has_sold_out_banner:
                    result["is_sold_out"] = True
                    result["success"] = True
                else:
                    result["error_message"] = "객실 목록 및 매진 배너를 판별할 수 없음 (선택자 불일치 또는 WAF 의심)"
                    result["success"] = False

        except Exception as e:
            print(f"[ERROR] 크롤링 중 예외 발생: {e}")
            result["error_message"] = str(e)
            result["success"] = False
        finally:
            browser.close()

    return result


# ---------------------------------------------------------------------------
# 메시지 포맷팅 및 메인 실행 오케스트레이터
# ---------------------------------------------------------------------------
def build_alert_message(crawl_res: dict, state: dict) -> str:
    now_kst = datetime.datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")

    if crawl_res.get("target_room_found"):
        title_info = crawl_res.get("target_room_info", TARGET_ROOM_NAME)
        return (
            f"🚨 <b>[취소표 긴급 발생!] {html.escape(HOTEL_NAME)}</b>\n\n"
            f"선생님, 고대하던 <b>동일한 프리미엄 온돌 객실</b>이 지금 예약 가능합니다!\n\n"
            f"📅 <b>일정:</b> {CHECK_IN_DATE} ~ {CHECK_OUT_DATE} ({NIGHTS}박 3일)\n"
            f"🛏️ <b>객실:</b> {html.escape(title_info)}\n"
            f"⏰ <b>감지 시각:</b> {now_kst} (KST)\n\n"
            f"연휴 취소표는 몇 분 만에 다시 마감될 수 있으니 지금 즉시 예약하세요!\n\n"
            f"👉 <a href=\"{AGODA_URL}\"><b>[아고다 지금 즉시 예약하기]</b></a>\n"
            f"📞 <b>호텔 직영 프런트:</b> {HOTEL_TEL}"
        )
    elif len(crawl_res.get("other_rooms", [])) > 0:
        rooms_str = ", ".join(crawl_res.get("other_rooms")[:4])
        return (
            f"🔔 <b>[객실 오픈 알림] {html.escape(HOTEL_NAME)}</b>\n\n"
            f"타깃 온돌방은 아니지만, <b>다른 유형의 객실 취소표</b>가 발생했습니다.\n\n"
            f"📅 <b>일정:</b> {CHECK_IN_DATE} ~ {CHECK_OUT_DATE} ({NIGHTS}박)\n"
            f"🛏️ <b>오픈 객실:</b> {html.escape(rooms_str)}\n"
            f"⏰ <b>감지 시각:</b> {now_kst} (KST)\n\n"
            f"동반 가족이 다른 객실이라도 고려 중이라면 확인해 보세요!\n\n"
            f"👉 <a href=\"{AGODA_URL}\"><b>[아고다 객실 확인하기]</b></a>"
        )
    else:
        return ""


def build_status_briefing(crawl_res: dict, state: dict) -> str:
    now_kst = datetime.datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    if crawl_res.get("target_room_found"):
        status_kr = "🚨 타깃 프리미엄 온돌 오픈 중! (즉시 예약 가능)"
    elif len(crawl_res.get("other_rooms", [])) > 0:
        status_kr = f"🔔 타깃 외 다른 객실 오픈 중 ({len(crawl_res['other_rooms'])}개)"
    elif crawl_res.get("is_sold_out"):
        status_kr = "🔒 전 객실 매진 유지 중 (SOLD OUT)"
    else:
        status_kr = "❓ 상태 미확인"

    return (
        f"📊 <b>[여수 더 호텔 수 실시간 모니터링 브리핑]</b>\n\n"
        f"선생님, 요청하신 개천절 연휴 취소표 감지 봇이 정상 가동 중입니다.\n\n"
        f"🏨 <b>숙소:</b> {html.escape(HOTEL_NAME)}\n"
        f"📅 <b>일정:</b> {CHECK_IN_DATE} ~ {CHECK_OUT_DATE} (2박 3일, 개천절 연휴)\n"
        f"🎯 <b>타깃:</b> {html.escape(TARGET_ROOM_NAME)}\n"
        f"📌 <b>현재 상태:</b> <b>{status_kr}</b>\n"
        f"⏰ <b>점검 시각:</b> {now_kst} (KST)\n\n"
        f"💡 <b>모니터링 안내:</b>\n"
        f"• 대만 항공권 봇과 동일하게 <b>매일 08:30 / 16:30 KST</b>에 자동 점검합니다.\n"
        f"• 취소표가 감지되는 즉시 텔레그램 긴급 알림과 다이렉트 예약 링크를 발송합니다.\n"
        f"• 무료 취소 집중 마감기(9/26~9/30)에 취소표 발생 확률이 가장 높습니다."
    )


def run_bot(force_notify: bool = False, dry_run: bool = False):
    now_kst = datetime.datetime.now(KST).isoformat()
    state = load_state()

    print("=" * 70)
    print(f"🏨 여수 더 호텔 수 취소표 감지 봇 가동 시작: {now_kst}")
    print(f"  - 호텔: {HOTEL_NAME}")
    print(f"  - 일정: {CHECK_IN_DATE} ~ {CHECK_OUT_DATE}")
    print(f"  - 타깃: {TARGET_ROOM_NAME}")
    print(f"  - 강제 알림 옵션(force_notify): {force_notify}")
    print("=" * 70)

    crawl_res = crawl_agoda(headless=True)
    state["last_checked_kst"] = now_kst

    if not crawl_res["success"]:
        state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
        print(f"[FAIL] 크롤링 실패 (연속 {state['consecutive_failures']}회): {crawl_res['error_message']}")
        if state["consecutive_failures"] >= 3:
            warn_msg = (
                f"⚠️ <b>[감시 봇 경고] {html.escape(HOTEL_NAME)} 크롤링 3회 연속 실패</b>\n\n"
                f"오류 내용: {html.escape(str(crawl_res['error_message']))}\n"
                f"사이트 선택자 변경 또는 일시적 네트워크 점검이 필요합니다."
            )
            send_telegram(warn_msg, dry_run=dry_run)
        save_state(state)
        return

    # 크롤링 성공 시 연속 실패 카운터 리셋
    state["consecutive_failures"] = 0

    current_status = "TARGET_AVAILABLE" if crawl_res["target_room_found"] else (
        "OTHER_AVAILABLE" if len(crawl_res["other_rooms"]) > 0 else "SOLD_OUT"
    )
    previous_status = state.get("status", "SOLD_OUT")

    print(f"[STATUS] 이전 상태: {previous_status} ➔ 현재 상태: {current_status}")

    # 상태 전이 판정
    should_alert = False
    alert_text = ""

    if current_status in ["TARGET_AVAILABLE", "OTHER_AVAILABLE"] and previous_status == "SOLD_OUT":
        # 매진에서 객실 오픈으로 전이 -> 즉각 알림
        should_alert = True
        alert_text = build_alert_message(crawl_res, state)
        state["last_alert_kst"] = now_kst
    elif force_notify:
        # 강제 브리핑 요청
        should_alert = True
        alert_text = build_status_briefing(crawl_res, state)
        state["last_alert_kst"] = now_kst

    # 상태 갱신 및 저장
    state["status"] = current_status
    state["history"].append({
        "timestamp": now_kst,
        "status": current_status,
        "other_rooms_count": len(crawl_res.get("other_rooms", []))
    })
    # 히스토리는 최근 30개만 보존
    state["history"] = state["history"][-30:]
    save_state(state)

    if should_alert and alert_text:
        print("[ALERT] 텔레그램 발송 시작...")
        sent_ok = send_telegram(alert_text, dry_run=dry_run)
        print(f"[ALERT] 텔레그램 발송 결과: {'성공' if sent_ok else '실패'}")
    else:
        print("[INFO] 상태 변동 없음(SOLD_OUT 유지) 및 강제 알림 미요청으로 조용히 종료합니다.")

    print("=" * 70)
    print("🏨 모니터링 사이클 완료")
    print("=" * 70)


# ---------------------------------------------------------------------------
# CLI 진입점
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="여수 더 호텔 수 취소표 모니터링 봇")
    parser.add_argument("--force-notify", action="store_true", help="상태 변동과 무관하게 텔레그램 브리핑 발송")
    parser.add_argument("--dry-run", action="store_true", help="텔레그램 실제 발송 없이 콘솔 출력만 수행")
    args = parser.parse_args()

    # 환경변수 FORCE_NOTIFY 도 함께 감지 (GitHub Actions workflow_dispatch 용)
    env_force = os.environ.get("FORCE_NOTIFY", "false").lower() in ["true", "1", "yes"]
    is_force = args.force_notify or env_force

    run_bot(force_notify=is_force, dry_run=args.dry_run)
