# -*- coding: utf-8 -*-
import os
import markdown
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']

def auth():
    creds = None
    token_path = r'd:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder\token.json'
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("token.json이 존재하지 않거나 유효하지 않습니다. 먼저 구글 인증을 완료해 주세요.")
    return creds

def create_gdoc(md_path):
    creds = auth()
    drive_service = build('drive', 'v3', credentials=creds)

    print(f">> 마크다운 파일 읽는 중: {md_path}")
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    html_text = markdown.markdown(md_text, extensions=['extra', 'nl2br', 'sane_lists'])
    
    styled_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; line-height: 1.5; color: #1F2937; }}
            h1 {{ color: #1E3A8A; font-size: 20pt; border-bottom: 2px solid #E5E7EB; padding-bottom: 8px; }}
            h2 {{ color: #2563EB; font-size: 15pt; margin-top: 20px; }}
            h3 {{ color: #4B5563; font-size: 12pt; }}
            table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
            th, td {{ border: 1px solid #D1D5DB; padding: 10px; text-align: center; }}
            th {{ background-color: #1E3A8A; color: white; font-weight: bold; }}
            tr:nth-child(even) {{ background-color: #F9FAFB; }}
            pre {{ background-color: #F3F4F6; padding: 12px; border: 1px solid #E5E7EB; border-radius: 4px; font-family: 'Consolas', monospace; font-size: 9.5pt; overflow-x: auto; }}
            blockquote {{ border-left: 4px solid #2563EB; background-color: #EFF6FF; padding: 10px 15px; margin: 15px 0; color: #1E3A8A; }}
        </style>
    </head>
    <body>
        {html_text}
    </body>
    </html>
    """
    
    html_path = md_path.replace('.md', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(styled_html)
    print(f">> 임시 HTML 빌드 완료: {html_path}")

    file_metadata = {
        'name': '연금저축_듀얼모멘텀_가이드',
        'mimeType': 'application/vnd.google-apps.document'
    }
    
    # MediaFileUpload 업로드 수행
    media = MediaFileUpload(html_path, mimetype='text/html', resumable=True)
    print(">> 구글 드라이브 업로드 및 구글 문서 변환 시작...")
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='webViewLink').execute()
    link = file.get('webViewLink')
    print("SUCCESS_LINK:", link)
    
    # 임시 HTML 파일 삭제 오류 격리 (삭제 실패해도 프로그램이 중단되지 않음)
    try:
        if os.path.exists(html_path):
            os.remove(html_path)
            print(">> 임시 HTML 파일이 성공적으로 삭제되었습니다.")
    except Exception as de:
        print(f">> [주의] 임시 HTML 파일 자동 삭제 지연(무시 가능): {de}")
        
    return link

if __name__ == '__main__':
    gemini_md_path = r"C:\Users\admin\.gemini\antigravity\brain\511269f4-87e3-4fe0-a35d-b422721a6ab6\retirement_savings_dual_momentum_guide.md"
    
    try:
        link = create_gdoc(gemini_md_path)
        
        # 바탕화면에 바로가기 생성
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        shortcut_path = os.path.join(desktop, "연금저축_듀얼모멘텀_가이드.url")
        with open(shortcut_path, 'w', encoding='utf-8') as f:
            f.write("[InternetShortcut]\n")
            f.write(f"URL={link}\n")
        print(f"SHORTCUT_CREATED: {shortcut_path}")
    except Exception as e:
        print(f"ERROR: {e}")
