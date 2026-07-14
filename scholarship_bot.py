import os
import json
import time
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import smtplib
from datetime import datetime, timedelta
import schedule
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import PyPDF2
import re
from email.mime.multipart import MIMEMultipart
import PyPDF2
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "scholarship_bot_history.log")
PROCESSED_FILE = os.path.join(BASE_DIR, "processed_files.txt")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")

def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_message + "\n")
    except Exception as e:
        print(f"濡쒓렇 ?뚯씪 湲곕줉 ?ㅽ뙣: {e}")

# You need to set these environment variables or fill them in
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_SHEET_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyyb-twRpcch3HxeGDmlJ3CvdI8YlrBgMd995NHCaSNosBw4i3oQaIkN5BltNXkHKxk/exec"
EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "hyh54311@gmail.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "obpv abgy acyh evho")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER", "hyh54311@gmail.com")
DRIVE_BASE_FOLDER_ID = "1DS87llxQbHTWNt4x-rulxmtV-pOsGyV1"
SCOPES = ['https://www.googleapis.com/auth/drive']

genai.configure(api_key=GEMINI_API_KEY)

def get_drive_service():
    """Authenticate and return Google Drive API service."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                log_message(f"Credentials file not found at {CREDENTIALS_FILE}")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def get_target_folder_id(service, base_folder_id):
    """Determine the correct subfolder based on current date's 'last year equivalent'."""
    now = datetime.now()
    target_year = now.year - 1
    target_month = now.month
    
    target_name = f"{target_year}년 {target_month}월"

    query = f"'{base_folder_id}' in parents and name = '{target_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    
    if not items:
        log_message(f"Target folder '{target_name}' not found.")
        return None
    return items[0]['id']

def download_pdf(service, file_id, file_name):
    """Download a file from Google Drive to local temp copy."""
    request = service.files().get_media(fileId=file_id)
    content = request.execute()
    local_path = os.path.join(BASE_DIR, f"tmp_{file_name}")
    with open(local_path, 'wb') as f:
        f.write(content)
    return local_path

def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Failed to read PDF {pdf_path}: {e}")
    return text

