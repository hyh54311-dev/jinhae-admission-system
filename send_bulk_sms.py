import os
import sys
import csv
import asyncio
from playwright.async_api import async_playwright

# Ensure UTF-8 console output
sys.stdout.reconfigure(encoding='utf-8')

CSV_PATH = r"C:\Users\admin\.gemini\antigravity\brain\48fcecfb-78c6-4a7f-a6c5-40fca9cea47b\scratch\sheet_content.csv"
CHROME_CDP_URL = "http://127.0.0.1:9222"

# Customize your message template here
MESSAGE_TEMPLATE = """[진해고등학교 입학홍보단 합격 및 소집 안내]

안녕하세요, {이름} 학생. 진해고등학교 입학홍보단 담당 교사입니다.

치열했던 지원 과정을 거쳐 2026학년도 진해고등학교 입학홍보단 최종 합격자로 선발된 것을 진심으로 축하합니다. 🎉

향후 상세 일정(오리엔테이션 및 활동 안내) 전달과 원활한 소통을 위해 입학홍보단 공식 오픈채팅방(단톡방)을 개설하였으니, 아래 링크를 통해 반드시 입장해 주기 바랍니다.

💬 공식 오픈채팅방 링크:
https://open.kakao.com/o/gVBn6Nwi

📌 입장 시 주의사항:
* 원활한 인원 확인을 위해 입장 시 프로필 닉네임을 반드시 '[ 학번 이름 ]' 형태로 설정해 주세요. (예: {학번} {이름})
* {이름} 학생은 오늘 중으로 입장을 완료해 주기 바랍니다.

진해고의 얼굴이자 대표로서 함께 멋진 활동을 만들어가길 기대합니다. 축하합니다!

- 진해고등학교 입학홍보단 담당 교사 올림 -"""

def load_accepted_students():
    accepted = []
    if not os.path.exists(CSV_PATH):
        raise Exception(f"Data file not found at {CSV_PATH}. Please make sure you have run the analyzer.")
        
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        
    for row in rows[1:]:
        if len(row) > 12:
            status = row[12].strip().upper()
            if status == 'O':
                student_id = row[1].strip()
                name = row[2].strip()
                phone = row[3].strip()
                # Clean phone number to 010-XXXX-XXXX format
                digits = "".join(c for c in phone if c.isdigit())
                if len(digits) == 10 and digits.startswith('10'):
                    phone_clean = f"010-{digits[2:6]}-{digits[6:]}"
                elif len(digits) == 11:
                    phone_clean = f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
                else:
                    phone_clean = phone
                
                accepted.append({
                    "id": student_id,
                    "name": name,
                    "phone": phone_clean
                })
    accepted.sort(key=lambda x: x["id"])
    return accepted

async def send_sms_automation():
    accepted_students = load_accepted_students()
    print(f"Loaded {len(accepted_students)} accepted students for SMS delivery.")
    
    async with async_playwright() as p:
        print(f"Connecting to running Chrome debug session at {CHROME_CDP_URL}...")
        try:
            browser = await p.chromium.connect_over_cdp(CHROME_CDP_URL)
        except Exception as e:
            print("\n[ERROR] Failed to connect to Chrome debug port 9222.")
            print("Please make sure you have:")
            print("1. Closed all regular Chrome windows completely.")
            print("2. Run 'Chrome_메인프로필_디버그.bat' in the workspace folder.")
            print("3. Logged in and paired Google Messages for Web.")
            print(f"Details: {e}")
            return
            
        contexts = browser.contexts
        if not contexts:
            print("[ERROR] No active browser contexts found in the debug session.")
            return
            
        context = contexts[0]
        # Check if Google Messages is already open in one of the active tabs
        page = None
        for p_tab in context.pages:
            if "messages.google.com" in p_tab.url:
                page = p_tab
                print("Found active Google Messages tab. Reusing it...")
                break
                
        if not page:
            page = await context.new_page()
            print("Opening Google Messages in a new tab...")
            await page.goto("https://messages.google.com/web", timeout=60000)
            
        # Check if paired
        print("Checking connection status. Please make sure your phone is paired.")
        await asyncio.sleep(5)
        
        is_qr_visible = await page.locator("mw-qr-code").count() > 0
        has_start_chat = await page.locator("[data-e2e-start-button]").count() > 0
        
        if is_qr_visible or not has_start_chat or "setup" in page.url:
            print("\n[WARNING] Google Messages is NOT paired with your phone in this Chrome window.")
            print("Please scan the QR code to pair your device, then try again.")
            return
        else:
            print("Phone pairing confirmed. Starting batch SMS delivery...")

        success_count = 0
        failed_students = []
        
        for idx, student in enumerate(accepted_students, 1):
            name = student["name"]
            phone = student["phone"]
            student_id = student["id"]
            
            # Format the message for this student
            message_text = MESSAGE_TEMPLATE.format(이름=name, 학번=student_id)
            
            print(f"\n[{idx}/{len(accepted_students)}] Sending message to {name} ({phone}, {student_id})...")
            print("=" * 60)
            print(message_text)
            print("=" * 60)
            
            try:
                # 1. Click "Start chat" button using robust data-e2e attribute
                start_chat_btn = page.locator("[data-e2e-start-button]").first
                await start_chat_btn.click()
                await asyncio.sleep(2)  # Wait for recipient input field to appear
                
                # 2. Find recipient input field using data-e2e attribute
                recipient_input = page.locator("[data-e2e-contact-input]").first
                if not await recipient_input.is_visible():
                    raise Exception("Could not locate the recipient input field.")
                    
                await recipient_input.fill(phone)
                await asyncio.sleep(2)  # Wait for dropdown "Send to..." button to appear
                
                # Click the dropdown button to actually open the chat room
                send_to_btn = page.locator("[data-e2e-send-to-button]").first
                if not await send_to_btn.is_visible():
                    raise Exception("Could not locate the 'Send to...' dropdown button.")
                await send_to_btn.click()
                await asyncio.sleep(4)  # Wait for chat window to load
                
                # 3. Locate text area to type message using data-e2e attribute
                message_box = page.locator("[data-e2e-message-input-box]").first
                if not await message_box.is_visible():
                    raise Exception("Could not locate the message input area.")
                    
                await message_box.focus()
                await message_box.fill(message_text)
                await asyncio.sleep(2)
                
                # 4. Click Send button using data-e2e attribute
                send_button = page.locator("[data-e2e-send-text-button]").first
                if await send_button.is_visible() and await send_button.is_enabled():
                    await send_button.click()
                else:
                    # Fallback to pressing Enter
                    await page.keyboard.press("Enter")
                    
                print(f"[SUCCESS] Message sent to {name} successfully!")
                success_count += 1
                
                # 5. Brief cool-down period to avoid carrier spam triggers
                await asyncio.sleep(4)
                
            except Exception as e:
                print(f"[FAILED] Failed to send message to {name}. Error: {e}")
                failed_students.append(student)
                # Try navigating back or reloading to recover from errors
                await page.goto("https://messages.google.com/web")
                await asyncio.sleep(5)
                
        print(f"\n==========================================")
        print(f"🎉 Batch Delivery Completed!")
        print(f"Successfully sent: {success_count}/{len(accepted_students)}")
        if failed_students:
            print(f"Failed deliveries ({len(failed_students)}):")
            for f_student in failed_students:
                print(f"  - {f_student['name']} ({f_student['phone']})")
        print(f"==========================================")
        
        # Disconnect Playwright from the CDP session
        await browser.close()

if __name__ == '__main__':
    asyncio.run(send_sms_automation())
