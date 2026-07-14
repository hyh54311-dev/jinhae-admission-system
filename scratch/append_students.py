import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/drive'])
sheets_service = build('sheets', 'v4', credentials=creds)
file_id = '1zyIRImgmdR-ocr3gqrmqgDR1Nzt92c8jZUd5sZYs_z8'

data = """
1-9
김태우
1-10
김민규
2-6
김재휘
2-8
오예준
3-1
김은호
3-4
조은성
"""

lines = [line.strip() for line in data.strip().split('\n') if line.strip()]
rows = []
start_idx = 27
for i in range(0, len(lines), 2):
    grade_cls = lines[i]
    name = lines[i+1]
    grade, cls = map(int, grade_cls.split('-'))
    row = [start_idx, '외부', name, grade, cls, '(재)창원시장학회', '장학금', '500,000 ', '', '', '']
    rows.append(row)
    start_idx += 1

sheets_service.spreadsheets().values().append(
    spreadsheetId=file_id,
    range='A6',
    valueInputOption='USER_ENTERED',
    insertDataOption='INSERT_ROWS',
    body={'values': rows}
).execute()
print('SUCCESS')
