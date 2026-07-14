import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = 'token_accounting.json'
SHEET_ID = '1yHEJsvgtQ6crum5H3PuKZzoQzEOxUhs5tT1_WUJzGr8'

def get_sheets_service():
    if not os.path.exists(TOKEN_FILE):
        return None
    creds = Credentials.from_authorized_user_file(TOKEN_FILE)
    return build('sheets', 'v4', credentials=creds)

def add_summary_tab(service):
    # 1. ?먮낯 ?쒗듃 ?대쫫 媛?몄삤湲?(?섏떇???ｊ린 ?꾪빐)
    spreadsheet = service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
    main_sheet = spreadsheet['sheets'][0]
    main_sheet_title = main_sheet['properties']['title']
    
    # 2. ???쒗듃 ?앹꽦 ?붿껌
    requests = []
    # 以묐났 ?ㅽ뻾 ???먮윭 諛⑹?瑜??꾪빐 ?쒕뜡?섍굅??怨좎젙??sheetId ?ъ슜, ?ш린??怨좎젙 ID(1111) ?좊떦
    tab_id = 1111
    requests.append({
        'addSheet': {
            'properties': {
                'sheetId': tab_id,
                'title': '媛쒖씤蹂?理쒖쥌 ?뺤궛',
                'gridProperties': {'frozenRowCount': 1}
            }
        }
    })
    
    try:
        service.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body={'requests': requests}).execute()
        print("New tab created successfully.")
    except Exception as e:
        if 'already exists' in str(e):
            print("Tab already exists. Proceeding to update.")
        else:
            raise e
            
    # 3. ?곗씠???낅젰 (Headers & Teachers)
    headers = ["?좎깮???깊븿", "?꾩쟻 吏異??⑷퀎", "?낃툑 ?꾨즺", "鍮꾧퀬"]
    teachers = [
        ("理쒖???遺?λ떂", "D"),
        ("諛뺤????좎깮??, "E"),
        ("諛뺤듅???좎깮??, "F"),
        ("?대퀝???좎깮??, "G"),
        ("源?꾩닕 二쇰Т愿??, "H"),
        ("?⑹슂???좎깮??, "I")
    ]
    
    values = [headers]
    for teacher, col in teachers:
        # SUMIF ?묒? ?섏떇: 硫붿씤?쒗듃???뱀젙 ?대쫫 而щ읆(D~I)??TRUE?쇰븣 K?댁쓽 ?뺤궛?≪쓣 ?뷀븿
        formula = f"=SUMIF('{main_sheet_title}'!{col}:{col}, TRUE, '{main_sheet_title}'!K:K)"
        values.append([teacher, formula, "FALSE", ""])
        
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': [
            {'range': f"'媛쒖씤蹂?理쒖쥌 ?뺤궛'!A1:D7", 'values': values}
        ]
    }
    service.spreadsheets().values().batchUpdate(spreadsheetId=SHEET_ID, body=body).execute()
    
    # 4. ?쒖떇 媛뺤젣 ?명똿 (?붿옄??紐⑤뱢)
    format_reqs = []
    
    # ???믪씠 40px
    format_reqs.append({
        'updateDimensionProperties': {
            'range': {'sheetId': tab_id, 'dimension': 'ROWS', 'startIndex': 0, 'endIndex': 20},
            'properties': {'pixelSize': 40},
            'fields': 'pixelSize'
        }
    })
    
    # ???덈퉬 ?명똿
    widths = [200, 200, 150, 300]
    for i, w in enumerate(widths):
        format_reqs.append({
            'updateDimensionProperties': {
                'range': {'sheetId': tab_id, 'dimension': 'COLUMNS', 'startIndex': i, 'endIndex': i+1},
                'properties': {'pixelSize': w},
                'fields': 'pixelSize'
            }
        })
        
    # ?ㅻ뜑 ?ㅽ겕 ?ㅼ씠鍮?    format_reqs.append({
        'repeatCell': {
            'range': {'sheetId': tab_id, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 4},
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': {'red': 0.11, 'green': 0.23, 'blue': 0.34},
                    'textFormat': {'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}, 'bold': True, 'fontSize': 12},
                    'horizontalAlignment': 'CENTER',
                    'verticalAlignment': 'MIDDLE'
                }
            },
            'fields': 'userEnteredFormat(backgroundColor,textFormat(foregroundColor,bold,fontSize),horizontalAlignment,verticalAlignment)'
        }
    })
    
    # ?곗씠????以묒븰?뺣젹 諛?湲덉븸 ?щ㎎ ?곸슜
    format_reqs.append({
        'repeatCell': {
            'range': {'sheetId': tab_id, 'startRowIndex': 1, 'endRowIndex': 10, 'startColumnIndex': 0, 'endColumnIndex': 4},
            'cell': {
                'userEnteredFormat': {
                    'verticalAlignment': 'MIDDLE',
                    'horizontalAlignment': 'CENTER',
                    'textFormat': {'fontSize': 11}
                }
            },
            'fields': 'userEnteredFormat(verticalAlignment,horizontalAlignment,textFormat(fontSize))'
        }
    })
    # 湲덉븸 ??(B) ?뚭퀎/?듯솕 ?щ㎎??    format_reqs.append({
        'repeatCell': {
            'range': {'sheetId': tab_id, 'startRowIndex': 1, 'endRowIndex': 10, 'startColumnIndex': 1, 'endColumnIndex': 2},
            'cell': {
                'userEnteredFormat': {'numberFormat': {'type': 'CURRENCY', 'pattern': '??,##0'}}
            },
            'fields': 'userEnteredFormat(numberFormat)'
        }
    })
    
    # 泥댄겕諛뺤뒪 異붽? (C???낃툑?꾨즺)
    format_reqs.append({
        'setDataValidation': {
            'range': {'sheetId': tab_id, 'startRowIndex': 1, 'endRowIndex': 7, 'startColumnIndex': 2, 'endColumnIndex': 3},
            'rule': {'condition': {'type': 'BOOLEAN'}, 'showCustomUi': True}
        }
    })
    
    # 吏釉뚮씪 ?⑦꽩 (Banding)
    format_reqs.append({
        'addBanding': {
            'bandedRange': {
                'range': {'sheetId': tab_id, 'startRowIndex': 1, 'endRowIndex': 7, 'startColumnIndex': 0, 'endColumnIndex': 4},
                'rowProperties': {
                    'firstBandColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0},
                    'secondBandColor': {'red': 0.95, 'green': 0.95, 'blue': 0.95}
                }
            }
        }
    })
    
    service.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body={'requests': format_reqs}).execute()
    print("Formatting applied successfully.")

if __name__ == '__main__':
    service = get_sheets_service()
    if service:
        add_summary_tab(service)
