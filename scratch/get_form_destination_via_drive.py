import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

token_path = 'token.json'
form_id = '1eWucmez2c6h1qT7nwuA0by_GwQaJS8N-N8M0wLZ_qAE'

try:
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    drive_service = build('drive', 'v3', credentials=creds)
    
    # 1. Get the form's parent folders
    form_meta = drive_service.files().get(
        fileId=form_id,
        fields="parents, name"
    ).execute()
    print(f"Form Name: {form_meta.get('name')}")
    parents = form_meta.get('parents', [])
    print(f"Form Parents: {parents}")
    
    for p in parents:
        print("=" * 50)
        print(f"Listing files in parent folder ID: {p}")
        # List all spreadsheets in this folder
        results = drive_service.files().list(
            q=f"'{p}' in parents and mimeType='application/vnd.google-apps.spreadsheet'",
            fields="files(id, name, modifiedTime)"
        ).execute()
        files = results.get('files', [])
        for f in files:
            print(f"  Name: {f['name']}")
            print(f"    ID: {f['id']}")
            print(f"    Modified Time: {f['modifiedTime']}")
            
except Exception as e:
    print("Error:", e)
