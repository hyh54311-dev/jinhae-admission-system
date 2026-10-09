import os
import sys
import io
import json
import datetime
import argparse
import time
import re
import requests

# Windows 콘솔 UTF-8 강제 설정 (이모지 및 한글 깨짐 방지)
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(CURRENT_DIR, ".env")
LOG_PATH = os.path.join(CURRENT_DIR, "weekend_news_exec.log")
REPORTS_DIR = os.path.join(CURRENT_DIR, "reports")

try:
    from dotenv import load_dotenv
    if os.path.exists(ENV_PATH):
        load_dotenv(ENV_PATH)
    else:
        load_dotenv()
except ImportError:
    pass

# ----------------- 환경 변수 설정 (GitHub Secrets 및 .env) ----------------- #
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

PRIMARY_MODEL = "gemini-flash-latest"
FALLBACK_MODELS = ["gemini-flash-lite-latest", "gemini-pro-latest"]
# ------------------------------------------------------------------------- #

def mask_sensitive_info(text):
    """C2: API 키 및 봇 토큰 로그 노출 차단 마스킹 함수"""
    if not text:
        return ""
    masked = str(text)
    if GEMINI_API_KEY and len(GEMINI_API_KEY) > 6:
        masked = masked.replace(GEMINI_API_KEY, "***GEMINI_KEY***")
    if TELEGRAM_TOKEN and len(TELEGRAM_TOKEN) > 6:
        masked = masked.replace(TELEGRAM_TOKEN, "***TELEGRAM_TOKEN***")
    return masked

def log_message(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    clean_msg = mask_sensitive_info(message)
    log_line = f"[{timestamp}] {clean_msg}"
    print(log_line, flush=True)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except Exception:
        pass

def get_recent_7days_range(dt):
    """
    토요일/주말 실행 시 미래 일요일이 포함되지 않도록
    오늘(dt) 기준 실제 최근 7일(dt - 6일 ~ dt) 범위를 반환
    """
    start_dt = dt - datetime.timedelta(days=6)
    return (
        start_dt.strftime("%Y년 %m월 %d일"),
        dt.strftime("%Y년 %m월 %d일"),
        start_dt.strftime("%Y-%m-%d"),
        dt.strftime("%Y-%m-%d")
    )

def sanitize_to_telegram_html(text):
    """
    M7 & N4: 텔레그램 공식 HTML 모드(parse_mode: 'HTML') 변환기
    - 코드 블록(`...`) 선행 추출 및 플레이스홀더 보호 (내부 별표/특수기호 오염 방지)
    - 줄머리 불릿(* 또는 -)을 유니코드 불릿(• )으로 선행 변환 (이탤릭 오인 방지)
    - 볼드+이탤릭(***텍스트***) 선행 변환으로 태그 엇갈림 원천 차단
    - HTML 엔티티 이스케이프 및 볼드, 이탤릭, 링크 변환 후 코드 블록 복원
    """
    if not text:
        return ""

    # 1. 백틱 코드 블록(`...`) 선행 추출 및 플레이스홀더 치환
    code_tokens = {}
    def repl_code(m):
        idx = len(code_tokens)
        token = f"\x00CODE_{idx}\x00"
        escaped_code = m.group(1).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        code_tokens[token] = f"<code>{escaped_code}</code>"
        return token
    text = re.sub(r'`([^`\n]+)`', repl_code, text)

    # 2. HTML 기본 엔티티 이스케이프 (&, <, >)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")

    # 3. 줄머리 마크다운 불릿(* 또는 -)을 유니코드 점(• )으로 변환 (들여쓰기 지원, 이탤릭 정규식 오작동 차단)
    text = re.sub(r'(?m)^(\s*)[\*\-]\s+', r'\1• ', text)

    # 4. 마크다운 헤더 (# 제목, ## 제목, ### 제목) -> <b>제목</b>
    def repl_header(match):
        return f"\n<b>{match.group(2).strip()}</b>\n"
    text = re.sub(r'(?m)^(\#{1,4})\s+(.+)$', repl_header, text)

    # 5. 볼드+이탤릭 (***텍스트***) 선행 처리 (태그 엇갈림 <b><i>...</b></i> 원천 차단)
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)

    # 6. 마크다운 볼드 (**텍스트**) -> <b>텍스트</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)

    # 7. 마크다운 이탤릭 (*텍스트*) -> <i>텍스트</i>
    text = re.sub(r'(?<!\*)\*([^\*\n]+?)\*(?!\*)', r'<i>\1</i>', text)

    # 8. 마크다운 링크 ([텍스트](URL)) -> <a href="URL">텍스트</a>
    text = re.sub(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)', r'<a href="\2">\1</a>', text)

    # 9. 코드 블록 토큰 복원
    for token, code_html in code_tokens.items():
        text = text.replace(token, code_html)

    return text.strip()

