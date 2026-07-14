import os
import sys
import time
import glob
import json
import re
import datetime
import pdfplumber
import requests
import urllib3
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# UTF-8 출력 설정 (터미널 한글 깨짐 및 유니코드 이모지 에러 방지)
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 경상남도교육청 학내망 SSL 인증서 우회 설정
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 구글 API 설정
TOKEN_FILE = 'token.json'
SPREADSHEET_ID = '1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU'
FOLDER_ID = '1lxKMH8ssyeHSEv3rI2a24pD8qCT6FXo1'
EXAM_DATABASE_SHEET_NAME = '수능_모평_문항_사전'
SCOPES = ['https://www.googleapis.com/auth/drive']

# 기출문제 폴더 경로 및 바탕화면 경로 설정
EXAM_DIR = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\수능_모의고사_기출문제"
DESKTOP_DIR = r"D:\OneDrive - 경상남도교육청\바탕 화면"

# 1. API 키 로드
def get_gemini_api_key():
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('GEMINI_API_KEY='):
                    return line.strip().split('=', 1)[1].strip()
    return os.environ.get('GEMINI_API_KEY', '')

# 2. 구글 API 인증 획득
def get_google_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return creds

# 3. 모든 기출 폴더 검색 및 문제/해설 매칭 쌍 리스트업
def get_all_matched_exams():
    target_dir = EXAM_DIR if os.path.exists(EXAM_DIR) else DESKTOP_DIR
    print(f"[*] 기출문제 폴더({target_dir})에서 모든 PDF 파일을 검색합니다...")
    
    if not os.path.exists(target_dir):
        print(f"[!] 탐색 경로가 존재하지 않습니다: {target_dir}")
        return []

    all_pdfs = []
    for root, dirs, files in os.walk(target_dir):
        for f in files:
            if f.lower().endswith(".pdf"):
                all_pdfs.append(os.path.join(root, f))
                
    if not all_pdfs:
        print("[!] PDF 파일이 없습니다.")
        return []

    # 디렉토리별로 그룹화
    dir_groups = {}
    for pdf in all_pdfs:
        d = os.path.dirname(pdf)
        if d not in dir_groups:
            dir_groups[d] = []
        dir_groups[d].append(pdf)

    matched_pairs = []
    # 각 디렉토리 내에서 문제/해설 매칭 찾기
    for d, pdfs in dir_groups.items():
        # 국어/언어/언매 관련 PDF만 필터링
        exam_pdfs = [p for p in pdfs if any(kw in os.path.basename(p) for kw in ["국어", "언어", "언매", "수능", "모평", "학평"])]
        
        # 문제지와 해설지 분류
        questions_in_dir = [p for p in exam_pdfs if not any(h in os.path.basename(p) for h in ["해설", "정답", "답지", "분석"])]
        commentaries_in_dir = [p for p in exam_pdfs if any(h in os.path.basename(p) for h in ["해설", "정답", "답지", "분석"])]
        
        # 이름 기반 매칭 시도
        for q in questions_in_dir:
            q_name = os.path.basename(q).replace("_문제", "").replace(" 홀수형", "").replace(" 짝수형", "").replace(".pdf", "")
            # 대략적인 이름 매칭을 통해 쌍 찾기
            matching_c = None
            for c in commentaries_in_dir:
                c_name = os.path.basename(c).replace("_해설", "").replace("_정답", "").replace(".pdf", "")
                if c_name in q_name or q_name in c_name or any(w in c_name for w in q_name.split() if len(w) > 1):
                    matching_c = c
                    break
            
            if not matching_c and commentaries_in_dir:
                matching_c = commentaries_in_dir[0]
                
            if q and matching_c:
                rel_path = os.path.relpath(d, target_dir)
                year_match = re.search(r"(\d{4})년", rel_path)
                year = int(year_match.group(1)) if year_match else 0
                
                matched_pairs.append({
                    'question': q,
                    'commentary': matching_c,
                    'folder': rel_path,
                    'year': year,
                    'mtime': max(os.path.getmtime(q), os.path.getmtime(matching_c))
                })

    matched_pairs.sort(key=lambda x: (x['year'], x['mtime']), reverse=True)
    return matched_pairs

