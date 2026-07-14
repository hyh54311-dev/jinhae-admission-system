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
    service = build('sheets', 'v4', credentials=creds)
    file_id = '1zyIRImgmdR-ocr3gqrmqgDR1Nzt92c8jZUd5sZYs_z8'
    
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=file_id, 
            range="'2026_장학금_정리'!A1:E12",
            valueRenderOption='FORMULA'
        ).execute()
        rows = result.get('values', [])
        
        print("Formulas or Values in '2026_장학금_정리':")
        for idx, row in enumerate(rows):
            print(f"Row {idx+1}: {row}")
            
    except Exception as e:
        print("Error fetching formulas:", e)

if __name__ == '__main__':
    main()
