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

def get_doc_text(service_docs, file_id):
    try:
        doc = service_docs.documents().get(documentId=file_id).execute()
        content = doc.get('body', {}).get('content', [])
        full_text = ""
        for elem in content:
            if 'paragraph' in elem:
                for p_elem in elem['paragraph'].get('elements', []):
                    if 'textRun' in p_elem:
                        full_text += p_elem['textRun'].get('content', '')
        return full_text.strip()
    except Exception:
        return None

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json missing")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service_sheets = build('sheets', 'v4', credentials=creds)
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
        
    student_rows = rows[1:] # row index 2~76
    
    suspect_rows = []
    
    for idx, r in enumerate(student_rows, start=2):
        grade = r[1] if len(r) > 1 else ""
        ban = r[2] if len(r) > 2 else ""
        num = r[3] if len(r) > 3 else ""
        name = r[4] if len(r) > 4 else ""
        career = r[5] if len(r) > 5 else ""
        work = r[6] if len(r) > 6 else ""
        title = r[7] if len(r) > 7 else ""
        
        c_mot = r[8] if len(r) > 8 else ""
        c_lit = r[9] if len(r) > 9 else ""
        c_fus = r[10] if len(r) > 10 else ""
        c_proc = r[11] if len(r) > 11 else ""
        c_conc = r[12] if len(r) > 12 else ""
        doc_url = r[13] if len(r) > 13 else ""
        draft = r[14] if len(r) > 14 else ""
        
        if not name or not draft:
            continue
            
        is_file = "(파일 제출" in c_mot or "(파일 제출" in title
        file_text = ""
        if is_file and doc_url:
            f_id = extract_file_id(doc_url)
            if f_id:
                file_text = get_doc_text(service_docs, f_id) or ""
                
        student_raw_text = f"{career} {work} {title} {c_mot} {c_lit} {c_fus} {c_proc} {c_conc} {file_text}".strip()
        
        # Check specific keywords in draft that might not be in student_raw_text
        # e.g., specific book names, specific theory names, specific term additions
        # Let's inspect draft vs raw_text
        issues = []
        
        # 1. Check if draft mentions '논문', '서적', '통계' when student didn't mention any materials
        if ("논문" in draft or "서적" in draft or "통계" in draft) and ("논문" not in student_raw_text and "서적" not in student_raw_text and "도서" not in student_raw_text and "책" not in student_raw_text and "자료" not in student_raw_text and "통계" not in student_raw_text and "구글" not in student_raw_text and "검색" not in student_raw_text and "뉴스" not in student_raw_text and not is_file):
            issues.append("추가 자료/논문 언급 검증 필요 (원문에 미작성)")
            
        # 2. Check if specific theories are mentioned (e.g. 아노미, 판옵티콘) when not in student_raw_text
        for theory in ["아노미", "판옵티콘", "스승", "신경", "도파민", "복지", "지역의사제"]:
            if theory in draft and theory not in student_raw_text:
                # check if student career or title implies it
                issues.append(f"이론/개념 '{theory}' 추가됨")
                
        if issues:
            suspect_rows.append({
                "row": idx,
                "ban": ban,
                "num": num,
                "name": name,
                "issues": issues,
                "draft": draft,
                "raw_text_snippet": student_raw_text[:150]
            })
            
    print(f"Total evaluated students: {len(student_rows)}")
    print(f"Total suspect rows for hallucination/unmentioned facts: {len(suspect_rows)}")
    
    with open("hallucination_audit.json", "w", encoding="utf-8") as f:
        json.dump(suspect_rows, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
