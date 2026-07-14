import os
from pyhwpx import Hwp

def inspect_hwp():
    path = r'D:\OneDrive - 경상남도교육청\바탕 화면\[최종] 2학년 문학_오발탄_심화학습.hwp'
    hwp = Hwp(visible=False)
    try:
        hwp.open(path)
        hwp.InitScan()
        text = ""
        while True:
            res = hwp.GetText()
            if res[0] in [0, 1]:  # 0: EOF, 1: Error
                break
            text += res[1]
        hwp.ReleaseScan()
        
        with open('template_dump.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Template extracted successfully.")
    except Exception as e:
        print("Error:", e)
    finally:
        hwp.quit()

if __name__ == "__main__":
    inspect_hwp()
