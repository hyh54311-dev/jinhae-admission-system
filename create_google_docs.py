import os
import markdown
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']

def auth():
    # token.json 위치 확인 (작업 디렉토리 기준)
    token_path = 'token.json'
    if not os.path.exists(token_path):
        # 만약 없으면 절대 경로로 시도
        base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
        token_path = os.path.join(base_dir, 'token.json')
        
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("token.json is missing or invalid. Please re-authenticate.")
    return creds

def upload_as_gdoc(md_path, doc_title):
    creds = auth()
    drive_service = build('drive', 'v3', credentials=creds)

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # 마크다운을 HTML로 변환
    html_body = markdown.markdown(md_text, extensions=['extra', 'nl2br'])
    
    # 구글 문서에서 테이블과 스타일이 잘 보이도록 CSS 추가
    styled_html = f"""
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <style>
            body {{ font-family: 'Arial', '맑은 고딕', sans-serif; line-height: 1.6; color: #333333; }}
            h1 {{ color: #0b3c5d; border-bottom: 2px solid #0b3c5d; padding-bottom: 5px; }}
            h2 {{ color: #328cc1; border-left: 5px solid #328cc1; padding-left: 10px; margin-top: 25px; }}
            h3 {{ color: #2c3e50; margin-top: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 15px 0; font-size: 10pt; }}
            th, td {{ border: 1px solid #cccccc; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f5f8; font-weight: bold; color: #0b3c5d; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .highlight {{ background-color: #fff0f0; font-weight: bold; }}
            blockquote {{ border-left: 4px solid #328cc1; padding-left: 10px; color: #555555; background-color: #f9f9f9; padding: 10px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    temp_html_path = md_path.replace('.md', '_temp.html')
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(styled_html)

    file_metadata = {
        'name': doc_title,
        'mimeType': 'application/vnd.google-apps.document'
    }
    media = MediaFileUpload(temp_html_path,
                            mimetype='text/html',
                            resumable=True)
    
    # 구글 문서로 업로드
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    file_id = file.get('id')
    link = file.get('webViewLink')

    # 누구나 링크가 있으면 볼 수 있도록 권한 설정 (anyone, reader)
    try:
        drive_service.permissions().create(
            fileId=file_id,
            body={
                'type': 'anyone',
                'role': 'reader'
            }
        ).execute()
        # 누구나 읽기 가능한 권한이 잘 부여되었을 때 webViewLink 획득
    except Exception as perm_ex:
        print(f"Warning: Failed to set permission for {doc_title}: {perm_ex}")

    # 임시 HTML 파일 삭제
    try:
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
    except Exception as e:
        print(f"Temporary file deletion deferred: {e}")

    print(f"SUCCESS_{doc_title}: {link}")
    return link

def main():
    base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
    plan_md = os.path.join(base_dir, "쉬었음_청년_현상_탐구_운영계획.md")
    report_md = os.path.join(base_dir, "쉬었음_청년_연구보고서_양식.md")

    print("Google Docs 변환 작업을 시작합니다...")
    
    plan_link = upload_as_gdoc(plan_md, "쉬었음 청년 현상 탐구 운영계획")
    report_link = upload_as_gdoc(report_md, "쉬었음 청년 연구보고서 양식")
    
    # 결과를 파일로도 기록
    result_path = os.path.join(base_dir, "google_docs_links.txt")
    with open(result_path, 'w', encoding='utf-8') as f:
        f.write(f"1. 쉬었음 청년 현상 탐구 운영계획:\n{plan_link}\n\n")
        f.write(f"2. 쉬었음 청년 연구보고서 양식:\n{report_link}\n")
    
    print(f"모든 작업이 완료되었습니다. 결과가 {result_path} 에 저장되었습니다.")

if __name__ == '__main__':
    main()
