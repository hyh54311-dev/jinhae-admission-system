import os
import re
import sys
import json
import time
import pandas as pd
import google.generativeai as genai

sys.stdout.reconfigure(encoding='utf-8')

# 1. Configuration
CONFIG = {
    "MODEL_NAME": "gemini-3.1-flash-lite",
    "BATCH_SIZE": 5,
    "DELAY_TIME": 10,  # Delay between batches in seconds
    "BYTE_MIN": 1100,
    "BYTE_MAX": 1300,
}

# 2. Setup API Key
def get_api_key():
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('GEMINI_API_KEY='):
                    return line.strip().split('=', 1)[1].strip()
    return os.environ.get('GEMINI_API_KEY', '')

api_key = get_api_key()
if not api_key:
    print("❌ 에러: .env 파일 또는 환경 변수에서 GEMINI_API_KEY를 찾을 수 없습니다.")
    sys.exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel(CONFIG["MODEL_NAME"])

# 3. Byte Counter (NEIS standard: Korean 3 bytes, space/english 1 byte)
def calculate_byte(s):
    if not isinstance(s, str):
        return 0
    b_len = 0
    for char in s:
        code = ord(char)
        if code == 10:  # Newline
            b_len += 2
        elif code == 13: # Carriage Return
            pass
        elif code > 127: # Multibyte (Korean)
            b_len += 3
        else:            # ASCII (Space, English, Number)
            b_len += 1
    return b_len

# 4. Korean typographic quotes helper
def convert_to_korean_quotes(s):
    if not isinstance(s, str):
        return ""
    # Toggle replacement of straight quotes to opening/closing curly quotes
    out = []
    open_q = True
    for char in s:
        if char == "'":
            out.append("‘" if open_q else "’")
            open_q = not open_q
        else:
            out.append(char)
    return "".join(out)

# 4.5. Telegram helper
def send_telegram_message(text):
    token = "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY"
    chat_id = "8518409134"
    if not token or not chat_id:
        return
    import requests, urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, verify=False)
    except Exception as e:
        print(f"⚠️ 텔레그램 발송 실패: {e}")

# 5. System Instructions
SYSTEM_INSTRUCTION = """당신은 10년차 고등학교 국어 교사이자 문학 세특 평가 전문가입니다.
학생의 고전시가 현대적 관점 비평 활동 답변을 기반으로, 2022 개정 국어과 역량이 드러나는 세특을 작성해야 합니다.

[작성 규칙]
1. 분량: 한글 380~420자 내외 (NEIS 바이트 기준 1100~1250B 엄수).
2. 서술조: 생활기록부용 명사형 종결어미(~함., ~임., ~됨., ~평가함.) 사용.
3. 금지: 기재 금지 조항(부모 직업, 학원, 외부 수상, 성적, 장학금) 절대 언급 금지. '**' 등 마크다운 기호 및 특수문자 금지.
4. 문장부호: 모든 인용, 강조, 탐구 질문 등은 반드시 둥근 따옴표(‘, ’)로 감싸야 합니다.

[6단계 문장 구조 및 템플릿]
반드시 다음 6단계 구조를 엄격히 따라 하나의 유기적인 문단으로 작성하시오:
- 1단계 (선정 및 동기): "고전시가 현대적 관점으로 비평하기 활동에서 [선정 이유]라는 점에 주목하여 [작품명·작가]를 선정함."
  ※ [선정 이유]는 학생의 3번 답변(이유)과 1번 답변(작품명)을 분석해 동적으로 완성할 것.
- 2단계 (해석 및 질문): "화자의 [상황/태도] 상황과 정서, [표현 기법]을 주체적으로 해석하고 현대사회와 유사한 사례를 연계하여 분석함. ‘[탐구 질문]’라는 탐구 질문을 능동적으로 구성하여 비평함."
  ※ 탐구 질문은 둥근 따옴표로 감싼 의문문 형식으로 작성할 것.
- 3단계 (사례 연결): "[현대 사회 사례]를 제시하고, 이를 화자가 [경계한/드러낸/지향한] [핵심 태도]를 현대사회 [분야/직군]의 [현상]에 빗대어 고전과 현대의 공통점을 도출함."
  ※ 비유는 문장 내 1회만 사용할 것.
- 4단계 (재해석/심화): "[인과적 원인]이 [결과·한계]로 이어진다고 재해석하고, [추가 자료명]을 분석하여 논거를 보완하는 논증 역량을 발휘함."
  ※ 학생이 6번 등에서 뉴스/논문 등 추가 자료명을 직접 언급하지 않은 경우 "[추가 자료명]을 분석하여 논거를 보완하는" 구절은 통째로 생략하거나 다른 표현(예: '비평적 논리를 분석하여 논거를 보완하는')으로 대체하여 허위 작성을 방지할 것.
- 5단계 (결론 제시): "이를 통해 [2단계 탐구 질문]이 [부정적 답]이 아닌 [긍정적 답]이라는 결론을 제시함."
  ※ 2단계 질문과 반드시 호응해야 하며, 주관적 성장 서술(~깨달음) 대신 객관적 서술(~제시함)을 사용할 것.
- 6단계 (관찰 및 후속): "[학생의 구체적 통찰/가치관]이 드러나며, 나아가 [지정된 6단계 종결어미 형태]로 마침."
  ※ 주관적 평가 어미(~돋보임)는 이 단계에서 1회만 사용할 것.

[출력 형식]
설명글 없이 오직 다음 JSON 형식으로만 응답하시오:
{ "seteuk": "생성된 세특 본문 전체" }"""

