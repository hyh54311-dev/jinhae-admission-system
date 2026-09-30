# -*- coding: utf-8 -*-
"""
test_main_flow.py - Verify main() execution flow across all modes (Normal, DRY_RUN, --force, --check-only)
and Claude Opus 5.5 audit scenarios (T-A: needs_work delayed cron alert vs T-B: completed delayed cron silence).
"""
import os
import sys
import datetime as dt
from zoneinfo import ZoneInfo
import unittest.mock as mock

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Force local proxy bypass for test if needed
os.environ["KIS_VERIFY_SSL"] = "0"
os.environ["TELEGRAM_TOKEN"] = ""
os.environ["TELEGRAM_CHAT_ID"] = ""

# Add repo to sys.path
repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "jinhae-k-momentum-bot"))
if repo_dir not in sys.path:
    sys.path.insert(0, repo_dir)

import kis_bot_multi
kis_bot_multi.TELEGRAM_TOKEN = ""
kis_bot_multi.TELEGRAM_CHAT_ID = ""

KST = ZoneInfo("Asia/Seoul")

def test_main_modes():
    weekend_dt = dt.datetime(2026, 9, 27, 10, 0, tzinfo=KST)  # 일요일

    print("🧪 [Test 1] Testing main() with standard args (Weekend silent exit)...")
    with mock.patch("kis_bot_multi.now_kst", return_value=weekend_dt):
        with mock.patch.object(sys, "argv", ["kis_bot_multi.py"]):
            kis_bot_multi._RUN_COMPLETED = False
            kis_bot_multi.main()
            assert kis_bot_multi._RUN_COMPLETED, "Weekend normal run should set _RUN_COMPLETED=True"
    print("✅ [Test 1 통과] Weekend normal run: Zero UnboundLocalError & clean exit.")

    print("\n🧪 [Test 2] Testing main() with --check-only (Weekend skip)...")
    with mock.patch("kis_bot_multi.now_kst", return_value=weekend_dt):
        with mock.patch.object(sys, "argv", ["kis_bot_multi.py", "--check-only"]):
            kis_bot_multi._RUN_COMPLETED = False
            kis_bot_multi.main()
            assert kis_bot_multi._RUN_COMPLETED, "--check-only weekend run should set _RUN_COMPLETED=True"
    print("✅ [Test 2 통과] --check-only weekend run: Zero UnboundLocalError & clean exit.")

    print("\n🧪 [Test 3] Testing main() with --force (Weekend DRY_RUN forced conversion)...")
    with mock.patch("kis_bot_multi.now_kst", return_value=weekend_dt):
        with mock.patch.object(sys, "argv", ["kis_bot_multi.py", "--force"]):
            with mock.patch("kis_bot_multi.send_telegram") as mock_tel:
                kis_bot_multi._RUN_COMPLETED = False
                kis_bot_multi.DRY_RUN = False
                kis_bot_multi.main()
                assert kis_bot_multi._RUN_COMPLETED, "--force run should set _RUN_COMPLETED=True"
                assert kis_bot_multi.DRY_RUN is True, "--force on weekend must force DRY_RUN=True"
    print("✅ [Test 3 통과] --force weekend run: DRY_RUN properly assigned globally without UnboundLocalError!")