def split_telegram_message(text, max_length=3800):
    """
    M6: 텔레그램 메시지 길이 제한(4,096자)을 대비한 3단계 안전 분할 엔진.
    섹션(---) -> 단락(\n\n) -> 줄바꿈(\n) -> 강제 절단 단계 적용으로
    단일 단락이 3,800자를 초과해도 결코 유실되지 않도록 보장합니다.
    """
    if not text:
        return []
    if len(text) <= max_length:
        return [text]
        
    # 1차 분할: 섹션 구분선(---) 또는 마크다운 헤더(###)
    sections = re.split(r'(\n---\n|\n(?=###\s))', text)
    chunks = []
    current_chunk = ""
    
    for sec in sections:
        if len(current_chunk) + len(sec) <= max_length:
            current_chunk += sec
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = ""
            if len(sec) <= max_length:
                current_chunk = sec
            else:
                # 2차 분할: 단락(\n\n)
                paragraphs = sec.split("\n\n")
                for p in paragraphs:
                    if len(current_chunk) + len(p) + 2 <= max_length:
                        current_chunk += ("\n\n" if current_chunk else "") + p
                    else:
                        if current_chunk.strip():
                            chunks.append(current_chunk.strip())
                            current_chunk = ""
                        if len(p) <= max_length:
                            current_chunk = p
                        else:
                            # 3차 분할: 줄바꿈(\n)
                            lines = p.split("\n")
                            for line in lines:
                                if len(current_chunk) + len(line) + 1 <= max_length:
                                    current_chunk += ("\n" if current_chunk else "") + line
                                else:
                                    if current_chunk.strip():
                                        chunks.append(current_chunk.strip())
                                        current_chunk = ""
                                    # 4차 최후 방어: 단일 라인이 max_length 초과 시 강제 슬라이싱
                                    while len(line) > max_length:
                                        chunks.append(line[:max_length])
                                        line = line[max_length:]
                                    current_chunk = line
                        
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
        
    # 복수 청크인 경우 상단에 파트 번호 부착
    if len(chunks) > 1:
        total = len(chunks)
        return [f"📑 [파트 {i+1}/{total}]\n\n{chunk}" for i, chunk in enumerate(chunks)]
    return chunks

