import win32com.client
import os

def extract_hwp_text(file_path):
    try:
        hwp = win32com.client.gencache.EnsureDispatch("HWPFrame.HwpObject")
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckDLL")
        hwp.Open(file_path)
        
        # Get all text
        text = ""
        hwp.InitScan()
        while True:
            res, msg = hwp.GetText()
            if res <= 1: # 0: next, 1: end of list, 2: end of doc
                text += msg
                if res == 1: break
            else:
                break
        hwp.ReleaseScan()
        hwp.Quit()
        return text
    except Exception as e:
        return str(e)

test_file = r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 나눔의 날\국어과\공개수업 지도안-(2)(문학)(이병의).hwp"
print(f"Extracting from: {test_file}")
print(extract_hwp_text(test_file))
