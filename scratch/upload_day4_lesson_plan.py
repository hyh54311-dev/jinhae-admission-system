import os, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.stdout.reconfigure(encoding='utf-8')

PARENT_FOLDER_ID = "1L407Q7d36HrcsSPMRWtNJ5b9MufC5k1A"
NEW_FOLDER_NAME = "2026_경남대_마이크로디그리_4일차_이상우강사_수업자료"
LOCAL_DIR = r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\scratch"
TOKEN_PATH = r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\token.json"

creds = Credentials.from_authorized_user_file(TOKEN_PATH, ['https://www.googleapis.com/auth/drive'])
service = build('drive', 'v3', credentials=creds)

# Find or create Day 4 folder
query = f"'{PARENT_FOLDER_ID}' in parents and name = '{NEW_FOLDER_NAME}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
results = service.files().list(q=query, fields='files(id, webViewLink)').execute()
folders = results.get('files', [])

if folders:
    day4_folder_id = folders[0]['id']
    folder_link = folders[0].get('webViewLink')
else:
    folder_metadata = {
        'name': NEW_FOLDER_NAME,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [PARENT_FOLDER_ID]
    }
    new_folder = service.files().create(body=folder_metadata, fields='id, webViewLink').execute()
    day4_folder_id = new_folder.get('id')
    folder_link = new_folder.get('webViewLink')

pdf_path = os.path.join(LOCAL_DIR, "lesson_plan_1InMLEUR.pdf")
file_metadata = {
    'name': '01_이상우강사_제미나이x노트북LM_융합수업기획안_오발탄.pdf',
    'parents': [day4_folder_id]
}
media = MediaFileUpload(pdf_path, mimetype='application/pdf', resumable=False)
service.files().create(body=file_metadata, media_body=media, fields='id').execute()

print(f"Day 4 Folder Link: {folder_link}")
