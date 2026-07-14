import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token.json'
candidate_ids = [
    '1uXPT8g0wc8-Ryufwk3yTr2RmX5TMraW4v5t9mBxpKYw',
    '1CtFAtJnysSLa1JWExpPXzImvCxvvZcDU4OuiLqV0p10',
    '1-TMsohbrUwaifTPpnSbrlU72nOjqiPIvYbKluSjLBsk',
    '1uwzh7t2K5igDR3UX5OYfQl2-tBqurlD9opzJCjsQuiI',
    '1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU'
]

creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
sheets_service = build('sheets', 'v4', credentials=creds)

for sid in candidate_ids:
    print("=" * 60)
    print(f"Checking Spreadsheet ID: {sid}")
    try:
        meta = sheets_service.spreadsheets().get(spreadsheetId=sid).execute()
        title = meta.get('properties', {}).get('title')
        print(f"Title: {title}")
        sheets = [s.get('properties', {}).get('title') for s in meta.get('sheets', [])]
        print(f"Sheets: {sheets}")
        
        # Check sheet with name like '설문지 응답 1' or '수행평가_응답'
        for sheet_title in sheets:
            if '응답' in sheet_title or '설문' in sheet_title or '시트' in sheet_title:
                res = sheets_service.spreadsheets().values().get(
                    spreadsheetId=sid,
                    range=f"'{sheet_title}'!A:J"
                ).execute()
                values = res.get('values', [])
                print(f"  [{sheet_title}] Total rows: {len(values)}")
                if values:
                    print(f"    Headers: {values[0]}")
                    print(f"    Last row: {values[-1]}")
    except Exception as e:
        print(f"Error checking {sid}: {e}")
