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
        await page.locator("text=/양식 관리/").first.hover()
        await page.wait_for_timeout(1000)
        
        # We expect a new page to open when we click "현재 설문지로 이동(G)"
        print("Clicking '현재 설문지로 이동(G)' and waiting for popup...")
        try:
            async with context.expect_page() as new_page_info:
                await page.click("text=/현재 설문지로 이동/")
            new_page = await new_page_info.value
            await new_page.wait_for_load_state("domcontentloaded")
            print("Successfully opened live form page!")
            print("Form URL:", new_page.url)
            
            # Save screenshot of the form
            await new_page.screenshot(path="scratch/form_screenshot.png")
            print("Screenshot of form saved to scratch/form_screenshot.png")
            
            # Save form page source
            form_html = await new_page.content()
            with open("scratch/form.html", "w", encoding="utf-8") as f:
                f.write(form_html)
            print("Form HTML source saved to scratch/form.html")
            
        except Exception as e:
            print("Error clicking or opening popup:", e)
            
        await browser.close()

asyncio.run(main())
