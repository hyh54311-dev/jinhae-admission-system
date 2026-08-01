import os
import sys
import io
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

TOKEN_FILE = "token.json"
SPREADSHEET_ID = "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"

def main():
    if not os.path.exists(TOKEN_FILE):
        print("token.json does not exist")
        return
        
    creds = Credentials.from_authorized_user_file(TOKEN_FILE)
    sheets_service = build("sheets", "v4", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)
    
    # 스프레드시트 2행에서 첫 번째 학생의 이름과 문서 링크 추출
    res = sheets_service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="탐구보고서_응답!A2:Q2"
    ).execute()
    
    rows = res.get("values", [])
    if not rows:
        print("No student data in spreadsheet.")
        return
        
    row = rows[0]
    name = row[4]
    doc_url = row[13]
    
    print(f"Reading spreadsheet row 2: Student Name = {name}")
    print(f"Google Doc URL = {doc_url}")
    
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", doc_url)
    if not match:
        print("Could not parse Document ID from URL.")
        return
        
    doc_id = match[1]
    
    # 구글 문서 읽기
    doc = docs_service.documents().get(documentId=doc_id).execute()
    title = doc.get("title")
    print(f"\nSuccessfully opened Google Doc! Title: '{title}'")
    
    content = doc.get("body").get("content")
    text_parts = []
    for element in content:
        if "paragraph" in element:
            for run in element["paragraph"]["elements"]:
                if "textRun" in run:
                    text_parts.append(run["textRun"]["content"])
                    
    full_text = "".join(text_parts)
    print("\n--- Document Body Content Preview (First 500 chars) ---")
    print(full_text[:500] + "\n...")
    print("-------------------------------------------------------")

if __name__ == '__main__':
    main()
