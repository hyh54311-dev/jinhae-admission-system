import os
import sys
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

def list_files():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("Error: token.json does not exist.")
        return
        
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Query Forms and Spreadsheets modified since June 1, 2026
        query = "(mimeType = 'application/vnd.google-apps.form' or mimeType = 'application/vnd.google-apps.spreadsheet') and trashed = false"
        print(f"Listing files with query: {query}")
        
        results = drive_service.files().list(q=query, fields="files(id, name, mimeType, modifiedTime, webViewLink)", orderBy="modifiedTime desc", pageSize=30).execute()
        files = results.get('files', [])
        
        output_path = 'scratch/drive_files_list.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(files, f, ensure_ascii=False, indent=2)
            
        print(f"Saved {len(files)} files information to {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    list_files()
