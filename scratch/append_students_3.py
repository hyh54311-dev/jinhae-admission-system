import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/drive'])
sheets_service = build('sheets', 'v4', credentials=creds)
file_id = '1zyIRImgmdR-ocr3gqrmqgDR1Nzt92c8jZUd5sZYs_z8'

data = """
2-2
박준제
2-5
임지민
"""

lines = [line.strip() for line in data.strip().split('\n') if line.strip()]
rows = []
start_idx = 35
for i in range(0, len(lines), 2):
    grade_cls = lines[i]
    name = lines[i+1]
    grade, cls = map(int, grade_cls.split('-'))
    # [연번, 구분, 성명, 학, 반, 지원 기관, 명목, 금액, 지원기간, 지원 일자, 비고]
    row = [start_idx, '외부', name, grade, cls, '창원시장학회', '해외역사문화체험', '-', '', '', '해외역사문화체험비 전액 지원']
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
