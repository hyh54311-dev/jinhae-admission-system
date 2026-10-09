# -*- coding: utf-8 -*-
"""
주간 대입 입시 정보 큐레이션 및 팩트 알리미 (admission_news.py)
Multi-Agent Orchestration v4.0

[5단계 멀티에이전트 파이프라인]:
  Step 1: 입시 정책 & 대학별 속보 리서처 (Research & Draft Agent - Google Search Grounding)
  Step 2: 팩트·연도 감사관(2A) & 정원·수치 검증관(2B) (병렬 Fan-Out 팩트체커)
  Step 3: 구글 문서 내용 검토 및 수정관 (Doc Review & Pedagogical Content Editor)
  Step 4: 가독성·레이아웃 디자인 에디터 (Readability & Visual Layout Optimizer)
  Step 5: Google Drive API 퍼블리셔 (네이티브 구글 문서 발행 및 퍼블릭 읽기 권한)
  Step 6: 텔레그램 맞춤형 카드 브리핑 전송관 (헤드라인 3선 + 대학별 요약 + 구글문서 링크)

[실행 옵션]:
  - python admission_news.py --dry-run (텔레그램 전송 없이 전체 파이프라인 및 구글문서 생성 검증)
  - python admission_news.py run_now   (즉시 1회 실행 후 텔레그램 전송)
  - python admission_news.py           (매주 수요일 11:00 무인 스케줄링)
"""

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

import os
import sys
import io
import re
import time
import json
import datetime
import math
import tempfile
from concurrent.futures import ThreadPoolExecutor
import schedule
import requests
import markdown
from dotenv import load_dotenv

# ----------------- 윈도우 OS 인증서 저장소(스쿨넷 루트 CA 포함) 신뢰 주입 ----------------- #
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass
# --------------------------------------------------------------------------------------- #

# Google Drive API
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ----------------- 기본 설정 ----------------- #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
LOG_FILE = os.path.join(BASE_DIR, "admission_news.log")
REPORT_DIR = os.path.join(BASE_DIR, "대입정보_리포트")

TOKEN_PATH = os.path.join(BASE_DIR, "token.json")
if not os.path.exists(TOKEN_PATH) and os.path.exists(os.path.join(PARENT_DIR, "token.json")):
    TOKEN_PATH = os.path.join(PARENT_DIR, "token.json")

load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(PARENT_DIR, ".env"))

# Windows 콘솔 UTF-8 출력 보정 (pythonw 및 윈도우 인코딩 예외 원천 차단)
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure') and sys.stdout:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure') and sys.stderr:
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PRIMARY_MODEL = "gemini-3.6-flash"
FALLBACK_MODEL = "gemini-flash-latest"

DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

# 텔레그램 환경변수 일원화 (P0-1: 하드코딩 완전 제거)
env_tokens = os.getenv("TELEGRAM_TOKENS", "")
single_token = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_TOKENS = [t.strip() for t in env_tokens.split(",") if t.strip()]
if not TELEGRAM_TOKENS and single_token:
    TELEGRAM_TOKENS = [single_token.strip()]
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
# 스쿨넷 프록시 루트 인증서를 별도 파일로 쓰는 경우에만 .env에 경로 지정 (미설정 시 표준 검증)
CA_BUNDLE = os.getenv("SCHOOLNET_CA_BUNDLE") or True
# --------------------------------------------- #


def log_message(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    full_message = f"[{timestamp}] [AdmissionOrchestrator] {message}"
    try:
        if sys.stdout:
            print(full_message)
    except Exception:
        pass
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_message + "\n")
    except (PermissionError, OSError):
        # OneDrive 동기화 잠금 등으로 인한 파일 접근 실패 시 무시
        pass
    except Exception:
        pass


def get_month_week(dt):
    first_day = dt.replace(day=1)
    first_weekday = first_day.weekday()
    adjusted_dom = dt.day + first_weekday
    week_num = int(math.ceil(adjusted_dom / 7.0))
    return dt.month, week_num


def extract_json_from_text(text):
    """
    모든 후보 JSON 블록을 탐색하고 정화하여 '마지막' 유효 객체를 채택
    (P1-4 해결: 프롬프트 내 예시 블록 오독 방지, 후행 콤마, 주석, 스마트따옴표 보정)
    """
    if not text:
        return None

    candidates = []
    for block in re.findall(r"```(?:json)?\s*(.*?)```", text, re.S):
        candidates.append(block.strip())
    candidates.append(text.strip())

    parsed_list = []
    for c in candidates:
        for body in (c, c[c.find('{'): c.rfind('}') + 1] if '{' in c and '}' in c else ''):
            if not body:
                continue
            cleaned = re.sub(r',\s*([}\]])', r'\1', body)              # 후행 콤마 제거
            cleaned = re.sub(r'^\s*//.*$', '', cleaned, flags=re.M)     # 주석 제거
            cleaned = cleaned.replace('“', '"').replace('”', '"')       # 스마트따옴표 보정
            try:
                obj = json.loads(cleaned)
                if isinstance(obj, dict):
                    parsed_list.append(obj)
                break
            except Exception:
                continue

    return parsed_list[-1] if parsed_list else None


