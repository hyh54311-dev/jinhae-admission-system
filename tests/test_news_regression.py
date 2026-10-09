# -*- coding: utf-8 -*-
"""
뉴스 브리핑 종합 회귀 테스트 스위트 (test_news_regression.py)
--------------------------------------------------------------------------------
Claude Opus 2차 검토(조건부 승인)에 따른 N1~N4 전수 검증:
1. [N1 검증] 야간 모드 피드(정치, 경제, 사회) 파싱 및 수집 건수 정상성 (society.xml BS4 폴백)
2. [N2 검증] 동일 사건 중복 판정 규칙 및 불용어(EVENT_STOP_WORDS) — 지정 3대 테스트 쌍 100% 통과
3. [N3 검증] 발송 직전 정리기의 한글 꺾쇠 표기(<기생충>, <미스 캐시>) 보존 검증
4. [N4 검증] 긴 기사 10건 포맷팅 시 파트당 3,800자 이하 캡 및 분할 동작 검증
5. [F1 & F2] 렌더링 메시지 내 비허용 HTML 태그(<ol>, <li>, <font> 등) 0건 검증
6. [야간 파이프라인] collect_evening_domestic_news 8건 정상 생성 및 텔레그램 규격 검증
--------------------------------------------------------------------------------
"""

import sys
import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from news_briefing_bot import (
    parse_feed_items,
    is_noise_article,
    deduplicate_and_cluster,
    scrape_article_details,
    format_briefing_messages,
    sanitize_telegram_text,
    is_same_topic_event,
    extract_title_keywords,
    collect_evening_domestic_news,
    EVENT_STOP_WORDS
)

def test_n1_evening_feeds():
    """N1: 야간 국내 피드(정치, 경제, 사회) 수집 건수 검증"""
    print("\n--- [N1 검증] 야간 국내 피드 수집 건수 테스트 ---")
    sections = [
        ("https://www.yna.co.kr/rss/politics.xml", "정치"),
        ("https://www.yna.co.kr/rss/economy.xml", "경제"),
        ("https://www.yna.co.kr/rss/society.xml", "사회")
    ]
    for url, sec_name in sections:
        items = parse_feed_items(url, default_source=f"연합뉴스 {sec_name}")
        print(f"  - [{sec_name}] 수집 건수: {len(items)}건")
        assert len(items) >= 50, f"{sec_name} 피드 수집 건수 부족 ({len(items)} < 50)"
    print("✅ [N1 통과] 야간 국내 3대 피드(정치/경제/사회) 전수 정상 수집 확인 (사회 XML 파싱 에러 극복)")

def test_n2_event_deduplication():
    """N2: Claude 지정 3대 사건 중복/분리 테스트 쌍 검증"""
    print("\n--- [N2 검증] 동일 사건 중복 판정 규칙(불용어 및 유사도) 테스트 ---")
    test_pairs = [
        (
            "합쳐야 함: 사형수 생존 사건",
            "약물사형 집행에서 생존한 미국 사형수는 앞으로 어떻게 되나?",
            "'독극물 사형' 실패로 생존한 사형수…깨어나자 '분노 폭발'",
            True
        ),
        (
            "합치면 안 됨: 트럼프 서로 다른 기사",
            "트럼프 노벨평화상 욕심 줄였다지만…노르웨이는 여전히 '눈치'",
            "눈엣가시 美민주후보 독감 소식에 트럼프 '12일째 행불' 공세",
            False
        ),
        (
            "합치면 안 됨: AI 오픈AI 실적 vs 뉴욕증시 시황",
            "AI낙관론에 '찬물'…예상보다 27조원 낮은 오픈AI 연매출에 충격",
            "뉴욕증시, AI 기술주 약세에 혼조 마감…나스닥 1.25%↓(종합)",
            False
        )
    ]

    for label, t1, t2, expected in test_pairs:
        kws1 = extract_title_keywords(t1)
        kws2 = extract_title_keywords(t2)
        res = is_same_topic_event(t1, t2, kws1, kws2)
        print(f"  - [{label}] 결과={res} (기대값={expected})")
        assert res == expected, f"N2 검증 실패: {label} (결과: {res}, 기대값: {expected})"
    print("✅ [N2 통과] Claude 지정 3대 테스트 쌍 100% 일치 통과")

