import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token.json'
spreadsheet_id = '1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU'

creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
sheets_service = build('sheets', 'v4', credentials=creds)

try:
    meta = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    print("Spreadsheet Title:", meta.get('properties', {}).get('title'))
    for sheet in meta.get('sheets', []):
        title = sheet.get('properties', {}).get('title')
        print("=" * 60)
        print(f"Sheet Title: {title}")
        try:
            res = sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"'{title}'!A:J"
            ).execute()
            values = res.get('values', [])
            print(f"Total rows: {len(values)}")
            if len(values) > 1:
                print("Headers:", values[0])
                print("Last 3 rows:")
                start_row = max(1, len(values) - 3)
                for idx, row in enumerate(values[start_row:]):
                    print(f"  Row {start_row + idx + 1}: {row}")
            else:
                print("  Empty or headers only")
        except Exception as sheet_err:
            print(f"  Error reading sheet {title}: {sheet_err}")
except Exception as e:
    print("Error:", e)
