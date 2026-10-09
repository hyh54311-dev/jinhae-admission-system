#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
텔레그램 자동 뉴스 브리핑 시스템 (뉴스 오케스트레이터)
================================================================================
- 제미나이 API 키 미의존: 100% 공신력 있는 언론사(연합뉴스, BBC 코리아 등) 취재 보도 크롤링
- 5단계 검수 & 정제 파이프라인:
    1단계 [공신력 다채널 수집]: 연합뉴스 국제/종합/정치/경제/사회 + BBC 코리아 + 구글뉴스
    2단계 [시간 유효성 & 잡음 필터링]: 최신 기사 선별, 포토/단신/가십/광고 배제
    3단계 [키워드 군집화 & 중복 제거]: 중복 기사 통합, 중요도 가중치 기반 Top 8~10 선별
    4단계 [심층 본문 크롤링 & 팩트 구조화]: 육하원칙 핵심 요약, 배경 맥락, 수치, 기자 바이라인 추출
    5단계 [텔레그램 안전 검수 & 분할 전송]: 4,096자 제한 대응 자동 분할, HTML 엔티티 정제
- 스케줄:
    * 오전 07:00 KST: 밤사이 주요 외신 뉴스 약 8~10개
    * 오후 21:00 KST: 당일 주요 국내 뉴스 (정치·경제·사회 균형)
