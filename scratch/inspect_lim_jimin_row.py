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
        range="탐구보고서_응답!A42:Q42"
    ).execute()
    
    rows = result.get('values', [])
    if rows:
        r = rows[0]
        print("Row 42 Detailed Contents:")
        print(f"제출일시: {r[0] if len(r)>0 else ''}")
        print(f"학번/이름: {r[1]}학년 {r[2]}반 {r[3]}번 {r[4]}")
        print(f"희망진로: {r[5] if len(r)>5 else ''}")
        print(f"작품: {r[6] if len(r)>6 else ''}")
        print(f"주제: {r[7] if len(r)>7 else ''}")
        print(f"세특초안: {r[14] if len(r)>14 else ''}")

if __name__ == '__main__':
    main()
