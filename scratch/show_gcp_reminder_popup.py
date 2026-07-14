import tkinter as tk
import winsound
import sys
import io
import webbrowser

# Force UTF-8 for standard output if needed
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def copy_json(root, btn):
    root.clipboard_clear()
    root.clipboard_append('{\n  "force": "true"\n}')
    btn.config(text="복사 완료!", bg="#28a745")
    root.after(1500, lambda: btn.config(text="JSON 복사하기", bg="#495057"))

def open_console():
    webbrowser.open("https://console.cloud.google.com/functions/list")

def show_popup():
    # 사운드 알림
    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
    
    root = tk.Tk()
    root.title("K-듀얼모멘텀 리밸런싱 알림")
    
    # 윈도우 크기 및 위치 설정 (화면 중앙)
    window_width = 580
    window_height = 425
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    x = int((screen_width/2) - (window_width/2))
    y = int((screen_height/2) - (window_height/2))
    
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # 항상 최상단에 표시 및 포커스 강제
    root.attributes('-topmost', True)
    root.lift()
    root.focus_force()
    root.after(100, root.focus_force)
    root.configure(bg="#f8f9fa")
    
    # 타이틀
    title_label = tk.Label(root, text="🔔 구글 클라우드 리밸런싱 실행 안내", font=("Malgun Gothic", 16, "bold"), 
                           pady=15, fg="#003366", bg="#f8f9fa")
    title_label.pack()
    
    # 설명 프레임
    content_frame = tk.Frame(root, bg="#ffffff", bd=1, relief="solid", padx=15, pady=15)
    content_frame.pack(padx=20, pady=5, fill="both", expand=True)
    
    instructions = (
        "구글 클라우드에서 리밸런싱 로봇을 수동 실행할 시간입니다.\n\n"
        "1. [구글 콘솔 바로가기] 버튼을 눌러 Cloud Functions 목록에 접속합니다.\n"
        "2. 리밸런싱 함수를 선택한 후 [테스트(Testing)] 탭을 클릭합니다.\n"
        "3. Triggering event (트리거 이벤트) 입력란의 내용을 지우고\n"
        "   아래의 JSON 강제 실행 옵션을 입력해 주세요:\n\n"
        "   {\n"
        "     \"force\": \"true\"\n"
        "   }\n\n"
        "4. 하단의 [함수 테스트(Test the function)] 버튼을 누릅니다."
    )
    
    desc_label = tk.Label(content_frame, text=instructions, font=("Malgun Gothic", 10), 
                          justify="left", bg="#ffffff", fg="#333333")
    desc_label.pack(anchor="w")
    
    # 버튼 프레임
    btn_frame = tk.Frame(root, bg="#f8f9fa")
    btn_frame.pack(side="bottom", pady=15)
    
    # 복사 버튼
    copy_btn = tk.Button(btn_frame, text="JSON 복사하기", command=lambda: copy_json(root, copy_btn), width=13, 
                         font=("Malgun Gothic", 11, "bold"), bg="#495057", fg="white", 
                         relief="flat", cursor="hand2")
    copy_btn.pack(side="left", padx=5)
    
    # 구글 콘솔 바로가기 버튼
    link_btn = tk.Button(btn_frame, text="구글 콘솔 바로가기", command=open_console, width=17, 
                         font=("Malgun Gothic", 11, "bold"), bg="#0275d8", fg="white", 
                         relief="flat", cursor="hand2")
    link_btn.pack(side="left", padx=5)
    
    # 확인 버튼
    confirm_btn = tk.Button(btn_frame, text="닫기", command=root.destroy, width=10, 
                            font=("Malgun Gothic", 11, "bold"), bg="#003366", fg="white", 
                            relief="flat", cursor="hand2")
    confirm_btn.pack(side="left", padx=5)
    
    # 엔터 키 바인딩 (닫기)
    root.bind('<Return>', lambda event: root.destroy())
    
    root.mainloop()

if __name__ == "__main__":
    show_popup()
