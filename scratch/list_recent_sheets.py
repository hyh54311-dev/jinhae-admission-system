import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token.json'

try:
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    drive_service = build('drive', 'v3', credentials=creds)
    
    # List files of type spreadsheet, sorted by modifiedTime descending
    results = drive_service.files().list(
        q="mimeType='application/vnd.google-apps.spreadsheet'",
        orderBy="modifiedTime desc",
        pageSize=10,
        fields="nextPageToken, files(id, name, modifiedTime)"
    ).execute()
    
    files = results.get('files', [])
    print("Recently modified Google Sheets:")
    for file in files:
        print(f"Name: {file['name']}")
        print(f"  ID: {file['id']}")
        print(f"  Modified Time: {file['modifiedTime']}")
        
except Exception as e:
    print("Error:", e)
