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
    m1 = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if m1:
        return m1.group(1)
    m2 = re.search(r'id=([a-zA-Z0-9_-]+)', url)
    if m2:
        return m2.group(1)
    return None

def get_student_text_content(service_docs, service_drive, r):
    # c_motivation to c_conclusion
    c_motivation = r[8] if len(r) > 8 else ""
    c_literary = r[9] if len(r) > 9 else ""
    c_fusion = r[10] if len(r) > 10 else ""
    c_process = r[11] if len(r) > 11 else ""
    c_conclusion = r[12] if len(r) > 12 else ""
    title = r[7] if len(r) > 7 else ""
    doc_url = r[13] if len(r) > 13 else ""
    
    is_file_submit = "(파일 제출" in c_motivation or "(파일 제출" in title
    
    if not is_file_submit:
        return f"탐구 주제: {title}\n1. 탐구 동기: {c_motivation}\n2-1. 작품 분석: {c_literary}\n2-2. 진로/사회 연계: {c_fusion}\n3. 탐구 과정: {c_process}\n4. 결론 및 성장: {c_conclusion}"
        
    file_id = extract_file_id(doc_url)
    if file_id:
        try:
            doc = service_docs.documents().get(documentId=file_id).execute()
            content = doc.get('body', {}).get('content', [])
            full_text = ""
            for elem in content:
                if 'paragraph' in elem:
                    for p_elem in elem['paragraph'].get('elements', []):
                        if 'textRun' in p_elem:
                            full_text += p_elem['textRun'].get('content', '')
            if len(full_text.strip()) > 30:
                return full_text.strip()
        except Exception as e:
            pass
            
    return f"탐구 주제: {title}\n1. 탐구 동기: {c_motivation}\n2-1. 작품 분석: {c_literary}\n2-2. 진로/사회 연계: {c_fusion}\n3. 탐구 과정: {c_process}\n4. 결론 및 성장: {c_conclusion}"

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
        return
        
    student_rows = rows[1:]
    
    # Target first 5 students
    batch_5 = []
    for idx, r in enumerate(student_rows, start=2):
        ban = r[2] if len(r) > 2 else ""
        num = r[3] if len(r) > 3 else ""
        name = r[4] if len(r) > 4 else ""
        career = r[5] if len(r) > 5 else ""
        work = r[6] if len(r) > 6 else ""
        title = r[7] if len(r) > 7 else ""
        
        full_content = get_student_text_content(service_docs, service_drive, r)
        
        batch_5.append({
            "row": idx,
            "ban": ban,
            "num": num,
            "name": name,
            "career": career,
            "work": work,
            "title": title,
            "content": full_content
        })
        if len(batch_5) == 5:
            break
            
    print(json.dumps(batch_5, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
