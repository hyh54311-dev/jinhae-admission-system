import os
import sys
import subprocess
import json
import time

# ----------------- ?ㅼ젙 ----------------- #
# notebooklm_auto.py? ?숈씪???좏겙 ?ъ슜
TELEGRAM_TOKEN = "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY"
TELEGRAM_CHAT_ID = "8518409134"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ---------------------------------------- #

def send_telegram_notification(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        import urllib.request
        import urllib.parse
        import ssl
        data = urllib.parse.urlencode({'chat_id': TELEGRAM_CHAT_ID, 'text': text}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        urllib.request.urlopen(req, context=ctx)
    except Exception as e:
        print(f"?붾젅洹몃옩 ?뚮┝ ?꾩넚 ?ㅽ뙣: {e}")

def check_session():
    print("?뵇 NotebookLM ?몄뀡 ?좏슚??寃??以?..")
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf8"
    env["PYTHONUTF8"] = "1"
    
    try:
        # nlm list --json ?ㅽ뻾?섏뿬 ?뺤긽?곸씤 JSON???ㅻ뒗吏 ?뺤씤
        cmd = [sys.executable, os.path.join(BASE_DIR, "run_nlm_patched.py"), "notebook", "list", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', env=env)
        
        # 1. 醫낅즺 肄붾뱶媛 0???꾨땲嫄곕굹 ?먮윭 硫붿떆吏??'login', 'unauthorized' ?깆씠 ?ы븿??寃쎌슦
        if result.returncode != 0 or any(kw in result.stderr.lower() for kw in ["login", "unauthorized", "expired"]):
            raise Exception("?몄뀡??留뚮즺?섏뿀嫄곕굹 濡쒓렇?몄씠 ?꾩슂?⑸땲??")

        # 2. 寃곌낵媛믪씠 HTML(?먮윭 ?섏씠吏)??寃쎌슦
        if result.stdout.strip().startswith("<!DOCTYPE html>") or result.stdout.strip().startswith("<html"):
             raise Exception("?쒕쾭濡쒕????먮윭 ?섏씠吏媛 諛섑솚?섏뿀?듬땲?? ?몄뀡 留뚮즺媛 ?섏떖?⑸땲??")

        # 3. JSON ?뚯떛 ?쒕룄
        json.loads(result.stdout.strip())
        
        print("??NotebookLM ?몄뀡???뺤긽?낅땲??")
        return True

    except Exception as e:
        print(f"???몄뀡 泥댄겕 ?ㅽ뙣: {e}")
        error_msg = (
            f"?슚 [NotebookLM 湲닿툒 ?뚮┝]\n\n"
            f"NotebookLM ?몄뀡??留뚮즺??寃껋쑝濡?蹂댁엯?덈떎.\n"
            f"?대?濡??먮㈃ ?덉빟??寃쎌젣 ?댁뒪 諛?????뺣낫???ㅻ뵒?ㅻ럭 ?앹꽦???ㅽ뙣?⑸땲??\n\n"
            f"?뱧 議곗튂 諛⑸쾿:\n"
            f"?낅Т??而댄벂?곗뿉??'NotebookLM_珥덇린濡쒓렇??bat' ?뚯씪???ㅽ뻾?섏뿬 ?ㅼ떆 濡쒓렇?명빐 二쇱꽭??"
        )
        send_telegram_notification(error_msg)
        return False

if __name__ == "__main__":
    check_session()
