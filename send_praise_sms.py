import os
import sys
import json
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

# Ensure UTF-8 console output
sys.stdout.reconfigure(encoding='utf-8')

CHROME_CDP_URL = "http://127.0.0.1:9222"

MESSAGE_TEMPLATE = """[진해고등학교 칭찬 알림 배달]

안녕하세요, {학생이름} 학생의 학부모님. 진해고등학교 담임교사입니다.

오늘 학교 생활 중 자녀가 실천한 따뜻한 칭찬 소식을 전해드립니다.

💌 칭찬 내용:
"{칭찬내용}"

귀가하는 자녀에게 따뜻한 격려와 공감의 대화를 건네주시기 바랍니다.

- 진해고등학교 -"""

def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

async def send_praise_sms():
    script_dir = get_script_dir()
    json_path = os.path.join(script_dir, 'praises.json')

    if not os.path.exists(json_path):
        print("[INFO] praises.json file not found. No praises to send.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        try:
            praises = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load praises.json: {e}")
            return

    # Filter pending praises
    pending_praises = [p for p in praises if p.get('status') == 'pending']

    if not pending_praises:
        print("[INFO] No pending praises to send today.")
        return

    print(f"[INFO] Found {len(pending_praises)} pending praises to send at 16:30.")

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
        
        for idx, item in enumerate(pending_praises, 1):
            name = item["name"]
            phone = item["phone"]
            student_id = item["student_id"]
            content = item["content"]
            
            # Format message
            message_text = MESSAGE_TEMPLATE.format(학생이름=name, 칭찬내용=content)
            
            print(f"\n[{idx}/{len(pending_praises)}] Sending praise SMS to {name}'s parent ({phone})...")
            print("=" * 60)
            print(message_text)
            print("=" * 60)
            
            try:
                # 1. Click "Start chat"
                start_chat_btn = page.locator("[data-e2e-start-button]").first
                await start_chat_btn.click()
                await asyncio.sleep(2.5)
                
                # 2. Enter recipient phone number
                recipient_input = page.locator("[data-e2e-contact-input]").first
                if not await recipient_input.is_visible():
                    raise Exception("Could not locate the recipient input field.")
                    
                await recipient_input.fill(phone)
                await asyncio.sleep(2.5)
                
                # Click dropdown Send to...
                send_to_btn = page.locator("[data-e2e-send-to-button]").first
                if not await send_to_btn.is_visible():
                    raise Exception("Could not locate the 'Send to...' dropdown button.")
                await send_to_btn.click()
                await asyncio.sleep(4.5)
                
                # 3. Locate text area
                message_box = page.locator("[data-e2e-message-input-box]").first
                if not await message_box.is_visible():
                    raise Exception("Could not locate the message input area.")
                    
                await message_box.focus()
                await message_box.fill(message_text)
                await asyncio.sleep(2)
                
                # 4. Click Send button or press Enter
                send_button = page.locator("[data-e2e-send-text-button]").first
                if await send_button.is_visible() and await send_button.is_enabled():
                    await send_button.click()
                else:
                    await page.keyboard.press("Enter")
                    
                print(f"[SUCCESS] Message sent to {name}'s parent successfully!")
                item['status'] = 'sent'
                item['sent_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                success_count += 1
                
                # Cooldown period
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"[FAILED] Failed to send to {name}'s parent. Error: {e}")
                item['status'] = 'failed'
                item['error'] = str(e)
                # Recover
                await page.goto("https://messages.google.com/web")
                await asyncio.sleep(5)

        # Save results back to praises.json
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(praises, f, ensure_ascii=False, indent=2)
            print("\n[INFO] praises.json file updated with delivery status.")
        except Exception as e:
            print(f"[ERROR] Failed to save updated praises.json: {e}")

        print(f"\n==========================================")
        print(f"🎉 Praise SMS Delivery Completed!")
        print(f"Successfully sent: {success_count}/{len(pending_praises)}")
        print(f"==========================================")
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(send_praise_sms())
