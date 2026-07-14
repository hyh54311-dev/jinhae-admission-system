import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

def find_form_and_sheet():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("Error: token.json does not exist.")
        return
        
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
                
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Search for Google Forms and Spreadsheets
        query = "(mimeType = 'application/vnd.google-apps.form' or mimeType = 'application/vnd.google-apps.spreadsheet') and name contains '수행평가' and trashed = false"
        print(f"Searching Drive with query: {query}")
        results = drive_service.files().list(q=query, fields="files(id, name, mimeType, webViewLink, createdTime, modifiedTime)").execute()
        files = results.get('files', [])
        
        if not files:
            print("No matching files found in Google Drive.")
            return
            
        print(f"Found {len(files)} matching file(s):")
        for f in files:
            print(f"- Name: {f['name']}")
            print(f"  ID: {f['id']}")
            print(f"  MimeType: {f['mimeType']}")
            print(f"  CreatedTime: {f['createdTime']}")
            print(f"  ModifiedTime: {f['modifiedTime']}")
            print(f"  WebViewLink: {f['webViewLink']}")
            print("-" * 40)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    find_form_and_sheet()
