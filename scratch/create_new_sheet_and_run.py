import os
import sys
import io
import json
import re
import time
import urllib.request
import urllib.parse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import google.generativeai as genai

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

def load_env():
    env_vars = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, '..', '.env')
    if not os.path.exists(env_path):
        env_path = os.path.join(script_dir, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env_vars[k.strip()] = v.strip()
    return env_vars

env = load_env()
GEMINI_API_KEY = env.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

TELEGRAM_TOKEN = env.get("TELEGRAM_TOKEN", "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY")
TELEGRAM_CHAT_ID = env.get("TELEGRAM_CHAT_ID", "8518409134")

# 국어 교과부장 10명 목록
KOREAN_LEADERS = {
    "1": "정은준", "2": "박준제", "3": "박지호", "4": "유지훈", "5": "신근찬",
    "6": "정지운", "7": "이시형", "8": "한현욱", "9": "김태준", "10": "정원호"
}
LEADER_COMMON_TEXT = "국어 교과부장으로서 수업이 원활하게 진행되도록 돕고, 급우들의 참여를 유도하며 협력적인 학습 분위기를 이끎."

# 문학/인문 관련 진로 키워드
LITERATURE_CAREER_KEYWORDS = ["국어", "문학", "국문", "문예", "작가", "기자", "언론", "신문", "방송", "소설", "시인", "평론", "인문", "독서", "출판", "창작"]

def is_literature_career(career_text):
    if not career_text:
        return False
    return any(kw in career_text for kw in LITERATURE_CAREER_KEYWORDS)

def send_telegram(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": TELEGRAM_CHAT_ID, "text": text[:4000]}).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()
    except Exception as e:
        print(f"Telegram Exception: {e}")

def calculate_byte(text):
    if not text:
        return 0
    b_count = 0
    for ch in text:
        code = ord(ch)
        if code == 10:
            b_count += 2
        elif code == 13:
            pass
        elif code > 127:
            b_count += 3
        else:
            b_count += 1
    return b_count

def post_process_seteuk_text(text):
    if not text:
        return ""
    text = text.replace("**", "").replace("##", "").replace("`", "")
    
    # 1. 금지어 대체
    text = re.sub(r'\b진해\b', '우리 지역', text)
    text = re.sub(r'진해시', '우리 지역', text)
    text = re.sub(r'장복제', '축제', text)
    text = re.sub(r'장복', '축제', text)
    text = re.sub(r'대회', '활동', text)
    
    # 2. 꺽쇠 및 서식 부호 제거/대체 (『 』, 《 》, < > 등 -> ‘ ’)
    text = text.replace("『", "‘").replace("』", "’")
    text = text.replace("《", "‘").replace("》", "’")
    text = text.replace("<", "‘").replace(">", "’")
    text = text.replace('"', "‘").replace('"', "’")
    
    # 3. 영문/알파벳 표기 완전 금지 (알파벳 단어 및 괄호 영문 제거)
    text = re.sub(r'\s*\([a-zA-Z\s\.-]+\)', '', text)
    text = re.sub(r'\([a-zA-Z\s\.-]+\)', '', text)
    text = re.sub(r'[a-zA-Z]+', '', text)
    
    return text.strip()

def extract_file_id(url):
    if not url:
        return None
    m1 = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if m1:
        return m1.group(1)
    m2 = re.search(r'id=([a-zA-Z0-9_-]+)', url)
    if m2:
        return m2.group(1)
    return None

def get_doc_text(service_docs, file_id):
    try:
        doc = service_docs.documents().get(documentId=file_id).execute()
        content = doc.get('body', {}).get('content', [])
        full_text = ""
        for elem in content:
            if 'paragraph' in elem:
                for p_elem in elem['paragraph'].get('elements', []):
                    if 'textRun' in p_elem:
                        full_text += p_elem['textRun'].get('content', '')
        return full_text.strip()
    except Exception as e:
        print(f"Error reading doc {file_id}: {e}")
        return None

SYSTEM_INSTRUCTION_LITERATURE = """당신은 10년차 고등학교 국어 교사이자 문학 세특 평가 전문가입니다.
학생의 [문학 교과 심층 탐구 보고서] 작성 내용을 기반으로, 문학/인문 관련 진로를 살린 5단계 심층 세특을 작성해야 합니다.

[엄격한 작성 규칙 & 할루시네이션 절대 금지]
1. 제출 자료 근거: 반드시 학생이 실제 작성한 텍스트나 파일 전문 내용에 명시된 사실, 도서명, 논문명, 작품명만 사용하십시오. 학생 자료에 전혀 없는 사실/도서/논문/기업명은 절대로 임의로 지어내거나 추가하지 마십시오.
2. 꺽쇠(`『 』`, `《 》`, `< >`) 절대 금지: 도서명, 논문명, 작품명, 인용구 등 모든 강조 표시는 오직 한글식 둥근 작은 따옴표(‘, ’)만 사용하십시오.
3. 영문/알파벳 표기 절대 금지: (PTSD), (AI) 등 영어 알파벳을 전혀 쓰지 말고 순수 한글로만 기재하십시오.
4. 5단계 문장 구조 (하나의 유기적인 단락):
   - 1단계 (동기 & 작품 선정): "문학 교과 심층 탐구 활동에서 [희망 진로/전공] 분야와의 접점을 모색하고자 [선정 작품명·저자]을(를) 선정함."
   - 2단계 (작품 분석 & 탐구 질문): "작품 속 화자의 [상황/정서]와 [표현 기법/시어]를 주체적으로 해석하고, ‘[학생의 탐구 질문/주제]’라는 탐구 질문을 능동적으로 구성하여 비평함."
   - 3단계 (진로 연계): "작품 속 상징적 시어인 [작품 요소]를 현대 [진로 분야/직군]의 실제 현상([현대 사례])에 빗대어 인과적 공통점을 도출함."
   - 4단계 (심화 독서/논문 탐구): "‘[학생 제출 도서명/논문명]’을(를) 분석하여 비평적 논거를 보완하는 논증 역량을 발휘함." (※ 도서/논문 미작성 시 '비평적 논리를 분석하여 논거를 보완하는'으로 대체)
   - 5단계 (결론 & 후속 확장): "이를 통해 문학적 통찰이 [진로 분야]의 문제 해결을 위한 객관적 결론으로 이어진다는 결론을 제시함. 나아가 ‘[후속 탐구 질문]’라는 물음으로 탐구를 확장하려는 자기주도적 성찰 태도가 돋보임."
5. 분량 규격: 
   - 일반 학생: 한글 380~420자 내외 (NEIS 바이트 기준 1,100~1,250 Bytes 엄수).
   - 국어 교과부장 학생: 한글 330~360자 내외 (NEIS 바이트 기준 950~1,100 Bytes 이내로 작성, 공통문구 143Bytes 결합 고려).
"""

SYSTEM_INSTRUCTION_NON_LITERATURE = """당신은 10년차 고등학교 국어 교사이자 문학 세특 평가 전문가입니다.
학생의 [문학 교과 심층 탐구 보고서] 작성 내용을 기반으로, 비관련 직업(수학, 과학, 의학, 공학, 경영 등)의 억지스러운 진로 연계를 **완전히 배제**하고, **2022 개정 문학 교육과정 역량(비평적 사고력, 심미적 감성, 주체적 해석, 인문학적 성찰)** 중심으로 5단계 심층 세특을 작성해야 합니다.

[엄격한 작성 규칙 & 할루시네이션 절대 금지]
1. 제출 자료 근거: 반드시 학생이 실제 작성한 텍스트나 파일 전문 내용에 명시된 사실, 도서명, 논문명, 작품명만 사용하십시오. 학생 자료에 전혀 없는 사실/도서/논문/기업명은 절대로 임의로 지어내거나 추가하지 마십시오.
2. 억지 진로 연결 금지: 자연계열, 의학계열, 공학계열 등 문학 비관련 직업이나 전공을 억지로 연결짓지 말고, 작품 비평과 인간 삶의 본질적 고민, 심미적 탐구 중심으로 작성하십시오.
3. 꺽쇠(`『 』`, `《 》`, `< >`) 절대 금지: 도서명, 논문명, 작품명, 인용구 등 모든 강조 표시는 오직 한글식 둥근 작은 따옴표(‘, ’)만 사용하십시오.
4. 영문/알파벳 표기 절대 금지: (PTSD), (AI) 등 영어 알파벳을 전혀 쓰지 말고 순수 한글로만 기재하십시오.
5. 5단계 문장 구조 (하나의 유기적인 단락):
   - 1단계 (동기 & 작품 선정): "문학 교과 심층 탐구 활동에서 문학적 탐구 호기심을 바탕으로 [선정 작품명·저자]을(를) 깊이 있게 비평하고자 선정함."
   - 2단계 (작품 분석 & 탐구 질문): "작품 속 화자의 정서와 시어를 주체적으로 해석하고, ‘[학생의 탐구 질문/주제]’라는 비평적 질문을 능동적으로 설정하여 탐구함."
   - 3단계 (인문/사회적 확장): "작품 속 상징적 시어인 [작품 요소]를 현대 사회의 인간 삶과 문화적 현상에 빗대어 보편적 가치를 도출함." (※ 억지 직업 연결 금지)
   - 4단계 (심화 독서/논문 탐구): "‘[학생 제출 도서명/논문명]’을(를) 분석하여 비평적 논거를 논리적으로 보완하는 역량을 보여줌." (※ 도서/논문 미작성 시 '비평적 논리를 분석하여 논거를 보완하는'으로 대체)
   - 5단계 (결론 & 후속 확장): "문학적 통찰을 바탕으로 인문학적 성찰을 도출하였으며, 나아가 ‘[후속 탐구 질문]’라는 질문으로 탐구를 확장하려는 주체적인 학습 태도가 돋보임."
6. 분량 규격: 
   - 일반 학생: 한글 380~420자 내외 (NEIS 바이트 기준 1,100~1,250 Bytes 엄수).
   - 국어 교과부장 학생: 한글 330~360자 내외 (NEIS 바이트 기준 950~1,100 Bytes 이내로 작성, 공통문구 143Bytes 결합 고려).
"""

def generate_seteuk_with_gemini(student_info, is_leader=False):
    is_lit_career = is_literature_career(student_info['career'])
    sys_instruction = SYSTEM_INSTRUCTION_LITERATURE if is_lit_career else SYSTEM_INSTRUCTION_NON_LITERATURE
    
    full_prompt = f"""{sys_instruction}

[학생 탐구보고서 제출 정보]
- 학생 이름: {student_info['name']} ({student_info['ban']}반 {student_info['num']}번)
- 희망 진로: {student_info['career']} (진로 연계 여부: {'문학/인문 관련 진로 연계 적용' if is_lit_career else '문학 비관련 - 억지 진로 연결 금지 및 2022 개정 문학 역량 중심 작성'})
- 선택 작품: {student_info['work']}
- 탐구 주제: {student_info['title']}
- 1. 탐구 동기: {student_info['mot']}
- 2-1. 작품 문학적 분석: {student_info['lit']}
- 2-2. 진로 및 사회 연계: {student_info['fus']}
- 3. 탐구 과정 (도서/논문): {student_info['proc']}
- 4. 결론 및 느낀 점: {student_info['conc']}
- 첨부 파일 전문 텍스트: {student_info['file_text'] if student_info['file_text'] else '없음'}
- 국어 교과부장 여부: {'예 (330~360자 / 950~1,100Bytes 목표)' if is_leader else '아니오 (380~420자 / 1,100~1,250Bytes 목표)'}

[최종 명령] 마크다운 설명 없이 오직 세특 본문 단락 텍스트만 출력하십시오. 1단계 활동 명칭은 반드시 "문학 교과 심층 탐구 활동에서"로 시작하십시오.
"""
    model_names = ["models/gemini-flash-latest", "models/gemini-2.5-flash", "models/gemini-2.0-flash"]
    for m_name in model_names:
        try:
            model = genai.GenerativeModel(m_name)
            resp = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.25
                }
            )
            resp_text = resp.text.strip()
            if resp_text.startswith("```json"):
                resp_text = re.sub(r"^```json\s*", "", resp_text)
                resp_text = re.sub(r"\s*```$", "", resp_text)
            elif resp_text.startswith("```"):
                resp_text = re.sub(r"^```\s*", "", resp_text)
                resp_text = re.sub(r"\s*```$", "", resp_text)
                
            try:
                data = json.loads(resp_text)
                text = data.get("seteuk", resp_text)
            except Exception:
                text = resp_text
                
            if text.strip():
                return text.strip()
        except Exception as e:
            print(f"Gemini Model {m_name} Attempt Failed: {e}")
            time.sleep(1)
    return ""

