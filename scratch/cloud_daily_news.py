import os
import sys
import json
import datetime
import requests
import urllib.request
import urllib.parse
import ssl

# ----------------- 환경 변수 설정 (GitHub Secrets) ----------------- #
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
MODEL_NAME = "gemini-3.1-flash-lite-preview"
# ------------------------------------------------------------------ #

def log_message(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def send_telegram_message(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        log_message("오류: 텔레그램 토큰 또는 채팅 ID가 설정되지 않았습니다.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # 메시지가 너무 길 경우 잘라서 전송 (텔레그램 제한: 4096)
    MAX_LENGTH = 4000
    for i in range(0, len(text), MAX_LENGTH):
        part = text[i:i+MAX_LENGTH]
        data = urllib.parse.urlencode({'chat_id': TELEGRAM_CHAT_ID, 'text': part, 'parse_mode': 'Markdown'}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        try:
            urllib.request.urlopen(req, context=ctx)
        except Exception as e:
            # Markdown 에러 방지를 위해 일반 텍스트로 재시도
            data = urllib.parse.urlencode({'chat_id': TELEGRAM_CHAT_ID, 'text': part}).encode('utf-8')
            req = urllib.request.Request(url, data=data)
            urllib.request.urlopen(req, context=ctx)
            log_message(f"오류 텔레그램 전송 (텍스트 모드): {e}")

def call_gemini_api(prompt):
    if not GEMINI_API_KEY:
        log_message("오류: GEMINI_API_KEY가 설정되지 않았습니다.")
        return None
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"googleSearch": {}}],
        "generationConfig": {
            "maxOutputTokens": 65536,
            "temperature": 0.2
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=300)
        
        # API 응답 상태 확인 및 상세 로그 출력
        if response.status_code != 200:
            log_message(f"API 에러 발생 (Status {response.status_code}): {response.text}")
            response.raise_for_status()
            
        json_data = response.json()
        candidates = json_data.get("candidates", [])
        
        if not candidates:
            log_message(f"오류: API 응답에 candidates가 없습니다: {json_data}")
            return None
            
        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join([part.get("text", "") for part in parts])
    except Exception as e:
        log_message(f"오류: API 호출 중 예외 발생: {e}")
        # GitHub Actions에서 실패 상태를 인지할 수 있도록 예외를 다시 발생시킵니다.
        raise e

def generate_weekend_news():
    now = datetime.datetime.now() + datetime.timedelta(hours=9) # KST 보정 (GitHub 서버는 UTC)
    today_str_full = f"{now.year}년 {now.month:02d}월 {now.day:02d}일"
    weekday = now.weekday()
    weekday_str = ["월", "화", "수", "목", "금", "토", "일"][weekday]
    
    log_message(f"주말 글로벌 경제 뉴스 자동 생성을 시작합니다. ({today_str_full})")

    # 신산업 로테이션 (주차별)
    industries = [
        "신재생 에너지", "AI", "우주 산업", "전기차/자율주행", "SMR",
        "차세대 바이오/디지털 헬스케어", "로보틱스/휴머노이드", "양자 컴퓨팅", "차세대 반도체 및 스마트 팩토리"
    ]
    week_of_year = now.isocalendar()[1]
    target_new_industry = industries[week_of_year % len(industries)]
    
    prompt = (
        f"당신은 글로벌 AI 경제 분석 및 신산업 전문가입니다. 현재 실제 날짜는 {today_str_full}({weekday_str}요일)입니다. "
        f"Google Search를 사용하여 이번 주간 미국, 중국을 포함한 글로벌 주요국들의 핵심 경제 동향 중 **가장 중요한 7가지 글로벌 이슈**를 엄선하여 작성해 주세요.\n\n"
        f"이와 별도로, 이번 주 주말엔 **[신산업 심층 포커스]** 섹션을 반드시 포함해야 합니다. 이번 주 선정 산업은 **'{target_new_industry}'**입니다. "
        f"해당 산업의 현재 글로벌 발전 현황과 전문가들의 수치 기반 의견을 바탕으로 심층 분석해 주세요.\n\n"
        f"각 이슈 분석엔 1)요약/데이터, 2)관련국 및 지정학적 맥락, 3)긍정/부정 시나리오, 4)한국 시장 기회 및 위협을 포함해야 합니다.\n"
        f"마지막에는 다음 요약을 포함해 주세요.\n"
        f"- [글로벌 마켓 뷰]: 이번 주 글로벌 거시경제 흐름 요약\n"
        f"- [한국의 대응 전략]: 투자 인사이트 3가지\n"
        f"글자가 깨지지 않도록 깔끔한 마크다운 형식으로 작성해 주세요."
    )
    
    content = call_gemini_api(prompt)
    if content:
        header = f"📰 *[{today_str_full} 주말 글로벌 경제 브리핑]*\n\n"
        send_telegram_message(header + content)
        log_message("주말 뉴스 생성 및 전송 완료!")
    else:
        send_telegram_message(f"오류: {today_str_full} 주말 뉴스 생성에 실패했습니다. API 로그를 확인해 주세요.")

if __name__ == "__main__":
    generate_weekend_news()
