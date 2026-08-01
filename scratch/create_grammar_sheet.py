import os
import sys
import io

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json does not exist")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    sheets_service = build('sheets', 'v4', credentials=creds)
    
    try:
        # Create a new spreadsheet
        spreadsheet = {
            'properties': {
                'title': '2026학년도 2학년 국어 문법 탐구 학습 및 세특 자동화 시스템'
            },
            'sheets': [
                {'properties': {'title': '문법_수행평가_응답'}},
                {'properties': {'title': '문법_조별_응답'}},
                {'properties': {'title': '문법_단어_사전'}},
                {'properties': {'title': 'Sheet1'}}
            ]
        }
        res = sheets_service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId,spreadsheetUrl').execute()
        sheet_id = res.get('spreadsheetId')
        sheet_url = res.get('spreadsheetUrl')
        
        print("==========================================================")
        print("Google Sheet created successfully!")
        print(f"Spreadsheet ID: {sheet_id}")
        print(f"Spreadsheet URL: {sheet_url}")
        print("==========================================================")
        
    except Exception as e:
        print("Error creating spreadsheet:", e)

if __name__ == '__main__':
    main()