def test_delayed_cron_scenarios():
    print("\n🧪 [Test 4 / T-A] Testing delayed cron at 16:40 KST with UNCOMPLETED account (needs_work)...")
    # Friday 16:40 KST (weekday=4)
    weekday_1640 = dt.datetime(2026, 9, 18, 16, 40, tzinfo=KST)

    with mock.patch("kis_bot_multi.now_kst", return_value=weekday_1640):
        with mock.patch("kis_bot_multi.calculate_momentum_signals", return_value=({"069500": 1.0}, "테스트")):
            with mock.patch("kis_bot_multi.fetch_prices", return_value={"069500": 35000}):
                # Uncompleted account: skip=False, prior_completed=False
                with mock.patch("kis_bot_multi.check_already_rebalanced_today", 
                                return_value=(False, "[연금저축계좌] 미집행 — 신규 집행", False)):
                    with mock.patch("kis_bot_multi.send_telegram") as mock_tel:
                        with mock.patch.object(sys, "argv", ["kis_bot_multi.py"]):
                            with mock.patch.dict(os.environ, {"GITHUB_EVENT_NAME": "schedule", "KIS_PENSION_CANO": "12345678"}):
                                kis_bot_multi._RUN_COMPLETED = False
                                kis_bot_multi.main()
                                assert kis_bot_multi._RUN_COMPLETED
                                assert mock_tel.call_count == 1, f"Expected exactly 1 alert, got {mock_tel.call_count}"
                                sent_msg = mock_tel.call_args[0][0]
                                assert "거래창 밖 기동" in sent_msg and "미완료 계좌" in sent_msg, f"Unexpected message: {sent_msg}"
    print("✅ [Test 4 / T-A 통과] 미완료 상태에서 16:40 크론 기동 ➔ 텔레그램 1통 발송 보장! (질문 3 요구 100% 충족)")

    print("\n🧪 [Test 5 / T-B] Testing delayed cron at 16:40 KST with COMPLETED account (당일 확인 샷)...")
    with mock.patch("kis_bot_multi.now_kst", return_value=weekday_1640):
        with mock.patch("kis_bot_multi.calculate_momentum_signals", return_value=({"069500": 1.0}, "테스트")):
            with mock.patch("kis_bot_multi.fetch_prices", return_value={"069500": 35000}):
                # Completed today: skip=True, prior_completed=False (당일 확인 알림 허용 모드이나 지연 샷이므로 무소음이어야 함)
                with mock.patch("kis_bot_multi.check_already_rebalanced_today", 
                                return_value=(True, "[연금저축계좌] 당일 리밸런싱 집행 완료 — 당일 확인 스킵", False)):
                    with mock.patch("kis_bot_multi.send_telegram") as mock_tel:
                        with mock.patch.object(sys, "argv", ["kis_bot_multi.py"]):
                            with mock.patch.dict(os.environ, {"GITHUB_EVENT_NAME": "schedule", "KIS_PENSION_CANO": "12345678"}):
                                kis_bot_multi._RUN_COMPLETED = False
                                kis_bot_multi.main()
                                assert kis_bot_multi._RUN_COMPLETED
                                assert mock_tel.call_count == 0, f"Expected 0 alerts for delayed check shot, got {mock_tel.call_count}"
    print("✅ [Test 5 / T-B 통과] 당일 집행 완료 상태에서 16:40 지연 크론 기동 ➔ 텔레그램 0통 완벽 무소음!")

    print("\n🎉 모든 결합 및 Claude 감사 시나리오 100% 통과! Assembly integrity verified.")


