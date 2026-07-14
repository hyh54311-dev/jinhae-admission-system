import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = 'token_accounting.json'
SHEET_ID = '1yHEJsvgtQ6crum5H3PuKZzoQzEOxUhs5tT1_WUJzGr8'

def delete_row():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE)
    service = build('sheets', 'v4', credentials=creds)

    # 3踰덉㎏ ???몃뜳??2) ?꾩쟾 ??젣
    requests = []
    requests.append({
        'deleteDimension': {
            'range': {
                'sheetId': 0, # ?쒗듃1
                'dimension': 'ROWS',
                'startIndex': 2,
                'endIndex': 3
            }
        }
    })
    
    try:
        service.spreadsheets().batchUpdate(
            spreadsheetId=SHEET_ID, body={'requests': requests}).execute()
        print("Example row deleted successfully.")
    except Exception as e:
        # ?뱀떆 ????젣 ???媛믪쓣 鍮꾩썙???섎뒗 寃쎌슦 ?鍮?        print(f"Error, attempting value clear instead: {e}")
        service.spreadsheets().values().clear(
            spreadsheetId=SHEET_ID, range="A3:M3").execute()

if __name__ == '__main__':
    delete_row()
