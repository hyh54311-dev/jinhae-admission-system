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
        
        # 1. 한글(HWP) 프로그램을 열어 텍스트를 직접 주입하여 HWP 파일 생성 (변환 대화창 우회)
        print("Launching Hangul (HWP) and creating document directly...")
        hwp_file_name = "문학_심층탐구보고서_양식.hwp"
        current_dir = os.getcwd()
        hwp_path = os.path.join(current_dir, "scratch", hwp_file_name)
        os.makedirs(os.path.join(current_dir, "scratch"), exist_ok=True)
        
        # 파일이 이미 있으면 삭제
        if os.path.exists(hwp_path):
            os.remove(hwp_path)
            
        try:
            hwp = win32.gencache.EnsureDispatch('HWPFrame.HwpObject')
            hwp.RegisterModule('FilePathCheckDLL', 'SecurityModule')
            hwp.SetMessageBoxMode(0x20000)  # 메시지 박스 차단
            
            # 양식 텍스트 정의
            template_text = (
                "진해고등학교 2학년 문학 교과 심층 탐구 보고서 양식\n"
                "===============================================\n"
                "※ 본 양식을 다운로드하여 본인의 내용으로 채운 뒤, PDF 또는 한글 파일로 변환하여 문학 탐구 보고서 제출 웹앱을 통해 업로드해 주십시오.\n\n"
                "■ 학생 인적 사항 및 주제\n"
                " - 학년: 2학년\n"
                " - 반 / 번호 / 이름: [   ]반 [   ]번 이름: [       ]\n"
                " - 희망 진로 (또는 관심 분야): [                     ]\n"
                " - 탐구 대상 문학 작품 및 저자: [                     ]\n"
                " - 탐구 주제 (제목): [                                                     ]\n\n"
                "■ 탐구 내용 서술부\n\n"
                "1. 탐구 동기 (수업 시간 배운 내용과의 연계)\n"
                " - 작성 팁: 수업 중 어떤 대목, 개념, 시어 등에서 지적 호기심이 생겼는지 논리적으로 서술해 주세요.\n"
                " [여기에 작성하세요]\n\n"
                "2. 탐구 내용 및 결과\n"
                " - 작성 팁: 주제에 대해 스스로 분석하고 도출해 낸 결과나 현대 사회적 비평 사례를 서술하세요. (관련 통계나 사회 이론 등을 연계하면 신뢰도가 높아집니다.)\n"
                " [여기에 작성하세요]\n\n"
                "3. 탐구 과정 및 심화 노력 (도서/논문 등 독서)\n"
                " - 작성 팁: RISS/DBpia에서 실제 검색한 키워드와 찾아본 논문명, 혹은 도서관에서 대출해 깊이 읽은 도서명(저자명)을 구체적인 극복 노력과 함께 서술하세요.\n"
                " [여기에 작성하세요]\n\n"
                "4. 결론 및 느낀 점 (인식의 변화와 학업적 성장)\n"
                " - 작성 팁: 탐구 후 나에게 일어난 문학적 관점의 변화나 진로 분야에서의 성찰적 학업 소명을 정리하세요.\n"
                " [여기에 작성하세요]\n"
            )
            
            # 텍스트 직접 입력 및 저장
            hwp.InsertText(template_text)
            hwp.SaveAs(hwp_path, "HWP")
            hwp.Quit()
            print(f"Successfully created HWP file directly at: {hwp_path}")
            
        except Exception as com_err:
            print(f"HWP COM Direct Error: {com_err}")
            # 한글 미설치 시 예외 복구로 docx 경로 사용
            docx_path = os.path.join(current_dir, "scratch", "template.docx")
            if os.path.exists(docx_path):
                print("Fallback: Using DOCX file as template.")
                hwp_file_name = "문학_심층탐구보고서_양식.docx"
                hwp_path = docx_path
            else:
                raise com_err
                
        # 2. HWP 파일을 구글 드라이브에 업로드
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
        
        # 3. 파일 공유 권한 설정
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
        
        # 4. Index.html의 CONFIG_TEMPLATE_HWP 변수를 이 직다운로드 링크로 업데이트
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
