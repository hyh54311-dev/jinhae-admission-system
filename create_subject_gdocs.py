import os
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

def upload_as_gdoc(md_path, doc_title):
    creds = auth()
    drive_service = build('drive', 'v3', credentials=creds)

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convert markdown to HTML
    html_body = markdown.markdown(md_text, extensions=['extra', 'nl2br'])
    
    # Premium Jinhae Navy and Sky Blue CSS stylesheet for A4 printable layout compatibility
    styled_html = f"""
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <style>
            body {{ 
                font-family: 'Malgun Gothic', '맑은 고딕', 'Arial', sans-serif; 
                font-size: 11.5pt; 
                line-height: 1.8; 
                color: #0f172a; 
                margin: 30px; 
            }}
            h1 {{ 
                color: #0b2545; 
                font-size: 22pt; 
                border-bottom: 3px solid #0b2545; 
                padding-bottom: 10px; 
                margin-top: 40px; 
                margin-bottom: 20px; 
            }}
            h2 {{ 
                color: #134074; 
                font-size: 16pt; 
                border-left: 6px solid #134074; 
                padding-left: 14px; 
                margin-top: 35px; 
                margin-bottom: 15px; 
            }}
            h3 {{ 
                color: #00B4D8; 
                font-size: 13pt; 
                margin-top: 25px; 
                margin-bottom: 10px; 
                font-weight: bold; 
            }}
            table {{ 
                border-collapse: collapse; 
                width: 100%; 
                margin: 25px 0; 
                font-size: 10pt; 
                line-height: 1.6;
            }}
            th, td {{ 
                border: 1px solid #cbd5e1; 
                padding: 12px 14px; 
                text-align: left; 
                vertical-align: top;
            }}
            th {{ 
                background-color: #f1f5f9; 
                font-weight: bold; 
                color: #0b2545; 
            }}
            tr:nth-child(even) {{ 
                background-color: #f8fafc; 
            }}
            blockquote {{ 
                border-left: 5px solid #ee6c4d; 
                padding: 16px 20px; 
                color: #334155; 
                background-color: #fff8f6; 
                margin: 20px 0; 
                border-radius: 6px; 
            }}
            ul, ol {{ 
                margin-bottom: 20px; 
                padding-left: 25px; 
            }}
            li {{ 
                margin-bottom: 8px; 
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    temp_html_path = md_path.replace('.md', '_temp2.html')
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
        print(f"Deferred delete: {e}")

    print(f"SUCCESS_{doc_title}: {link}")
    return link

def main():
    base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
    artifact_dir = r"C:\Users\admin\.gemini\antigravity\brain\150d9a84-507f-44fe-9c50-7ff6555dafb8"
    rw_md = os.path.join(artifact_dir, "reading_writing_gdoc_guide.md")
    mc_md = os.path.join(artifact_dir, "media_communication_gdoc_guide.md")

    print("Uploading Reading/Writing and Media guides to Google Docs...")
    
    rw_link = upload_as_gdoc(rw_md, "[선택과목 가이드] 2학년 독서 토론과 글쓰기")
    mc_link = upload_as_gdoc(mc_md, "[선택과목 가이드] 2학년 매체 의사소통")
    
    # Save links to result file
    result_path = os.path.join(base_dir, "curriculum_gdocs_links.txt")
    with open(result_path, 'w', encoding='utf-8') as f:
        f.write(f"1. [선택과목 가이드] 2학년 독서 토론과 글쓰기:\n{rw_link}\n\n")
        f.write(f"2. [선택과목 가이드] 2학년 매체 의사소통:\n{mc_link}\n")
        
    print("All tasks finished successfully.")

if __name__ == '__main__':
    main()
