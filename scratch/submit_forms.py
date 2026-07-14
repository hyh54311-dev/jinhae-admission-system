import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Student data to submit
students_data = [
    {
        'class': '4반',
        'name_label': '20번 이승우',
        'answers': [
            '의도하지 않은 상태에서 탐구 목적과는 관계없이 우연적으로 이루어진 발견이 엄청난 의미를 가지고 있음이 드러났을 때이다.', # 16번
            '플레밍', # 17번
            '페니실린이 불안정하고 박테리아를 죽이는 데 즉각적이지 않기 때문이다.', # 18번
            '페이니실의 베타-락탐이 박테리아의 트랜스텝디데이스와 결합해 세포벽을 약화시킨다.', # 19번
            '그람 양성균에 없는 박테리아 외막 구조가 있기 때문이다.' # 20번
        ]
    },
    {
        'class': '5반',
        'name_label': '19번 이요한',
        'answers': [
            '과학에서 의도하지 않은 상태에서 탐구 목적과는 상관없이 우연적으로 이루어진 발견이 엄청난 의미를 가지고 있음이 드러냈을 때 그 발견', # 16번
            '플레밍', # 17번
            '페이실린이 불안정하고 박테리아를 죽이는데 즉각적이지 않다는 점 때문. 당신는 감염병을 해결하기 위해 백신을 활용하는 것이 각광 받았기 때문', # 18번
            ' ', # 19번 (서술 안함)
            ' '  # 20번 (서술 안함)
        ]
    },
    {
        'class': '10반',
        'name_label': '26번 최윤혁',
        'answers': [
            ' ', ' ', ' ', ' ', ' ' # All 서술 안함
        ]
    },
    {
        'class': '8반',
        'name_label': '3번 김도현',
        'answers': [
            ' ', ' ', ' ', ' ', ' ' # All 서술 안함
        ]
    },
    {
        'class': '8반',
        'name_label': '1번 강수민',
        'answers': [
            ' ', ' ', ' ', ' ', ' ' # All 서술 안함
        ]
    }
]

async def submit_student(context, student):
    print(f"\n--- Submitting for {student['class']} {student['name_label']} ---")
    page = await context.new_page()
    
    try:
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
            ans = student['answers'][i]
            # If answer is '서술 안함', we use a single space
            if ans.strip() == "" or "서술 안함" in ans:
                ans = " "
            await textareas[i].fill(ans)
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
            # Save screenshot of confirmation
            await page.screenshot(path=f"scratch/confirm_{student['name_label']}.png")
        else:
            print(f"WARNING: Submission confirmation text not found for {student['name_label']}, please check screenshot.")
            await page.screenshot(path=f"scratch/error_{student['name_label']}.png")
            
    except Exception as e:
        print(f"ERROR submitting for {student['name_label']}: {e}")
        # Save error screenshot
        try:
            await page.screenshot(path=f"scratch/error_{student['name_label']}.png")
        except:
            pass
    finally:
        await page.close()

async def main():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            ignore_https_errors=True
        )
        
        for student in students_data:
            await submit_student(context, student)
            await asyncio.sleep(2) # brief delay between submissions
            
        await browser.close()

asyncio.run(main())
