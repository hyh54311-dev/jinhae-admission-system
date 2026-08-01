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
        
    student_rows = rows[1:]
    print(f"Total rows: {len(student_rows)}")
    
    file_submits = []
    text_submits = []
    
    for idx, r in enumerate(student_rows, start=2):
        ban = r[2] if len(r) > 2 else ""
        num = r[3] if len(r) > 3 else ""
        name = r[4] if len(r) > 4 else ""
        title = r[7] if len(r) > 7 else ""
        doc_url = r[13] if len(r) > 13 else ""
        
        # text content sum
        text_content = ""
        for c_idx in [8, 9, 10, 11, 12]:
            if len(r) > c_idx:
                text_content += r[c_idx] + "\n"
                
        is_file = "(파일 제출" in text_content or "(파일 제출" in title
        
        info = {
            "row": idx,
            "ban": ban,
            "num": num,
            "name": name,
            "title": title,
            "doc_url": doc_url,
            "is_file": is_file,
            "text_len": len(text_content.strip()),
        }
        
        if is_file:
            file_submits.append(info)
        else:
            text_submits.append(info)
            
    print(f"File submissions: {len(file_submits)}")
    print(f"Text submissions: {len(text_submits)}")
    
    with open("submission_analysis.json", "w", encoding="utf-8") as f:
        json.dump({"file_submits": file_submits, "text_submits": text_submits}, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
