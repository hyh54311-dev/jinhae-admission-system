import os
import json
import markdown
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']

def auth():
    token_path = 'token.json'
    if not os.path.exists(token_path):
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

def upload_as_gdoc(md_path, doc_title, file_id=None):
    creds = auth()
    drive_service = build('drive', 'v3', credentials=creds)

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convert markdown to HTML
    html_body = markdown.markdown(md_text, extensions=['extra', 'nl2br'])
    
    # Style HTML
    styled_html = f"""
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <style>
            body {{ font-family: 'Arial', '맑은 고딕', sans-serif; line-height: 1.6; color: #333333; font-size: 11pt; }}
            h1 {{ color: #0284c7; border-bottom: 2px solid #e0f2fe; padding-bottom: 8px; margin-top: 30px; font-size: 20pt; }}
            h2 {{ color: #0369a1; border-left: 6px solid #0284c7; padding-left: 12px; margin-top: 25px; font-size: 15pt; }}
            h3 {{ color: #0f172a; margin-top: 20px; font-size: 12pt; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 10pt; }}
            th, td {{ border: 1px solid #bae6fd; padding: 10px; text-align: left; }}
            th {{ background-color: #f0f9ff; font-weight: bold; color: #0369a1; }}
            tr:nth-child(even) {{ background-color: #fafafa; }}
            blockquote {{ border-left: 4px solid #0284c7; padding: 12px; color: #475569; background-color: #f0f9ff; margin: 15px 0; border-radius: 4px; }}
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

    media = MediaFileUpload(temp_html_path,
                            mimetype='text/html',
                            resumable=True)

    if file_id:
        print(f"Updating existing Google Doc with ID: {file_id}")
        file = drive_service.files().update(fileId=file_id, media_body=media, fields='id, webViewLink').execute()
        link = file.get('webViewLink')
    else:
        print("Creating a new Google Doc...")
        file_metadata = {
            'name': doc_title,
            'mimeType': 'application/vnd.google-apps.document'
        }
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        file_id = file.get('id')
        link = file.get('webViewLink')

        # Share with anyone as reader
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

    # Remove temporary HTML file
    try:
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
    except Exception as e:
        print(f"Temporary file deletion deferred: {e}")

    return file_id, link

def main():
    base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
    md_path = os.path.join(base_dir, "scratch", "3억_5천만원_자금_마련_계획서.md")
    info_path = os.path.join(base_dir, "scratch", "gdoc_loan_info.json")
    
    file_id = None
    if os.path.exists(info_path):
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                info = json.load(f)
                file_id = info.get("gdocId")
        except Exception as e:
            print("Failed to load existing doc info:", e)

    file_id, link = upload_as_gdoc(md_path, "누님 이사 자금 조달 계획서 (3억 5천만원)", file_id=file_id)
    print(f"Uploaded successfully. Link: {link}")
    
    # Save the link info locally
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump({"gdocId": file_id, "webViewLink": link}, f, indent=2)
    print(f"Saved link info to {info_path}")

if __name__ == '__main__':
    main()
