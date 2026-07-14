import os
import sys
import json
import markdown
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SCOPES = ['https://www.googleapis.com/auth/drive']

def auth():
    creds = None
    token_path = 'token.json'
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("token.json is missing or invalid.")
    return creds

def main():
    md_path = 'C:/Users/admin/.gemini/antigravity/brain/d84b3a92-9d17-4a5a-81b1-20511d474960/curriculum_survey_analysis.md'
    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found.")
        return
        
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    # Replace Mermaid block with a clean bullet point list for Google Docs compatibility
    mermaid_block = """```mermaid
pie title 2026학년도 교육과정 편성표 투표 결과 (총 8표)
    "1안 (이전과 동일 / 일부과목 제외)" : 3
    "2안 (선택군 C-D 통합)" : 3
    "3안 (C-D / E-F 통합)" : 2
    "4안 (지정 축소 및 E-F 통합)" : 0
```"""
    
    clean_list = """* **1안 (이전과 동일 / 일부과목 제외)**: 3표 (37.5%)
* **2안 (선택군 C-D 통합)**: 3표 (37.5%)
* **3안 (C-D / E-F 통합)**: 2표 (25.0%)
* **4안 (지정 축소 및 E-F 통합)**: 0표 (0.0%)"""
    
    if mermaid_block in md_content:
        md_content = md_content.replace(mermaid_block, clean_list)
    else:
        # Fallback regex-free replacement just in case of formatting variations
        import re
        md_content = re.sub(r'```mermaid.*?```', clean_list, md_content, flags=re.DOTALL)
        
    # Convert markdown to html
    html_text = markdown.markdown(md_content, extensions=['extra', 'nl2br'])
    
    html_styled = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: 'Malgun Gothic', 'Dotum', sans-serif; line-height: 1.6; color: #334155; }}
        h1 {{ color: #0369a1; border-bottom: 2px solid #0284c7; padding-bottom: 8px; font-size: 20pt; font-weight: bold; }}
        h2 {{ color: #0369a1; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; font-size: 14pt; margin-top: 20px; font-weight: bold; }}
        h3 {{ color: #0f172a; font-size: 11pt; margin-top: 15px; font-weight: bold; }}
        ul {{ margin-bottom: 15px; }}
        li {{ margin-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 15px; margin-bottom: 15px; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; }}
        th {{ background-color: #f1f5f9; font-weight: bold; color: #0f172a; }}
        blockquote {{ background-color: #f8fafc; border-left: 5px solid #0ea5e9; padding: 10px 15px; margin: 15px 0; }}
        hr {{ border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0; }}
    </style>
    </head>
    <body>
    {html_text}
    </body>
    </html>
    """
    
    html_path = 'scratch/temp_gdoc.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_styled)
        
    try:
        creds = auth()
        drive_service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {
            'name': '2026학년도 교육과정 편성표 의견 수렴 결과 보고서 (최종)',
            'mimeType': 'application/vnd.google-apps.document'
        }
        
        media = MediaFileUpload(html_path, mimetype='text/html', resumable=True)
        print(">> Creating Google Doc...")
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        file_id = file.get('id')
        web_link = file.get('webViewLink')
        print(f">> Google Doc Created. ID: {file_id}")
        
        print(">> Sharing Google Doc (Anyone with Link can View)...")
        drive_service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        print(">> Share permission set.")
        
        # Output results
        print(f"URL: {web_link}")
        
        # Save info to json file in scratch
        output_info = {
            "gdocId": file_id,
            "webViewLink": web_link
        }
        with open('scratch/gdoc_report_info.json', 'w', encoding='utf-8') as info_f:
            json.dump(output_info, info_f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if os.path.exists(html_path):
            try:
                os.remove(html_path)
            except Exception:
                pass

if __name__ == '__main__':
    main()
