import os
import sys
import time
from playwright.sync_api import sync_playwright

def main():
    url = "https://aimyai.net/sns"
    screenshot_dir = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # Credentials provided by user
    username = "trust_ai"
    password = "dong001!!"
    
    print("Launching browser...")
    with sync_playwright() as p:
        # Launching headless=True (or False if we want to run visually, but headless=True is fine since we take screenshots)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"Navigating to {url}...")
        page.goto(url)
        time.sleep(5)
        page.wait_for_load_state("networkidle")
        print(f"Stabilized URL: {page.url}")
        
        # Fill credentials
        print("Filling login form...")
        # Target input fields by index or query selector
        inputs = page.query_selector_all("input")
        if len(inputs) >= 2:
            inputs[0].fill(username)
            inputs[1].fill(password)
            print("Credentials filled successfully.")
        else:
            # Fallback using get_by_placeholder
            try:
                page.get_by_placeholder("ID 입력").fill(username)
                page.get_by_placeholder("비밀번호 입력").fill(password)
                print("Credentials filled via placeholder.")
            except Exception as fe:
                print(f"Failed to fill credentials: {fe}")
                browser.close()
                return
                
        # Take a screenshot before clicking login
        page.screenshot(path=os.path.join(screenshot_dir, "lms_before_login.png"))
        
        # Click login button
        print("Clicking login button...")
        buttons = page.query_selector_all("button")
        login_btn = None
        for btn in buttons:
            txt = btn.inner_text().strip()
            if "로그인" in txt or "로그" in txt or "α" in txt:
                login_btn = btn
                break
        if not login_btn and len(buttons) > 0:
            login_btn = buttons[0]
            
        if login_btn:
            login_btn.click()
            print("Login button clicked. Waiting for navigation/stabilization...")
            time.sleep(7) # Wait for page load after login
            page.wait_for_load_state("networkidle")
        else:
            print("Login button not found.")
            browser.close()
            return
            
        print(f"Current URL after login: {page.url}")
        screenshot_path = os.path.join(screenshot_dir, "lms_dashboard.png")
        page.screenshot(path=screenshot_path)
        print(f"Dashboard screenshot saved to {screenshot_path}")
        
        # Save dashboard HTML
        html_path = os.path.join(screenshot_dir, "lms_dashboard.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page.content())
        print(f"Dashboard HTML saved to {html_path}")
        
        browser.close()

if __name__ == '__main__':
    main()