def send_telegram_message(raw_text, test_mode=False):
    """
    M7 & N6: 텔레그램 발송 함수 (HTML 모드 적용)
    - 400 Bad Request 발생 시 3회 재시도 낭비 없이 즉시 평문 폴백 1회 시도
    - 429 Rate Limit 및 서버 일시 오류 시 지수 백오프 적용
    - 최종 발송 성공 여부, 성공 파트 수, 전체 파트 수 반환 (all_sent, success_count, total_count)
    """
    if test_mode:
        log_message("[TEST MODE] 텔레그램 실제 전송을 생략하고 표준 출력(stdout) 및 로그에 리포트를 덤프합니다.")
        preview_text = "\n" + "="*50 + " [TELEGRAM HTML PREVIEW] " + "="*50 + "\n" + raw_text + "\n" + "="*126 + "\n"
        print(preview_text, flush=True)
        try:
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(preview_text + "\n")
        except Exception:
            pass
        return True, 1, 1

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        log_message("오류: 텔레그램 토큰 또는 채팅 ID가 설정되지 않아 발송을 중단합니다.")
        return False, 0, 0
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    chunks = split_telegram_message(raw_text, max_length=3800)
    success_count = 0
    
    for i, part in enumerate(chunks):
        html_part = sanitize_to_telegram_html(part)
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': html_part,
            'parse_mode': 'HTML'
        }
        
        part_success = False
        for attempt in range(1, 4):
            try:
                resp = requests.post(url, json=payload, timeout=30)
                if resp.status_code == 200:
                    log_message(f"텔레그램 전송 성공 (파트 {i+1}/{len(chunks)})")
                    part_success = True
                    break
                elif resp.status_code == 400:
                    # N6: 400 에러는 서식 결함이므로 즉시 평문 폴백 1회 시도 후 break
                    log_message(f"⚠️ 텔레그램 400 Bad Request (파트 {i+1}/{len(chunks)}): {resp.text[:120]}")
                    log_message(f"파트 {i+1} 평문 폴백 전송 시도...")
                    plain_payload = {
                        'chat_id': TELEGRAM_CHAT_ID,
                        'text': part
                    }
                    fallback_resp = requests.post(url, json=plain_payload, timeout=30)
                    if fallback_resp.status_code == 200:
                        log_message(f"파트 {i+1} 평문 전송 성공!")
                        part_success = True
                    else:
                        log_message(f"파트 {i+1} 평문 전송마저 실패 (Status {fallback_resp.status_code}): {fallback_resp.text[:120]}")
                    break
                elif resp.status_code == 429:
                    retry_after = 3
                    try:
                        retry_after = resp.json().get("parameters", {}).get("retry_after", 3)
                    except Exception:
                        pass
                    log_message(f"텔레그램 429 초과: {retry_after}초 대기 후 재시도 (시도 {attempt}/3)...")
                    time.sleep(retry_after)
                else:
                    log_message(f"텔레그램 전송 실패 (Status {resp.status_code}, 파트 {i+1}/{len(chunks)}, 시도 {attempt}/3): {resp.text[:120]}")
                    time.sleep(1.5)
            except Exception as e:
                log_message(f"텔레그램 통신 예외 발생 (파트 {i+1}, 시도 {attempt}/3): {e}")
                time.sleep(1.5)

        if part_success:
            success_count += 1
        else:
            log_message(f"❌ 파트 {i+1}/{len(chunks)} 전송 최종 실패")
            break  # 파트 전송 실패 시 이후 파트 전송 중단 (순서 및 정합성 보장)

        time.sleep(1.5)  # 파트 순서 역전 방지 대기

    all_sent = (success_count == len(chunks))
    return all_sent, success_count, len(chunks)

def get_macro_system_instruction(current_year, current_month_str):
    """C3: 현재 연도 및 월 기반 동적 시스템 인스트럭션"""
    return (
        f"당신은 글로벌 거시경제(Macroeconomics) 및 미래 신산업 동향을 정밀 분석하는 수석 경제학자이자 금융 에디터입니다.\n"
        f"현재 분석 기준 시점은 **{current_year}년 {current_month_str}**입니다.\n"
        f"당신의 모든 브리핑은 엄격한 팩트와 최신 공식 통계에 근거해야 하며, 아래의 [절대 가드레일]을 100% 준수해야 합니다.\n\n"
        f"[절대 가드레일 1: 당해 시점({current_year}년 {current_month_str}) 실측 팩트 앵커링 및 과거 연도 혼입 엄금]\n"
        f"- 검색된 뉴스의 실제 발행 연도와 공식 발표 일자를 반드시 확인하십시오.\n"
        f"- 과거 연도(2024년, 2025년 등)의 과거 지표가 현재 {current_year}년의 최신 지표로 둔갑하거나 섞여 들어가는 타임슬립 왜곡을 절대 금지합니다.\n"
        f"- 본문에 언급되는 경제 지표는 반드시 {current_year}년 당해 주간에 공식 발표된 수치여야 하며, 발표 기관과 공식 발표 일자를 명확히 적시하십시오.\n\n"
        f"[절대 가드레일 2: 통화정책 및 경제 지표의 객관적 서술]\n"
        f"- 중앙은행(연준, 한국은행, ECB, BOJ 등)의 기준금리 및 통화정책은 확인된 공식 성명서와 실제 결정치에 기반하여 객관적으로 서술하십시오.\n"
        f"- 지표 결과에 따라 무조건 '금리 인상 베팅'이나 '무조건 빅컷'과 같이 단편적으로 비약하지 말고, 금리 동결, 점진적 인하, 인하 속도 조절 등 실제 시장과 당국의 공식 입장을 균형 있게 서술하십시오.\n\n"
        f"[절대 가드레일 3: 수치 정확도 및 자의적 창작 금지 (Zero Extrapolation)]\n"
        f"- 웹 검색에서 명확히 확인되지 않는 구체적 통계 수치를 자의적으로 지어내거나 추정치를 실측치로 단정하지 마십시오.\n"
        f"- 공식 기관의 공식 데이터와 민간 금융기관의 자체 전망치를 엄격히 분리하여 주체를 명시하십시오.\n\n"
        f"[절대 가드레일 4: 시계열 및 지정학적 사건 팩트 검증]\n"
        f"- 주요 국제 분쟁(우크라이나 전쟁 2022년 2월 발발, 가자지구 분쟁 2023년 10월 발발 등)의 경과 시점과 현황은 {current_year}년 현재 시점에 부합하게 수학적으로 정확히 기술하십시오.\n\n"
        f"[절대 가드레일 5: 본문-요약 간 100% 논리적 정합성 및 전문 한글화]\n"
        f"- 본문 7대 이슈의 진단과 하단 [글로벌 마켓 뷰] 및 [한국의 대응 전략]의 결론은 완벽히 동일한 인과관계와 방향성을 유지해야 합니다."
    )