def call_gemini_agent(agent_name, prompt, system_instruction=None, use_search=False, json_mode=False, temperature=0.2, max_tokens=8192, timeout=90):
    """
    제미나이 에이전트 공통 호출 헬퍼 (자동 재시도, 타임아웃 제어, MAX_TOKENS 경고 감지)
    """
    if not GEMINI_API_KEY:
        log_message(f"[{agent_name}] 오류: GEMINI_API_KEY가 설정되지 않았습니다.")
        return None

    models_to_try = [PRIMARY_MODEL, FALLBACK_MODEL]

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
            
        if use_search:
            payload["tools"] = [{"googleSearch": {}}]
            if not json_mode:
                pass
        elif json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        headers = {"Content-Type": "application/json"}

        for attempt in range(2):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=timeout)
                if response.status_code == 200:
                    json_data = response.json()
                    candidates = json_data.get("candidates", [])
                    if candidates:
                        finish_reason = candidates[0].get("finishReason")
                        if finish_reason == "MAX_TOKENS":
                            log_message(f"[{agent_name}] ⚠️ 경고: 응답이 MAX_TOKENS(maxOutputTokens: {max_tokens})에 도달하여 잘렸을 수 있습니다.")
                        parts = candidates[0].get("content", {}).get("parts", [])
                        text = "".join([p.get("text", "") for p in parts]).strip()
                        if text:
                            return text
                    log_message(f"[{agent_name}] {model_name} 빈 응답 수신, 재시도...")
                elif response.status_code in (429, 503):
                    log_message(f"[{agent_name}] {model_name} HTTP {response.status_code}, 1.5초 대기 후 재시도...")
                    time.sleep(1.5)
                else:
                    log_message(f"[{agent_name}] {model_name} HTTP {response.status_code}: {response.text[:200]}")
                    break
            except Exception as e:
                log_message(f"[{agent_name}] {model_name} 호출 예외 발생 (시도 {attempt+1}): {e}")
                time.sleep(1)

    log_message(f"[{agent_name}] 모든 모델 호출에 실패했습니다.")
    return None


# =====================================================================
# 🤖 Step 1: 입시 정책 & 대학별 속보 리서처 (Research & Draft Agent)
# =====================================================================
def run_research_draft_agent(now):
    """
    Google Search Grounding을 통해 교육부, 대교협, 주요 대학 최신 대입 공지 및 정책 속보 수집
    """
    month, week = get_month_week(now)
    date_str = now.strftime('%Y년 %m월 %d일')
    log_message(f"📡 [Step 1] 입시 정책 & 대학별 속보 리서처 가동 ({date_str}, {month}월 {week}주차)...")

    sys_inst = (
        "당신은 대한민국 최고 권위의 대학입시 정책 및 진학 분석 전문 리서처입니다. "
        "교육부(MOE), 한국대학교육협의회(대교협, KCUE), 한국교육과정평가원, EBSi 및 "
        "주요 대학(서울대, 연세대, 고려대, 서강대, 성균관대, 한양대, 중앙대, 경희대 등 수도권 15개대 및 주요 거점국립대)의 "
        "가장 최신 공식 발표자료와 보도자료를 신속하고 정밀하게 수집하여 심층 분석 초안을 작성합니다."
    )

    prompt = f"""
[조사 기준일: {date_str}]
현재 시점 기준 최신 1~2주간의 대입 관련 공식 보도자료 및 대학별 최신 공지사항을 정밀 검색하여, 
교사와 수험생에게 실질적인 도움이 되는 '주간 대입 정책 및 주요 대학 전형 심층 분석 초안'을 작성해 주세요.

반드시 다음 3대 영역을 포괄해야 합니다:
1. [교육부·대교협 핵심 정책 및 제도 동향]:
   - 무전공(전공자율선택제) 확대 운영 및 세부 모집단위 변화
   - 첨단학과(반도체·AI·바이오 등) 정원 및 의대 증원/지역인재 전형 관련 최신 확정 공지
   - 2027학년도(현재 고2) 대입 기본사항 및 2028학년도(현재 고1) 대입개편안 주요 로드맵

2. [수도권 주요 15개 대학 및 거점국립대 최신 입학처 공지]:
   - 각 대학별 최신 수시/정시 요강 공지, 모의논술·입시설명회 일정, 전형방법(수능최저, 학생부 반영 등) 미세 변화

3. [현장 시사점 및 수험생 영향 분석]:
   - 이번 정책/공지 변화가 수험생 지원 성향(경쟁률, 수능최저 충족 부담 등)에 미칠 영향

정확한 사실과 출처를 바탕으로 충실한 분량의 원고 초안을 작성해 주세요.
"""
    draft = call_gemini_agent("ResearchDraftAgent", prompt, system_instruction=sys_inst, use_search=True, temperature=0.2)
    return draft


