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
        
        # Wait for form to render
        await page.wait_for_timeout(3000)
        print("Page title:", await page.title())
        
        # Print class options
        radios = await page.locator("[role='radio']").all()
        print(f"Found {len(radios)} radio buttons on page 1:")
        for idx, r in enumerate(radios):
            label = await r.get_attribute("aria-label")
            text = await r.evaluate("el => el.textContent")
            print(f"  Radio {idx}: label={label}, text={text.strip()}")
            
        # Let's select '4반' (assuming it has text '4반')
        print("Selecting '4반'...")
        # Try clicking element with text='4반'
        await page.click("text='4반'")
        await page.wait_for_timeout(1000)
        
        # Click Next
        print("Clicking '다음' (Next)...")
        await page.click("text='다음'")
        await page.wait_for_timeout(3000)
        
        print("Navigated to page 2!")
        await page.screenshot(path="scratch/form_page2_screenshot.png")
        print("Screenshot of page 2 saved to scratch/form_page2_screenshot.png")
        
        # Print headings on page 2
        headings = await page.locator("[role='heading']").all()
        print(f"\nFound {len(headings)} headings on page 2:")
        for idx, h in enumerate(headings):
            text = await h.text_content()
            print(f"  Heading {idx}: {text.strip()}")
            
        # Print buttons on page 2
        buttons = await page.locator("[role='button']").all()
        print(f"\nFound {len(buttons)} buttons on page 2:")
        for idx, b in enumerate(buttons):
            text = await b.text_content()
            print(f"  Button {idx}: {text.strip()}")
            
        # Print input fields / textareas / dropdowns on page 2
        dropdowns = await page.locator("[role='listbox']").all()
        print(f"\nFound {len(dropdowns)} dropdowns (listboxes) on page 2:")
        for idx, d in enumerate(dropdowns):
            label = await d.get_attribute("aria-label")
            text = await d.text_content()
            print(f"  Dropdown {idx}: label={label}, text={text.strip()}")
            
        # Search for text inputs (usually input[type='text'] or textarea)
        text_inputs = await page.locator("input[type='text'], textarea").all()
        print(f"\nFound {len(text_inputs)} text inputs/textareas on page 2:")
        for idx, ti in enumerate(text_inputs):
            label = await ti.get_attribute("aria-label")
            placeholder = await ti.get_attribute("placeholder")
            print(f"  Input {idx}: tag={await ti.evaluate('el => el.tagName')}, label={label}, placeholder={placeholder}")
            
        await browser.close()

asyncio.run(main())