def call_gemini_api(prompt, system_instruction=None, enable_search=True, model_name=PRIMARY_MODEL):
    """
    C2: URL 쿼리 파라미터 대신 headers에 API 키 전달 (로그 노출 차단)
    개선 1: finishReason 검사 (MAX_TOKENS, SAFETY 시 경고 및 폴백)
    개선 2: 응답 텍스트 비어있을 시 2초 대기 후 재시도
    """
    if not GEMINI_API_KEY:
        log_message("오류: GEMINI_API_KEY가 설정되지 않았습니다.")
        return None
        
    models_to_try = [model_name] + [m for m in FALLBACK_MODELS if m != model_name]
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 65536,
            "temperature": 0.15
        }
    }
    
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        
    if enable_search:
        payload["tools"] = [{"googleSearch": {}}]
        
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    for current_model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent"
        for attempt in range(1, 4):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=(20, 120))
                if response.status_code == 200:
                    json_data = response.json()
                    candidates = json_data.get("candidates", [])
                    if candidates:
                        first_cand = candidates[0]
                        finish_reason = first_cand.get("finishReason", "")
                        
                        if finish_reason in ["SAFETY", "RECITATION", "BLOCKLIST"]:
                            log_message(f"⚠️ Gemini 콘텐츠 안전 필터 차단 (Reason: {finish_reason}, Model: {current_model})")
                            break  # 다른 모델 시도
                        elif finish_reason == "MAX_TOKENS":
                            log_message(f"⚠️ Gemini 토큰 한도 초과 절단 경고 (Model: {current_model})")

                        parts = first_cand.get("content", {}).get("parts", [])
                        result_text = "".join([p.get("text", "") for p in parts if "text" in p])
                        if result_text.strip():
                            log_message(f"Gemini API 호출 성공 (Model: {current_model}, Search: {enable_search})")
                            return result_text
                    
                    log_message(f"주의: {current_model} 응답 텍스트 비어있음. 2초 대기 후 재시도합니다.")
                    time.sleep(2)
                elif response.status_code in [400, 401, 403, 404]:
                    log_message(f"클라이언트 API 에러 ({current_model}, Status {response.status_code}): {response.text[:150]}")
                    break  # 치명적 인증/요청 에러는 재시도 없이 다음 모델로 이동
                else:
                    log_message(f"API 에러 ({current_model}, Status {response.status_code}): {response.text[:150]}")
                    if response.status_code in [429, 503]:
                        time.sleep(2 ** attempt)
            except Exception as e:
                log_message(f"예외 발생 ({current_model}, 시도 {attempt}/3): {e}")
                time.sleep(2 ** attempt)
                
    log_message("모든 모델 및 재시도 실패")
    return None

