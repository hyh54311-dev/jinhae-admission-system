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
        metadata = service_sheets.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = metadata.get('sheets', [])
        print("Sheets in this spreadsheet:")
        for s in sheets:
            props = s.get('properties', {})
            print(f" - Title: {props.get('title')}, Sheet ID: {props.get('sheetId')}, Index: {props.get('index')}")
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
