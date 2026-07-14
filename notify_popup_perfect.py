import tkinter as tk
import winsound
import sys
import io

# Force UTF-8 for standard output if needed
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def show_popup():
    # 사운드 알림
    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
    
    root = tk.Tk()
    root.title("Antigravity AI 작업 완료")
    
    # 윈도우 크기 및 위치 설정 (화면 중앙)
    window_width = 450
    window_height = 180
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    x = int((screen_width/2) - (window_width/2))
    y = int((screen_height/2) - (window_height/2))
    
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # 항상 최상단에 표시 및 포커스 강제
    root.attributes('-topmost', True)
    root.lift()
    root.focus_force()
    # 윈도우가 완전히 생성된 후 다시 한번 포커스 강제
    root.after(100, root.focus_force)
    root.configure(bg="#f8f9fa")
    
    # 메인 메시지
    message = "선생님 말씀하신 작업을 완료하였습니다!"
    label = tk.Label(root, text=message, font=("Malgun Gothic", 15, "bold"), 
                     pady=30, fg="#003366", bg="#f8f9fa")
    label.pack(expand=True, fill="both")
    
    # 확인 버튼
    btn = tk.Button(root, text="확인", command=root.destroy, width=15, 
                    font=("Malgun Gothic", 11, "bold"), bg="#003366", fg="white", 
                    relief="flat", cursor="hand2")
    btn.pack(side="bottom", pady=20)
    
    # 엔터 키 바인딩
    root.bind('<Return>', lambda event: root.destroy())
    
    root.mainloop()

if __name__ == "__main__":
    show_popup()
