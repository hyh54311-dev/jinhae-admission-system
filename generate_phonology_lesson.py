import os
import sys
import glob
import json
import re
import datetime
import pdfplumber
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# 구글 API 설정
TOKEN_FILE = 'token.json'
SPREADSHEET_ID = '1P3EuWeLlxjmozKGPpow279Qyc_moSGt4QAzx68SqJBU'
FOLDER_ID = '1lxKMH8ssyeHSEv3rI2a24pD8qCT6FXo1'
EXAM_DATABASE_SHEET_NAME = '수능_모평_문항_사전'
SCOPES = ['https://www.googleapis.com/auth/drive']

# 기출문제 및 바탕화면 절대 경로 설정
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

# 3. 기출문제 폴더에서 최근 수능/모의평가 PDF 검색 (하위 폴더 재귀 스캔)
def detect_desktop_pdfs():
    target_dir = EXAM_DIR if os.path.exists(EXAM_DIR) else DESKTOP_DIR
    print(f"[*] 기출문제 폴더({target_dir})에서 최신 PDF 파일을 검색합니다...")
    if not os.path.exists(target_dir):
        print(f"[!] 탐색 경로가 존재하지 않습니다: {target_dir}")
        return None, None

    # 모든 하위 폴더에서 PDF 파일 목록 찾기
    all_pdfs = []
    for root, dirs, files in os.walk(target_dir):
        for f in files:
            if f.lower().endswith(".pdf"):
                all_pdfs.append(os.path.join(root, f))
                
    if not all_pdfs:
        print("[!] 기출문제 폴더에 PDF 파일이 없습니다.")
        return None, None

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
        question_pdf = None
        commentary_pdf = None
        
        # 기출문제 관련 PDF만 필터링
        exam_pdfs = [p for p in pdfs if any(kw in os.path.basename(p) for kw in ["수능", "모의평가", "모평", "학력평가", "학평", "국어", "언어"])]
        
        for p in exam_pdfs:
            fname = os.path.basename(p)
            is_commentary = any(h in fname for h in ["해설", "정답", "답지", "분석"])
            if is_commentary:
                if not commentary_pdf:
                    commentary_pdf = p
            else:
                if not question_pdf:
                    question_pdf = p
                    
        if question_pdf and commentary_pdf:
            # 매칭 완료, 두 파일의 가장 최신 수정 시간 기준 저장
            mtime = max(os.path.getmtime(question_pdf), os.path.getmtime(commentary_pdf))
            matched_pairs.append({
                'question': question_pdf,
                'commentary': commentary_pdf,
                'mtime': mtime,
                'folder': os.path.relpath(d, target_dir)
            })

    if not matched_pairs:
        print("[!] 문제지와 해설지가 쌍으로 존재하는 기출문제를 찾지 못했습니다.")
        return None, None

    # 가장 최근에 다운로드/수정된 매칭 쌍 찾기
    matched_pairs.sort(key=lambda x: x['mtime'], reverse=True)
    latest_pair = matched_pairs[0]
    
    print(f"[+] 발견된 최신 기출 세트 폴더: {latest_pair['folder']}")
    print(f"   - 문제지: {os.path.basename(latest_pair['question'])}")
    print(f"   - 해설지: {os.path.basename(latest_pair['commentary'])}")
    return latest_pair['question'], latest_pair['commentary']

# 4. PDF 텍스트 추출 (pdfplumber 활용)
def extract_text_from_pdf(pdf_path, max_pages=16):
    if not pdf_path or not os.path.exists(pdf_path):
        return ""
    
    print(f"[*] PDF 텍스트 추출 중: {os.path.basename(pdf_path)}")
    extracted_text = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            pages_to_read = min(total_pages, max_pages)
            
            # 국어 시험지는 보통 8페이지 또는 16페이지. 문법은 보통 뒤쪽(언매 선택의 경우 11-12p) 또는 앞쪽(11-15번)에 위치
            # 키워드가 들어있는 페이지만 우선 필터링하거나 전체 페이지를 순차적으로 추출
            for i in range(pages_to_read):
                page = pdf.pages[i]
                text = page.extract_text() or ""
                extracted_text.append(f"--- PAGE {i+1} ---\n{text}")
                
        return "\n".join(extracted_text)
    except Exception as e:
        print(f"[!] PDF 텍스트 추출 오류: {e}")
        return ""

