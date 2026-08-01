# -*- coding: utf-8 -*-
import os
import sys
import json
import ssl
import requests
import datetime
import urllib.parse
import urllib.request
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(PARENT_DIR)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_TOKENS = ["8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY"]
TELEGRAM_CHAT_ID = "8518409134"
TARGET_FOLDER_ID = "1phqLh0I4iX5QEteNV-EYfoFwzo7YYe7U"
MODEL_NAME = "gemini-3.1-flash-lite"

def log_msg(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        print(f"[{timestamp}] {msg}")
    except Exception:
        print(f"[{timestamp}] {msg.encode('utf-8', errors='ignore').decode('utf-8')}")

def call_gemini_api(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"googleSearch": {}}],
        "generationConfig": {"maxOutputTokens": 65536, "temperature": 0.2}
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        log_msg("Sending request to Gemini API (googleSearch grounding enabled)...")
        res = requests.post(url, json=payload, headers=headers, timeout=180)
        if res.status_code != 200:
            log_msg(f"API Error ({res.status_code}): {res.text[:300]}")
            return None
        data = res.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            parts = data["candidates"][0]["content"]["parts"]
            text = "".join([p.get("text", "") for p in parts])
            return text
    except Exception as e:
        log_msg(f"Exception during Gemini API call: {e}")
    return None

def upload_to_gdoc(title, md_content, folder_id=TARGET_FOLDER_ID):
    import markdown
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    SCOPES = ['https://www.googleapis.com/auth/drive']
    token_path = os.path.join(PARENT_DIR, 'token.json')
    
    if not os.path.exists(token_path):
        log_msg("token.json not found in parent, trying token_calendar.json...")
        token_path = os.path.join(PARENT_DIR, 'token_calendar.json')

    creds = None
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
        except Exception as e:
            log_msg(f"Token refresh error: {e}")

    if not creds:
        log_msg("No valid Google Drive credentials available.")
        return None

    try:
        drive_service = build('drive', 'v3', credentials=creds)
        html_body = markdown.markdown(md_content, extensions=['extra'])
        
        styled_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: 'Georgia', serif; margin: 40px; line-height: 1.6; color: #2F3E46; }}
