import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Force stdout to be utf-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("Error: token.json does not exist.")
        return
        
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        drive_service = build('drive', 'v3', credentials=creds)
        sheets_service = build('sheets', 'v4', credentials=creds)
        
        # Search for spreadsheets
        query = "mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
        results = drive_service.files().list(q=query, fields="files(id, name)", orderBy="modifiedTime desc", pageSize=30).execute()
        files = results.get('files', [])
        
        print(f"Checking {len(files)} spreadsheets...")
        for f in files:
            file_id = f['id']
            file_name = f['name']
            
            try:
                sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=file_id).execute()
                sheets = [s['properties']['title'] for s in sheet_metadata.get('sheets', [])]
                
                print(f"Spreadsheet: {file_name} (ID: {file_id})")
                print(f"  Sheets: {sheets}")
                
                if "교육과정_웹앱_응답" in sheets:
                    print(f"  🎯 FOUND CURRICULUM SURVEY SHEET: {file_name}")
                    # Fetch all rows from this sheet
                    result = sheets_service.spreadsheets().values().get(
                        spreadsheetId=file_id, 
                        range="'교육과정_웹앱_응답'!A:G"
                    ).execute()
                    rows = result.get('values', [])
                    print(f"  Rows Count: {len(rows)}")
                    if rows:
                        print("  Headers:", rows[0])
                        for idx, r in enumerate(rows[1:], 1):
                            print(f"    [{idx}] {r}")
                print("-" * 50)
            except Exception as se:
                print(f"  Error reading {file_name}: {se}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
