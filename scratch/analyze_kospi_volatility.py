import sys
import datetime
import requests
import json
import numpy as np

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def fetch_kospi_data():
    # Yahoo Finance ^KS11 (KOSPI Composite Index) 
    url = "https://query1.finance.yahoo.com/v8/finance/chart/^KS11?interval=1d&range=max"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    print(">> Yahoo Finance 코스피(^KS11) 역대 데이터 수집 중...")
    res = requests.get(url, headers=headers, timeout=15, verify=False)
    if res.status_code != 200:
        print(f"Yahoo Finance API 실패 (HTTP {res.status_code})")
        return None
        
    result = res.json()["chart"]["result"][0]
    timestamps = result.get("timestamp", [])
    quote = result["indicators"]["quote"][0]
    
    opens = quote.get("open", [])
    highs = quote.get("high", [])
    lows = quote.get("low", [])
    closes = quote.get("close", [])
    
    data = []
    kst_tz = datetime.timezone(datetime.timedelta(hours=9))
    for ts, o, h, l, c in zip(timestamps, opens, highs, lows, closes):
        if c is not None and o is not None and h is not None and l is not None:
            dt = datetime.datetime.fromtimestamp(ts, tz=kst_tz)
            data.append({
                "date": dt.strftime("%Y-%m-%d"),
                "year_month": dt.strftime("%Y-%m"),
                "year": dt.year,
                "open": o,
                "high": h,
                "low": l,
                "close": c,
                "range_pct": (h - l) / o * 100.0 if o > 0 else 0.0
            })
    return data

data = fetch_kospi_data()

if data:
    print(f">> 총 {len(data)}개 일별 데이터 확보 완료! ({data[0]['date']} ~ {data[-1]['date']})")
    
    # 일별 수익률 계산
    for i in range(1, len(data)):
        prev_c = data[i-1]["close"]
        curr_c = data[i]["close"]
        data[i]["return_pct"] = (curr_c - prev_c) / prev_c * 100.0
    data[0]["return_pct"] = 0.0

    # 월별 변동성 (일별 수익률의 표준편차 & 평균 장중 변동폭) 그룹화
    monthly_stats = {}
    for d in data:
        ym = d["year_month"]
        if ym not in monthly_stats:
            monthly_stats[ym] = {"returns": [], "ranges": [], "year": d["year"]}
        monthly_stats[ym]["returns"].append(d["return_pct"])
        monthly_stats[ym]["ranges"].append(d["range_pct"])

    monthly_summary = []
    for ym, stats in monthly_stats.items():
        if len(stats["returns"]) >= 5: # 최소 5거래일 이상
            std_dev = np.std(stats["returns"])
            avg_range = np.mean(stats["ranges"])
            monthly_summary.append({
                "year_month": ym,
                "year": stats["year"],
                "std_dev": std_dev, # 일별 수익률 표준편차 (변동성 지표)
                "avg_range": avg_range, # 평균 일일 장중 변동폭 %
                "days": len(stats["returns"])
            })

    # 전체 월별 std_dev 내림차순 정렬
    sorted_by_vol = sorted(monthly_summary, key=lambda x: x["std_dev"], reverse=True)
    
    # 2026년 7월 데이터 찾기 (또는 가장 최근 2026년 데이터)
    july_2026 = [m for m in monthly_summary if m["year_month"] == "2026-07"]
    recent_2026 = [m for m in monthly_summary if m["year"] == 2026]

    print("\n==================================================")
    print("📊 코스피 역대 월별 변동성(일별 수익률 표준편차) 분석")
    print("==================================================")
    print(f"• 분석 대상 기간: {data[0]['date']} ~ {data[-1]['date']} (약 {data[-1]['year'] - data[0]['year']}년)")
    print(f"• 전체 분석 월 수: 총 {len(monthly_summary)}개 월")
    
    all_std_devs = [m["std_dev"] for m in monthly_summary]
    avg_historical_std = np.mean(all_std_devs)
    median_historical_std = np.median(all_std_devs)
    
    print(f"• 40년 역대 평균 월간 변동성(표준편차): {avg_historical_std:.2f}%")
    print(f"• 40년 역대 중위 월간 변동성(표준편차): {median_historical_std:.2f}%")
    
    print("\n🔥 역대 최악의 폭풍우 변동성 Top 5 월:")
    for rank, m in enumerate(sorted_by_vol[:5], 1):
        print(f"  {rank}위: {m['year_month']} -> 일별 수익률 표준편차: {m['std_dev']:.2f}%, 장중 평균 변동폭: {m['avg_range']:.2f}%")

    if july_2026:
        m26 = july_2026[0]
        rank_26 = sorted_by_vol.index(m26) + 1
        pct_rank = (rank_26 / len(sorted_by_vol)) * 100.0
        print(f"\n🎯 [2026년 7월 실측 백테스팅 수치]")
        print(f"  - 2026년 7월 월간 변동성(표준편차): {m26['std_dev']:.2f}%")
        print(f"  - 2026년 7월 평균 장중 변동폭: {m26['avg_range']:.2f}%")
        print(f"  - 역대 {len(sorted_by_vol)}개 월 중 변동성 순위: 상위 {pct_rank:.1f}% ({rank_26}위)")
        print(f"  - 역대 평균 변동성({avg_historical_std:.2f}%) 대비: 약 {m26['std_dev'] / avg_historical_std:.1f}배 높은 수치")
    else:
        print("\n🎯 [2026년 최근 월별 실측 백테스팅 수치]")
        for m in recent_2026:
            rank_26 = sorted_by_vol.index(m) + 1
            pct_rank = (rank_26 / len(sorted_by_vol)) * 100.0
            print(f"  - {m['year_month']} -> 변동성: {m['std_dev']:.2f}%, 장중 평균 변동폭: {m['avg_range']:.2f}% (역대 상위 {pct_rank:.1f}%, {rank_26}위)")

    # 결과를 json으로도 임시 저장
    with open(r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\scratch\kospi_volatility_analysis.json', 'w', encoding='utf-8') as f:
        json.dump({
            "avg_historical_std": avg_historical_std,
            "median_historical_std": median_historical_std,
            "top_5": sorted_by_vol[:5],
            "recent_2026": recent_2026
        }, f, ensure_ascii=False, indent=2)
