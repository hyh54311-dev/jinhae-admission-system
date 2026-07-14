# -*- coding: utf-8 -*-
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']
base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
token_path = os.path.join(base_dir, 'token.json')

def auth():
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, 'w') as f:
                f.write(creds.to_json())
        else:
            raise Exception("token.json is missing or invalid.")
    return creds

def list_pdfs():
    creds = auth()
    drive_service = build('drive', 'v3', credentials=creds)

    print("Listing ALL PDF files on Google Drive...")
    query = "mimeType = 'application/pdf'"
    results = drive_service.files().list(
        q=query,
        pageSize=100,
        fields="files(id, name, webViewLink, createdTime)"
    ).execute()
    
    files = results.get('files', [])
    for file in files:
        print(f"- {file['name']}")
        print(f"  ID: {file['id']}")
        print(f"  Link: {file['webViewLink']}")
        print(f"  Created: {file['createdTime']}")

if __name__ == '__main__':
    list_pdfs()
