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
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service_sheets = build('sheets', 'v4', credentials=creds)
    spreadsheet_id = "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"
    
    result = service_sheets.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="탐구보고서_응답!A1:Q10"
    ).execute()
    
    rows = result.get('values', [])
    print(f"Total rows retrieved: {len(rows)}")
    for idx, r in enumerate(rows):
        b = r[2] if len(r)>2 else ""
        n = r[3] if len(r)>3 else ""
        name = r[4] if len(r)>4 else ""
        title = r[7] if len(r)>7 else ""
        print(f"Row {idx+1}: {b}반 {n}번 {name} | Title: {title}")

if __name__ == '__main__':
    main()
