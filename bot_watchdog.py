# -*- coding: utf-8 -*-
"""
Antigravity 봇 프로세스 0-토큰 로컬 감시자 (Watchdog)
- AI 토큰 0개 사용 (순수 로컬 OS 프로세스 점검 + 텔레그램 HTTP API)
- telegram_assistant.py 가 꺼졌거나 다운되면 즉시 재시작 후 텔레그램으로 알림
"""

import os
import sys
import time
import socket
import subprocess
import requests
from dotenv import load_dotenv

# Windows OS 신뢰 인증서 저장소(학내망/기관망 SSL) 자동 연동
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ALLOWED_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_SCRIPT = os.path.join(BASE_DIR, "telegram_assistant.py")

def send_alert(message):
    if not TELEGRAM_TOKEN or not ALLOWED_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": ALLOWED_CHAT_ID, "text": message}, timeout=10)
    except Exception as e:
        print(f"[Watchdog Alert Failed]: {e}")

def is_bot_running():
    """65432 포트로 PING-PONG 헬스체크하여 실시간 응답 가능 여부 검증 (토큰 0개)"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        res = s.connect_ex(('127.0.0.1', 65432))
        if res == 0:
            s.sendall(b"PING")
            reply = s.recv(1024)
            s.close()
            return b"PONG" in reply
        s.close()
        return False
    except Exception:
        return False

CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0

def kill_stuck_bot_processes():
    """멈춘 봇 프로세스 강제 정리"""
    try:
        my_pid = str(os.getpid())
        ps_cmd = f"Get-CimInstance Win32_Process | Where-Object {{ $_.CommandLine -like '*telegram_assistant.py*' }} | Where-Object {{ $_.ProcessId -ne {my_pid} }} | ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force }}"
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
        time.sleep(1)
    except Exception as e:
        print(f"[Watchdog] 프로세스 정리 오류: {e}")

def start_bot_process():
    """봇 프로세스 새로 구동"""
    try:
        kill_stuck_bot_processes()
        cmd = [sys.executable, BOT_SCRIPT]
        subprocess.Popen(cmd, cwd=BASE_DIR, creationflags=CREATE_NO_WINDOW)
        print(f"[Watchdog] Bot restarted successfully.")
        return True
    except Exception as e:
        print(f"[Watchdog] Failed to start bot: {e}")
        return False

def main():
    print("[Watchdog] 0-Token Bot Process Watchdog Started.")
    
    # 봇 최초 상태 점검
    if not is_bot_running():
        print("[Watchdog] Bot is not running on startup. Starting now...")
        start_bot_process()

    consecutive_failures = 0

    while True:
        time.sleep(15)  # 15초 간격 로컬 체크 (토큰 0개)
        if not is_bot_running():
            consecutive_failures += 1
            print(f"[Watchdog Warning] Bot unresponsive ({consecutive_failures}/2)")
            
            if consecutive_failures >= 2:
                print("[Watchdog Alert] Bot confirmed down! Restarting...")
                start_alert_sent = False
                if start_bot_process():
                    time.sleep(5)
                    if is_bot_running():
                        send_alert("🚨 [시스템 알림] 텔레그램 에이전트 봇이 중단되어 백그라운드에서 자동 재시작되었습니다.\n(토큰 소모: 0개)")
                        consecutive_failures = 0
        else:
            consecutive_failures = 0

if __name__ == "__main__":
    main()
