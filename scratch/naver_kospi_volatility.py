import sys
import datetime
import requests
import numpy as np

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Naver Finance KOSPI index history (Item: KOSPI)
url = "https://fchart.stock.naver.com/sise.nhn?symbol=KOSPI&timeframe=day&count=8000&requestType=0"
print(">> 네이버 금융 코스피 일별 시세 데이터 수집 중 (약 30년치)...")
res = requests.get(url, timeout=10)
text = res.text

import xml.etree.ElementTree as ET
root = ET.fromstring(text)

items = root.findall(".//item")
print(f">> 총 {len(items)}개 거래일 데이터 수집 성공!")

data = []
for item in items:
    # data format: "날짜|시가|고가|저가|종가|거래량"
    val = item.attrib["data"].split("|")
    dt_str = val[0]
    try:
        o = float(val[1])
        h = float(val[2])
        l = float(val[3])
        c = float(val[4])
        dt = datetime.datetime.strptime(dt_str, "%Y%m%d")
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
    except Exception:
        pass

# 일별 수익률 계산
for i in range(1, len(data)):
    prev_c = data[i-1]["close"]
    curr_c = data[i]["close"]
    data[i]["return_pct"] = (curr_c - prev_c) / prev_c * 100.0
data[0]["return_pct"] = 0.0

monthly_stats = {}
for d in data:
    ym = d["year_month"]
    if ym not in monthly_stats:
        monthly_stats[ym] = {"returns": [], "ranges": [], "year": d["year"]}
    monthly_stats[ym]["returns"].append(d["return_pct"])
    monthly_stats[ym]["ranges"].append(d["range_pct"])

monthly_summary = []
for ym, stats in monthly_stats.items():
    if len(stats["returns"]) >= 5:
        std_dev = float(np.std(stats["returns"]))
        avg_range = float(np.mean(stats["ranges"]))
        monthly_summary.append({
            "year_month": ym,
            "year": stats["year"],
            "std_dev": std_dev,
            "avg_range": avg_range,
            "days": len(stats["returns"])
        })

sorted_by_vol = sorted(monthly_summary, key=lambda x: x["std_dev"], reverse=True)

all_std_devs = [m["std_dev"] for m in monthly_summary]
avg_historical_std = np.mean(all_std_devs)
median_historical_std = np.median(all_std_devs)

print("\n==================================================")
print("📊 [네이버 금융 실측 DB] 코스피 역대 월별 변동성 분석")
print("==================================================")
print(f"• 분석 대상 기간: {data[0]['date']} ~ {data[-1]['date']} (약 {data[-1]['year'] - data[0]['year']}년 간)")
print(f"• 전체 분석 월 수: 총 {len(monthly_summary)}개 월")
print(f"• 역대 30년 평균 일별 변동성(표준편차): {avg_historical_std:.2f}%")
print(f"• 역대 30년 중위 일별 변동성(표준편차): {median_historical_std:.2f}%")

print("\n🔥 역대 최악의 폭풍우 변동성 장세 Top 10 월:")
for rank, m in enumerate(sorted_by_vol[:10], 1):
    print(f"  {rank:2d}위: {m['year_month']} -> 일별 변동성(표준편차): {m['std_dev']:.2f}%, 평균 장중 변동폭: {m['avg_range']:.2f}%")

july_2026 = [m for m in monthly_summary if m["year_month"] == "2026-07"]
if not july_2026:
    # 가장 최근 월
    july_2026 = [monthly_summary[-1]]

m26 = july_2026[0]
rank_26 = sorted_by_vol.index(m26) + 1
pct_rank = (rank_26 / len(sorted_by_vol)) * 100.0

print(f"\n🎯 [2026년 7월 실측 백테스팅 변동성 데이터]")
print(f"  - 2026년 7월 일별 수익률 변동성(표준편차): {m26['std_dev']:.2f}%")
print(f"  - 2026년 7월 평균 일일 장중 변동폭: {m26['avg_range']:.2f}%")
print(f"  - 역대 {len(sorted_by_vol)}개 월 중 변동성 순위: 상위 {pct_rank:.1f}% ({rank_26}위 / {len(sorted_by_vol)}개 월)")
print(f"  - 역대 평시 평균 변동성({avg_historical_std:.2f}%) 대비: 약 {m26['std_dev'] / avg_historical_std:.1f}배 강력한 변동성 장세")
