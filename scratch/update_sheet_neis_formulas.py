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
    print("=== 구글 스프레드시트 E열(NEIS 바이트 수식) 및 F열(글자 수 수식) 자동 입력 스크립트 ===")
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json missing")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service_sheets = build('sheets', 'v4', credentials=creds)
    
    spreadsheet_id = "10diJ7L5Z-mtwDsRndOYv4cGx_OZMsSmwxvZ_kndmF24"
    tabs = ['1~3반', '4~6반', '7~10반']
    
    for tab_name in tabs:
        # 데이터가 있는 전체 행 수 가져오기
        res = service_sheets.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{tab_name}!A1:D100"
        ).execute()
        rows = res.get('values', [])
        num_rows = len(rows)
        if num_rows <= 1:
            continue
            
        e_f_formulas = []
        for r_idx in range(2, num_rows + 1):
            # NEIS 바이트 수식: LENB(D{r_idx}) + (LEN(D{r_idx}) - LEN(SUBSTITUTE(D{r_idx}, CHAR(10), "")))
            # 한글/전각 3B, 영문/공백 1B, 줄바꿈 2B
            b_formula = f'=LENB(D{r_idx}) + (LEN(D{r_idx}) - LEN(SUBSTITUTE(D{r_idx}, CHAR(10), ""))) & " Bytes"'
            c_formula = f'=LEN(D{r_idx}) & "자"'
            e_f_formulas.append([b_formula, c_formula])
            
        service_sheets.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{tab_name}!E2:F{num_rows}",
            valueInputOption="USER_ENTERED",
            body={"values": e_f_formulas}
        ).execute()
        print(f"  └ ✅ {tab_name} 탭 E2:F{num_rows} NEIS 바이트 수식 및 글자 수 수식 입력 완료")
        
    print("\n🎉 모든 탭의 NEIS 바이트 및 글자 수 동적 수식 업데이트가 완수되었습니다!")

if __name__ == "__main__":
    main()
