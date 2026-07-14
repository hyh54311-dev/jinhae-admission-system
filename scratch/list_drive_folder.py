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

def list_folder_files():
    creds = auth()
    drive_service = build('drive', 'v3', credentials=creds)

    folder_id = '1HIq4PoF9rCC3D2sgqGPoE0GSOkZ4H-Mf' # 입학요강 학교 홈피 게시용 자료 folder
    print(f"Listing all files in folder: '{folder_id}'...")
    
    query = f"'{folder_id}' in parents"
    results = drive_service.files().list(
        q=query,
        pageSize=100,
        fields="files(id, name, mimeType, webViewLink, createdTime)"
    ).execute()
    
    files = results.get('files', [])
    if not files:
        print("No files found in this folder.")
    else:
        for file in files:
            print(f"- {file['name']} ({file['mimeType']})")
            print(f"  ID: {file['id']}")
            print(f"  Link: {file['webViewLink']}")
            print(f"  Created: {file['createdTime']}")

if __name__ == '__main__':
    list_folder_files()
