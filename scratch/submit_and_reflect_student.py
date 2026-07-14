import datetime
import requests
import urllib3
import openpyxl
import os

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Google Form Info
FORM_URL = "https://docs.google.com/forms/d/1eWucmez2c6h1qT7nwuA0by_GwQaJS8N-N8M0wLZ_qAE/formResponse"

# Field Entry IDs from form parsing
ENTRY_CLASS = "entry.1225269417"
ENTRY_NAME_9 = "entry.1124961061"  # For Class 9
ENTRY_Q16 = "entry.1520619704"
ENTRY_Q17 = "entry.338011484"
ENTRY_Q18 = "entry.1851975331"
ENTRY_Q19 = "entry.1842842402"
ENTRY_Q20 = "entry.962604409"

# Student answers
student_info = {
    "class": "9반",
    "number": 14,
    "name": "박규성",
    "name_with_num": "14번 박규성",
    "q16": "의도하지 않은 상태에서 탐구 목적과는 관계없이 우연적으로 이루어진 발견이 엄청난 의미를 가지고 있음이 드러난 발견",
    "q17": "플레밍",
    "q18": "페니실린이 불안정하다. 박테리아를 죽이는 데 즉각적이지 않았다.",
    "q19": "페니실린의 베타-락탐이 펩타이드 전이 효소와 결합하여 박테리아의 세포벽을 약화시킨다.",
    "q20": "그람 양성균에 없는 박테리아 외막 구조가 있기 때문이다."
}

def submit_google_form():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    payload = {
        ENTRY_CLASS: student_info["class"],
        ENTRY_NAME_9: student_info["name_with_num"],
        ENTRY_Q16: student_info["q16"],
        ENTRY_Q17: student_info["q17"],
        ENTRY_Q18: student_info["q18"],
        ENTRY_Q19: student_info["q19"],
        ENTRY_Q20: student_info["q20"]
    }
    
    print(f"Submitting to Google Form for {student_info['class']} {student_info['name_with_num']}...")
    try:
        response = requests.post(FORM_URL, data=payload, headers=headers, verify=False, timeout=15)
        if response.status_code == 200:
            print(f"=> Google Form Submission SUCCESS (Status Code: {response.status_code})")
            return True
        else:
            print(f"=> Google Form Submission FAILED (Status Code: {response.status_code})")
            return False
    except Exception as e:
        print(f"=> Google Form Submission ERROR: {e}")
        return False

def update_local_excel():
    excel_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\3학년_화법과작문_수행평가_양식.xlsx"
    if not os.path.exists(excel_path):
        print(f"Excel file not found at: {excel_path}")
        return False
        
    try:
        wb = openpyxl.load_workbook(excel_path)
        sheet_name = "수행평가_응답"
        if sheet_name not in wb.sheetnames:
            print(f"Error: sheet '{sheet_name}' not found in Excel.")
            return False
            
        sheet = wb[sheet_name]
        
        # Format current time: YYYY. M. D. 오전/오후 H:MM:SS (matches Google Form style)
        now = datetime.datetime.now()
        hour = now.hour
        am_pm = "오전" if hour < 12 else "오후"
        if hour > 12:
            hour = hour - 12
        elif hour == 0:
            hour = 12
        timestamp_str = f"{now.year}. {now.month}. {now.day}. {am_pm} {hour}:{now.minute:02d}:{now.second:02d}"
        
        # Prepare the new row
        # Col A: 제출일시 (Timestamp)
        # Col B: 반 (Integer)
        # Col C: 번호 (Integer)
        # Col D: 이름 (String)
        # Col E: 16번 답변 (세런디피티)
        # Col F: 17번 답변 (연구 수행자)
        # Col G: 18번 답변 (개발 동기)
        # Col H: 19번 답변 (페니실린 박테리아 억제)
        # Col I: 20번 답변 (그람 음성균 효과 없음)
        new_row = [
            timestamp_str,
            9,  # Class 9
            14, # Number 14
            student_info["name"],
            student_info["q16"],
            student_info["q17"],
            student_info["q18"],
            student_info["q19"],
            student_info["q20"]
        ]
        
        sheet.append(new_row)
        wb.save(excel_path)
        print("=> Local Excel Update SUCCESS")
        return True
    except Exception as e:
        print(f"=> Local Excel Update ERROR: {e}")
        return False

if __name__ == "__main__":
    form_success = submit_google_form()
    excel_success = update_local_excel()
    print("-" * 50)
    print(f"Summary: Form Submission: {'SUCCESS' if form_success else 'FAILED'}, Excel Update: {'SUCCESS' if excel_success else 'FAILED'}")
