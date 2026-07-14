import os
import sys
from pyhwpx import Hwp

sys.stdout.reconfigure(encoding='utf-8')

hwp_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\업무 이외\연락망, 배치도\2026.3.5.자 교직원 비상연락처(휴직자포함 전체).hwp"
txt_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\scratch\contacts.txt"

try:
    hwp = Hwp()
    hwp.open(hwp_path)
    # Save as TXT
    hwp.SaveAs(txt_path, "TXT")
    hwp.quit()
    print("Saved as TXT successfully.")
    
    if os.path.exists(txt_path):
        with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        print(f"Extracted content size: {len(content)}")
        lines = content.split('\n')
        print(f"Total lines: {len(lines)}")
        for idx, line in enumerate(lines):
            line_str = line.strip()
            if any(k in line_str for k in ['보건', '행정', '교무', '전화', '번호', '연락처', '팩스']):
                print(f"Line {idx+1}: {line_str}")
    else:
        print("TXT file does not exist.")
except Exception as e:
    print(f"Error: {e}")
