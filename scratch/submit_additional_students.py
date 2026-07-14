import datetime
import requests
import urllib3
import openpyxl
import os

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FORM_URL = "https://docs.google.com/forms/d/1eWucmez2c6h1qT7nwuA0by_GwQaJS8N-N8M0wLZ_qAE/formResponse"

students = [
    {
        "class": "8반",
        "num": 4,
        "name": "김동현",
        "name_with_num": "4번 김동현",
        "name_field": "entry.1818992395",
        "answers": {
            "q16": "과학사에서 의도하지 않은 상태에서 탐구 목적과는 관계없이 우연적으로 이루어진 발견이 엄청난 의미를 가지고 있음이 드러났을 때 그 발견 세런디피티라고 한다.",
            "q17": "플레밍",
            "q18": "페이실린이 불안정하고 박테리아를 죽이는 데 즉각적이지 않다는 점이다. 감염병을 해결하기 위해 백신을 활용하는 것이 각광을 받았기에 의약계에서도 동기가 미약했다.",
            "q19": "페니실린의 베타-락탐은 박테리아의 세포벽을 구성하는 주요 성분인 펩티도글리칸 분자를 형성하는 역할을 하는 펩타이드 전이 효소가 만난다.",
            "q20": "그람 양성균에 없는 박테리아 외막 구조가 있기 때문이다."
        }
    },
    {
        "class": "6반",
        "num": 11,
        "name": "박지성",
        "name_with_num": "11번 박지성",
        "name_field": "entry.1405061817",
        "answers": {
            "q16": "과학사에서 의도하지 않은 상태에서 탐구 목적과는 관계없이 우연적으로 이루어진 발견이 엄청난 의미를 가지고 있음이 드러났을 때 그 발견 세런디피티라고 한다.",
            "q17": "플레밍",
            "q18": "페이실린이 불안정하고 박테리아를 죽이는 데 즉각적이지 않다는 점이다. 감염병을 해결하기 위해 백신을 활용하는 것이 각광을 받았기 때문이다",
            "q19": "페니실린의 베타-락탐은 박테리아의 트랜스펩티데이스와 임의로 결합하여 박테리아의 세포벽을 약화시킨다.",
            "q20": "그람 양성균에 없는 박테리아 외막 구조가 있기 때문이다."
        }
    },
    {
        "class": "4반",
        "num": 9,
        "name": "남지훈",
        "name_with_num": "9번 남지훈",
        "name_field": "entry.1905977477",
        "answers": {
            "q16": "과학사에서 의도하지 않은 상태에서 탐구 목적과는 관계없이 우연적으로 이루어진 발견이 엄청난 의미를 가지고 있음이 드러났을 때 그 발견 세런디피티라고 한다.",
            "q17": "플레밍",
            "q18": "페이실린이 불안정하고 박테리아를 죽이는 데 즉각적이지 않다는 점이다. 감염병을 해결하기 위해 백신을 활용하는 것이 각광을 받았기에 의약계에서도 동기가 미약했다.",
            "q19": "페니실린의 베타-락탐은 박테리아의 트랜스펩티데이스와 임의로 결합하여 박테리아의 세포벽을 약화시킨다.",
            "q20": "그람 양성균에 없는 박테리아 외막 구조가 있기 때문이다."
        }
    },
    {
        "class": "10반",
        "num": 25,
        "name": "조준우",
        "name_with_num": "25번 조준우",
        "name_field": "entry.1385440557",
        "answers": {
            "q16": "과학사에서 의도하지 않은 상태에서 탐구 목적과는 관계없이 우연적으로 이루어진 발견이 엄청난 의미를 가지고 있음이 드러났을 때 그 발견 세런디피티라고 한다.",
            "q17": "플레밍",
            "q18": "페이실린이 불안정하고 박테리아를 죽이는 데 즉각적이지 않다는 점이다.",
            "q19": "페니실린이 트랜스펩티데이스와 임의로 결합하여 박테리아의 세포벽을 약화시킨다.",
            "q20": "그람 양성균에 없는 박테리아 외막 구조가 있기 때문이다."
        }
    }
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

excel_path = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\3학년_화법과작문_수행평가_양식.xlsx"

def submit_to_form(student):
    payload = {
        # Class Selection
        "entry.961434093": student["class"],
        "entry.1225269417": student["class"],
        
        # Name Selection
        student["name_field"]: student["name_with_num"],
        
        # Q16
        "entry.786998359": student["answers"]["q16"],
        "entry.1520619704": student["answers"]["q16"],
        
        # Q17
        "entry.1567984727": student["answers"]["q17"],
        "entry.338011484": student["answers"]["q17"],
        
        # Q18
        "entry.549236679": student["answers"]["q18"],
        "entry.1851975331": student["answers"]["q18"],
        
        # Q19
        "entry.1923200604": student["answers"]["q19"],
        "entry.1842842402": student["answers"]["q19"],
        
        # Q20
        "entry.668103064": student["answers"]["q20"],
        "entry.962604409": student["answers"]["q20"]
    }
    
    try:
        response = requests.post(FORM_URL, data=payload, headers=headers, verify=False, timeout=15)
        if response.status_code == 200:
            print(f"=> Google Form Submission SUCCESS for {student['class']} {student['name_with_num']}")
            return True
        else:
            print(f"=> Google Form Submission FAILED for {student['class']} {student['name_with_num']} (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"=> Google Form Submission ERROR for {student['class']} {student['name_with_num']}: {e}")
        return False

def update_excel(student):
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
        
        now = datetime.datetime.now()
        hour = now.hour
        am_pm = "오전" if hour < 12 else "오후"
        if hour > 12:
            hour = hour - 12
        elif hour == 0:
            hour = 12
        timestamp_str = f"{now.year}. {now.month}. {now.day}. {am_pm} {hour}:{now.minute:02d}:{now.second:02d}"
        
        class_num = int(student["class"].replace("반", ""))
        
        new_row = [
            timestamp_str,
            class_num,
            student["num"],
            student["name"],
            student["answers"]["q16"],
            student["answers"]["q17"],
            student["answers"]["q18"],
            student["answers"]["q19"],
            student["answers"]["q20"]
        ]
        
        sheet.append(new_row)
        wb.save(excel_path)
        print(f"=> Local Excel Update SUCCESS for {student['class']} {student['name_with_num']}")
        return True
    except Exception as e:
        print(f"=> Local Excel Update ERROR for {student['class']} {student['name_with_num']}: {e}")
        return False

if __name__ == "__main__":
    success_form_count = 0
    success_excel_count = 0
    
    for s in students:
        form_res = submit_to_form(s)
        excel_res = update_excel(s)
        if form_res:
            success_form_count += 1
        if excel_res:
            success_excel_count += 1
        print("-" * 50)
        
    print(f"All operations finished! Form success: {success_form_count}/{len(students)}, Excel success: {success_excel_count}/{len(students)}")
