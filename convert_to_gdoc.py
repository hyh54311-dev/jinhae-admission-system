import os
import markdown
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']

def auth():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("token.json is missing or invalid. Please re-authenticate.")
    return creds

def create_gdoc(md_path):
    creds = auth()
    drive_service = build('drive', 'v3', credentials=creds)

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    html_text = markdown.markdown(md_text, extensions=['extra'])
    html_path = md_path.replace('.md', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_text)

    file_metadata = {
        'name': os.path.basename(md_path).replace('.md', ''),
        'mimeType': 'application/vnd.google-apps.document'
    }
    media = MediaFileUpload(html_path,
                            mimetype='text/html',
                            resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='webViewLink').execute()
    print("SUCCESS_LINK:", file.get('webViewLink'))

if __name__ == '__main__':
    create_gdoc(r"d:\OneDrive - 寃쎌긽?⑤룄援먯쑁泥?諛뷀깢 ?붾㈃\吏꾪빐怨좊벑?숆탳\2026?숇뀈??antigravity_folder\寃쎌젣?댁뒪 TXT\2026-04-17_Macro_Briefing.md")
