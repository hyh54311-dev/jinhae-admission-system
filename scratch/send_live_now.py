# -*- coding: utf-8 -*-
"""
Fetch live KOSPI data and send a concise Telegram message directly from the agent sandbox.
Overrides the GAS proxy fetcher to connect directly to Naver Finance.
"""
import sys
import os
import requests

# Add root directory to python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(PARENT_DIR)

import kospi_investor_tracker

# Override proxy fetch with direct request (agent sandbox is not firewalled)
def fetch_direct(target_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Referer": "https://finance.naver.com/"
    }
    if target_url == "KOSPI_INVESTOR_MULTIPLE":
        combined_html = ""
        for page in range(1, 27):
            url = f"https://finance.naver.com/sise/investorDealTrendDay.nhn?sosok=KOSPI&page={page}"
            res = requests.get(url, headers=headers, verify=False, timeout=20)
            res.raise_for_status()
            combined_html += res.text + "\n"
        return combined_html
        
    res = requests.get(target_url, headers=headers, verify=False, timeout=20)
    res.raise_for_status()
    return res.text

# Apply override
kospi_investor_tracker.fetch_html_via_gas = fetch_direct

if __name__ == "__main__":
    print("수집 및 실시간 텔레그램 발송 시작...")
    # Run in test mode to bypass early-exit check in case today's market is closed or not open yet
    sys.argv = [sys.argv[0], "--test"]
    kospi_investor_tracker.main()
    print("발송 완료.")
