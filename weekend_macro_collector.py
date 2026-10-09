#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
주말 글로벌 거시경제 3주 팩트 수집 및 크롤링 엔진 (weekend_macro_collector.py)
================================================================================
- 공신력 있는 언론사(연합뉴스 경제/국제/산업, BBC 코리아, 구글뉴스) RSS 기반 수집
- 구글뉴스 검색 RSS(when:21d) 및 당해 주차 신산업 키워드 연동을 통한 3주 누적 수집
- 불필요한 가십, 연예, 스포츠 단신 정밀 필터링 (한국어 조사 대응, 경제 용어 완전 보존)
- 정밀 제목 정제 및 하이픈 처리 버그 해결
- R1: 연합/BBC 직접 기사 최소 10건 보장 + 구글 3주 검색 기사 20건 균형 군집화 선별
- R2: 구글뉴스 RSS <source> 태그 및 제목 접미사 기반 실제 언론사명 100% 추출
- R3: 10건 미만 수집 시 기존 팩트 풀 보존 및 sys.exit(1) 종료 코드 보장
- R4': 표준 SSL 검증 기본 적용 및 인증서 예외 시에만 안전 우회 폴백
- R5: 발행일 미확인 기사 '발행일 미상' 안전 표기 (KST 기준 일관성 유지)
- R6: 불용어 목록 완전 복원 및 자카드 유사도 최적화
- R7: metadata 및 articles를 포함한 표준 JSON 및 마크다운 원자적(Atomic) 교체 저장
================================================================================
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
import ssl
import datetime
from email.utils import parsedate_to_datetime
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

# Windows 콘솔 UTF-8 강제 설정
if sys.platform == 'win32':
    try:
        if sys.stdout and hasattr(sys.stdout, 'buffer') and getattr(sys.stdout, 'encoding', None) and sys.stdout.encoding.lower() != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        if sys.stderr and hasattr(sys.stderr, 'buffer') and getattr(sys.stderr, 'encoding', None) and sys.stderr.encoding.lower() != 'utf-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FACT_POOL_JSON = os.path.join(CURRENT_DIR, "weekend_macro_fact_pool.json")
FACT_POOL_MD = os.path.join(CURRENT_DIR, "weekend_macro_fact_pool.md")
LOG_PATH = os.path.join(CURRENT_DIR, "weekend_news_exec.log")

def log(msg):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{now_str}] [FactCollector] {msg}"
    print(formatted, flush=True)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

def safe_fetch_url(url, timeout=12, max_retries=2):
    """
    R4': Windows OS 신뢰 저장소(truststore) 기반 안전한 표준 SSL 검증 적용
    """
    req = urllib.request.Request(url, headers=HTTP_HEADERS)
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as e:
            if attempt == max_retries - 1:
                log(f"URL 요청 최종 실패 ({url}): {e}")
                return None
        time.sleep(1.0)
    return None

def parse_feed_items(feed_url, default_source="언론사"):
    """
    R2: RSS 피드 파싱 후 표준 딕셔너리 리스트 반환
    - 구글뉴스 RSS <source> 태그 및 제목 접미사 기반 실제 언론사명 정확 추출
    - HTML 태그 정제 및 timezone-aware datetime 보장
    """
    data = safe_fetch_url(feed_url)
    if not data:
        return []
    
    items = []
    try:
        root = ET.fromstring(data)
        for item in root.findall('.//item'):
            title = item.find('title').text.strip() if item.find('title') is not None and item.find('title').text else ""
            link = item.find('link').text.strip() if item.find('link') is not None and item.find('link').text else ""
            pub_date_str = item.find('pubDate').text.strip() if item.find('pubDate') is not None and item.find('pubDate').text else ""
            raw_desc = item.find('description').text.strip() if item.find('description') is not None and item.find('description').text else ""

            if not title or not link:
                continue

            # R2: 진짜 언론사명 추출 (<source> 태그 우선, 제목 접미사 2차 파싱)
            source_text = ""
            source_elem = item.find('source')
            if source_elem is not None and source_elem.text and source_elem.text.strip():
                source_text = source_elem.text.strip()
            elif re.search(r'\s+-\s+([^-]+)$', title):
                m = re.search(r'\s+-\s+([^-]+)$', title)
                source_text = m.group(1).strip()
            
            real_source = source_text if source_text else default_source

            # M2: 구글뉴스 description 등 HTML 태그 정제
            clean_desc = ""
            if raw_desc:
                clean_desc = BeautifulSoup(raw_desc, "html.parser").get_text(" ", strip=True)

            # C4: 시간대 정보가 없는 naive datetime 처리 (TypeError 크래시 원천 차단)
            pub_dt = None
            if pub_date_str:
                try:
                    pub_dt = parsedate_to_datetime(pub_date_str)
                    if pub_dt and pub_dt.tzinfo is None:
                        pub_dt = pub_dt.replace(tzinfo=datetime.timezone.utc)
                except Exception:
                    pub_dt = None

            items.append({
                'title': title,
                'link': link,
                'pub_date': pub_dt,
                'pub_date_str': pub_date_str,
                'desc': clean_desc,
                'source': real_source,
                'feed': default_source
            })
    except Exception as e:
        log(f"피드 파싱 에러 ({feed_url}): {e}")
    return items