# =====================================================================
# 🔍 Step 2A: 팩트·연도 감사관 (Timeline & Cohort Auditor)
# =====================================================================
def run_timeline_auditor(draft, now):
    """
    2027학년도(현재 고2) vs 2028학년도(현재 고1 개편안) 전형 연도 오류 및 일정 교차검증
    """
    log_message("⏳ [Step 2A] 팩트·연도 감사관 가동 (2027 vs 2028 전형 연도 엄격 검증)...")

    sys_inst = (
        "당신은 대한민국 대학입시 전형 연도 및 학년도별 교육과정 일치성을 검사하는 최고 감사관입니다. "
        "입시 리포트에서 흔히 발생하는 연도 오류(예: 2028학년도 통합수능/5등급제 개편 내용을 2027학년도에 잘못 적용하는 오류 등)를 "
        "완벽히 적발하고 교정 가이드를 제시합니다."
    )

    prompt = f"""
현재 날짜는 {now.strftime('%Y년 %m월 %d일')}입니다.
- 현재 고3: 2026/2027학년도 대입 대상
- 현재 고2: 2027학년도 대입 준비생
- 현재 고1: 2028학년도 대입 대상 (2028 개편안: 통합형 수능, 고교 내신 5등급 체제 적용)

아래 대입 분석 리포트 초안을 읽고, 전형 연도 오류가 있는지 정밀 검증하세요.

반드시 아래 스키마의 JSON "하나만" 출력하세요. 설명·인사말·예시 재출력 금지.
{{
  "is_pass": <true|false>,
  "detected_errors": [<발견된_오류_문자열_목록>],
  "correction_guide": "<교정_가이드_문자열>"
}}

[검증 대상 초안]:
{draft}
"""
    raw = call_gemini_agent("TimelineAuditor", prompt, system_instruction=sys_inst, json_mode=False, temperature=0.0, timeout=45)
    parsed = extract_json_from_text(raw)
    if parsed and "is_pass" in parsed:
        log_message(f"Step 2A 결과: Pass={parsed.get('is_pass')}, 오류={len(parsed.get('detected_errors', []))}건")
        return parsed

    log_message(f"⚠️ Step 2A 감사 실패(응답 파싱 불가). 원문 앞 200자: {str(raw)[:200]}")
    return {
        "is_pass": None,
        "audit_failed": True,
        "detected_errors": [],
        "correction_guide": "감사 미수행 — 연도 표기를 사람이 직접 확인할 것"
    }


# =====================================================================
# 📊 Step 2B: 정원·수치 검증관 (Statistics & Quota Auditor)
# =====================================================================
def run_quota_auditor(draft):
    """
    의대 증원, 무전공(유형1, 유형2) 선발 정원, 주요 대학별 모집 인원 실시간 교차검증
    """
    log_message("🔢 [Step 2B] 정원·수치 검증관 가동 (모집인원 및 통계 팩트체크)...")

    sys_inst = (
        "당신은 대학별 모집인원, 전형별 비율, 정원 증원 수치를 공식 보도자료와 대조 검증하는 팩트체크 에이전트입니다. "
        "언론 추정치와 정부 공식 확정치를 엄격히 구분하고, 리포트 본문의 수치적 정확성을 보증합니다."
    )

    prompt = f"""
아래 대입 리포트 초안에 언급된 모든 수치(대학별 모집인원, 무전공 선발 규모, 의대 정원, 비율 등)의 사실관계를 구글 검색을 통해 공식 발표와 대조 검증하세요.

[검증 대상 초안]:
{draft[:4000]}

반드시 아래 스키마의 JSON "하나만" 출력하세요. 설명·인사말·예시 재출력 금지.
{{
  "is_pass": <true|false>,
  "number_issues": [<발견된_수치_오류_문자열_목록>],
  "correction_guide": "<수치_교정_가이드_문자열>"
}}
"""
    raw = call_gemini_agent("QuotaAuditor", prompt, system_instruction=sys_inst, use_search=True, json_mode=False, temperature=0.0, timeout=45)
    parsed = extract_json_from_text(raw)
    if parsed and "is_pass" in parsed:
        log_message(f"Step 2B 결과: Pass={parsed.get('is_pass')}, 수치이슈={len(parsed.get('number_issues', []))}건")
        return parsed

    log_message(f"⚠️ Step 2B 감사 실패(응답 파싱 불가). 원문 앞 200자: {str(raw)[:200]}")
    return {
        "is_pass": None,
        "audit_failed": True,
        "number_issues": [],
        "correction_guide": "감사 미수행 — 모집정원 및 수치를 사람이 직접 확인할 것"
    }


