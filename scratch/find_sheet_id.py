import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json not found")
        return
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service = build('drive', 'v3', credentials=creds)
    
    # Search for spreadsheets modified recently
    q = "mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    
    try:
        results = service.files().list(
            q=q, 
            orderBy="modifiedTime desc",
            fields='files(id, name, modifiedTime)',
            pageSize=30
        ).execute()
        files = results.get('files', [])
        for f in files:
            name_bytes = f['name'].encode('utf-8', errors='ignore')
            print(f"Name: {f['name']} | ID: {f['id']} | Modified: {f['modifiedTime']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
