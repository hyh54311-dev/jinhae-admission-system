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
            range="탐구보고서_응답!A2:Q2"
        ).execute()
        
        rows = result.get('values', [])
        if not rows:
            print("No data found in row 2")
            return
            
        r = rows[0]
        
        headers_result = service_sheets.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="탐구보고서_응답!A1:Q1"
        ).execute()
        headers = headers_result.get('values', [])[0]
        
        print("--- Go Eun-seok Columns Detailed ---")
        for i in range(len(headers)):
            col_name = headers[i]
            val = r[i] if i < len(r) else ""
            print(f"[{i+1}] {col_name}:")
            print(f"    Length: {len(val)} characters")
            print(f"    Value: {val}")
            print("-" * 50)
            
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