# =====================================================================
# 📝 Step 3: 구글 문서 내용 검토 및 수정관 (Doc Review & Content Editor)
# =====================================================================
def run_doc_content_review_agent(draft, timeline_feedback, quota_feedback):
    """
    초안과 2단계 감사 피드백을 반영하여 교육적 통찰과 실무 전략을 심층 보강하는 내용 검토관
    """
    log_message("🎓 [Step 3] 구글 문서 내용 검토 및 수정관 가동 (심층 분석 및 전략 보강)...")

    sys_inst = (
        "당신은 시도교육청 진학지도지원단 수석연구원이자 대입 전략 전문 칼럼니스트입니다. "
        "단순 뉴스 브리핑 수준의 피상적인 글을 교사, 학부모, 학생이 실제 진학 상담에 바로 활용할 수 있는 "
        "'최고급 대입 심층 분석 리포트'로 발전시키는 내용 검토 및 전문 교열을 전담합니다."
    )

    prompt = f"""
초안 및 팩트 감사관의 피드백을 반영하여 완성도 높은 구글 문서용 본문을 재작성해 주세요.

[초안]:
{draft}

[연도 감사관 피드백]:
{json.dumps(timeline_feedback, ensure_ascii=False, indent=2)}

[정원 수치 검증관 피드백]:
{json.dumps(quota_feedback, ensure_ascii=False, indent=2)}

[내용 보강 필수 요구사항]:
1. 피상적인 사실 나열을 배제하고, '해당 정책/전형 변화가 특정 성적대 수험생에게 미치는 유불리'를 구체적으로 서술하세요.
2. 주요 대학별(서연고, 서성한, 중경외시 등) 전형 차이점(수능최저, 탐구 반영 방식, 정시 내신 반영 여부)을 명확한 비교로 서술하세요.
3. 고교 현장 교사와 수험생을 위한 '주간 실천 전략 가이드'를 현실적이고 구체적인 조언으로 포함하세요.
4. 감사관의 지적 사항(연도 오류, 수치 오류)은 100% 교정하여 반영하세요.
"""
    reviewed = call_gemini_agent("DocReviewContentEditor", prompt, system_instruction=sys_inst, temperature=0.2)
    return reviewed