# 6. Student Prompt Generator
def create_student_prompt(name, q1, q2, q3, q4, q5, q6, q7, ending_style):
    return f"""[학생 정보]
- 이름: {name}
- 1. 선택 작품: {q1}
- 2. 관점 주제(질문): {q2}
- 3. 선정 이유: {q3}
- 4. 현대사회 사례: {q4}
- 5. 화자 태도 생각: {q5}
- 6. 극복 노력: {q6}
- 7. 성장 부분: {q7}

[지정된 6단계 종결어미 형태]
{ending_style}
※ 물결표(~) 부분에 둥근 따옴표(‘ ’)로 감싼 구체적인 의문문 형식의 후속 탐구 질문을 자연스럽게 생성하여 넣으십시오."""

# 7. Call API with Retry
def call_generation_api(name, q1, q2, q3, q4, q5, q6, q7, ending_style):
    prompt = create_student_prompt(name, q1, q2, q3, q4, q5, q6, q7, ending_style)
    last_error = ""
    for attempt in range(3):
        try:
            # We configure model system instruction
            model_session = genai.GenerativeModel(
                model_name=CONFIG["MODEL_NAME"],
                system_instruction=SYSTEM_INSTRUCTION
            )
            response = model_session.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.4,
                    "response_mime_type": "application/json",
                    "response_schema": {
                        "type": "OBJECT",
                        "properties": {
                            "seteuk": {
                                "type": "STRING",
                                "description": "규격에 맞춘 완결된 세특 본문"
                            }
                        },
                        "required": ["seteuk"]
                    }
                }
            )
            res_json = json.loads(response.text.strip())
            seteuk_text = res_json.get("seteuk", "").strip()
            if seteuk_text and len(seteuk_text) > 30:
                return seteuk_text
            last_error = "응답이 비어있거나 너무 짧습니다."
        except Exception as e:
            last_error = str(e)
            time.sleep(2)
    raise Exception(f"세특 생성 실패 (3회 시도): {last_error}")

