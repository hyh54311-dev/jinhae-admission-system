import json
from collections import defaultdict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/drive'])
sheets_service = build('sheets', 'v4', credentials=creds)
file_id = '1zyIRImgmdR-ocr3gqrmqgDR1Nzt92c8jZUd5sZYs_z8'

sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=file_id).execute()
sheets = sheet_metadata.get('sheets', '')
main_sheet_name = sheets[0]['properties']['title']

result = sheets_service.spreadsheets().values().get(spreadsheetId=file_id, range=f'{main_sheet_name}!A5:K').execute()
rows = result.get('values', [])

students_count = defaultdict(list)
grade_counts_distinct = defaultdict(set)
grade_counts_total = defaultdict(int)

for row in rows:
    if len(row) < 5 or not row[0]:
        continue
    name = row[2].strip()
    grade = row[3].strip()
    cls = row[4].strip()
    org = row[5].strip() if len(row) > 5 else ''
    
    uid = f'{grade}학년 {cls}반 {name}'
    students_count[uid].append(org)
    grade_counts_distinct[grade].add(uid)
    grade_counts_total[grade] += 1

print('---DUPLICATES---')
for uid, orgs in students_count.items():
    if len(orgs) > 1:
        print(f'{uid}: {len(orgs)}회 ({", ".join(orgs)})')

print('---GRADE_COUNTS---')
for g in sorted(grade_counts_distinct.keys()):
    print(f'{g}학년: 수혜 건수 {grade_counts_total[g]}건 / 실제 수혜 학생 {len(grade_counts_distinct[g])}명')