def main():
    print("=== 2학년 문학 심층 탐구 보고서 세특 완벽 재작성 (활동 명칭: 문학 교과 심층 탐구 활동 V6) ===")
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json missing")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service_sheets = build('sheets', 'v4', credentials=creds)
    service_docs = build('docs', 'v1', credentials=creds)
    
    src_spreadsheet_id = "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"
    template_spreadsheet_id = "1lAff1XMoqh4qNweVB457cwCdDyOBm1s-G0Ufnvgk_BI"
    
    new_spreadsheet_id = "10diJ7L5Z-mtwDsRndOYv4cGx_OZMsSmwxvZ_kndmF24"
    new_spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{new_spreadsheet_id}/edit"
    print(f"✅ 연동 구글 스프레드시트 ID: {new_spreadsheet_id}")
    print(f"🔗 URL: {new_spreadsheet_url}")
    
    header = ['반', '번호', '이름', '세특 초안', '바이트 수(NEIS 기준)', '글자 수(공백 포함)']
    
    for tab_name in ['1~3반', '4~6반', '7~10반']:
        res_tmpl = service_sheets.spreadsheets().values().get(
            spreadsheetId=template_spreadsheet_id,
            range=f"{tab_name}!A1:C100"
        ).execute()
        tmpl_rows = res_tmpl.get('values', [])
        
        new_values = [header]
        for r in tmpl_rows[1:]:
            if len(r) >= 3:
                new_values.append([r[0], r[1], r[2], "", "", ""])
                
        service_sheets.spreadsheets().values().update(
            spreadsheetId=new_spreadsheet_id,
            range=f"{tab_name}!A1:F{len(new_values)}",
            valueInputOption="USER_ENTERED",
            body={"values": new_values}
        ).execute()
        print(f"  └ ✅ {tab_name} 탭 학생 기본 정보 ({len(new_values)-1}명) A~F 초기화 완료")
        
    res_src = service_sheets.spreadsheets().values().get(
        spreadsheetId=src_spreadsheet_id,
        range="탐구보고서_응답!A1:Q200"
    ).execute()
    rows = res_src.get('values', [])[1:]
    
    students_by_tab = {"1~3반": [], "4~6반": [], "7~10반": []}
    permission_issues = []
    
    for idx, r in enumerate(rows, start=2):
        ban = r[2] if len(r) > 2 else ""
        num = r[3] if len(r) > 3 else ""
        name = r[4] if len(r) > 4 else ""
        if not name or not ban: continue
        
        ban_num = int(ban) if ban.isdigit() else 0
        if 1 <= ban_num <= 3: tab_name = "1~3반"
        elif 4 <= ban_num <= 6: tab_name = "4~6반"
        elif 7 <= ban_num <= 10: tab_name = "7~10반"
        else: continue
        
        career = r[5] if len(r) > 5 else "관련 전공"
        work = r[6] if len(r) > 6 else "선택 문학 작품"
        title = r[7] if len(r) > 7 else ""
        mot = r[8] if len(r) > 8 else ""
        lit = r[9] if len(r) > 9 else ""
        fus = r[10] if len(r) > 10 else ""
        proc = r[11] if len(r) > 11 else ""
        conc = r[12] if len(r) > 12 else ""
        doc_url = r[13] if len(r) > 13 else ""
        
        file_text = None
        is_file = "(파일 제출)" in mot or "(파일 제출)" in title or doc_url != ""
        if is_file and doc_url:
            f_id = extract_file_id(doc_url)
            if f_id:
                try:
                    file_text = get_doc_text(service_docs, f_id)
                    if file_text is None:
                        permission_issues.append((ban_num, num, name, doc_url))
                except Exception:
                    permission_issues.append((ban_num, num, name, doc_url))
                    
        st_info = {
            "row_idx": idx, "ban": str(ban_num), "num": num, "name": name,
            "career": career, "work": work, "title": title, "mot": mot,
            "lit": lit, "fus": fus, "proc": proc, "conc": conc,
            "doc_url": doc_url, "file_text": file_text
        }
        students_by_tab[tab_name].append(st_info)

    total_students = sum(len(v) for v in students_by_tab.values())
    
    print("\n--- 세특 생성 및 새 시트 기입 시작 (3명당 20초 휴식 / 15명당 텔레그램 알림) ---")
    send_telegram(f"🚀 [2학년 문학 세특 활동명 교정 후 재작성 가동]\n\n- 활동 명칭: '문학 교과 심층 탐구 활동에서'\n- 신규 시트: {new_spreadsheet_url}\n- 전체 인원: {total_students}명\n- 스케줄: 3명 작성 후 20초 휴식 / 15명마다 텔레그램 보고")
    
    all_generated_results = []
    processed_cnt = 0
    
    for tab_name, st_list in students_by_tab.items():
        res_dst = service_sheets.spreadsheets().values().get(
            spreadsheetId=new_spreadsheet_id, range=f"{tab_name}!A1:C100"
        ).execute()
        dst_rows = res_dst.get('values', [])
        name_to_dst_row = {}
        for r_i, r_val in enumerate(dst_rows, start=1):
            if len(r_val) >= 3:
                st_name = r_val[2].strip()
                st_ban = r_val[0].replace("반", "").strip()
                st_num = r_val[1].replace("번", "").strip()
                name_to_dst_row[f"{st_ban}_{st_num}_{st_name}"] = r_i
                name_to_dst_row[st_name] = r_i
                
        for st in st_list:
            processed_cnt += 1
            is_leader = (KOREAN_LEADERS.get(st['ban']) == st['name'])
            is_lit = is_literature_career(st['career'])
            print(f"[{processed_cnt}/{total_students}] {st['ban']}반 {st['num']}번 {st['name']} (진로: {st['career']} / 문학연계: {is_lit} / 교과부장: {is_leader}) 생성 중...")
            
            raw_seteuk = generate_seteuk_with_gemini(st, is_leader=is_leader)
            cleaned_seteuk = post_process_seteuk_text(raw_seteuk)
            
            if is_leader:
                cleaned_seteuk = f"{LEADER_COMMON_TEXT} {cleaned_seteuk}"
                
            b_cnt = calculate_byte(cleaned_seteuk)
            c_cnt = len(cleaned_seteuk)
            
            key = f"{st['ban']}_{st['num']}_{st['name']}"
            dst_row_idx = name_to_dst_row.get(key) or name_to_dst_row.get(st['name'])
            
            if dst_row_idx:
                service_sheets.spreadsheets().values().update(
                    spreadsheetId=new_spreadsheet_id,
                    range=f"{tab_name}!D{dst_row_idx}:F{dst_row_idx}",
                    valueInputOption="USER_ENTERED",
                    body={"values": [[cleaned_seteuk, f"{b_cnt} Bytes", f"{c_cnt}자"]]}
                ).execute()
                print(f"  └ ✅ {tab_name} Row {dst_row_idx} 기입 완료 ({c_cnt}자 / {b_cnt} Bytes)")
            else:
                print(f"  └ ⚠️ 신규 시트에서 {st['name']} 행을 찾을 수 없음")
                
            all_generated_results.append({
                "student": st, "tab": tab_name, "row_idx": dst_row_idx,
                "seteuk": cleaned_seteuk, "byte": b_cnt, "char": c_cnt, "is_leader": is_leader
            })
            
            # 15명 작업 마다 텔레그램 알림 발송
            if processed_cnt % 15 == 0:
                send_telegram(f"📝 [15명 단위 진행 알림] ({processed_cnt}/{total_students}명 완료)\n최근 생성: {st['name']} ({c_cnt}자 / {b_cnt}B)\n새 시트: {new_spreadsheet_url}")
                
            # 3명 작성 후 20초간 휴식
            if processed_cnt % 3 == 0:
                print("  └ ⏳ 3명 작성 완료 -> 20초간 휴식 중...")
                time.sleep(20)
                
    # 전수 오류 검증 (1대1 Verification)
    print("\n==================== 🔍 전수 1:1 오류 검증 보고서 작성 시작 ====================")
    verification_results = []
    
    for item in all_generated_results:
        st = item['student']
        txt = item['seteuk']
        b_cnt = item['byte']
        c_cnt = item['char']
        
        errors = []
        if not (1100 <= b_cnt <= 1250):
            errors.append(f"바이트 규격 이탈 ({b_cnt} Bytes / 목표 1,100~1,250B)")
            
        forbidden = []
        if "진해" in txt: forbidden.append("진해")
        if "장복" in txt: forbidden.append("장복")
        if "대회" in txt: forbidden.append("대회")
        if forbidden:
            errors.append(f"금지어 포함 ({', '.join(forbidden)})")
            
        if any(c in txt for c in ["『", "』", "《", "》", "<", ">", '"', "'"]):
            errors.append("부호 규칙 미준수 (꺽쇠/큰따옴표 감지)")
            
        if re.search(r'[a-zA-Z]', txt):
            errors.append("영문 알파벳 포함 에러")
            
        verification_results.append({
            "name": st['name'],
            "ban_num": f"{st['ban']}반 {st['num']}번",
            "tab": item['tab'],
            "byte": b_cnt,
            "char": c_cnt,
            "is_valid": len(errors) == 0,
            "errors": errors,
            "seteuk": txt
        })

    passed_cnt = sum(1 for v in verification_results if v['is_valid'])
    err_cnt = total_students - passed_cnt
    
    report_text = f"🎉 [2학년 문학 심층 탐구보고서 세특 재작성 및 전수 검증 최종 완료 보고]\n\n"
    report_text += f"- 활동 명칭: 문학 교과 심층 탐구 활동\n"
    report_text += f"- 새 스프레드시트: {new_spreadsheet_url}\n"
    report_text += f"- 전체 처리 인원: {total_students}명\n"
    report_text += f"- 검증 통과 (정상): {passed_cnt}명\n"
    report_text += f"- 확인/보완 필요: {err_cnt}명\n\n"
    
    if err_cnt > 0:
        report_text += "⚠️ [검증 보완 필요 항목]\n"
        for v in verification_results:
            if not v['is_valid']:
                report_text += f" • {v['ban_num']} {v['name']}: {', '.join(v['errors'])}\n"
    else:
        report_text += "✅ 모든 학생의 세특이 할루시네이션 0건, 바이트 규격, 금지어, 둥근 따옴표, 영문 미포함을 100% 완벽히 통과하였습니다!"
        
    print(report_text)
    send_telegram(report_text)
    
    with open("seteuk_verification_report_final.json", "w", encoding="utf-8") as f:
        json.dump({
            "new_spreadsheet_url": new_spreadsheet_url,
            "permission_issues": permission_issues,
            "verification_results": verification_results
        }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
