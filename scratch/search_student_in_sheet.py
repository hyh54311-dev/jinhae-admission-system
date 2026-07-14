import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

token_path = 'token.json'
spreadsheet_id = '1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU'
names = ["김동현", "박지성", "남지훈", "조준우"]

creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
sheets_service = build('sheets', 'v4', credentials=creds)

try:
    meta = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    print("Spreadsheet Title:", meta.get('properties', {}).get('title'))
    for sheet in meta.get('sheets', []):
        title = sheet.get('properties', {}).get('title')
        res = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{title}'!A:Q"
        ).execute()
        values = res.get('values', [])
        
        for name in names:
            found = []
            for r_idx, row in enumerate(values):
                row_str = " ".join([str(cell) for cell in row])
                if name in row_str:
                    found.append((r_idx + 1, row))
            if found:
                print(f"Name '{name}' found in sheet '{title}' {len(found)} times:")
                for r_num, r_val in found:
                    print(f"  Row {r_num}: {r_val[:4]}...")
                    
except Exception as e:
    print("Error:", e)
