import os
import sys
import time
import json
import subprocess
import threading
import io
import requests
import urllib3
import re
from datetime import datetime
import unified_schedule
import stay_awake
from dotenv import load_dotenv

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform == 'win32':
    try:
        if sys.stdout.encoding.lower() != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

# ----------------- ?ъ슜???ㅼ젙 ----------------- #
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8799464748:AAHD2ERa9aEnqn6Dtr7SNDjDOf9KGFEMziU")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.1-flash-lite"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "telegram_assistant.log")
# ----------------------------------------------- #

def log_message(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    full_message = f"[{timestamp}] [Bot] {message}"
    print(full_message)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_message + "\n")
    except Exception as e:
        print(f"濡쒓렇 ?뚯씪 湲곕줉 ?ㅽ뙣: {e}")

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=10, verify=False)
    except Exception as e:
        log_message(f"?붾젅洹몃옩 諛쒖넚 ?ㅻ쪟: {e}")

def ask_gemini(user_message, context_data=None):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
    
    current_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    system_instruction = (
        f"?뱀떊???대쫫? 'Antigravity'?낅땲?? 吏꾪빐怨좊벑?숆탳 ?⑹슂???좎깮?섏쓽 ?낅Т瑜??꾨떞?섎뒗 珥덉???AI 鍮꾩꽌?낅땲??\n"
        f"?꾩옱 ?쒓컖: {current_now}\n\n"
        "?뱀떊? 援ш? 罹섎┛?? ?쒖뒪?? ???濡쒓렇 ?곗씠?곕? ?ㅼ떆媛꾩쑝濡?議고쉶?섏뿬 ?듬??????덉뒿?덈떎.\n"
        "### [?꾩닔 ?듬? 媛?대뱶]\n"
        "1. ?뺤쭅?? [?ㅼ떆媛?李멸퀬 ?곗씠?????녿뒗 ?뺣낫???덈? 吏?대궡吏 留덉떗?쒖삤. 紐⑤Ⅴ硫?'湲곕줉??李얠쓣 ???놁뒿?덈떎'?쇨퀬 ?듯븯??떆??\n"
        "2. ?쒓퀎?? 紐⑤뱺 ?듬????꾩옱 ?곕룄(2026??瑜?諛섎뱶???멸툒?섏뿬 ?쒖젏???뺥솗?깆쓣 ?뺣낫?섏떗?쒖삤.\n"
        "3. 援ъ“?? 鍮꾧탳 遺꾩꽍?대굹 ?ㅻ웾???뺣낫 ?붿껌 ?쒖뿉??諛섎뱶??[留덊겕?ㅼ슫 ??|---|) ?뺤떇]???ъ슜?섏뿬 ?쇰ぉ?붿뿰?섍쾶 蹂닿퀬?섏떗?쒖삤.\n"
        "4. 異쒖쿂: ?쇱젙 釉뚮━?????뺣낫??異쒖쿂(罹섎┛?? 濡쒓렇 ??瑜?紐낇솗??諛앺엳??떆??\n"
        "5. ?섎Ⅴ?뚮굹: ??긽 ?뺤쨷?섍퀬 ?덇꺽 ?덈뒗 ?댁“濡??좎깮?섏쓣 蹂댄븘?섏떗?쒖삤."
    )
    
    final_prompt = f"{system_instruction}\n\n"
    if context_data:
        final_prompt += f"### [?ㅼ떆媛?李멸퀬 ?곗씠??\n{context_data}\n\n"
        
    final_prompt += f"[?좎깮?섏쓽 吏덈Ц]: {user_message}"
    
    payload = {
        "contents": [{"parts": [{"text": final_prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 4096,
            "temperature": 0.1 # ?좊ː??洹밸??붾? ?꾪빐 ?⑤룄瑜???땄
        }
    }
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30, verify=False)
        response.raise_for_status()
        json_data = response.json()
        candidates = json_data.get("candidates", [])
        if not candidates:
            return "?묐떟???앹꽦?섏? 紐삵뻽?듬땲??"
        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join([part.get("text", "") for part in parts])
    except Exception as e:
        return f"AI ?곌껐 ?ㅻ쪟媛 諛쒖깮?덉뒿?덈떎: {e}"

def run_script_in_background(script_name, args, chat_id, task_name):
    script_path = os.path.join(BASE_DIR, script_name)
    if not os.path.exists(script_path):
        send_telegram_message(chat_id, f"??{script_name} ?뚯씪??李얠쓣 ???놁뒿?덈떎.")
        return
    
    send_telegram_message(chat_id, f"?? [{task_name}] ?묒뾽??諛깃렇?쇱슫?쒖뿉???쒖옉?⑸땲??..\n(?꾨즺 諛??ㅻ쪟 ?뚮┝? ?쒖뒪?쒖뿉???먮룞 諛쒖넚?⑸땲??)")
    
    try:
        cmd = [sys.executable, script_path] + args
        subprocess.Popen(cmd, cwd=BASE_DIR)
    except Exception as e:
        send_telegram_message(chat_id, f"???ㅽ뻾 ?ㅽ뙣: {e}")

def process_message(message_data):
    try:
        chat_id = message_data["chat"]["id"]
        text = message_data.get("text", "").strip()
        
        if not text:
            return

        log_message(f"[?섏떊] {chat_id}: {text}")

        if text.startswith("/news"):
            run_script_in_background("daily_news.py", [], chat_id, "寃쎌젣 ?댁뒪 ?앹꽦")
        elif text.startswith("/admission"):
            run_script_in_background("admission_news.py", ["run_now"], chat_id, "????뺣낫 ?앹꽦")
        elif text.startswith("/ping"):
            import socket
            hostname = socket.gethostname()
            send_telegram_message(chat_id, f"??Antigravity ?쒕쾭 ?뺤긽 ?묐룞 以?\n?뱧 ?꾩튂: {hostname}")
        else:
            context_data = None
            schedule_keywords = ["?쇱젙", "?ㅼ?以?, "怨꾪쉷", "萸???, "萸???, "?쎌냽", "湲곗뼲"]
            
            offset = 0
            if "?댁씪" in text: offset = 1
            elif "紐⑤젅" in text: offset = 2
            
            if any(kw in text for kw in schedule_keywords):
                send_telegram_message(chat_id, "?뵇 ?ㅼ젣 ?곗씠??罹섎┛?? 濡쒓렇)瑜??뺤씤?섏뿬 ?쇱젙???뚯븙 以묒엯?덈떎...")
                context_data = unified_schedule.get_unified_briefing(date_offset=offset)
            
            reply = ask_gemini(text, context_data)
            send_telegram_message(chat_id, reply)

    except Exception as e:
        log_message(f"硫붿떆吏 泥섎━ ?ㅻ쪟: {e}")

def check_single_instance():
    import socket
    try:
        lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lock_socket.bind(('127.0.0.1', 65432))
        return lock_socket
    except socket.error:
        return None

def main():
    import socket
    current_hostname = socket.gethostname()
    ALLOWED_HOSTNAME = "?⑹슂??026"
    
    # ?몄뒪?몃꽕?꾩쓽 ?몄퐫??臾몄젣(?⑹슂??026 vs 황2026)瑜?怨좊젮?섏뿬 ?좎뿰?섍쾶 泥댄겕
    if "2026" not in current_hostname and current_hostname != ALLOWED_HOSTNAME:
        return

    lock = check_single_instance()
    if not lock:
        return

    log_message(f"?쨼 Antigravity ?붾젅洹몃옩 鍮꾩꽌媛 ?쒖옉?섏뿀?듬땲?? (湲곌린: {current_hostname})")
    
    # ?쒖뒪???덉쟾 諛⑹? ?쒖꽦??    stay_awake.start_stay_awake_thread()
    
    update_id = None
    
    while True:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        params = {"timeout": 60}
        if update_id:
            params["offset"] = update_id
            
        try:
            response = requests.get(url, params=params, timeout=70, verify=False)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    for item in data.get("result", []):
                        update_id = item["update_id"] + 1
                        if "message" in item:
                            threading.Thread(target=process_message, args=(item["message"],)).start()
            else:
                time.sleep(5)
        except Exception as e:
            time.sleep(10)

if __name__ == "__main__":
    main()

