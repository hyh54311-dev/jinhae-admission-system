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
        print("token.json missing")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service_sheets = build('sheets', 'v4', credentials=creds)
    spreadsheet_id = "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"
    
    # 1. 시트 메타데이터 (탭 목록)
    sheet_metadata = service_sheets.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')
    print("=== Spreadsheet Sheets List ===")
    for s in sheets:
        title = s.get('properties', {}).get('title')
        sheet_id = s.get('properties', {}).get('sheetId')
        print(f"Sheet Title: {title} (ID: {sheet_id})")
        
        # Read sample first 5 rows of each sheet
        try:
            res = service_sheets.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"'{title}'!A1:Z5"
            ).execute()
            rows = res.get('values', [])
            print(f"  Rows count: {len(rows)}")
            if rows:
                print(f"  Header: {rows[0]}")
        except Exception as e:
            print(f"  Error reading sheet {title}: {e}")

if __name__ == '__main__':
    main()