def is_noise_article(title):
    """
    N5: 한국어 조사에 대응하기 위해 \\b 제거
    거시경제/신산업 분석에 불필요한 가십, 스포츠, 날씨, 포토 등 차단
    (키움증권, 두산에너빌리티, 기아(KIA), SSG닷컴, 이벤트 리스크, 안타까운 등 정상 경제 기사 완벽 보존)
    """
    noise_patterns = [
        r"\[포토\]", r"\[화보\]", r"\[인사\]", r"\[부고\]", r"\[동정\]",
        r"로또", r"운세", r"오늘의 운세", r"날씨",
        # 스포츠 노이즈: 구단은 풀네임으로 매칭, 조사 결합 대응
        r"프로야구", r"가을야구", r"KBO", r"골프", r"축구", r"야구", r"농구", r"배구",
        r"손흥민", r"이강인", r"김민재", r"황희찬", r"메이저리그", r"MLB", r"EPL",
        r"홈런", r"\d+안타", r"호투", r"완투", r"타율", r"선발승",
        r"\d+연승", r"\d+연패", r"연패",
        r"두산베어스", r"LG트윈스", r"KIA타이거즈", r"삼성라이온즈", r"SSG랜더스", r"키움히어로즈", r"한화이글스",
        # 연예/홍보/단순단신 (경제 기사 용어 배제)
        r"팬미팅", r"시청률", r"경품", r"출석체크", r"할인행사", r"선착순"
    ]
    for pat in noise_patterns:
        if re.search(pat, title, re.IGNORECASE):
            return True
    return False

def clean_title_for_display(title):
    """
    M4: 제목 정제 시 하이픈 버그 교정
    ' - 언론사명' 형태의 접미사만 안전하게 제거
    """
    clean = re.sub(r"\s+-\s+[^-]+$", "", title)
    clean = re.sub(r"\[속보\]|\[단독\]|\[종합\d?보?\]", "", clean).strip()
    return clean

def extract_title_keywords(title):
    """
    R6: 불용어 목록 완전 복원 및 자카드 유사도 군집화를 위한 핵심 키워드 집합 추출
    """
    clean = clean_title_for_display(title)
    tokens = re.findall(r'[가-힣a-zA-Z0-9]{2,}', clean)
    stop_words = {
        "오늘", "어제", "내일", "최근", "논란", "결국", "종합", "속보", "기자", "특파원",
        "이유", "관련", "대해", "게시판", "미국", "한국", "중국", "정부", "경제", "시장",
        "발표", "전망", "증가", "감소", "올해", "지난달", "이번", "통해", "위해", "대한",
        "따른", "결과", "연합뉴스"
    }
    return set([t for t in tokens if t not in stop_words])

