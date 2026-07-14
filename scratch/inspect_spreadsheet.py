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
    service = build('sheets', 'v4', credentials=creds)
    
    sheet_ids = [
        "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"
    ]
    
    for sid in sheet_ids:
        try:
            metadata = service.spreadsheets().get(spreadsheetId=sid).execute()
            sheets = metadata.get('sheets', [])
            print(f"Spreadsheet Title: {metadata.get('properties').get('title')} | ID: {sid}")
            print("Sheets:")
            for s in sheets:
                print(f" - {s.get('properties').get('title')}")
        except Exception as e:
            print(f"Error inspecting {sid}:", e)

if __name__ == '__main__':
    main()
