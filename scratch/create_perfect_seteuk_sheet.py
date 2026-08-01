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

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json missing")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service_sheets = build('sheets', 'v4', credentials=creds)
    service_drive = build('drive', 'v3', credentials=creds)
    
    src_spreadsheet_id = "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"
    
    # 1. 기존 데이터에서 74명 학생 정보 가져오기
    result = service_sheets.spreadsheets().values().get(
        spreadsheetId=src_spreadsheet_id,
        range="탐구보고서_응답!A2:Q100"
    ).execute()
    
    rows = result.get('values', [])
    if not rows:
        print("No rows found in source sheet")
        return
        
    student_list = []
    for r in rows:
        grade = r[1] if len(r) > 1 else "2"
        ban = r[2] if len(r) > 2 else ""
        num = r[3] if len(r) > 3 else ""
        name = r[4] if len(r) > 4 else ""
        draft = r[14] if len(r) > 14 else ""
        
        if not name or not draft:
            continue
            
        ban_num = int(ban) if ban.isdigit() else 99
        num_num = int(num) if num.isdigit() else 99
        
        byte_cnt = calculate_byte(draft)
        char_cnt = len(draft)
        
        student_list.append({
            "ban": ban_num,
            "num": num_num,
            "ban_str": f"{ban}반",
            "num_str": f"{num}번",
            "name": name,
            "draft": draft,
            "byte_cnt": f"{byte_cnt} Bytes",
            "char_cnt": f"{char_cnt}자"
        })
        
    # 2. 반, 번호 순 정렬
    student_list.sort(key=lambda x: (x["ban"], x["num"]))
    
    # 3. 새로운 구글 시트 생성 ("2학년 문학 탐구보고서 세특 초안")
    spreadsheet_body = {
        'properties': {
            'title': '2학년 문학 탐구보고서 세특 초안'
        }
    }
    new_sheet = service_sheets.spreadsheets().create(
        body=spreadsheet_body,
        fields='spreadsheetId,sheets.properties'
    ).execute()
    
    new_spreadsheet_id = new_sheet.get('spreadsheetId')
    sheet_title = new_sheet['sheets'][0]['properties']['title']
    sheet_id = new_sheet['sheets'][0]['properties']['sheetId']
    print(f"Created New Spreadsheet ID: {new_spreadsheet_id} (Sheet Title: {sheet_title})")
    
    # 4. 헤더 및 데이터 준비
    header = ['반', '번호', '이름', '세특 초안', '바이트 수(NEIS 기준)', '글자 수(공백 포함)']
    data_values = [header]
    
    for s in student_list:
        data_values.append([
            s["ban_str"],
            s["num_str"],
            s["name"],
            s["draft"],
            s["byte_cnt"],
            s["char_cnt"]
        ])
        
    # 5. 새 시트에 데이터 입력
    body = {
        'values': data_values
    }
    service_sheets.spreadsheets().values().update(
        spreadsheetId=new_spreadsheet_id,
        range=f"'{sheet_title}'!A1",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    
    # 6. 보기 좋은 서식 설정 (헤더 배경색, 자동 줄바꿈, 폰트/정렬)
    requests = [
        # 헤더 서식 (네이비 배경 + 흰색 볼드 텍스트 + 중앙 정렬)
        {
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 0,
                    'endRowIndex': 1,
                    'startColumnIndex': 0,
                    'endColumnIndex': 6
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.12, 'green': 0.23, 'blue': 0.43},
                        'textFormat': {'bold': True, 'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}, 'fontSize': 11},
                        'horizontalAlignment': 'CENTER',
                        'verticalAlignment': 'MIDDLE'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)'
            }
        },
        # 세특 초안 열(D열) 자동 줄바꿈(WRAP) 및 수직 가운데 정렬
        {
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 1,
                    'endRowIndex': len(data_values),
                    'startColumnIndex': 3,
                    'endColumnIndex': 4
                },
                'cell': {
                    'userEnteredFormat': {
                        'wrapStrategy': 'WRAP',
                        'verticalAlignment': 'MIDDLE'
                    }
                },
                'fields': 'userEnteredFormat(wrapStrategy,verticalAlignment)'
            }
        },
        # A, B, C, E, F열 중앙 정렬
        {
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 1,
                    'endRowIndex': len(data_values),
                    'startColumnIndex': 0,
                    'endColumnIndex': 3
                },
                'cell': {
                    'userEnteredFormat': {
                        'horizontalAlignment': 'CENTER',
                        'verticalAlignment': 'MIDDLE'
                    }
                },
                'fields': 'userEnteredFormat(horizontalAlignment,verticalAlignment)'
            }
        },
        {
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 1,
                    'endRowIndex': len(data_values),
                    'startColumnIndex': 4,
                    'endColumnIndex': 6
                },
                'cell': {
                    'userEnteredFormat': {
                        'horizontalAlignment': 'CENTER',
                        'verticalAlignment': 'MIDDLE'
                    }
                },
                'fields': 'userEnteredFormat(horizontalAlignment,verticalAlignment)'
            }
        },
        # 열 너비 조절 (D열 너비 650px 지정)
        {
            'updateDimensionProperties': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'COLUMNS',
                    'startIndex': 3,
                    'endIndex': 4
                },
                'properties': {
                    'pixelSize': 650
                },
                'fields': 'pixelSize'
            }
        }
    ]
    
    service_sheets.spreadsheets().batchUpdate(
        spreadsheetId=new_spreadsheet_id,
        body={'requests': requests}
    ).execute()
    
    # 7. 보기 공유 권한 설정 (링크가 있는 모든 사용자 보기)
    user_permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    service_drive.permissions().create(
        fileId=new_spreadsheet_id,
        body=user_permission
    ).execute()
    
    new_sheet_url = f"https://docs.google.com/spreadsheets/d/{new_spreadsheet_id}/edit?usp=sharing"
    print(f"\n✅ New Formatted Spreadsheet Created Successfully!")
    print(f"URL: {new_sheet_url}")

if __name__ == '__main__':
    main()
