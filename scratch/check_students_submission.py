import os
import sys
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

# 3학년 10반 전체 명렬표 (구글 폼의 옵션 데이터와 일치)
class10_roster = {
    1: "최우주",
    2: "강윤태",
    3: "고현종",
    4: "권윤호",
    5: "김기범",
    6: "김상민",
    7: "김석현",
    8: "김우영",
    9: "김우진",
    10: "김지윤",
    11: "김지한",
    12: "노재영",
    13: "노태훈",
    14: "민석준",
    15: "박태환",
    16: "송지한",
    17: "양우석",
    18: "오민환",
    19: "이승주",
    20: "이찬서",
    21: "임석민",
    22: "조민석",
    23: "정지백",
    24: "천수호",
    25: "최은우",
    26: "최재우",
    27: "최주환",
    28: "하정훈",
    29: "허성범",
    30: "홍지원"
}

def verify_submissions():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("Error: token.json does not exist.")
        return
        
    spreadsheet_id = '1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU'
    
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        sheets_service = build('sheets', 'v4', credentials=creds)
        
        # Get sheet metadata to fetch the exact tab title dynamically
        sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', [])
        first_sheet_title = sheets[0].get('properties', {}).get('title')
        
        # Retrieve all values
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{first_sheet_title}'!A:Q"
        ).execute()
        rows = result.get('values', [])
        
        if not rows:
            print("The sheet is empty.")
            return
            
        print(f"Total rows in sheet: {len(rows)}")
        
        submitted_numbers = set()
        submitted_students = {}
        
        # Parse rows (skip header row)
        for idx, row in enumerate(rows[1:], start=2):
            if len(row) < 12:
                continue
                
            class_name = row[1].strip() if row[1] else ""
            student_name_field = row[11].strip() if row[11] else "" # Column L (Col 11) is for Class 10 names
            
            # Check if this row is for 10반 and contains a student name
            if class_name == "10반" and student_name_field:
                # Extract number from name field e.g., "24번 천수호" -> 24
                match = re.match(r'(\d+)번', student_name_field)
                if match:
                    num = int(match.group(1))
                    submitted_numbers.add(num)
                    submitted_students[num] = {
                        'name': student_name_field,
                        'row_idx': idx,
                        'timestamp': row[0]
                    }
                    
        print(f"Unique Class 10 submissions found in sheet: {len(submitted_numbers)}")
        print("\n=== Submission Report ===")
        
        missing_numbers = []
        for num in range(1, 31):
            if num not in submitted_numbers:
                missing_numbers.append(num)
                
        if not missing_numbers:
            print("SUCCESS: All 30 students (No. 1 to 30) from Class 10 have submitted successfully!")
        else:
            print(f"MISSING: {len(missing_numbers)} student(s) have NOT submitted yet:")
            for num in missing_numbers:
                print(f"- {num}번 {class10_roster[num]}")
                
        print("\n=== Submissions in Sheet ===")
        for num in sorted(submitted_students.keys()):
            s = submitted_students[num]
            print(f"[{num}번] {class10_roster[num]} - Submitted at {s['timestamp']} (Row: {s['row_idx']})")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    verify_submissions()
