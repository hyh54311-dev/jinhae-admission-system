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

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ----------------- 환경 변수 설정 (GitHub Secrets 및 .env) ----------------- #
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

PRIMARY_MODEL = "gemini-flash-latest"
FALLBACK_MODELS = ["gemini-3.1-flash-lite", "gemini-pro-latest"]
# ------------------------------------------------------------------------- #

# 거시경제 팩트 및 통화정책 가드레일 시스템 인스트럭션
MACRO_SYSTEM_INSTRUCTION = (
    "당신은 글로벌 거시경제(Macroeconomics) 및 미래 신산업 동향을 정밀 분석하는 수석 경제학자이자 금융 에디터입니다.\n"
    "당신의 모든 브리핑은 엄격한 팩트와 최신 공식 통계에 근거해야 하며, 아래의 [절대 가드레일]을 100% 준수해야 합니다.\n\n"
    "[절대 가드레일 1: 글로벌 통화정책 피벗 국면 앵커링]\n"
    "- 현재 글로벌 거시경제는 '연준(Fed)의 긴축 종료 및 금리 인하(Pivot) 사이클'입니다.\n"
    "- '금리 인상 가능성', '금리 추가 인상 베팅'과 같은 통화정책 역주행 환각(Rate Hike Hallucination)은 절대 금지합니다.\n"
    "- 고용/물가 둔화는 '금리 인하 폭 확대(빅컷) 및 경기 침체 대응'으로, 고용/물가 호조는 '금리 인하 속도 조절(점진적 인하) 및 금리 동결 유지'로 일관되게 해석하십시오.\n\n"
    "[절대 가드레일 2: 수치 정확도 및 무임의 생성 원칙 (Zero Extrapolation)]\n"
    "- 검색 결과에서 명확히 확인되지 않는 구체적 통계 수치를 자의적으로 창작(Invent)하거나 지어내지 마십시오.\n"
    "- 미국 연방부채 실측치는 현재 약 35조~36조 달러 수준이며, 40조 달러는 향후 10년 후 장기 전망치(미 의회예산국 CBO 추산)입니다. '현재 40조 달러 돌파'와 같은 과장 표현은 엄금합니다.\n"
    "- 고용지표는 미국 노동통계국(BLS) 공식 발표치(비농업 신규 고용, 실업률)를 기준으로 인용하고 과거 연도(2022~2023)와 혼동하지 마십시오.\n\n"
    "[절대 가드레일 3: 정부 공식 목표와 민간 IB 전망치 구분]\n"
    "- 중국 경제성장률의 경우, 중국 정부의 공식 연간 목표('5% 안팎')와 골드만삭스 등 민간 투자은행(IB)의 자체 하향 전망치('4.x%')를 엄격히 분리하여 주체를 명시하십시오. '중국 정부가 목표를 낮췄다'고 왜곡하지 마십시오.\n\n"
    "[절대 가드레일 4: 시계열 및 지정학적 사건 팩트 앵커링]\n"
    "- 이스라엘-하마스 무력 분쟁 발발 시점은 2023년 10월 7일입니다. 현재 시점 기준 경과 기간을 정확히 서술하십시오.\n\n"
    "[절대 가드레일 5: 본문-요약 간 100% 논리적 정합성 및 전문 한글화]\n"
    "- 본문(7대 이슈)의 거시경제 진단과 하단 [글로벌 마켓 뷰] 및 [한국의 대응 전략]의 결론은 완벽히 동일한 인과관계와 방향성을 유지해야 합니다.\n"
    "- 외신 원문 내용은 외래어 남발 없이 가독성 높은 전문 한국어 금융/경제 용어로 완벽히 번역·정제하십시오."
)

def log_message(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}", flush=True)