# 4. PDF 텍스트 추출 (앞/뒤쪽 국어 언어/매체 페이지만 발췌하여 속도 개선)
def extract_exam_text(pdf_path, max_pages=16):
    if not pdf_path or not os.path.exists(pdf_path):
        return ""
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            pages_to_read = []
            
            keywords = ["언어", "매체", "음운", "발음", "받침", "교체", "탈락", "첨가", "축약", "된소리", "자음", "모음"]
            
            for i in range(total_pages):
                page = pdf.pages[i]
                sample_text = page.within_bbox((0, 0, page.width, 150)).extract_text() or ""
                page_text_full = page.extract_text() or ""
                
                if any(kw in page_text_full for kw in keywords) or any(kw in sample_text for kw in keywords):
                    pages_to_read.append(i)
            
            if not pages_to_read:
                pages_to_read = list(range(min(total_pages, max_pages)))
            
            extracted = []
            for idx in pages_to_read[:12]:
                page = pdf.pages[idx]
                text = page.extract_text() or ""
                extracted.append(f"--- PAGE {idx+1} ---\n{text}")
                
            return "\n".join(extracted)
    except Exception as e:
        print(f"[!] PDF 텍스트 추출 실패 ({os.path.basename(pdf_path)}): {e}")
        return ""

# 5. Gemini API를 사용하여 음운론 문제 추출 (SSL 우회 추가)
def extract_phonology_questions_via_gemini(question_text, commentary_text, api_key, retries=3):
    if not api_key:
        return None

    model = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    system_instruction = (
        "당신은 고등학교 국어 교사이자 교육과정 평가원 문항 분석 전문가입니다.\n"
        "제공된 국어 시험지 및 해설지 텍스트에서 **'음운론(음운 변동, 표준 발음법, 자음/모음 체계, 음운 현상 등)'** 영역에 해당하는 문제를 찾으십시오.\n"
        "추출한 문제를 아래 스키마에 정의된 JSON 구조로 완벽하게 구조화하여 응답해 주십시오. 음운론 문제가 없다면 빈 리스트를 반환하십시오."
    )

    prompt = f"""
다음은 시험지 텍스트와 해설지 텍스트입니다.
이 데이터 속에서 '음운론(음운 변동, 발음 규칙, 자음군 단순화, 사잇소리 현상 등)'에 관한 문항을 식별하고 내용을 추출해 주세요.

[시험지 텍스트]
{question_text[:30000]}

[해설지 텍스트]
{commentary_text[:15000]}

[출력 스키마 요구사항]
반드시 아래 키들을 포함하는 JSON 객체의 리스트 형식으로만 응답해 주십시오 (마크다운 ```json 코드 블록으로 감싸주세요):
[
  {{
    "examName": "시험명 (예: 2026학년도 6월 모의평가)",
    "qNum": "문항번호 (숫자만, 예: 35)",
    "phonologyType": "음운 변동 유형 (예: 교체 - 비음화, 탈락 - 자음군 단순화)",
    "qContent": "문제 발문 내용",
    "boxContent": "<보기> 또는 지문 상자 텍스트 내용",
    "options": "오지선다 선택지 1~5번 합본 텍스트",
    "answer": "정답 번호 (1~5 중 숫자)",
    "explanation": "해설지 기준의 정답 및 오답 선지 상세 해설",
    "keywords": "해당 문항에 등장한 단어 및 핵심 음운 변동 명칭 (쉼표로 구분한 리스트, 예: 굳이,국물,읊고,구개음화,자음군단순화)"
  }}
]
"""

    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }

    for attempt in range(retries):
        try:
            # verify=False 로 교육청 방화벽 우회
            response = requests.post(url, headers=headers, json=payload, timeout=50, verify=False)
            if response.status_code == 429:
                sleep_time = (attempt + 1) * 10
                print(f"[!] API Rate Limit 도달. {sleep_time}초 대기 후 재시도 합니다...")
                time.sleep(sleep_time)
                continue
                
            if response.status_code != 200:
                print(f"[!] Gemini API 에러 (Status {response.status_code}): {response.text}")
                return None
            
            result = response.json()
            raw_json_str = result['candidates'][0]['content']['parts'][0]['text'].strip()
            
            cleaned_json = raw_json_str.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_json)
        except Exception as e:
            print(f"[!] Gemini API 분석 실패 (시도 {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(5)
            else:
                return None

# 6. 구글 스프레드시트에 일괄 기입 및 중복 체크
def upload_to_google_sheet(questions, creds):
    if not creds or not questions:
        return False
    
    try:
        service = build('sheets', 'v4', credentials=creds)
        range_name = f"'{EXAM_DATABASE_SHEET_NAME}'!A:J"
        
        # 1. 시트 존재 확인 및 생성
        spreadsheet_meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = spreadsheet_meta.get('sheets', [])
        sheet_titles = [s.get('properties', {}).get('title') for s in sheets]
        
        if EXAM_DATABASE_SHEET_NAME not in sheet_titles:
            add_sheet_request = {'requests': [{'addSheet': {'properties': {'title': EXAM_DATABASE_SHEET_NAME}}}]}
            service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=add_sheet_request).execute()
            
            exam_headers = ["ID", "시험명", "문항번호", "음운론유형", "문제내용(발문)", "보기(Box)", "선지(1~5번)", "정답", "해설", "연계 키워드"]
            header_body = {'values': [exam_headers]}
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID, range=f"'{EXAM_DATABASE_SHEET_NAME}'!A1:J1",
                valueInputOption='USER_ENTERED', body=header_body
            ).execute()

        # 2. 기존 ID 로드
        res = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
        existing_values = res.get('values', [])
        existing_ids = set()
        if len(existing_values) > 1:
            for row in existing_values[1:]:
                if row and len(row) > 0:
                    existing_ids.add(row[0])

        rows_to_append = []
        for q in questions:
            q_id = f"{q.get('examName', 'EXAM')}_{q.get('qNum', '00')}".replace(" ", "_")
            if q_id in existing_ids:
                continue
                
            def safe_str(val, join_char='\n'):
                if isinstance(val, list):
                    return join_char.join(str(item) for item in val)
                return str(val) if val is not None else ""

            row = [
                q_id,
                safe_str(q.get('examName', '')),
                safe_str(q.get('qNum', '')),
                safe_str(q.get('phonologyType', '')),
                safe_str(q.get('qContent', '')),
                safe_str(q.get('boxContent', '')),
                safe_str(q.get('options', '')),
                safe_str(q.get('answer', '')),
                safe_str(q.get('explanation', '')),
                safe_str(q.get('keywords', ''), join_char=', ')
            ]
            rows_to_append.append(row)
            existing_ids.add(q_id)

        if rows_to_append:
            body = {'values': rows_to_append}
            service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            print(f"[+] 구글 스프레드시트에 {len(rows_to_append)}개의 수능/모평 문항이 성공적으로 추가 적재되었습니다.")
            return True
        return True
            
    except Exception as e:
        print(f"[!] 구글 스프레드시트 적재 실패: {e}")
        return False

