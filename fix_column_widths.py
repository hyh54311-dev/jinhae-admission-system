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

def fix_widths(service):
    requests = []
    
    # [A] ?좎쭨: 120px
    requests.append({'updateDimensionProperties': {'range': {'sheetId': 0, 'dimension': 'COLUMNS', 'startIndex': 0, 'endIndex': 1}, 'properties': {'pixelSize': 120}, 'fields': 'pixelSize'}})
    # [B] ?ъ슜泥? 160px
    requests.append({'updateDimensionProperties': {'range': {'sheetId': 0, 'dimension': 'COLUMNS', 'startIndex': 1, 'endIndex': 2}, 'properties': {'pixelSize': 160}, 'fields': 'pixelSize'}})
    # [C] 珥?吏異?湲덉븸: 140px
    requests.append({'updateDimensionProperties': {'range': {'sheetId': 0, 'dimension': 'COLUMNS', 'startIndex': 2, 'endIndex': 3}, 'properties': {'pixelSize': 140}, 'fields': 'pixelSize'}})
    # [D~I] 遺?쒖썝 ?대쫫??(理쒖???遺?λ떂 ~ ?⑹슂???좎깮??: 媛?150px
    requests.append({'updateDimensionProperties': {'range': {'sheetId': 0, 'dimension': 'COLUMNS', 'startIndex': 3, 'endIndex': 9}, 'properties': {'pixelSize': 145}, 'fields': 'pixelSize'}})
    # [J] 李몄꽍 ?몄썝: 110px
    requests.append({'updateDimensionProperties': {'range': {'sheetId': 0, 'dimension': 'COLUMNS', 'startIndex': 9, 'endIndex': 10}, 'properties': {'pixelSize': 110}, 'fields': 'pixelSize'}})
    # [K] 1?몃떦 ?뺤궛?? 140px
    requests.append({'updateDimensionProperties': {'range': {'sheetId': 0, 'dimension': 'COLUMNS', 'startIndex': 10, 'endIndex': 11}, 'properties': {'pixelSize': 140}, 'fields': 'pixelSize'}})
    # [L] 寃곗젣?? 100px
    requests.append({'updateDimensionProperties': {'range': {'sheetId': 0, 'dimension': 'COLUMNS', 'startIndex': 11, 'endIndex': 12}, 'properties': {'pixelSize': 100}, 'fields': 'pixelSize'}})
    # [M] 鍮꾧퀬: 250px
    requests.append({'updateDimensionProperties': {'range': {'sheetId': 0, 'dimension': 'COLUMNS', 'startIndex': 12, 'endIndex': 13}, 'properties': {'pixelSize': 250}, 'fields': 'pixelSize'}})
    
    # ?ㅽ뻾
    try:
        service.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body={'requests': requests}).execute()
        print("Success! Column widths successfully fixed.")
    except Exception as e:
        print(f"Error while fixing widths: {e}")

if __name__ == '__main__':
    service = get_sheets_service()
    if service:
        fix_widths(service)
