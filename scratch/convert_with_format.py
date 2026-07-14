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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
            print("Error:", e)
    return None

def main():
    creds = get_credentials()
    if not creds:
        print("No credentials found.")
        return
        
    try:
        base_http = httplib2.Http(disable_ssl_certificate_validation=True)
        authorized_http = google_auth_httplib2.AuthorizedHttp(creds, http=base_http)
        drive_service = build("drive", "v3", http=authorized_http)
        
        # 1. 구글 문서 다운로드
        print("Downloading docx template...")
        export_url = f"https://docs.google.com/document/d/{DOC_ID}/export?format=docx"
        headers = {"Authorization": f"Bearer {creds.token}"}
        response = requests.get(export_url, headers=headers, verify=False)
        if response.status_code != 200:
            print("Failed to download doc:", response.status_code)
            return
            
        current_dir = os.getcwd()
        docx_path = os.path.join(current_dir, "scratch", "template.docx")
        with open(docx_path, "wb") as f:
            f.write(response.content)
        print("Downloaded docx.")

        # 2. HWP COM 호출 (DOCX 포맷 지정 및 메시지박스 비활성화)
        print("Launching HWP COM Object...")
        hwp_path = os.path.join(current_dir, "scratch", "문학_심층탐구보고서_양식.hwp")
        if os.path.exists(hwp_path):
            os.remove(hwp_path)
            
        success = False
        try:
            hwp = win32.gencache.EnsureDispatch('HWPFrame.HwpObject')
            hwp.RegisterModule('FilePathCheckDLL', 'SecurityModule')
            hwp.SetMessageBoxMode(0x20000)  # 모든 메시지 박스 및 변환 팝업 차단
            hwp.XHwpWindows.Item(0).Visible = True
            
            # DOCX 포맷 문자열 지정하여 열기 (팝업 우회)
            print("Opening template.docx in Hangul with format 'DOCX'...")
            # Hwp.Open(path, Format, Arg) -> Format에 "DOCX"를 지정
            open_success = hwp.Open(docx_path, "DOCX", "")
            
            if not open_success:
                print("Failed to open with Format='DOCX'. Trying format='Microsoft Word'...")
                open_success = hwp.Open(docx_path, "Microsoft Word", "")
                
            if not open_success:
                print("Failed to open with specific format. Trying default Open...")
                open_success = hwp.Open(docx_path)
                
            if open_success:
                hwp.SaveAs(hwp_path, "HWP")
                print("Successfully saved HWP!")
                success = True
            else:
                print("HWP Open failed completely.")
            
            hwp.Quit()
        except Exception as e:
            print("HWP COM Error:", e)
            
        if not success:
            print("Fallback: Using DOCX file as HWP template directly.")
            hwp_path = docx_path
            
        # 3. 드라이브 업로드
        print("Uploading template file to Google Drive...")
        file_metadata = {
            "name": "문학_심층탐구보고서_양식.hwp" if hwp_path.endswith(".hwp") else "문학_심층탐구보고서_양식.docx",
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
        
        # 4. 공유 설정 및 다운로드 링크 추출
        drive_service.permissions().create(fileId=file_id, body={"type": "anyone", "role": "reader"}).execute()
        hwp_download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        print("Upload success. Download link:", hwp_download_url)
        
        # 5. Index.html 업데이트
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
