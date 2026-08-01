import os
import sys
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json does not exist")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service_sheets = build('sheets', 'v4', credentials=creds)
    
    spreadsheet_id = "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"
    
    try:
        result = service_sheets.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="탐구보고서_응답!A:Q"
        ).execute()
        
        rows = result.get('values', [])
        if not rows:
            print("No data found")
            return
            
        student_rows = rows[1:]
        
        class_counts = {}
        class_students = {}
        
        for idx, r in enumerate(student_rows, start=2):
            grade = r[1] if len(r) > 1 else ""
            ban = r[2] if len(r) > 2 else ""
            num = r[3] if len(r) > 3 else ""
            name = r[4] if len(r) > 4 else ""
            
            # Format class name
            ban_key = int(ban) if ban.isdigit() else ban
            
            if ban_key not in class_counts:
                class_counts[ban_key] = 0
                class_students[ban_key] = []
                
            class_counts[ban_key] += 1
            class_students[ban_key].append(f"{num}번 {name}")
            
        print("Class summary:")
        for ban in sorted(class_counts.keys()):
            students_list = ", ".join(class_students[ban])
            print(f" - {ban}반: {class_counts[ban]}명 ({students_list})")
            
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
