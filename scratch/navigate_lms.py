import os
import sys
import time
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
        print(f"Logged in successfully. Current URL: {page.url}")
        
        # Click "최근 워크북 열기"
        print("Looking for '최근 워크북 열기' button...")
        buttons = page.query_selector_all("button")
        target_btn = None
        for btn in buttons:
            txt = btn.inner_text().strip()
            if "최근 워크북 열기" in txt or "최근" in txt or "워크북" in txt:
                target_btn = btn
                print(f"Found button: '{txt}'")
                break
                
        if target_btn:
            print("Clicking '최근 워크북 열기'...")
            target_btn.click()
            time.sleep(5)
            page.wait_for_load_state("networkidle")
            print(f"URL after clicking: {page.url}")
            page.screenshot(path=os.path.join(screenshot_dir, "lms_workbook.png"))
            with open(os.path.join(screenshot_dir, "lms_workbook.html"), "w", encoding="utf-8") as f:
                f.write(page.content())
            print("Saved workbook page screenshot and HTML.")
        else:
            print("Button '최근 워크북 열기' not found on the page.")
            
        browser.close()

if __name__ == '__main__':
    main()
