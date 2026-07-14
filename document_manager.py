import os
import sys
import time
import json
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import PyPDF2
import google.generativeai as genai
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
from dotenv import load_dotenv

load_dotenv()

# --- 환경 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "document_manager_history.log")
PROCESSED_FILE = os.path.join(BASE_DIR, "processed_folders.txt")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")

DRIVE_FOLDER_ID = "1tHvEWDBtEoTURFy6xMps8qAELZbyidP9"
SHEET_NAME = "공문_관리_대장"
SCOPES = ['https://www.googleapis.com/auth/drive']

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMAIL_SENDER = "hyh54311@gmail.com"
EMAIL_PASSWORD = "obpv abgy acyh evho"
EMAIL_RECEIVER = "hyh54311@gmail.com"

genai.configure(api_key=GEMINI_API_KEY)

def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_message + "\n")
    except Exception as e:
        print(f"로그 기록 실패: {e}")

def get_google_services():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try: creds.refresh(Request())
            except: creds = None
        if not creds:
            if not os.path.exists(CREDENTIALS_FILE): return None, None, None
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=8140, open_browser=True)
        with open(TOKEN_FILE, 'w') as token: token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds), build('sheets', 'v4', credentials=creds), build('tasks', 'v1', credentials=creds)

def apply_premium_formatting(service, spreadsheet_id):
    requests = [
        {"updateSheetProperties": {"properties": {"sheetId": 0, "gridProperties": {"frozenRowCount": 1}}, "fields": "gridProperties.frozenRowCount"}},
        {"updateDimensionProperties": {"range": {"sheetId": 0, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2}, "properties": {"pixelSize": 450}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": 0, "dimension": "COLUMNS", "startIndex": 4, "endIndex": 5}, "properties": {"pixelSize": 550}, "fields": "pixelSize"}},
        {"repeatCell": {"range": {"sheetId": 0, "startRowIndex": 0, "endRowIndex": 1}, "cell": {"userEnteredFormat": {"backgroundColor": {"red": 0.0, "green": 0.2, "blue": 0.4}, "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}}}, "fields": "userEnteredFormat(backgroundColor,textFormat)"}}
    ]
    try: service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": requests}).execute()
    except: pass

def get_or_create_spreadsheet(drive_service, sheets_service):
    query = f"name = '{SHEET_NAME}' and '{DRIVE_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    headers = [["등록일", "공문 제목", "마감일", "시행기관", "요약", "상태"]]
    if files:
        sheet_id = files[0]['id']
        sheets_service.spreadsheets().values().update(spreadsheetId=sheet_id, range="A1", valueInputOption="RAW", body={"values": headers}).execute()
        apply_premium_formatting(sheets_service, sheet_id)
        return sheet_id
    else:
        file_metadata = {'name': SHEET_NAME, 'parents': [DRIVE_FOLDER_ID], 'mimeType': 'application/vnd.google-apps.spreadsheet'}
        file = drive_service.files().create(body=file_metadata, fields='id').execute()
        sheet_id = file.get('id')
        sheets_service.spreadsheets().values().update(spreadsheetId=sheet_id, range="A1", valueInputOption="RAW", body={"values": headers}).execute()
        apply_premium_formatting(sheets_service, sheet_id)
        return sheet_id

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages: text += (page.extract_text() or "") + "\n"
    except: pass
    return text

def analyze_folder_documents(folder_name, documents_info):
    try:
        model = genai.GenerativeModel('gemini-3.1-flash-lite')
        prompt = f"다음은 공문 폴더({folder_name})의 내용입니다. JSON 형식으로 추출하세요: name(제목), deadline(마감일 YYYY-MM-DD), provider(기관), summary(요약)."
        inputs = [prompt]
        combined_text = ""
        for doc in documents_info:
            if doc.get('image_path'):
                with open(doc['image_path'], "rb") as f: inputs.append({"mime_type": "image/jpeg", "data": f.read()})
            if doc.get('text'): combined_text += doc['text']
        if combined_text: inputs.append(combined_text[:30000])
        
        response = model.generate_content(inputs)
        content = response.text.strip()
        if "```" in content: content = content.split("```")[1].replace("json", "").strip()
        return json.loads(content)
    except: return None

def update_google_sheet(service, sheet_id, data):
    row = [datetime.now().strftime("%Y-%m-%d"), data.get("name", "N/A"), data.get("deadline", "마감 정보 없음"), data.get("provider", "N/A"), data.get("summary", "N/A"), "대기"]
    service.spreadsheets().values().append(spreadsheetId=sheet_id, range="A2", valueInputOption="RAW", body={"values": [row]}).execute()

def sync_and_check_reminders(sheets_service, tasks_service, sheet_id):
    try:
        result = sheets_service.spreadsheets().values().get(spreadsheetId=sheet_id, range="A:F").execute()
        rows = result.get('values', [])
        if len(rows) <= 1: return
        
        today = datetime.now().date()
        reminders = []
        for i, row in enumerate(rows[1:], start=2):
            if len(row) < 6: continue
            name, deadline_str, status = row[1], row[2], row[5]
            if status == "완료": continue
            if deadline_str and deadline_str not in ("N/A", "마감 정보 없음"):
                try:
                    deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
                    if deadline_date <= today + timedelta(days=7):
                        reminders.append(f"- {name} ({deadline_str})")
                except: continue
        if reminders: send_reminder_email(reminders)
    except: pass

def send_reminder_email(reminders):
    msg = MIMEMultipart()
    msg['Subject'] = f"[업무 알림] 공문 마감 안내 ({datetime.now().strftime('%Y-%m-%d')})"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    body = "<ul>" + "".join([f"<li>{r}</li>" for r in reminders]) + "</ul>"
    msg.attach(MIMEText(body, 'html'))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
    except: pass

def process_docs():
    drive_service, sheets_service, tasks_service = get_google_services()
    if not drive_service: return
    
    processed_folders = set()
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f: processed_folders = set(f.read().splitlines())

    query = f"'{DRIVE_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    folders = drive_service.files().list(q=query, fields="files(id, name)").execute().get('files', [])
    sheet_id = get_or_create_spreadsheet(drive_service, sheets_service)

    newly_processed = False
    for folder in folders:
        if folder['id'] in processed_folders: continue
        
        files = drive_service.files().list(q=f"'{folder['id']}' in parents and trashed = false").execute().get('files', [])
        documents_info = []
        for file in files:
            ext = os.path.splitext(file['name'])[1].lower()
            if ext in (".pdf", ".jpg", ".jpeg", ".png"):
                request = drive_service.files().get_media(fileId=file['id'])
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done: _, done = downloader.next_chunk()
                fh.seek(0)
                if ext == ".pdf": documents_info.append({'text': extract_text_from_pdf(io.BytesIO(fh.read())), 'path': file['name']})
                else:
                    tmp = f"temp_{file['name']}"
                    with open(tmp, "wb") as f: f.write(fh.read())
                    documents_info.append({'image_path': tmp})

        if documents_info:
            data = analyze_folder_documents(folder['name'], documents_info)
            if data:
                update_google_sheet(sheets_service, sheet_id, data)
                processed_folders.add(folder['id'])
                newly_processed = True
            for f in os.listdir("."):
                if f.startswith("temp_") and os.path.isfile(f): os.remove(f)

    if newly_processed:
        with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
            for fid in sorted(list(processed_folders)): f.write(f"{fid}\n")
    
    # sync_and_check_reminders(sheets_service, tasks_service, sheet_id)

if __name__ == "__main__":
    process_docs()
