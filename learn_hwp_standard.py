import win32com.client
import os

def learn_from_user_file():
    try:
        hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        hwp.XHwpWindows.Item(0).Visible = False
        
        user_file = r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 대강 계획서(2026.04.24).hwp"
        
        if not os.path.exists(user_file):
            print(f"File not found: {user_file}")
            return

        hwp.Open(user_file)
        
        # 전체 텍스트 추출하여 구조 파악
        hwp.InitScan()
        text_content = []
        while True:
            res, text = hwp.GetText()
            if res == 0 or res == 1: # 0: 끝, 1: 텍스트
                break
            text_content.append(text)
        hwp.ReleaseScan()
        
        # 파일로 저장해서 나중에 참고
        with open("hwp_standard_content.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(text_content))
            
        print("SUCCESS: Learned from user file and saved text content to hwp_standard_content.txt")
        hwp.Quit()

    except Exception as e:
        print(f"ERROR: {e}")
        try: hwp.Quit()
        except: pass

if __name__ == "__main__":
    learn_from_user_file()
