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
    service = build('sheets', 'v4', credentials=creds)
    
    spreadsheet_id = "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"
    
    try:
        # Fetch the entire sheet values
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="탐구보고서_응답!A:Q"
        ).execute()
        
        rows = result.get('values', [])
        print(f"Total rows retrieved (including headers): {len(rows)}")
        
        if len(rows) > 0:
            headers = rows[0]
            print(f"Headers ({len(headers)} columns): {', '.join(headers)}")
            
            # Check row integrity
            errors = []
            for idx, r in enumerate(rows[1:], start=2):
                if len(r) != 17:
                    errors.append(f"Row {idx} has {len(r)} columns (expected 17)")
                
                # Check byte count
                try:
                    byte_count = int(r[15])
                    # Calc length ofmotivation (col 9), content_literary (col 10), content_fusion (col 11), process (col 12), conclusion (col 13)
                    # Indices: motivation=8, content_literary=9, content_fusion=10, process=11, conclusion=12
                    calc_len = len(r[8]) + len(r[9]) + len(r[10]) + len(r[11]) + len(r[12])
                    if byte_count != calc_len:
                        errors.append(f"Row {idx} ({r[4]}): Byte count {byte_count} does not match calculated length {calc_len}")
                except Exception as e:
                    errors.append(f"Row {idx} ({r[4]}): Error parsing byte count: {e}")
                    
            if not errors:
                print("All rows are fully valid and consistent!")
            else:
                print("Validation issues found:")
                for err in errors:
                    print(f" - {err}")
                    
            # Print summary of imported students
            print("\nSubmitted Students Summary:")
            for idx, r in enumerate(rows[1:], start=1):
                print(f"[{idx}] {r[2]}반 {r[3]}번 {r[4]} | 진로: {r[5]} | 작품: {r[6]} | 글자수: {r[15]}자 | 상태: {r[16]}")
                
    except Exception as e:
        print("Error fetching sheet values:", e)

if __name__ == '__main__':
    main()
