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
            orderBy="modifiedTime desc",
            fields='files(id, name, modifiedTime)',
            pageSize=30
        ).execute()
        files = results.get('files', [])
        print(f"Top 30 recently modified spreadsheets:")
        for idx, f in enumerate(files):
            sid = f['id']
            name = f['name']
            try:
                metadata = service.spreadsheets().get(spreadsheetId=sid).execute()
                sheets = [s.get('properties', {}).get('title', '') for s in metadata.get('sheets', [])]
                print(f"[{idx+1}] Name: {name} | ID: {sid} | Sheets: {sheets}")
            except Exception as se:
                print(f"[{idx+1}] Name: {name} | ID: {sid} | Error: {se}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
