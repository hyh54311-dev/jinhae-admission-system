# -*- coding: utf-8 -*-
import os
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

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

def list_files_in_folder_recursive(drive_service, folder_id, folder_name=""):
    query = f"'{folder_id}' in parents"
    results = drive_service.files().list(
        q=query,
        pageSize=100,
        fields="files(id, name, mimeType, webViewLink, createdTime)"
    ).execute()
    
    files = results.get('files', [])
    for file in files:
        path = f"{folder_name} / {file['name']}" if folder_name else file['name']
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            list_files_in_folder_recursive(drive_service, file['id'], path)
        else:
            print(f"- {path} ({file['mimeType']})")
            print(f"  ID: {file['id']}")
            print(f"  Link: {file['webViewLink']}")
            print(f"  Created: {file['createdTime']}")

def main():
    creds = auth()
    drive_service = build('drive', 'v3', credentials=creds)
    root_folder_id = '1CjULv1KTBoCL_LBTZfQszAxBOrUyQvvk' # 2027학년도 진해고등학교 신입생 입학요강 folder
    
    print(f"Recursively listing all files inside Google Drive folder '{root_folder_id}'...")
    list_files_in_folder_recursive(drive_service, root_folder_id)

if __name__ == '__main__':
    main()
