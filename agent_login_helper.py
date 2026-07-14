import os
import json
import time
import sys
import io
from playwright.sync_api import sync_playwright
from datetime import datetime

# ----------------- 寃쎈줈 ?ㅼ젙 ----------------- #
NLM_PROFILES_DIR = os.path.join(os.environ["USERPROFILE"], ".notebooklm-mcp-cli", "profiles", "default")
NLM_COOKIES_JSON = os.path.join(NLM_PROFILES_DIR, "cookies.json")
# --------------------------------------------- #

# ?덈룄??肄섏넄 ?몄퐫?????if sys.platform == 'win32' and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def save_cookies(cookies):
    os.makedirs(NLM_PROFILES_DIR, exist_ok=True)
    with open(NLM_COOKIES_JSON, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2)
    
    meta_path = os.path.join(NLM_PROFILES_DIR, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({"profile_name": "default", "updated_at": str(datetime.now())}, f)

def run_helper():
    with sync_playwright() as p:
        print("==================================================")
        print("   [Antigravity] NotebookLM 濡쒓렇???꾩슦誘??ㅽ뻾   ")
        print("==================================================")
        print("1. ?덈줈??釉뚮씪?곗? 李쎌씠 ?대┰?덈떎.")
        print("2. ?됱냼泥섎읆 援ш? 濡쒓렇?몄쓣 吏꾪뻾??二쇱꽭??")
        print("3. 濡쒓렇?몄씠 ?꾨즺?섎㈃ ?쒓? ?먮룞?쇰줈 ?뺣낫瑜??싳븘梨뺣땲??")
        print("==================================================\n")
        
        # 釉뚮씪?곗? ?ㅽ뻾 (?ъ슜?먭? 蹂????덈룄濡?headless=False)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://notebooklm.google.com")
        
        print(">> 濡쒓렇???湲?以?.. (濡쒓렇?몄쓣 留덉튇 ??'?깃났' 硫붿떆吏媛 ???뚭퉴吏 李쎌쓣 ?レ? 留덉꽭??")
        
        captured = False
        while not captured:
            time.sleep(2)
            
            # ?섏씠吏媛 ?ロ삍?붿? 泥댄겕
            if page.is_closed():
                break
                
            cookies = context.cookies()
            
            # NotebookLM???듭떖 ?뱀쭠??SID 荑좏궎? ??쒕낫??URL ?묎렐 ?뺤씤
            has_sid = any(c['name'] == 'SID' for c in cookies)
            is_on_dashboard = any(keyword in page.url for keyword in ["notebooks", "sources", "list", "chat"])
            
            if has_sid and is_on_dashboard:
                print("\n[?깃났] ?곕룞???꾩슂??蹂댁븞 ?몄뀡???깃났?곸쑝濡??싳븘梨섏뒿?덈떎!")
                save_cookies(cookies)
                captured = True
                break
                
        if captured:
            print("\n==================================================")
            print("   ???몄뀡 蹂듦뎄 ?깃났! ?댁젣 李쎌쓣 ?レ쑝?붾룄 ?⑸땲?? ??)
            print("==================================================")
            time.sleep(2)
            browser.close()
        else:
            print("\n[-] ?몄뀡???싳븘梨꾩? 紐삵뻽?듬땲?? 李쎌씠 ?덈Т ?쇱컢 ?ロ삍嫄곕굹 濡쒓렇?몄씠 ?섏? ?딆븯?듬땲??")
            browser.close()

if __name__ == "__main__":
    try:
        run_helper()
    except Exception as e:
        print(f"\n[-] ?ㅻ쪟 諛쒖깮: {e}")
        time.sleep(5)
