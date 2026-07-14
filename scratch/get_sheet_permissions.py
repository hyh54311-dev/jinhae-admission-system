import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token.json'
file_id = '12bXJl_SRj8mVIZBBADWix8ZZ5Rh7XKFodH62iGzDTF8'

try:
    creds = Credentials.from_authorized_user_file(token_path)
    drive_service = build('drive', 'v3', credentials=creds)
    
    # Get permissions of the spreadsheet
    res = drive_service.permissions().list(
        fileId=file_id,
        fields="permissions(id, emailAddress, role, type, displayName)"
    ).execute()
    
    permissions = res.get('permissions', [])
    print("Permissions for spreadsheet '진해고 입학 홍보 챗봇 v2.0 질문과 답변':")
    for p in permissions:
        print(f"- Name: {p.get('displayName', 'N/A')}")
        print(f"  Email: {p.get('emailAddress')}")
        print(f"  Role: {p.get('role')}")
        print(f"  Type: {p.get('type')}")
        print("-" * 40)
        
except Exception as e:
    print("Error:", e)
