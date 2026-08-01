import os
import sys
import io
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def extract_file_id(url):
    if not url:
        return None
    # match /d/FILE_ID or id=FILE_ID
    m1 = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if m1:
        return m1.group(1)
    m2 = re.search(r'id=([a-zA-Z0-9_-]+)', url)
    if m2:
        return m2.group(1)
    return None

def get_gdoc_length(service_docs, file_id):
    try:
        doc = service_docs.documents().get(documentId=file_id).execute()
        content = doc.get('body', {}).get('content', [])
        full_text = ""
        for elem in content:
            if 'paragraph' in elem:
                for p_elem in elem['paragraph'].get('elements', []):
                    if 'textRun' in p_elem:
                        full_text += p_elem['textRun'].get('content', '')
        return len(full_text.strip()), full_text.strip()
    except Exception as e:
        return None, str(e)

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json does not exist")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service_sheets = build('sheets', 'v4', credentials=creds)
    service_drive = build('drive', 'v3', credentials=creds)
    service_docs = build('docs', 'v1', credentials=creds)
    
    spreadsheet_id = "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"
    
    result = service_sheets.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="탐구보고서_응답!A1:Q100"
    ).execute()
    
    rows = result.get('values', [])
    if not rows:
        print("No data found")
        return
        
    student_rows = rows[1:]
    
    detailed_list = []
    
    for idx, r in enumerate(student_rows, start=2):
        grade = r[1] if len(r) > 1 else "2"
        ban = r[2] if len(r) > 2 else ""
        num = r[3] if len(r) > 3 else ""
        name = r[4] if len(r) > 4 else ""
        career = r[5] if len(r) > 5 else ""
        work = r[6] if len(r) > 6 else ""
        title = r[7] if len(r) > 7 else ""
        doc_url = r[13] if len(r) > 13 else ""
        byte_val = r[15] if len(r) > 15 else ""
        
        # text content from sheet
        c_motivation = r[8] if len(r) > 8 else ""
        c_literary = r[9] if len(r) > 9 else ""
        c_fusion = r[10] if len(r) > 10 else ""
        c_process = r[11] if len(r) > 11 else ""
        c_conclusion = r[12] if len(r) > 12 else ""
        
        is_file_submit = "(파일 제출" in c_motivation or "(파일 제출" in title
        
        sheet_text = f"{title}\n{c_motivation}\n{c_literary}\n{c_fusion}\n{c_process}\n{c_conclusion}".strip()
        sheet_char_count = len(sheet_text)
        sheet_byte_count = len(sheet_text.encode('utf-8'))
        
        file_id = extract_file_id(doc_url)
        gdoc_char_count = None
        gdoc_err = None
        
        if file_id:
            gdoc_char_count, gdoc_err = get_gdoc_length(service_docs, file_id)
            
        detailed_list.append({
            "row": idx,
            "ban": ban,
            "num": num,
            "name": name,
            "work": work,
            "title": title,
            "is_file_submit": is_file_submit,
            "doc_url": doc_url,
            "file_id": file_id,
            "sheet_char_count": sheet_char_count,
            "sheet_byte_count": sheet_byte_count,
            "gdoc_char_count": gdoc_char_count,
            "gdoc_err": gdoc_err
        })
        
    print(f"Processed {len(detailed_list)} students.")
    with open("detailed_report_lengths.json", "w", encoding="utf-8") as f:
        json.dump(detailed_list, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
