import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/drive'])
sheets_service = build('sheets', 'v4', credentials=creds)
file_id = '1zyIRImgmdR-ocr3gqrmqgDR1Nzt92c8jZUd5sZYs_z8'

rows = [
    [42, '외부', '정은준', 2, 1, '안주환 장학금', '장학금', '1,000,000 ', '', '', ''],
    [43, '외부', '이승기', 2, 2, '안주환 장학금', '장학금', '1,000,000 ', '', '', ''],
    [44, '외부', '이윤건', 3, 4, '안주환 장학금', '장학금', '1,000,000 ', '', '', ''],
    [45, '외부', '조윤성', 3, 5, '안주환 장학금', '장학금', '1,000,000 ', '', '', ''],
    [46, '외부', '박예준', 3, 7, '안주환 장학금', '장학금', '1,000,000 ', '', '', '']
]

sheets_service.spreadsheets().values().append(
    spreadsheetId=file_id,
    range='A6',
    valueInputOption='USER_ENTERED',
    insertDataOption='INSERT_ROWS',
    body={'values': rows}
).execute()
print('SUCCESS')
