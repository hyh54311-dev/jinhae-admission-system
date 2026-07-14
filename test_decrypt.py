import os
import json
import base64
import sqlite3
import shutil
import win32crypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import sys

# 1. 寃쎈줈 ?ㅼ젙
CHROME_PATH = os.path.join(os.environ["LOCALAPPDATA"], r"Google\Chrome\User Data")
LS_PATH = os.path.join(CHROME_PATH, "Local State")
DB_PATH = os.path.join(CHROME_PATH, "Profile 3", "Network", "Cookies")

def get_key():
    with open(LS_PATH, "r", encoding="utf-8") as f:
        ls = json.load(f)
    ek = base64.b64decode(ls["os_crypt"]["encrypted_key"])
    key = win32crypt.CryptUnprotectData(ek[5:], None, None, None, 0)[1]
    return key

def test_decrypt():
    key = get_key()
    print(f"Master Key Length: {len(key)}")
    
    shutil.copyfile(DB_PATH, "test.db")
    conn = sqlite3.connect("test.db")
    c = conn.cursor()
    
    # .google.com ??SID ?섎굹留??쒕룄
    c.execute("SELECT name, host_key, encrypted_value FROM cookies WHERE host_key='.google.com' AND name='SID' LIMIT 1")
    row = c.fetchone()
    if not row:
        print("No SID found for .google.com")
        return
        
    name, host, val = row
    print(f"Testing decryption for {name} ({host}). Payload length: {len(val)}")
    
    try:
        iv = val[3:15]
        data = val[15:]
        aesgcm = AESGCM(key)
        decrypted = aesgcm.decrypt(iv, data, None)
        print(f"Decryption SUCCESS! Value starts with: {decrypted[:10].decode('utf-8')}...")
    except Exception as e:
        print(f"Decryption FAILED: {e}")
        # ?섏씠濡쒕뱶 ?ㅻ뜑 ?뺤씤 (v10 ?몄??)
        print(f"Header: {val[:3]}")

    conn.close()
    os.remove("test.db")

if __name__ == "__main__":
    test_decrypt()
