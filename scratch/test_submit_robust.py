import requests
import urllib3
import time
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FORM_URL = "https://docs.google.com/forms/d/1eWucmez2c6h1qT7nwuA0by_GwQaJS8N-N8M0wLZ_qAE/formResponse"

payload = {
    # Class Selection
    "entry.961434093": "9반",
    "entry.1225269417": "9반",
    
    # Class 9 Name Selection
    "entry.185372250": "14번 박규성",
    "entry.1124961061": "14번 박규성",
    
    # Q16
    "entry.786998359": "의도하지 않은 상태에서 탐구 목적과는 관계없이 우연적으로 이루어진 발견이 엄청난 의미를 가지고 있음이 드러난 발견",
    "entry.1520619704": "의도하지 않은 상태에서 탐구 목적과는 관계없이 우연적으로 이루어진 발견이 엄청난 의미를 가지고 있음이 드러난 발견",
    
    # Q17
    "entry.1567984727": "플레밍",
    "entry.338011484": "플레밍",
    
    # Q18
    "entry.549236679": "페니실린이 불안정하다. 박테리아를 죽이는 데 즉각적이지 않았다.",
    "entry.1851975331": "페니실린이 불안정하다. 박테리아를 죽이는 데 즉각적이지 않았다.",
    
    # Q19
    "entry.1923200604": "페니실린의 베타-락탐이 펩타이드 전이 효소와 결합하여 박테리아의 세포벽을 약화시킨다.",
    "entry.1842842402": "페니실린의 베타-락탐이 펩타이드 전이 효소와 결합하여 박테리아의 세포벽을 약화시킨다.",
    
    # Q20
    "entry.668103064": "그람 양성균에 없는 박테리아 외막 구조가 있기 때문이다.",
    "entry.962604409": "그람 양성균에 없는 박테리아 외막 구조가 있기 때문이다."
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

print("Submitting robust payload...")
response = requests.post(FORM_URL, data=payload, headers=headers, verify=False, timeout=15)
print("Status Code:", response.status_code)

# Now check the Google Sheet
time.sleep(5)
token_path = 'token.json'
creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
sheets_service = build('sheets', 'v4', credentials=creds)
meta = sheets_service.spreadsheets().get(spreadsheetId='1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU').execute()
sheet_title = meta['sheets'][0]['properties']['title']
res = sheets_service.spreadsheets().values().get(spreadsheetId='1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU', range=f'\'{sheet_title}\'!A:Q').execute()
values = res.get('values', [])
print('Total rows in Google Sheet:', len(values))
print('Last row in Google Sheet:', values[-1] if values else 'None')
