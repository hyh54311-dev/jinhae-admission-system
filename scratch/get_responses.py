import os
import sys
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SCOPES = ['https://www.googleapis.com/auth/drive']
SPREADSHEET_ID = '1CtFAtJnysSLa1JWExpPXzImvCxvvZcDU4OuiLqV0p10'

def main():
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("Error: token.json does not exist.")
        return
        
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        sheets_service = build('sheets', 'v4', credentials=creds)
        
        # Read all data from sheet
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, 
            range="'교육과정_웹앱_응답'!A:G"
        ).execute()
        rows = result.get('values', [])
        
        print(f"Total rows retrieved: {len(rows)}")
        
        # Write to JSON file
        output_path = 'scratch/curriculum_responses.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        print(f"Responses saved to {output_path}")
        
        # Print all responses cleanly
        for idx, r in enumerate(rows):
            print(f"Row {idx}: {r}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
