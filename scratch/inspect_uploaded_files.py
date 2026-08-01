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
    service_drive = build('drive', 'v3', credentials=creds)
    
    spreadsheet_id = "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"
    
    result = service_sheets.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="탐구보고서_응답!A1:Q100"
    ).execute()
    
    rows = result.get('values', [])
    if not rows:
        return
        
    student_rows = rows[1:]
    
    for idx, r in enumerate(student_rows, start=2):
        ban = r[2] if len(r) > 2 else ""
        num = r[3] if len(r) > 3 else ""
        name = r[4] if len(r) > 4 else ""
        title = r[7] if len(r) > 7 else ""
        c_mot = r[8] if len(r) > 8 else ""
        doc_url = r[13] if len(r) > 13 else ""
        
        if "(파일 제출" in c_mot or "(파일 제출" in title:
            print(f"Row {idx}: {ban}반 {num}번 {name} | URL: {doc_url}")
            # check file metadata from drive
            import re
            m = re.search(r'/d/([a-zA-Z0-9_-]+)', doc_url)
            if m:
                file_id = m.group(1)
                try:
                    f_meta = service_drive.files().get(fileId=file_id, fields="id, name, mimeType").execute()
                    print(f"   Drive File: Name={f_meta.get('name')}, MimeType={f_meta.get('mimeType')}")
                except Exception as e:
                    print(f"   Drive Error: {e}")

if __name__ == '__main__':
    main()
