import os
import markdown
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']

def auth():
    base_dir = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
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
    except Exception as perm_ex:
        print(f"Warning: Failed to set permission: {perm_ex}")

    # 임시 HTML 파일 삭제
    try:
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
    except Exception as e:
        print(f"Temporary file deletion deferred: {e}")

    print(f"SUCCESS_LINK:{link}")
    return link

if __name__ == '__main__':
    base_dir = r"d:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
    md_file = os.path.join(base_dir, "2026_AI_교육_활용_로드맵.md")
    print(f"Uploading {md_file} as Google Doc...")
    upload_as_gdoc(md_file, "황요한 선생님의 AI 교육 활용 및 에듀테크 리더십 로드맵")
