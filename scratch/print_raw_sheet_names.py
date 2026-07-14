import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    token_path = 'token.json'
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service = build('sheets', 'v4', credentials=creds)
    
    sheet_ids = [
        '1EReikad-ObOGz1eQBRrkcWhAq-ViHL38BmL6uCI7mqc',
        '1VU8Kwa7c5wD0LlFaQaHoAmVt-Il9saOt6e9iGXqQReQ',
        '1mo8VwNcAPCOw0julQWpvMFUvHHbtwAVY0DHSFAaQcvk',
        '1eBxIut6dQIo3PoRvA9unwwBb4KQWlrBiyoXrTVMrLv4',
        '1VU8Kwa7c5wD0LlFaQaHoAmVt-Il9saOt6e9iGXqQReQ'
    ]
    
    for sid in sheet_ids:
        try:
            metadata = service.spreadsheets().get(spreadsheetId=sid).execute()
            title = metadata.get('properties', {}).get('title', 'Unknown')
            print(f"Spreadsheet: {title} ({sid})")
            for s in metadata.get('sheets', []):
                s_title = s.get('properties', {}).get('title')
                s_title_decoded = "".join([chr(ord(c)) for c in s_title])
                print(f"  Sheet Title Decoded: {s_title_decoded} | Hex: {[hex(ord(c)) for c in s_title]}")
        except Exception as e:
            print(f"Spreadsheet: {sid} | Error: {e}")

if __name__ == '__main__':
    main()
