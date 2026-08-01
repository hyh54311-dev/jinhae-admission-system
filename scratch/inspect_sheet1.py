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
            range="시트1!A1:J10"
        ).execute()
        
        rows = result.get('values', [])
        print("시트1 (A1:J10) Contents:")
        for r in rows:
            print(r)
            
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
