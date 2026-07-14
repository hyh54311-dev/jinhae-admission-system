import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime

token_path = 'token.json'

try:
    creds = Credentials.from_authorized_user_file(token_path)
    drive_service = build('drive', 'v3', credentials=creds)
    
    # Query for spreadsheets modified or created around April 2026
    query = "mimeType = 'application/vnd.google-apps.spreadsheet'"
    results = drive_service.files().list(
        q=query,
        pageSize=500,
        fields="nextPageToken, files(id, name, webViewLink, createdTime, modifiedTime, owners)"
    ).execute()
    
    files = results.get('files', [])
    print("Spreadsheets modified or created in April 2026, or related to chatbot/admission:")
    count = 0
    for f in files:
        name = f.get('name', '')
        modified_time = f.get('modifiedTime', '')
        created_time = f.get('createdTime', '')
        
        is_april_2026 = "2026-04" in modified_time or "2026-04" in created_time
        is_relevant_name = any(kw in name for kw in ["챗봇", "상담", "진해", "로그", "입학", "질문", "답변", "jinhae", "bot"])
        
        if is_april_2026 or is_relevant_name:
            owners = ", ".join([o.get('displayName', 'Unknown') for o in f.get('owners', [])])
            print(f"Name: {name}")
            print(f"  ID: {f.get('id')}")
            print(f"  Created: {created_time}")
            print(f"  Modified: {modified_time}")
            print(f"  Link: {f.get('webViewLink')}")
            print(f"  Owners: {owners}")
            print("-" * 50)
            count += 1
            
    print(f"Total matching sheets: {count}")
            
except Exception as e:
    print("Error:", e)
