import os
import json
import base64
import sqlite3
import shutil
import win32crypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from datetime import datetime
import time
import io
import sys

# ?덈룄??肄섏넄 ?몄퐫?????if sys.platform == 'win32' and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ----------------- 寃쎈줈 ?ㅼ젙 ----------------- #
CHROME_USER_DATA_PATH = os.path.join(os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data")
LOCAL_STATE_PATH = os.path.join(CHROME_USER_DATA_PATH, "Local State")
# 理쒓렐 ?щ＼ 踰꾩쟾? Network ?대뜑 ?덉뿉 Cookies媛 ?덉쓬
COOKIES_DB_PATH = os.path.join(CHROME_USER_DATA_PATH, "Default", "Network", "Cookies")
TEMP_COOKIES_DB = os.path.join(os.getenv("TEMP", "."), "nlm_cookies_temp.db")

# NotebookLM CLI??寃쎈줈
NLM_PROFILES_DIR = os.path.join(os.environ["USERPROFILE"], ".notebooklm-mcp-cli", "profiles", "default")
NLM_COOKIES_JSON = os.path.join(NLM_PROFILES_DIR, "cookies.json")
# --------------------------------------------- #

def get_master_key():
    try:
        with open(LOCAL_STATE_PATH, "r", encoding="utf-8") as f:
            local_state = json.loads(f.read())
        
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        # 'DPAPI' 臾몄옄??5諛붿씠?? ?쒓굅 ??蹂듯샇??        master_key = win32crypt.CryptUnprotectData(encrypted_key[5:], None, None, None, 0)[1]
        return master_key
    except Exception as e:
        print(f"??留덉뒪????異붿텧 ?ㅽ뙣: {e}")
        return None

def decrypt_payload(cipher, payload, key):
    try:
        # payload 援ъ“: [3諛붿씠?퇠refix:v10][12諛붿씠?퇞once][EncryptedData][16諛붿씠?퇤ag]
        # (cryptography ?쇱씠釉뚮윭由щ뒗 [Nonce][EncryptedData+Tag] ?뺥깭瑜?湲곕???
        iv = payload[3:15]
        encrypted_data = payload[15:]
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(iv, encrypted_data, None).decode('utf-8')
    except Exception as e:
        # print(f"??蹂듯샇???먮윭: {e}")
        return None

def scavenge_google_cookies():
    print("[吏꾪뻾] ?щ＼ 釉뚮씪?곗??먯꽌 NotebookLM ?몄뀡 ?뺣? ?ㅼ틪 以?..")
    
    master_key = get_master_key()
    if not master_key:
        return None

    # 紐⑤뱺 ?꾨줈???대뜑 ?먯깋 (Default, Profile 1~10)
    profile_dirs = ["Default"]
    for i in range(1, 11):
        profile_dirs.append(f"Profile {i}")

    all_scavenged_list = []
    target_names = ["SID", "HSID", "SSID", "SAPISID", "APISID", "__Secure-1PSID", "__Secure-3PSID", "OSID"]

    for p_dir in profile_dirs:
        # 理쒓렐 ?щ＼ 踰꾩쟾? Network ?대뜑 ?덉뿉 Cookies媛 ?덇퀬, 援щ쾭?꾩? ?꾨줈??猷⑦듃???덉쓬
        p_paths = [
            os.path.join(CHROME_USER_DATA_PATH, p_dir, "Network", "Cookies"),
            os.path.join(CHROME_USER_DATA_PATH, p_dir, "Cookies")
        ]
        
        current_db_path = None
        for p in p_paths:
            if os.path.exists(p):
                current_db_path = p
                break
        
        if not current_db_path:
            continue

        # print(f">> ?꾨줈???먯깋 以? {p_dir}")

        # 釉뚮씪?곗?媛 ?대젮 ?덉뼱???쎌쓣 ???덈룄濡?DB 蹂듭궗
        try:
            if os.path.exists(TEMP_COOKIES_DB):
                os.remove(TEMP_COOKIES_DB)
            shutil.copyfile(current_db_path, TEMP_COOKIES_DB)
        except Exception as e:
            continue

        conn = sqlite3.connect(TEMP_COOKIES_DB)
        cursor = conn.cursor()
        
        try:
            # 援ш? 愿???꾨찓??.com, .co.kr, notebooklm ?? 荑좏궎 異붿텧
            query = "SELECT host_key, name, path, expires_utc, is_httponly, is_secure, encrypted_value FROM cookies WHERE host_key LIKE '%google%'"
            cursor.execute(query)
            
            for host_key, name, path, expires, is_httponly, is_secure, encrypted_value in cursor.fetchall():
                is_target_cookie = name in target_names
                is_google_domain = any(domain in host_key for domain in [".google.com", ".google.co.kr", "notebooklm.google.com"])
                
                if is_target_cookie and is_google_domain:
                    decrypted_value = decrypt_payload(None, encrypted_value, master_key)
                    if decrypted_value:
                        cookie_obj = {
                            "name": name,
                            "value": decrypted_value,
                            "domain": host_key,
                            "path": path,
                            "expires": (expires / 1000000) - 11644473600 if expires > 0 else 0,
                            "httpOnly": True if is_httponly else False,
                            "secure": True if is_secure else False,
                            "sameSite": "Lax",
                            "priority": "High"
                        }
                        # 以묐났 ?쒓굅 諛?理쒖떊媛??좎?
                        if not any(c["name"] == name and c["domain"] == host_key for c in all_scavenged_list):
                            all_scavenged_list.append(cookie_obj)
        except Exception as e:
            pass
        finally:
            conn.close()

    if os.path.exists(TEMP_COOKIES_DB):
        os.remove(TEMP_COOKIES_DB)
        
    print(f"[OK] {len(all_scavenged_list)}媛쒖쓽 ?듭떖 蹂댁븞 荑좏궎瑜??섏쭛?덉뒿?덈떎.")
    return all_scavenged_list

def save_to_nlm_config(cookies_list):
    if not cookies_list:
        return False
        
    os.makedirs(NLM_PROFILES_DIR, exist_ok=True)
    
    # 湲곗〈 ?뚯씪 泥섎━
    final_list = []
    if os.path.exists(NLM_COOKIES_JSON):
        try:
            with open(NLM_COOKIES_JSON, "r", encoding="utf-8") as f:
                final_list = json.load(f)
        except:
            final_list = []

    # ??荑좏궎濡?援먯껜
    new_keys = set((c["name"], c["domain"]) for c in cookies_list)
    final_list = [c for c in final_list if (c.get("name"), c.get("domain")) not in new_keys]
    final_list.extend(cookies_list)

    with open(NLM_COOKIES_JSON, "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=2)
    
    meta_path = os.path.join(NLM_PROFILES_DIR, "metadata.json")
    if not os.path.exists(meta_path):
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({"profile_name": "default", "updated_at": str(datetime.now())}, f)
            
    return True

def main():
    print("===================================================")
    print("      NotebookLM '????대뱶由? ?먮룞 蹂듦뎄 ?붿쭊      ")
    print("===================================================")
    
    cookies = scavenge_google_cookies()
    if cookies and len(cookies) > 0:
        if save_to_nlm_config(cookies):
            print("\n[?깃났] 紐⑤뱺 ?몄뀡 ?뺣낫瑜??깃났?곸쑝濡??댁떇?덉뒿?덈떎!")
            print(">> ?댁젣 蹂꾨룄??濡쒓렇???놁씠 NotebookLM ?먮룞?붽? 媛?ν빀?덈떎.")
        else:
            print("\n[-] ?뚯씪 ???以??ㅻ쪟媛 諛쒖깮?덉뒿?덈떎.")
    else:
        print("\n[-] ?몄뀡 ?뺣낫瑜?李얠? 紐삵뻽?듬땲?? ?щ＼?먯꽌 NotebookLM??濡쒓렇?몃릺???덈뒗吏 ?뺤씤??二쇱꽭??")

if __name__ == "__main__":
    main()
