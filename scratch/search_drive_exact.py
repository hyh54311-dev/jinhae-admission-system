import os
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
        # Search specifically for '대신해' or '응답' or '반응' or '기획서'
        query = "name contains '대신해' or name contains '기획서' or name contains '설문' or name contains '응답' or name contains '반응'"
        results = service.files().list(q=query, spaces='drive', fields="files(id, name, mimeType)").execute()
        files = results.get('files', [])
        
        print(f"Found {len(files)} files:")
        for idx, f in enumerate(files):
            print(f"[{idx+1}] {f['name']} | ID: {f['id']} | Mime: {f['mimeType']}")
            
    except Exception as e:
        print("Error searching drive:", e)

if __name__ == '__main__':
    main()
