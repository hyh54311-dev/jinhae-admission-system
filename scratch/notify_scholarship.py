import tkinter as tk
import winsound
import sys

def show_scholarship_popup():
    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
    
    root = tk.Tk()
    root.title("장학금 업무 알림")
    
    window_width = 500
    window_height = 200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    x = int((screen_width/2) - (window_width/2))
    y = int((screen_height/2) - (window_height/2))
    
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    root.attributes('-topmost', True)
    root.lift()
    root.focus_force()
    root.after(100, root.focus_force)
    root.configure(bg="#fff3cd")  # 노란색 계열 배경
    
    title_label = tk.Label(root, text="⏰ 안주환 장학금 업무 처리 알림", font=("Malgun Gothic", 16, "bold"), 
                           pady=15, fg="#856404", bg="#fff3cd")
    title_label.pack()
    
    desc_label = tk.Label(root, text="작성해둔 협의록을 바탕으로\n장학생 선발 관련 업무를 진행해 주세요!", 
                          font=("Malgun Gothic", 12), fg="#856404", bg="#fff3cd")
    desc_label.pack(pady=5)
    
    btn = tk.Button(root, text="확인 및 닫기", command=root.destroy, width=15, 
                    font=("Malgun Gothic", 11, "bold"), bg="#ffc107", fg="black", 
                    relief="flat", cursor="hand2")
    btn.pack(side="bottom", pady=20)
    
    root.bind('<Return>', lambda event: root.destroy())
    
    root.mainloop()

if __name__ == "__main__":
    show_scholarship_popup()
