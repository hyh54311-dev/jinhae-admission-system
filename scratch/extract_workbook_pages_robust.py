import os
import sys
import time
import re
from playwright.sync_api import sync_playwright

def main():
    login_url = "https://aimyai.net/login/9/"
    screenshot_dir = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    username = "trust_ai"
    password = "dong001!!"
    
    print("Launching browser in headful/headless mode...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"Navigating directly to login page: {login_url}")
        page.goto(login_url)
        page.wait_for_load_state("networkidle")
        
        # Wait for input fields to be visible
        print("Waiting for input fields...")
        page.wait_for_selector("input[placeholder='ID 입력']", timeout=15000)
        
        # Fill inputs
        page.fill("input[placeholder='ID 입력']", username)
        page.fill("input[placeholder='비밀번호 입력']", password)
        print("Filled credentials successfully.")
        
        # Click login button
        print("Clicking login button...")
        page.click("button:has-text('로그인')")
        
        # Wait for navigation to dashboard
        print("Waiting for dashboard navigation...")
        time.sleep(5)
        page.wait_for_load_state("networkidle")
        print(f"Dashboard URL: {page.url}")
        
        # Wait for "최근 워크북 열기" button to be visible
        print("Waiting for '최근 워크북 열기' button...")
        page.wait_for_selector("button:has-text('최근 워크북 열기')", timeout=15000)
        
        # Click it
        print("Clicking '최근 워크북 열기'...")
        page.click("button:has-text('최근 워크북 열기')")
        
        # Wait for page load
        print("Waiting for workbook page to load...")
        time.sleep(8)
        page.wait_for_load_state("networkidle")
        print(f"Current page URL: {page.url}")
        
        # Take page screenshot to verify
        page.screenshot(path=os.path.join(screenshot_dir, "workbook_loaded_debug.png"))
        
        # Locate the iframe
        print("Locating iframe...")
        wb_frame = None
        for f in page.frames:
            print(f"  Frame URL: {f.url}")
            if "rootsall.net" in f.url:
                wb_frame = f
                break
                
        if not wb_frame:
            print("rootsall.net iframe not found. Trying to locate iframe by ID selector...")
            iframe_elem = page.query_selector("iframe")
            if iframe_elem:
                wb_frame = iframe_elem.content_frame()
                print(f"Found iframe content frame by tag: {wb_frame.url if wb_frame else 'None'}")
                
        if not wb_frame:
            print("ERROR: Could not locate workbook iframe.")
            browser.close()
            return
            
        print(f"Workbook iframe located: {wb_frame.url}")
        
        # Define the tab texts to click
        tabs = [
            "1차시: 데이터로 만드는 AI",
            "1차시 학습 정리",
            "2차시: 데이터의 배신",
            "2차시 학습 정리",
            "3차시: AI가 넘으면 안되는 선",
            "3차시 학습 정리"
        ]
        
        for idx, tab_name in enumerate(tabs):
            print(f"\n=== Navigating to Tab {idx+1}: {tab_name} ===")
            
            # Locate tab inside the iframe
            # Wait for selector inside the frame
            try:
                # Find elements containing tab text inside the frame
                # Roots workbook menu elements are often inside a specific class
                locator = wb_frame.locator(f"div:has-text('{tab_name}')").first
                if locator.count() == 0:
                    locator = wb_frame.locator(f"text='{tab_name}'").first
                    
                print(f"Clicking locator for tab '{tab_name}'...")
                locator.click()
                time.sleep(4)  # wait for page render
                
                # Take screenshot of the workbook area or the whole page
                screenshot_path = os.path.join(screenshot_dir, f"workbook_page_{idx+1}.png")
                page.screenshot(path=screenshot_path)
                print(f"Saved page screenshot to {screenshot_path}")
                
                # Save frame HTML
                html_path = os.path.join(screenshot_dir, f"workbook_page_{idx+1}.html")
                with open(html_path, "w", encoding="utf-8") as f_html:
                    f_html.write(wb_frame.content())
                print(f"Saved frame HTML to {html_path}")
                
            except Exception as e:
                print(f"Error processing tab {tab_name}: {e}")
                # Take a debug screenshot
                page.screenshot(path=os.path.join(screenshot_dir, f"error_tab_{idx+1}.png"))
                
        print("\nAll 6 pages extracted successfully!")
        browser.close()

if __name__ == '__main__':
    main()
