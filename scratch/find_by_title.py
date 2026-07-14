import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    token_path = 'token.json'
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service = build('sheets', 'v4', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    
    q = "mimeType = 'application/vnd.google-apps.spreadsheet' and name contains '자율' and trashed = false"
    
    try:
        results = drive_service.files().list(q=q, fields='files(id, name)').execute()
        files = results.get('files', [])
        for f in files:
            sid = f['id']
            try:
                metadata = service.spreadsheets().get(spreadsheetId=sid).execute()
                sheets = [s.get('properties', {}).get('title', '') for s in metadata.get('sheets', [])]
                print(f"Spreadsheet: {f['name']} | ID: {sid} | Sheets: {sheets}")
            except Exception as e:
                print(f"Spreadsheet: {f['name']} | ID: {sid} | Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