================================================================================
"""

import os
import sys
import io
import re
import html
import time
import argparse
import datetime
from email.utils import parsedate_to_datetime
from difflib import SequenceMatcher
import ssl
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Windows OS 신뢰 인증서 저장소(학내망/기관망 SSL) 자동 연동 (P1 반영)
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

# Windows 콘솔 UTF-8 입출력 강제 설정
if sys.platform == 'win32':
    try:
        if sys.stdout and hasattr(sys.stdout, 'buffer') and getattr(sys.stdout, 'encoding', None) and sys.stdout.encoding.lower() != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        if sys.stderr and hasattr(sys.stderr, 'buffer') and getattr(sys.stderr, 'encoding', None) and sys.stderr.encoding.lower() != 'utf-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

# ----------------- 기본 경로 및 환경변수 설정 ----------------- #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "news_briefing.log")

# .env 로드
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# ----------------- 로깅 함수 ----------------- #
def log(msg):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{now_str}] {msg}"
    print(formatted)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

# ----------------- 네트워크 헬퍼 ----------------- #
HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

def safe_fetch_url(url, timeout=10):
    """안전한 HTTP/HTTPS URL 요청 (OS 신뢰 인증서 저장소 기반 표준 SSL 검증 수행)"""
    try:
        req = urllib.request.Request(url, headers=HTTP_HEADERS)
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read()
    except Exception as e:
        log(f"URL 요청 실패 ({url}): {e}")
        return None

# ==============================================================================
# 1단계 & 2단계: 다채널 수집 및 시간/품질 필터링 (Ingestion & Quality Filtering)
# ==============================================================================
def parse_feed_items(feed_url, default_source="언론사"):
    """RSS 피드 파싱 후 표준 딕셔너리 리스트 반환 (ET 실패 시 BeautifulSoup XML 내결함성 파서 자동 폴백)"""
    data = safe_fetch_url(feed_url)
    if not data:
        return []
    
    items = []
    # 1차 시도: 고속 표준 ElementTree 파서
    try:
        root = ET.fromstring(data)
        for item in root.findall('.//item'):
            title = item.find('title').text.strip() if item.find('title') is not None and item.find('title').text else ""
            link = item.find('link').text.strip() if item.find('link') is not None and item.find('link').text else ""
            pub_date_str = item.find('pubDate').text.strip() if item.find('pubDate') is not None and item.find('pubDate').text else ""
            desc = item.find('description').text.strip() if item.find('description') is not None and item.find('description').text else ""
            source = item.find('source').text.strip() if item.find('source') is not None and item.find('source').text else default_source

            if not title or not link:
                continue

            # HTML 태그 제거 및 순수 텍스트 정제
            if '<' in title and '>' in title:
                title = BeautifulSoup(title, 'html.parser').get_text(separator=' ', strip=True)
            if '<' in desc and '>' in desc:
                desc = BeautifulSoup(desc, 'html.parser').get_text(separator=' ', strip=True)

            pub_dt = None
            if pub_date_str:
                try:
                    pub_dt = parsedate_to_datetime(pub_date_str)
                except Exception:
                    pub_dt = None

            items.append({
                'title': title,
                'link': link,
                'pub_date': pub_dt,
                'pub_date_str': pub_date_str,
                'desc': desc,
                'source': source
            })
        if items:
            return items
    except Exception as e:
        log(f"  [안내] 표준 XML 파싱 예외({e}) -> BeautifulSoup(lxml) 내결함성 파서로 자동 전환")

    # 2차 시도: 비표준 엔티티(& 등) 포용적 BeautifulSoup/lxml 파서
    try:
        soup = BeautifulSoup(data, 'xml')
        for item in soup.find_all('item'):
            t_node = item.find('title')
            l_node = item.find('link')
            p_node = item.find('pubDate') or item.find('pubdate')
            d_node = item.find('description')
            s_node = item.find('source')

            title = t_node.get_text(strip=True) if t_node else ""
            link = l_node.get_text(strip=True) if l_node else ""
            pub_date_str = p_node.get_text(strip=True) if p_node else ""
            desc = d_node.get_text(strip=True) if d_node else ""
            source = s_node.get_text(strip=True) if s_node else default_source

            if not title or not link:
                continue

            if '<' in title and '>' in title:
                title = BeautifulSoup(title, 'html.parser').get_text(separator=' ', strip=True)
            if '<' in desc and '>' in desc:
                desc = BeautifulSoup(desc, 'html.parser').get_text(separator=' ', strip=True)

            pub_dt = None
            if pub_date_str:
                try:
                    pub_dt = parsedate_to_datetime(pub_date_str)
                except Exception:
                    pub_dt = None

            items.append({
                'title': title,
                'link': link,
                'pub_date': pub_dt,
                'pub_date_str': pub_date_str,
                'desc': desc,
                'source': source
            })
    except Exception as e2:
        log(f"피드 2차 파싱 에러 ({feed_url}): {e2}")

    return items

def is_noise_article(title):
    """단순 가십, 연예, 날씨, 스포츠, 포토단신 및 기업 홍보/이벤트 잡음 기사 검수 및 차단"""
    # 1. 무조건 차단 잡음 패턴 (가십, 연예, 날씨, 스포츠, 명백한 상업 프로모션)
    noise_patterns = [
        r"\[포토\]", r"\[화보\]", r"\[인사\]", r"\[부고\]", r"\[동정\]",
        r"로또", r"운세", r"오늘의 운세", r"날씨",
        # 스포츠 노이즈 철저 차단
        r"프로야구", r"가을야구", r"KBO", r"골프", r"축구", r"야구", r"농구", r"배구",
        r"손흥민", r"이강인", r"김민재", r"황희찬", r"메이저리그", r"MLB", r"EPL",
        r"홈런", r"안타", r"완투", r"호투", r"타율", r"선발승", r"2연승", r"3연승", r"연패",
        r"두산", r"LG트윈스", r"KIA", r"삼성라이온즈", r"SSG", r"키움", r"한화이글스",
        # 연예/가십 차단
        r"팬미팅", r"시청률", r"결혼", r"이혼", r"음주운전", r"마약", r"단독입수",
        # 명백한 상업 프로모션 패턴
        r"한정\s*판매", r"협업\s*컬렉션", r"팝업스토어", r"박람회\s*참가",
        r"경품", r"이벤트", r"특가", r"출석체크", r"할인행사", r"할인\s*프로모션", r"레드카펫\s*입양제"
    ]
    for pat in noise_patterns:
        if re.search(pat, title, re.IGNORECASE):
            return True

    # 2. [P2 반영] 종목코드([005930] 등)가 포함된 기사의 경우:
    # 단독 차단하지 않고, '홍보/출시/이벤트/마케팅' 성격이 결합되었을 때만 차단
    # (실적, 영업이익, 매출, 수출입, 관세, 투자, 인수합병 등 주요 경제 뉴스는 철저히 보존)
    if re.search(r"\[\d{6}\]", title):
        pr_keywords = [r"출시", r"패키지", r"선보여", r"선보인다", r"기념", r"입점", r"오픈", r"신제품", r"참가한다고.*밝혔다"]
        for pr_pat in pr_keywords:
            if re.search(pr_pat, title, re.IGNORECASE):
                if not re.search(r"실적|영업이익|매출|수출|투자|관세|인수|합병|공시", title):
                    return True

    return False

# ==============================================================================
# 3단계: 키워드 군집화 & 중복 제거 (De-duplication & Topic Clustering)
# ==============================================================================
# [N2 요구사항 반영] 흔한 고유명사 및 범용 뉴스 어휘 불용어 사전
EVENT_STOP_WORDS = {
    '트럼프', '바이든', '미국', '한국', '북한', '러시아', '우크라이나', '중국', '이스라엘', '이란', '일본',
    '정부', '대통령', '총리', '장관', '의원', '국회', '군', '당국', '서울', '워싱턴', '뉴욕', 'AI', '인공지능',
    '오늘', '어제', '내일', '최근', '논란', '결국', '종합', '속보', '단독', '기자', '특파원', '이유', '관련', '대해'
}

def extract_title_keywords(title):
    """제목에서 불용어가 제외된 핵심 사건 명사/키워드 토큰 추출 (M2: 단어 간 하이픈 美-中 등 온전히 보존)"""
    clean_title = re.sub(r"\[.*?\]|\(.*?\)|<.*?>|'|\"|“|”|‘|’|…|\.\.\.|\s+-\s+[^-]+$", " ", title)
    tokens = [w for w in re.findall(r'[가-힣a-zA-Z0-9]{2,}', clean_title) if len(w) >= 2]
    return set([t for t in tokens if t not in EVENT_STOP_WORDS])

def normalize_title_for_comparison(title):
    """비교를 위한 제목 정규화 (특수문자, 인용부호 등 제거, M2: 하이픈 복합어 보존)"""
    t = re.sub(r"\[.*?\]|\(.*?\)|<.*?>|\s+-\s+[^-]+$", "", title)
    t = re.sub(r"['\"“”‘’…\.\,\s\?\!\:\;\-]", "", t)
    return t

def is_same_topic_event(title1, title2, kws1, kws2):
    """
    [N2 요구사항 반영] 상이한 언론사 간 동일 사건 보도 정밀 판정:
    - 단순 공통 엔티티(트럼프, 미국, 대통령 등)로 인한 오탐을 방지하기 위해 EVENT_STOP_WORDS 배제
    - '하나라도 충족'이 아닌 유사도와 고유 사건 어근(root) 일치를 복합 요구하여 과군집화 방지
    1. 고유사도(0.50 이상) + 최소 1개 고유 사건 어근 일치
    2. 중유사도(0.35 이상) + 2개 이상 구체적 사건 어근 일치 (예: 사형, 생존)
    3. 3개 이상 구체적 사건 어근 일치
    """
    norm1 = normalize_title_for_comparison(title1)
    norm2 = normalize_title_for_comparison(title2)
    ratio = SequenceMatcher(None, norm1, norm2).ratio() if (norm1 and norm2) else 0

    # 불용어가 이미 배제된 고유 사건 키워드 기반 2음절 어근 추출
    ev_kws1 = set([w for w in kws1 if w not in EVENT_STOP_WORDS])
    ev_kws2 = set([w for w in kws2 if w not in EVENT_STOP_WORDS])
    roots1 = set([w[:2] for w in ev_kws1 if len(w) >= 2])
    roots2 = set([w[:2] for w in ev_kws2 if len(w) >= 2])
    common_roots = roots1.intersection(roots2)

    # 조건 1: 매우 높은 제목 유사도(0.50 이상) + 최소 1개 고유 사건 어근 일치
    if ratio >= 0.50 and len(common_roots) >= 1:
        return True

    # 조건 2: 중간 유사도(0.35 이상) + 2개 이상 구체적 사건 어근 일치 (예: 사형, 생존)
    if ratio >= 0.35 and len(common_roots) >= 2:
        return True

    # 조건 3: 제목 표현 방식은 달라도 핵심 고유 사건 어근이 3개 이상 일치
    if len(common_roots) >= 3:
        return True

    return False

def deduplicate_and_cluster(items, target_count=10):
    """유사 키워드 및 difflib 유사도를 바탕으로 사건별 군집화 후 최상급 1건만 선별"""
    clusters = []
    
    for item in items:
        item_kws = extract_title_keywords(item['title'])
        if not item_kws:
            continue
        
        matched_cluster = None
        for cl in clusters:
            if is_same_topic_event(item['title'], cl['representative']['title'], item_kws, cl['keywords']):
                matched_cluster = cl
                break
        
        if matched_cluster:
            matched_cluster['items'].append(item)
            matched_cluster['keywords'].update(item_kws)
        else:
            clusters.append({
                'representative': item,
                'items': [item],
                'keywords': set(item_kws)
            })

    # 각 군집에서 가장 공신력 높은 대표 기사 선별
    selected = []
    for cl in clusters:
        best = sorted(cl['items'], key=lambda x: (
            1 if ("yna.co.kr" in x['link'] or "bbc.com" in x['link'] or "voakorea.com" in x['link']) else 0,
            len(x.get('desc', ''))
        ), reverse=True)[0]
        selected.append(best)
        if len(selected) >= target_count:
            break
            
    return selected

# ==============================================================================
# 4단계: 심층 본문 크롤링 & 팩트 구조화 (Deep Crawling & Fact Structuring)
# ==============================================================================
def clean_news_text(text):
    """뉴스 본문 내의 HTML 태그, 바이라인, 이메일, 불필요한 공백 등 정제"""
    if not text:
        return ""
    # 1. HTML 태그 완전 제거
    if '<' in text and '>' in text:
        text = BeautifulSoup(text, 'html.parser').get_text(separator=' ', strip=True)
    # 2. 바이라인/출처 표기 정제
    text = re.sub(r'\(.*?=연합뉴스\)\s*[^=]+=\s*', '', text) # 바이라인 시작부
    text = re.sub(r'\(.*?=연합뉴스\)', '', text)
    text = re.sub(r'\[.*?=연합뉴스.*?\]', '', text)
    text = re.sub(r'\[연합뉴스.*?\]', '', text)
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def scrape_article_details(item):
    """기사 URL에 직접 접속하여 기자 바이라인, 핵심 문단, 상세 맥락 추출"""
    url = item['link']
    data = safe_fetch_url(url)
    if not data:
        return {
            'title': item['title'],
            'lead': item['desc'][:150] if item['desc'] else "원문 기사를 참고해 주십시오.",
            'context': "",
            'byline': item['source'],
            'link': url
        }

    html = data.decode('utf-8', errors='replace')
    soup = BeautifulSoup(html, 'html.parser')
    
    paragraphs = []
    byline = item['source']
    
    # 1. 연합뉴스 파싱
    if "yna.co.kr" in url:
        article_div = soup.find('div', class_='story-news') or soup.find('article')
        if article_div:
            for p in article_div.find_all('p'):
                # 사진/그래픽 figure, figcaption, txt-desc 문단 완벽 제외
                if p.find_parent('figure') or p.find_parent('figcaption') or 'txt-desc' in p.get('class', []):
                    continue
                txt = p.text.strip()
                if not txt:
                    continue
                # 사진/그래픽 캡션 문단 완벽 제외
                if any(m in txt for m in ['재판매 및 DB 금지', '자료사진', '사진 제공', '연합뉴스 사진', '그래픽=연합뉴스']):
                    continue
                if txt.startswith('[') and txt.endswith(']'):
                    continue
                # 바이라인 추출
                if '@yna.co.kr' in txt or '=연합뉴스' in txt:
                    byline_match = re.search(r'([가-힣]{2,4}\s*기자|[가-힣]{2,4}\s*특파원)', txt)
                    if byline_match:
                        byline = f"연합뉴스 ({byline_match.group(1)})"
                    if '@yna.co.kr' in txt:
                        continue
                paragraphs.append(txt)
    # 2. BBC 코리아 파싱
    elif "bbc.com" in url:
        article_div = soup.find('main') or soup.find('article')
        if article_div:
            for p in article_div.find_all('p'):
                txt = p.text.strip()
                if not txt or len(txt) <= 20:
                    continue
                # BBC 사진 캡션 및 이미지 출처 완벽 제외
                if any(m in txt for m in ['사진 출처', '이미지 출처', '캡션,', '사진 제공', 'Getty Images', 'AFP']):
                    continue
                paragraphs.append(txt)
        byline = "BBC News 코리아"
    # 3. 기타 언론사 범용 파싱
    else:
        article_div = soup.find('article') or soup.find('div', class_=re.compile(r'article|content|body'))
        if article_div:
            for p in article_div.find_all('p'):
                txt = p.text.strip()
                if txt and len(txt) > 25 and not any(k in txt for k in ['기자', '저작권', '무단전재', '구독']):
                    paragraphs.append(txt)
        else:
            paragraphs = [item['desc']]

    # 정제 및 팩트 구조화
    cleaned_paras = [clean_news_text(p) for p in paragraphs if len(clean_news_text(p)) > 15]
    
    # 사진 캡션이 남아있다면 2차 제거
    cleaned_paras = [p for p in cleaned_paras if not ('재판매 및 DB 금지' in p or '자료사진' in p)]

    # 제목 다듬기 (불필요한 언론사명 꼬리표 제거)
    clean_title = re.sub(r'\s*-\s*[가-힣A-Za-z0-9\s]+$', '', item['title'])
    clean_title = re.sub(r'\[속보\]|\[단독\]|\[종합\d?보?\]', '', clean_title).strip()
    
    # 1. 핵심 팩트 리드문 (M4 요구사항: 300자 내외 문장 종결 부호 기준 정밀 캡)
    raw_lead = cleaned_paras[0] if len(cleaned_paras) >= 1 else (item['desc'] or clean_title)
    if len(raw_lead) > 300:
        truncated = raw_lead[:300]
        last_punc = max(
            truncated.rfind('. '),
            truncated.rfind('.\n'),
            truncated.rfind('? '),
            truncated.rfind('! '),
            truncated.rfind('."'),
            truncated.rfind('.\'')
        )
        if last_punc > 100:
            lead = truncated[:last_punc + 1].strip()
        else:
            lead = truncated.rstrip() + "…"
    else:
        lead = raw_lead
    
    # 2. 배경 맥락 및 상세 내용 (N4 요구사항: 기사당 최대 500자 내외 문장 종결 부호 기준 정밀 캡)
    context = ""
    if len(cleaned_paras) >= 2:
        subsequent_paras = [p for p in cleaned_paras[1:5] if not p.startswith(('◇', '▲', '■', '◆'))]
        raw_context = " ".join(subsequent_paras)
        if len(raw_context) > 500:
            truncated = raw_context[:500]
            # 500자 이내의 마지막 문장 종결부(. ? ! 또는 ." 등) 탐색
            last_punc = max(
                truncated.rfind('. '),
                truncated.rfind('.\n'),
                truncated.rfind('? '),
                truncated.rfind('! '),
                truncated.rfind('."'),
                truncated.rfind('.\'')
            )
            if last_punc > 200:
                context = truncated[:last_punc + 1].strip()
            else:
                context = truncated.rstrip() + "…"
        else:
            context = raw_context

    return {
        'title': clean_title,
        'lead': lead,
        'context': context,
        'byline': byline,
        'link': url
    }

# ==============================================================================
# 뉴스 오케스트레이션 파이프라인 (Orchestration Pipeline)
# ==============================================================================
def collect_morning_world_news(target_count=10, foreign_only=False):
    """
    [오전 07:00] 외신 뉴스 수집 및 다단계 검수
    - 연합뉴스 국제 데스크 (워싱턴/베이징/도쿄/런던 특파원 120개 기사)
    - BBC News 코리아 (심층 글로벌 분석 20여 개 기사)
    """
    if foreign_only:
        log("🌅 [오전 07:00] 순수 해외 언론사 외신 뉴스 수집 가동 (BBC)...")
        feeds = [
            ("https://feeds.bbci.co.uk/korean/rss.xml", "BBC News 코리아")
        ]
    else:
        log("🌅 [오전 07:00] 글로벌 및 주요 외신 뉴스 수집 가동 (연합뉴스 국제 + BBC)...")
        feeds = [
            ("https://www.yna.co.kr/rss/international.xml", "연합뉴스 국제"),
            ("https://feeds.bbci.co.uk/korean/rss.xml", "BBC News 코리아")
        ]
    
    raw_candidates = []
    for url, src in feeds:
        items = parse_feed_items(url, default_source=src)
        raw_candidates.extend(items)
        log(f"  - [{src}] {len(items)}건 수집 완료")

    # 1단계 검수: 잡음 기사 제거 및 시간 유효성 검사
    now = datetime.datetime.now(datetime.timezone.utc)
    filtered = []
    for item in raw_candidates:
        if is_noise_article(item['title']):
            continue
        if item['pub_date']:
            age_hours = (now - item['pub_date']).total_seconds() / 3600.0
            if age_hours > 24:
                continue
        filtered.append(item)

    log(f"  - 1차 잡음·시간 필터링 통과: {len(filtered)}건")

    # 2단계 검수: 키워드 군집화 및 중복 기사 통합
    deduped = deduplicate_and_cluster(filtered, target_count=target_count + 3)
    log(f"  - 2차 군집화 및 중복 제거 완료: {len(deduped)}건 선별")

    # 3단계 검수: 심층 본문 크롤링 및 팩트 구조화
    final_briefings = []
    for idx, item in enumerate(deduped[:target_count], 1):
        log(f"    -> ({idx}/{target_count}) 본문 크롤링: {item['title'][:30]}...")
        details = scrape_article_details(item)
        final_briefings.append(details)
        time.sleep(0.2)

    return final_briefings

def collect_evening_domestic_news(target_count=8):
    """
    [오후 21:00] 국내 주요 뉴스 수집 및 다단계 검수
    - 연합뉴스 정치 / 경제 / 사회 데스크 기사 균형 선별 (각 분야별 핵심 뉴스)
    - [M3 반영] 동일 기자(바이라인) 최대 1건 제한으로 취재 다양성 확보
    """
    log("🌙 [오후 21:00] 국내 주요 뉴스 수집 파이프라인 가동 (정치·경제·사회 균형)...")
    
    sections = [
        ("https://www.yna.co.kr/rss/politics.xml", "정치", 3),
        ("https://www.yna.co.kr/rss/economy.xml", "경제", 3),
        ("https://www.yna.co.kr/rss/society.xml", "사회", 2)
    ]
    
    selected_items = []
    seen_reporters = set()
    
    for feed_url, sec_name, count in sections:
        items = parse_feed_items(feed_url, default_source=f"연합뉴스 {sec_name}")
        filtered = [it for it in items if not is_noise_article(it['title'])]
        deduped = deduplicate_and_cluster(filtered, target_count=count + 8)
        log(f"  - [{sec_name}] {len(items)}건 중 잡음·군집 필터링 통과 후보: {len(deduped)}건")
        
        sec_selected = []
        for it in deduped:
            details = scrape_article_details(it)
            reporter = details['byline']
            # M3: 동일 기자 중복 방지 (기자명이 식별 가능한 경우)
            if reporter != f"연합뉴스 {sec_name}" and reporter in seen_reporters:
                log(f"    * 동일 기자({reporter}) 중복 보도 감지 -> 다양성 확보 위해 스킵")
                continue
            seen_reporters.add(reporter)
            sec_selected.append(details)
            time.sleep(0.1)
            if len(sec_selected) >= count:
                break
                
        selected_items.extend(sec_selected)

    return selected_items[:target_count]

# ==============================================================================
# 5단계: 텔레그램 안전 검수 & 분할 전송 (Formatting & Dispatcher)
# ==============================================================================
def sanitize_telegram_text(text):
    """
    [F2 & N3 반영] 발송 직전 공통 정리기:
    1. HTML 태그 안전 추출 (BeautifulSoup)
    2. html.unescape 디코딩
    3. 연속 공백 및 줄바꿈 정리
    4. 영문 태그 모양만 정밀 제거 (한글 작품명/도서명 <기생충>, <미스 캐시> 등 보존)
    5. 텔레그램 안전 escape (html.escape)
    """
    if not text:
        return ""
    if '<' in text and '>' in text:
        text = BeautifulSoup(text, 'html.parser').get_text(separator=' ', strip=True)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    # N3: 오직 영문 알파벳으로 시작하는 잔여 HTML 태그만 정밀 제거하여 한글 꺾쇠 보존
    text = re.sub(r'</?[a-zA-Z][^>]*>', '', text)
    return html.escape(text)

def format_briefing_messages(briefings, mode="morning", foreign_only=False):
    """
    텔레그램 4,096자 제한을 완벽히 준수하도록
    렌더링 글자 수(파트당 3,800자 이하) 기준으로 파트를 동적 분할 포맷팅
    """
    now_korea = datetime.datetime.now().strftime("%Y년 %m월 %d일")
    
    is_morning = (mode == "morning")
    if is_morning:
        main_title = "🌅 [모닝 해외 외신 브리핑]" if foreign_only else "🌅 [모닝 글로벌 & 주요 뉴스 브리핑]"
        sub_title = "밤사이 주요 글로벌 외신 및 특파원 핵심 취재 팩트"
    else:
        main_title = "🌙 [나이트 국내 주요 뉴스]"
        sub_title = "오늘 하루 국내 정치·경제·사회 핵심 팩트 정리"
    
    # 1. 각 기사별 완전한 텍스트 블록 생성 (F2 & N3 공통 정리기 경유)
    formatted_articles = []
    for i, item in enumerate(briefings, 1):
        s_title = sanitize_telegram_text(item['title'])
        s_lead = sanitize_telegram_text(item['lead'])
        s_context = sanitize_telegram_text(item.get('context', ''))
        s_byline = sanitize_telegram_text(item['byline'])

        lines = [
            f"<b>{i}. {s_title}</b>",
            f"• <b>주요 사실:</b> {s_lead}"
        ]
        if s_context:
            lines.append(f"• <b>상세 맥락:</b> {s_context}")
        lines.append(f"• <b>출처:</b> {s_byline} | <a href=\"{item['link']}\">원문 기사 보기</a>")
        lines.append("")
        formatted_articles.append("\n".join(lines))

    # 2. [N4 요구사항 반영] 텔레그램 4,096자 제한 대응: 렌더링 글자 수(파트당 3,800자 이하) 기준 동적 분할
    HEADER_FOOTER_ESTIMATE = 250
    MAX_PART_CHARS = 3800 - HEADER_FOOTER_ESTIMATE  # 본문 순수 최대 약 3,550자
    
    chunks = []
    current_chunk = []
    current_chars = 0
    
    for art_block in formatted_articles:
        # [M4 반영] 단일 기사가 극도로 긴 경우 안전 절단 방어
        if len(art_block) > MAX_PART_CHARS:
            art_block = art_block[:MAX_PART_CHARS - 60] + "…\n• <b>출처:</b> 원문 기사 보기\n"
        art_len = len(art_block) + 1  # 줄바꿈 포함
        if current_chunk and (current_chars + art_len > MAX_PART_CHARS):
            chunks.append(current_chunk)
            current_chunk = [art_block]
            current_chars = art_len
        else:
            current_chunk.append(art_block)
            current_chars += art_len
            
    if current_chunk:
        chunks.append(current_chunk)

    total_parts = len(chunks)
    messages = []
    
    for part_idx, chunk in enumerate(chunks, 1):
        lines = []
        part_tag = f" ({part_idx}/{total_parts})" if total_parts > 1 else ""
        lines.append(f"<b>{main_title}{part_tag}</b>")
        lines.append(f"📅 <i>{now_korea} | {sub_title}</i>")
        lines.append("━" * 24)
        lines.append("")

        lines.extend(chunk)

        lines.append("━" * 24)
        lines.append("📰 <i>주요 공신력 언론사 실시간 팩트 기사 정제 완료 | Antigravity</i>")
        
        messages.append("\n".join(lines))

    return messages

def send_telegram_messages(messages):
    """텔레그램 봇 API로 메시지 안전 발송 (OS 표준 SSL 검증 및 HTML 파싱 모드)"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        log("❌ 오류: .env 파일에 TELEGRAM_TOKEN 또는 TELEGRAM_CHAT_ID가 설정되어 있지 않습니다.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    success_count = 0

    for idx, msg in enumerate(messages, 1):
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        data = json.dumps(payload).encode("utf-8")
        
        sent = False
        for attempt in range(1, 4):
            try:
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": HTTP_HEADERS['User-Agent']
                    }
                )
                ctx = ssl.create_default_context()
                with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                    if resp.status == 200:
                        log(f"✅ 텔레그램 메시지 발송 성공 ({idx}/{len(messages)})")
                        sent = True
                        success_count += 1
                        break
                    else:
                        log(f"⚠️ 발송 실패 (시도 {attempt}/3): HTTP {resp.status}")
                        time.sleep(2)
            except urllib.error.HTTPError as he:
                log(f"⚠️ HTTP 에러 (시도 {attempt}/3): {he.code} - {he.read().decode('utf-8', errors='replace')}")
                time.sleep(2)
            except Exception as e:
                log(f"⚠️ 네트워크 에러 (시도 {attempt}/3): {e}")
                time.sleep(2)

        if not sent:
            log(f"❌ 텔레그램 메시지 ({idx}/{len(messages)}) 최종 발송 실패")
        
        time.sleep(1.2)

    return success_count == len(messages)

