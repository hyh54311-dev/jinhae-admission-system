import os
import markdown
import sys
from pathlib import Path
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

def create_files():
    base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도\antigravity_folder"
    md_path = os.path.join(base_dir, "poetry_analysis.md")
    
    # Read Markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convert to HTML body
    html_body = markdown.markdown(md_text, extensions=['extra', 'nl2br'])
    
    # HTML for PDF (Elegant print styling)
    pdf_html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>황지우, <새들도 세상을 뜨는구나> 분석 및 감상</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        @page {{
            size: A4;
            margin: 22mm 20mm;
        }}
        body {{
            font-family: 'Noto Sans KR', sans-serif;
            color: #2c3e50;
            line-height: 1.72;
            background-color: #ffffff;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        h1 {{
            font-family: 'Nanum Myeongjo', serif;
            font-size: 24pt;
            font-weight: 800;
            color: #1a365d;
            text-align: center;
            margin-top: 10px;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px double #1a365d;
        }}
        h2 {{
            font-family: 'Nanum Myeongjo', serif;
            font-size: 16pt;
            font-weight: 700;
            color: #1a365d;
            margin-top: 35px;
            margin-bottom: 15px;
            border-left: 5px solid #1a365d;
            padding-left: 12px;
        }}
        h3 {{
            font-size: 12.5pt;
            font-weight: 700;
            color: #2c3e50;
            margin-top: 25px;
            margin-bottom: 10px;
        }}
        h4 {{
            font-size: 11pt;
            font-weight: 700;
            color: #34495e;
            margin-top: 18px;
            margin-bottom: 8px;
        }}
        p {{
            margin-top: 0;
            margin-bottom: 12px;
            font-size: 10.5pt;
            text-align: justify;
        }}
        ul {{
            margin-top: 0;
            margin-bottom: 15px;
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 6px;
            font-size: 10.5pt;
        }}
        code {{
            font-family: 'Courier New', Courier, monospace;
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 4px;
            font-size: 9.5pt;
        }}
        pre {{
            background-color: #fdfdfd;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 20px;
            overflow-x: auto;
            margin-top: 15px;
            margin-bottom: 25px;
        }}
        pre code {{
            font-family: 'Nanum Myeongjo', serif;
            background-color: transparent;
            padding: 0;
            font-size: 11.5pt;
            line-height: 1.8;
            color: #2c3e50;
            display: block;
            text-align: center;
        }}
        blockquote {{
            font-family: 'Noto Sans KR', sans-serif;
            background-color: #f7fafc;
            border-left: 4px solid #4a5568;
            padding: 12px 18px;
            margin: 20px 0;
            color: #4a5568;
            border-radius: 0 6px 6px 0;
        }}
        blockquote p {{
            font-size: 10.5pt;
            font-weight: 500;
            margin: 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            margin-bottom: 30px;
            font-size: 10pt;
        }}
        th, td {{
            border: 1px solid #cbd5e0;
            padding: 10px 12px;
            text-align: left;
        }}
        th {{
            background-color: #edf2f7;
            font-weight: 700;
            color: #1a365d;
        }}
        tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
        .highlight {{
            font-weight: bold;
            color: #e53e3e;
        }}
        hr {{
            border: 0;
            height: 1px;
            background-color: #e2e8f0;
            margin: 30px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_body}
    </div>
</body>
</html>"""

    # HTML for Google Doc (Simple styling, mimicking create_google_docs.py)
    gdoc_html_content = f"""<html>
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
</html>"""

    # Save HTML paths
    pdf_html_path = os.path.join(base_dir, "poetry_analysis_pdf.html")
    gdoc_html_path = os.path.join(base_dir, "poetry_analysis_gdoc.html")
    
    with open(pdf_html_path, 'w', encoding='utf-8') as f:
        f.write(pdf_html_content)
    with open(gdoc_html_path, 'w', encoding='utf-8') as f:
        f.write(gdoc_html_content)
        
    print("HTML files generated successfully.")

    # PDF generation path (Desktop)
    desktop_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면"
    pdf_dest_path = os.path.join(desktop_dir, "황지우_새들도_세상을_뜨는구나_분석.pdf")
    
    # 1. Convert to PDF using Playwright
    print("Generating PDF with Playwright...")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # Convert file path to file URL
            file_url = Path(pdf_html_path).as_uri()
            page.goto(file_url)
            # Wait for any fonts/rendering to complete
            page.wait_for_timeout(1000)
            page.pdf(path=pdf_dest_path, format="A4", print_background=True)
            browser.close()
        print(f"PDF successfully created at: {pdf_dest_path}")
    except Exception as e:
        print(f"Error during Playwright PDF generation: {e}")
        # In case browser binary is missing, we can try running playwright install chromium
        import subprocess
        try:
            print("Attempting to run 'playwright install chromium'...")
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                file_url = Path(pdf_html_path).as_uri()
                page.goto(file_url)
                page.wait_for_timeout(1000)
                page.pdf(path=pdf_dest_path, format="A4", print_background=True)
                browser.close()
            print(f"PDF successfully created after install at: {pdf_dest_path}")
        except Exception as ex_inner:
            print(f"Failed to generate PDF even after installing browser: {ex_inner}")
            
    # 2. Upload to Google Drive as Google Doc
    print("Uploading to Google Drive...")
    try:
        creds = auth()
        drive_service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {
            'name': '황지우, <새들도 세상을 뜨는구나> 분석 및 감상',
            'mimeType': 'application/vnd.google-apps.document'
        }
        media = MediaFileUpload(gdoc_html_path, mimetype='text/html', resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        file_id = file.get('id')
        link = file.get('webViewLink')
        
        # Share permissions (anyone as reader)
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
            
        print(f"GDOC_SUCCESS: {link}")
    except Exception as e:
        print(f"Error during Google Docs upload: {e}")
        
    # Clean up temp HTML files
    try:
        if os.path.exists(pdf_html_path):
            os.remove(pdf_html_path)
        if os.path.exists(gdoc_html_path):
            os.remove(gdoc_html_path)
    except Exception as cleanup_err:
        print(f"Cleanup deferred: {cleanup_err}")

if __name__ == '__main__':
    create_files()