def analyze_document_with_gemini(text):
    """Use Gemini to extract structured scholarship data from text."""
    prompt = f"""
?ㅼ쓬 ?ν븰湲?愿??臾몄꽌瑜?遺꾩꽍?섍퀬, ?꾨옒 ?뺣낫瑜?異붿텧?섏뿬 ?쒖닔 JSON ?щ㎎?쇰줈 諛섑솚?섏꽭?? ?묐떟?먮뒗 留덊겕?ㅼ슫 肄붾뱶釉붾줉(```json ?????ы븿?섏? 留먭퀬 ?ㅼ쭅 JSON ?먯껜留?異쒕젰?섏꽭??

異붿텧?댁빞 ???뺣낫:
- month: 愿????(?レ옄留? ?? "3")
- name: ?ν븰湲덈챸
- provider: 吏湲됱쿂
- budget: 1?몃떦 湲덉븸 諛?珥??덉궛 (?? "1?몃떦 100留뚯썝, 珥?500留뚯썝")
- count: ?좊컻 ?몄썝 (?レ옄 ?먮뒗 "5紐? ??
- criteria: ?좊컻 湲곗? (?깆쟻, 寃쎌젣 ?곹솴 ??援ъ껜?곸쑝濡?
- type: 臾몄꽌 ?댁슜??湲곕컲?쇰줈, ?숆탳?먯꽌 ?먯껜 ?좊컻?섏뿬 ?뺤젙?섎뒗 寃쎌슦??"[100%吏湲?", ?몃? ?ъ궗媛 ?꾩슂?섍굅???숈깮 媛쒖씤??吏곸젒 ?좎껌?댁빞 ?섎뒗 寃쎌슦??"[?ъ떖??媛쒖씤]" ?쇰줈 遺꾨쪟?섏꽭??
- deadline: ?묒닔 留덇컧???먮뒗 ?쒗뻾??(?뺤떇: "YYYY-MM-DD")
- promoDeadline: "[?ъ떖??媛쒖씤]"??寃쎌슦 deadline??3?????좎쭨 ("YYYY-MM-DD"). "[100%吏湲?"??寃쎌슦 鍮?臾몄옄??

?곗씠??寃利?(Validation):
臾몄꽌 ?댁뿉 1?몃떦 湲덉븸怨??좊컻 ?몄썝 ?댁슜???덈떎硫? (1?몃떦 湲덉븸 * ?좊컻 ?몄썝)??珥??덉궛怨??쇱튂?섎뒗吏 ?뺤씤?섏꽭?? ?쇱튂?섏? ?딄굅???ㅻ쪟媛 ?덈떎硫?JSON ?댁쓽 "warning" ?꾨뱶??寃쎄퀬 硫붿떆吏瑜??묒꽦?섏꽭??(?뺤긽?대㈃ "" 鍮?臾몄옄??.
?숈깮 媛쒖씤?뺣낫(?깅챸, 二쇰?踰덊샇 ??媛 臾몄꽌???ы븿?섏뼱 ?덈뜑?쇰룄 ?덈? 異쒕젰???ы븿?쒗궎吏 留덉꽭??(蹂댁븞).

?뱀닔 洹쒖튃 (遺꾨쪟 ?쒖쇅):
留뚯빟 遺꾩꽍 以묒씤 臾몄꽌媛 ?숈깮 ??곸쓽 '?ν븰湲? 怨듬Ц???꾨땲?쇰㈃ (?? "?ㅼ듅?섎궇 ?좉났援먯썝 ?쒖갹", "援먯궗 ?곗닔", "?됱젙 怨듬낫" ???ν븰湲덇낵 臾닿????댁슜??寃쎌슦), ?ㅻⅨ 紐⑤뱺 ?뺣낫瑜?異붿텧?섏? 留먭퀬 ?ㅼ쭅 `{{"filter_out": true}}` ?쇰뒗 JSON ?뚮씪誘명꽣留??⑤룆?쇰줈 諛섑솚?섏꽭??

臾몄꽌 ?댁슜:
{text}
"""
    model = genai.GenerativeModel('gemini-3.1-flash-lite') # ?ъ슜??吏移⑥뿉 ?곕씪 2.5 Flash 紐⑤뜽濡??듭씪
    response = model.generate_content(prompt)
    answer = response.text.strip()
    
    # Clean up possible markdown wrappers
    if answer.startswith("```json"):
        answer = answer[7:]
    if answer.startswith("```"):
        answer = answer[3:]
    if answer.endswith("```"):
        answer = answer[:-3]
        
    try:
        return json.loads(answer.strip())
    except json.JSONDecodeError as e:
        safe_answer = answer.encode('cp949', 'replace').decode('cp949', 'replace')
        log_message(f"Failed to decode Gemini response as JSON: {safe_answer}")
        return None

def send_to_webhook(data):
    """Send extracted data to the Google Apps Script Webhook."""
    try:
        # If Gemini returned a list of items instead of one item
        if isinstance(data, list):
            data = data[0] if len(data) > 0 else {}
            
        # Expected Payload: { "month": "?レ옄", "name": "?ν븰湲덈챸", "provider": "吏湲됱쿂", "budget": "湲덉븸", ...}
        payload = {k: v for k, v in data.items() if k != "warning"}
        response = requests.post(GOOGLE_SHEET_WEBHOOK_URL, json=payload, headers={'Content-Type': 'application/json'}, verify=False)
        response.raise_for_status()
        return True
    except Exception as e:
        log_message(f"Webhook failed: {e}")
        return False

