import tkinter as tk
from tkinter import messagebox
import winsound
import os

def show_reminder():
    root = tk.Tk()
    root.withdraw() # 硫붿씤 李??④?
    
    # ?뚮┝???ъ깮
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
    
    # 硫붿떆吏 諛뺤뒪 異쒕젰
    messagebox.showinfo(
        "?? 吏꾪빐怨?梨쀫큸 ??諛고룷 ?뚮┝", 
        "?좎깮?? ?쎌냽?섏떊 13?쒖엯?덈떎!\n\n?댁젣 梨쀫큸???뱀뿉 諛고룷?섏뿬 ?꾧뎄???????덇쾶 ???쒓컙?낅땲??\nAntigravity?먭쾶 '諛고룷 ?쒖옉?섏옄'?쇨퀬 留먯???二쇱꽭??"
    )
    root.destroy()

if __name__ == "__main__":
    show_reminder()
