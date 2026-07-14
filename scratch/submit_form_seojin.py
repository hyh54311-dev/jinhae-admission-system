import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

student = {
    'class': '7반',
    'name_label': '11번 박서진',
    'answers': [
        '의도하지 않은 상태에서 탐구 목적과는 관계없이 우연적으로 이루어진 발견이 엄청난 의미를 가지고 있음이 들어났을 때의 그 발견', # 16번
        '알렉산더 플레밍', # 17번
        '페니실린이 불안정하며, 박테리아를 죽이는 데 즉각적이지 않았으며 당시에는 감염병 해결을 위해 백신의 홀용이 더욱 각광받았기에 개발 동기가 약했다.', # 18번
        '페니실린의 베타-락탐이 박테리아의 세포벽 성분인 펩티도글리칸 분자를 형성하는 펩타이드 전이 효소와 임의로 결합하여 박테리아의 세포벽을 약화시키고, 박테리아는 터져 죽게 된다.', # 19번
        '그람 양성균에 없는 박테리아 외막 구조가 있기 때문이다.' # 20번
    ]
}

async def main():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        try:
            print(f"\n--- Submitting for {student['class']} {student['name_label']} ---")
            # 1. Open form
            await page.goto("https://docs.google.com/forms/d/e/1FAIpQLSdWxHFRnWOX6AhXP0SHOhisykHsr-_cNcm1iT8HNsFKNTJ_xA/viewform", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)
            
            # 2. Select Class
            print(f"Selecting class: {student['class']}")
            await page.click(f"text='{student['class']}'")
            await page.wait_for_timeout(500)
            
            # Click Next
            await page.click("text='다음'")
            await page.wait_for_timeout(2000)
            
            # 3. Select Name
            print(f"Selecting name: {student['name_label']}")
            await page.click(f"text='{student['name_label']}'")
            await page.wait_for_timeout(500)
            
            # Click Next
            await page.click("text='다음'")
            await page.wait_for_timeout(2000)
            
            # 4. Fill answers on page 3
            textareas = await page.locator("textarea").all()
            if len(textareas) < 5:
                raise Exception(f"Expected 5 textareas, but found {len(textareas)} on page 3")
                
            print("Filling answers...")
            for i in range(5):
                await textareas[i].fill(student['answers'][i])
                await page.wait_for_timeout(200)
                
            # Click Submit (제출)
            print("Clicking Submit (제출)...")
            await page.click("text='제출'")
            
            # Wait for confirmation page
            print("Waiting for confirmation...")
            await page.wait_for_timeout(5000)
            
            # Verify submission by checking page content or url
            content = await page.content()
            if "응답이 기록되었습니다" in content or "제출" in await page.title() or "응답" in await page.title():
                print(f"SUCCESS: Submitted successfully for {student['class']} {student['name_label']}!")
                await page.screenshot(path=f"scratch/confirm_{student['name_label']}.png")
            else:
                print(f"WARNING: Submission confirmation text not found for {student['name_label']}, please check screenshot.")
                await page.screenshot(path=f"scratch/error_{student['name_label']}.png")
                
        except Exception as e:
            print(f"ERROR submitting for {student['name_label']}: {e}")
            try:
                await page.screenshot(path=f"scratch/error_{student['name_label']}.png")
            except:
                pass
        finally:
            await page.close()
            await browser.close()

asyncio.run(main())