def format_and_send_telegram(results):
    """Format the results and send a Telegram briefing."""
    if not results:
        return
        
    results.sort(key=lambda x: (x.get('deadline') or '9999-12-31'))

    body = f"?럳 [?ν븰湲?怨듦퀬 遺꾩꽍 釉뚮━??\n?덈줈 泥섎━???ν븰湲??댁슜?낅땲?? (留덇컧 ?꾨컯 ??\n\n"
    
    for res in results:
        body += f"?뱦 {res.get('name', '?ν븰湲덈챸 誘몄긽')} ({res.get('type', '')})\n"
        body += f" - 吏湲됱쿂: {res.get('provider', '')}\n"
        body += f" - ?덉궛/?몄썝: {res.get('budget', '')} / {res.get('count', '')}\n"
        body += f" - ?좊컻 湲곗?: {res.get('criteria', '')}\n"
        body += f" - 留덇컧?? {res.get('deadline', '')}\n"
        if res.get('promoDeadline'):
            body += f" - ?좑툘 ?띾낫 留덇컧?? {res.get('promoDeadline')}\n"
        if res.get('warning'):
            body += f" - ?슚 ?쒖뒪??寃쎄퀬: {res.get('warning')}\n"
        body += "\n"
        
    body += "???ν븰湲?珥앷큵 援ш? ?쒗듃 湲곕줉(?숆린?? ?꾨즺"
    
    try:
        import urllib.request
        import urllib.parse
        import ssl
        
        token = "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY"
        chat_id = "8518409134"
        
        telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({'chat_id': chat_id, 'text': body}).encode('utf-8')
        req = urllib.request.Request(telegram_url, data=data)
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        urllib.request.urlopen(req, context=ctx)
        log_message("???붾젅洹몃옩 ?ν븰湲?釉뚮━???꾩넚 ?꾨즺!")
    except Exception as e:
        log_message(f"?좑툘 ?붾젅洹몃옩 ?꾩넚 ?ㅽ뙣: {e}")

def process_scholarships():
    """Main job routine to process documents from Drive."""
    print(f"[{datetime.now()}] Starting scholarship processing job...")
    service = get_drive_service()
    if not service:
        print("Could not initialize Drive service.")
        return

    folder_id = get_target_folder_id(service, DRIVE_BASE_FOLDER_ID)
    if not folder_id:
        return

    # Find PDFs in the determined target folder
    query = f"'{folder_id}' in parents and mimeType = 'application/pdf' and trashed = false"
    # To prevent re-processing, we ideally should track processed files. Here we process them all or we could update an external database.
    # For now, let's process max 10 latest or keep track via memory/file.
    # Implementing a simple processed.txt check
    processed_files = set()
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r") as f:
            processed_files = set(f.read().splitlines())

    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    
    briefing_results = []
    seen_scholarships = set()
    
    def normalize_name(name):
        return re.sub(r'202\d|?숇뀈???ν븰???좊컻|異붿쿇|?ν븰湲?\s+', '', name)
    
    for item in items:
        file_id = item['id']
        file_name = item['name']
        if file_id in processed_files:
            continue
            
        print(f"Processing {file_name}...")
        local_path = download_pdf(service, file_id, file_name)
        text = extract_text_from_pdf(local_path)
        
        parsed_data = analyze_document_with_gemini(text)
        if parsed_data:
            if isinstance(parsed_data, list):
                parsed_data = parsed_data[0] if len(parsed_data) > 0 else {}
                
            if parsed_data.get("filter_out"):
                print(f"Skipping {file_name} as it is not related to a scholarship.")
                processed_files.add(file_id)
                continue
                
            raw_name = parsed_data.get("name", "")
            norm_name = normalize_name(raw_name) if raw_name else None
            if norm_name and norm_name in seen_scholarships:
                print(f"Skipping duplicate document for scholarship: {raw_name}")
                processed_files.add(file_id)
                continue
                
            if norm_name:
                seen_scholarships.add(norm_name)
                
            success = send_to_webhook(parsed_data)
            if success:
                briefing_results.append(parsed_data)
                processed_files.add(file_id)
                
        # Clean up temp file
        if os.path.exists(local_path):
            os.remove(local_path)
            
    if briefing_results:
        format_and_send_telegram(briefing_results)
        # Update processed files list
        with open(PROCESSED_FILE, "w") as f:
            for fid in processed_files:
                f.write(f"{fid}\n")
    else:
        log_message("No new documents processed.")

def main():
    print("Scholarship Bot is starting...")
    # Schedule setup: Monday, Wednesday, Friday at 08:30 AM
    schedule.every().monday.at("08:30").do(process_scholarships)
    schedule.every().wednesday.at("08:30").do(process_scholarships)
    schedule.every().friday.at("08:30").do(process_scholarships)
    
    print("Schedule set! Waiting for the next run...")
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # If a command line flag like --test is passed, run immediately once.
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        process_scholarships()
    else:
        main()
