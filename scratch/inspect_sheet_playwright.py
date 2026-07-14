import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        # Add ignore_https_errors=True to handle SSL issues
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        print("Opening Google Sheet...")
        # Use default load (or load/domcontentloaded) instead of networkidle
        await page.goto("https://docs.google.com/spreadsheets/d/1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU/edit?usp=sharing", wait_until="domcontentloaded")
        
        print("Waiting 10 seconds for content to load...")
        await page.wait_for_timeout(10000)
        
        print("Page title:", await page.title())
        
        # Save screenshot
        await page.screenshot(path="scratch/sheet_screenshot.png")
        print("Screenshot saved to scratch/sheet_screenshot.png")
        
        # Search for form menus or buttons in DOM
        html = await page.content()
        print("HTML length:", len(html))
        
        # Find elements containing '설문지', 'Form', '도구', 'Tools'
        form_elements = await page.locator("text=/설문지|Form|form|도구|Tools/i").all()
        print(f"Found {len(form_elements)} elements containing target keywords")
        for idx, el in enumerate(form_elements[:20]):
            try:
                text = await el.text_content()
                tag = await el.evaluate("el => el.tagName")
                outer_html = await el.evaluate("el => el.outerHTML")
                if len(text.strip()) > 0:
                    print(f"  {idx}: tag={tag}, text={text.strip()[:100]}")
                    print(f"     HTML: {outer_html[:150]}")
            except Exception as e:
                pass
                
        # Let's search specifically for form links in any 'a' tags or elements
        print("\nSearching for links containing forms/d:")
        links = await page.locator("a").all()
        for idx, link in enumerate(links):
            try:
                href = await link.get_attribute("href")
                if href and 'forms' in href:
                    print(f"  Link: {href}")
            except Exception as e:
                pass
                
        await browser.close()

asyncio.run(main())