def generate_weekend_news(test_mode=False):
    """안티그래비티 외부 독립 실행 시 3단계 Gemini 파이프라인 (팩트 풀 주입 지원)"""
    try:
        kst = datetime.timezone(datetime.timedelta(hours=9))
        now = datetime.datetime.now(datetime.timezone.utc).astimezone(kst)
        current_year = now.year
        month_str = f"{now.month}월"
        month_en = now.strftime("%B")
        today_str_full = f"{now.year}년 {now.month:02d}월 {now.day:02d}일"
        weekday = now.weekday()
        weekday_str = ["월", "화", "수", "목", "금", "토", "일"][weekday]
        
        week_start_str, week_end_str, _, _ = get_recent_7days_range(now)
        
        log_message(f"주말 글로벌 경제 뉴스 생성 시작 (기준일: {today_str_full}, 대상 주간: {week_start_str} ~ {week_end_str})")

        # 신산업 로테이션 (연중 주차 기준)
        industries = [
            "신재생 에너지", "AI", "우주 산업", "전기차/자율주행", "SMR",
            "차세대 바이오/디지털 헬스케어", "로보틱스/휴머노이드", "양자 컴퓨팅", "차세대 반도체 및 스마트 팩토리"
        ]
        week_of_year = now.isocalendar()[1]
        target_new_industry = industries[week_of_year % len(industries)]
        log_message(f"이번 주 신산업 심층 포커스 주제: {target_new_industry} (연중 {week_of_year}주차)")

        system_instruction = get_macro_system_instruction(current_year, month_str)

        # 팩트 풀 파일 주입 여부 확인
        fact_pool_md_path = os.path.join(CURRENT_DIR, "weekend_macro_fact_pool.md")
        fact_context = ""
        if os.path.exists(fact_pool_md_path):
            try:
                with open(fact_pool_md_path, "r", encoding="utf-8") as f:
                    fact_context = f"\n\n[최근 3주간 공신력 언론사 실측 팩트 풀]:\n" + f.read()[:8000]
                log_message("로컬 3주 팩트 풀 데이터를 프롬프트 컨텍스트에 주입했습니다.")
            except Exception:
                pass

        # ------------------- [Pass 1: 초안 작성 (Draft Agent)] ------------------- #
        log_message("Pass 1: [초안 작성 에이전트] 실시간 검색 그라운딩 기반 브리핑 초안 생성 중...")
        pass1_prompt = (
            f"당신은 글로벌 AI 거시경제 분석 전문가입니다. 현재 실제 날짜는 **{today_str_full}({weekday_str}요일)**입니다.\n"
            f"이번 주 분석 대상 기간은 **{week_start_str}부터 {week_end_str}까지({current_year}년 최근 7일)**입니다.\n\n"
            f"아래 제공된 3주 실측 팩트 풀과 Google Search를 사용하여 위 기간에 발표된 거시경제 핵심 동향 중 "
            f"**가장 중요한 7가지 글로벌 이슈**를 엄선하여 작성해 주세요.{fact_context}\n\n"
            f"[필수 검색 및 작성 지침]:\n"
            f"1. 검색 쿼리를 생성할 때 반드시 연도 및 월 키워드 **'{current_year}년 {month_str}'** 또는 **'{month_en} {current_year}'**를 포함하여 검색하십시오. "
            f"(예: '{current_year}년 {month_str} 경제 지표', '{month_en} {current_year} economic data', 'FOMC {current_year}')\n"
            f"2. 과거 연도(2024, 2025 등)의 기사를 {current_year}년 기사로 혼동하지 않도록 기사의 발표 일자를 정밀 확인하십시오.\n"
            f"3. 확인된 공식 발표치만 인용하고, 확인되지 않은 숫자는 창작하지 마십시오.\n"
            f"4. 각국 중앙은행의 정책 결정 및 통화정책 기조는 확인된 공식 회의 결과와 성명서에 기반하여 객관적으로 작성하십시오.\n\n"
            f"이와 별도로, 이번 주 주말엔 **[신산업 심층 포커스]** 섹션에 **'{target_new_industry}'**를 심층 분석해 주세요.\n\n"
            f"각 이슈 분석 구성:\n"
            f"- 요약/데이터: (발표일자, 출처 기관, 핵심 수치 명시)\n"
            f"- 지정학적 맥락: (관련국 정책 및 글로벌 파급효과)\n"
            f"- 시나리오 분석: (긍정/부정 시나리오)\n"
            f"- 한국 시장 영향: (국내 증시, 환율, 주요 수출 기간산업 영향)\n\n"
            f"마지막 섹션 구성 (본문 7대 이슈와 100% 논리적으로 일치해야 함):\n"
            f"- [글로벌 마켓 뷰]: 이번 주 글로벌 거시경제 흐름 총평\n"
            f"- [한국의 대응 전략]: 국내 투자자 및 기업 관점의 대응 전략 3가지"
        )
        
        draft_content = call_gemini_api(
            pass1_prompt, 
            system_instruction=system_instruction, 
            enable_search=True, 
            model_name=PRIMARY_MODEL
        )
        if not draft_content:
            log_message("Pass 1 초안 생성 실패")
            return False

        # ------------------- [Pass 2: 하위 전문 에이전트 1차 검색 검증] ------------------- #
        log_message("Pass 2: [하위 전문 검증 에이전트] 실시간 검색 기반 팩트체크·통계수치·연도 정합성 1차 정밀 대조 중...")
        pass2_prompt = (
            f"당신은 [하위 전문 팩트체크 및 거시 통계 검증 에이전트]입니다.\n"
            f"아래 [Pass 1 초안]의 모든 사실관계, 발표 날짜, 통화정책 결정, 통계 수치를 Google Search를 활용하여 엄격히 교차 대조하고 수정한 [1차 수정본]을 작성해 주세요.\n\n"
            f"[현재 기준 일자]: {today_str_full} (주간 대상: {week_start_str} ~ {week_end_str})\n\n"
            f"[Pass 1 초안]:\n{draft_content}\n\n"
            f"[하위 에이전트 1차 필수 검증 및 수정 지침]:\n"
            f"1. **연도 및 일자 교차 검증**: 초안의 각 이슈가 실제로 **{current_year}년 {month_str}**에 공식 발표된 내용인지 Google Search로 확인하십시오. 만약 과거 뉴스가 섞여 있다면 즉시 {current_year}년 {month_str} 실제 발표된 거시경제 데이터로 전면 교체하십시오.\n"
            f"2. **통계 수치 정확성 검증**: 미국 소매판매, 실업수당 청구건수, CPI, 산업생산 등 공식 발표치의 오기 여부를 검색하여 교정하십시오.\n"
            f"3. **주체 구분 검증**: 정부 공식 목표/실측치와 민간 투자은행(IB)의 자체 추정치가 명확히 구분되었는지 확인하십시오.\n"
            f"4. **시계열 산술 검증**: 주요 지정학적 사건의 발생일 기준 경과 시점이 {current_year}년 {month_str} 기준과 일치하는지 수학적으로 검증하십시오.\n\n"
            f"부연 설명 없이 완벽히 사실관계가 검증·수정된 브리핑 본문 전체를 출력하십시오."
        )
        
        subagent_verified_content = call_gemini_api(
            pass2_prompt, 
            system_instruction=system_instruction, 
            enable_search=True, 
            model_name=PRIMARY_MODEL
        )
        if not subagent_verified_content:
            log_message("Pass 2 하위 검증 실패로 Pass 1 초안을 유지합니다.")
            subagent_verified_content = draft_content

        # ------------------- [Pass 3: 총괄 에디터 에이전트 2차 최종 재검토] ------------------- #
        log_message("Pass 3: [총괄 에디터 에이전트] 1차 수정본 2차 최종 재검토, 논리 완결성 및 가독성 통합 마감 중...")
        pass3_prompt = (
            f"당신은 최고 수석 총괄 에디터 에이전트(Master Editor Agent)입니다.\n"
            f"하위 에이전트가 팩트체크를 거쳐 수정한 아래 [1차 수정본]을 다시 한 번 최종 검토하고 문체와 레이아웃을 통합 마감해 주세요.\n\n"
            f"[1차 수정본]:\n{subagent_verified_content}\n\n"
            f"[총괄 에디터 최종 검토 기준]:\n"
            f"1. **거시경제 논리 완결성**: 7대 이슈와 하단 [글로벌 마켓 뷰], [한국의 대응 전략]이 100% 모순 없는 동일한 결론과 인과적 흐름을 갖추었는지 확인 및 정렬.\n"
            f"2. **전문 한국어 금융 문체**: 기계적 번역 투나 외래어 남발 없이 독자가 신뢰할 수 있는 최고급 경제 브리핑 문체로 다듬기.\n"
            f"3. **비문 및 잔존 가드레일 표현 정돈**: 가드레일 지침 문구가 본문에 어색하게 삽입되거나 조사가 어긋난 문장이 없도록 자연스럽게 교열.\n\n"
            f"다른 서두나 메타 설명 없이 오직 완성된 최종 브리핑 본문(마크다운)만을 출력하십시오."
        )
        
        final_content = call_gemini_api(
            pass3_prompt, 
            system_instruction=system_instruction, 
            enable_search=False, 
            model_name=PRIMARY_MODEL
        )
        if not final_content:
            log_message("Pass 3 총괄 검토 실패로 Pass 2 1차 수정본을 채택합니다.")
            final_content = subagent_verified_content

        # ------------------- [최종 리포트 로컬 저장 및 발송] ------------------- #
        # N3: 깃허브 액션 환경 대응 메타데이터 주입
        date_iso = now.strftime('%Y-%m-%d')
        meta_header = f"<!-- report_date: {date_iso} -->\n# 📰 [{today_str_full} 주말 글로벌 경제 브리핑]\n\n"
        full_message = meta_header + final_content.strip()

        latest_report_path = os.path.join(CURRENT_DIR, "latest_weekend_report.md")
        if test_mode:
            os.makedirs(REPORTS_DIR, exist_ok=True)
            test_save_path = os.path.join(REPORTS_DIR, f"test_{now.strftime('%Y%m%d_%H%M%S')}.md")
            with open(test_save_path, "w", encoding="utf-8") as f:
                f.write(full_message)
            log_message(f"🧪 [테스트 모드] 리포트를 별도 경로에 저장 완료: {test_save_path}")
        else:
            with open(latest_report_path, "w", encoding="utf-8") as f:
                f.write(full_message)
            log_message(f"신규 생성된 리포트를 로컬에 저장 완료: {latest_report_path}")
        
        # 개선 3: 신규 생성 리포트 영구 보존용 백업
        os.makedirs(REPORTS_DIR, exist_ok=True)
        gen_backup_path = os.path.join(REPORTS_DIR, f"generated_{now.strftime('%Y%m%d_%H%M%S')}.md")
        try:
            with open(gen_backup_path, "w", encoding="utf-8") as f:
                f.write(full_message)
        except Exception:
            pass

        ok, success_count, total_count = send_telegram_message(full_message, test_mode=test_mode)
        if ok and not test_mode:
            archive_name = f"sent_{now.strftime('%Y%m%d_%H%M%S')}.md"
            archive_path = os.path.join(REPORTS_DIR, archive_name)
            os.replace(latest_report_path, archive_path)
            log_message(f"📦 발송 완료된 리포트를 아카이브 폴더로 이동 완료: {archive_path}")

        log_message("주말 경제 뉴스 파이프라인 정상 완료!")
        return ok
        
    except Exception as e:
        log_message(f"심각한 오류: generate_weekend_news 실행 중 예외 발생: {e}")
        return False

