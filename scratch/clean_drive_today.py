import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime

# Point to the root directory where token.json resides
ROOT_DIR = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
FOLDER_ID = "1aXM_giZCkZVKnFrDK6tRQZly6e2JvTUX"
SCOPES = ['https://www.googleapis.com/auth/drive']

def clean_google_drive():
    token_path = os.path.join(ROOT_DIR, 'token.json')
    if not os.path.exists(token_path):
        print(f"token.json not found at {token_path}")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    service = build('drive', 'v3', credentials=creds)
    
    today_prefix = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # List files in the folder
    query = f"'{FOLDER_ID}' in parents and name contains '{today_prefix}' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    if not files:
        print("No files found to delete for today.")
        return
        
    for file in files:
        print(f"Deleting file: {file['name']} ({file['id']})")
        try:
            service.files().delete(fileId=file['id']).execute()
        except Exception as e:
            print(f"Error deleting {file['name']}: {e}")

if __name__ == "__main__":
    clean_google_drive()
