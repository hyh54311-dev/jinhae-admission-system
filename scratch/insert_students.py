import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/drive'])
sheets_service = build('sheets', 'v4', credentials=creds)
file_id = '1zyIRImgmdR-ocr3gqrmqgDR1Nzt92c8jZUd5sZYs_z8'

sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=file_id).execute()
sheets = sheet_metadata.get('sheets', '')
main_sheet_name = sheets[0]['properties']['title']

# Fetch existing rows
result = sheets_service.spreadsheets().values().get(spreadsheetId=file_id, range=f"{main_sheet_name}!A5:K").execute()
existing_rows = result.get('values', [])

# Filter out empty rows at the end if any
filtered_existing = []
for r in existing_rows:
    if len(r) > 0 and r[0].strip():
        # Pad row to 11 columns to match A-K
        r = r + [''] * (11 - len(r))
        filtered_existing.append(r)

# New 8 rows
new_data = [
    ('박정빈', '2,000,000 ', '입학내신석차 1등'),
    ('김지환', '1,500,000 ', '입학내신석차 2등'),
    ('김태환', '1,000,000 ', '입학내신석차 3등'),
    ('송성호', '1,000,000 ', '입학내신석차 4등'),
    ('홍지우', '1,000,000 ', '입학내신석차 5등'),
    ('배성윤', '1,000,000 ', '입학내신석차 6등'),
    ('손준원', '1,000,000 ', '입학내신석차 7등'),
    ('허준성', '1,000,000 ', '입학내신석차 8등')
]

# Match existing class if possible from previous rows
name_to_class = {}
for r in filtered_existing:
    if len(r) >= 5 and r[2]:
        name_to_class[r[2]] = r[4]

new_rows = []
for name, amt, rank in new_data:
    # [연번, 구분, 성명, 학, 반, 지원 기관, 명목, 금액, 지원기간, 지원 일자, 비고]
    cls = name_to_class.get(name, '')
    new_rows.append([0, '외부', name, 1, cls, '(재)진해고등학교동창회장학재단', '장학금', amt, '', '', rank])

# Combine and reindex
all_rows = new_rows + filtered_existing
for i, r in enumerate(all_rows):
    r[0] = i + 1

# Clear existing data
sheets_service.spreadsheets().values().clear(
    spreadsheetId=file_id,
    range=f"{main_sheet_name}!A5:K1000"
).execute()

# Write updated data
sheets_service.spreadsheets().values().update(
    spreadsheetId=file_id,
    range=f"{main_sheet_name}!A5",
    valueInputOption='USER_ENTERED',
    body={'values': all_rows}
).execute()

print('SUCCESS')
