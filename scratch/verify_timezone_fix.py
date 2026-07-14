import sys
import os
import datetime

# Add the workspace directory to path to import kis_bot_multi
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import kis_bot_multi

def test_timezone_fix():
    print("Testing Timezone Fix in kis_bot_multi.py...")
    
    # 1. Test timezone-aware datetime now in KST
    kst_tz = datetime.timezone(datetime.timedelta(hours=9))
    now_kst = datetime.datetime.now(kst_tz)
    print(f"Current Time in KST: {now_kst}")
    print(f"Current Time in UTC: {datetime.datetime.utcnow()}")
    
    # 2. Test is_market_open()
    market_open = kis_bot_multi.is_market_open()
    print(f"is_market_open() returned: {market_open}")
    
    # 3. Test get_actual_rebalance_date
    today_kst = datetime.datetime.now(kst_tz).date()
    rebalance_date = kis_bot_multi.get_actual_rebalance_date(today_kst.year, today_kst.month)
    print(f"Today (KST): {today_kst}")
    print(f"Rebalance date (KST): {rebalance_date}")
    print(f"Is today the rebalance date? {today_kst == rebalance_date}")
    
    # Assert check
    assert market_open == True, "Error: Market should be open right now (between 09:00 and 15:30 KST)!"
    assert today_kst == rebalance_date, "Error: Today is June 17, 2026, which should be the actual rebalance date!"
    
    print("\n✅ Verification Successful! Timezone logic works perfectly.")

if __name__ == "__main__":
    try:
        test_timezone_fix()
    except AssertionError as ae:
        print(f"❌ Verification Failed: {ae}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error during verification: {e}")
        sys.exit(1)