# =====================================================================
# 🎨 Step 4: 가독성·레이아웃 디자인 에디터 (Readability & Layout Optimizer)
# =====================================================================
def run_readability_layout_agent(reviewed_content, now, audit_warnings=None):
    """
    가독성을 극대화하기 위해 표, 콜아웃 박스, 3줄 요약 카드로 구조화하고 세련된 HTML/CSS 렌더링
    (상단 고정 안내 배너 및 팩트 감사 경고 박스 자동 주입)
    """
    month, week = get_month_week(now)
    date_str = now.strftime('%Y년 %m월 %d일')
    log_message("📐 [Step 4] 가독성·레이아웃 디자인 에디터 가동 (표·콜아웃 구조화 및 CSS 스타일링)...")

    sys_inst = (
        "당신은 구글 문서(Google Docs) 전문 시각화 및 문서 편집 디자이너 에이전트입니다. "
        "텍스트가 빽빽하게 나열된 리포트를 한눈에 읽히도록 구조화(3줄 요약 카드, 비교 표, Callout 인용구, 글머리 기호)하여 "
        "최고 수준의 가독성을 가진 정갈한 마크다운 문서로 변환합니다."
    )

    prompt = f"""
[발행 정보: {date_str} ({month}월 {week}주차)]
아래 검토 완료된 대입 리포트를 가독성이 극대화된 구조화 마크다운 문서로 재구성해 주세요.

[검토 완료 본문]:
{reviewed_content}

[가독성 재구성 규칙]:
1. **문서 상단 [📌 이번 주 대입 핵심 브리핑 (3-Line Summary)] 카드**: 가장 중요한 3대 핵심 이슈를 명확한 불릿으로 요약.
2. **비교 표(Markdown Table) 적극 도입**: 대학별 전형 변화나 정책 비교는 반드시 마크다운 표로 깔끔하게 정리.
3. **핵심 강조 Callout 박스**: 주의사항 및 전문가 핵심 전략은 `> 💡 [핵심 전략]` 또는 `> ⚠️ [주의사항]` 인용 블록으로 강조.
4. **시각적 계층화**: H1(#), H2(##), H3(###)를 체계적으로 구분하고 단락 간 여백을 충분히 확보.
5. **문서 하단 [🎯 고교 현장 주간 체크포인트]**: 학년별(고1/고2/고3) 필수 점검 과제를 체크박스 형식(`- [ ]`)으로 제시.

오직 정돈된 마크다운 전문만 출력해 주세요. 불필요한 인사말이나 코드 블록 기호(```markdown 등)는 제외하세요.
"""
    structured_md = call_gemini_agent("ReadabilityOptimizer", prompt, system_instruction=sys_inst, temperature=0.2, timeout=90)
    if not structured_md:
        structured_md = reviewed_content

    # 앞뒤 코드 블록 기호 제거
    clean_md = structured_md.replace("```markdown", "").replace("```", "").strip()

    # 마크다운을 확장 HTML로 변환
    html_body = markdown.markdown(clean_md, extensions=['extra', 'tables', 'nl2br'])

    # 팩트 감사관 주의 배너 구성
    audit_banner_html = ""
    if audit_warnings:
        audit_banner_html = f'''
<div class="audit-alert-banner">
    🚨 <strong>[팩트 감사관 주의 알림]</strong> 자동 팩트 검증 과정에서 다음 주의 항목이 보고되었습니다. 지원 전략 수립 시 대학별 공식 요강과의 대조가 필수적입니다:<br>
    {audit_warnings}
</div>
'''

    # 구글 문서 최적화 고급 CSS 스타일 템플릿
    styled_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
    body {{
        font-family: '맑은 고딕', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
        font-size: 11pt;
        line-height: 1.75;
        color: #1e293b;
        background-color: #ffffff;
        margin: 0;
        padding: 24px;
    }}
    .disclaimer-banner {{
        border: 2px solid #f59e0b;
        background-color: #fffbeb;
        color: #b45309;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 22px;
        font-size: 10.5pt;
        line-height: 1.6;
    }}
    .audit-alert-banner {{
        border: 2px solid #ef4444;
        background-color: #fef2f2;
        color: #991b1b;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 22px;
        font-size: 10.5pt;
        line-height: 1.6;
    }}
    h1 {{
        color: #0f172a;
        font-size: 20pt;
        font-weight: 800;
        border-bottom: 3px solid #2563eb;
        padding-bottom: 10px;
        margin-top: 10px;
        margin-bottom: 25px;
    }}
    h2 {{
        color: #1e40af;
        font-size: 14pt;
        font-weight: 700;
        border-left: 5px solid #2563eb;
        padding-left: 12px;
        margin-top: 35px;
        margin-bottom: 15px;
        background-color: #f8fafc;
        padding-top: 6px;
        padding-bottom: 6px;
    }}
    h3 {{
        color: #334155;
        font-size: 12pt;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 10px;
    }}
    p {{
        margin-top: 0;
        margin-bottom: 14px;
        text-align: justify;
    }}
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
        font-size: 10pt;
    }}
    th, td {{
        border: 1px solid #cbd5e1;
        padding: 10px 12px;
        text-align: left;
    }}
    th {{
        background-color: #f1f5f9;
        font-weight: bold;
        color: #0f172a;
        border-bottom: 2px solid #94a3b8;
    }}
    tr:nth-child(even) {{
        background-color: #f8fafc;
    }}
    blockquote {{
        border-left: 4px solid #3b82f6;
        background-color: #eff6ff;
        color: #1e3a8a;
        margin: 18px 0;
        padding: 12px 16px;
        border-radius: 0 6px 6px 0;
    }}
    ul, ol {{
        margin-top: 0;
        margin-bottom: 14px;
        padding-left: 24px;
    }}
    li {{
        margin-bottom: 6px;
    }}
    strong {{
        color: #0f172a;
        font-weight: 700;
    }}
    .footer-note {{
        margin-top: 40px;
        padding-top: 15px;
        border-top: 1px dashed #cbd5e1;
        color: #64748b;
        font-size: 9pt;
        text-align: center;
    }}
</style>
</head>
<body>
<div class="disclaimer-banner">
    ⚠️ <strong>[대입 진학 지도 유의사항]</strong> 본 리포트는 AI 멀티에이전트가 자동 수집·분석한 참고 자료입니다. 실제 수시/정시 지원 결정 및 원서 작성 전 반드시 각 대학 입학처의 2027/2028학년도 최종 모집요강 원문을 재확인하시기 바랍니다.
