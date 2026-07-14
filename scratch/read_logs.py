import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token.json'
spreadsheet_id = '12bXJl_SRj8mVIZBBADWix8ZZ5Rh7XKFodH62iGzDTF8'

try:
    creds = Credentials.from_authorized_user_file(token_path)
    sheets_service = build('sheets', 'v4', credentials=creds)
    
    meta = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    title = meta.get('properties', {}).get('title')
    print("Spreadsheet Title:", title)
    
    sheet_name = meta.get('sheets', [])[0].get('properties', {}).get('title')
    print("Reading sheet:", sheet_name)
    
    res = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'{sheet_name}'!A:C"
    ).execute()
    
    values = res.get('values', [])
    print(f"Total entries: {len(values)}")
    if len(values) > 1:
        print("\nLast 5 Q&A Logs:")
        for idx, row in enumerate(values[-5:], 1):
            time_val = row[0] if len(row) > 0 else 'N/A'
            q_val = row[1] if len(row) > 1 else 'N/A'
            a_val = row[2][:50] + "..." if len(row) > 2 else 'N/A'
            print(f"[{idx}] Time: {time_val}")
            print(f"    Q: {q_val}")
            print(f"    A: {a_val}")
            print("-" * 40)
            
except Exception as e:
    print("Error:", e)
