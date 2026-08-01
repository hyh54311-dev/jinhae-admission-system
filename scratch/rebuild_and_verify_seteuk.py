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

def clean_and_replace_forbidden_terms(text):
    if not text:
        return ""
    text = text.replace("**", "").replace("##", "").replace("`", "")
    text = re.sub(r'\b진해\b', '우리 지역', text)
    text = re.sub(r'진해시', '우리 지역', text)
    text = re.sub(r'장복제', '축제', text)
    text = re.sub(r'장복', '축제', text)
    text = re.sub(r'대회', '활동', text)
    # 인용부호 둥근 따옴표 변환
    text = text.replace('"', "‘").replace('"', "’")
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

SYSTEM_INSTRUCTION = """당신은 10년차 고등학교 국어 교사이자 문학 세특 평가 전문가입니다.
학생의 [문학 교과 심층 탐구 보고서] 작성 내용을 기반으로, 2022 개정 국어과 역량이 드러나는 5단계 심층 세특을 작성해야 합니다.

[엄격한 작성 규칙 & 할루시네이션 절대 금지]
1. 제출 자료 근거: 반드시 학생이 실제 작성한 텍스트나 파일 전문 내용에 명시된 사실, 도서명, 논문명, 작품명만 사용하십시오. 학생 자료에 전혀 없는 사실/도서/논문/기업명은 절대로 임의로 지어내거나 추가하지 마십시오.
2. 5단계 문장 구조 및 템플릿 (하나의 유기적인 단락):
   - 1단계 (동기 & 작품 선정): "고전시가/문학 현대적 관점으로 비평하기(탐구) 활동에서 [희망 진로/전공] 분야와의 접점을 모색하고자 [선정 작품명·저자]을(를) 선정함."
   - 2단계 (작품 분석 & 탐구 질문): "작품 속 화자의 [상황/정서]와 [표현 기법/시어]를 주체적으로 해석하고, ‘[학생의 탐구 질문/주제]’라는 탐구 질문을 능동적으로 구성하여 비평함."
   - 3단계 (진로/현대사회 연계): "작품 속 상징적 시어인 [작품 요소]를 현대 [진로 분야/직군]의 실제 현상([현대 사례])에 빗대어 인과적 공통점을 도출함."
   - 4단계 (심화 독서/논문 탐구): "[학생 제출 도서명/논문명/학술자료]을(를) 분석하여 비평적 논거를 보완하는 논증 역량을 발휘함." (※ 도서/논문 미작성 시 '비평적 논리를 분석하여 논거를 보완하는'으로 대체)
   - 5단계 (결론 & 후속 확장): "이를 통해 문학적 통찰이 [진로 분야]의 문제 해결을 위한 객관적 결론으로 이어진다는 결론을 제시함. 나아가 ‘[후속 탐구 질문]’라는 물음으로 탐구를 확장하려는 자기주도적 성찰 태도가 돋보임."
3. 분량 규격: 
   - 일반 학생: 한글 380~420자 내외 (NEIS 바이트 기준 1,100~1,250 Bytes 엄수).
   - 국어 교과부장 학생: 한글 330~360자 내외 (NEIS 바이트 기준 950~1,100 Bytes 이내로 작성, 공통문구 143Bytes 결합 고려).
4. 서술 및 문장 부호:
   - 생활기록부용 명사형 종결어미(~함., ~임., ~됨., ~평가함.) 사용.
   - 모든 인용 및 탐구 질문은 반드시 한글식 둥근 따옴표(‘, ’)로 감쌀 것.
   - 특정 지명('우리 지역'), 사기업/기관명 일반화, '대회' 단어 절대 금지.

[출력 형식]
설명글 없이 오직 다음 JSON 형식으로만 응답하시오:
{ "seteuk": "완성된 5단계 세특 본문 전체" }
"""

def generate_seteuk_with_gemini(student_info, is_leader=False):
    prompt = f"""[학생 탐구보고서 제출 정보]
- 학생 이름: {student_info['name']} ({student_info['ban']}반 {student_info['num']}번)
- 희망 진로: {student_info['career']}
- 선택 작품: {student_info['work']}
- 탐구 주제: {student_info['title']}
- 1. 탐구 동기: {student_info['mot']}
- 2-1. 작품 문학적 분석: {student_info['lit']}
- 2-2. 진로 및 사회 연계: {student_info['fus']}
- 3. 탐구 과정 (도서/논문): {student_info['proc']}
- 4. 결론 및 느낀 점: {student_info['conc']}
- 첨부 파일 전문 텍스트: {student_info['file_text'] if student_info['file_text'] else '없음'}
- 국어 교과부장 여부: {'예 (330~360자 / 950~1,100Bytes 목표)' if is_leader else '아니오 (380~420자 / 1,100~1,250Bytes 목표)'}
"""
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=SYSTEM_INSTRUCTION)
    for attempt in range(3):
        try:
            resp = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "response_mime_type": "application/json"
                }
            )
            data = json.loads(resp.text)
            text = data.get("seteuk", "")
            return text
        except Exception as e:
            print(f"Gemini Attempt {attempt+1} Failed: {e}")
            time.sleep(3)
    return ""

