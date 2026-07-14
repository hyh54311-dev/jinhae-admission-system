import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']

def upload_and_share():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("Error: token.json does not exist.")
        return
        
    desktop_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면"
    pdf_files = ["1안.pdf", "2안.pdf", "3안.pdf", "4안.pdf"]
    folder_id = "1tHvEWDBtEoTURFy6xMps8qAELZbyidP9" # Workspace folder ID
    
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
        drive_service = build('drive', 'v3', credentials=creds)
        
        uploaded_links = {}
        
        for name in pdf_files:
            file_path = os.path.join(desktop_dir, name)
            if not os.path.exists(file_path):
                print(f"Error: {name} not found on Desktop.")
                continue
                
            print(f"Uploading {name} to Google Drive...")
            file_metadata = {
                'name': name,
                'parents': [folder_id]
            }
            media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=True)
            
            # Create/upload the file
            file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            file_id = file.get('id')
            view_link = file.get('webViewLink')
            
            # Set permission to anyone with link can view (reader)
            print(f"Setting permission for {name} to anyone with link...")
            permission_metadata = {
                'role': 'reader',
                'type': 'anyone'
            }
            drive_service.permissions().create(
                fileId=file_id,
                body=permission_metadata
            ).execute()
            
            # Retrieve shareable link (often webViewLink is sufficient, but we can clean it)
            uploaded_links[name] = view_link
            print(f"Uploaded {name} successfully. Link: {view_link}")
            print("-" * 50)
            
        # Write links to a text file for reference
        with open("scratch/uploaded_pdf_links.json", "w", encoding="utf-8") as f:
            import json
            json.dump(uploaded_links, f, ensure_ascii=False, indent=2)
            
        print("All uploads complete and links saved.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    upload_and_share()