def get_week_range(dt):
    """현재 날짜가 속한 주의 월요일부터 일요일까지 날짜 범위를 반환"""
    monday = dt - datetime.timedelta(days=dt.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return (
        monday.strftime("%Y년 %m월 %d일"),
        sunday.strftime("%Y년 %m월 %d일"),
        monday.strftime("%Y-%m-%d"),
        sunday.strftime("%Y-%m-%d")
    )

def call_gemini_api(prompt, system_instruction=MACRO_SYSTEM_INSTRUCTION, enable_search=True, model_name=PRIMARY_MODEL):
    if not GEMINI_API_KEY:
        log_message("오류: GEMINI_API_KEY가 설정되지 않았습니다.")
        return None
        
    models_to_try = [model_name] + [m for m in FALLBACK_MODELS if m != model_name]
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 65536,
            "temperature": 0.15 # 팩트 정밀도를 위해 낮은 temperature 유지
        }
    }
    
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        
    if enable_search:
        payload["tools"] = [{"googleSearch": {}}]
        
    for current_model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={GEMINI_API_KEY}"
        for attempt in range(1, 4):
            try:
                response = requests.post(url, json=payload, timeout=(15, 120))
                if response.status_code == 200:
                    json_data = response.json()
                    candidates = json_data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        result_text = "".join([p.get("text", "") for p in parts if "text" in p])
                        if result_text.strip():
                            log_message(f"Gemini API 호출 성공 (Model: {current_model}, Search: {enable_search})")
                            return result_text
                    log_message(f"주의: {current_model} 응답 텍스트 비어있음. 재시도합니다.")
                else:
                    log_message(f"API 에러 ({current_model}, Status {response.status_code}): {response.text[:200]}")
                    if response.status_code in [429, 503]:
                        time.sleep(2 ** attempt)
            except Exception as e:
                log_message(f"예외 발생 ({current_model}, 시도 {attempt}/3): {e}")
                time.sleep(2 ** attempt)
                
    log_message("모든 모델 및 재시도 실패")
    return None

def sanitize_macro_report(text):
    """
    Python 레벨의 2차 방어선 (Safety Net):
    알고리즘적 키워드 필터링을 통해 금리 인상 오기, 부채 과장 등 잔존 오류 교정
    """
    if not text:
        return text
        
    # 1. 금리 인상 오기 교정
    forbidden_rate_phrases = [
        "금리 인상 베팅", "금리 인상 압박", "금리를 인상할 것", "금리 인상 기조 복귀", "금리 인상 가능성"
    ]
    for phrase in forbidden_rate_phrases:
        if phrase in text:
            log_message(f"⚠️ 사후 교정: 금리 인상 환각 문구 감지 및 치환 ('{phrase}')")
            text = text.replace(phrase, "금리 인하 속도 조절 및 동결 유지 전망")
            
    # 2. 미국 부채 과장 교정
    debt_patterns = [
        (r"부채(가)?\s*40조\s*달러(를)?\s*돌파", "부채가 약 35~36조 달러 수준(향후 장기 전망상 40조 달러 돌파 예상)"),
        (r"연방\s*부채가\s*40조\s*달러", "연방 부채가 약 35조~36조 달러")
    ]
    for pattern, repl in debt_patterns:
        if re.search(pattern, text):
            log_message("⚠️ 사후 교정: 미국 연방부채 40조 달러 돌파 과장 환각 교정")
            text = re.sub(pattern, repl, text)
            
    return text

