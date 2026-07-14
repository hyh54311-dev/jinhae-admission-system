import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

token_path = 'token.json'
spreadsheet_id = '1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU'
sheet_title = '설문지 응답 시트6'

creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
sheets_service = build('sheets', 'v4', credentials=creds)

try:
    res = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'{sheet_title}'!A178:Q182"
    ).execute()
    values = res.get('values', [])
    print("Rows 178 to 182:")
    for idx, row in enumerate(values):
        print(f"  Row {178 + idx}: {row}")
except Exception as e:
    print("Error:", e)
