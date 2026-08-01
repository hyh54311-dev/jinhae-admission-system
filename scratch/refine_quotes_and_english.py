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
        
    # 1. 괄호 안 영문표기 및 영문 제거 (예: (Down-regulation), (GNC), (V1), (IT) 등)
    # (영어포함) -> 삭제
    text = re.sub(r'\s*\([A-Za-z0-9\s_\-\./]+\)', '', text)
    # 혹시 남아있는 단독 영문 표현도 문맥에 맞춰 한글이나 제거 (단, AI, IT 등은 문맥상 필요할 수 있으나 가능하면 제거/정리)
    # 조세원의 (Down-regulation) 등 괄호 영문 제거
    
    # 2. 낫표/겹낫표/화살괄호/겹화살괄호/큰따옴표를 둥근 작은따옴표(' ')로 변경
    # 『...』 -> ‘...’
    text = re.sub(r'『([^』]+)』', r'‘\1’', text)
    # 「...」 -> ‘...’
    text = re.sub(r'「([^」]+)」', r'‘\1’', text)
    # 《...》 -> ‘...’
    text = re.sub(r'《([^》]+)》', r'‘\1’', text)
    # <...> -> ‘...’ (단, HTML 태그 제외)
    text = re.sub(r'<([^>]+)>', r'‘\1’', text)
    
    # 3. 작품 제목에 작은따옴표가 누락된 경우 '작품명' 처리
    works = [
        "오발탄", "대설주의보", "새들도 세상을 뜨는구나", "원미동 사람들", 
        "광장", "아홉 켤레의 구두로 남은 사내", "태평천하", "동백꽃", "춘향전", "진달래꽃"
    ]
    for w in works:
        # '오발탄'이나 ‘오발탄’이 아닌 그냥 오발탄이 있으면 ‘오발탄’으로 변경
        pattern = r'(?<![‘\'"「『])' + re.escape(w) + r'(?![’\'"」』])'
        text = re.sub(pattern, f'‘{w}’', text)
        
    # 4. 일반 작은따옴표(')도 한글식 둥근 작은따옴표(‘, ’)로 정돈
    # 문장 내 단독 '어구' 처리
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
    
    target_spreadsheet_id = "1lAff1XMoqh4qNweVB457cwCdDyOBm1s-G0Ufnvgk_BI"
    src_spreadsheet_id = "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"
    
    tab_names = ["1~3반", "4~6반", "7~10반"]
    
    total_refined_count = 0
    
    # 1. target_spreadsheet_id의 3개 탭에서 세특 읽어와서 윤문 적용 후 업데이트
    for t_name in tab_names:
        res = service_sheets.spreadsheets().values().get(
            spreadsheetId=target_spreadsheet_id,
            range=f"'{t_name}'!A1:F100"
        ).execute()
        
        rows = res.get('values', [])
        if len(rows) <= 1:
            continue
            
        header = rows[0]
        data_rows = rows[1:]
        
        updated_rows = [header]
        
        for r in data_rows:
            ban_str = r[0] if len(r) > 0 else ""
            num_str = r[1] if len(r) > 1 else ""
            name = r[2] if len(r) > 2 else ""
            draft = r[3] if len(r) > 3 else ""
            
            if not draft:
                updated_rows.append(r)
                continue
                
            refined_draft = refine_seteuk_text(draft)
            b_cnt = calculate_byte(refined_draft)
            c_cnt = len(refined_draft)
            
            updated_rows.append([
                ban_str,
                num_str,
                name,
                refined_draft,
                f"{b_cnt} Bytes",
                f"{c_cnt}자"
            ])
            total_refined_count += 1
            
        # 탭 갱신
        service_sheets.spreadsheets().values().update(
            spreadsheetId=target_spreadsheet_id,
            range=f"'{t_name}'!A1",
            valueInputOption="USER_ENTERED",
            body={'values': updated_rows}
        ).execute()
        
        print(f"Updated tab '{t_name}': {len(updated_rows)-1} students refined.")

    # 2. src_spreadsheet_id (원본 응답 시트) O, P열도 함께 윤문 적용 갱신
    res_src = service_sheets.spreadsheets().values().get(
        spreadsheetId=src_spreadsheet_id,
        range="탐구보고서_응답!A2:Q100"
    ).execute()
    
    src_rows = res_src.get('values', [])
    for idx, r in enumerate(src_rows, start=2):
        draft = r[14] if len(r) > 14 else ""
        if draft:
            refined_draft = refine_seteuk_text(draft)
            b_cnt = calculate_byte(refined_draft)
            service_sheets.spreadsheets().values().update(
                spreadsheetId=src_spreadsheet_id,
                range=f"탐구보고서_응답!O{idx}:P{idx}",
                valueInputOption="USER_ENTERED",
                body={'values': [[refined_draft, b_cnt]]}
            ).execute()

    print(f"\n✅ Total {total_refined_count} students Seteuk drafts perfectly refined with Korean single quotes ‘ ’ and English parentheses removed!")

if __name__ == '__main__':
    main()
