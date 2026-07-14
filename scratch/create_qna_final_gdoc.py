# -*- coding: utf-8 -*-
import os
import markdown
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']
base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
token_path = os.path.join(base_dir, 'token.json')

def auth(token_path, scopes):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, 'w') as f:
                f.write(creds.to_json())
        else:
            raise Exception(f"Credentials at {token_path} are invalid.")
    return creds

def upload_as_gdoc(md_text, doc_title):
    creds = auth(token_path, SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)

    html_body = markdown.markdown(md_text, extensions=['extra', 'nl2br'])
    
    styled_html = f"""
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <style>
            body {{ font-family: 'Malgun Gothic', '맑은 고딕', 'Arial', sans-serif; line-height: 1.6; color: #333333; }}
            h1 {{ color: #0b3c5d; border-bottom: 2px solid #0b3c5d; padding-bottom: 8px; margin-bottom: 20px; }}
            h2 {{ color: #328cc1; border-left: 5px solid #328cc1; padding-left: 10px; margin-top: 30px; margin-bottom: 15px; }}
            p {{ margin-bottom: 10px; font-size: 10.5pt; }}
            ul {{ margin-bottom: 15px; }}
            li {{ margin-bottom: 5px; font-size: 10.5pt; }}
            .question {{ font-weight: bold; color: #0b3c5d; margin-top: 12px; }}
            .answer {{ margin-left: 15px; margin-bottom: 18px; color: #555555; }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    temp_html_path = os.path.join(base_dir, 'scratch', 'temp_qna_final.html')
    os.makedirs(os.path.dirname(temp_html_path), exist_ok=True)
    
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(styled_html)

    file_metadata = {
        'name': doc_title,
        'mimeType': 'application/vnd.google-apps.document'
    }
    media = MediaFileUpload(temp_html_path,
                            mimetype='text/html',
                            resumable=True)
    
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    file_id = file.get('id')
    link = file.get('webViewLink')

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

    try:
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
    except Exception as e:
        pass

    return link

def main():
    qna_md_path = os.path.join(base_dir, 'scratch', 'qna_final_content.md')
    print("Reading corrected Q&As Markdown...")
    with open(qna_md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Uploading Q&As as a Google Doc...")
    link = upload_as_gdoc(content, "진해고등학교 입학 상담 챗봇 예상 Q&A 100선 (최종)")
    print(f"SUCCESS: {link}")

if __name__ == '__main__':
    main()
