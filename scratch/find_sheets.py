import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json not found")
        return
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service = build('sheets', 'v4', credentials=creds)
    
    sid = '1eBxIut6dQIo3PoRvA9unwwBb4KQWlrBiyoXrTVMrLv4'
    try:
        metadata = service.spreadsheets().get(spreadsheetId=sid).execute()
        title = metadata.get('properties', {}).get('title', 'Unknown')
        print(f"Spreadsheet Title: {title}")
        for s in metadata.get('sheets', []):
            s_title = s.get('properties', {}).get('title', 'Unknown')
            print(f"  Sheet Title: {s_title}")
            
            # Print first 2 rows of each sheet to check headers
            try:
                res = service.spreadsheets().values().get(
                    spreadsheetId=sid,
                    range=f"'{s_title}'!A1:N2"
                ).execute()
                rows = res.get('values', [])
                print(f"    First Row: {rows[0] if len(rows) > 0 else 'Empty'}")
            except Exception as se:
                print(f"    Error reading rows: {se}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
