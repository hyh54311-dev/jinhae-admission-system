import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token.json'

try:
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    drive_service = build('drive', 'v3', credentials=creds)
    
    # Search for files modified since June 8th 2026 UTC
    # Since today is June 8th Korean time, 
    # let's query files modified after June 7th 12:00:00 UTC (June 7th 21:00:00 KST)
    query = "modifiedTime > '2026-06-07T12:00:00Z'"
    results = drive_service.files().list(
        q=query,
        orderBy="modifiedTime desc",
        pageSize=50,
        fields="files(id, name, mimeType, modifiedTime)"
    ).execute()
    
    files = results.get('files', [])
    print("Files modified since June 7, 2026 UTC:")
    for file in files:
        print(f"Name: {file['name']}")
        print(f"  ID: {file['id']}")
        print(f"  MimeType: {file['mimeType']}")
        print(f"  Modified Time: {file['modifiedTime']}")
        
except Exception as e:
    print("Error:", e)
