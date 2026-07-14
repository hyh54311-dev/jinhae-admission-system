import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("Error: token.json does not exist.")
        return
        
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        drive_service = build('drive', 'v3', credentials=creds)
        sheets_service = build('sheets', 'v4', credentials=creds)
        
        # List recent spreadsheets
        query = "mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
        results = drive_service.files().list(q=query, fields="files(id, name, modifiedTime)", orderBy="modifiedTime desc", pageSize=30).execute()
        files = results.get('files', [])
        
        print(f"Total spreadsheets found: {len(files)}")
        for f in files:
            file_id = f['id']
            file_name = f['name']
            
            try:
                sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=file_id).execute()
                sheet_titles = [s['properties']['title'] for s in sheet_metadata.get('sheets', [])]
                print(f"Name: {file_name}")
                print(f"ID: {file_id}")
                print(f"Sheets: {sheet_titles}")
                print("-" * 50)
            except Exception as e:
                print(f"Error reading {file_name}: {e}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
