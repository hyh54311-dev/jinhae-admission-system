import os
import sys
import io
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json not found")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service = build('drive', 'v3', credentials=creds)
    
    # Query all files modified after 2026-06-01
    query = "modifiedTime > '2026-06-01T00:00:00' and trashed = false"
    
    print("Searching Drive for files modified since June 1, 2026...")
    results = service.files().list(
        q=query, 
        spaces='drive', 
        fields="files(id, name, mimeType, createdTime, modifiedTime)",
        pageSize=30,
        orderBy="modifiedTime desc"
    ).execute()
    files = results.get('files', [])
    
    print(f"Found {len(files)} files:")
    for idx, f in enumerate(files):
        print(f"[{idx+1}] {f['name']} | ID: {f['id']} | Mime: {f['mimeType']} | Modified: {f['modifiedTime']}")

if __name__ == '__main__':
    main()
