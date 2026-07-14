import os
import sys
import requests
import tkinter as tk
import winsound
import io
import webbrowser
from dotenv import load_dotenv

# Force UTF-8 for stdout/stderr
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

# Load environmental variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8518409134")

reminder_text = (
    "🚨 [정보(AI·SW)교육 직무연수 신청 알림]\n\n"
    "선생님, 오늘(6월 15일)부터 2026년 정보(AI·SW)교육 역량강화 원격 직무연수 신청이 시작됩니다!\n\n"
    "■ 수강 신청 정보:\n"
    "1. 비바샘 원격연수원: 학생 주도성이 살아 있는 에듀테크 활용 수업 외 10강좌 (600명 선착순)\n"
    "2. 티처빌 원격연수원: 수업에 바로 쓰는 AI 로봇 교육 외 5강좌 (400명 선착순)\n\n"
    "■ 신청 및 운영기간:\n"
    "- 2026. 6. 15.(월) ~ 9. 30.(수)\n\n"
    "■ 안내사항:\n"
    "- 연수비는 경상남도교육청 전액 지원\n"
    "- 선착순 모집으로 조기 마감될 수 있으니 서둘러 신청하세요!\n\n"
    "비바샘 바로가기: https://www.vivasam.com\n"
    "티처빌 바로가기: https://www.teacherville.co.kr"
)

def send_telegram():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": reminder_text
    }
    try:
        r = requests.post(url, json=payload, timeout=10, verify=False)
        if r.status_code == 200:
            print("Telegram message sent successfully.")
        else:
            print(f"Failed to send Telegram: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Telegram error: {e}")

def open_websites():
    webbrowser.open("https://www.vivasam.com")
    webbrowser.open("https://www.teacherville.co.kr")

def show_popup():
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
    
    root = tk.Tk()
    root.title("🚨 정보(AI·SW)교육 원격 직무연수 신청 알림")
    
    window_width = 600
    window_height = 420
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    x = int((screen_width/2) - (window_width/2))
    y = int((screen_height/2) - (window_height/2))
    
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.attributes('-topmost', True)
    root.lift()
    root.focus_force()
    root.configure(bg="#0f172a") # Slate Dark
    
    # Title Label
    title_label = tk.Label(
        root, 
        text="🚨 정보(AI·SW)교육 직무연수 신청 개시", 
        font=("Malgun Gothic", 16, "bold"), 
        fg="#3b82f6", 
        bg="#0f172a",
        pady=15
    )
    title_label.pack()
    
    # Text Box
    text_frame = tk.Frame(root, bg="#0f172a")
    text_frame.pack(fill="both", expand=True, padx=20, pady=5)
    
    msg_box = tk.Text(
        text_frame, 
        font=("Malgun Gothic", 11), 
        fg="#cbd5e1", 
        bg="#1e293b", 
        bd=0, 
        padx=10, 
        pady=10, 
        wrap="word"
    )
    msg_box.insert("1.0", reminder_text)
    msg_box.config(state="disabled")
    msg_box.pack(fill="both", expand=True)
    
    # Buttons
    btn_frame = tk.Frame(root, bg="#0f172a")
    btn_frame.pack(side="bottom", fill="x", pady=15)
    
    # Apply Website Button
    btn_open = tk.Button(
        btn_frame, 
        text="연수원 사이트 열기", 
        command=lambda: [open_websites(), root.destroy()], 
        width=20, 
        font=("Malgun Gothic", 11, "bold"), 
        bg="#3b82f6", 
        fg="white", 
        relief="flat", 
        cursor="hand2"
    )
    btn_open.pack(side="left", padx=50)
    
    # Close Button
    btn_close = tk.Button(
        btn_frame, 
        text="닫기", 
        command=root.destroy, 
        width=15, 
        font=("Malgun Gothic", 11, "bold"), 
        bg="#475569", 
        fg="white", 
        relief="flat", 
        cursor="hand2"
    )
    btn_close.pack(side="right", padx=50)
    
    # Bind Enter key
    root.bind('<Return>', lambda event: root.destroy())
    
    root.mainloop()

if __name__ == '__main__':
    send_telegram()
    try:
        show_popup()
    except Exception as e:
        print(f"GUI Error: {e}")