# ==============================================================================
# 메인 실행 엔트리포인트 (CLI & Automation)
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="텔레그램 자동 뉴스 브리핑 시스템")
    parser.add_argument("--mode", choices=["morning", "evening", "auto"], default="auto",
                        help="브리핑 모드 (morning: 외신 8~10개, evening: 국내 뉴스, auto: 현재 시각 기반 자동 판정)")
    parser.add_argument("--test", action="store_true", help="테스트 모드 (즉시 텔레그램 발송)")
    parser.add_argument("--dry-run", action="store_true", help="텔레그램으로 보내지 않고 콘솔에만 출력")
    parser.add_argument("--foreign-only", action="store_true", help="순수 해외 외신 언론사(BBC 코리아 등)만 수집")
    
    args = parser.parse_args()
    
    current_hour = datetime.datetime.now().hour
    if args.mode == "auto":
        mode = "morning" if current_hour < 14 else "evening"
    else:
        mode = args.mode

    log(f"==================================================")
    log(f"🚀 뉴스 브리핑 오케스트레이터 시작 (모드: {mode}, 해외외신전용: {args.foreign_only}, 테스트: {args.test}, 드라이런: {args.dry_run})")
    log(f"==================================================")

    if mode == "morning":
        briefings = collect_morning_world_news(target_count=10, foreign_only=args.foreign_only)
    else:
        briefings = collect_evening_domestic_news(target_count=8)

    if not briefings:
        log("❌ 수집된 유효 뉴스가 없어 브리핑 생성을 중단합니다.")
        sys.exit(1)

    log(f"📊 최종 검수 통과 기사 수: {len(briefings)}건")
    messages = format_briefing_messages(briefings, mode=mode, foreign_only=args.foreign_only)
    log(f"📦 생성된 텔레그램 메시지 파트 수: {len(messages)}개")

    if args.dry_run:
        log("--- [DRY-RUN 콘솔 미리보기] ---")
        for i, m in enumerate(messages, 1):
            print(f"\n[PART {i}]\n" + m)
            print("-" * 50)
    else:
        log("📨 텔레그램으로 브리핑 발송 시작...")
        success = send_telegram_messages(messages)
        if success:
            log("🎉 모든 뉴스 브리핑이 성공적으로 텔레그램으로 배달되었습니다!")
        else:
            log("❌ 일부 또는 전체 메시지 발송에 실패했습니다. 종료코드 1(exit 1)로 종료하여 비상 알림을 트리거합니다.")
            sys.exit(1)

if __name__ == "__main__":
    main()
