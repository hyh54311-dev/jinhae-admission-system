import os
import json
import time
import sys

# ----------------- ?ㅼ젙 ----------------- #
COOKIE_PATH = r"C:\Users\admin\.notebooklm-mcp-cli\profiles\default\cookies.json"
METADATA_PATH = r"C:\Users\admin\.notebooklm-mcp-cli\profiles\default\metadata.json"
# ---------------------------------------- #

def parse_cookie_string(cookie_str):
    """
    釉뚮씪?곗??먯꽌 蹂듭궗??荑좏궎 臾몄옄??Key=Value; Key2=Value2...)???뚯씠???뺤뀛?덈━濡??뚯떛
    """
    cookies = {}
    try:
        parts = cookie_str.split(';')
        for part in parts:
            if '=' in part:
                key, value = part.strip().split('=', 1)
                cookies[key] = value
        return cookies
    except Exception as e:
        print(f"??荑좏궎 ?뚯떛 以??ㅻ쪟 諛쒖깮: {e}")
        return None

def update_cookies_json(new_cookies_dict):
    """
    湲곗〈 cookies.json ?뚯씪???쎌뼱???듭떖 荑좏궎?ㅼ쓣 ?낅뜲?댄듃?섍굅???덈줈 ?앹꽦
    """
    # 湲곕낯 ? ?앹꽦 (留뚯빟 ?뚯씪???놁쑝硫?
    base_cookies = []
    if os.path.exists(COOKIE_PATH):
        try:
            with open(COOKIE_PATH, "r", encoding="utf-8") as f:
                base_cookies = json.load(f)
        except:
            base_cookies = []

    # ?듭떖 ?꾨찓??由ъ뒪??    domains = [".google.com", ".google.co.kr", "notebooklm.google.com"]
    
    # ?낅뜲?댄듃??荑좏궎 紐⑸줉
    target_names = ["SID", "HSID", "SSID", "SAPISID", "APISID", "__Secure-1PSID", "__Secure-3PSID"]
    
    updated_count = 0
    
    # 1. 湲곗〈 荑좏궎 以??寃잛씠 ?덉쑝硫??낅뜲?댄듃
    for cookie_obj in base_cookies:
        name = cookie_obj.get("name")
        if name in new_cookies_dict and name in target_names:
            cookie_obj["value"] = new_cookies_dict[name]
            updated_count += 1
            
    # 2. 留뚯빟 湲곗〈???녿뒗 ?꾩닔 荑좏궎媛 ?덈떎硫??덈줈 異붽? (湲곕낯 媛??명똿)
    existing_names = [c.get("name") for c in base_cookies]
    for name in target_names:
        if name in new_cookies_dict and name not in existing_names:
            for domain in [".google.com"]: # 媛??湲곕낯 ?꾨찓?몄쑝濡?異붽?
                new_obj = {
                    "name": name,
                    "value": new_cookies_dict[name],
                    "domain": domain,
                    "path": "/",
                    "expires": time.time() + (365 * 24 * 60 * 60), # 1????留뚮즺
                    "httpOnly": True if "SID" in name else False,
                    "secure": True,
                    "session": False,
                    "priority": "High"
                }
                base_cookies.append(new_obj)
                updated_count += 1

    # ?뚯씪 ???    os.makedirs(os.path.dirname(COOKIE_PATH), exist_ok=True)
    with open(COOKIE_PATH, "w", encoding="utf-8") as f:
        json.dump(base_cookies, f, indent=2)
        
    return updated_count

def main():
    print("===================================================")
    print("   [NotebookLM ?섎룞 ?몄뀡 蹂듦뎄 ?꾩슦誘?   ")
    print("===================================================")
    print("1. Chrome 釉뚮씪?곗??먯꽌 NotebookLM??濡쒓렇?명빀?덈떎.")
    print("2. F12 (媛쒕컻???꾧뎄) -> Network ???대┃")
    print("3. 紐⑸줉 以?'notebooklm.google.com' ?먮뒗 'list' ??ぉ ?대┃")
    print("4. Headers ??뿉??'Cookie:' ??ぉ???꾩껜 ?댁슜??蹂듭궗?섏꽭??")
    print("===================================================\n")
    
    cookie_input = input("蹂듭궗??荑좏궎 ?댁슜???ш린??遺숈뿬?ｌ뼱 二쇱꽭??\n> ").strip()
    
    if not cookie_input:
        print("???낅젰???댁슜???놁뒿?덈떎. 醫낅즺?⑸땲??")
        return

    # 'Cookie: ' ?묐몢?ш? ?ы븿??寃쎌슦 ?쒓굅
    if cookie_input.lower().startswith("cookie:"):
        cookie_input = cookie_input[7:].strip()

    parsed = parse_cookie_string(cookie_input)
    if not parsed or len(parsed) < 3:
        print("???좏슚??荑좏궎 ?뺤떇???꾨땲嫄곕굹 ?꾩닔 ?뺣낫(SID ??媛 遺議깊빀?덈떎.")
        return

    count = update_cookies_json(parsed)
    print(f"\n??{count}媛쒖쓽 ?몄뀡 荑좏궎 ?뺣낫媛 ?깃났?곸쑝濡??낅뜲?댄듃?섏뿀?듬땲??")
    
    # metadata.json 議댁옱?щ????곕씪 ?붾? ?앹꽦 (?먮윭 諛⑹???
    if not os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump({"profile_name": "default", "created_at": time.time()}, f)

    print("\n[?뚯뒪??以?..] NotebookLM ?곕룞???뺤씤?⑸땲??")
    time.sleep(1)
    
    # 寃利??쒕룄
    try:
        import subprocess
        # BASE_DIR??湲곗??쇰줈 run_nlm_patched.py ?ㅽ뻾
        working_dir = r"d:\OneDrive - 寃쎌긽?⑤룄援먯쑁泥?諛뷀깢 ?붾㈃\吏꾪빐怨좊벑?숆탳\2026?숇뀈??antigravity_folder"
        cmd = [sys.executable, os.path.join(working_dir, "run_nlm_patched.py"), "notebook", "list"]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0 and "ID" in result.stdout:
            print("?? ?곕룞 ?깃났! ?댁젣 ?ㅻ뵒?ㅻ럭 ?앹꽦???뺤긽 ?묐룞?⑸땲??")
        else:
            print(f"?좑툘 ?곕룞 ?뺤씤 ?ㅽ뙣: {result.stderr if result.stderr else '?묐떟 ?놁쓬'}")
    except Exception as e:
        print(f"?좑툘 寃利??꾩쨷 ?ㅻ쪟 諛쒖깮: {e}")

    print("\n?꾨Т ?ㅻ굹 ?꾨Ⅴ硫?醫낅즺?⑸땲??")
    input()

if __name__ == "__main__":
    main()
