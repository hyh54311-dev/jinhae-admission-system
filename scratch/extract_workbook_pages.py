import os
import sys
import time
import re
from playwright.sync_api import sync_playwright

def main():
    url = "https://aimyai.net/sns"
    screenshot_dir = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    username = "trust_ai"
    password = "dong001!!"
    
    print("Launching browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print("Navigating and logging in...")
        page.goto(url)
        time.sleep(5)
        page.wait_for_load_state("networkidle")
        
        inputs = page.query_selector_all("input")
        if len(inputs) >= 2:
            inputs[0].fill(username)
            inputs[1].fill(password)
        else:
            page.get_by_placeholder("ID 입력").fill(username)
            page.get_by_placeholder("비밀번호 입력").fill(password)
            
        buttons = page.query_selector_all("button")
        login_btn = None
        for btn in buttons:
            txt = btn.inner_text().strip()
            if "로그인" in txt or "로그" in txt or "α" in txt:
                login_btn = btn
                break
        if not login_btn and len(buttons) > 0:
            login_btn = buttons[0]
            
        login_btn.click()
        time.sleep(7)
        page.wait_for_load_state("networkidle")
        print(f"Logged in. Current URL: {page.url}")
        
        # Click "최근 워크북 열기"
        buttons = page.query_selector_all("button")
        target_btn = None
        for btn in buttons:
            txt = btn.inner_text().strip()
            if "최근 워크북 열기" in txt or "최근" in txt or "워크북" in txt:
                target_btn = btn
                break
                
        if not target_btn:
            print("최근 워크북 열기 button not found.")
            browser.close()
            return
            
        print("Clicking '최근 워크북 열기'...")
        target_btn.click()
        time.sleep(10) # Wait for page and iframe to load
        page.wait_for_load_state("networkidle")
        print(f"Workbook URL: {page.url}")
        
        # Find the rootsall.net iframe
        print("Locating rootsall.net iframe...")
        wb_frame = None
        for f in page.frames:
            print(f"  Checking frame: Name='{f.name}', URL='{f.url}'")
            if "rootsall.net" in f.url:
                wb_frame = f
                print(f"--> Found matching iframe: {f.url}")
                break
                
        if not wb_frame:
            print("Failed to find rootsall.net iframe.")
            browser.close()
            return
            
        # Let's inspect the tabs inside the iframe
        # In the screenshot, we have 6 tabs:
        # "1 1차시: 데이터로 만드는 AI", "2 1차시 학습 정리", "3 2차시: 데이터의 배신", "4 2차시 학습 정리", "5 3차시: AI가 넘으면 안되는 선", "6 3차시 학습 정리"
        # Let's find them by text inside the iframe
        print("Scanning navigation elements inside iframe...")
        
        # Click each tab and capture screenshot + HTML
        tab_keywords = [
            "1차시: 데이터로 만드는 AI",
            "1차시 학습 정리",
            "2차시: 데이터의 배신",
            "2차시 학습 정리",
            "3차시: AI가 넘으면 안되는 선",
            "3차시 학습 정리"
        ]
        
        for idx, kw in enumerate(tab_keywords):
            print(f"\n--- Processing Tab {idx+1}: {kw} ---")
            
            # Find the tab element inside the iframe and click it
            # We can use frame.locator("text=" + kw) or select elements containing the text
            try:
                # Target the tab element containing the text
                tab_locator = wb_frame.locator(f"text={kw}")
                if tab_locator.count() > 0:
                    print(f"Clicking tab locator for '{kw}'...")
                    tab_locator.first.click()
                    time.sleep(5)  # Wait for content transition
                    
                    # Capture screenshot of the entire page showing the workbook
                    screenshot_path = os.path.join(screenshot_dir, f"workbook_page_{idx+1}.png")
                    page.screenshot(path=screenshot_path)
                    print(f"Saved screenshot to {screenshot_path}")
                    
                    # Save HTML of the iframe
                    html_path = os.path.join(screenshot_dir, f"workbook_page_{idx+1}.html")
                    with open(html_path, "w", encoding="utf-8") as f_html:
                        f_html.write(wb_frame.content())
                    print(f"Saved HTML to {html_path}")
                else:
                    print(f"Tab with text '{kw}' not found in iframe.")
                    # Try using a index based click if text is not clickable directly
                    # e.g., finding all divs on the left navigation and clicking the idx-th one
            except Exception as te:
                print(f"Error clicking tab {idx+1}: {te}")
                
        browser.close()

if __name__ == '__main__':
    main()
