# -*- coding: utf-8 -*-
import os
import sys
import json
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

def read_doc_or_sheet():
    creds = auth()
    drive_service = build('drive', 'v3', credentials=creds)
    
    file_id = '12bXJl_SRj8mVIZBBADWix8ZZ5Rh7XKFodH62iGzDTF8'
    print(f"Fetching metadata for file ID: {file_id}")
    file_meta = drive_service.files().get(fileId=file_id, fields="name, mimeType").execute()
    print(f"File Name: {file_meta.get('name')}")
    print(f"MimeType: {file_meta.get('mimeType')}")
    
    mime_type = file_meta.get('mimeType')
    
    if 'document' in mime_type:
        docs_service = build('docs', 'v1', credentials=creds)
        doc = docs_service.documents().get(documentId=file_id).execute()
        print("Reading Google Doc content...")
        text = ""
        for element in doc.get('body').get('content'):
            if 'paragraph' in element:
                for run in element.get('paragraph').get('elements'):
                    if 'textRun' in run:
                        text += run.get('textRun').get('content')
        
        # Save content locally
        out_path = os.path.join(base_dir, "scratch", "drive_doc_content.txt")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Content saved to {out_path} (length: {len(text)} characters)")
        
    elif 'spreadsheet' in mime_type:
        sheets_service = build('sheets', 'v4', credentials=creds)
        sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=file_id).execute()
        sheets = sheet_metadata.get('sheets', [])
        print(f"Spreadsheet contains {len(sheets)} sheets.")
        
        all_data = {}
        for s in sheets:
            title = s.get('properties').get('title')
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=file_id, range=title
            ).execute()
            rows = result.get('values', [])
            all_data[title] = rows
            print(f"Sheet '{title}': {len(rows)} rows found.")
            
        out_path = os.path.join(base_dir, "scratch", "drive_doc_content.txt")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(all_data, ensure_ascii=False, indent=2))
        print(f"Content saved to {out_path}")
    else:
        print("Unsupported MimeType for direct reading.")

if __name__ == '__main__':
    read_doc_or_sheet()
