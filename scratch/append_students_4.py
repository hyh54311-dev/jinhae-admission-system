import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/drive'])
sheets_service = build('sheets', 'v4', credentials=creds)
file_id = '1zyIRImgmdR-ocr3gqrmqgDR1Nzt92c8jZUd5sZYs_z8'

rows = [
    [37, '교내', '이성민', 2, 5, '2026학년도 3월 글로컬 학우상', '글로컬 인재상', '30,000 ', '', '', ''],
    [38, '교내', '김민석', 2, 10, '2026학년도 3월 글로컬 학우상', '글로컬 인재상', '30,000 ', '', '', ''],
    [39, '교내', '박정빈', 1, 1, '2026학년도 3월 글로컬 학우상', '솔향 인재상', '20,000 ', '', '', ''],
    [40, '교내', '김태환', 1, 3, '2026학년도 3월 글로컬 학우상', '솔향 인재상', '20,000 ', '', '', ''],
    [41, '교내', '강민준', 2, 10, '2026학년도 3월 글로컬 학우상', '솔향 인재상', '20,000 ', '', '', '']
]

sheets_service.spreadsheets().values().append(
    spreadsheetId=file_id,
    range='A6',
    valueInputOption='USER_ENTERED',
    insertDataOption='INSERT_ROWS',
    body={'values': rows}
).execute()
print('SUCCESS')
