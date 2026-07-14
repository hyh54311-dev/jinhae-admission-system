import os
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
summary_sheet_name = sheets[1]['properties']['title']

# Fetch data
result = sheets_service.spreadsheets().values().get(spreadsheetId=file_id, range=f"{main_sheet_name}!A5:K").execute()
rows = result.get('values', [])

summary = defaultdict(list)

for row in rows:
    if len(row) < 3 or not row[0]:
        continue
    # row = [연번, 구분, 성명, 학, 반, 지원 기관, 명목, 금액, 지원기간, 지원 일자, 비고]
    org = row[5] if len(row) > 5 else ''
    amt_str = row[7].strip().replace(',', '') if len(row) > 7 else '0'
    try:
        amt = int(amt_str) if amt_str.isdigit() else 0
    except:
        amt = 0
    note = row[10] if len(row) > 10 else ''
    summary[org].append({'amt': amt, 'note': note})

output_rows = [
    ["지급처", "수여 장학생 수", "1인당 지원금액 및 지원 내역", "지원 총액", "특기사항"]
]

total_students = 0
total_sum = 0

for org, students in summary.items():
    if not org: continue
    count = len(students)
    total_students += count
    
    # Group by amounts
    amt_counts = defaultdict(int)
    for s in students:
        amt_counts[s['amt']] += 1
        
    amt_desc_parts = []
    org_sum = 0
    for amt, c in amt_counts.items():
        if amt > 0:
            amt_desc_parts.append(f"{amt:,}원 x {c}명")
            org_sum += amt * c
            total_sum += amt * c
        else:
            amt_desc_parts.append(f"전액지원 등 x {c}명")
            
    amt_desc = "\n".join(amt_desc_parts)
    
    # Collect unique notes
    unique_notes = list(set([s['note'] for s in students if s['note']]))
    note_desc = "\n".join(unique_notes)
    
    output_rows.append([
        org,
        f"{count}명",
        amt_desc,
        f"{org_sum:,}원" if org_sum > 0 else "-",
        note_desc
    ])

output_rows.append([
    "총계",
    f"{total_students}명",
    "",
    f"{total_sum:,}원",
    ""
])

# Clear existing summary sheet data (from A2 downwards)
sheets_service.spreadsheets().values().clear(
    spreadsheetId=file_id,
    range=f"{summary_sheet_name}!A2:E"
).execute()

# Write new data
sheets_service.spreadsheets().values().update(
    spreadsheetId=file_id,
    range=f"{summary_sheet_name}!A1",
    valueInputOption='USER_ENTERED',
    body={'values': output_rows}
).execute()

print('SUCCESS')
