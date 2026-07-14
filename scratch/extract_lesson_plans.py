import win32com.client
import os
import time

def extract_info(folder_path):
    hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
    hwp.SetMessageBoxMode(0x00000020) # Suppress some message boxes
    
    results = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".hwp"):
            file_path = os.path.join(folder_path, filename)
            print(f"Processing: {filename}")
            hwp.Open(file_path)
            
            info = {"filename": filename}
            
            # Simple text extraction for keywords
            hwp.InitScan()
            while True:
                res, msg = hwp.GetText()
                if res <= 1:
                    # Look for keywords in msg
                    if "일시" in msg: info["datetime"] = msg.split("일시")[-1].strip()
                    if "장소" in msg: info["location"] = msg.split("장소")[-1].strip()
                    if "대상" in msg: info["target"] = msg.split("대상")[-1].strip()
                    if "과목" in msg: info["subject"] = msg.split("과목")[-1].strip()
                    if "주제" in msg or "단원" in msg: info["topic"] = msg.split("주제")[-1].split("단원")[-1].strip()
                    if res == 1: break
                else:
                    break
            hwp.ReleaseScan()
            
            # Extract teacher name from filename if not found
            # e.g., "공개수업 지도안-(2)(문학)(이병의).hwp"
            import re
            match = re.search(r'\(([^)]+)\)\.hwp', filename)
            if match:
                info["teacher"] = match.group(1)
            
            results.append(info)
            hwp.Run("FileClose") # Close without saving

    hwp.Quit()
    return results

folder = r"D:\OneDrive - 경상남도교육청\바탕 화면\수업 나눔의 날\국어과"
data = extract_info(folder)
for d in data:
    print(d)
