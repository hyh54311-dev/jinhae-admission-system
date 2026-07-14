import os
import sys
import io
import time
import datetime
import math
import schedule
import requests
from dotenv import load_dotenv

load_dotenv()

# Windows 콘솔 출력 UTF-8 설정
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding.lower() != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

# ----------------- 사용자 설정 ----------------- #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "admission_news.log")
FOLDER_PATH = os.path.join(BASE_DIR, "대입정보 TXT")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.1-flash-lite"

TELEGRAM_TOKEN = "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY"
TELEGRAM_CHAT_ID = "8518409134"

AUDIO_INSTRUCTIONS = """[오디오 리뷰 생성 지침]
당신들은 교육 및 입시 전략 분야의 베테랑 전문가들입니다. 제가 업로드한 최신 대입 정보 리포트를 바탕으로, 학부모와 교사들에게 실질적인 도움이 되는 심층 오디오 리뷰를 생성해 주세요.

분량 및 밀도: 시간에 구애받지 말고 텍스트의 모든 입시 정책 변화와 대학별 상세 정보를 충실히 반영하여 대화를 나눠주세요. 단순 요약이 아닌 전문가적 통찰이 필요합니다.
대학별 상세 분석 필수: 리포트에 언급된 주요 대학들의 모집 인원 변화나 전형 방식의 미세한 차이를 반드시 상세히 다뤄주세요.
전략적 시사점: 정책 변화가 실제 수험생들의 지원 패턴에 어떤 영향을 미칠지 구체적으로 분석해 주세요.
한국어로 만드시오.

---
"""
# ----------------------------------------------- #

def log_message(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    full_message = f"[{timestamp}] [Admission] {message}"
    print(full_message)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_message + "\n")
    except Exception as e:
        print(f"로그 기록 실패: {e}")

def get_month_week(dt):
    first_day = dt.replace(day=1)
    first_weekday = first_day.weekday()
    adjusted_dom = dt.day + first_weekday
    week_num = int(math.ceil(adjusted_dom / 7.0))
    return dt.month, week_num

def send_telegram_alert(file_name, file_path, prompt_text):
    import urllib.request
    import urllib.parse
    import ssl
    
    tokens = [
        "8799464748:AAHD2ERa9aEnqn6Dtr7SNDjDOf9KGFEMziU", # Assistant Bot
        "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY"  # Macro News Bot
    ]
    chat_id = "8518409134"
    
    text = f"📝 [대입 정보 텍스트 추출 완료]\n\n이번 주 대입 정보 파일({file_name}) 추출 및 검증이 완료되었습니다.\n직접 NotebookLM에 업로드하여 오디오 리뷰를 생성해 주세요."
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for token in tokens:
        try:
            telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
            
            # 1. Alert Message
            data = urllib.parse.urlencode({'chat_id': chat_id, 'text': text}).encode('utf-8')
            req = urllib.request.Request(telegram_url, data=data)
            urllib.request.urlopen(req, context=ctx)

            # 2. Master Prompt
            data_p = urllib.parse.urlencode({'chat_id': chat_id, 'text': prompt_text}).encode('utf-8')
            req_p = urllib.request.Request(telegram_url, data=data_p)
            urllib.request.urlopen(req_p, context=ctx)
            
            log_message(f"텔레그램 대입 정보 알림 전송 완료! (Bot ID: {token.split(':')[0]})")
            return
        except Exception as e:
            log_message(f"텔레그램 전송 실패 (Bot ID: {token.split(':')[0]}): {e}")
    
    log_message("모든 텔레그램 봇 전송에 실패했습니다.")

def _call_gemini_api(prompt, model_name, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"googleSearch": {}}],
        "generationConfig": {"maxOutputTokens": 65536, "temperature": 0.2}
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=150)
        response.raise_for_status()
        json_data = response.json()
        candidates = json_data.get("candidates", [])
        if not candidates: return None
        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join([part.get("text", "") for part in parts])
    except Exception as e:
        log_message(f"API 호출 오류: {e}")
        return None