</div>
{audit_banner_html}
{html_body}
<div class="footer-note">
    본 리포트는 진해고등학교 대입 정보 알리미 시스템(Gemini Orchestrator v4.1)에 의해 자동 생성·검증된 문서입니다.
</div>
</body>
</html>
"""
    return clean_md, styled_html


# =====================================================================
# ☁️ Step 5: Google Drive API 퍼블리셔 (Google Doc 발행)
# =====================================================================
def publish_to_google_docs(styled_html, doc_title, is_dry_run=False, folder_id=None):
    """
    Google Drive API를 활용하여 스타일 HTML을 네이티브 구글 문서로 업로드하고 퍼블릭/비공개 링크 생성
    (P1-8: 드라이런 시 퍼블릭 권한 생략 및 전용 폴더 지원, P2-10: 임시 파일 안전 정리)
    """
    log_message(f"☁️ [Step 5] Google Drive API 퍼블리셔 가동 ('{doc_title}' 발행)...")

    if not os.path.exists(TOKEN_PATH):
        log_message(f"경고: {TOKEN_PATH}가 존재하지 않아 구글 문서 발행을 건너뜁니다.")
        return None, None

    temp_html_path = None
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, DRIVE_SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_PATH, 'w', encoding='utf-8') as f:
                f.write(creds.to_json())

        drive_service = build('drive', 'v3', credentials=creds)

        # 시스템 임시 디렉터리에 고유 파일로 생성하여 REPORT_DIR 오염 방지
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(styled_html)
            temp_html_path = temp_file.name

        file_metadata = {
            'name': doc_title,
            'mimeType': 'application/vnd.google-apps.document'
        }
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(temp_html_path, mimetype='text/html', resumable=True)

        doc_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        doc_id = doc_file.get('id')
        web_link = doc_file.get('webViewLink')

        # 퍼블릭 읽기 권한 부여 (드라이런이 아닐 때만 전체 공개)
        if not is_dry_run:
            try:
                drive_service.permissions().create(
                    fileId=doc_id,
                    body={'type': 'anyone', 'role': 'reader'}
                ).execute()
                log_message(f"구글 문서 퍼블릭 읽기 권한 설정 완료 (Doc ID: {doc_id})")
            except Exception as pe:
                log_message(f"권한 설정 경고: {pe}")
        else:
            log_message("🧪 [DRY-RUN] 퍼블릭 공개 권한 부여를 생략했습니다 (작성자 본인만 열람 가능).")

        # Windows 파일 핸들 해제 및 임시 HTML 삭제
        media = None
        if temp_html_path and os.path.exists(temp_html_path):
            try:
                os.remove(temp_html_path)
            except Exception:
                pass

        # 이전 버전 잔재 파일 정리
        legacy_temp = os.path.join(REPORT_DIR, "temp_upload.html")
        if os.path.exists(legacy_temp):
            try:
                os.remove(legacy_temp)
            except Exception:
                pass

        log_message(f"✅ 구글 문서 발행 성공! 링크: {web_link}")
        return web_link, doc_id

    except Exception as e:
        log_message(f"구글 문서 발행 실패: {e}")
        if temp_html_path and os.path.exists(temp_html_path):
            try:
                os.remove(temp_html_path)
            except Exception:
                pass
        return None, None


# =====================================================================
# 📱 Step 6: 텔레그램 맞춤형 카드 브리핑 전송관
# =====================================================================
def extract_telegram_summary(clean_md, gdoc_link, now, audit_issues_count=0):
    """
    구글 문서 링크와 연동된 고밀도 텔레그램 카드 메시지 생성
    """
    month, week = get_month_week(now)
    date_str = now.strftime('%Y.%m.%d')

    prompt = f"""
아래 대입 리포트 마크다운 본문을 바탕으로, 모바일 텔레그램에서 한눈에 읽히는 [초압축 카드형 브리핑 메시지]를 작성해 주세요.

[본문]:
{clean_md[:3000]}

