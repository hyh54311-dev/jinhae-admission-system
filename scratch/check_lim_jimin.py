import os
import sys
import io
import json
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
    
    result = service_sheets.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="탐구보고서_응답!A1:Q100"
    ).execute()
    
    rows = result.get('values', [])
    if not rows:
        print("No data found")
        return
        
    print(f"Total rows in sheet: {len(rows)}")
    
    matching_rows = []
    for idx, r in enumerate(rows, start=1):
        grade = r[1] if len(r) > 1 else ""
        ban = r[2] if len(r) > 2 else ""
        num = r[3] if len(r) > 3 else ""
        name = r[4] if len(r) > 4 else ""
        
        if name == "임지민" or (ban == "5" and num == "26"):
            time_stamp = r[0] if len(r) > 0 else ""
            title = r[7] if len(r) > 7 else ""
            doc_url = r[13] if len(r) > 13 else ""
            draft = r[14] if len(r) > 14 else ""
            byte_val = r[15] if len(r) > 15 else ""
            matching_rows.append({
                "row_index": idx,
                "timestamp": time_stamp,
                "grade": grade,
                "ban": ban,
                "num": num,
                "name": name,
                "title": title,
                "doc_url": doc_url,
                "draft": draft,
                "byte_val": byte_val,
                "row_data": r
            })
            
    print(f"Matching rows count: {len(matching_rows)}")
    for m in matching_rows:
        print(f"\nRow {m['row_index']}: [{m['timestamp']}] {m['grade']}학년 {m['ban']}반 {m['num']}번 {m['name']}")
        print(f"   주제: {m['title']}")
        print(f"   구글문서: {m['doc_url']}")
        print(f"   세특초안: {m['draft'][:50]}...")

if __name__ == '__main__':
    main()
