import os
import subprocess
import socket
import time
import sys

# ----------------- ?ㅼ젙 ----------------- #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_SCRIPT = "telegram_assistant.py"
LOCK_PORT = 65432
RUN_BAT = "run_telegram_assistant.bat"
LOG_FILE = os.path.join(BASE_DIR, "telegram_assistant.log")
# ---------------------------------------- #

def log_maintenance(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    full_message = f"[{timestamp}] [Maintenance] {message}"
    print(full_message)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_message + "\n")
    except:
        pass

def is_bot_running():
    """?좉툑 ?ы듃 ?ъ슜 ?щ?濡?遊?媛???곹깭 ?뺤씤"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', LOCK_PORT))
            return False # ?ы듃瑜??????덉쑝硫?遊뉗씠 ???곌퀬 ?덈뒗 寃?        except socket.error:
            return True # ?ы듃媛 ?대? ?ъ슜 以묒씠硫?遊뉗씠 ?ㅽ뻾 以?
def restart_bot():
    log_maintenance("?좑툘 遊?以묐떒 媛먯?! ?먭? 移섏쑀 ?쒖뒪??媛??..")
    bat_path = os.path.join(BASE_DIR, RUN_BAT)
    if os.path.exists(bat_path):
        try:
            # 諛곗튂 ?뚯씪???듯빐 ?덉쟾?섍쾶 諛깃렇?쇱슫???ъ떆??            subprocess.Popen([bat_path], shell=True, cwd=BASE_DIR)
            log_maintenance("??遊??ъ떆??紐낅졊???꾨떖?덉뒿?덈떎.")
        except Exception as e:
            log_maintenance(f"??遊??ъ떆???ㅽ뙣: {e}")
    else:
        log_maintenance(f"??{RUN_BAT} ?뚯씪??李얠쓣 ???놁뒿?덈떎.")

def main():
    if not is_bot_running():
        restart_bot()
    else:
        # log_maintenance("?윟 遊뉗씠 ?뺤긽?곸쑝濡?媛??以묒엯?덈떎.")
        pass

if __name__ == "__main__":
    main()
