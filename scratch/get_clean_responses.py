import os
import sys
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SCOPES = ['https://www.googleapis.com/auth/drive']
SPREADSHEET_ID = '1uXPT8g0wc8-Ryufwk3yTr2RmX5TMraW4v5t9mBxpKYw'

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("Error: token.json does not exist.")
        return
        
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        sheets_service = build('sheets', 'v4', credentials=creds)
        
        # Read the sheet metadata to find correct sheet name (just in case there's any encoding shift)
        metadata = sheets_service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheet_titles = [s['properties']['title'] for s in metadata.get('sheets', [])]
        
        target_sheet = None
        if "교육과정_웹앱_응답" in sheet_titles:
            target_sheet = "교육과정_웹앱_응답"
        else:
            for title in sheet_titles:
                if "교육과정" in title:
                    target_sheet = title
                    break
                
        if not target_sheet:
            print("Could not find the response sheet in the spreadsheet.")
            return
            
        print(f"Reading from sheet: {target_sheet}")
        
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{target_sheet}'!A:Z"
        ).execute()
        
        rows = result.get('values', [])
        print(f"Total rows: {len(rows)}")
        
        # Output as JSON
        output_data = {
            "sheet_name": target_sheet,
            "headers": rows[0] if rows else [],
            "rows": rows[1:] if len(rows) > 1 else []
        }
        
        with open('scratch/curriculum_survey_data.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
            
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