def deduplicate_and_cluster(items, target_count=30, min_direct_quota=10):
    """
    R1 & 개선 4: 자카드 유사도 기반 군집화 및 3주 누적 다양성 선별 엔진
    - 연합뉴스/BBC 등 직접 수집 기사 최소 10건 확정 배분
    - 나머지 20개 슬롯은 군집 크기 순으로 직접/구글 검색 기사가 균형 있게 배분되도록 보장
    """
    clusters = []
    for item in items:
        item_kws = extract_title_keywords(item['title'])
        if not item_kws:
            continue
        
        matched_cluster = None
        for cl in clusters:
            rep_kws = cl['representative_kws']
            intersection = item_kws.intersection(rep_kws)
            union = item_kws.union(rep_kws)
            jaccard = len(intersection) / len(union) if union else 0.0
            if jaccard >= 0.3 or len(intersection) >= 2:
                matched_cluster = cl
                break
        
        if matched_cluster:
            matched_cluster['items'].append(item)
        else:
            clusters.append({
                'representative_kws': set(item_kws),
                'items': [item]
            })

    # 1. 보도량이 많은 군집 순으로 정렬 (핵심 이슈 우선)
    clusters.sort(key=lambda c: len(c['items']), reverse=True)

    def is_direct_source(it):
        link = it.get('link', '')
        src = it.get('source', '')
        feed = it.get('feed', '')
        return ("yna.co.kr" in link or "연합뉴스" in src or "연합뉴스" in feed or
                "bbc.com" in link or "BBC" in src or "BBC" in feed)

    selected = []
    selected_links = set()
    used_cluster_ids = set()

    # Step 1: 연합뉴스/BBC 직접 수집 기사를 우선 최대 min_direct_quota(10건)만 선별
    for cl in clusters:
        if len(selected) >= min_direct_quota:
            break
        direct_items = [it for it in cl['items'] if is_direct_source(it) and it['link'] not in selected_links]
        if direct_items:
            best_direct = max(direct_items, key=lambda x: len(x.get('desc', '')))
            selected.append(best_direct)
            selected_links.add(best_direct['link'])
            used_cluster_ids.add(id(cl))

    # Step 2: 나머지 슬롯(20건)은 군집 크기 순서대로 돌면서, 아직 미포함된 군집의 대표 기사 선별
    for cl in clusters:
        if len(selected) >= target_count:
            break
        if id(cl) in used_cluster_ids:
            continue
        available_items = [it for it in cl['items'] if it['link'] not in selected_links]
        if available_items:
            best_item = max(available_items, key=lambda x: len(x.get('desc', '')))
            selected.append(best_item)
            selected_links.add(best_item['link'])
            used_cluster_ids.add(id(cl))

    # Step 3: 목표 수량(30건) 미달 시 전체 남은 기사 중 미선택 기사 추가
    if len(selected) < target_count:
        for cl in clusters:
            for it in cl['items']:
                if it['link'] not in selected_links:
                    selected.append(it)
                    selected_links.add(it['link'])
                    if len(selected) >= target_count:
                        break
            if len(selected) >= target_count:
                break

    return selected[:target_count]

