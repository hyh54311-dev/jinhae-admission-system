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
    
    spreadsheet_id = "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"
    
    try:
        result = service_sheets.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="탐구보고서_응답!A:Q"
        ).execute()
        
        rows = result.get('values', [])
        if not rows:
            print("No data found")
            return
            
        headers = rows[0]
        student_rows = rows[1:]
        
        print(f"총 제출 건수: {len(student_rows)}건\n")
        
        # Check by 반/번호 combination
        class_num_map = {}
        # Check by 이름
        name_map = {}
        
        duplicates_class_num = []
        duplicates_name = []
        
        for idx, r in enumerate(student_rows, start=2):
            # Row index in sheet is idx
            grade = r[1] if len(r) > 1 else ""
            ban = r[2] if len(r) > 2 else ""
            num = r[3] if len(r) > 3 else ""
            name = r[4] if len(r) > 4 else ""
            
            key_class_num = (grade, ban, num)
            
            # Check class/number duplicates
            if key_class_num in class_num_map:
                class_num_map[key_class_num].append((idx, name))
            else:
                class_num_map[key_class_num] = [(idx, name)]
                
            # Check name duplicates
            if name in name_map:
                name_map[name].append((idx, f"{grade}학년 {ban}반 {num}번"))
            else:
                name_map[name] = [(idx, f"{grade}학년 {ban}반 {num}번")]
                
        # Find duplicates
        print("--- [학년-반-번호] 중복 검사 ---")
        has_class_num_dup = False
        for key, occurrences in class_num_map.items():
            if len(occurrences) > 1:
                has_class_num_dup = True
                grade, ban, num = key
                print(f"⚠️ 중복 발견: {grade}학년 {ban}반 {num}번")
                for sheet_idx, name in occurrences:
                    print(f"   - 시트 {sheet_idx}행: 이름 '{name}'")
        if not has_class_num_dup:
            print("✅ 학년-반-번호 중복이 없습니다.")
            
        print("\n--- [이름] 중복 검사 ---")
        has_name_dup = False
        for name, occurrences in name_map.items():
            if len(occurrences) > 1:
                has_name_dup = True
                print(f"⚠️ 중복 발견: 이름 '{name}'")
                for sheet_idx, class_info in occurrences:
                    print(f"   - 시트 {sheet_idx}행: {class_info}")
        if not has_name_dup:
            print("✅ 이름 중복이 없습니다.")
            
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
