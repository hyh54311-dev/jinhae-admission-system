import os
import json
import urllib3
import httplib2
import google_auth_httplib2
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN_FILE = "token.json"

def get_credentials():
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE)
            if creds and creds.valid:
                return creds
            if creds and creds.expired and creds.refresh_token:
                import requests
                session = requests.Session()
                session.verify = False
                creds.refresh(Request(session=session))
                return creds
        except Exception as e:
            print("Error loading credentials:", e)
    return None

def find_folder_by_name_and_parent(service, name, parent_id=None):
    query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    results = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name, parents)"
    ).execute()
    
    return results.get("files", [])

def main():
    creds = get_credentials()
    if not creds:
        print("No credentials found.")
        return
        
    try:
        base_http = httplib2.Http(disable_ssl_certificate_validation=True)
        authorized_http = google_auth_httplib2.AuthorizedHttp(creds, http=base_http)
        drive_service = build("drive", "v3", http=authorized_http)
        
        # 1단계: "진해고등학교" 폴더 찾기
        jinhae_folders = find_folder_by_name_and_parent(drive_service, "진해고등학교")
        for jinhae in jinhae_folders:
            print(f"Jinhae folder ID: {jinhae['id']}")
            # 2단계: "2026학년도" 폴더 찾기
            years = find_folder_by_name_and_parent(drive_service, "2026학년도", jinhae['id'])
            for yr in years:
                print(f"  Year 2026 folder ID: {yr['id']}")
                # 3단계: "수업" 폴더 찾기
                classes = find_folder_by_name_and_parent(drive_service, "수업", yr['id'])
                for cls in classes:
                    print(f"    Class folder ID: {cls['id']}")
                    # 4단계: "2026학년도 세특" 폴더 찾기
                    seteuks = find_folder_by_name_and_parent(drive_service, "2026학년도 세특", cls['id'])
                    for setk in seteuks:
                        print(f"      Seteuk folder ID: {setk['id']}")
                        # 5단계: "2학년 문학" 폴더 찾기
                        lits = find_folder_by_name_and_parent(drive_service, "2학년 문학", setk['id'])
                        for lit in lits:
                            print(f"        TARGET FOLDER FOUND - 2학년 문학 ID: {lit['id']}")
                            # 결과를 파일에 안전하게 기록
                            with open("scratch/target_folder_id.txt", "w") as out:
                                out.write(lit['id'])
                            return
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
