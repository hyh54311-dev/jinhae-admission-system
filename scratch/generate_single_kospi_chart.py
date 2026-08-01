import sys
import datetime
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import shutil
import os

plt.rc('font', family='Malgun Gothic')
plt.rc('axes', unicode_minus=False)

url_kospi = "https://fchart.stock.naver.com/sise.nhn?symbol=KOSPI&timeframe=day&count=10000&requestType=0"
res = requests.get(url_kospi, timeout=15)

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

df_monthly = df.resample("ME").last()
df_monthly["Mom12"] = df_monthly["Close"].pct_change(12)
df_monthly["Signal"] = df_monthly["Mom12"] > 0

# 도서 인쇄에 최적화된 300 DPI 초고화질 단일 음영 차트
fig, ax = plt.subplots(figsize=(14, 7), dpi=300)

# 코스피 꺾은선
ax.plot(df_monthly.index, df_monthly["Close"], color="#1c7ed6", linewidth=2.2, label="코스피(KOSPI) 지수 궤적")

# 단 하나의 깔끔한 세로 음영: 코스피 매수 기간만 표시
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
        ax.axvspan(start_date, end_date, color="#2b8a3e", alpha=0.25)

if in_signal:
    ax.axvspan(start_date, df_monthly.index[-1], color="#2b8a3e", alpha=0.25)

ax.set_title("K-듀얼모멘텀 코스피(KOSPI) 구간별 매수/대피 시각화 (2014~2026)", fontsize=16, fontweight="bold", pad=15)
ax.set_xlabel("연도 (Year)", fontsize=12, labelpad=10)
ax.set_ylabel("코스피 지수 (포인트)", fontsize=12, labelpad=10)

ax.set_yscale("log")
ax.set_yticks([1500, 2000, 3000, 5000, 8000])
ax.get_yaxis().set_major_formatter(plt.ScalarFormatter())

# 심플한 안내 텍스트 박스
textbox_text = (
    "[초록색 음영 구간]: 코스피 모멘텀 우수 -> KOSPI 매수 집행\n"
    "[무음영 흰색 구간]: 코스피 하락/정체 -> 미국주식 / 채권 / 달러 안전자산으로 대피"
)
ax.text(0.02, 0.93, textbox_text, transform=ax.transAxes, fontsize=11, fontweight="bold",
        verticalalignment='top', bbox=dict(boxstyle='round,pad=0.6', facecolor='#f8f9fa', edgecolor='#ced4da', alpha=0.95))

ax.grid(True, which="major", linestyle="--", linewidth=0.5, alpha=0.7)

from matplotlib.patches import Patch
legend_elements = [
    plt.Line2D([0], [0], color='#1c7ed6', lw=2.2, label='코스피(KOSPI) 지수 궤적'),
    Patch(facecolor='#2b8a3e', edgecolor='none', alpha=0.35, label='코스피 매수 기간 (초록색 음영)'),
    Patch(facecolor='white', edgecolor='#ced4da', label='미국주식 / 안전자산 대피 기간 (무음영)')
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=11, frameon=True, facecolor='white', framealpha=0.95)

plt.tight_layout()

chart_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\k_momentum_kospi_single_chart.png'
plt.savefig(chart_path, dpi=300)

art_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f'
art_path = os.path.join(art_dir, 'k_momentum_kospi_single_chart.png')
shutil.copy(chart_path, art_path)

print(f"SUCCESSFULLY GENERATED SINGLE SHADED KOSPI CHART AT {chart_path} AND {art_path}")