# 5. Gemini API를 사용하여 음운론 문제 추출 및 정제
def extract_phonology_questions_via_gemini(question_text, commentary_text, api_key):
    if not api_key:
        print("[!] Gemini API 키가 제공되지 않았습니다.")
        return None

    model = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    system_instruction = (
        "당신은 고등학교 국어 교사이자 교육과정 평가원 문항 분석 전문가입니다.\n"
        "제공된 국어 시험지 및 해설지 텍스트에서 **'음운론(음운 변동, 표준 발음법, 자음/모음 체계 등)'** 영역에 해당하는 문제를 찾으십시오.\n"
        "추출한 문제를 아래 스키마에 정의된 JSON 구조로 완벽하게 구조화하여 응답해 주십시오. 음운론 문제가 없다면 빈 리스트를 반환하십시오."
    )

    prompt = f"""
다음은 최근 모의평가/수능 시험지의 텍스트와 해설지의 텍스트입니다.
이 데이터 속에서 '음운론(음운 변동, 발음 규칙, 자음군 단순화, 사잇소리 현상 등)'에 관한 문항을 식별하고 내용을 추출해 주세요.

[시험지 텍스트]
{question_text[:35000]}

[해설지 텍스트]
{commentary_text[:20000]}

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

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=45)
        if response.status_code != 200:
            print(f"[!] Gemini API 에러: Status Code {response.status_code}\n{response.text}")
            return None
        
        result = response.json()
        raw_json_str = result['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # JSON 파싱
        cleaned_json = raw_json_str.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_json)
    except Exception as e:
        print(f"[!] Gemini API 분석 실패: {e}")
        return None

# 6. 구글 스프레드시트에 기출 데이터 추가
def upload_to_google_sheet(questions, creds):
    if not creds or not questions:
        return False
    
    try:
        service = build('sheets', 'v4', credentials=creds)
        
        # 1. 시트 존재 여부 확인 및 자동 생성
        spreadsheet_meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = spreadsheet_meta.get('sheets', [])
        sheet_titles = [s.get('properties', {}).get('title') for s in sheets]
        
        if EXAM_DATABASE_SHEET_NAME not in sheet_titles:
            print(f"[*] '{EXAM_DATABASE_SHEET_NAME}' 시트가 존재하지 않아 새로 생성합니다...")
            add_sheet_request = {
                'requests': [
                    {
                        'addSheet': {
                            'properties': {
                                'title': EXAM_DATABASE_SHEET_NAME
                            }
                        }
                    }
                ]
            }
            service.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=add_sheet_request
            ).execute()
            
            # 헤더 기입
            exam_headers = ["ID", "시험명", "문항번호", "음운론유형", "문제내용(발문)", "보기(Box)", "선지(1~5번)", "정답", "해설", "연계 키워드"]
            header_body = {'values': [exam_headers]}
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"'{EXAM_DATABASE_SHEET_NAME}'!A1:J1",
                valueInputOption='USER_ENTERED',
                body=header_body
            ).execute()
            print(f"[+] '{EXAM_DATABASE_SHEET_NAME}' 시트 및 헤더 초기화 완료.")

        range_name = f"'{EXAM_DATABASE_SHEET_NAME}'!A:J"
        
        # 기존 데이터를 조회하여 중복 체크
        res = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name
        ).execute()
        existing_values = res.get('values', [])
        
        existing_ids = set()
        if len(existing_values) > 1:
            for row in existing_values[1:]:
                if row:
                    existing_ids.add(row[0])

        rows_to_append = []
        for q in questions:
            # ID 생성 (예: 2026_6M_35)
            q_id = f"{q.get('examName', 'EXAM')}_{q.get('qNum', '00')}".replace(" ", "_")
            
            if q_id in existing_ids:
                print(f"[*] 이미 등록된 문항입니다. 건너뜁니다: {q_id}")
                continue
                
            # 안전하게 문자열로 변환 (Gemini가 리스트나 숫자를 반환할 것에 대비)
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

        if rows_to_append:
            body = {'values': rows_to_append}
            service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            print(f"[+] 구글 스프레드시트에 {len(rows_to_append)}개의 수능/모평 문항이 성공적으로 등록되었습니다.")
            return True
        else:
            print("[*] 추가할 신규 기출 문항이 없습니다.")
            return True
            
    except Exception as e:
        print(f"[!] 구글 스프레드시트 적재 실패: {e}")
        return False

# 7. 교사용 수업 지도안 (Markdown) 생성
def generate_teacher_guide(question, api_key):
    if not api_key:
        return ""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
다음은 최근 기출된 수능/모평 음운론 문제 데이터입니다.
이 문제를 바탕으로 고등학교 2학년 2학기 학생들을 대상으로 하는 **50분 수업 지도안(교사용)**을 만들어 주세요.

[수능/모평 기출 정보]
- 시험명: {question['examName']} ({question['qNum']}번)
- 음운론 유형: {question['phonologyType']}
- 발문: {question['qContent']}
- 보기: {question['boxContent']}
- 선지: {question['options']}
- 정답: {question['answer']}번
- 해설: {question['explanation']}

[지도안 작성 요구사항]
1. **수업 개요**: 단원명(음운 변동), 성취기준, 학습 목표를 명확히 제시하십시오.
2. **도입 (10분)**: 기출문제의 키워드(예: {question['keywords']})를 활용한 흥미 유발 및 전시학습 상기.
3. **전개 (30분)**:
   - 기출문제의 핵심 개념(예: {question['phonologyType']}) 설명.
   - 학생들에게 기출문제를 제시하고, 오개념이 발생할 수 있는 매력적인 오답 선지를 찾아내어 토론하는 과정 설계.
   - AI 튜터 시스템(웹앱)을 사용하여 학생들이 귀납적으로 가설을 검증하도록 유도하는 시나리오 포함.
4. **정리 및 평가 (10분)**: 학습 내용 요약 및 기출문제 정답 확인, 형성 평가 퀴즈 제시.
5. **교사 팁(Tip)**: 학생들이 특히 헷갈리기 쉬운 오개념(예: 자음군 단순화와 음절의 끝소리 규칙의 변동 차이 등)을 명확하게 피드백하는 팁 기재.

출력은 반드시 깔끔하고 정돈된 마크다운(Markdown) 포맷으로 해 주십시오.
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.4}
    }
    
    try:
        response = requests.post(url, json=payload, timeout=90)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"[!] 지도안 생성 실패: {e}")
    return ""

# 8. 학생용 연계 학습지 (HTML) 생성
def generate_student_worksheet(question, api_key):
    if not api_key:
        return ""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
다음은 최신 수능/모평 음운론 기출문제입니다.
이 문제를 활용하여 고등학교 2학년 학생들이 직접 손으로 적고 탐구할 수 있는 **귀납적 탐구 학습지(학생용)**를 HTML 파일 형식으로 작성해 주세요.

[수능/모평 기출 정보]
- 시험명: {question['examName']} ({question['qNum']}번)
- 음운론 유형: {question['phonologyType']}
- 발문: {question['qContent']}
- 보기: {question['boxContent']}
- 선지: {question['options']}
- 정답: {question['answer']}번
- 해설: {question['explanation']}

[학습지 구성 요구사항]
1. **학습지 제목**: "[학습지] 최신 기출 연계 문법 탐구 : {question['phonologyType']}"
2. **학생 인적사항**: 학년, 반, 번호, 이름 기입란 생성.
3. **[1단계] 기출 데이터 분석하기**:
   - 기출문제의 <보기>와 문제를 그대로 수록하고, 학생들이 실제 시험 문제를 읽어보도록 유도.
   - 기출 단어들의 발음이 어떻게 변하는지 적어보는 표를 만드시오 (예: 표기 | 실제 발음 | 발생한 음운 변동).
4. **[2단계] 가설 및 탐구**:
   - "이 문제의 정답이 {question['answer']}번인 이유를 위의 표를 바탕으로 귀납적으로 추론하여 가설을 세워봅시다." 빈 칸 작성란.
   - 학생들이 AI 튜터 웹앱에 접속해 해당 규칙을 검증해 볼 수 있도록 권장하는 가이드 안내문 기재.
5. **[3단계] 개념 정교화 및 응용**:
   - 교과서 연계 추가 탐구 단어를 제시하고 스스로 소리 내어 발음하여 음운 변동을 분류해 보게 하시오.
6. **디자인 테마**: 
   - 폰트는 'Malgun Gothic' 혹은 기본 시스템 폰트 적용.
   - 테두리가 부드러운 회색 박스(`.box`), 표 스타일은 연한 회색 배경(`th`)과 깔끔한 경계선(`border`)을 지니며 줄간격은 `2.0`으로 가독성 좋게 Vanilla CSS 스타일링을 HTML 헤더 안에 내장해 주십시오.

출력은 오직 HTML 코드로만(마크다운 ```html 코드 블록 포함) 응답해 주십시오.
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3}
    }
    
    try:
        response = requests.post(url, json=payload, timeout=90)
        if response.status_code == 200:
            raw_html = response.json()['candidates'][0]['content']['parts'][0]['text']
            return raw_html.replace("```html", "").replace("```", "").strip()
    except Exception as e:
        print(f"[!] 학습지 HTML 생성 실패: {e}")
    return ""

# 9. 생성된 학습지 HTML을 Google Docs에 자동 업로드
def upload_worksheet_to_google_docs(title, html_content, creds):
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
        
        return file.get('webViewLink')
    except Exception as e:
        print(f"[!] 구글 문서 업로드 실패: {e}")
        return None

# 10. 테스트용 데모 데이터 정의 (바탕화면에 새 파일이 없을 시 실행)
def get_demo_question():
    return {
        "examName": "2024학년도 대학수학능력시험",
        "qNum": "35",
        "phonologyType": "교체 - 구개음화 및 탈락 - 자음군 단순화",
        "qContent": "다음은 음운 변동에 대한 수업의 일부이다. [A]에 들어갈 내용으로 가장 적절한 것은?",
        "boxContent": (
            "선생님: 음운 변동은 크게 교체, 탈락, 첨가, 축약으로 나뉩니다. 두 개 이상의 음운 변동이 결합하여 일어나는 경우도 있습니다. "
            "예를 들어 '짚고'는 [집고]를 거쳐 최종적으로 [집꼬]로 발음되므로 음절의 끝소리 규칙과 된소리되기가 차례로 적용됩니다. "
            "이는 두 가지 모두 '교체'에 해당합니다. 그럼 다음 단어들의 음운 변동을 분류해 볼까요?\n"
            "단어: 놓는[논는], 굳이[구지], 읊고[읍꼬]"
        ),
        "options": (
            "① '놓는'은 '탈락'과 '교체'가 차례로 일어났습니다.\n"
            "② '굳이'는 '교체'만 두 번 일어났습니다.\n"
            "③ '읊고'는 '탈락'과 '교체'가 차례로 일어났습니다.\n"
            "④ '놓는'과 '굳이'는 공통적으로 '교체'가 일어났습니다.\n"
            "⑤ '굳이'와 '읊고'는 공통적으로 '탈락'이 일어났습니다."
        ),
        "answer": "4",
        "explanation": (
            "정답 4번: '놓는'은 [논는]으로 발음되며 ㅎ-탈락(탈락)이 적용되는 표준 발음 규정에 근거하지만, "
            "실제 수능 시험 범위에서는 음절의 끝소리 규칙(교체, ㄷ으로 바뀜) 후 비음화(교체, ㄴ으로 바뀜)가 적용되는 것으로 볼 수도 있고, "
            "교육과정 평가원의 공식 입장으로는 ㅎ-탈락(탈락) 후 비음화가 적용되기도 합니다. "
            "어느 설을 따르든 '비음화(교체)'가 적용됩니다. '굳이'는 [구지]로 발음되므로 구개음화(교체)가 적용됩니다. "
            "따라서 두 단어 모두 공통적으로 '교체' 음운 변동이 최소 1회 이상 발생합니다."
        ),
        "keywords": "놓는,굳이,읊고,구개음화,자음군단순화,된소리되기,비음화,교체,탈락"
    }

# 메인 제어 흐름
def main():
    print("=== 수능/모평 음운론 수업 자료 자동 생성 및 AI 튜터 연계 시스템 ===")
    api_key = get_gemini_api_key()
    creds = get_google_credentials()
    
    if not api_key:
        print("[!] 경고: GEMINI_API_KEY가 .env 파일에 설정되어 있지 않습니다.")
        sys.exit(1)
        
    question_pdf, commentary_pdf = detect_desktop_pdfs()
    
    questions = []
    
    if question_pdf and commentary_pdf:
        print(f"[+] 감지된 시험지: {os.path.basename(question_pdf)}")
        print(f"[+] 감지된 해설지: {os.path.basename(commentary_pdf)}")
        
        # PDF 텍스트 추출 (보통 국어 영역 문법은 뒤쪽이므로 10~14페이지 내외 집중 추출)
        q_text = extract_text_from_pdf(question_pdf, max_pages=16)
        c_text = extract_text_from_pdf(commentary_pdf, max_pages=30)
        
        # Gemini API로 음운론 문제 파싱
        print("[*] Gemini를 통해 음운론(문법) 기출 문항 분석을 시작합니다...")
        parsed_questions = extract_phonology_questions_via_gemini(q_text, c_text, api_key)
        
        if parsed_questions:
            questions = parsed_questions
            print(f"[+] 분석 성공! 총 {len(questions)}개의 음운론 문제를 추출했습니다.")
        else:
            print("[!] PDF에서 신규 음운론 문제를 추출하지 못했습니다. 데모 모드로 전환합니다.")
            questions = [get_demo_question()]
    else:
        print("[*] 바탕화면에 최근 수능/모의평가 PDF 세트가 없습니다. 데모 기출문항(2024 수능 35번)을 사용하여 기초 작업을 진행합니다.")
        questions = [get_demo_question()]
        
    # 구글 스프레드시트 적재
    if creds:
        print("[*] 구글 스프레드시트에 기출 데이터를 적재합니다...")
        sheet_success = upload_to_google_sheet(questions, creds)
        if sheet_success:
            print("[+] DB 적재 완료!")
    else:
        print("[!] 구글 API 인증 토큰(token.json)이 누락되어 스프레드시트 DB 적재 단계를 건너뜁니다.")
        
    # 문항별 수업 자료 생성
    for q in questions:
        print(f"\n[*] [{q['examName']} {q['qNum']}번] 수업 자료 생성 중...")
        
        # 교사용 지도안 마크다운 파일 작성
        teacher_guide = generate_teacher_guide(q, api_key)
        if teacher_guide:
            guide_filename = f"[교사용_지도안]_{q['examName']}_{q['qNum']}번_음운론.md".replace(" ", "_")
            with open(guide_filename, 'w', encoding='utf-8') as f:
                f.write(teacher_guide)
            print(f"   [+] 교사용 지도안 생성 완료: {guide_filename}")
            
        # 학생용 학습지 HTML 파일 작성
        student_worksheet = generate_student_worksheet(q, api_key)
        if student_worksheet:
            sheet_filename = f"[학생용_학습지]_{q['examName']}_{q['qNum']}번_음운론.html".replace(" ", "_")
            with open(sheet_filename, 'w', encoding='utf-8') as f:
                f.write(student_worksheet)
            print(f"   [+] 학생용 학습지(HTML) 생성 완료: {sheet_filename}")
            
            # 구글 문서 업로드 시도
            if creds:
                print("   [*] 학습지 구글 문서 업로드를 시도합니다...")
                doc_title = f"[학습지] {q['examName']} {q['qNum']}번 음운론 연계 탐구"
                web_link = upload_worksheet_to_google_docs(doc_title, student_worksheet, creds)
                if web_link:
                    print(f"   [+] 구글 문서 업로드 완료! 링크: {web_link}")
                    # 결과를 로컬 로그 파일에 기록
                    with open("google_docs_links.txt", "a", encoding="utf-8") as f:
                        f.write(f"{datetime.date.today()} - {doc_title}: {web_link}\n")
                        
    print("\n[+] 모든 기초 작업이 완료되었습니다!")

if __name__ == "__main__":
    main()
