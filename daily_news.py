import os
import sys
import io
import time
import datetime
import schedule
import requests
import markdown
import subprocess
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()

# Windows 콘솔 출력 UTF-8 설정
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding.lower() != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

# ----------------- 사용자 설정 ----------------- #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "daily_news_history.log")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.1-flash-lite" 

FOLDER_PATH = os.path.join(BASE_DIR, "경제뉴스 TXT")

EMAIL_SENDER = "hyh54311@gmail.com"  
EMAIL_PASSWORD = "obpv abgy acyh evho"
EMAIL_RECEIVER = "hyh54311@gmail.com"

PAUSE_WEEKDAY = True  # 주중 데일리 뉴스 자동 생성 일시 중지 플래그

# ----------------------------------------------- #

def log_message(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_message + "\n")
    except Exception as e:
        print(f"로그 기록 실패: {e}")

def upload_to_gdoc(md_path):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    FOLDER_ID = "1aXM_giZCkZVKnFrDK6tRQZly6e2JvTUX"
    creds = None
    token_path = os.path.join(BASE_DIR, 'token.json')
    if os.path.exists(token_path):
        cr = Credentials.from_authorized_user_file(token_path, SCOPES)
        if cr and cr.expired and cr.refresh_token:
            cr.refresh(Request())
            with open(token_path, 'w') as token:
                token.write(cr.to_json())
        creds = cr
    if not creds:
        log_message("구글 드라이브 인증 정보(token.json)가 없습니다.")
        return None

    try:
        drive_service = build('drive', 'v3', credentials=creds)
        with open(md_path, 'r', encoding='utf-8') as f:
            md_text = f.read()
            
        html_text = markdown.markdown(md_text, extensions=['extra'])
        
        temp_dir = os.path.join(BASE_DIR, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        html_path = os.path.join(temp_dir, os.path.basename(md_path).replace('.md', '.html'))
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_text)
            
        file_metadata = {
            'name': os.path.basename(md_path).replace('.md', ''),
            'mimeType': 'application/vnd.google-apps.document',
            'parents': [FOLDER_ID]
        }
        media = MediaFileUpload(html_path, mimetype='text/html', resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='webViewLink').execute()
        
        try:
            if os.path.exists(html_path):
                os.remove(html_path)
        except: pass
        
        return file.get('webViewLink')
    except Exception as e:
        log_message(f"구글 문서 업로드 실패: {e}")
        return None

def send_telegram_alert(file_name, file_path, is_weekend=False, doc_link=None, summary=None):
    import urllib.request
    import urllib.parse
    import ssl
    
    tokens = [
        "8799464748:AAHD2ERa9aEnqn6Dtr7SNDjDOf9KGFEMziU", # Assistant Bot
        "8407908239:AAHgWACsaJ9y4JMkxI0iC4Kyhs4RNbxpdaY"  # Macro News Bot
    ]
    chat_id = "8518409134"
    prefix = "주말 글로벌 지식 브리핑" if is_weekend else "경제 뉴스"
    link_text = f"\n\n🔗 구글 문서 링크:\n{doc_link}" if doc_link else ""
    
    summary_text = f"\n\n💡 **핵심 요약 (5줄 이내):**\n{summary}" if summary else ""
    text = f"📝 [{prefix} 생성 완료]\n\n오늘의 리포트({file_name})가 구글 드라이브에 저장되었습니다.{summary_text}{link_text}\n태블릿이나 휴대폰의 구글 문서 앱으로 편리하게 확인하실 수 있습니다."
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for token in tokens:
        try:
            telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
            
            # Alert Message 발송
            data = urllib.parse.urlencode({'chat_id': chat_id, 'text': text}).encode('utf-8')
            req = urllib.request.Request(telegram_url, data=data)
            urllib.request.urlopen(req, context=ctx)
            
            log_message(f"텔레그램 알림 전송 완료! (Bot ID: {token.split(':')[0]})")
            return # Success
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

