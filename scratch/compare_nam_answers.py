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
    res156 = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=f"'{sheet_title}'!A156:Q156"
    ).execute()
    row156 = res156.get('values', [])[0]
    
    res181 = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=f"'{sheet_title}'!A181:Q181"
    ).execute()
    row181 = res181.get('values', [])[0]
    
    print("Row 156 (Original submission at 4:27 PM):")
    print("  Class:", row156[1])
    print("  Name:", row156[5])
    print("  Q16:", row156[12])
    print("  Q17:", row156[13])
    print("  Q18:", row156[14])
    print("  Q19:", row156[15])
    print("  Q20:", row156[16])
    
    print("\nRow 181 (Our direct submission at 8:04 PM):")
    print("  Class:", row181[1])
    print("  Name:", row181[5])
    print("  Q16:", row181[12])
    print("  Q17:", row181[13])
    print("  Q18:", row181[14])
    print("  Q19:", row181[15])
    print("  Q20:", row181[16])
    
except Exception as e:
    print("Error:", e)
