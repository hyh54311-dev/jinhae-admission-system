import requests
import urllib3
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Use the published Form ID formResponse URL
PUBLISHED_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdhoKp3oOBxIPuhTGy0Q9LMCw3emDYAJ-i-jEVkSOgCmMP2IA/formResponse"
spreadsheet_id = '1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU'

payload = {
    # Class Selection
    "entry.1225269417": "8반",
    
    # 8반 Name Selection
    "entry.1818992395": "4번 김동현",
    
    # Q16-20
    "entry.1520619704": "TEST Q16",
    "entry.338011484": "TEST Q17",
    "entry.1851975331": "TEST Q18",
    "entry.1842842402": "TEST Q19",
    "entry.962604409": "TEST Q20"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

print("Submitting to published Form...")
res = requests.post(PUBLISHED_FORM_URL, data=payload, headers=headers, verify=False, timeout=15)
print("Form Submission Status Code:", res.status_code)

print("Waiting 5 seconds for Google Sheets to sync...")
time.sleep(5)

try:
    token_path = 'token.json'
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    sheets_service = build('sheets', 'v4', credentials=creds)
    
    meta = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for sheet in meta.get('sheets', []):
        title = sheet.get('properties', {}).get('title')
        if '응답 6' in title:
            val_res = sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"'{title}'!A:J"
            ).execute()
            values = val_res.get('values', [])
            print(f"Spreadsheet Title: {meta.get('properties', {}).get('title')}")
            print(f"Sheet '{title}' row count: {len(values)}")
            print(f"Last row in spreadsheet: {values[-1] if values else 'None'}")
            
except Exception as e:
    print("Error checking sheet:", e)
