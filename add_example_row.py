import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = 'token_accounting.json'
SHEET_ID = '1yHEJsvgtQ6crum5H3PuKZzoQzEOxUhs5tT1_WUJzGr8'

def add_row():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE)
    service = build('sheets', 'v4', credentials=creds)

    # 3踰덉㎏ ??A3~M3)???쇨껸???덉젣 ?낅젰
    row3 = [
        "2026-04-03", 
        "?쇨껸?댁쭛", 
        "125000",       # 珥?吏異?湲덉븸
        "TRUE", "TRUE", "TRUE", "TRUE", "TRUE", "TRUE",  # 6紐??꾩썝 李몄꽍
        "=COUNTIF(D3:I3, TRUE)",   # 李몄꽍?몄썝?섏떇
        "=IF(J3>0, ROUND(C3/J3, 0), 0)", # N鍮?湲덉븸 ?섏떇
        "?⑹슂??, 
        "?먯떖 ?뚯떇"
    ]
    
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': [
            {'range': 'A3:M3', 'values': [row3]}
        ]
    }
    
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SHEET_ID, body=body).execute()
    print("Example row added successfully.")

if __name__ == '__main__':
    add_row()
