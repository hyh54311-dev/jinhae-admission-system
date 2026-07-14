import os
import sys
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json does not exist")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service = build('drive', 'v3', credentials=creds)
    
    try:
        query = "mimeType = 'application/vnd.google-apps.spreadsheet'"
        results = service.files().list(
            q=query, 
            spaces='drive', 
            fields="files(id, name, modifiedTime)",
            orderBy="modifiedTime desc"
        ).execute()
        files = results.get('files', [])
        
        print(f"Found {len(files)} spreadsheets sorted by modified time:")
        for idx, f in enumerate(files[:25]): # Print top 25
            print(f"[{idx+1}] {f['name']} | ID: {f['id']} | Modified: {f['modifiedTime']}")
            
    except Exception as e:
        print("Error searching spreadsheets:", e)

if __name__ == '__main__':
    main()