def test_stale_order_scenarios():
    print("\n🧪 [Test 6 / T-C] Testing stale order (09:47 order, age>30m) at 11:17 KST (Market Open)...")
    weekday_1117 = dt.datetime(2026, 9, 18, 11, 17, tzinfo=KST)

    with mock.patch("kis_bot_multi.now_kst", return_value=weekday_1117):
        with mock.patch("kis_bot_multi.is_market_open_today", return_value=True):
            with mock.patch("kis_bot_multi.calculate_momentum_signals", return_value=({"069500": 1.0}, "테스트")):
                with mock.patch("kis_bot_multi.fetch_prices", return_value={"069500": 35000}):
                    # Mock open order from 09:47:00 (age 90m > 30m)
                    stale_order = [{"odno": "9001", "pdno": "069500", "rmn_qty": "10", "ord_tmd": "094700", "ord_gno_brno": "00"}]
                    
                    def mock_get_daily_orders(token, cano, prdt_cd, ccld_dvsn="00", start_dt=None):
                        if ccld_dvsn == "02":  # 미체결 조회
                            return stale_order
                        return []  # 당월 체결 없음

                    with mock.patch("kis_bot_multi.get_daily_orders", side_effect=mock_get_daily_orders):
                        with mock.patch("kis_bot_multi.get_account_balance", return_value=(500000, 100000, {})):
                            with mock.patch("kis_bot_multi.cancel_order", return_value={"rt_cd": "0", "msg1": "정상"}) as mock_cancel:
                                with mock.patch("kis_bot_multi.rebalance_account", return_value="[연금저축계좌] 리밸런싱 완료") as mock_reb:
                                    with mock.patch("kis_bot_multi.send_telegram") as mock_tel:
                                        with mock.patch.object(sys, "argv", ["kis_bot_multi.py"]):
                                            with mock.patch.dict(os.environ, {"GITHUB_EVENT_NAME": "schedule", "KIS_PENSION_CANO": "12345678"}):
                                                kis_bot_multi._RUN_COMPLETED = False
                                                kis_bot_multi.main()
                                                assert kis_bot_multi._RUN_COMPLETED
                                                assert mock_cancel.call_count == 1, f"Expected 1 cancel_order call, got {mock_cancel.call_count}"
                                                assert mock_reb.call_count == 1, f"Expected 1 rebalance_account call, got {mock_reb.call_count}"
    print("✅ [Test 6 / T-C 통과] 장중 묵은 미체결 발견 시 ➔ cancel_order 1회 호출 후 rebalance_account 정상 재집행!")

    print("\n🧪 [Test 7 / T-D] Testing stale order (09:47 order, age>30m) at 16:40 KST (Market Closed)...")
    weekday_1640 = dt.datetime(2026, 9, 18, 16, 40, tzinfo=KST)

    with mock.patch("kis_bot_multi.now_kst", return_value=weekday_1640):
        with mock.patch("kis_bot_multi.is_market_open_today", return_value=True):
            with mock.patch("kis_bot_multi.calculate_momentum_signals", return_value=({"069500": 1.0}, "테스트")):
                with mock.patch("kis_bot_multi.fetch_prices", return_value={"069500": 35000}):
                    stale_order = [{"odno": "9001", "pdno": "069500", "rmn_qty": "10", "ord_tmd": "094700", "ord_gno_brno": "00"}]
                    
                    def mock_get_daily_orders(token, cano, prdt_cd, ccld_dvsn="00", start_dt=None):
                        if ccld_dvsn == "02":
                            return stale_order
                        return []

                    with mock.patch("kis_bot_multi.get_daily_orders", side_effect=mock_get_daily_orders):
                        with mock.patch("kis_bot_multi.get_account_balance", return_value=(500000, 100000, {})):
                            with mock.patch("kis_bot_multi.cancel_order") as mock_cancel:
                                with mock.patch("kis_bot_multi.rebalance_account") as mock_reb:
                                    with mock.patch("kis_bot_multi.send_telegram") as mock_tel:
                                        with mock.patch.object(sys, "argv", ["kis_bot_multi.py"]):
                                            with mock.patch.dict(os.environ, {"GITHUB_EVENT_NAME": "schedule", "KIS_PENSION_CANO": "12345678"}):
                                                kis_bot_multi._RUN_COMPLETED = False
                                                kis_bot_multi.main()
                                                assert kis_bot_multi._RUN_COMPLETED
                                                assert mock_cancel.call_count == 0, f"Expected 0 cancel_order calls outside trading window, got {mock_cancel.call_count}"
                                                assert mock_reb.call_count == 0, f"Expected 0 rebalance_account calls, got {mock_reb.call_count}"
                                                assert mock_tel.call_count == 1, f"Expected exactly 1 alert, got {mock_tel.call_count}"
                                                sent_msg = mock_tel.call_args[0][0]
                                                assert "거래창 밖 기동" in sent_msg and "미완료 계좌" in sent_msg, f"Unexpected message: {sent_msg}"
    print("✅ [Test 7 / T-D 통과] 장후 묵은 미체결 잔존 시 ➔ cancel_order 0회(부작용 없음) 및 텔레그램 1통 발송 보장!")

    print("\n🎉 모든 T-A, T-B, T-C, T-D 4대 회귀 시나리오 100% All Green 통과!")


