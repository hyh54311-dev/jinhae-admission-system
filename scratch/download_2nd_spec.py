import os
import sys
import io
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

sys.stdout.reconfigure(encoding='utf-8')
base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
token_path = os.path.join(base_dir, 'token.json')
creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

service = build('drive', 'v3', credentials=creds)
query = "name contains '2차검토' or name contains '추가수정명세'"
results = service.files().list(q=query, fields='files(id, name, mimeType)').execute()
items = results.get('files', [])
print(f"Found {len(items)} files:")
for item in items:
    print(f"- {item['name']} ({item['id']})")
    request = service.files().get_media(fileId=item['id'])
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    save_path = os.path.join(base_dir, 'scratch', 'claude_2nd_review_spec.md')
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(fh.getvalue().decode('utf-8'))
    print(f"Saved to {save_path}, length: {len(fh.getvalue())} bytes")
