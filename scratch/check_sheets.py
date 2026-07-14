import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token.json'
spreadsheet_id = '1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU'

try:
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    sheets_service = build('sheets', 'v4', credentials=creds)
    
    meta = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    print("Spreadsheet Title:", meta.get('properties', {}).get('title'))
    print("Sheets inside:")
    for sheet in meta.get('sheets', []):
        title = sheet.get('properties', {}).get('title')
        print(f" - {title}")
        
        # Get last 10 rows
        res = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{title}'!A:J"
        ).execute()
        values = res.get('values', [])
        print(f"   Total rows: {len(values)}")
        if values:
            print("   Headers:", values[0])
            print("   Last 5 rows:")
            for row in values[-5:]:
                print("     ", row)
        else:
            print("   Empty sheet")
            
except Exception as e:
    print("Error:", e)
