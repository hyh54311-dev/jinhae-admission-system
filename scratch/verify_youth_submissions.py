import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    token_path = 'token.json'
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service = build('sheets', 'v4', credentials=creds)
    
    # Correct Spreadsheet ID verified
    spreadsheet_id = '1VU8Kwa7c5wD0LlFaQaHoAmVt-Il9saOt6e9iGXqQReQ'
    
    # We will get sheet metadata to see the exact sheet names
    metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheet_names = [s.get('properties', {}).get('title', '') for s in metadata.get('sheets', [])]
    print(f"Sheet titles in spreadsheet: {sheet_names}")
    
    for s_name in sheet_names:
        print(f"\n=== Reading Sheet: {s_name} ===")
        try:
            res = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"'{s_name}'!A1:D15"
            ).execute()
            rows = res.get('values', [])
            print(f"Total rows retrieved: {len(rows)}")
            for idx, r in enumerate(rows):
                print(f"  Row {idx+1}: {r}")
        except Exception as e:
            print(f"  Error reading: {e}")

if __name__ == '__main__':
    main()
