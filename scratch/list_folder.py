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
    
    folder_id = '11dDs5GL4bldSNAByJ0Gjs1jTFBVHqDRYbXaIqyRIHvpZxOdeP2T154UyNedqs-FqOuD3k9dU'
    try:
        query = f"'{folder_id}' in parents"
        results = service.files().list(q=query, fields='files(id, name, mimeType)').execute()
        files = results.get('files', [])
        
        print(f"Found {len(files)} files in folder:")
        for idx, f in enumerate(files):
            sys.stdout.buffer.write(f"[{idx+1}] {f['name']} (ID: {f['id']})\n".encode('utf-8'))
    except Exception as e:
        print("Error listing folder:", e)

if __name__ == '__main__':
    main()
