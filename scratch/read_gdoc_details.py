import os
import json
import urllib3
import httplib2
import google_auth_httplib2
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN_FILE = "token.json"
TARGET_DOC_ID = "1L7U7S__MwoRStH-vdllIit-FBn8_yoUTnHzBj6QxGWk"

def get_credentials():
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE)
            if creds and creds.valid:
                return creds
            if creds and creds.expired and creds.refresh_token:
                import requests
                session = requests.Session()
                session.verify = False
                creds.refresh(Request(session=session))
                return creds
        except Exception as e:
            print("Error loading credentials:", e)
    return None

def main():
    creds = get_credentials()
    if not creds:
        print("No credentials found.")
        return
        
    try:
        base_http = httplib2.Http(disable_ssl_certificate_validation=True)
        authorized_http = google_auth_httplib2.AuthorizedHttp(creds, http=base_http)
        docs_service = build("docs", "v1", http=authorized_http)
        
        doc = docs_service.documents().get(documentId=TARGET_DOC_ID).execute()
        print("\n=== Document Info ===")
        print(f"Title: {doc.get('title')}")
        
        # 문서 구조 분석을 위한 간단한 텍스트 출력
        body = doc.get("body", {})
        content = body.get("content", [])
        
        text_lines = []
        for element in content:
            if "paragraph" in element:
                paragraph = element["paragraph"]
                elements = paragraph.get("elements", [])
                for el in elements:
                    if "textRun" in el:
                        text_lines.append(el["textRun"].get("content", ""))
                        
        print("\n=== First 30 lines of Content ===")
        full_text = "".join(text_lines)
        lines = full_text.split("\n")
        for i, line in enumerate(lines[:30]):
            print(f"Line {i+1}: {line}")
            
    except Exception as e:
        print("Error fetching document:", e)

if __name__ == "__main__":
    main()
