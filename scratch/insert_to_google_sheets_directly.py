import datetime
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

token_path = 'token.json'
spreadsheet_id = '1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU'
sheet_title = '설문지 응답 시트6'

students_data = [
    {
        "class": "8반",
        "num": 4,
        "name_with_num": "4번 김동현",
        "class_col_idx": 9, # index in row (0-based: col J is index 9)
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
        "name_with_num": "11번 박지성",
        "class_col_idx": 7, # index in row (col H is index 7)
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
        "name_with_num": "9번 남지훈",
        "class_col_idx": 5, # index in row (col F is index 5)
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
        "name_with_num": "25번 조준우",
        "class_col_idx": 11, # index in row (col L is index 11)
        "answers": {
            "q16": "과학사에서 의도하지 않은 상태에서 탐구 목적과는 관계없이 우연적으로 이루어진 발견이 엄청난 의미를 가지고 있음이 드러났을 때 그 발견 세런디피티라고 한다.",
            "q17": "플레밍",
            "q18": "페이실린이 불안정하고 박테리아를 죽이는 데 즉각적이지 않다는 점이다.",
            "q19": "페니실린이 트랜스펩티데이스와 임의로 결합하여 박테리아의 세포벽을 약화시킨다.",
            "q20": "그람 양성균에 없는 박테리아 외막 구조가 있기 때문이다."
        }
    }
]

try:
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    sheets_service = build('sheets', 'v4', credentials=creds)
    
    # 1. Fetch current rows to make sure we append correctly
    res = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'{sheet_title}'!A:Q"
    ).execute()
    existing_rows = res.get('values', [])
    print(f"Current rows in {sheet_title}: {len(existing_rows)}")
    
    rows_to_append = []
    
    now = datetime.datetime.now()
    # Format: YYYY. M. D. 오전/오후 H:MM:SS
    hour = now.hour
    am_pm = "오전" if hour < 12 else "오후"
    if hour > 12:
        hour = hour - 12
    elif hour == 0:
        hour = 12
    timestamp_str = f"{now.year}. {now.month}. {now.day}. {am_pm} {hour}:{now.minute:02d}:{now.second:02d}"
    
    for student in students_data:
        # Construct row with 17 elements
        row = [""] * 17
        row[0] = timestamp_str          # Col A: Timestamp
        row[1] = student["class"]       # Col B: Class Selection
        
        # Col C to L (index 2 to 11): Class names dropdowns
        row[student["class_col_idx"]] = student["name_with_num"]
        
        # Col M to Q (index 12 to 16): Q16 to Q20
        row[12] = student["answers"]["q16"]
        row[13] = student["answers"]["q17"]
        row[14] = student["answers"]["q18"]
        row[15] = student["answers"]["q19"]
        row[16] = student["answers"]["q20"]
        
        rows_to_append.append(row)
        print(f"Constructed row for {student['class']} {student['name_with_num']}")

    # 2. Append rows to spreadsheet
    append_res = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"'{sheet_title}'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": rows_to_append}
    ).execute()
    
    print("Append API response:", append_res)
    
    # 3. Verify final row count
    res_verify = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'{sheet_title}'!A:Q"
    ).execute()
    print(f"Verified row count in {sheet_title}: {len(res_verify.get('values', []))}")
    
except Exception as e:
    print("Error:", e)
