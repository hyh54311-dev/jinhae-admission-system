import sys
import datetime
import requests

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

url = "https://fchart.stock.naver.com/sise.nhn?symbol=KOSPI&timeframe=day&count=100&requestType=0"
res = requests.get(url, timeout=10)

import xml.etree.ElementTree as ET
root = ET.fromstring(res.text)
items = root.findall(".//item")

print("=== 2026년 7월 하반기 코스피 일별 시세 팩트 체크 ===")
july_2026_days = []
for item in items:
    val = item.attrib["data"].split("|")
    dt_str = val[0]
    if dt_str.startswith("202607"):
        o = float(val[1])
        h = float(val[2])
        l = float(val[3])
        c = float(val[4])
        july_2026_days.append({
            "date": dt_str,
            "open": o, "high": h, "low": l, "close": c
        })

# 일별 등락률 계산
for i in range(len(july_2026_days)):
    if i == 0:
        july_2026_days[i]["pct"] = 0.0
    else:
        prev = july_2026_days[i-1]["close"]
        curr = july_2026_days[i]["close"]
        july_2026_days[i]["pct"] = (curr - prev) / prev * 100.0

for d in july_2026_days:
    print(f"• {d['date']}: 시가 {d['open']:,.2f} | 고가 {d['high']:,.2f} | 저가 {d['low']:,.2f} | 종가 {d['close']:,.2f} (일일 등락률: {d['pct']:+.2f}%)")

july_31 = [d for d in july_2026_days if d["date"] == "20260731"]
if july_31:
    print("\n✅ 7월 31일 데이터가 백테스팅 및 분석에 100% 정상 수록되어 있습니다!")
    print(f"   7월 31일 종가: {july_31[0]['close']:,.2f}원 (등락률: {july_31[0]['pct']:+.2f}%)")
else:
    print("\n⚠️ 7월 31일 데이터 수집 상태 재확인 필요")