def main():
    print("=== 2학년 문학 심층 탐구 보고서 세특 재작성 및 전수 검증 프로세스 시작 ===")
    token_path = 'token.json'
    if not os.path.exists(token_path):
        print("token.json missing")
        return
        
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/drive'])
    service_sheets = build('sheets', 'v4', credentials=creds)
    service_docs = build('docs', 'v1', credentials=creds)
    
    src_spreadsheet_id = "1GG3_Yld5QSzqQ-Ai3XvNWbTosPyOqDSVaWiQEJ_43cY"
    dst_spreadsheet_id = "1lAff1XMoqh4qNweVB457cwCdDyOBm1s-G0Ufnvgk_BI"
    
    # 1. 원본 응답 시트 데이터 읽기
    res_src = service_sheets.spreadsheets().values().get(
        spreadsheetId=src_spreadsheet_id,
        range="탐구보고서_응답!A1:Q200"
    ).execute()
    rows = res_src.get('values', [])
    if not rows:
        print("원본 데이터를 찾을 수 없습니다.")
        return
        
    student_rows = rows[1:] # row 2~
    print(f"총 원본 제출 수: {len(student_rows)}건")
    
    # 2. 반별 학생 정보 정돈
    students_by_tab = {
        "1~3반": [],
        "4~6반": [],
        "7~10반": []
    }
    
    for idx, r in enumerate(student_rows, start=2):
        ban = r[2] if len(r) > 2 else ""
        num = r[3] if len(r) > 3 else ""
        name = r[4] if len(r) > 4 else ""
        if not name or not ban:
            continue
            
        ban_num = int(ban) if ban.isdigit() else 0
        if 1 <= ban_num <= 3:
            tab_name = "1~3반"
        elif 4 <= ban_num <= 6:
            tab_name = "4~6반"
        elif 7 <= ban_num <= 10:
            tab_name = "7~10반"
        else:
            continue
            
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
                file_text = get_doc_text(service_docs, f_id)
                
        st_info = {
            "row_idx": idx,
            "ban": str(ban_num),
            "num": num,
            "name": name,
            "career": career,
            "work": work,
            "title": title,
            "mot": mot,
            "lit": lit,
            "fus": fus,
            "proc": proc,
            "conc": conc,
            "doc_url": doc_url,
            "file_text": file_text
        }
        students_by_tab[tab_name].append(st_info)

    # 3. 대상 스프레드시트 초기화 (기존 세특 D~F열 삭제)
    print("\n--- 대상 스프레드시트 3개 탭 초기화 진행 ---")
    for tab in ["1~3반", "4~6반", "7~10반"]:
        service_sheets.spreadsheets().values().clear(
            spreadsheetId=dst_spreadsheet_id,
            range=f"{tab}!D2:F100"
        ).execute()
        print(f"✅ {tab} 탭 D2:F100 영역 초기화 완료")
        
    # 4. 학생별 세특 생성 및 기입 (1명 후 20초 휴식)
    all_generated_results = []
    total_students = sum(len(v) for v in students_by_tab.values())
    processed_cnt = 0
    
    send_telegram(f"🚀 [2학년 문학 탐구보고서 세특 자동 생성 시작]\n\n- 전체 작업 인원: {total_students}명\n- 방식: 5단계 심층 세특 + 1명당 20초 대기\n- 전수 검증 연동 예정")
    
    for tab_name, st_list in students_by_tab.items():
        print(f"\n==================== {tab_name} ({len(st_list)}명) 작업 시작 ====================")
        # 대상 시트에서 이름 매칭하여 행 찾기
        res_dst = service_sheets.spreadsheets().values().get(
            spreadsheetId=dst_spreadsheet_id,
            range=f"{tab_name}!A1:C100"
        ).execute()
        dst_rows = res_dst.get('values', [])
        
        # dst_rows: row 1 is header. row 2 -> idx 2
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
            print(f"[{processed_cnt}/{total_students}] {st['ban']}반 {st['num']}번 {st['name']} (교과부장: {is_leader}) 생성 중...")
            
            raw_seteuk = generate_seteuk_with_gemini(st, is_leader=is_leader)
            cleaned_seteuk = clean_and_replace_forbidden_terms(raw_seteuk)
            
            if is_leader:
                cleaned_seteuk = f"{LEADER_COMMON_TEXT} {cleaned_seteuk}"
                
            b_cnt = calculate_byte(cleaned_seteuk)
            c_cnt = len(cleaned_seteuk)
            
            # 대상 행 찾기
            key = f"{st['ban']}_{st['num']}_{st['name']}"
            dst_row_idx = name_to_dst_row.get(key) or name_to_dst_row.get(st['name'])
            
            if dst_row_idx:
                service_sheets.spreadsheets().values().update(
                    spreadsheetId=dst_spreadsheet_id,
                    range=f"{tab_name}!D{dst_row_idx}:F{dst_row_idx}",
                    valueInputOption="USER_ENTERED",
                    body={"values": [[cleaned_seteuk, f"{b_cnt} Bytes", f"{c_cnt}자"]]}
                ).execute()
                print(f"  └ ✅ {tab_name} Row {dst_row_idx} 기입 완료 ({c_cnt}자 / {b_cnt} Bytes)")
            else:
                print(f"  └ ⚠️ 대상 시트에서 {st['name']} 학생 행을 찾을 수 없음")
                
            all_generated_results.append({
                "student": st,
                "tab": tab_name,
                "row_idx": dst_row_idx,
                "seteuk": cleaned_seteuk,
                "byte": b_cnt,
                "char": c_cnt,
                "is_leader": is_leader
            })
            
            if processed_cnt % 5 == 0:
                send_telegram(f"📝 [진행 알림] ({processed_cnt}/{total_students}명 완료)\n최근 생성: {st['name']} ({c_cnt}자 / {b_cnt}B)")
                
            print("  └ ⏳ 20초간 휴식 (Rate Limit 및 안정성 조절)...")
            time.sleep(20)
            
    # 5. 전수 오류 검증 (1대1 Verification)
    print("\n==================== 🔍 전수 1:1 오류 검증 보고서 작성 시작 ====================")
    verification_results = []
    
    for item in all_generated_results:
        st = item['student']
        txt = item['seteuk']
        b_cnt = item['byte']
        c_cnt = item['char']
        
        errors = []
        
        # [검증 1] 바이트 규격 검사 (1100 ~ 1250 Bytes)
        if not (1100 <= b_cnt <= 1250):
            errors.append(f"바이트 규격 이탈 ({b_cnt} Bytes / 목표 1,100~1,250B)")
            
        # [검증 2] 기재 금지어 검사
        forbidden = []
        if "진해" in txt: forbidden.append("진해")
        if "장복" in txt: forbidden.append("장복")
        if "대회" in txt: forbidden.append("대회")
        if forbidden:
            errors.append(f"금지어 포함 ({', '.join(forbidden)})")
            
        # [검증 3] 인용 따옴표 검사 (큰따옴표/홑따옴표 사용 여부)
        if '"' in txt or "'" in txt:
            errors.append("둥근 따옴표(‘ ’) 미준수")
            
        # [검증 4] 할루시네이션 검사 (학생 제출 텍스트에 없는 외생 도서/논문 언급 여부)
        book_matches = re.findall(r'『(.*?)』|《(.*?)》', txt)
        for bm in book_matches:
            b_name = bm[0] or bm[1]
            src_full_text = f"{st['mot']} {st['lit']} {st['fus']} {st['proc']} {st['conc']} {st['file_text'] or ''}"
            if b_name and b_name not in src_full_text:
                errors.append(f"할루시네이션 감지 (임의 도서/논문명: 『{b_name}』)")
                
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

    # 검증 결과 보고서 저장 및 텔레그램 발송
    passed_cnt = sum(1 for v in verification_results if v['is_valid'])
    err_cnt = total_students - passed_cnt
    
    report_text = f"🎉 [2학년 문학 탐구보고서 세특 생성 및 전수 검증 최종 완료 보고]\n\n"
    report_text += f"- 전체 처리 인원: {total_students}명\n"
    report_text += f"- 검증 통과 (정상): {passed_cnt}명\n"
    report_text += f"- 확인/보완 필요: {err_cnt}명\n\n"
    
    if err_cnt > 0:
        report_text += "⚠️ [검증 보완 필요 항목]\n"
        for v in verification_results:
            if not v['is_valid']:
                report_text += f" • {v['ban_num']} {v['name']}: {', '.join(v['errors'])}\n"
    else:
        report_text += "✅ 모든 학생의 세특이 할루시네이션 0건, 바이트 규격, 금지어, 둥근 따옴표를 100% 완벽히 통과하였습니다!"
        
    print(report_text)
    send_telegram(report_text)
    
    # JSON 파일로 검증 결과 persistence
    with open("seteuk_verification_report.json", "w", encoding="utf-8") as f:
        json.dump(verification_results, f, ensure_ascii=False, indent=2)
        
    print("검증 리포트가 seteuk_verification_report.json 에 저장되었습니다.")

if __name__ == "__main__":
    main()
