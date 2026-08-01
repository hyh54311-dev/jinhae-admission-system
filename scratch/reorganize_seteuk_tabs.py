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
    target_spreadsheet_id = "1lAff1XMoqh4qNweVB457cwCdDyOBm1s-G0Ufnvgk_BI"
    
    # 1. 기존 원본 데이터에서 74명 학생 정보 가져오기
    result = service_sheets.spreadsheets().values().get(
        spreadsheetId=src_spreadsheet_id,
        range="탐구보고서_응답!A2:Q100"
    ).execute()
    
    rows = result.get('values', [])
    if not rows:
        print("No rows found in source sheet")
        return
        
    group_1_3 = []  # 1~3반
    group_4_6 = []  # 4~6반
    group_7_10 = [] # 7~10반
    
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
        
        item = {
            "ban": ban_num,
            "num": num_num,
            "ban_str": f"{ban}반",
            "num_str": f"{num}번",
            "name": name,
            "draft": draft,
            "byte_cnt": f"{byte_cnt} Bytes",
            "char_cnt": f"{char_cnt}자"
        }
        
        if 1 <= ban_num <= 3:
            group_1_3.append(item)
        elif 4 <= ban_num <= 6:
            group_4_6.append(item)
        elif 7 <= ban_num <= 10:
            group_7_10.append(item)
            
    group_1_3.sort(key=lambda x: (x["ban"], x["num"]))
    group_4_6.sort(key=lambda x: (x["ban"], x["num"]))
    group_7_10.sort(key=lambda x: (x["ban"], x["num"]))
    
    print(f"Group 1~3반: {len(group_1_3)}명")
    print(f"Group 4~6반: {len(group_4_6)}명")
    print(f"Group 7~10반: {len(group_7_10)}명")
    
    # 2. 타겟 시트의 기존 탭 확인 및 3개 탭("1~3반", "4~6반", "7~10반") 생성/정리
    sheet_metadata = service_sheets.spreadsheets().get(spreadsheetId=target_spreadsheet_id).execute()
    existing_sheets = sheet_metadata.get('sheets', [])
    
    reqs = []
    
    # 새 탭 추가
    tab_names = ["1~3반", "4~6반", "7~10반"]
    tab_ids = {}
    
    for t_name in tab_names:
        found = False
        for s in existing_sheets:
            if s['properties']['title'] == t_name:
                found = True
                tab_ids[t_name] = s['properties']['sheetId']
                break
        if not found:
            # Add sheet
            add_res = service_sheets.spreadsheets().batchUpdate(
                spreadsheetId=target_spreadsheet_id,
                body={'requests': [{'addSheet': {'properties': {'title': t_name}}}]}
            ).execute()
            new_s_id = add_res['replies'][0]['addSheet']['properties']['sheetId']
            tab_ids[t_name] = new_s_id
            
    # 기존 '시트1' 또는 'Sheet1' 탭 삭제 (남아 있다면)
    for s in existing_sheets:
        title = s['properties']['title']
        s_id = s['properties']['sheetId']
        if title not in tab_names:
            try:
                service_sheets.spreadsheets().batchUpdate(
                    spreadsheetId=target_spreadsheet_id,
                    body={'requests': [{'deleteSheet': {'sheetId': s_id}}]}
                ).execute()
            except Exception as e:
                print(f"Delete sheet error: {e}")
                
    # 3. 각 탭에 데이터 채우기 및 서식 적용
    groups_data = [
        ("1~3반", group_1_3),
        ("4~6반", group_4_6),
        ("7~10반", group_7_10)
    ]
    
    header = ['반', '번호', '이름', '세특 초안', '바이트 수(NEIS 기준)', '글자 수(공백 포함)']
    
    for t_name, g_list in groups_data:
        s_id = tab_ids[t_name]
        data_values = [header]
        for s in g_list:
            data_values.append([
                s["ban_str"],
                s["num_str"],
                s["name"],
                s["draft"],
                s["byte_cnt"],
                s["char_cnt"]
            ])
            
        # 기존 내용 비우고 업데이트
        service_sheets.spreadsheets().values().clear(
            spreadsheetId=target_spreadsheet_id,
            range=f"'{t_name}'!A1:Z500"
        ).execute()
        
        service_sheets.spreadsheets().values().update(
            spreadsheetId=target_spreadsheet_id,
            range=f"'{t_name}'!A1",
            valueInputOption="USER_ENTERED",
            body={'values': data_values}
        ).execute()
        
        # 서식 지정 (네이비 헤더, 줄바꿈, 너비 설정)
        style_reqs = [
            # 헤더 서식
            {
                'repeatCell': {
                    'range': {
                        'sheetId': s_id,
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
            # D열 자동 줄바꿈
            {
                'repeatCell': {
                    'range': {
                        'sheetId': s_id,
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
            # A,B,C열 및 E,F열 중앙 정렬
            {
                'repeatCell': {
                    'range': {
                        'sheetId': s_id,
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
                        'sheetId': s_id,
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
            # D열 너비 650px 지정
            {
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': s_id,
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
            spreadsheetId=target_spreadsheet_id,
            body={'requests': style_reqs}
        ).execute()
        
    print(f"\n✅ Spreadsheet successfully reorganized into 3 tabs: '1~3반', '4~6반', '7~10반'!")
    print(f"URL: https://docs.google.com/spreadsheets/d/{target_spreadsheet_id}/edit?usp=sharing")

if __name__ == '__main__':
    main()
