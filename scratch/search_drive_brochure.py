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

def list_drive_files():
    creds = auth()
    drive_service = build('drive', 'v3', credentials=creds)

    print("Searching Google Drive for files containing '홍보', '책자', '입학', or '2026'...")
    query = "name contains '홍보' or name contains '책자' or name contains '입학' or name contains '요강' or name contains '2026'"
    results = drive_service.files().list(
        q=query,
        pageSize=50,
        fields="nextPageToken, files(id, name, mimeType, webViewLink, createdTime)"
    ).execute()
    
    files = results.get('files', [])
    if not files:
        print("No matching files found in Google Drive.")
    else:
        print("Found files:")
        for file in files:
            print(f"- {file['name']} ({file['mimeType']})")
            print(f"  ID: {file['id']}")
            print(f"  Link: {file['webViewLink']}")
            print(f"  Created: {file['createdTime']}")

if __name__ == '__main__':
    list_drive_files()
