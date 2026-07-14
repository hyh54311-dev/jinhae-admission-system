import os
import sys
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']

def upload_images():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("Error: token.json does not exist. Please authorize first.")
        return
        
    image_names = ["1안.png", "2안.png", "3안.png", "4안.png"]
    input_dir = "scratch"
    folder_id = "1tHvEWDBtEoTURFy6xMps8qAELZbyidP9"
    
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
        drive_service = build('drive', 'v3', credentials=creds)
        uploaded_image_ids = {}
        
        for name in image_names:
            file_path = os.path.join(input_dir, name)
            if not os.path.exists(file_path):
                print(f"Error: {file_path} not found.")
                continue
                
            print(f"Uploading {name} to Google Drive...")
            file_metadata = {
                'name': name,
                'parents': [folder_id]
            }
            media = MediaFileUpload(file_path, mimetype='image/png', resumable=True)
            
            # Create/upload the file
            file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            file_id = file.get('id')
            view_link = file.get('webViewLink')
            
            # Set permission to anyone with link can view (reader)
            print(f"Setting permission for {name} to public (anyone can view)...")
            permission_metadata = {
                'role': 'reader',
                'type': 'anyone'
            }
            drive_service.permissions().create(
                fileId=file_id,
                body=permission_metadata
            ).execute()
            
            uploaded_image_ids[name] = file_id
            print(f"Uploaded {name} successfully. File ID: {file_id}")
            print("-" * 50)
            
        # Write image IDs to a JSON file for Apps Script construction
        output_json = "scratch/uploaded_image_ids.json"
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(uploaded_image_ids, f, ensure_ascii=False, indent=2)
            
        print(f"All image uploads complete. IDs saved to {output_json}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    upload_images()
