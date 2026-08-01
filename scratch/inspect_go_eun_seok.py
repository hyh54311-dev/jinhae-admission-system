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
    service_sheets = build('sheets', 'v4', credentials=creds)
    service_docs = build('docs', 'v1', credentials=creds)
    
    spreadsheet_id = "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"
    
    try:
        # Get Row 2 (the first student, Go Eun-seok)
        result = service_sheets.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="탐구보고서_응답!A2:Q2"
        ).execute()
        
        rows = result.get('values', [])
        if not rows:
            print("No data found in row 2")
            return
            
        r = rows[0]
        print("--- Row 2 Student Data ---")
        for col_idx, val in enumerate(r):
            print(f"Col {col_idx} (1-based {col_idx+1}): {val[:150] if val else ''}")
            
        doc_link = r[13] if len(r) > 13 else ""
        print(f"\nGoogle Doc Link: {doc_link}")
        
        # Extract doc ID from URL
        # e.g., https://docs.google.com/document/d/DOC_ID/edit
        doc_id = ""
        if "document/d/" in doc_link:
            doc_id = doc_link.split("document/d/")[1].split("/")[0]
        elif "open?id=" in doc_link:
            doc_id = doc_link.split("open?id=")[1].split("&")[0]
            
        if doc_id:
            print(f"Extracted Doc ID: {doc_id}")
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
                print("\n--- Google Doc Text ---")
                print(doc_text[:1000])
                print("-----------------------\n")
                
                # Check if the user's requested topics are inside the doc
                keywords = ["오발탄", "철호", "신체활동", "정신적 외상", "치유", "스파크", "운동", "뇌 기능", "정서 회복", "체육교육", "학교 폭력"]
                print("Keyword checking in Google Doc:")
                for kw in keywords:
                    found = kw in doc_text
                    print(f" - '{kw}': {'FOUND' if found else 'NOT FOUND'}")
                    
            except Exception as e:
                print("Error reading Google Doc:", e)
        else:
            print("Could not extract Doc ID from link")
            
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
