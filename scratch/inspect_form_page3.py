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
        
        print("Opening Google Form...")
        await page.goto("https://docs.google.com/forms/d/e/1FAIpQLSdWxHFRnWOX6AhXP0SHOhisykHsr-_cNcm1iT8HNsFKNTJ_xA/viewform", wait_until="domcontentloaded")
        
        await page.wait_for_timeout(3000)
        
        # Select 4반 and click Next
        print("Selecting '4반'...")
        await page.click("text='4반'")
        await page.wait_for_timeout(1000)
        
        print("Clicking '다음'...")
        await page.click("text='다음'")
        await page.wait_for_timeout(3000)
        
        # Now on page 2. Let's see the radio buttons
        radios = await page.locator("[role='radio']").all()
        print(f"\nFound {len(radios)} radio buttons on Page 2:")
        for idx, r in enumerate(radios):
            label = await r.get_attribute("aria-label")
            text = await r.evaluate("el => el.textContent")
            print(f"  Radio {idx}: label={label}, text={text.strip()}")
            
        # Let's select '20번 이승우'
        print("Selecting '20번 이승우'...")
        await page.click("text='20번 이승우'")
        await page.wait_for_timeout(1000)
        
        # Click Next
        print("Clicking '다음' to go to Page 3...")
        await page.click("text='다음'")
        await page.wait_for_timeout(3000)
        
        print("Navigated to Page 3!")
        await page.screenshot(path="scratch/form_page3_screenshot.png")
        print("Screenshot of Page 3 saved to scratch/form_page3_screenshot.png")
        
        # Print headings on Page 3
        headings = await page.locator("[role='heading']").all()
        print(f"\nFound {len(headings)} headings on Page 3:")
        for idx, h in enumerate(headings):
            text = await h.text_content()
            print(f"  Heading {idx}: {text.strip()}")
            
        # Print textareas and inputs on Page 3
        # Google Forms short answer is usually input[type='text'], paragraph answer is textarea
        textareas = await page.locator("textarea").all()
        print(f"\nFound {len(textareas)} textareas on Page 3:")
        for idx, ta in enumerate(textareas):
            # Try to get question label
            # Google Forms questions usually have aria-label or aria-labelledby
            label = await ta.get_attribute("aria-label")
            print(f"  Textarea {idx}: label={label}")
            
        text_inputs = await page.locator("input[type='text']").all()
        print(f"\nFound {len(text_inputs)} text inputs on Page 3:")
        for idx, ti in enumerate(text_inputs):
            label = await ti.get_attribute("aria-label")
            print(f"  Input {idx}: label={label}")
            
        # Let's see all visible labels/texts to find the question names
        questions = await page.locator("[role='heading']").all()
        
        await browser.close()

asyncio.run(main())
