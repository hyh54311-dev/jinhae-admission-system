import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

token_path = 'token.json'
spreadsheet_id = '1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU'
target_sheet_title = '설문지 응답 시트6'
row_to_delete = 156  # 1-indexed

try:
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    sheets_service = build('sheets', 'v4', credentials=creds)
    
    # 1. Get sheetId of the target tab
    meta = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheet_id = None
    for sheet in meta.get('sheets', []):
        props = sheet.get('properties', {})
        if props.get('title') == target_sheet_title:
            sheet_id = props.get('sheetId')
            break
            
    if sheet_id is None:
        raise ValueError(f"Sheet '{target_sheet_title}' not found.")
        
    print(f"Found Sheet ID for '{target_sheet_title}': {sheet_id}")
    
    # 2. Verify row 156 contents before deletion
    res_before = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'{target_sheet_title}'!A156:Q156"
    ).execute()
    row_data = res_before.get('values', [])
    if row_data:
        print(f"Row 156 content before deletion: {row_data[0]}")
    else:
        print("Row 156 is empty. Deletion aborted to prevent error.")
        sys.exit(0)
        
    # 3. Request deleteDimension (0-indexed start/end, so Row 156 is index 155 to 156)
    body = {
        "requests": [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": row_to_delete - 1,
                        "endIndex": row_to_delete
                    }
                }
            }
        ]
    }
    
    response = sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()
    print("Delete row API response:", response)
    
    # 4. Verify new row count and last rows
    res_after = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'{target_sheet_title}'!A:Q"
    ).execute()
    values = res_after.get('values', [])
    print(f"Verified new total rows in sheet: {len(values)}")
    print("Last 3 rows now:")
    for idx, row in enumerate(values[-3:]):
        print(f"  Row {len(values) - 2 + idx}: {row[:6]}...")
        
except Exception as e:
    print("Error:", e)