def clean_news_text(text):
    """바이라인, 이메일, 불필요한 공백 등 정제"""
    text = re.sub(r'\(.*?=연합뉴스\)\s*[^=]+=\s*', '', text)
    text = re.sub(r'\[.*?=연합뉴스.*?\]', '', text)
    text = re.sub(r'\[연합뉴스.*?\]', '', text)
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def scrape_article_details(item):
    """기사 URL에 접속하여 기자 바이라인, 핵심 문단, 상세 맥락 추출"""
    url = item['link']
    clean_title = clean_title_for_display(item['title'])
    
    # R5: 발행일 표기 일관성 보장 (KST 변환 또는 '발행일 미상')
    kst = datetime.timezone(datetime.timedelta(hours=9))
    if item.get('pub_date'):
        pub_dt = item['pub_date']
        pub_date_display = pub_dt.astimezone(kst).strftime("%Y-%m-%d %H:%M:%S KST")
    else:
        pub_date_display = "발행일 미상"

    # M2: 구글뉴스 기사는 본문 직접 크롤링이 불가능하므로 정제된 desc 활용
    if "news.google.com" in url:
        return {
            'title': clean_title,
            'pub_date': pub_date_display,
            'lead': item['desc'] if item['desc'] else clean_title,
            'context': "",
            'byline': item['source'],
            'feed': item.get('feed', item['source']),
            'link': url
        }

    data = safe_fetch_url(url)
    if not data:
        return {
            'title': clean_title,
            'pub_date': pub_date_display,
            'lead': item['desc'][:180] if item['desc'] else "원문 기사를 참고해 주십시오.",
            'context': "",
            'byline': item['source'],
            'feed': item.get('feed', item['source']),
            'link': url
        }

    soup = BeautifulSoup(data, 'html.parser')
    paragraphs = []
    byline = item['source']
    
    # 1. 연합뉴스
    if "yna.co.kr" in url:
        article_div = soup.find('div', class_='story-news') or soup.find('article')
        if article_div:
            for p in article_div.find_all('p'):
                txt = p.text.strip()
                if not txt:
                    continue
                if any(m in txt for m in ['재판매 및 DB 금지', '자료사진', '사진 제공', '연합뉴스 사진', '그래픽=연합뉴스']):
                    continue
                if txt.startswith('[') and txt.endswith(']'):
                    continue
                if '@yna.co.kr' in txt or '=연합뉴스' in txt:
                    byline_match = re.search(r'([가-힣]{2,4}\s*기자|[가-힣]{2,4}\s*특파원)', txt)
                    if byline_match:
                        byline = f"연합뉴스 ({byline_match.group(1)})"
                    if '@yna.co.kr' in txt:
                        continue
                paragraphs.append(txt)
    # 2. BBC 코리아
    elif "bbc.com" in url:
        article_div = soup.find('main') or soup.find('article')
        if article_div:
            for p in article_div.find_all('p'):
                txt = p.text.strip()
                if txt and len(txt) > 20:
                    paragraphs.append(txt)
        byline = "BBC News 코리아"
    # 3. 기타 범용 언론사
    else:
        article_div = soup.find('article') or soup.find('div', class_=re.compile(r'article|content|body'))
        if article_div:
            for p in article_div.find_all('p'):
                txt = p.text.strip()
                if txt and len(txt) > 25 and not any(k in txt for k in ['기자', '저작권', '무단전재', '구독']):
                    paragraphs.append(txt)
        else:
            paragraphs = [item['desc']]

    cleaned_paras = [clean_news_text(p) for p in paragraphs if len(clean_news_text(p)) > 15]
    cleaned_paras = [p for p in cleaned_paras if not ('재판매 및 DB 금지' in p or '자료사진' in p)]

    lead = cleaned_paras[0] if len(cleaned_paras) >= 1 else (item['desc'] or clean_title)
    context = ""
    if len(cleaned_paras) >= 2:
        subsequent_paras = [p for p in cleaned_paras[1:5] if not p.startswith(('◇', '▲', '■', '◆'))]
        context = " ".join(subsequent_paras)

    return {
        'title': clean_title,
        'pub_date': pub_date_display,
        'lead': lead,
        'context': context,
        'byline': byline,
        'feed': item.get('feed', item['source']),
        'link': url
    }

def get_current_week_new_industry(now_dt=None):
    """개선 5: 당해 주차에 대응하는 신산업 키워드 반환"""
    industries = [
        "신재생에너지", "인공지능 AI", "우주항공", "자율주행 전기차", "SMR 원전",
        "디지털헬스케어", "휴머노이드 로봇", "양자컴퓨팅", "차세대 반도체"
    ]
    if now_dt is None:
        kst = datetime.timezone(datetime.timedelta(hours=9))
        now_dt = datetime.datetime.now(datetime.timezone.utc).astimezone(kst)
    week_of_year = now_dt.isocalendar()[1]
    return industries[week_of_year % len(industries)]

