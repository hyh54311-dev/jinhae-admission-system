import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

def find_recent_sheets():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("Error: token.json does not exist.")
        return
        
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Search for spreadsheets modified in June 2026
        query = "mimeType = 'application/vnd.google-apps.spreadsheet' and modifiedTime > '2026-06-01T00:00:00Z' and trashed = false"
        print(f"Searching for spreadsheets with query: {query}")
        results = drive_service.files().list(q=query, fields="files(id, name, createdTime, modifiedTime, webViewLink)", orderBy="modifiedTime desc").execute()
        files = results.get('files', [])
        
        if not files:
            print("No matching spreadsheets found.")
            return
            
        print(f"Found {len(files)} matching spreadsheet(s):")
        for f in files:
            print(f"- Name: {f['name']}")
            print(f"  ID: {f['id']}")
            print(f"  ModifiedTime: {f['modifiedTime']}")
            print(f"  WebViewLink: {f['webViewLink']}")
            print("-" * 40)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    find_recent_sheets()
