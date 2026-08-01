import os
import sys
import io
import json
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
    
    result = service_sheets.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="탐구보고서_응답!A1:Q100"
    ).execute()
    
    rows = result.get('values', [])
    if not rows:
        print("No data found")
        return
        
    student_rows = rows[1:]
    
    over_2pages = []   # 2장 넘어감 (충분한 분량)
    under_2pages = []  # 2장 미만 (분량 미달/부족)
    
    for idx, r in enumerate(student_rows, start=2):
        grade = r[1] if len(r) > 1 else "2"
        ban = r[2] if len(r) > 2 else ""
        num = r[3] if len(r) > 3 else ""
        name = r[4] if len(r) > 4 else ""
        career = r[5] if len(r) > 5 else ""
        work = r[6] if len(r) > 6 else ""
        title = r[7] if len(r) > 7 else ""
        
        # text content sum from sheet
        c_motivation = r[8] if len(r) > 8 else ""
        c_literary = r[9] if len(r) > 9 else ""
        c_fusion = r[10] if len(r) > 10 else ""
        c_process = r[11] if len(r) > 11 else ""
        c_conclusion = r[12] if len(r) > 12 else ""
        
        doc_url = r[13] if len(r) > 13 else ""
        byte_val = r[15] if len(r) > 15 else "0"
        
        is_file_submit = "(파일 제출" in c_motivation or "(파일 제출" in title
        
        pure_text = f"{c_motivation}\n{c_literary}\n{c_fusion}\n{c_process}\n{c_conclusion}".strip()
        pure_char_count = len(pure_text)
        
        # 바이트 수 파싱
        try:
            byte_num = int(byte_val)
        except:
            byte_num = len(pure_text.encode('utf-8'))
            
        student_info = {
            "ban": int(ban) if ban.isdigit() else ban,
            "num": int(num) if num.isdigit() else num,
            "name": name,
            "work": work,
            "title": title,
            "is_file": is_file_submit,
            "char_count": pure_char_count,
            "byte_count": byte_num,
            "doc_url": doc_url
        }
        
        # 2장 초과 기준 판별:
        # 파일 제출건의 경우 웹앱에서 자동 생성/저장된 드라이브 문서이거나 첨부된 문서.
        # 웹 폼 직접 기입건의 경우 순수 서술 글자 수 1,200자 이상(공백 포함) 또는 3,500 Byte 이상이면 2장 초과로 판별.
        if is_file_submit:
            # 파일 제출자는 양식 파일/HWP/PDF 제출이므로 2장 이상 분량으로 분류
            over_2pages.append(student_info)
        else:
            if pure_char_count >= 1100 or byte_num >= 3300:
                over_2pages.append(student_info)
            else:
                under_2pages.append(student_info)
                
    # 반/번호 정렬
    over_2pages.sort(key=lambda x: (x["ban"] if isinstance(x["ban"], int) else 99, x["num"] if isinstance(x["num"], int) else 99))
    under_2pages.sort(key=lambda x: (x["ban"] if isinstance(x["ban"], int) else 99, x["num"] if isinstance(x["num"], int) else 99))
    
    print(f"=== 2장 넘어감 (분량 충실): {len(over_2pages)}명 ===")
    for s in over_2pages:
        file_tag = "[파일제출]" if s["is_file"] else f"[{s['char_count']}자]"
        print(f" - {s['ban']}반 {s['num']}번 {s['name']}: {file_tag}")
        
    print(f"\n=== 2장 미만 (분량 미달/부족): {len(under_2pages)}명 ===")
    for s in under_2pages:
        print(f" - {s['ban']}반 {s['num']}번 {s['name']}: [{s['char_count']}자]")

    with open("page_classification.json", "w", encoding="utf-8") as f:
        json.dump({"over_2pages": over_2pages, "under_2pages": under_2pages}, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