def get_past_briefings(folder_path, count=3):
    if not os.path.exists(folder_path): return "이전 뉴스 기록이 없습니다."
    files = [f for f in os.listdir(folder_path) if f.endswith("_Macro_Briefing.md")]
    files.sort(reverse=True)
    past_contents = []
    for f_name in files[:count]:
        path = os.path.join(folder_path, f_name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                summary = content[:1000].replace("\n", " ")
                past_contents.append(f"[{f_name}] {summary}...")
        except: pass
    return "\n".join(past_contents) if past_contents else "이전 뉴스 기록이 없습니다."

def get_past_future_tech_topics(folder_path):
    if not os.path.exists(folder_path): return "이전 기술 분석 기록이 없습니다."
    files = [f for f in os.listdir(folder_path) if f.endswith("_Future_Tech_Report.md")]
    files.sort(reverse=True)
    past_topics = []
    for f_name in files:
        path = os.path.join(folder_path, f_name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = [f.readline().strip() for _ in range(15)]
                title = ""
                for line in lines:
                    if line.startswith("#"):
                        title = line.replace("#", "").strip()
                        break
                if not title:
                    title = f_name
                past_topics.append(f"- {title} (생성일자: {f_name[:10]})")
        except Exception:
            pass
    return "\n".join(past_topics) if past_topics else "이전 기술 분석 기록이 없습니다."

def generate_saturday_future_tech():
    now = datetime.datetime.now()
    today_str_full = f"{now.year}년 {now.month:02d}월 {now.day:02d}일"
    today_str_iso = now.strftime("%Y-%m-%d")
    
    log_message(f"🚀 토요일 미래 기술 & 친환경 기술 분석 시작 ({today_str_full})")
    past_history = get_past_future_tech_topics(FOLDER_PATH)
    
    prompt = (
        f"당신은 글로벌 벤처캐피털(VC)의 시니어 기술 파트너이자 친환경 미래 기술 학술 분석가입니다. 현재 실제 날짜는 {today_str_full}입니다.\n"
        f"아래는 기존에 이미 분석 보고서를 작성한 기술 목록입니다. 중복을 방지하기 위해 이 목록에 명시된 기술은 제외해 주세요.\n"
        f"--- 이미 다룬 기술 및 산업 역사 ---\n{past_history}\n--------------------\n\n"
        f"Google Search를 사용하여, 현재 글로벌 친환경 기술, 미래 혁신 기술, 또는 신성장 동력 분야 중 **최근 1-2주 사이에 가장 의미 있는 성과나 변화가 있었고 중요도가 높은 기술 분야**를 하나만 엄선해 주세요.\n"
        f"단, 과거에 다룬 주제라 할지라도 최근 1주일 이내에 세상을 바꿀 만한 획기적인 기술적 돌파구(Breakthrough)가 발표된 경우에 한해 예외적으로 중복 선정이 가능하며, 이 경우 무엇이 달라졌는지 명확히 설명해야 합니다.\n\n"
        f"**[요약 및 본문 구분 규칙 - 필수]**\n"
        f"반드시 응답의 맨 처음에 아래와 같이 `[요약]`과 `[본문]` 태그를 사용하여 요약과 본문을 명확히 구분해 주세요:\n"
        f"[요약]\n"
        f"- 5줄 이내로 이 리포트의 핵심 개념과 중요 인사이트를 개조식으로 요약해 주세요 (각 줄 끝에 줄바꿈 필수).\n"
        f"[본문]\n"
        f"(여기에 에세이 본문을 작성해 주세요. 아래 서식 규칙 준수)\n\n"
        f"**[E-Book 서식 및 태블릿 가독성 최적화 요구사항]**\n"
        f"- 본 텍스트는 건조한 '비즈니스 보고서'가 아닌, **한 권의 인문/과학 단행본(E-Book)이나 품격 있는 기술 에세이**처럼 서사적이고 유려한 문체로 작성해 주세요.\n"
        f"- **분량 극대화**: 본문은 **최소 4,000자 이상(공백 제외)**의 충분한 분량으로 상세히 기술하여 깊은 읽을거리를 제공해야 합니다. 얕은 단편 요약을 철저히 배제하고, 한 장의 밀도가 매우 높아야 합니다.\n"
        f"- 딱딱하게 숫자가 매겨진 제목(예: '1. 기술 작동 원리') 대신, 소설이나 과학책의 챕터처럼 **서사적이고 흥미를 유발하는 제목**을 사용해 주세요. (예: '제1장: 분자의 노래 - 작동과 흐름의 원리' 등)\n"
        f"- 항목을 단순히 나열하는 개조식 리스트(번호나 점 기호)는 되도록 지양하고, **부드럽게 연결되는 산문(줄글) 형식**을 사용하여 호흡이 끊기지 않고 책을 읽듯 읽어내려갈 수 있도록 해 주세요.\n"
        f"- 좁은 모바일 기기 화면에서도 눈이 편하도록 문단 구분을 명확히 하고 **주요 용어나 수치는 볼드체(**)로 표기해 주세요.\n"
        f"- 각 챕터 사이에는 마크다운 구분선(`---`)을 넣어 지면을 아름답게 구분해 주세요.\n\n"
        f"에세이는 대학 수준의 깊이를 갖추어 마크다운 형식으로 작성해 주시고, 아래 맥락을 담은 4개의 장으로 구성해 주세요. 각 장(Chapter)은 최소 1,000자 이상의 충분한 산문으로 자세히 상술되어야 합니다:\n"
        f"- **제1장 (기술의 핵심 원리와 정의)**\n"
        f"- **제2장 (글로벌 연구 및 상용화의 최전선)** (선도 기업, 연구소, 핵심 수치 데이터 포함)\n"
        f"- **제3장 (친환경적 가치와 인류에 미칠 파급력)**\n"
        f"- **제4장 (남겨진 기술적 난제와 미래의 지도)**"
    )
    
    content = _call_gemini_api(prompt, MODEL_NAME, GEMINI_API_KEY)
    if not content:
        log_message("❌ 토요일 미래 기술 콘텐츠 생성 실패.")
        return
        
    summary = ""
    body_text = content
    
    summary_idx = content.find("[요약]")
    body_idx = content.find("[본문]")
    if summary_idx != -1 and body_idx != -1:
        summary = content[summary_idx + 4:body_idx].strip()
        body_text = content[body_idx + 4:].strip()
        
    os.makedirs(FOLDER_PATH, exist_ok=True)
    file_path = os.path.join(FOLDER_PATH, f"{today_str_iso}_Future_Tech_Report.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(body_text)
        
    doc_link = upload_to_gdoc(file_path)
    send_telegram_alert(os.path.basename(file_path), file_path, is_weekend=True, doc_link=doc_link, summary=summary)
    
    try:
        popup_script = os.path.join(BASE_DIR, "notify_popup_perfect.py")
        if os.path.exists(popup_script):
            subprocess.Popen([sys.executable, popup_script])
    except Exception:
        pass

def generate_sunday_philosophy():
    now = datetime.datetime.now()
    today_str_full = f"{now.year}년 {now.month:02d}월 {now.day:02d}일"
    today_str_iso = now.strftime("%Y-%m-%d")
    
    log_message(f"🚀 일요일 대학 수준 철학 & 인류사 분석 시작 ({today_str_full})")
    
    # 2026년 1월을 0으로 기준 삼아 5개월 단위 순환 루프 생성
    months_since_start = (now.year - 2026) * 12 + (now.month - 1)
    cycle_index = months_since_start % 5
    
    eras = {
        0: ("고대 철학", "그리스 철학의 탄생부터 헬레니즘 시대까지 (소크라테스, 플라톤, 아리스토텔레스, 스토아 학파, 에피쿠로스 등)"),
        1: ("고대에 가까운 중세 철학", "로마 말기 교부 철학부터 초기 이슬람 철학의 황금기까지 (아우구스티누스, 보에티우스, 이븐 시나, 가잘리 등)"),
        2: ("중세 신학 및 철학", "스콜라 철학의 융성 및 중세 후기 신학적 논쟁 (토마스 아퀴나스, 안셀무스, 윌리엄 오브 오컴 등)"),
        3: ("근대 철학", "르네상스, 대륙 합리론, 영미 경험론 및 계몽주의 시대 (마키아벨리, 데카르트, 스피노자, 로크, 흄, 칸트 등)"),
        4: ("현대 철학 및 인지과학", "19세기 실존주의, 실용주의, 현상학, 분석철학 및 행동경제학 (니체, 하이데거, 사르트르, 비트겐슈타인, 대니얼 카너먼 등)")
    }
    era_name, era_desc = eras[cycle_index]
    
    prompt = (
        f"당신은 인문학, 철학, 그리고 역사적 사상의 계보에 정통한 석학 교수입니다. 현재 실제 날짜는 {today_str_full}입니다.\n"
        f"이번 달의 탐구 영역은 **'[{era_name}]'** ({era_desc}) 입니다.\n\n"
        f"이 영역 내에서 가장 논쟁적이고 사상사적 깊이가 깊은 **핵심 사상가 1명과 그의 핵심 개념/논쟁**을 엄선하여 깊이 있게 다뤄 주세요.\n"
        f"**[요구사항]**:\n"
        f"1. **학술적 수준**: 대략 대학 학부생(Undergraduate) 이상의 전공 수준으로 작성해 주세요. 단순 인물 소개나 넓고 얕은 요약은 피하고, 사상의 논리적 구조, 텍스트(원전)의 구절, 사상사적 계보 및 한계점을 깊이 있게 헤집어야 합니다.\n"
        f"2. **친근한 비유**: 글의 논조는 격조 높고 학구적이어야 하지만, 어려운 전문 용어가 처음 등장할 때는 고등학생이나 일반인이 직관적으로 이해할 수 있도록 명료한 일상적 비유나 사고 실험을 하나씩 곁들여 주세요.\n"
        f"3. **요약 및 본문 구분 규칙 - 필수**:\n"
        f"   반드시 응답의 맨 처음에 아래와 같이 `[요약]`과 `[본문]` 태그를 사용하여 요약과 본문을 명확히 구분해 주세요:\n"
        f"   [요약]\n"
        f"   - 5줄 이내로 이 리포트의 핵심 개념과 중요 인사이트를 개조식으로 요약해 주세요 (각 줄 끝에 줄바꿈 필수).\n"
        f"   [본문]\n"
        f"   (여기에 에세이 본문을 작성해 주세요. 아래 서식 규칙 준수)\n\n"
        f"4. **E-Book 서식 및 태블릿 가독성 최적화 요구사항**:\n"
        f"   - 본 텍스트는 건조한 '비즈니스 보고서'가 아닌, **한 권의 인문/철학 단행본(E-Book)이나 품격 있는 에세이**처럼 서사적이고 유려한 문체로 작성해 주세요.\n"
        f"   - **분량 극대화**: 본문은 **최소 4,000자 이상(공백 제외)**의 충분한 분량으로 상세히 기술하여 깊은 읽을거리를 제공해야 합니다. 얕은 단편 요약을 철저히 배제하고, 한 장의 밀도가 매우 높아야 합니다.\n"
        f"   - 딱딱하게 숫자가 매겨진 제목(예: '1. 사상적 맥락') 대신, 실제 철학 대중서의 챕터처럼 **서사적이고 영감을 주는 제목**을 사용해 주세요. (예: '제1장: 존재의 심연을 들여다보다' 등)\n"
        f"   - 리스트(번호나 점 기호)를 남발하지 말고, **부드럽고 긴밀하게 흐르는 줄글(산문) 형식**을 위주로 작성하여 책의 흐름을 즐길 수 있게 해 주세요. 중요한 철학 원전 인용은 마크다운 인용 블록(`>`)을 적극 활용해 주세요.\n"
        f"   - 좁은 화면에서도 눈이 편하도록 단락 구분을 명확히 하고, 핵심 원어(개념)는 **볼드체(**)로 표기하며, 챕터 사이에는 마크다운 구분선(`---`)을 넣어 주세요.\n"
        f"5. **구조화**: 아래 맥락을 담은 4개의 장으로 구성해 주세요. 각 장(Chapter)은 최소 1,000자 이상의 충분한 산문으로 자세히 상술되어야 합니다.\n"
        f"   - **제1장 (시대의 어둠과 철학적 문제의식)**\n"
        f"   - **제2장 (개념의 지도와 핵심 논증 아키텍처)** (원어 해설 포함)\n"
        f"   - **제3장 (비판자들의 시선과 학술적 한계)**\n"
        f"   - **제4장 (21세기 문명에 던지는 시사점과 생각거리)** (마지막에는 대학 세미나 수준의 성찰용 토론 질문 3가지를 본문 속에 자연스럽게 포함)"
    )
    
    content = _call_gemini_api(prompt, MODEL_NAME, GEMINI_API_KEY)
    if not content:
        log_message("❌ 일요일 철학 콘텐츠 생성 실패.")
        return
        
    summary = ""
    body_text = content
    
    summary_idx = content.find("[요약]")
    body_idx = content.find("[본문]")
    if summary_idx != -1 and body_idx != -1:
        summary = content[summary_idx + 4:body_idx].strip()
        body_text = content[body_idx + 4:].strip()
        
    os.makedirs(FOLDER_PATH, exist_ok=True)
    file_path = os.path.join(FOLDER_PATH, f"{today_str_iso}_Philosophy_Reading.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(body_text)
        
    doc_link = upload_to_gdoc(file_path)
    send_telegram_alert(os.path.basename(file_path), file_path, is_weekend=True, doc_link=doc_link, summary=summary)
    
    try:
        popup_script = os.path.join(BASE_DIR, "notify_popup_perfect.py")
        if os.path.exists(popup_script):
            subprocess.Popen([sys.executable, popup_script])
    except Exception:
        pass

def generate_daily_news():
    now = datetime.datetime.now()
    weekday = now.weekday()
    
    if weekday < 5:
        if PAUSE_WEEKDAY:
            log_message("주중 데일리 경제 뉴스 생성이 일시 중지되어 작동을 스킵합니다.")
            return
            
        today_str_full = f"{now.year}년 {now.month:02d}월 {now.day:02d}일"
        today_str_iso = now.strftime("%Y-%m-%d")
        past_history = get_past_briefings(FOLDER_PATH, count=3)
        target_rank = (now.day - 1) % 10 + 1

        log_message(f"🚀 데일리 경제 뉴스 자동 생성 시작 ({today_str_full})")

        # Phase 1
        prompt1 = (
            f"당신은 AI 경제 전문가입니다. 현재 실제 날짜는 {today_str_full}입니다. "
            f"최근 3일간의 브리핑 내용을 분석하여 중복을 방지합니다.\n"
            f"--- 이전 뉴스 이력 ---\n{past_history}\n--------------------\n\n"
            f"Google Search를 사용하여 오늘자 글로벌 주요국들의 핵심 경제 동향 중 가장 중요한 4가지(이슈 1~4)를 엄선하여 작성해 주세요.\n\n"
            f"이와 별도로 **[우리나라 코스피 상위 기업 포커스]** 섹션을 반드시 포함해야 합니다. 오늘은 **코스피 시가총액 {target_rank}위 기업**을 선정하여, "
            f"해당 기업의 **최근 2주 이내(뉴스 생성일 기준)**의 주요 동향과 이슈를 상세 분석해 주세요. (타임스탬프가 2주 이내인 정보만 사용)\n\n"
            f"각 이슈 및 기업 분석은 1)요약/데이터, 2)배경/역사적 맥락, 3)반대 시나리오, 4)한국 시장 영향력을 포함해야 합니다.\n"
            f"격조 있고 품격 있는 분량으로 작성해 주세요. 서론 및 코스피 기업 분석을 포함하여 이슈 4번까지만 작성하고 멈춰주세요."
        )
        
        content1 = _call_gemini_api(prompt1, MODEL_NAME, GEMINI_API_KEY)
        if not content1:
            log_message("❌ Phase 1 생성 실패.")
            return

        # Phase 2
        prompt2 = (
            f"당신은 AI 경제 전문가입니다. 현재 실제 날짜는 {today_str_full}입니다. "
            f"앞서 작성한 리포트(이슈 1~4 및 기업 분석)에 이어지는 **나머지 3가지 중요 이슈(이슈 5~7)**와 최종 요약을 작성해 주세요.\n"
            f"역시 최근 3일간 다른 주제들과 피해서 구성해야 합니다.\n"
            f"이슈 5, 6, 7번 역시 1)요약/데이터, 2)배경/역사적 맥락, 3)반대 시나리오, 4)한국 시장 영향력을 포함해야 합니다.\n"
            f"마지막에는 반드시 다음 요약을 포함해 주세요.\n"
            f"- [아시아 마켓 뷰]: 시장 흐름 요약\n"
            f"- [대응 전략]: 투자 포인트 3가지\n"
            f"격조 있고 품격 있는 분량으로 작성해 주세요."
        )
        
        content2 = _call_gemini_api(prompt2, MODEL_NAME, GEMINI_API_KEY)
        content = content1 + "\n\n---\n\n" + (content2 if content2 else "")
        
        os.makedirs(FOLDER_PATH, exist_ok=True)
        file_path = os.path.join(FOLDER_PATH, f"{today_str_iso}_Macro_Briefing.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        doc_link = upload_to_gdoc(file_path)
        send_telegram_alert(os.path.basename(file_path), file_path, doc_link=doc_link)
        
        try:
            popup_script = os.path.join(BASE_DIR, "notify_popup_perfect.py")
            if os.path.exists(popup_script):
                subprocess.Popen([sys.executable, popup_script])
        except: pass
    elif weekday == 5:
        generate_saturday_future_tech()
    elif weekday == 6:
        generate_sunday_philosophy()

def generate_weekend_news():
    now = datetime.datetime.now()
    weekday = now.weekday()
    if weekday == 5:
        generate_saturday_future_tech()
    elif weekday == 6:
        generate_sunday_philosophy()
    else:
        log_message("주말이 아니므로 주말 뉴스 생성을 건너뜁니다.")

def main():
    print("--------------------------------------------------")
    print("지식 브리핑 자동 생성 시스템 (Python) 대기 중..")
    print("- [평일 15:15] 데일리 경제 뉴스 생성 대기 (현재 일시정지 상태)")
    print("- [토요일 08:30] 토요일 미래/친환경 기술 보고서 생성")
    print("- [일요일 08:30] 일요일 대학 전공수준 인문철학 보고서 생성")
    print("--------------------------------------------------\n")
    schedule.every().day.at("15:15").do(generate_daily_news)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    generate_daily_news()
