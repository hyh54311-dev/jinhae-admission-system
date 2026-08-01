import os
import sys
import io

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json does not exist")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service = build('drive', 'v3', credentials=creds)
    
    try:
        # Search recent files modified or created in June/July 2026
        query = "modifiedTime > '2026-06-01T00:00:00'"
        results = service.files().list(q=query, spaces='drive', fields="files(id, name, mimeType, webViewLink, createdTime, modifiedTime)", pageSize=100, orderBy="modifiedTime desc").execute()
        files = results.get('files', [])
        
        print(f"Recent files modified after June 2026 ({len(files)} files):")
        for idx, f in enumerate(files):
            print(f"[{idx+1}] {f['name']} | Mime: {f['mimeType']} | Modified: {f.get('modifiedTime')} | Link: {f.get('webViewLink')}")
            
    except Exception as e:
        print("Error searching drive:", e)

if __name__ == '__main__':
    main()