# 8. Main Execution Loop
def main():
    input_file = r"D:\OneDrive - 경상남도교육청\바탕 화면\2026년 2학년 국어 2학년 문학 자기평가서 제출 (2-4반)_20260707_083301.xlsx"
    output_file = r"D:\OneDrive - 경상남도교육청\바탕 화면\2026년 2학년 국어 2학년 문학 자기평가서 제출 (2-4반)_세특완료.xlsx"
    
    print(f"📖 엑셀 파일 로딩 중: {os.path.basename(input_file)}")
    df = pd.read_excel(input_file)
    
    # 0. Clean names & student IDs
    df_clean = df.dropna(subset=['현재학번', '이름']).copy()
    df_clean['현재학번'] = df_clean['현재학번'].astype(int)
    df_clean = df_clean.sort_values(by='현재학번')
    
    # 1. Initialize output columns if they don't exist
    if '세특 초안 (AI)' not in df_clean.columns:
        df_clean['세특 초안 (AI)'] = ""
    if '총 글자수/바이트' not in df_clean.columns:
        df_clean['총 글자수/바이트'] = ""
    if '처리 상태' not in df_clean.columns:
        df_clean['처리 상태'] = "대기"
        
    df_clean['세특 초안 (AI)'] = df_clean['세특 초안 (AI)'].fillna("")
    df_clean['총 글자수/바이트'] = df_clean['총 글자수/바이트'].fillna("")
    df_clean['처리 상태'] = df_clean['처리 상태'].fillna("대기")

    # Reset processed status to re-run and verify V8.3 quality
    df_clean['세특 초안 (AI)'] = ""
    df_clean['총 글자수/바이트'] = ""
    df_clean['처리 상태'] = "대기"

    pending_students = df_clean[df_clean['처리 상태'] != "완료"]
    total_pending = len(pending_students)
    
    print(f"🎯 총 {total_pending}명의 학생 대상 V8.3 토큰 최적화 생성 시작.\n")
    
    ending_styles = [
        "~라는 물음으로 탐구를 확장하려는 태도가 돋보임",
        "~라는 물음을 향한 지적 호기심을 드러냄",
        "~라는 물음을 후속 탐구 과제로 제시함",
        "~라는 물음을 스스로 탐색해보려는 학문적 열의를 보임",
        "~라는 물음으로 사고를 확장해가는 모습이 인상적임",
        "~라는 물음을 품고 심화 탐구를 계획함"
    ]
    
    processed_count = 0
    
    for idx, row in df_clean.iterrows():
        name = row['이름']
        hakbun = row['현재학번']
        
        # Extract inputs safely using keywords
        def get_col_val(keywords, default_col):
            if default_col in df_clean.columns:
                return row[default_col]
            for col in df_clean.columns:
                if all(kw in col for kw in keywords):
                    return row[col]
            for col in df_clean.columns:
                if any(kw in col for kw in keywords):
                    return row[col]
            return ""

        q1 = get_col_val(['작품', '저자'], '작품 제목과 저자명을 써주세요 (예시) 상춘곡(정철)')
        q2 = get_col_val(['관점', '질문'], '관점 주제(질문)를 써주세요.')
        q3 = get_col_val(['선정', '이유'], '관점 주제(질문)를 선정한 이유를 써주세요.')
        q4 = get_col_val(['현대사회', '사례'], '작품의 시적 상황과  유사한 현대사회의 구체적인 사례를 써주세요. [300자 이내]')
        q5 = get_col_val(['태도', '생각'], '현대사회의 사례를 바탕으로 고전시가에 나타난 화자의 태도에 대한 자신의 생각을 써주세요. [300자 이내]')
        q6 = get_col_val(['어려움', '보완'], '고전작품을 현대적 관점에서 비평할 때 어떤 어려움이 있었고,그것을 어떻게 해결하고 보완하였는지? [300자 이내]')
        q7 = get_col_val(['배운점', '성장'], '고전작품을 현대적 관점에서 비평하면서 배운점과  본인이 성장한 부분은? [200자 이내]')
        
        clean_q1 = str(q1).replace('\n', ' ').strip() if not pd.isna(q1) else ""
        
        # Skip if missing fundamental text
        if not clean_q1 or clean_q1 in ['까먹었습니다.', '까먹었습니다', '없음', '모름', '모르겠습니다']:
            print(f"⚠️ [{hakbun} {name}] 필수 데이터(작품명) 누락 또는 플레이스홀더 입력으로 건너뜁니다.")
            df_clean.at[idx, '세특 초안 (AI)'] = "[확인필요: 기본데이터 누락]"
            df_clean.at[idx, '처리 상태'] = "건너뜀"
            continue
            
        ending_style = ending_styles[idx % len(ending_styles)]
        
        print(f"🤖 [{hakbun} {name}] 세특 생성 중... ({processed_count + 1}명째)")
        try:
            seteuk = call_generation_api(name, q1, q2, q3, q4, q5, q6, q7, ending_style)
            
            # Post process formatting
            seteuk = convert_to_korean_quotes(seteuk.replace("**", "").replace("`", "").strip())
            byte_len = calculate_byte(seteuk)
            char_len = len(seteuk)
            
            df_clean.at[idx, '세특 초안 (AI)'] = seteuk
            df_clean.at[idx, '총 글자수/바이트'] = f"{char_len}자 ({byte_len}B)"
            
            if byte_len < CONFIG["BYTE_MIN"] or byte_len > CONFIG["BYTE_MAX"]:
                df_clean.at[idx, '처리 상태'] = "확인필요"
                print(f"✅ [{hakbun} {name}] 완료 [확인필요: 분량 {byte_len}B]")
            else:
                df_clean.at[idx, '처리 상태'] = "완료"
                print(f"✅ [{hakbun} {name}] 완료 [정상 {byte_len}B]")
                
        except Exception as e:
            print(f"❌ [{hakbun} {name}] 실패: {str(e)}")
            df_clean.at[idx, '세특 초안 (AI)'] = f"오류 발생: {str(e)}"
            df_clean.at[idx, '처리 상태'] = "실패"
            
        processed_count += 1
        
        # Intermediate Save & Batch Delay
        if processed_count % CONFIG["BATCH_SIZE"] == 0 or idx == df_clean.index[-1]:
            df_clean.to_excel(output_file, index=False)
            print(f"💾 중간 저장 완료: {os.path.basename(output_file)}")
            if idx != df_clean.index[-1]:
                print(f"💤 API 제한 방지를 위해 {CONFIG['DELAY_TIME']}초간 대기합니다...\n")
                time.sleep(CONFIG["DELAY_TIME"])
                
    # Final save
    df_clean.to_excel(output_file, index=False)
    print(f"\n🎉 전체 처리 완료! 최종 파일 저장 경로: {output_file}")
    
    # Send Telegram summary
    val_counts = df_clean['처리 상태'].value_counts()
    completed = val_counts.get('완료', 0)
    to_verify = val_counts.get('확인필요', 0)
    skipped = val_counts.get('건너뜀', 0)
    failed = val_counts.get('실패', 0)
    summary_text = (
        f"📝 [문학 세특 자동화 V8.3 완료 보고]\n\n"
        f"- 대상 학급: 2-4반\n"
        f"- 완료(정상 규격): {completed}명\n"
        f"- 확인필요(분량 미달 등): {to_verify}명\n"
        f"- 건너뜀(불성실 답변): {skipped}명\n"
        f"- 실패: {failed}명\n\n"
        f"모든 대기 학생에 대한 세특 V8.3 토큰 최적화 생성이 완료되었습니다."
    )
    send_telegram_message(summary_text)

if __name__ == "__main__":
    main()