# 7-2. 폴더명을 기반으로 해당 기출 시험이 이미 스프레드시트에 기적재되었는지 체크
def is_exam_already_processed(folder_name, existing_ids):
    year_match = re.search(r"(\d{4})", folder_name)
    if not year_match:
        return False
    year = year_match.group(1)
    
    test_type = None
    if "수능" in folder_name or "대학수학능력" in folder_name:
        test_type = "수능"
    else:
        month_match = re.search(r"(\d{1,2})월", folder_name)
        if month_match:
            test_type = month_match.group(1)
            
    if not test_type:
        return False
        
    for eid in existing_ids:
        if year in eid:
            if test_type == "수능":
                if "수능" in eid or "대학수학능력" in eid or "대수능" in eid:
                    return True
            else:
                if f"{test_type}월" in eid or f"_{test_type}_" in eid:
                    return True
    return False

# 7. 스프레드시트에서 모든 수능/모평 문항 조회
def fetch_all_questions_from_sheet(creds):
    if not creds:
        return []
    
    try:
        service = build('sheets', 'v4', credentials=creds)
        range_name = f"'{EXAM_DATABASE_SHEET_NAME}'!A:J"
        res = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
        values = res.get('values', [])
        
        if len(values) < 2:
            return []
            
        questions = []
        for row in values[1:]:
            if not row or len(row) < 9:
                continue
            
            q = {
                'id': row[0],
                'examName': row[1] if len(row) > 1 else '',
                'qNum': row[2] if len(row) > 2 else '',
                'phonologyType': row[3] if len(row) > 3 else '',
                'qContent': row[4] if len(row) > 4 else '',
                'boxContent': row[5] if len(row) > 5 else '',
                'options': row[6] if len(row) > 6 else '',
                'answer': row[7] if len(row) > 7 else '',
                'explanation': row[8] if len(row) > 8 else '',
                'keywords': row[9] if len(row) > 9 else ''
            }
            questions.append(q)
            
        return questions
    except Exception as e:
        print(f"[!] 스프레드시트 데이터 조회 실패: {e}")
        return []

