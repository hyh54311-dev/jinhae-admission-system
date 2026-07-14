import os
import sys
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

TOKEN_FILE = "token.json"
DOCS_TEMPLATE_ID = "1L7U7S__MwoRStH-vdllIit-FBn8_yoUTnHzBj6QxGWk"
HWP_TEMPLATE_ID = "1lNpRB4DGv-4I1KGdv3VCQXqJma_t-WE8"

def check_and_fix_permissions(service, file_id, name):
    print(f"\nChecking permissions for {name} (ID: {file_id})...")
    try:
        # 파일 메타데이터 및 권한 가져오기
        file_meta = service.files().get(fileId=file_id, fields="name, permissions").execute()
        permissions = file_meta.get("permissions", [])
        
        is_public = False
        for perm in permissions:
            if perm.get("type") == "anyone" and perm.get("role") in ["reader", "writer"]:
                is_public = True
                print(f" -> Current permission is already PUBLIC: {perm.get('role')} ({perm.get('type')})")
                break
                
        if not is_public:
            print(" -> Permission is RESTRICTED. Fixing to 'Anyone with the link can view'...")
            service.permissions().create(
                fileId=file_id,
                body={
                    "type": "anyone",
                    "role": "reader"
                }
            ).execute()
            print(" -> Successfully set to PUBLIC (Anyone with link can view)!")
            
    except Exception as e:
        print(f"Error checking/fixing permissions for {file_id}: {e}")

def main():
    if not os.path.exists(TOKEN_FILE):
        print("token.json does not exist")
        return
        
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, ['https://www.googleapis.com/auth/drive'])
    service = build('drive', 'v3', credentials=creds)
    
    check_and_fix_permissions(service, DOCS_TEMPLATE_ID, "Google Docs Template")
    check_and_fix_permissions(service, HWP_TEMPLATE_ID, "HWP/Word Template (.docx)")

if __name__ == '__main__':
    main()
