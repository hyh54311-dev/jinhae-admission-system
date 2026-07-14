import os
import sqlite3
import shutil

# 1. 寃쎈줈 ?ㅼ젙
CHROME_PATH = os.path.join(os.environ["LOCALAPPDATA"], r"Google\Chrome\User Data")
PROFILE_NAME = "Profile 3" 
COOKIES_PATH = os.path.join(CHROME_PATH, PROFILE_NAME, "Network", "Cookies")
TEMP_DB = "diag_nlm_cookies_v3.db"

def diag():
    if not os.path.exists(COOKIES_PATH):
        print(f"Path not found: {COOKIES_PATH}")
        return

    # ?대? ?щ＼???쒖뒪?ы궗 ?덉쑝誘濡?諛붾줈 蹂듭궗媛?ν븷 寃?    shutil.copyfile(COOKIES_PATH, TEMP_DB)
    conn = sqlite3.connect(TEMP_DB)
    c = conn.cursor()
    
    # 1. ?꾨찓??紐⑸줉 ?뺤씤 (?곸쐞 20媛?
    print("--- Sample Domains ---")
    c.execute("SELECT DISTINCT host_key FROM cookies LIMIT 20")
    print([r[0] for r in c.fetchall()])
    
    # 2. 援ш? 愿??荑좏궎 ?꾨찓??諛??대쫫 ?꾩껜 ?뺤씤
    print("\n--- Google Related Cookies (Host, Name) ---")
    c.execute("SELECT host_key, name FROM cookies WHERE host_key LIKE '%google%'")
    rows = c.fetchall()
    print(f"Found {len(rows)} cookies.")
    for h, n in rows:
        print(f"[{h}] {n}")
    
    conn.close()
    if os.path.exists(TEMP_DB):
        os.remove(TEMP_DB)

if __name__ == "__main__":
    diag()
