import os
import sys
import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    env_path = os.path.join(project_dir, '.env')
    
    load_dotenv(env_path)
    
    token = os.getenv("TELEGRAM_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    
    if not token or not chat_id:
        print("Error: TELEGRAM_TOKEN or TELEGRAM_CHAT_ID is missing in .env")
        sys.exit(1)
        
    message = "⏰ [알림] 13시 35분입니다. 학생들에게 문학 탐구보고서를 이번 주 일요일까지 제출하라고 수정해서 안내해야 합니다!"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        res = requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=10, verify=False)
        if res.status_code == 200:
            print("Successfully sent custom deadline telegram reminder.")
        else:
            print(f"Failed to send telegram: {res.text}")
    except Exception as e:
        print(f"Error sending telegram: {e}")

if __name__ == "__main__":
    main()
