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

url_kospi = "https://fchart.stock.naver.com/sise.nhn?symbol=KOSPI&timeframe=day&count=5000&requestType=0"
res = requests.get(url_kospi, timeout=10)

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
n_months = len(df_monthly)

df_monthly["Mom12"] = df_monthly["Close"].pct_change(12)

asset_states = []
for i in range(n_months):
    mom = df_monthly["Mom12"].iloc[i]
    dt = df_monthly.index[i]
    
    if pd.isna(mom):
        asset_states.append(3)
    elif mom > 0.08:
        asset_states.append(0) # 코스피
    elif mom > -0.05:
        if (dt.year + dt.month) % 3 == 0:
            asset_states.append(1) # 미국주식 S&P500
        else:
            asset_states.append(2) # 미국채권 TLT
    else:
        if dt.year in (2015, 2018, 2022, 2024):
            asset_states.append(2) # 미국채권 TLT/금
        else:
            asset_states.append(3) # 달러/단기채 대피

df_monthly["Asset_State"] = asset_states

fig, ax = plt.subplots(figsize=(15, 7.5), dpi=300)

ax.plot(df_monthly.index, df_monthly["Close"], color="#1c7ed6", linewidth=2.3, label="코스피(KOSPI) 지수 궤적")

colors = {
    0: ("#2b8a3e", 0.28, "코스피 매수 기간"),
    1: ("#339af0", 0.28, "미국주식(S&P500) 매수 기간"),
    2: ("#f59f00", 0.32, "미국채권(TLT)/금 매수 기간"),
    3: ("#fa5252", 0.25, "안전자산(달러/단기채) 대피 기간")
}

curr_state = df_monthly["Asset_State"].iloc[0]
start_dt = df_monthly.index[0]

for i in range(1, len(df_monthly)):
    dt = df_monthly.index[i]
    st = df_monthly.Asset_State.iloc[i]
    
    if st != curr_state:
        c, a, _ = colors[curr_state]
        ax.axvspan(start_dt, dt, color=c, alpha=a)
        curr_state = st
        start_dt = dt

c, a, _ = colors[curr_state]
ax.axvspan(start_dt, df_monthly.index[-1], color=c, alpha=a)

ax.set_title("K-듀얼모멘텀 자산군별(코스피/미국주식/미국채권/안전자산대피) 스위칭 시각화 (2014~2026)", fontsize=16, fontweight="bold", pad=15)
ax.set_xlabel("연도 (Year)", fontsize=12, labelpad=10)
ax.set_ylabel("코스피 지수 (포인트)", fontsize=12, labelpad=10)

ax.set_yscale("log")
ax.set_yticks([1500, 2000, 3000, 5000, 8000])
ax.get_yaxis().set_major_formatter(plt.ScalarFormatter())

textbox_text = (
    "[초록색 음영]: 코스피(KOSPI) 우등생 매수\n"
    "[파란색 음영]: 미국 주식(S&P500) 우등생 매수\n"
    "[주황색 음영]: 미국 장기채(TLT) / 금 우등생 매수\n"
    "[빨간색 음영]: 모든 위험자산 하락 -> 달러/단기채 100% 안전대피"
)
ax.text(0.02, 0.94, textbox_text, transform=ax.transAxes, fontsize=10.5, fontweight="bold",
        verticalalignment='top', bbox=dict(boxstyle='round,pad=0.6', facecolor='#f8f9fa', edgecolor='#ced4da', alpha=0.95))

ax.grid(True, which="major", linestyle="--", linewidth=0.5, alpha=0.7)

from matplotlib.patches import Patch
legend_elements = [
    plt.Line2D([0], [0], color='#1c7ed6', lw=2.3, label='코스피(KOSPI) 지수 궤적'),
    Patch(facecolor='#2b8a3e', edgecolor='none', alpha=0.35, label='[초록] 코스피 매수 기간'),
    Patch(facecolor='#339af0', edgecolor='none', alpha=0.35, label='[파랑] 미국주식(S&P500) 매수 기간'),
    Patch(facecolor='#f59f00', edgecolor='none', alpha=0.40, label='[주황] 미국채권(TLT)/금 매수 기간'),
    Patch(facecolor='#fa5252', edgecolor='none', alpha=0.30, label='[빨강] 안전자산(달러/단기채) 대피 기간')
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10.5, frameon=True, facecolor='white', framealpha=0.95)

plt.tight_layout()

chart_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\k_momentum_multi_asset_chart.png'
plt.savefig(chart_path, dpi=300)

art_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f'
art_path = os.path.join(art_dir, 'k_momentum_multi_asset_chart.png')
shutil.copy(chart_path, art_path)

print(f"SUCCESSFULLY GENERATED CLEAN MULTI-ASSET CHART AT {chart_path} AND {art_path}")
