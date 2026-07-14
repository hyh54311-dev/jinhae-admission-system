import os
import sys
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

def submit_one():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("Error: token.json does not exist. Please authorize first.")
        return
        
    spreadsheet_id = '1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU'
    
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
        sheets_service = build('sheets', 'v4', credentials=creds)
        
        # Get sheet title dynamically
        sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', [])
        first_sheet_title = sheets[0].get('properties', {}).get('title')
        range_name = f"'{first_sheet_title}'!A:Q"
        
        # Current timestamp
        now = datetime.datetime.now()
        am_pm = "오전" if now.hour < 12 else "오후"
        hour = now.hour
        if hour > 12:
            hour = hour - 12
        elif hour == 0:
            hour = 12
        timestamp_str = f"{now.year}. {now.month}. {now.day}. {am_pm} {hour}:{now.minute:02d}:{now.second:02d}"
        
        # Row data for Park Gyu-seong (Class 9, No. 14)
        # Col 0: Timestamp
        # Col 1: Class ("9반")
        # Col 2-9: Class 1 to 8 Name (Empty "")
        # Col 10: Class 9 Name ("14번 박규성")
        # Col 11: Class 10 Name (Empty "")
        # Col 12: Q16
        # Col 13: Q17
        # Col 14: Q18
        # Col 15: Q19
        # Col 16: Q20
        row = [
            timestamp_str,
            "9반",
            "", "", "", "", "", "", "", "", # 1반 to 8반 빈값 (8개)
            "14번 박규성",                   # 9반 이름 (Col 10)
            "",                             # 10반 이름 (Col 11)
            "의도하지 않은 상태에서 탐구 목적과는 관계없이 우연적으로 이루어진 발견이 엄청난 의미를 가지고 있음이 드러난 발견", # Q16
            "플레밍",                        # Q17
            "페니실린이 불안정하다. 박테리아를 죽이는 데 즉각적이지 않았다.", # Q18
            "페니실린의 베타-락탐이 펩타이드 전이 효소와 결합하여 박테리아의 세포벽을 약화시킨다.", # Q19
            "그람 양성균에 없는 박테리아 외막 구조가 있기 때문이다." # Q20
        ]
        
        body = {
            'values': [row]
        }
        
        print(f"Appending response for 9반 14번 박규성 to {first_sheet_title}...")
        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()
        
        print("Success! Row appended.")
        print(f"Updated range: {result.get('updates', {}).get('updatedRange')}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    submit_one()
