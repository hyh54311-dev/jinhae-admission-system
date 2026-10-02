import os
import sys
import json
import markdown
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.stdout.reconfigure(encoding='utf-8')

SCOPES = ['https://www.googleapis.com/auth/drive']

def auth():
    base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
    token_path = os.path.join(base_dir, 'token.json')
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, 'w') as f:
                f.write(creds.to_json())
        else:
            raise Exception("token.json is missing or invalid.")
    return creds

def main():
    creds = auth()
    drive_service = build('drive', 'v3', credentials=creds)

    md_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\2026_여수_순천_2박3일_가족여행_가이드.md"
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convert markdown to html with tables and extra extensions
    html_body = markdown.markdown(md_text, extensions=['extra', 'nl2br', 'tables'])

    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>2026 여수·순천 2박 3일 힐링 가족여행 가이드</title>
        <style>
            body {{
                font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
                line-height: 1.7;
                color: #2d3748;
                padding: 20px;
                max-width: 900px;
                margin: auto;
            }}
            h1 {{
                color: #1a365d;
                border-bottom: 3px solid #3182ce;
                padding-bottom: 12px;
                font-size: 26px;
            }}
            h2 {{
                color: #2b6cb0;
                border-bottom: 2px solid #e2e8f0;
                padding-bottom: 8px;
                margin-top: 35px;
                font-size: 20px;
            }}
            h3 {{
                color: #2c5282;
                margin-top: 25px;
                font-size: 17px;
            }}
            h4 {{
                color: #319795;
                margin-top: 18px;
                font-size: 15px;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
                font-size: 14px;
            }}
            th, td {{
                border: 1px solid #cbd5e0;
                padding: 10px 12px;
                text-align: left;
            }}
            th {{
                background-color: #ebf8ff;
                color: #2b6cb0;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f7fafc;
            }}
            blockquote {{
                border-left: 5px solid #3182ce;
                background-color: #ebf8ff;
                padding: 14px 18px;
                margin: 20px 0;
                border-radius: 4px;
                color: #2c5282;
            }}
            code {{
                background-color: #edf2f7;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: Consolas, monospace;
                font-size: 13px;
                color: #c53030;
            }}
            pre {{
                background-color: #2d3748;
                color: #f7fafc;
                padding: 15px;
                border-radius: 8px;
                overflow-x: auto;
                font-size: 13px;
                line-height: 1.5;
            }}
            pre code {{
                background-color: transparent;
                color: #f7fafc;
                padding: 0;
            }}
            hr {{
                border: 0;
                height: 1px;
                background-color: #e2e8f0;
                margin: 30px 0;
            }}
            strong {{
                color: #1a202c;
            }}
            ul, ol {{
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 6px;
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    temp_html_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\temp_travel_guide.html"
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(styled_html)

    doc_title = "🚗 2026 여수·순천 2박 3일 힐링 가족여행 가이드 (전체 공유용)"
    file_metadata = {
        'name': doc_title,
        'mimeType': 'application/vnd.google-apps.document'
    }
    media = MediaFileUpload(temp_html_path, mimetype='text/html; charset=utf-8', resumable=True)

    print("Google Docs 문서 업로드 중...")
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    file_id = file.get('id')
    link = file.get('webViewLink')

    del media

    # Set public permission (anyone with link can read)
    print("공개 링크(누구나 열람 가능) 권한 설정 중...")
    drive_service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    # Clean up temp file
    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)

    print("=" * 60)
    print(f"DOC_ID: {file_id}")
    print(f"PUBLIC_SHARE_LINK: {link}")
    print("=" * 60)

    # Save to gdoc link file for record
    gdoc_path = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\2026_여수_순천_2박3일_가족여행_가이드.gdoc"
    with open(gdoc_path, 'w', encoding='utf-8') as f:
        json.dump({'doc_id': file_id, 'url': link}, f, indent=2)

if __name__ == '__main__':
    main()
