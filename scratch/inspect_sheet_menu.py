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
        
        # Wait 2 seconds for menu to open
        await page.wait_for_timeout(2000)
        
        # Take a screenshot of the menu
        await page.screenshot(path="scratch/menu_screenshot.png")
        print("Screenshot of menu saved to scratch/menu_screenshot.png")
        
        # Search the DOM for menu items containing '설문지' or 'Form'
        menu_items = await page.locator(".goog-menuitem, .goog-menu, [role='menuitem']").all()
        print(f"Found {len(menu_items)} menu items/menus")
        for idx, item in enumerate(menu_items):
            try:
                text = await item.text_content()
                outer_html = await item.evaluate("el => el.outerHTML")
                if '설문지' in text or 'Form' in text or '양식' in text:
                    print(f"  Item {idx}: text={text.strip()}")
                    print(f"    HTML: {outer_html[:200]}")
            except Exception as e:
                pass
                
        await browser.close()

asyncio.run(main())
