import sys
import datetime
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 한글 폰트 설정 (Windows 맑은 고딕)
plt.rc('font', family='Malgun Gothic')
plt.rc('axes', unicode_minus=False)

# 네이버 금융 코스피 일별 시세 데이터 가져오기 (30년치)
url = "https://fchart.stock.naver.com/sise.nhn?symbol=KOSPI&timeframe=day&count=10000&requestType=0"
print(">> 네이버 금융 코스피 장기 일별 데이터 수집 중...")
res = requests.get(url, timeout=15)

import xml.etree.ElementTree as ET
root = ET.fromstring(res.text)
items = root.findall(".//item")

dates = []
closes = []

for item in items:
    val = item.attrib["data"].split("|")
    dt_str = val[0]
    try:
        c = float(val[4])
        dt = datetime.datetime.strptime(dt_str, "%Y%m%d")
        dates.append(dt)
        closes.append(c)
    except Exception:
        pass

df = pd.DataFrame({"Date": dates, "Close": closes})
df.set_index("Date", inplace=True)
df.sort_index(inplace=True)

# 월별 종가 데이터 추출 (Monthly Resample)
df_monthly = df.resample("M").last()

# 12개월 모멘텀 계산 (12-month Momentum = Current Close / 12-month ago Close - 1)
df_monthly["Mom12"] = df_monthly["Close"].pct_change(12)

# 코스피 매수 시그널 조건:
# 1) 코스피 12개월 수익률이 0보다 큼 (> 0)
# 2) (간단 듀얼모멘텀 대표 시그널) 12개월 모멘텀이 양수인 구간을 코스피 모멘텀 매수 구간으로 지정
df_monthly["Signal"] = df_monthly["Mom12"] > 0

print(f">> 분석 월 수: {len(df_monthly)}개 월 ({df_monthly.index[0].strftime('%Y-%m')} ~ {df_monthly.index[-1].strftime('%Y-%m')})")

# 차트 그리기 (고화질 300 DPI)
fig, ax = plt.subplots(figsize=(14, 7), dpi=300)

# 코스피 지수 꺾은선 그래프
ax.plot(df_monthly.index, df_monthly["Close"], color="#1f77b4", linewidth=2.0, label="코스피(KOSPI) 지수 궤적")

# 코스피 매수 구간 세로 음영 처리
signal_series = df_monthly["Signal"]
in_signal = False
start_date = None

for i in range(len(df_monthly)):
    dt = df_monthly.index[i]
    sig = signal_series.iloc[i]
    
    if sig and not in_signal:
        in_signal = True
        start_date = dt
    elif not sig and in_signal:
        in_signal = False
        end_date = dt
        ax.axvspan(start_date, end_date, color="#2ca02c", alpha=0.22, label="K-듀얼모멘텀 코스피 매수 기간" if 'axvspan_labeled' not in locals() else "")
        axvspan_labeled = True

# 마지막 구간 처리
if in_signal:
    ax.axvspan(start_date, df_monthly.index[-1], color="#2ca02c", alpha=0.22, label="K-듀얼모멘텀 코스피 매수 기간" if 'axvspan_labeled' not in locals() else "")

# 차트 스타일링
ax.set_title("K-듀얼모멘텀 코스피(KOSPI) 구간별 매수/피신 백테스트 시각화 (1995~2026)", fontsize=16, fontweight="bold", pad=15)
ax.set_xlabel("연도 (Year)", fontsize=12, labelpad=10)
ax.set_ylabel("코스피 지수 (포인트)", fontsize=12, labelpad=10)

# Y축 로그 스케일 또는 일반 스케일
ax.set_yscale("log")
ax.set_yticks([500, 1000, 2000, 3000, 5000, 8000])
ax.get_yaxis().set_major_formatter(plt.ScalarFormatter())

# 주석 설명 텍스트 박스
textbox_text = (
    "🟩 [초록색 음영 구간]: 코스피 상승 모멘텀 포착 -> KOSPI 매수 집행\n"
    "⬜ [흰색/무음영 구간]: 코스피 하락/정체 -> 미국주식, 금, 국채, 달러 안전자산으로 대피"
)
ax.text(0.02, 0.92, textbox_text, transform=ax.transAxes, fontsize=11,
        verticalalignment='top', bbox=dict(boxstyle='round,pad=0.6', facecolor='white', edgecolor='#cccccc', alpha=0.9))

ax.grid(True, which="major", linestyle="--", linewidth=0.5, alpha=0.7)

# 범례 설정
from matplotlib.patches import Patch
legend_elements = [
    plt.Line2D([0], [0], color='#1f77b4', lw=2, label='코스피(KOSPI) 지수 궤적'),
    Patch(facecolor='#2ca02c', edgecolor='none', alpha=0.3, label='코스피 매수 기간 (초록색 음영)'),
    Patch(facecolor='white', edgecolor='#cccccc', label='미국주식 / 안전자산 대피 기간 (무음영)')
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=11, frameon=True, facecolor='white', framealpha=0.9)

plt.tight_layout()

chart_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\k_momentum_kospi_signal_chart.png'
plt.savefig(chart_path, dpi=300)
print(f"SUCCESSFULLY GENERATED CHART AT {chart_path}")
