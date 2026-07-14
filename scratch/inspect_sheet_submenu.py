import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        print("Opening Google Sheet...")
        await page.goto("https://docs.google.com/spreadsheets/d/1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU/edit?usp=sharing", wait_until="domcontentloaded")
        
        print("Waiting 10 seconds for content to load...")
        await page.wait_for_timeout(10000)
        
        # Click on '도구' menu
        print("Clicking on '도구' menu...")
        await page.click("#docs-tools-menu")
        await page.wait_for_timeout(1000)
        
        # Hover over '양식 관리(M)'
        print("Hovering over '양식 관리(M)'...")
        # We can find it by text '양식 관리'
        try:
            await page.locator("text=/양식 관리/").first.hover()
            print("Hovered successfully!")
        except Exception as e:
            print("Failed to hover by text, trying to find element and hover:", e)
            # Find the menuitem with aria-haspopup="true" and text containing '양식 관리'
            el = page.locator(".goog-menuitem:has-text('양식 관리')")
            await el.first.hover()
            print("Hovered by selector!")
            
        # Wait 2 seconds for submenu to open
        await page.wait_for_timeout(2000)
        
        # Save screenshot
        await page.screenshot(path="scratch/submenu_screenshot.png")
        print("Screenshot of submenu saved to scratch/submenu_screenshot.png")
        
        # Print all menu items currently in the DOM containing '설문지' or '양식' or '보기'
        menu_items = await page.locator(".goog-menuitem").all()
        print(f"Found {len(menu_items)} menu items in DOM after hover:")
        for idx, item in enumerate(menu_items):
            try:
                text = await item.text_content()
                outer_html = await item.evaluate("el => el.outerHTML")
                # print any items that are visible or have relevant text
                if any(kw in text for kw in ['설문지', '양식', '실시간', '보기', '수정', '수행']):
                    print(f"  Item {idx}: text='{text.strip()}'")
                    print(f"    HTML: {outer_html[:150]}")
            except Exception as e:
                pass
                
        await browser.close()

asyncio.run(main())
