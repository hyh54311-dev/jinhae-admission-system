import os
import sys
import io
import json
import re
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def calculate_byte(text):
    if not text:
        return 0
    b_count = 0
    for ch in text:
        code = ord(ch)
        if code == 10:
            b_count += 2
        elif code == 13:
            pass
        elif code > 127:
            b_count += 3
        else:
            b_count += 1
    return b_count

def refine_seteuk_text(text):
    if not text:
        return ""
        
    # 1. 괄호 안 영문표기 및 영문 제거 (예: (Down-regulation), (GNC), (V1) 등)
    text = re.sub(r'\s*\([A-Za-z0-9\s_\-\./]+\)', '', text)
    
    # 2. 낫표/겹낫표/화살괄호/겹화살괄호/큰따옴표를 둥근 작은따옴표(' ')로 변경
    text = re.sub(r'『([^』]+)』', r'‘\1’', text)
    text = re.sub(r'「([^」]+)」', r'‘\1’', text)
    text = re.sub(r'《([^》]+)》', r'‘\1’', text)
    text = re.sub(r'<([^>]+)>', r'‘\1’', text)
    
    # 3. 작품 제목에 작은따옴표가 누락된 경우 '작품명' 처리
    works = [
        "오발탄", "대설주의보", "새들도 세상을 뜨는구나", "원미동 사람들", 
        "광장", "아홉 켤레의 구두로 남은 사내", "태평천하", "동백꽃", "춘향전", "진달래꽃"
    ]
    for w in works:
        pattern = r'(?<![‘\'"「『])' + re.escape(w) + r'(?![’\'"」』])'
        text = re.sub(pattern, f'‘{w}’', text)
        
    # 4. 일반 작은따옴표(')도 한글식 둥근 작은따옴표(‘, ’)로 정돈
    parts = text.split("'")
    if len(parts) > 1:
        new_text = ""
        for idx, p in enumerate(parts):
            if idx % 2 == 1:
                new_text += f"‘{p}’"
            else:
                new_text += p
        text = new_text

    return text.strip()

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json missing")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service_sheets = build('sheets', 'v4', credentials=creds)
    src_spreadsheet_id = "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"
    
    # 소스 시트 전체 한 번에 batchUpdate
    res_src = service_sheets.spreadsheets().values().get(
        spreadsheetId=src_spreadsheet_id,
        range="탐구보고서_응답!O2:P100"
    ).execute()
    
    src_rows = res_src.get('values', [])
    data_updates = []
    
    for idx, r in enumerate(src_rows, start=2):
        draft = r[0] if len(r) > 0 else ""
        if draft:
            refined_draft = refine_seteuk_text(draft)
            b_cnt = calculate_byte(refined_draft)
            data_updates.append({
                'range': f"탐구보고서_응답!O{idx}:P{idx}",
                'values': [[refined_draft, b_cnt]]
            })
            
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': data_updates
    }
    
    service_sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=src_spreadsheet_id,
        body=body
    ).execute()
    
    print("✅ Source sheet batchUpdate completed without rate limits!")

if __name__ == '__main__':
    main()
