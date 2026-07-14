import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    token_path = 'token.json'
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service = build('sheets', 'v4', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    
    q = "mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    
    try:
        results = drive_service.files().list(
            q=q, 
            fields='files(id, name)',
            pageSize=100
        ).execute()
        files = results.get('files', [])
        print(f"Searching {len(files)} spreadsheets for '쉬었음'...")
        for f in files:
            sid = f['id']
            try:
                metadata = service.spreadsheets().get(spreadsheetId=sid).execute()
                sheets = [s.get('properties', {}).get('title', '') for s in metadata.get('sheets', [])]
                for s in sheets:
                    if '쉬었음' in s:
                        print(f"MATCH: Spreadsheet Title: {f['name']} | ID: {sid} | Sheets: {sheets}")
                        break
            except Exception:
                pass
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
