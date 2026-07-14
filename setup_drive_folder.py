import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_NAME = "二쇱쨷 寃쎌젣?댁뒪_?꾩넚"
DOC_ID = "16inISFZhc17T2vldQ6wGXBpiB8UZSbHbvBH5lfu3tlE"

def auth():
    creds = None
    if os.path.exists('token.json'):
        cr = Credentials.from_authorized_user_file('token.json', SCOPES)
        if cr and cr.expired and cr.refresh_token:
            cr.refresh(Request())
            with open('token.json', 'w') as token:
                token.write(cr.to_json())
        creds = cr
    return creds

def setup():
    creds = auth()
    drive_service = build('drive', 'v3', credentials=creds)

    # 1. Check if folder exists
    query = f"mimeType='application/vnd.google-apps.folder' and name='{FOLDER_NAME}' and trashed = false"
    results = drive_service.files().list(q=query, spaces='drive', fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    
    if not items:
        # Create folder
        folder_metadata = {
            'name': FOLDER_NAME,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')
        print(f"FOLDER_CREATED: {folder_id}")
    else:
        folder_id = items[0].get('id')
        print(f"FOLDER_EXISTS: {folder_id}")

    # 2. Move file
    file = drive_service.files().get(fileId=DOC_ID, fields='parents').execute()
    previous_parents = ",".join(file.get('parents', []))
    drive_service.files().update(
        fileId=DOC_ID,
        addParents=folder_id,
        removeParents=previous_parents,
        fields='id, parents'
    ).execute()
    print("FILE_MOVED_SUCCESSFULLY")

    # Write folder ID to a local config so daily_news.py can use it without hardcoding if I want,
    # but I will just print it and inject it directly into daily_news.py
    print(f"USE_FOLDER_ID: {folder_id}")

if __name__ == '__main__':
    setup()
