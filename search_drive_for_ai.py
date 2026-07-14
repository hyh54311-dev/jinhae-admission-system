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
        # Search for files containing 'AI' or '동아리'
        query = "name contains 'AI' or name contains '동아리' or name contains '컴퓨터'"
        results = service.files().list(q=query, spaces='drive', fields="files(id, name, mimeType)").execute()
        files = results.get('files', [])
        
        print(f"Found {len(files)} files in Google Drive:")
        for idx, f in enumerate(files):
            print(f"[{idx+1}] {f['name']} | ID: {f['id']} | Mime: {f['mimeType']}")
            
    except Exception as e:
        print("Error searching drive:", e)

if __name__ == '__main__':
    main()
