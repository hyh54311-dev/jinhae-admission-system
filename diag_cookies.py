import os
import shutil
import sqlite3
import json
import base64
import win32crypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# 1. 寃쎈줈 ?ㅼ젙
CHROME_PATH = os.path.join(os.environ["LOCALAPPDATA"], r"Google\Chrome\User Data")
PROFILE_NAME = "Profile 3" # 理쒓렐 蹂寃??대젰???덈뒗 ?꾨줈??COOKIES_PATH = os.path.join(CHROME_PATH, PROFILE_NAME, "Network", "Cookies")
LOCAL_STATE = os.path.join(CHROME_PATH, "Local State")
TEMP_DB = "diag_nlm_cookies.db"

def get_key():
    with open(LOCAL_STATE, "r", encoding="utf-8") as f:
        ls = json.load(f)
    ek = base64.b64decode(ls["os_crypt"]["encrypted_key"])
    return win32crypt.CryptUnprotectData(ek[5:], None, None, None, 0)[1]

def diag():
    if not os.path.exists(COOKIES_PATH):
        print(f"Path not found: {COOKIES_PATH}")
        return

    shutil.copyfile(COOKIES_PATH, TEMP_DB)
    conn = sqlite3.connect(TEMP_DB)
    c = conn.cursor()
    
    # ?꾨찓??紐⑸줉 ?뺤씤
    print("--- Domains containing 'google' ---")
    c.execute("SELECT DISTINCT host_key FROM cookies WHERE host_key LIKE '%google%'")
    domains = [r[0] for r in c.fetchall()]
    print(domains)
    
    # ?듭떖 荑좏궎 ?뺤씤
    print("\n--- Specific Cookies Search ---")
    targets = ("SID", "HSID", "SSID", "__Secure-1PSID")
    query = f"SELECT host_key, name, encrypted_value FROM cookies WHERE name IN {targets}"
    c.execute(query)
    rows = c.fetchall()
    print(f"Found {len(rows)} matching cookies.")
    for h, n, v in rows:
        print(f"Domain: {h}, Name: {n}, Value Length: {len(v)}")
    
    conn.close()
    if os.path.exists(TEMP_DB):
        os.remove(TEMP_DB)

if __name__ == "__main__":
    diag()
