import os
import sys
import time
from playwright.sync_api import sync_playwright

def main():
    login_url = "https://aimyai.net/login/9/"
    screenshot_dir = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # Using the test account to prevent session conflicts
    username = "t_trust_ai"
    password = "dong001!!"
    
    print("Launching browser in headless mode...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"Navigating to login page: {login_url}")
        page.goto(login_url)
        page.wait_for_load_state("networkidle")
        
        # Wait for input fields to be visible
        print("Waiting for ID input field...")
        page.wait_for_selector("input[placeholder='ID 입력']", timeout=15000)
        
        # Fill inputs
        page.fill("input[placeholder='ID 입력']", username)
        page.fill("input[placeholder='비밀번호 입력']", password)
        print("Credentials entered.")
        
        # Click login button
        print("Clicking login button...")
        page.click("button:has-text('로그인')")
        
        # Wait for navigation to dashboard
        print("Waiting for dashboard navigation...")
        time.sleep(5)
        page.wait_for_load_state("networkidle")
        print(f"Dashboard URL: {page.url}")
        
        # Wait for "최근 워크북 열기" button
        print("Waiting for '최근 워크북 열기' button...")
        page.wait_for_selector("button:has-text('최근 워크북 열기')", timeout=15000)
        
        # Click it
        print("Opening workbook...")
        page.click("button:has-text('최근 워크북 열기')")
        
        # Wait for page load
        print("Waiting for workbook page to stabilize...")
        time.sleep(8)
        page.wait_for_load_state("networkidle")
        print(f"Workbook URL: {page.url}")
        
        # Locate the iframe
        print("Locating rootsall.net iframe...")
        wb_frame = None
        for f in page.frames:
            if "rootsall.net" in f.url:
                wb_frame = f
                break
                
        if not wb_frame:
            print("rootsall.net iframe not found. Trying tag fallback...")
            iframe_elem = page.query_selector("iframe")
            if iframe_elem:
                wb_frame = iframe_elem.content_frame()
                
        if not wb_frame:
            print("ERROR: Could not locate workbook iframe.")
            browser.close()
            return
            
        print(f"Workbook iframe URL: {wb_frame.url}")
        
        # Wait for sidebar tabs to load inside the iframe
        print("Waiting for sidebar tabs to become visible inside iframe...")
        sidebar_tabs_selector = "div.grow.overflow-y-auto div.cursor-pointer"
        try:
            wb_frame.locator(sidebar_tabs_selector).first.wait_for(state="visible", timeout=30000)
            print("Sidebar tabs loaded successfully.")
        except Exception as e:
            print(f"Error waiting for sidebar tabs: {e}")
            page.screenshot(path=os.path.join(screenshot_dir, "error_loading_iframe.png"))
            browser.close()
            return
            
        # We will loop exactly 6 times corresponding to the 6 tabs
        for idx in range(6):
            print(f"\n=== Navigating to Tab {idx+1} ===")
            
            try:
                # Target the tab locator by index
                locator = wb_frame.locator(sidebar_tabs_selector).nth(idx)
                
                # Retrieve the text content for logging
                tab_text = locator.inner_text()
                tab_text_clean = " ".join(tab_text.split())
                print(f"Found tab text: '{tab_text_clean}'")
                
                print(f"Clicking tab {idx+1}...")
                locator.click()
                
                # Wait for content to render
                time.sleep(5)
                
                # Take page screenshot
                screenshot_path = os.path.join(screenshot_dir, f"workbook_page_{idx+1}.png")
                page.screenshot(path=screenshot_path)
                print(f"Saved screenshot: {screenshot_path}")
                
                # Save frame HTML
                html_path = os.path.join(screenshot_dir, f"workbook_page_{idx+1}.html")
                with open(html_path, "w", encoding="utf-8") as f_html:
                    f_html.write(wb_frame.content())
                print(f"Saved HTML content: {html_path}")
                
            except Exception as e:
                print(f"Error navigating to tab {idx+1}: {e}")
                err_screenshot = os.path.join(screenshot_dir, f"error_tab_{idx+1}.png")
                page.screenshot(path=err_screenshot)
                print(f"Saved error screenshot: {err_screenshot}")
                
        print("\nWorkbook pages extraction complete!")
        browser.close()

if __name__ == '__main__':
    main()
