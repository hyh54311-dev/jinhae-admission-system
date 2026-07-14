import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token.json'

try:
    creds = Credentials.from_authorized_user_file(token_path)
    drive_service = build('drive', 'v3', credentials=creds)
    
    # Query for all spreadsheet files in Google Drive
    query = "mimeType = 'application/vnd.google-apps.spreadsheet'"
    results = drive_service.files().list(
        q=query,
        pageSize=100,
        fields="nextPageToken, files(id, name, webViewLink, createdTime, modifiedTime, owners)"
    ).execute()
    
    files = results.get('files', [])
    print(f"Found {len(files)} spreadsheet files in Google Drive:\n")
    for f in files:
        owners = ", ".join([o.get('displayName', 'Unknown') for o in f.get('owners', [])])
        print(f"Name: {f.get('name')}")
        print(f"  ID: {f.get('id')}")
        print(f"  Modified: {f.get('modifiedTime')}")
        print(f"  Link: {f.get('webViewLink')}")
        print(f"  Owners: {owners}")
        print("-" * 50)
            
except Exception as e:
    print("Error:", e)
