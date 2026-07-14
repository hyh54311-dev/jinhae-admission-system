# -*- coding: utf-8 -*-
import os
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Force stdout to use UTF-8
sys.stdout.reconfigure(encoding='utf-8')

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

def search_brochures():
    creds = auth()
    drive_service = build('drive', 'v3', credentials=creds)

    print("Searching Google Drive for all PDFs matching '홍보', '책자', '브로슈어', or '요강'...")
    query = "mimeType = 'application/pdf' and (name contains '홍보' or name contains '책자' or name contains '브로슈어' or name contains '요강')"
    results = drive_service.files().list(
        q=query,
        pageSize=100,
        fields="files(id, name, webViewLink, createdTime)"
    ).execute()
    
    files = results.get('files', [])
    if not files:
        print("No matching PDF files found on Google Drive.")
        return
        
    for file in files:
        print(f"- Name: {file['name']}")
        print(f"  ID: {file['id']}")
        print(f"  Link: {file['webViewLink']}")
        print(f"  Created: {file['createdTime']}")

if __name__ == '__main__':
    search_brochures()
