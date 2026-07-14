import os
import sys
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("Error: token.json not found.")
        return
        
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        drive_service = build('drive', 'v3', credentials=creds)
        sheets_service = build('sheets', 'v4', credentials=creds)
        
        # Search for all spreadsheets
        query = "mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        
        found = False
        for f in files:
            file_id = f['id']
            file_name = f['name']
            
            try:
                sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=file_id).execute()
                sheet_titles = [s['properties']['title'] for s in sheet_metadata.get('sheets', [])]
                
                # We check if '교육과정_웹앱_응답' is in the sheet titles
                # Note: We do case-insensitive or partial match just in case
                for title in sheet_titles:
                    if "교육과정" in title or "웹앱" in title or "응답" in title:
                        print(f"Candidate: Spreadsheet name '{file_name}' (ID: {file_id}) has sheet '{title}'")
                        
                if "교육과정_웹앱_응답" in sheet_titles:
                    print(f"🎯 Found survey responses in spreadsheet '{file_name}' (ID: {file_id})!")
                    
                    # Fetch all values
                    val_result = sheets_service.spreadsheets().values().get(
                        spreadsheetId=file_id,
                        range=f"'{title}'!A:G" if title else "'교육과정_웹앱_응답'!A:G"
                    ).execute()
                    
                    rows = val_result.get('values', [])
                    print(f"Retrieved {len(rows)} rows from sheet '교육과정_웹앱_응답'.")
                    
                    # Write to a file
                    with open('scratch/survey_responses.json', 'w', encoding='utf-8') as out_f:
                        json.dump({
                            "spreadsheet_id": file_id,
                            "spreadsheet_name": file_name,
                            "rows": rows
                        }, out_f, ensure_ascii=False, indent=2)
                    
                    found = True
                    break
            except Exception as e:
                # print(f"Error checking {file_name}: {e}")
                pass
                
        if not found:
            print("Could not find any spreadsheet with sheet '교육과정_웹앱_응답'")
            
    except Exception as e:
        print(f"Main error: {e}")

if __name__ == '__main__':
    main()