def send_telegram_message(text, test_mode=False):
    if test_mode:
        log_message("[TEST MODE] 텔레그램 실제 전송을 생략하고 표준 출력(stdout)에 리포트를 덤프합니다.")
        print("\n" + "="*50 + " [TELEGRAM MESSAGE PREVIEW] " + "="*50, flush=True)
        print(text, flush=True)
        print("="*126 + "\n", flush=True)
        return

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        log_message("주의: 텔레그램 토큰 또는 채팅 ID가 설정되지 않아 메시지를 전송하지 않습니다.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    MAX_LENGTH = 4000
    
    for i in range(0, len(text), MAX_LENGTH):
        part = text[i:i+MAX_LENGTH]
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': part,
            'parse_mode': 'Markdown'
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code != 200:
                log_message(f"텔레그램 마크다운 전송 실패 (Status {resp.status_code}), 일반 텍스트로 재시도합니다.")
                payload.pop('parse_mode')
                requests.post(url, json=payload, timeout=30)
        except Exception as e:
            log_message(f"오류: 텔레그램 전송 중 예외 발생: {e}")
        time.sleep(0.5)

def generate_weekend_news(test_mode=False):
    try:
        now = datetime.datetime.now() + datetime.timedelta(hours=9) # KST 보정 (UTC+9)
        today_str_full = f"{now.year}년 {now.month:02d}월 {now.day:02d}일"
        weekday = now.weekday()
        weekday_str = ["월", "화", "수", "목", "금", "토", "일"][weekday]
        
        week_start_str, week_end_str, _, _ = get_week_range(now)
        
        log_message(f"주말 글로벌 경제 뉴스 생성 시작 (기준일: {today_str_full}, 대상 주간: {week_start_str} ~ {week_end_str})")

        # 신산업 로테이션 (주차별)
        industries = [
            "신재생 에너지", "AI", "우주 산업", "전기차/자율주행", "SMR",
            "차세대 바이오/디지털 헬스케어", "로보틱스/휴머노이드", "양자 컴퓨팅", "차세대 반도체 및 스마트 팩토리"
        ]
        week_of_year = now.isocalendar()[1]
        target_new_industry = industries[week_of_year % len(industries)]
        log_message(f"이번 주 신산업 심층 포커스 주제: {target_new_industry} (연중 {week_of_year}주차)")

        # ------------------- [Pass 1: 초안 작성 (Search Grounding)] ------------------- #
        log_message("Pass 1: 실시간 검색 그라운딩 기반 초안 작성 중...")
        pass1_prompt = (
            f"당신은 글로벌 AI 거시경제 분석 전문가입니다. 현재 실제 날짜는 {today_str_full}({weekday_str}요일)입니다.\n"
            f"이번 주 분석 대상 기간은 **{week_start_str}부터 {week_end_str}까지(최근 7일)**입니다.\n\n"
            f"Google Search를 사용하여 위 7일간 실제로 미국, 중국 등 주요국에서 발표된 거시경제 핵심 동향 중 "
            f"**가장 중요한 7가지 글로벌 이슈**를 엄선하여 작성해 주세요.\n\n"
            f"[필수 작성 규칙]:\n"
            f"1. 통화정책 기조: 현재는 연준의 '금리 인하(Pivot)' 국면입니다. '금리 인상' 환각을 절대 적지 마십시오.\n"
            f"2. 수치 정확성: 검색된 공식 발표치(미 노동부 BLS, 연준, 미 재무부 등)만 인용하고, 확인되지 않은 숫자는 절대 창작하지 마십시오.\n"
            f"3. 미국 연방부채: 현재 실측치는 약 35조~36조 달러 대이며, 40조 달러는 미래 10년 후 장기 전망치입니다. '현재 40조 돌파'로 과장하지 마십시오.\n"
            f"4. 중국 경제: 중국 정부의 공식 목표('5% 안팎')와 민간 IB(골드만삭스 등)의 전망치('4.x%')의 주체를 정확히 구분하여 명시하십시오.\n"
            f"5. 중동 분쟁: 2023년 10월 7일 발발 시점을 기준으로 수학적으로 정확한 기간을 기술하십시오.\n\n"
            f"이와 별도로, 이번 주 주말엔 **[신산업 심층 포커스]** 섹션에 **'{target_new_industry}'**를 심층 분석해 주세요.\n"
            f"해당 산업의 현재 글로벌 발전 현황과 검증된 수치를 바탕으로 분석해 주세요.\n\n"
            f"각 이슈 분석 구성:\n"
            f"- 요약/데이터: (출처 명시 및 확인된 수치만 기술)\n"
            f"- 지정학적 맥락: (관련국 및 정책 동향)\n"
            f"- 시나리오: (긍정/부정)\n"
            f"- 한국 영향: (국내 증시, 환율, 주요 수출 기업 파급효과)\n\n"
            f"마지막 섹션 구성 (본문 7대 이슈와 100% 논리적으로 일치해야 함):\n"
            f"- [글로벌 마켓 뷰]: 이번 주 글로벌 거시경제 흐름 요약\n"
            f"- [한국의 대응 전략]: 국내 투자자 및 기업 관점의 전략 3가지\n"
            f"글자가 깨지지 않도록 깔끔한 마크다운 형식으로 작성해 주세요."
        )
        
        draft_content = call_gemini_api(pass1_prompt, enable_search=True, model_name=PRIMARY_MODEL)
        if not draft_content:
            log_message("Pass 1 초안 생성 실패")
            return False

        # ------------------- [Pass 2: 팩트체크 및 정밀 교열 (Verifier/Critic)] ------------------- #
        log_message("Pass 2: 금융 수석 에디터 팩트체크 및 모순 교열 수행 중...")
        pass2_prompt = (
            f"당신은 엄격한 최고 금융 데스크 수석 에디터입니다.\n"
            f"아래 [초안]을 정밀 감사하여 사실 왜곡, 통화정책 오류, 내부 논리 모순을 완벽히 교정한 [최종 브리핑]을 완성해 주세요.\n\n"
            f"[기준 시점]: {today_str_full} (주간 대상 기간: {week_start_str} ~ {week_end_str})\n\n"
            f"[초안 본문]:\n{draft_content}\n\n"
            f"[필수 감사 체크리스트]:\n"
            f"1. 통화정책 방향: 연준의 정책 기조가 '금리 인상'으로 잘못 기술된 곳이 있다면 즉시 '금리 인하 속도 조절 / 동결 유지' 등 올바른 피벗 기조로 전면 수정하십시오.\n"
            f"2. 수치 검증: 미국 부채 40조 달러 돌파와 같은 과장된 수치는 '약 35조~36조 달러 수준(장기 전망상 40조 도달 우려)'으로 정확히 정정하십시오.\n"
            f"3. 주체 검증: 중국 경제성장률의 '정부 공식 목표(5% 안팎)'와 '민간 IB 하향 전망치(4.x%)'가 혼동되지 않도록 명문화하십시오.\n"
            f"4. 내부 모순 감사: 본문(7대 이슈)의 진단과 하단 [글로벌 마켓 뷰]의 결론이 100% 동일한 논리적 방향을 갖도록 일치시키십시오.\n"
            f"5. 전문 한글화: 외신 내용 중 번역되지 않은 영문 텍스트가 없도록 유려한 전문 한국어 금융 용어로 정제하십시오.\n"
            f"6. 마크다운 정합성: 텔레그램 파싱 오류를 유발할 수 있는 불완전한 기호를 교열하십시오.\n\n"
            f"반드시 다른 메타 해설 없이 최종 교열된 브리핑 본문(마크다운)만을 출력하십시오."
        )
        
        final_content = call_gemini_api(pass2_prompt, enable_search=False, model_name=PRIMARY_MODEL)
        if not final_content:
            log_message("Pass 2 교열 실패로 Pass 1 초안을 기반으로 진행합니다.")
            final_content = draft_content

        # ------------------- [Python 레벨 사후 정제 (Sanitization)] ------------------- #
        sanitized_content = sanitize_macro_report(final_content)
        
        # ------------------- [헤더 부착 및 발송/출력] ------------------- #
        header = f"📰 *[{today_str_full} 주말 글로벌 경제 브리핑]*\n\n"
        full_message = header + sanitized_content
        
        send_telegram_message(full_message, test_mode=test_mode)
        log_message("주말 경제 뉴스 파이프라인 정상 완료!")
        return True
        
    except Exception as e:
        log_message(f"심각한 오류: generate_weekend_news 실행 중 예외 발생: {e}")
        if not test_mode:
            send_telegram_message(f"⚠️ 오류: {today_str_full} 주말 뉴스 생성 중 오류 발생: {e}")
        raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="주말 글로벌 경제 뉴스 자동화 봇")
    parser.add_argument("--test", "--dry-run", action="store_true", dest="test_mode",
                        help="텔레그램 전송을 생략하고 콘솔로 결과를 출력하는 테스트 모드")
    args = parser.parse_args()
    
    generate_weekend_news(test_mode=args.test_mode)