[작성 규칙]:
- 전체 길이는 700자 내외로 간결하고 임팩트 있게 작성.
- 텔레그램은 서식이 적용되지 않으므로 별표(**), 밑줄(_), 백틱(`) 등 마크다운 기호를 절대 쓰지 마세요. 강조가 필요하면 【 】 또는 줄바꿈과 이모지로 구분하십시오.
- 구성:
  🎓 [주간 대입 입시 심층 브리핑] ({month}월 {week}주차)
  📅 일자: {date_str}

  📌 이번 주 핵심 정책 3선
  1. ...
  2. ...
  3. ...

  🏛️ 주요 대학 전형 변화 포인트
  • ...
  • ...

  🎯 수험생/교사 주간 실천 가이드
  • ...

불필요한 서두는 빼고 텔레그램 메시지 본문만 출력해 주세요.
"""
    summary_text = call_gemini_agent("TelegramCardGenerator", prompt, temperature=0.2, timeout=60)
    if not summary_text:
        summary_text = f"🎓 [주간 대입 입시 심층 브리핑] ({month}월 {week}주차)\n📅 일자: {date_str}\n\n이번 주 최신 대입 정책 및 주요 대학 전형 변화 분석이 완료되었습니다."
    else:
        # 텔레그램은 parse_mode 미사용 → 마크다운 기호가 글자로 보이므로 제거 (F-2 해결)
        summary_text = re.sub(r'\*\*(.+?)\*\*', r'\1', summary_text)
        summary_text = re.sub(r'(?<!\w)[*_`]{1,2}(?=\S)|(?<=\S)[*_`]{1,2}(?!\w)', '', summary_text)

    warning_section = ""
    if audit_issues_count > 0:
        warning_section = f"\n⚠️ [팩트체크 알림] 자동 감사에서 {audit_issues_count}건의 확인 권고 항목이 보고되었습니다. 입학처 요강 원문을 반드시 교차 확인하십시오.\n"

    gdoc_section = ""
    if gdoc_link:
        gdoc_section = f"\n━━━━━━━━━━━━━━━━━━━━\n📄 [고화질 구글 문서 전문 열람]\n👉 {gdoc_link}\n━━━━━━━━━━━━━━━━━━━━"
    else:
        gdoc_section = "\n\n(로컬 리포트 폴더에 저장되었습니다.)"

    final_telegram_msg = summary_text.strip() + warning_section + gdoc_section
    return final_telegram_msg


def send_telegram_alert(message_text):
    """
    복수 텔레그램 봇 토큰 폴백 + 4096자 줄 단위 안전 분할 (P0-2: TLS 검증 복구, F-3: URL 절단 방지 줄 단위 분할)
    """
    if not TELEGRAM_TOKENS or not TELEGRAM_CHAT_ID:
        log_message("텔레그램 토큰/챗ID가 설정되지 않았습니다 (.env 확인 필요).")
        return False

    # 텔레그램 단일 메시지 상한 4096자 → 3800자 단위 줄 기반 안전 분할 (F-3 해결: URL 절단 방지)
    LIMIT = 3800
    chunks, buf = [], ""
    for line in message_text.split("\n"):
        # 한 줄 자체가 상한을 넘으면 그 줄만 불가피하게 문자 단위로 분할
        if len(line) > LIMIT:
            if buf:
                chunks.append(buf); buf = ""
            for i in range(0, len(line), LIMIT):
                chunks.append(line[i:i + LIMIT])
            continue
        if len(buf) + len(line) + 1 > LIMIT:
            chunks.append(buf); buf = line
        else:
            buf = line if not buf else buf + "\n" + line
    if buf:
        chunks.append(buf)
    if not chunks:
        chunks = [""]

    for token in TELEGRAM_TOKENS:
        bot_id = token.split(':')[0] if ':' in token else 'invalid'
        try:
            for idx, chunk in enumerate(chunks):
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                payload = {"chat_id": TELEGRAM_CHAT_ID, "text": chunk}
                res = requests.post(url, json=payload, timeout=15, verify=CA_BUNDLE)
                res.raise_for_status()

                if idx < len(chunks) - 1:
                    time.sleep(0.5)
            log_message(f"✅ 텔레그램 전송 성공! ({len(chunks)}건 분할 전송, Bot ID: {bot_id})")
            return True
        except Exception as e:
            log_message(f"텔레그램 전송 실패 (Bot ID: {bot_id}): {e}")

    log_message("❌ 모든 텔레그램 봇 전송에 실패했습니다.")
    return False


# =====================================================================
# 🚀 메인 오케스트레이션 파이프라인 (Master Pipeline)
# =====================================================================
def execute_admission_news_pipeline(is_dry_run=False):
    """
    6단계 멀티에이전트 오케스트레이션 전체 실행 디스패처
    """
    now = datetime.datetime.now()
    month, week = get_month_week(now)
    doc_title = f"{now.strftime('%Y%m%d')}_대입_심층_리포트_{month}월{week}주차"

    log_message("=" * 65)
    log_message(f"🎓 주간 대입 입시 정보 멀티에이전트 오케스트레이션 시작 ({doc_title})")
    if is_dry_run:
        log_message("🧪 [DRY-RUN 모드] 텔레그램 실제 발송은 생략됩니다.")
    log_message("=" * 65)

    # Step 1: 리서치 초안 작성
    draft = run_research_draft_agent(now)
    if not draft:
        log_message("치명적 오류: Step 1 초안 생성 실패로 파이프라인을 중단합니다.")
        return False

    # Step 2: 팩트 감사 병렬 진행 (P1-6: True Parallel Fan-Out)
    with ThreadPoolExecutor(max_workers=2) as executor:
        f_timeline = executor.submit(run_timeline_auditor, draft, now)
        f_quota = executor.submit(run_quota_auditor, draft)
        timeline_feedback = f_timeline.result()
        quota_feedback = f_quota.result()

    # 감사 이슈 집계
    audit_issues = []
    if timeline_feedback.get("audit_failed"):
        audit_issues.append("연도 감사관: 응답 파싱 실패로 사람이 직접 연도 표기를 확인할 것")
    elif not timeline_feedback.get("is_pass"):
        errs = timeline_feedback.get("detected_errors", [])
        guide = timeline_feedback.get("correction_guide", "")
        audit_issues.append(f"연도 감사관 지적 ({len(errs)}건): {', '.join(errs[:3])} (가이드: {guide})")

    if quota_feedback.get("audit_failed"):
        audit_issues.append("정원 감사관: 응답 파싱 실패로 사람이 직접 모집인원 및 수치를 확인할 것")
    elif not quota_feedback.get("is_pass"):
        errs = quota_feedback.get("number_issues", [])
        guide = quota_feedback.get("correction_guide", "")
        audit_issues.append(f"정원 감사관 지적 ({len(errs)}건): {', '.join(errs[:3])} (가이드: {guide})")

    audit_warnings_html = "<br>• " + "<br>• ".join(audit_issues) if audit_issues else ""

    # Step 3: 구글 문서 내용 검토 및 수정
    reviewed_content = run_doc_content_review_agent(draft, timeline_feedback, quota_feedback)
    if not reviewed_content:
        log_message("내용 검토관 응답 실패, 초안을 유지합니다.")
        reviewed_content = draft

    # Step 4: 가독성 및 레이아웃 최적화 (상단 배너 및 감사 알림 주입)
    clean_md, styled_html = run_readability_layout_agent(reviewed_content, now, audit_warnings=audit_warnings_html)

    # 로컬 저장소 백업
    os.makedirs(REPORT_DIR, exist_ok=True)
    md_file_path = os.path.join(REPORT_DIR, f"{doc_title}.md")
    html_file_path = os.path.join(REPORT_DIR, f"{doc_title}.html")
    with open(md_file_path, "w", encoding="utf-8") as f:
        f.write(clean_md)
    with open(html_file_path, "w", encoding="utf-8") as f:
        f.write(styled_html)
    log_message(f"로컬 리포트 저장 완료: {md_file_path}")

    # Step 5: Google Drive API 네이티브 문서 발행 (드라이런/폴더 격리 지원)
    gdoc_link, doc_id = publish_to_google_docs(styled_html, doc_title, is_dry_run=is_dry_run, folder_id=DRIVE_FOLDER_ID)

    # Step 6: 텔레그램 카드 메시지 생성 및 전송
    telegram_card_msg = extract_telegram_summary(clean_md, gdoc_link, now, audit_issues_count=len(audit_issues))

    if is_dry_run:
        log_message("\n" + "─" * 40 + "\n[텔레그램 전송 미리보기]:\n" + telegram_card_msg + "\n" + "─" * 40)
        log_message("✅ [DRY-RUN] 전체 파이프라인이 성공적으로 검증되었습니다!")
        return True
    else:
        success = send_telegram_alert(telegram_card_msg)
        if success:
            log_message("🎉 주간 대입 입시 정보 발행 및 텔레그램 전송 완결!")
        return success


def main():
    try:
        if len(sys.argv) > 1:
            arg = sys.argv[1].lower()
            if arg in ("--dry-run", "--test", "test"):
                execute_admission_news_pipeline(is_dry_run=True)
                return
            elif arg in ("run_now", "--run-now", "run"):
                execute_admission_news_pipeline(is_dry_run=False)
                return

        log_message("📅 [스케줄러 대기 중] 매주 수요일 11:00 정기 자동 실행 모드 가동...")
        schedule.every().wednesday.at("11:00").do(execute_admission_news_pipeline, is_dry_run=False)
        while True:
            schedule.run_pending()
            time.sleep(60)
    except Exception as e:
        import traceback
        log_message(f"치명적 오류 발생(main): {e}\n{traceback.format_exc()}")


if __name__ == "__main__":
    main()