h1 {{ color: #1A1A1A; text-align: center; margin-top: 30px; font-size: 24pt; }}
h2, h3 {{ color: #1D3557; margin-top: 25px; }}
blockquote {{ color: #4F5D75; font-style: italic; margin-left: 30px; border-left: 3px solid #1D3557; padding-left: 15px; }}
hr {{ border: 0; height: 1px; background: #ccc; margin: 30px 0; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""
        
        temp_dir = os.path.join(PARENT_DIR, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        html_file = os.path.join(temp_dir, f"{title}.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(styled_html)
            
        file_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.document',
            'parents': [folder_id]
        }
        media = MediaFileUpload(html_file, mimetype='text/html', resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='webViewLink, id').execute()
        
        try:
            drive_service.permissions().create(
                fileId=file.get('id'),
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
        except Exception as perm_err:
            log_msg(f"Permission share warning: {perm_err}")

        doc_url = file.get('webViewLink')
        log_msg(f"Google Doc created successfully: {doc_url}")
        return doc_url
    except Exception as e:
        log_msg(f"Failed to upload Google Doc: {e}")
        return None

def send_telegram_alert(file_name, is_sunday, summary, file_url):
    prefix = "일요일 철학/인물산책" if is_sunday else "토요일 미래/친환경 기술"
    summary_section = f"\n\n💡 <b>핵심 요약 (5줄 이내):</b>\n{summary}" if summary else ""
    file_link_part = f"\n\n🔗 <a href=\"{file_url}\">여기서 리포트 바로 읽기</a>" if file_url else ""
    
    text = (
        f"📝 <b>[{prefix} 생성 완료]</b>\n\n"
        f"오늘의 리포트(<code>{file_name}</code>)가 구글 문서로 저장되었습니다."
        f"{summary_section}"
        f"{file_link_part}"
    )
    
    for token in TELEGRAM_TOKENS:
        try:
            telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML"
            }
            res = requests.post(telegram_url, data=payload, timeout=15)
            if res.status_code == 200:
                log_msg(f"텔레그램 알림 전송 성공! (Bot ID: {token.split(':')[0]})")
                return True
            else:
                log_msg(f"텔레그램 전송 에러 ({res.status_code}): {res.text}")
        except Exception as e:
            log_msg(f"텔레그램 전송 예외: {e}")
    return False

def run_saturday_future_tech():
    log_msg("Saturday Future Tech Report generating...")
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d")
    date_full_str = now.strftime("%Y년 %m월 %d일")
    
    prompt = (
        f"당신은 글로벌 벤처캐피털(VC)의 시니어 기술 파트너이자 친환경 미래 기술 학술 분석가입니다. 현재 실제 날짜는 {date_full_str}입니다.\n\n"
        "Google Search를 사용하여, 현재 글로벌 친환경 기술, 미래 혁신 기술, 또는 신성장 동력 분야 중 **최근 1-2주 사이에 가장 의미 있는 성과나 변화가 있었고 중요도가 높은 기술 분야**를 하나만 엄선해 주세요.\n\n"
        "**[요약 및 본문 구분 규칙 - 필수]**\n"
        "반드시 응답의 맨 처음에 아래와 같이 `[요약]`과 `[본문]` 태그를 사용하여 요약과 본문을 명확히 구분해 주세요:\n"
        "[요약]\n"
        "- 5줄 이내로 이 리포트의 핵심 개념과 중요 인사이트를 개조식으로 요약해 주세요 (각 줄 끝에 줄바꿈 필수).\n"
        "[본문]\n"
        "(여기에 에세이 본문을 작성해 주세요. 아래 서식 규칙 준수)\n\n"
        "**[E-Book 서식 및 태블릿 가독성 최적화 요구사항]**\n"
        "- 본 텍스트는 건조한 '비즈니스 보고서'가 아닌, **한 권의 인문/과학 단행본(E-Book)이나 품격 있는 기술 에세이**처럼 서사적이고 유려한 문체로 작성해 주세요.\n"
        "- **분량 극대화**: 본문은 **최소 4,000자 이상(공백 제외)**의 충분한 분량으로 상세히 기술하여 깊은 읽을거리를 제공해야 합니다.\n"
        "- 소설이나 과학책의 챕터처럼 **서사적이고 흥미를 유발하는 제목**을 사용해 주세요.\n"
        "- 부드럽게 연결되는 산문(줄글) 형식을 위주로 작성하고, 주요 용어나 수치는 볼드체(**)로 표기해 주세요.\n"
        "- 각 챕터 사이에는 마크다운 구분선(`---`)을 넣어 주세요.\n\n"
        "아래 맥락을 담은 4개의 장으로 구성해 주세요:\n"
        "- **제1장 (기술의 핵심 원리와 정의)**\n"
        "- **제2장 (글로벌 연구 및 상용화의 최전선)** (선도 기업, 연구소, 핵심 수치 데이터 포함)\n"
        "- **제3장 (친환경적 가치와 인류에 미칠 파급력)**\n"
        "- **제4장 (남겨진 기술적 난제와 미래의 지도)**"
    )
    
    content = call_gemini_api(prompt)
    if not content:
        log_msg("Saturday Future Tech Report Generation Failed")
        return False
        
    summary = ""
    body_text = content
    if "[요약]" in content and "[본문]" in content:
        summary_part = content.split("[본문]")[0]
        summary = summary_part.replace("[요약]", "").strip()
        body_text = content.split("[본문]")[1].strip()
        
    file_name = f"{date_str}_Future_Tech_Report"
    file_url = upload_to_gdoc(file_name, body_text)
    
    send_telegram_alert(file_name, False, summary, file_url)
    return True

def run_sunday_philosophy():
    log_msg("Sunday Philosophy Report generating...")
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d")
    date_full_str = now.strftime("%Y년 %m월 %d일")
    
    era_name = "고대에 가까운 중세 철학"
    era_desc = "로마 말기 교부 철학부터 초기 이슬람 철학의 황금기까지 (아우구스티누스, 보에티우스, 이븐 시나, 가잘리 등)"
    
    prompt = (
        f"당신은 인문학, 철학, 그리고 역사적 사상의 계보에 정통한 석학 교수입니다. 현재 실제 날짜는 {date_full_str}입니다.\n"
        f"이번 달의 탐구 영역은 **'[{era_name}]'** ({era_desc}) 입니다.\n\n"
        "이 영역 내에서 가장 논쟁적이고 사상사적 깊이가 깊은 **핵심 사상가 1명과 그의 핵심 개념/논쟁**을 엄선하여 깊이 있게 다뤄 주세요.\n\n"
        "**[요청사항]**\n"
        "1. **학술적 수준**: 대학 학부 전공 수준으로 사상의 논리적 구조, 텍스트 원전 구절, 사상사적 계보 및 한계점을 깊이 있게 헤집어 주세요.\n"
        "2. **친근한 비유**: 어려운 전문 용어 등장 시 고등학생도 직관적으로 이해할 수 있는 일상적 비유나 사고 실험을 곁들여 주세요.\n"
        "3. **[요약 및 본문 구분 규칙 - 필수]**\n"
        "   [요약]\n"
        "   - 5줄 이내로 핵심 개념과 중요 인사이트를 개조식 요약 (각 줄 끝 줄바꿈 필수).\n"
        "   [본문]\n"
        "   (에세이 본문 작성)\n\n"
        "4. **분량 극대화**: 본문은 **최소 4,000자 이상(공백 제외)**으로 상세히 기술해 주세요.\n"
        "5. **구조화**: 아래 4개 장으로 작성해 주세요:\n"
        "   - **제1장 (시대의 어둠과 철학적 문제의식)**\n"
        "   - **제2장 (개념의 지도와 핵심 논증 아키텍처)** (원어 해설 포함)\n"
        "   - **제3장 (비판자들의 시선과 학술적 한계)**\n"
        "   - **제4장 (21세기 문명에 던지는 시사점과 생각거리)** (마지막에 성찰용 토론 질문 3가지 자연스럽게 포함)"
    )
    
    content = call_gemini_api(prompt)
    if not content:
        log_msg("Sunday Philosophy Report Generation Failed")
        return False
        
    summary = ""
    body_text = content
    if "[요약]" in content and "[본문]" in content:
        summary_part = content.split("[본문]")[0]
        summary = summary_part.replace("[요약]", "").strip()
        body_text = content.split("[본문]")[1].strip()
        
    file_name = f"{date_str}_Philosophy_Reading"
    file_url = upload_to_gdoc(file_name, body_text)
    
    send_telegram_alert(file_name, True, summary, file_url)
    return True

if __name__ == "__main__":
    log_msg("==========================================")
    log_msg("Weekend Reports Instant Generation Start")
    log_msg("==========================================")
    
    log_msg("1/2: Running Saturday Future Tech Report...")
    sat_success = run_saturday_future_tech()
    
    log_msg("\n2/2: Running Sunday Philosophy Report...")
    sun_success = run_sunday_philosophy()
    
    log_msg("==========================================")
    log_msg(f"Result - Saturday: {'Success' if sat_success else 'Fail'}, Sunday: {'Success' if sun_success else 'Fail'}")
    log_msg("==========================================")
