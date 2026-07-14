import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Reconfigure stdout to use UTF-8
sys.stdout.reconfigure(encoding='utf-8')

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
        res = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{title}'!A:Q"
        ).execute()
        values = res.get('values', [])
        print(f"Total rows: {len(values)}")
        if len(values) > 1:
            print("Headers:", values[0])
            print("Last 5 rows:")
            start_row = max(1, len(values) - 5)
            for idx, row in enumerate(values[start_row:]):
                # Print non-empty columns with their indices
                print(f"  Row {start_row + idx + 1}: {row}")
        else:
            print("  Empty or headers only")
except Exception as e:
    print("Error:", e)
