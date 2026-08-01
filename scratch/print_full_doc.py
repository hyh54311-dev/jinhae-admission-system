import os
import sys
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json does not exist")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service_docs = build('docs', 'v1', credentials=creds)
    
    doc_id = "1aw8n3rx3sCrVMq5DVu7SCWtRTod_XcOu7Acwj9TJmAg"
    
    try:
        doc = service_docs.documents().get(documentId=doc_id).execute()
        print(f"Doc Title: {doc.get('title')}")
        
        # Extract text
        body_content = doc.get('body').get('content', [])
        text_runs = []
        for element in body_content:
            if 'paragraph' in element:
                for run in element.get('paragraph').get('elements', []):
                    if 'textRun' in run:
                        text_runs.append(run.get('textRun').get('content'))
        doc_text = "".join(text_runs)
        print("\n--- Google Doc Full Text ---")
        print(doc_text)
        print("----------------------------\n")
        
    except Exception as e:
        print("Error reading Google Doc:", e)

if __name__ == '__main__':
    main()
