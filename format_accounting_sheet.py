import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = 'token_accounting.json'
SHEET_ID = '1yHEJsvgtQ6crum5H3PuKZzoQzEOxUhs5tT1_WUJzGr8'

def get_sheets_service():
    if not os.path.exists(TOKEN_FILE):
        print(f"Error: {TOKEN_FILE} not found. Cannot format the sheet.")
        return None
    creds = Credentials.from_authorized_user_file(TOKEN_FILE)
    return build('sheets', 'v4', credentials=creds)

def format_sheet(service):
    # 1. 諛대뵫(Zebra striping) 而щ윭 異붽?
    # 2. 泥????ㅽ겕 ?ㅼ씠鍮??ㅻ뜑
    # 3. ?곗씠?????섏쭅/?섑룊 ?뺣젹
    # 4. ?꾩껜 ???믪씠 40px ?뺤옣
    
    # 諛대뵫 異붽? ?? 以묐났 諛⑹?瑜??꾪빐 湲곗〈 諛대뵫??議고쉶 ????젣?섎뒗 湲곕뒫? ?앸왂
    # (?덈줈 留뚮뱺 ?쒗듃?대?濡?諛대뵫???녿떎???꾩젣)
    
    requests = []
    
    # [1] ?꾩껜 ???믪씠 ?뺤옣 (40px)
    requests.append({
        'updateDimensionProperties': {
            'range': {
                'sheetId': 0, 'dimension': 'ROWS', 
                'startIndex': 0, 'endIndex': 100
            },
            'properties': {'pixelSize': 40},
            'fields': 'pixelSize'
        }
    })
    
    # [2] 泥?踰덉㎏ ???ㅻ뜑) 怨좉툒 ?ㅼ씠鍮?而щ윭濡??쒖떇 蹂寃?    requests.append({
        'repeatCell': {
            'range': {
                'sheetId': 0, 'startRowIndex': 0, 'endRowIndex': 1,
                'startColumnIndex': 0, 'endColumnIndex': 13
            },
            'cell': {
                'userEnteredFormat': {
                    'backgroundColor': {'red': 0.11, 'green': 0.23, 'blue': 0.34}, # Dark Navy
                    'textFormat': {
                        'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}, # White
                        'bold': True,
                        'fontSize': 11
                    },
                    'horizontalAlignment': 'CENTER',
                    'verticalAlignment': 'MIDDLE'
                }
            },
            'fields': 'userEnteredFormat(backgroundColor,textFormat(foregroundColor,bold,fontSize),horizontalAlignment,verticalAlignment)'
        }
    })
    
    # [3] 紐⑤뱺 ?곗씠?????섏쭅 以묒븰 ?뺣젹 諛?媛?낆꽦
    requests.append({
        'repeatCell': {
            'range': {
                'sheetId': 0, 'startRowIndex': 1, 'endRowIndex': 100,
                'startColumnIndex': 0, 'endColumnIndex': 13
            },
            'cell': {
                'userEnteredFormat': {
                    'verticalAlignment': 'MIDDLE',
                    'horizontalAlignment': 'CENTER',
                    'textFormat': {
                        'fontSize': 10
                    }
                }
            },
            'fields': 'userEnteredFormat(verticalAlignment,horizontalAlignment,textFormat(fontSize))'
        }
    })
    
    # [4] ?/吏앹닔 ??援먯감 ?뚯쁺 (吏釉뚮씪 ?쇱씤)
    requests.append({
        'addBanding': {
            'bandedRange': {
                'range': {
                    'sheetId': 0, 'startRowIndex': 1, 'endRowIndex': 100,
                    'startColumnIndex': 0, 'endColumnIndex': 13
                },
                'rowProperties': {
                    'firstBandColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}, # ?곗깋
                    'secondBandColor': {'red': 0.95, 'green': 0.95, 'blue': 0.95} # ?꾩＜ ?고븳 ?뚯깋
                }
            }
        }
    })
    
    # [5] 而щ읆 ?덈퉬 ?쎄컙 議곗젙 (A, B, C ??媛?낆꽦???꾪빐)
    # A(Date) 110px
    requests.append({
        'updateDimensionProperties': {
            'range': {'sheetId': 0, 'dimension': 'COLUMNS', 'startIndex': 0, 'endIndex': 1},
            'properties': {'pixelSize': 100},
            'fields': 'pixelSize'
        }
    })
    # B(Place) 120px
    requests.append({
        'updateDimensionProperties': {
            'range': {'sheetId': 0, 'dimension': 'COLUMNS', 'startIndex': 1, 'endIndex': 2},
            'properties': {'pixelSize': 120},
            'fields': 'pixelSize'
        }
    })
    # C(Amount) 120px
    requests.append({
        'updateDimensionProperties': {
            'range': {'sheetId': 0, 'dimension': 'COLUMNS', 'startIndex': 2, 'endIndex': 3},
            'properties': {'pixelSize': 110},
            'fields': 'pixelSize'
        }
    })
    
    # ?ㅽ뻾
    try:
        service.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body={'requests': requests}).execute()
        print("Success! Sheet has been completely reformatted.")
    except Exception as e:
        print(f"Error while formatting sheet: {e}")

def main():
    service = get_sheets_service()
    if service:
        format_sheet(service)

if __name__ == '__main__':
    main()