def test_check_only_last_business_day():
    print("\n🧪 [Test 8] Testing --check-only on scheduled non-last business day (Sep 28, Mon) ➔ Silent skip...")
    mon_dt = dt.datetime(2026, 9, 28, 14, 0, tzinfo=KST)
    with mock.patch("kis_bot_multi.now_kst", return_value=mon_dt):
        with mock.patch.object(sys, "argv", ["kis_bot_multi.py", "--check-only"]):
            with mock.patch.dict(os.environ, {"GITHUB_EVENT_NAME": "schedule"}):
                with mock.patch("kis_bot_multi.send_telegram") as mock_tel:
                    kis_bot_multi._RUN_COMPLETED = False
                    kis_bot_multi.main()
                    assert kis_bot_multi._RUN_COMPLETED, "Should complete run"
                    assert mock_tel.call_count == 0, f"Expected 0 alerts on non-last day, got {mock_tel.call_count}"
    print("✅ [Test 8 통과] 25~31일 중 마지막 영업일이 아닌 날에는 텔레그램 0통 완벽 무소음 대기!")

    print("\n🧪 [Test 9] Testing --check-only on scheduled last business day (Sep 30, Wed) ➔ Exactly 1 alert...")
    wed_dt = dt.datetime(2026, 9, 30, 14, 0, tzinfo=KST)
    with mock.patch("kis_bot_multi.now_kst", return_value=wed_dt):
        with mock.patch.object(sys, "argv", ["kis_bot_multi.py", "--check-only"]):
            with mock.patch.dict(os.environ, {"GITHUB_EVENT_NAME": "schedule", "KIS_PENSION_CANO": "12345678"}):
                with mock.patch("kis_bot_multi.calculate_momentum_signals", return_value=({"069500": 1.0}, "테스트")):
                    with mock.patch("kis_bot_multi.fetch_prices", return_value={"069500": 35000}):
                        with mock.patch("kis_bot_multi.check_already_rebalanced_today",
                                        return_value=(True, "[연금저축계좌] 당월 완료 (현금 0.77%)", False)):
                            with mock.patch("kis_bot_multi.send_telegram") as mock_tel:
                                kis_bot_multi._RUN_COMPLETED = False
                                kis_bot_multi.main()
                                assert kis_bot_multi._RUN_COMPLETED
                                assert mock_tel.call_count == 1, f"Expected 1 alert on last business day, got {mock_tel.call_count}"
                                sent_msg = mock_tel.call_args[0][0]
                                assert "월말 결산 생존 점검 (30일)" in sent_msg, f"Unexpected message: {sent_msg}"
    print("✅ [Test 9 통과] 당월 마지막 영업일에는 정확히 1회의 결산 점검 리포트 발송 보장!")

    print("\n🧪 [Test 10] Testing --check-only manual workflow_dispatch bypass (Sep 28, Mon) ➔ 1 alert...")
    with mock.patch("kis_bot_multi.now_kst", return_value=mon_dt):
        with mock.patch.object(sys, "argv", ["kis_bot_multi.py", "--check-only"]):
            with mock.patch.dict(os.environ, {"GITHUB_EVENT_NAME": "workflow_dispatch", "KIS_PENSION_CANO": "12345678"}):
                with mock.patch("kis_bot_multi.calculate_momentum_signals", return_value=({"069500": 1.0}, "테스트")):
                    with mock.patch("kis_bot_multi.fetch_prices", return_value={"069500": 35000}):
                        with mock.patch("kis_bot_multi.check_already_rebalanced_today",
                                        return_value=(True, "[연금저축계좌] 당월 완료", False)):
                            with mock.patch("kis_bot_multi.send_telegram") as mock_tel:
                                kis_bot_multi._RUN_COMPLETED = False
                                kis_bot_multi.main()
                                assert kis_bot_multi._RUN_COMPLETED
                                assert mock_tel.call_count == 1, f"Expected 1 alert on manual trigger, got {mock_tel.call_count}"
    print("✅ [Test 10 통과] 사용자가 웹에서 수동으로 'Check Only' 실행 시 날짜와 상관없이 즉시 1회 보고서 발송!")


if __name__ == "__main__":
    test_main_modes()
    test_delayed_cron_scenarios()
    test_stale_order_scenarios()
    test_check_only_last_business_day()
