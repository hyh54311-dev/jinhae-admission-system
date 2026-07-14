import os
import json
import requests
import urllib3
import httplib2
import google_auth_httplib2
import win32com.client as win32
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# 경고 메시지 무시 설정
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ID와 토큰 설정
DOC_ID = "1L7U7S__MwoRStH-vdllIit-FBn8_yoUTnHzBj6QxGWk"
TOKEN_FILE = "token.json"

def get_credentials():
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE)
            if creds and creds.valid:
                return creds
            if creds and creds.expired and creds.refresh_token:
                session = requests.Session()
                session.verify = False
                creds.refresh(Request(session=session))
                return creds
        except Exception as e:
            print("Error loading credentials:", e)
    return None

def main():
    creds = get_credentials()
    if not creds:
        print("No credentials found.")
        return
        
    try:
        # SSL 검증 우회용 http 설정
        base_http = httplib2.Http(disable_ssl_certificate_validation=True)
        authorized_http = google_auth_httplib2.AuthorizedHttp(creds, http=base_http)
        drive_service = build("drive", "v3", http=authorized_http)
        
        # 1. 구글 문서를 DOCX 파일로 로컬에 다운로드
        print("Downloading Google Doc as DOCX...")
        export_url = f"https://docs.google.com/document/d/{DOC_ID}/export?format=docx"
        
        headers = {"Authorization": f"Bearer {creds.token}"}
        response = requests.get(export_url, headers=headers, verify=False)
        if response.status_code != 200:
            print(f"Failed to download doc: {response.status_code} {response.text}")
            return
            
        current_dir = os.getcwd()
        docx_path = os.path.join(current_dir, "scratch", "template.docx")
        os.makedirs(os.path.join(current_dir, "scratch"), exist_ok=True)
        
        with open(docx_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded DOCX to: {docx_path}")
        
        # 2. 한글(HWP) 오토메이션을 활용하여 HWP 파일로 변환 저장
        print("Launching Hangul (HWP) COM Automation...")
        hwp_file_name = "문학_심층탐구보고서_양식.hwp"
        hwp_path = os.path.join(current_dir, "scratch", hwp_file_name)
        
        # 파일이 이미 있으면 삭제하여 충돌 방지
        if os.path.exists(hwp_path):
            os.remove(hwp_path)
            
        try:
            hwp = win32.gencache.EnsureDispatch('HWPFrame.HwpObject')
            hwp.RegisterModule('FilePathCheckDLL', 'SecurityModule')
            hwp.SetMessageBoxMode(0x20000)  # 메시지 박스 및 팝업 대화상자 차단 (무반응 모드)
            
            # DOCX 파일 열기
            hwp.Open(docx_path)
            # HWP 파일 형식으로 저장
            hwp.SaveAs(hwp_path, "HWP")
            hwp.Quit()
            print(f"Successfully converted and saved HWP file to: {hwp_path}")
        except Exception as com_err:
            print(f"HWP COM Error: {com_err}")
            # 한글 미설치 또는 COM 오류 시 차선책으로 docx를 그대로 업로드 경고
            print("Fallback: Using DOCX file as template.")
            hwp_file_name = "문학_심층탐구보고서_양식.docx"
            hwp_path = docx_path
            
        # 3. HWP 파일을 구글 드라이브에 업로드
        print("Uploading template file to Google Drive...")
        file_metadata = {
            "name": hwp_file_name,
            "mimeType": "application/x-hwp" if hwp_path.endswith(".hwp") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }
        
        media = MediaFileUpload(
            hwp_path, 
            mimetype=file_metadata["mimeType"], 
            resumable=True
        )
        
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()
        
        file_id = uploaded_file.get("id")
        print(f"Uploaded File ID: {file_id}")
        
        # 4. 파일 공유 권한 설정 (링크가 있는 모든 사용자가 읽기 가능)
        permission = {
            "type": "anyone",
            "role": "reader"
        }
        drive_service.permissions().create(
            fileId=file_id,
            body=permission
        ).execute()
        print("Set file permission to 'anyone with the link can read'.")
        
        # 구글 드라이브 파일 직다운로드 주소 구성
        hwp_download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        print(f"Direct download URL: {hwp_download_url}")
        
        # 5. Index.html의 CONFIG_TEMPLATE_HWP 변수를 이 직다운로드 링크로 업데이트
        html_path = "문학_탐구보고서_웹앱_Index.html"
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
            
        import re
        html = re.sub(
            r'var CONFIG_TEMPLATE_HWP = "[^"]+";',
            f'var CONFIG_TEMPLATE_HWP = "{hwp_download_url}";',
            html
        )
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
            
        print("Successfully updated Index.html with direct HWP template download link!")
        
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
