import tkinter as tk
import winsound
import sys
import io

# Force UTF-8 for standard output
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def show_popup():
    # 사운드 알림
    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
    
    root = tk.Tk()
    root.title("Antigravity AI 알림")
    
    # 윈도우 크기 및 위치 설정 (화면 중앙)
    window_width = 500
    window_height = 200
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
    
    # 메인 메시지
    message = "황요한 선생님, 안녕하십니까!\n\n오늘 아침 수능/모의평가 음운론 기출 정리 작업을\n다시 진행하기로 하셨습니다."
    label = tk.Label(root, text=message, font=("Malgun Gothic", 12, "bold"), 
                     pady=20, fg="#1e3a8a", bg="#f8f9fa", justify="center")
    label.pack(expand=True, fill="both")
    
    # 확인 버튼
    btn = tk.Button(root, text="작업 준비 완료", command=root.destroy, width=18, 
                    font=("Malgun Gothic", 11, "bold"), bg="#1e3a8a", fg="white", 
                    relief="flat", cursor="hand2")
    btn.pack(side="bottom", pady=20)
    
    # 엔터 키 바인딩
    root.bind('<Return>', lambda event: root.destroy())
    
    root.mainloop()

if __name__ == "__main__":
    show_popup()
