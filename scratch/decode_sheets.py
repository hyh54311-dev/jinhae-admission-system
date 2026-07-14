import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

token_path = 'token.json'
output_path = 'scratch/sheets_list.txt'

try:
    creds = Credentials.from_authorized_user_file(token_path)
    drive_service = build('drive', 'v3', credentials=creds)
    
    query = "mimeType = 'application/vnd.google-apps.spreadsheet'"
    results = drive_service.files().list(
        q=query,
        pageSize=500,
        fields="files(id, name, webViewLink, createdTime, modifiedTime, owners)"
    ).execute()
    
    files = results.get('files', [])
    
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write("Google Sheets list (UTF-8 clean):\n")
        out.write("=" * 80 + "\n")
        for f in files:
            name = f.get('name', '')
            created = f.get('createdTime', '')
            modified = f.get('modifiedTime', '')
            owners = ", ".join([o.get('displayName', 'Unknown') for o in f.get('owners', [])])
            
            # Write all spreadsheets so we don't miss anything
            out.write(f"Name: {name}\n")
            out.write(f"ID:   {f.get('id')}\n")
            out.write(f"Link: {f.get('webViewLink')}\n")
            out.write(f"Created: {created} | Modified: {modified}\n")
            out.write(f"Owners: {owners}\n")
            out.write("-" * 80 + "\n")
            
    print(f"Successfully wrote {len(files)} sheets to {output_path}")
            
except Exception as e:
    print("Error:", e)
