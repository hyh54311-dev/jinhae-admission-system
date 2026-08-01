import os, json, re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token.json'
creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
service_sheets = build('sheets', 'v4', credentials=creds)
service_docs = build('docs', 'v1', credentials=creds)

src_spreadsheet_id = '1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY'
res_src = service_sheets.spreadsheets().values().get(spreadsheetId=src_spreadsheet_id, range='탐구보고서_응답!A1:Q200').execute()
rows = res_src.get('values', [])[1:]

permission_issues = []
accessible_docs = []

def extract_file_id(url):
    if not url: return None
    m1 = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if m1: return m1.group(1)
    m2 = re.search(r'id=([a-zA-Z0-9_-]+)', url)
    if m2: return m2.group(1)
    return None

for r in rows:
    ban = r[2] if len(r) > 2 else ''
    num = r[3] if len(r) > 3 else ''
    name = r[4] if len(r) > 4 else ''
    mot = r[8] if len(r) > 8 else ''
    title = r[7] if len(r) > 7 else ''
    doc_url = r[13] if len(r) > 13 else ''
    
    is_file = '(파일 제출)' in mot or '(파일 제출)' in title or doc_url != ''
    if is_file and doc_url:
        f_id = extract_file_id(doc_url)
        if f_id:
            try:
                doc = service_docs.documents().get(documentId=f_id).execute()
                accessible_docs.append((ban, num, name, doc_url))
            except Exception as e:
                permission_issues.append((ban, num, name, doc_url, str(e)))

print(f'Total Docs Checked: {len(accessible_docs) + len(permission_issues)}')
print(f'Accessible Docs: {len(accessible_docs)}')
print(f'Permission Issues: {len(permission_issues)}')
if permission_issues:
    print('\nPermission Issues List:')
    for item in permission_issues:
        print(f' - {item[0]}반 {item[1]}번 {item[2]}: {item[3]}')

# JSON 결과 저장
with open('doc_permission_results.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total': len(accessible_docs) + len(permission_issues),
        'accessible': accessible_docs,
        'issues': permission_issues
    }, f, ensure_ascii=False, indent=2)
