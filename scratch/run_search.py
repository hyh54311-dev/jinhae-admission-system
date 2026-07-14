import os, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json not found")
        return
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service = build('drive', 'v3', credentials=creds)
    
    query = "mimeType = 'application/vnd.google-apps.spreadsheet' and (name contains '동아리' or name contains '배정' or name contains '결과' or name contains '명단')"
    results = service.files().list(q=query, spaces='drive', orderBy='modifiedTime desc', fields='files(id, name, mimeType)').execute()
    files = results.get('files', [])
    
    with open('scratch/drive_results.txt', 'w', encoding='utf-8') as f:
        f.write(f"Found {len(files)} files:\n")
        for idx, file_info in enumerate(files):
            f.write(f"[{idx+1}] {file_info['name']} | ID: {file_info['id']} | Mime: {file_info['mimeType']}\n")
    print(f"Done. Found {len(files)} files.")

if __name__ == '__main__':
    main()
