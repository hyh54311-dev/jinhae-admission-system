import time
import urllib.request
import json
import ssl

TOKEN = "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY"
URL = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

print("?ъ슜?먯쓽 ?붾젅洹몃옩 硫붿떆吏瑜?湲곕떎由щ뒗 以묒엯?덈떎...")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

for i in range(20): # 理쒕? 1遺꾧컙 ?湲?(3珥?媛꾧꺽)
    try:
        req = urllib.request.Request(URL)
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data["ok"] and len(data["result"]) > 0:
                # 媛??留덉?留?硫붿떆吏 異붿텧
                last_update = data["result"][-1]
                chat_id = last_update["message"]["chat"]["id"]
                sender_name = last_update["message"]["from"].get("first_name", "User")
                print(f"\n[?깃났] 硫붿떆吏瑜?諛쏆븯?듬땲?? (諛쒖떊?? {sender_name})")
                print(f"CHAT_ID={chat_id}")
                
                # ?뺤씤 硫붿떆吏 ?뚯떊
                send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text=遊??곌껐???깃났?곸쑝濡??꾨즺?섏뿀?듬땲??"
                urllib.request.urlopen(send_url, context=ctx)
                exit(0)
    except Exception as e:
        print(f"?먮윭諛쒖깮: {e}")
    time.sleep(3)
    print(".", end="", flush=True)

print("\n[?쒓컙珥덇낵] 1遺??숈븞 硫붿떆吏媛 ?ㅼ? ?딆븯?듬땲??")