def verify_report(content, api_key, model_name, now):
    log_message("🔍 [Harness] 3단계 무결성 검증을 시작합니다...")
    
    # 1. 연도 일관성 체크
    p1 = (f"당신은 입시 리포트 검증 전문가입니다. 현재 날짜는 {now.strftime('%Y-%m-%d')}이며, 주요 타겟은 '2027학년도' 대입입니다. 리포트에 연도 오류가 있는지 확인하고 [PASS] 혹은 수정 가이드를 작성하세요.\n\n{content}")
    # 2. 수치 체크
    p2 = (f"리포트의 주요 대학 모집 인원 및 전형 수치(숫자)를 구글 검색으로 검증하세요. 2027학년도 대입 시행계획 기준입니다. [PASS] 혹은 오류 수정을 알려주세요.\n\n{content}")
    # 3. 지침 준수 여부
    p3 = (f"리포트가 입시 마인드셋과 주간 체크포인트를 포함하고 있는지 확인하세요. [PASS] 혹은 [MISSING]을 표시하세요.\n\n{content}")

    results = []
    for i, p in enumerate([p1, p2, p3], 1):
        res = _call_gemini_api(p, model_name, api_key)
        results.append(res)
        if "[PASS]" not in (res or ""): log_message(f"검증 {i}단계 문제 발견.")
    
    if all("[PASS]" in (r or "") for r in results): return True, content
    
    fix_prompt = (f"다음 리포트와 검증 결과를 바탕으로 최종 보정된 리포트를 작성해 주세요.\n\n원본:\n{content}\n\n검증 피드백:\n" + "\n".join(results))
    return False, _call_gemini_api(fix_prompt, model_name, api_key)

def generate_admission_news(is_force=False):
    now = datetime.datetime.now()
    month, week = get_month_week(now)
    log_message(f"입시 정보 생성 시작: {month}월 {week}주차")
    
    prompt1 = (
        f"당신은 대한민국 최고의 입시 전문가입니다. 현재 날짜는 {now.strftime('%Y-%m-%d')}입니다. "
        f"최근 1주일간의 교육부(MOE), 대교협(KCUE) 및 대학들의 핵심 입시 정책 변화를 분석해 주세요. "
        f"2027/2028학년도 무전공, 첨단학과 정원 등 주요 변화를 다루고 정책 파트까지만 작성해 주세요."
    )
    content1 = _call_gemini_api(prompt1, MODEL_NAME, GEMINI_API_KEY)
    if not content1: return

    prompt2 = (f"앞서 작성한 정책 배경에 이어, 수도권 주요 대학(서연고 포함 15개대)의 최신 입학처 공지사항과 전문가 전략을 작성해 주세요. 마지막엔 [입시 마인드셋]과 [주간 체크포인트 3가지]를 포함해 주세요.")
    content2 = _call_gemini_api(prompt2, MODEL_NAME, GEMINI_API_KEY)
    
    content = content1 + "\n\n---\n\n" + (content2 if content2 else "")
    _, final_content = verify_report(content, GEMINI_API_KEY, MODEL_NAME, now)
    
    final_with_instr = AUDIO_INSTRUCTIONS + (final_content if final_content else content)
    
    os.makedirs(FOLDER_PATH, exist_ok=True)
    file_name = f"{now.strftime('%Y%m%d')}_Admission_Info.md"
    file_path = os.path.join(FOLDER_PATH, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_with_instr)
    
    master_prompt = (
        "당신들은 대한민국 최고의 대입 전략 전문가입니다. 업로드된 리포트를 바탕으로 교사들을 위한 고밀도 오디오 브리핑을 생성해 주세요. "
        "분량에 구애받지 말고 대학별 미세한 차이와 전략적 시사점을 심도 있게 다뤄야 합니다. 한국어로 진행하세요."
    )
    send_telegram_alert(file_name, file_path, master_prompt)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "run_now":
        generate_admission_news(is_force=True)
        return
    schedule.every().wednesday.at("11:00").do(generate_admission_news)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