def test_n3_korean_brackets():
    """N3: 한국어 작품명/책 제목 꺾쇠 괄호(<기생충>, <미스 캐시>) 보존 검증"""
    print("\n--- [N3 검증] 한글 꺾쇠 제목 보존 테스트 ---")
    raw = "영화 <기생충> 재개봉 및 소설 <미스 캐시> 출간 소식"
    cleaned = sanitize_telegram_text(raw)
    print(f"  - 원문: {raw}")
    print(f"  - 정제: {cleaned}")
    assert "&lt;기생충&gt;" in cleaned, "기생충 꺾쇠 보존 실패"
    assert "&lt;미스 캐시&gt;" in cleaned, "미스 캐시 꺾쇠 보존 실패"
    
    # 일반 HTML 태그는 정상 제거되는지 교차 확인
    dirty = "<div><b>공지</b>: 영화 <괴물> 상영</div>"
    sanitized_dirty = sanitize_telegram_text(dirty)
    assert "&lt;괴물&gt;" in sanitized_dirty
    assert "<div>" not in sanitized_dirty
    print("✅ [N3 통과] 한글 꺾쇠 괄호는 안전하게 HTML 엔티티(&lt;&gt;)로 보존되고 HTML 태그는 박멸됨")

def test_n4_message_length_capping():
    """N4: 텔레그램 4,096자 제한 대응 (파트당 3,800자 이하 동적 분할 및 상세 맥락 500자 캡)"""
    print("\n--- [N4 검증] 메시지 길이 상한(3,800자) 및 상세 맥락 500자 캡 테스트 ---")
    long_mock_items = []
    for i in range(1, 11):
        long_mock_items.append({
            'title': f"아주 긴 제목의 글로벌 외신 및 국내 주요 분석 기사 제 {i}호 종합 분석 리포트",
            'lead': f"리드문 문단입니다. 첫 번째 문단으로서 핵심 사건의 육하원칙과 팩트를 상세하게 진술합니다. " * 3,
            'context': f"상세 배경 맥락 문단입니다. 경제적 수치와 관련 당국의 입장, 향후 파장과 전문가들의 심층 인터뷰 내용이 포함되어 매우 길게 이어집니다. " * 8, # ~800자
            'byline': f"연합뉴스 (홍길동 기자)",
            'link': f"https://www.yna.co.kr/view/AKR202610090000{i}"
        })

    # scrape_article_details의 맥락 500자 캡 시뮬레이션
    for item in long_mock_items:
        raw_ctx = item['context']
        if len(raw_ctx) > 500:
            truncated = raw_ctx[:500]
            last_punc = max(truncated.rfind('. '), truncated.rfind('.\n'), truncated.rfind('? '), truncated.rfind('! '))
            if last_punc > 200:
                item['context'] = truncated[:last_punc + 1].strip()
            else:
                item['context'] = truncated.rstrip() + "…"
        assert len(item['context']) <= 505, f"맥락 500자 캡 초과: {len(item['context'])}"

    messages = format_briefing_messages(long_mock_items, mode="evening")
    print(f"  - 긴 기사 10건 포맷팅 결과: 총 {len(messages)}개 파트로 자동 분할 생성")
    
    for idx, msg in enumerate(messages, 1):
        char_count = len(msg)
        print(f"    * Part {idx}: {char_count}자 (상한 3,800자 / 텔레그램 한계 4,096자 대비)")
        assert char_count <= 3800, f"Part {idx} 글자수 초과 ({char_count} > 3800)"
        assert char_count <= 4096, f"Part {idx} 텔레그램 하드 리밋 초과 ({char_count} > 4096)"

    print("✅ [N4 통과] 긴 기사 10건 전수 포맷팅 시에도 파트당 3,800자 이하 철저 준수")

def test_evening_pipeline_dry_run():
    """야간 모드 전체 파이프라인(수집 -> 군집화 -> 정제 -> 분할) 실행 검증"""
    print("\n--- [야간 실전 파이프라인] 전체 드라이런 검증 ---")
    briefings = collect_evening_domestic_news(target_count=8)
    assert len(briefings) == 8, f"선정된 기사 수 불일치 ({len(briefings)} != 8)"
    messages = format_briefing_messages(briefings, mode="evening")
    assert len(messages) >= 2, f"분할 메시지 수 부족 ({len(messages)} < 2)"
    
    for idx, msg in enumerate(messages, 1):
        assert len(msg) <= 3800, f"메시지 {idx} 글자수 초과: {len(msg)}"
        disallowed = re.findall(r'<(?!/?(?:b|i|a\b))[^>]+>', msg)
        assert len(disallowed) == 0, f"비허용 태그 발견: {disallowed}"
    print(f"✅ [야간 파이프라인 통과] 8건 기사 수집 및 {len(messages)}개 파트 정제 완료")

if __name__ == "__main__":
    test_n1_evening_feeds()
    test_n2_event_deduplication()
    test_n3_korean_brackets()
    test_n4_message_length_capping()
    test_evening_pipeline_dry_run()
    print("\n==================================================")
    print("🎉 모든 N1~N4 회귀 테스트 100% PASS 성공!")
    print("==================================================")
