import os
import sys
import time
from playwright.sync_api import sync_playwright

def main():
    url = "https://aimyai.net/sns"
    screenshot_dir = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    print("Launching browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"Navigating to {url}...")
        try:
            page.goto(url)
            # Wait for 5 seconds to let any redirects stabilize
            print("Waiting for page redirect stabilization...")
            time.sleep(5)
            page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"Navigation or wait failed: {e}")
            
        print(f"Stabilized URL: {page.url}")
        
        # Save HTML source before click
        with open(os.path.join(screenshot_dir, "lms_stabilized.html"), "w", encoding="utf-8") as f:
            f.write(page.content())
            
        # Check for iframes
        print(f"Total frames: {len(page.frames)}")
        for idx, f in enumerate(page.frames):
            print(f"  Frame [{idx}] Name: {f.name} | URL: {f.url}")
            
        # Let's check buttons on page or inside frames
        buttons = page.query_selector_all("button")
        print(f"Found {len(buttons)} buttons on stabilized page:")
        login_btn = None
        for idx, btn in enumerate(buttons):
            txt = btn.inner_text().strip()
            print(f"  [{idx}] Button text: '{txt}'")
            if "로그인" in txt or "로그" in txt or "α" in txt:
                login_btn = btn
                
        # Let's check input fields
        inputs = page.query_selector_all("input")
        print(f"Found {len(inputs)} input fields on stabilized page:")
        for idx, inp in enumerate(inputs):
            name = inp.get_attribute("name")
            id_attr = inp.get_attribute("id")
            type_attr = inp.get_attribute("type")
            placeholder = inp.get_attribute("placeholder")
            print(f"  [{idx}] Type: {type_attr} | Name: {name} | ID: {id_attr} | Placeholder: {placeholder}")
            
        if login_btn:
            print("Clicking the login button...")
            login_btn.click()
            time.sleep(3)  # Wait for modal or page load
            print(f"URL after clicking login: {page.url}")
            page.screenshot(path=os.path.join(screenshot_dir, "lms_after_login_click.png"))
            
            # Print input fields after login button click
            inputs_after = page.query_selector_all("input")
            print(f"Found {len(inputs_after)} input fields after click:")
            for idx, inp in enumerate(inputs_after):
                name = inp.get_attribute("name")
                id_attr = inp.get_attribute("id")
                type_attr = inp.get_attribute("type")
                placeholder = inp.get_attribute("placeholder")
                print(f"  [{idx}] Type: {type_attr} | Name: {name} | ID: {id_attr} | Placeholder: {placeholder}")
                
        else:
            print("Login button not found by text.")
            page.screenshot(path=os.path.join(screenshot_dir, "lms_stabilized.png"))
            
        browser.close()

if __name__ == '__main__':
    main()
