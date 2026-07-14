import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token.json'
spreadsheet_id = '12bXJl_SRj8mVIZBBADWix8ZZ5Rh7XKFodH62iGzDTF8'
output_path = 'scratch/sheet_details.txt'

try:
    creds = Credentials.from_authorized_user_file(token_path)
    sheets_service = build('sheets', 'v4', credentials=creds)
    
    meta = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    title = meta.get('properties', {}).get('title')
    
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(f"Spreadsheet Title: {title}\n")
        
        for idx, sheet in enumerate(meta.get('sheets', [])):
            sheet_title = sheet.get('properties', {}).get('title')
            out.write(f"Sheet [{idx}]: {sheet_title}\n")
            
except Exception as e:
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(f"Error: {e}\n")
