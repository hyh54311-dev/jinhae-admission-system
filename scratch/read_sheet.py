import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# 스프레드시트 ID
SPREADSHEET_ID = "1KgpBoxrQUwiqA86qJr9eB6KAckSNfuC7QJea-m7qiSg"

def get_credentials():
    # 사용 가능한 토큰 파일 후보군
    token_files = ["token.json", "token_calendar.json", "token_tasks.json", "token_gmail.json"]
    creds = None
    
    for token_file in token_files:
        if os.path.exists(token_file):
            print(f"Trying token file: {token_file}")
            try:
                creds = Credentials.from_authorized_user_file(token_file)
                if creds and creds.valid:
                    return creds
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    return creds
            except Exception as e:
                print(f"Error reading {token_file}: {e}")
    return None

def main():
    creds = get_credentials()
    if not creds:
        print("No valid credentials found.")
        return
        
    try:
        service = build("sheets", "v4", credentials=creds)
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        
        print("\n=== Spreadsheet Metadata ===")
        print(f"Title: {spreadsheet.get('properties', {}).get('title')}")
        
        sheets = spreadsheet.get("sheets", [])
        sheet_names = [sheet.get("properties", {}).get("title") for sheet in sheets]
        print(f"Sheets: {sheet_names}")
        
        # 각 시트의 첫 5행을 출력해 봅니다.
        for name in sheet_names[:3]: # 처음 3개 시트만 확인
            print(f"\n--- Data from Sheet: {name} (First 10 rows) ---")
            result = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=f"'{name}'!A1:Z15"
            ).execute()
            rows = result.get("values", [])
            for i, row in enumerate(rows):
                print(f"Row {i+1}: {row}")
                
    except Exception as e:
        print("Error calling Google Sheets API:", e)

if __name__ == "__main__":
    main()