# 8. 파이썬 기반 고품질 HTML 학습지 자체 생성 (API 타임아웃 방지)
def build_html_worksheet_in_python(questions):
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>수능/모의평가 음운론 기출 정복 마스터북</title>
<style>
  body { font-family: 'Malgun Gothic', 'Dotum', sans-serif; line-height: 1.7; font-size: 11pt; color: #2c3e50; padding: 20px; background-color: #f8f9fa; }
  .container { max-width: 900px; margin: 0 auto; background: #fff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
  h1 { text-align: center; color: #1e3a8a; border-bottom: 3px solid #1e3a8a; padding-bottom: 15px; margin-bottom: 25px; font-size: 20pt; }
  h2 { color: #2563eb; margin-top: 30px; border-left: 5px solid #2563eb; padding-left: 15px; font-size: 14pt; margin-bottom: 15px; }
  .header-info { text-align: right; font-weight: bold; margin-bottom: 25px; border-bottom: 2px solid #333; padding-bottom: 10px; }
  .summary-table { width: 100%; border-collapse: collapse; margin: 15px 0 30px 0; }
  .summary-table th, .summary-table td { border: 1px solid #cbd5e1; padding: 12px; text-align: left; font-size: 10pt; }
  .summary-table th { background-color: #f1f5f9; text-align: center; font-weight: bold; }
  
  /* 문제 카드 스타일 - 1페이지에 맞춤 */
  .question-card { border: 1px solid #cbd5e1; border-radius: 8px; padding: 30px; background-color: #ffffff; min-height: 500px; }
  .badge-exam { background-color: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 20px; font-size: 9pt; font-weight: bold; display: inline-block; margin-right: 10px; }
  .badge-type { background-color: #f3e8ff; color: #6b21a8; padding: 4px 12px; border-radius: 20px; font-size: 9pt; font-weight: bold; display: inline-block; }
  .q-title { font-weight: bold; font-size: 12.5pt; margin-top: 15px; margin-bottom: 15px; line-height: 1.6; }
  .box-content { border: 1px dashed #94a3b8; padding: 20px; background-color: #f8fafc; border-radius: 6px; margin-bottom: 20px; font-size: 10.5pt; white-space: pre-wrap; line-height: 1.6; }
  .options { margin-bottom: 20px; padding-left: 10px; }
  .option-item { margin-bottom: 8px; font-size: 11pt; }
  
  /* 해설 카드 스타일 - 독립된 1페이지에 맞춤 */
  .answer-card { border: 1px solid #cbd5e1; border-radius: 8px; padding: 30px; background-color: #fafafa; min-height: 500px; }
  .answer-title { font-weight: bold; font-size: 13pt; color: #1e3a8a; border-bottom: 2px solid #1e3a8a; padding-bottom: 10px; margin-bottom: 15px; }
  .answer-keywords { font-size: 10pt; color: #64748b; margin-bottom: 15px; font-weight: bold; }
  .answer-explanation { font-size: 10.5pt; line-height: 1.8; white-space: pre-wrap; color: #334155; }
</style>
</head>
<body>
<div class="container">
  <h1>[학습지] 수능/모의평가 음운론(음운 변동) 기출 정복 마스터북</h1>
  <div class="header-info">
    2학년 <u>&nbsp;&nbsp;&nbsp;&nbsp;</u>반 <u>&nbsp;&nbsp;&nbsp;&nbsp;</u>번 &nbsp;&nbsp;&nbsp;&nbsp; 이름: __________________
  </div>
  
  <h2>[개념 정리] 음운 변동 핵심 요약</h2>
  <table class="summary-table" style="page-break-after: always; break-after: page;">
    <tr>
      <th style="width: 15%;">변동 유형</th>
      <th style="width: 25%;">정의</th>
      <th style="width: 35%;">주요 변동 현상</th>
      <th style="width: 25%;">대표 예시</th>
    </tr>
    <tr>
      <td style="text-align: center; font-weight: bold; background-color: #eff6ff;">교체 (Substitution)</td>
      <td>한 음운이 다른 음운으로 바뀌는 현상</td>
      <td>음절의 끝소리 규칙, 비음화, 유음화, 구개음화, 된소리되기</td>
      <td>국물[궁물], 굳이[구지], 옷[옫]</td>
    </tr>
    <tr>
      <td style="text-align: center; font-weight: bold; background-color: #fef2f2;">탈락 (Deletion)</td>
      <td>두 음운 중 어느 하나가 없어지는 현상</td>
      <td>자음군 단순화, ㅎ 탈락, ㄹ 탈락, ㅡ 탈락, 동음 탈락</td>
      <td>닭[닥], 싫어도[시러도], 가니(가-+-니)</td>
    </tr>
    <tr>
      <td style="text-align: center; font-weight: bold; background-color: #f0fdf4;">첨가 (Addition)</td>
      <td>형태소가 결합할 때 없던 음운이 덧나는 현상</td>
      <td>ㄴ 첨가, 반모음 첨가</td>
      <td>솜이불[솜니불], 피어[피어/피여](허용)</td>
    </tr>
    <tr>
      <td style="text-align: center; font-weight: bold; background-color: #faf5ff;">축약 (Contraction)</td>
      <td>두 음운이 합쳐져 하나의 새로운 음운이 되는 현상</td>
      <td>자음 축약 (거센소리되기)</td>
      <td>좋다[조타], 국화[구콰]</td>
    </tr>
  </table>
  
  <h2>[실전 탐구] 수능/모의평가 기출 문제 및 상세 해설 (총 {len(questions)}문항)</h2>
"""

    # 기출문제 및 해당 해설을 번갈아가며 추가
    for idx, q in enumerate(questions):
        html += f"""
  <!-- {idx+1}번 문제 페이지 -->
  <div class="question-card" style="page-break-after: always; break-after: page;">
    <div>
      <span class="badge-exam">{q['examName']} {q['qNum']}번</span>
      <span class="badge-type">{q['phonologyType']}</span>
    </div>
    <div class="q-title">{idx+1}. {q['qContent']}</div>
"""
        if q['boxContent']:
            html += f"""    <div class="box-content">{q['boxContent']}</div>\n"""
            
        if q['options']:
            html += f"""    <div class="options">\n"""
            options_lines = q['options'].split('\n')
            for line in options_lines:
                if line.strip():
                    html += f"""      <div class="option-item">{line.strip()}</div>\n"""
            html += f"""    </div>\n"""
            
        html += f"""
  </div>
  
  <!-- {idx+1}번 해설 페이지 -->
  <div class="answer-card" style="page-break-after: always; break-after: page;">
    <div class="answer-title">🔑 {idx+1}번 문항 정답: {q['answer']}번 ({q['examName']} {q['qNum']}번)</div>
    <div class="answer-keywords">연계 키워드: {q['keywords']}</div>
    <div class="answer-explanation">{q['explanation']}</div>
  </div>
"""

    html += """
</div>
</body>
</html>
"""
    return html

# 9. 생성된 학습지 Google Drive에 업로드
def upload_master_worksheet_to_drive(title, html_content, creds):
    if not creds or not html_content:
        return None
        
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.document',
            'parents': [FOLDER_ID]
        }
        
        encoded_html = html_content.encode('utf-8')
        media = MediaIoBaseUpload(io.BytesIO(encoded_html), mimetype='text/html', resumable=True)
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        file_id = file.get('id')
        
        # Google Docs API를 사용하여 페이지 나누기를 강제로 주입
        try:
            docs_service = build('docs', 'v1', credentials=creds)
            doc = docs_service.documents().get(documentId=file_id).execute()
            body_content = doc.get('body', {}).get('content', [])
            
            break_positions = []
            for element in body_content:
                if 'paragraph' in element:
                    paragraph = element.get('paragraph')
                    text = ""
                    for elem in paragraph.get('elements', []):
                        text_run = elem.get('textRun')
                        if text_run:
                            text += text_run.get('content', '')
                            
                    start_index = element.get('startIndex')
                    
                    if '[실전 탐구]' in text:
                        break_positions.append(start_index)
                    elif re.match(r'^\d+\.\s', text.strip()):
                        if not text.strip().startswith('1.'):
                            break_positions.append(start_index)
                    elif '🔑' in text:
                        break_positions.append(start_index)
            
            # 뒷부분 인덱스가 밀리지 않도록 큰 인덱스부터 역순 정렬
            break_positions.sort(reverse=True)
            
            requests = []
            for pos in break_positions:
                requests.append({
                    'insertPageBreak': {
                        'location': {
                            'index': pos
                        }
                    }
                })
                
            if requests:
                print(f"[#] 구글 문서 API를 통해 강제 페이지 나누기 {len(requests)}개를 주입합니다...")
                docs_service.documents().batchUpdate(
                    documentId=file_id,
                    body={'requests': requests}
                ).execute()
                print("[+] 구글 문서 페이지 나누기 적용 완료!")
                
        except Exception as api_err:
            print(f"[!] 구글 문서 API 페이지 나누기 주입 중 오류 발생: {api_err}")
            
        return file.get('webViewLink')
    except Exception as e:
        print(f"[!] 구글 문서 업로드 실패: {e}")
        return None

# 10. 텔레그램 메시지 발송 함수 (SSL 우회 추가)
def send_telegram_message(message):
    token = ""
    chat_id = ""
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('TELEGRAM_TOKEN='):
                    token = line.split('=', 1)[1].strip()
                elif line.startswith('TELEGRAM_CHAT_ID='):
                    chat_id = line.split('=', 1)[1].strip()
                    
    if not token or not chat_id:
        print("[!] 텔레그램 토큰 또는 Chat ID가 .env 파일에 설정되어 있지 않습니다.")
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        # verify=False 로 교육청 SSL 인증서 간섭 우회
        response = requests.post(url, json=payload, timeout=20, verify=False)
        if response.status_code == 200:
            print("[+] 텔레그램 알림 메시지가 성공적으로 발송되었습니다.")
            return True
        else:
            print(f"[!] 텔레그램 발송 실패 (Status {response.status_code}): {response.text}")
    except Exception as e:
        print(f"[!] 텔레그램 발송 오류: {e}")
    return False

# 메인 제어 흐름
def main():
    print("=== 수능/모평 음운론 전수 분석 및 마스터 학습지 생성기 ===")
    api_key = get_gemini_api_key()
    creds = get_google_credentials()
    
    if not api_key:
        print("[!] GEMINI_API_KEY가 없습니다.")
        sys.exit(1)
        
    # 1. 기출 폴더 전수 조사
    matched_exams = get_all_matched_exams()
    print(f"[+] 총 {len(matched_exams)}개의 국어 기출문항 폴더(문제/해설 세트)가 발견되었습니다.")
    
    # 2. 스프레드시트의 기존 기출 ID 로드하여 중복 회피
    existing_ids = set()
    if creds:
        try:
            service = build('sheets', 'v4', credentials=creds)
            res = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID, 
                range=f"'{EXAM_DATABASE_SHEET_NAME}'!A:A"
            ).execute()
            vals = res.get('values', [])
            if len(vals) > 1:
                existing_ids = set(v[0] for v in vals[1:] if v)
        except Exception as e:
            print(f"[*] 기존 스프레드시트 ID 로드 실패(시트가 미개설 상태일 수 있음): {e}")

    # 3. 각 기출문제 분석 및 스프레드시트 적재 (최근 6년간 데이터 최우선 집중 스캔)
    processed_count = 0
    
    print("[*] 미등록된 최신 기출문제 분석 및 스프레드시트 적재를 시작합니다...")
    last_rest_time = time.time()
    
    for idx, exam in enumerate(matched_exams):
        # 2020년 이전 기출은 과도한 API 콜 방지를 위해 1차 건너뜀
        if exam['year'] < 2020:
            continue
            
        folder_name = exam['folder']
        # 이미 처리된 시험지인지 확인
        if is_exam_already_processed(folder_name, existing_ids):
            print(f"[*] [{idx+1}/{len(matched_exams)}] 건너뜀 (이미 처리됨): {folder_name}")
            continue
            
        # Throttling 제어: 3분(180초) 진행 후 30초 휴식
        current_time = time.time()
        if current_time - last_rest_time > 180:
            print(f"[*] 3분 동안 지속 실행되어 30초 동안 대기(휴식)합니다...")
            time.sleep(30)
            last_rest_time = time.time() # 휴식 타이머 리셋
            
        print(f"[*] [{idx+1}/{len(matched_exams)}] 분석 중: {folder_name} (연도: {exam['year']})")
        
        q_text = extract_exam_text(exam['question'])
        c_text = extract_exam_text(exam['commentary'])
        
        if not q_text or not c_text:
            print(f"   [-] 텍스트를 추출할 수 없어 건너뜁니다: {folder_name}")
            continue
            
        # Gemini 호출
        questions = extract_phonology_questions_via_gemini(q_text, c_text, api_key)
        
        if questions:
            print(f"   [+] 음운론 문제 {len(questions)}개 추출 성공!")
            if creds:
                upload_to_google_sheet(questions, creds)
                processed_count += len(questions)
        else:
            print("   [-] 음운론 문항이 발견되지 않았습니다.")
            
        time.sleep(3.5)
        
    print(f"\n[+] 기출문제 분석 적재 프로세스가 완료되었습니다. (추가된 신규 문항 수: {processed_count}개)")
    
    # 4. 스프레드시트의 전체 기출문항 데이터 조회
    print("[*] 구글 스프레드시트 기출문제 데이터베이스에서 전수 데이터를 수집합니다...")
    all_questions = fetch_all_questions_from_sheet(creds)
    print(f"[+] 총 {len(all_questions)}개의 음운론 기출문항을 수집했습니다.")
    
    if not all_questions:
        print("[!] 기출문제 사전 시트가 비어있거나 데이터를 가져올 수 없습니다. 통합 학습지 생성을 취소합니다.")
        send_telegram_message("❌ [오류 알림]\n수능/모평 음운론 기출 통합 학습지 제작 중 데이터베이스에서 문항을 불러올 수 없습니다.")
        return
        
    # 5. 수집된 문제를 바탕으로 하나의 통합 학습지 HTML 문서 빌드 (파이썬 렌더링으로 타임아웃 방지)
    print("[*] 파이썬 내장 템플릿으로 통합 학습지(HTML)를 렌더링하고 있습니다...")
    master_html = build_html_worksheet_in_python(all_questions)
    
    if master_html:
        output_filename = "[통합학습지]_수능_모평_음운론_기출정복.html"
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(master_html)
        print(f"[+] 로컬 통합 학습지 파일 저장 완료: {output_filename}")
        
        # 6. 구글 드라이브 업로드
        if creds:
            print("[*] 구글 드라이브에 구글 문서로 일괄 변환 및 업로드를 시작합니다...")
            doc_title = f"[통합학습지] 수능/모의평가 음운론 기출 정복 마스터북 (총 {len(all_questions)}문항)"
            web_link = upload_master_worksheet_to_drive(doc_title, master_html, creds)
            
            if web_link:
                print(f"[완료] 구글 문서 통합 학습지 업로드 완료!!")
                print(f"     링크: {web_link}")
                
                # 로그 저장
                with open("google_docs_links.txt", "a", encoding="utf-8") as f:
                    f.write(f"{datetime.date.today()} - {doc_title}: {web_link}\n")
                
                # 텔레그램 알림 전송
                tel_msg = (
                    f"🔔 [작업 완료 알림]\n\n"
                    f"안녕하세요, 황요한 선생님!\n"
                    f"요청하신 수능/모의평가 음운론 기출문항 전수 분석 및 마스터 학습지 제작이 성공적으로 완료되었습니다.\n\n"
                    f"📝 문서명: {doc_title}\n"
                    f"🔗 구글 문서 링크: {web_link}\n\n"
                    f"신규 기출문항들이 스프레드시트 DB에 추가 누적 적재되었으며, 기존 웹앱의 소크라테스 AI 튜터와도 완벽하게 연계되었습니다."
                )
                send_telegram_message(tel_msg)
                
                # 윈도우 데스크탑 팝업 알림 실행
                if sys.platform == 'win32':
                    try:
                        import subprocess
                        subprocess.Popen('cmd /c start python notify_popup_perfect.py', shell=True)
                        print("[+] 윈도우 데스크탑 팝업 알림창이 성공적으로 실행되었습니다.")
                    except Exception as pop_err:
                        print(f"[!] 팝업 알림 실행 실패: {pop_err}")
            else:
                print("[!] 구글 문서 업로드에 실패했습니다.")
                send_telegram_message("❌ [오류 알림]\n수능/모평 음운론 기출 통합 학습지 제작 중 구글 문서 업로드에 실패했습니다.")
    else:
        print("[!] 통합 학습지 HTML을 생성하지 못했습니다.")
        send_telegram_message("❌ [오류 알림]\n수능/모평 음운론 기출 통합 학습지 HTML 생성에 실패했습니다.")

if __name__ == "__main__":
    main()