def parse_report_date(content):
    """
    N3: 리포트 본문에서 날짜 메타데이터 추출 (GitHub Actions mtime 초기화 대응)
    1. <!-- report_date: YYYY-MM-DD --> 메타 주석 탐색
    2. # 📰 [YYYY년 MM월 DD일 ...] 헤더 탐색
    """
    if not content:
        return None
        
    m1 = re.search(r'<!--\s*report_date:\s*(\d{4})-(\d{2})-(\d{2})\s*-->', content)
    if m1:
        try:
            return datetime.date(int(m1.group(1)), int(m1.group(2)), int(m1.group(3)))
        except ValueError:
            pass

    m2 = re.search(r'\[(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', content)
    if m2:
        try:
            return datetime.date(int(m2.group(1)), int(m2.group(2)), int(m2.group(3)))
        except ValueError:
            pass

    return None

def dispatch_latest_report(test_mode=False):
    """
    C1 & N1 & N3: 안티그래비티가 작성한 latest_weekend_report.md 신선도 검사 및 발송
    반환 상태 (str):
    - "sent": 정상 발송 성공 및 sent_...md 아카이브 완료
    - "stale": 72시간(3일) 초과 과거 리포트
    - "missing": 파일이 존재하지 않음
    - "send_failed": 파일은 유효하나 텔레그램 발송 실패 (네트워크/API 오류)
    """
    latest_report_path = os.path.join(CURRENT_DIR, "latest_weekend_report.md")
    if not os.path.exists(latest_report_path):
        log_message("리포트 파일(latest_weekend_report.md)이 존재하지 않습니다.")
        return "missing"

    try:
        with open(latest_report_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        log_message(f"리포트 파일 읽기 실패: {e}")
        return "missing"

    # N3: 1차 본문 날짜 메타데이터 기반 신선도 검증 (GitHub Actions mtime 초기화 대응)
    kst = datetime.timezone(datetime.timedelta(hours=9))
    today_kst = datetime.datetime.now(datetime.timezone.utc).astimezone(kst).date()
    report_date = parse_report_date(content)

    is_fresh = False
    if report_date:
        days_diff = (today_kst - report_date).days
        log_message(f"리포트 본문 기준 일자: {report_date} (오늘과 {days_diff}일 차이)")
        if 0 <= days_diff <= 3:
            is_fresh = True
        else:
            log_message(f"⚠️ 리포트 날짜({report_date})가 유효 범위(최근 3일)를 벗어났습니다.")
            return "stale"
    else:
        # 2차: 날짜 메타데이터 부재 시 mtime 폴백 검사
        mtime = os.path.getmtime(latest_report_path)
        file_dt = datetime.datetime.fromtimestamp(mtime)
        age_hours = (datetime.datetime.now() - file_dt).total_seconds() / 3600.0
        log_message(f"리포트 파일 mtime 경과 시간: {age_hours:.1f}시간")
        if age_hours <= 72.0:
            is_fresh = True
        else:
            log_message(f"⚠️ latest_weekend_report.md 파일이 {age_hours:.1f}시간 전 생성되어 72시간을 초과했습니다.")
            return "stale"

    if not is_fresh:
        return "stale"

    log_message("유효한 최신 리포트 텔레그램 발송을 시작합니다...")
    ok, success_count, total_count = send_telegram_message(content, test_mode=test_mode)

    if ok:
        if not test_mode:
            os.makedirs(REPORTS_DIR, exist_ok=True)
            archive_name = f"sent_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            archive_path = os.path.join(REPORTS_DIR, archive_name)
            os.replace(latest_report_path, archive_path)
            log_message(f"📦 발송 완료된 리포트를 아카이브 폴더로 이동 완료: {archive_path}")
        log_message("최신 브리핑 리포트 텔레그램 발송 성공 완료!")
        return "sent"
    else:
        log_message(f"❌ 리포트 텔레그램 발송 실패 (성공 파트: {success_count}/{total_count})")
        if success_count > 0 and not test_mode:
            # N1: 부분 전송 실패 시 다음 실행에서 첫 파트부터 중복 재전송되는 참사 방지
            os.makedirs(REPORTS_DIR, exist_ok=True)
            partial_name = f"partial_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            partial_path = os.path.join(REPORTS_DIR, partial_name)
            os.replace(latest_report_path, partial_path)
            log_message(f"⚠️ 일부 파트만 전송되어 중복 방지를 위해 partial 아카이브로 격리: {partial_path}")
        return "send_failed"

def run_collector(max_age_days=21):
    """주중 봇 수준의 고성능 크롤러로 3주간 팩트 풀 수집 및 정제"""
    try:
        from weekend_macro_collector import collect_3week_macro_news
        log_message("최근 3주 실측 언론사 팩트 풀 수집 파이프라인 가동...")
        res = collect_3week_macro_news(target_count=30, max_age_days=max_age_days)
        if res:
            log_message("최근 3주 실측 팩트 풀(weekend_macro_fact_pool.json) 갱신 완료!")
            return True
        else:
            log_message("⚠️ 팩트 풀 수집 실패 또는 기준 미달")
            return False
    except Exception as e:
        log_message(f"팩트 풀 수집 중 오류: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="주말 글로벌 경제 뉴스 자동화 및 발송 시스템")
    parser.add_argument("--collect-only", action="store_true", help="최근 3주 언론사 팩트 풀만 수집/갱신")
    parser.add_argument("--dispatch", action="store_true", help="안티그래비티가 작성한 latest_weekend_report.md를 텔레그램으로 발송")
    parser.add_argument("--test", "--dry-run", action="store_true", dest="test_mode",
                        help="텔레그램 실제 전송을 생략하고 콘솔로 결과를 출력하는 테스트 모드")
    args = parser.parse_args()
    
    success = False
    if args.collect_only:
        success = run_collector()
    elif args.dispatch:
        status = dispatch_latest_report(test_mode=args.test_mode)
        success = (status == "sent")
    else:
        # 스케줄러 기본 실행: 팩트 풀 갱신 및 유효한 리포트 발송
        run_collector()
        
        # N1: dispatch_latest_report 반환 상태 기반 엄격 제어
        status = dispatch_latest_report(test_mode=args.test_mode)
        if status == "sent":
            success = True
        elif status in ("missing", "stale"):
            log_message(f"기존 리포트 상태({status}): 신규 브리핑 생성을 진행합니다.")
            success = generate_weekend_news(test_mode=args.test_mode)
        elif status == "send_failed":
            # N1: 발송 실패 시 제미나이 리포트 중복 연쇄 발송 원천 차단
            log_message("❌ 기존 리포트 텔레그램 발송 실패: 중복 발송 방지를 위해 신규 생성을 중단합니다.")
            success = False

    # M9: 종료 코드 정합성 보장 (실패 시 1, 성공 시 0 반환)
    sys.exit(0 if success else 1)