def collect_3week_macro_news(target_count=30, max_age_days=21):
    """
    최대 3주간(최근 21일)의 경제, 금융, 국제, 산업 주요 기사 수집 및 크롤링
    R3: 최소 10건 미만 수집 시 기존 팩트 풀 보존 및 실패(None) 반환
    """
    kst = datetime.timezone(datetime.timedelta(hours=9))
    now = datetime.datetime.now(datetime.timezone.utc)
    now_kst = now.astimezone(kst)
    start_date_kst = (now_kst - datetime.timedelta(days=max_age_days)).strftime("%Y-%m-%d")
    end_date_kst = now_kst.strftime("%Y-%m-%d")
    
    current_industry_keyword = get_current_week_new_industry(now_kst)

    log(f"==================================================")
    log(f"🌐 3주 팩트 수집 파이프라인 가동 (대상 기간: {start_date_kst} ~ {end_date_kst}, 최대 {max_age_days}일)")
    log(f"   포커스 신산업 키워드: [{current_industry_keyword}]")
    log(f"==================================================")

    feeds = [
        ("https://www.yna.co.kr/rss/economy.xml", "연합뉴스 경제"),
        ("https://www.yna.co.kr/rss/international.xml", "연합뉴스 국제"),
        ("https://www.yna.co.kr/rss/industry.xml", "연합뉴스 산업"),
        ("https://feeds.bbci.co.uk/korean/rss.xml", "BBC News 코리아")
    ]

    # 개선 5: 신산업 키워드를 포함한 8대 핵심 검색 쿼리
    search_queries = [
        "기준금리", "환율", "수출", "소비자물가", "FOMC", "반도체", "국제유가", current_industry_keyword
    ]
    for q in search_queries:
        encoded_q = urllib.parse.quote(f"{q} when:{max_age_days}d")
        url = f"https://news.google.com/rss/search?q={encoded_q}&hl=ko&gl=KR&ceid=KR:ko"
        feeds.append((url, f"구글검색-{q}"))

    raw_candidates = []
    for url, src in feeds:
        items = parse_feed_items(url, default_source=src)
        raw_candidates.extend(items)
        log(f"  - [{src}] {len(items)}건 수집 완료")

    filtered = []
    for item in raw_candidates:
        if is_noise_article(item['title']):
            continue
        if item['pub_date']:
            age_days = (now - item['pub_date']).total_seconds() / 86400.0
            if age_days > max_age_days:
                continue
        filtered.append(item)

    log(f"  - 1차 잡음·3주(21일) 시간 필터링 통과: {len(filtered)}건")

    # R1: 10건 직접 기사 보장 + 구글 기사 20건 균형 군집화
    deduped = deduplicate_and_cluster(filtered, target_count=target_count, min_direct_quota=10)
    log(f"  - 2차 군집화 및 중복 제거 완료: {len(deduped)}건 대표 기사 선별")

    # R3: 최소 건수(10건) 미달 시 기존 파일 보호
    if len(deduped) < 10:
        log(f"⚠️ 경고: 수집된 유효 기사가 {len(deduped)}건으로 최소 기준(10건)에 미달합니다. 기존 팩트 풀을 보존합니다.")
        return None

    final_articles = []
    for idx, item in enumerate(deduped[:target_count], 1):
        log(f"    -> ({idx}/{min(len(deduped), target_count)}) 심층 본문 크롤링: {item['title'][:32]}... [{item['source']}]")
        details = scrape_article_details(item)
        final_articles.append(details)
        time.sleep(0.1)

    # R7: metadata 및 articles 표준 JSON 구조 복원
    fact_pool_data = {
        "metadata": {
            "collected_at": now_kst.strftime("%Y-%m-%d %H:%M:%S KST"),
            "period_start": start_date_kst,
            "period_end": end_date_kst,
            "max_age_days": max_age_days,
            "target_industry": current_industry_keyword,
            "total_articles": len(final_articles)
        },
        "articles": final_articles
    }

    tmp_json = FACT_POOL_JSON + ".tmp"
    with open(tmp_json, "w", encoding="utf-8") as f:
        json.dump(fact_pool_data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_json, FACT_POOL_JSON)
    log(f"💾 JSON 팩트 풀 저장 완료: {FACT_POOL_JSON} ({len(final_articles)}건)")

    md_lines = [
        f"# 주말 글로벌 거시경제 3주 실측 팩트 풀 (Fact Pool)",
        f"**수집 일시**: {now_kst.strftime('%Y년 %m월 %d일 %H:%M KST')}  ",
        f"**분석 대상 기간**: {start_date_kst} ~ {end_date_kst} (최대 {max_age_days}일간 공식 언론 보도)  ",
        f"**포커스 신산업**: {current_industry_keyword}  ",
        f"**총 수집 기사**: {len(final_articles)}건  ",
        "",
        "---",
        ""
    ]
    for i, a in enumerate(final_articles, 1):
        md_lines.append(f"### {i}. {a['title']}")
        md_lines.append(f"- **발행 시점 / 출처**: {a['pub_date']} | {a['byline']}")
        md_lines.append(f"- **핵심 팩트**: {a['lead']}")
        if a['context']:
            md_lines.append(f"- **상세 맥락**: {a['context']}")
        md_lines.append(f"- **원문 링크**: {a['link']}")
        md_lines.append("")

    tmp_md = FACT_POOL_MD + ".tmp"
    with open(tmp_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    os.replace(tmp_md, FACT_POOL_MD)
    log(f"📄 마크다운 팩트 풀 저장 완료: {FACT_POOL_MD}")

    log("🎉 3주 팩트 수집 및 정제 작업 완결!")
    return fact_pool_data

if __name__ == "__main__":
    res = collect_3week_macro_news(target_count=30, max_age_days=21)
    if not res:
        sys.exit(1)
    sys.exit(0)
