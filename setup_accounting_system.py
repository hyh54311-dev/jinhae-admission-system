import os
import json
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/tasks' # ?쒖뒪??異붽? ?곌린 沅뚰븳
]

FOLDER_ID = '1G8bF6VpQ7PWR-kAbeNPT8AYAgvSmze3e'
TOKEN_FILE = 'token_accounting.json'
CRED_FILE = 'credentials.json'

def get_services():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            
    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    tasks_service = build('tasks', 'v1', credentials=creds)
    return drive_service, sheets_service, tasks_service

def setup_sheet(drive_service, sheets_service):
    # 1. ?쒕씪?대툕 ?대뜑???쒗듃 ?앹꽦
    file_metadata = {
        'name': '2026?숇뀈??1?숆린 援먮Т湲고쉷遺 寃쎈퉬 ?뺤궛遺',
        'parents': [FOLDER_ID],
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    file = drive_service.files().create(body=file_metadata, fields='id, webViewLink').execute()
    sheet_id = file.get('id')
    print(f"Spreadsheet Created: {file.get('webViewLink')}")
    
    # 2. 媛?諛??묒떇 ?명똿
    headers = [
        "?좎쭨", "?ъ슜泥?, "珥?吏異?湲덉븸", 
        "理쒖???遺?λ떂", "諛뺤????좎깮??, "諛뺤듅???좎깮??, 
        "?대퀝???좎깮??, "源?꾩닕 二쇰Т愿??, "?⑹슂???좎깮??, 
        "李몄꽍 ?몄썝", "1?몃떦 ?뺤궛??, "寃곗젣??, "鍮꾧퀬"
    ]
    
    # 2?됱쓽 珥덇린媛?(?ㅻ뒛 而ㅽ뵾媛? 湲덉븸? 鍮꾩썙??
    # 泥댄겕諛뺤뒪??臾몄옄??TRUE/FALSE濡??낅젰?섎㈃ ?곸슜??(?쒖떇 ?명똿 湲곗?)
    row2 = [
        "2026-04-03", "移댄럹", "", 
        "TRUE", "TRUE", "TRUE", 
        "TRUE", "FALSE", "TRUE",
        "=COUNTIF(D2:I2, TRUE)", "=IF(J2>0, ROUND(C2/J2, 0), 0)", "?⑹슂??, ""
    ]
    
    # ?곗씠???낅뜲?댄듃
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': [
            {'range': 'A1:M1', 'values': [headers]},
            {'range': 'A2:M2', 'values': [row2]}
        ]
    }
    sheets_service.spreadsheets().values().batchUpdate(
        spreadsheetId=sheet_id, body=body).execute()
        
    # 3. ?쒖떇 媛뺤젣 ?명똿 (泥댄겕諛뺤뒪 ?앹꽦, 泥???怨좎젙 ??
    requests = []
    # ?곗씠??寃利?(泥댄겕諛뺤뒪) D2:I100 踰붿쐞
    requests.append({
        'setDataValidation': {
            'range': {
                'sheetId': 0, 'startRowIndex': 1, 'endRowIndex': 100,
                'startColumnIndex': 3, 'endColumnIndex': 9
            },
            'rule': {
                'condition': {'type': 'BOOLEAN'},
                'showCustomUi': True
            }
        }
    })
    # 泥???怨좎젙 諛??ㅻ뜑 援듦쾶, 以묒븰 ?뺣젹
    requests.append({
        'updateSheetProperties': {
            'properties': {
                'sheetId': 0,
                'gridProperties': {'frozenRowCount': 1}
            },
            'fields': 'gridProperties.frozenRowCount'
        }
    })
    requests.append({
        'repeatCell': {
            'range': {
                'sheetId': 0, 'startRowIndex': 0, 'endRowIndex': 1,
                'startColumnIndex': 0, 'endColumnIndex': 13
            },
            'cell': {
                'userEnteredFormat': {
                    'textFormat': {'bold': True},
                    'horizontalAlignment': 'CENTER',
                    'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                }
            },
            'fields': 'userEnteredFormat(textFormat,horizontalAlignment,backgroundColor)'
        }
    })
    # ???믪씠/?덈퉬 ?먮룞議곗젙 (媛꾩씠)
    requests.append({
        'autoResizeDimensions': {
            'dimensions': {'sheetId': 0, 'dimension': 'COLUMNS', 'startIndex': 0, 'endIndex': 13}
        }
    })
    
    sheets_service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={'requests': requests}).execute()
    return sheet_id, file.get('webViewLink')

def create_task(tasks_service):
    # ?ㅻ뒛 ?ㅽ썑 6??由щ쭏?몃뜑???쒖뒪???앹꽦
    # Google Tasks API??留덇컧?쇱쓽 '?쒓컙' 遺遺꾩쓣 00:00:00.000Z濡??쒗븳?⑸땲??
    # ?섏?留?理쒖떊 ?섍꼍?먯꽌 紐⑤컮???뚮┝???꾪빐 ?쒓컙???쒕ぉ??紐낆떆?섍퀬 ?ㅻ뒛 ?좎쭨濡??ｌ뒿?덈떎.
    today_str = datetime.datetime.now().strftime("%Y-%m-%dT00:00:00.000Z")
    
    task_body = {
        'title': '??[?ㅽ썑 6??由щ쭏?몃뱶] 援먮Т湲고쉷遺 移댄럹 ?뺤궛 湲덉븸 ?낅젰?섍린',
        'notes': '?덊떚洹몃옒鍮꾪떚 梨쀫큸?먭쾶 ?ㅻ뒛 ?ъ슜??移댄럹 珥앹븸???뚮젮二쇱떆硫? ?뺤궛 援ш? ?쒗듃???먮룞?쇰줈 梨꾩썙?ｊ퀬 1/N 湲덉븸??留덈Т由ы빀?덈떎.',
        'due': today_str
    }
    task = tasks_service.tasks().insert(tasklist='@default', body=task_body).execute()
    print(f"Task created: {task.get('title')}")

def main():
    print("?쒖뒪???몄쬆 ?쒖옉 (??李쎌뿉??沅뚰븳???뱀씤??二쇱꽭??...")
    drive_service, sheets_service, tasks_service = get_services()
    
    print("援ш? ?쒗듃 ?앹꽦 以?..")
    sheet_id, sheet_url = setup_sheet(drive_service, sheets_service)
    
    print("援ш? ?쒖뒪??由щ쭏?몃뜑 異붽? 以?..")
    create_task(tasks_service)
    
    print("紐⑤뱺 ?묒뾽 ?꾨즺!")
    print(f"?쒗듃 留곹겕: {sheet_url}")

if __name__ == '__main__':
    main()
