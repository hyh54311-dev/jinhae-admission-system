import os, urllib.request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Save new workbook to local day3_downloads and upload to Google Drive
LOCAL_DIR = r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\scratch\day3_downloads"
TOKEN_PATH = r"g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\token.json"
TARGET_FOLDER_ID = "1ZjvSj25WrSlvg8Amlq6Hhq3BVq7HLfa1"

doc_id = "170cdJIDtPi47zL_bKr6bi8RqhY_LPoNBCwRxY2J2Fw8"
pdf_url = f"https://docs.google.com/document/d/{doc_id}/export?format=pdf"
save_path = os.path.join(LOCAL_DIR, "06_2026_교원_마이크로디그리_참가자_실습_워크북.pdf")

req = urllib.request.Request(pdf_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp, open(save_path, 'wb') as f:
    f.write(resp.read())

creds = Credentials.from_authorized_user_file(TOKEN_PATH, ['https://www.googleapis.com/auth/drive'])
service = build('drive', 'v3', credentials=creds)

file_metadata = {
    'name': '06_2026_교원_마이크로디그리_참가자_실습_워크북.pdf',
    'parents': [TARGET_FOLDER_ID]
}
media = MediaFileUpload(save_path, mimetype='application/pdf', resumable=False)
service.files().create(body=file_metadata, media_body=media, fields='id').execute()
print("Uploaded 06_2026_교원_마이크로디그리_참가자_실습_워크북.pdf to Google Drive!")
