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
        # Search all spreadsheets & scripts
        query = "mimeType = 'application/vnd.google-apps.script' or mimeType = 'application/vnd.google-apps.spreadsheet'"
        results = service.files().list(q=query, spaces='drive', fields="files(id, name, mimeType, webViewLink, createdTime)", pageSize=100).execute()
        files = results.get('files', [])
        
        print(f"Total Apps Script and Spreadsheets found: {len(files)}")
        for idx, f in enumerate(files):
            print(f"[{idx+1}] {f['name']} | ID: {f['id']} | Mime: {f['mimeType']} | Created: {f.get('createdTime')} | Link: {f.get('webViewLink')}")
            
    except Exception as e:
        print("Error searching drive:", e)

if __name__ == '__main__':
    main()
