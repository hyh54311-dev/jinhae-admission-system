import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import shutil
import os

# 한글 폰트 설정 (Windows 맑은 고딕)
plt.rc('font', family='Malgun Gothic')
plt.rc('axes', unicode_minus=False)

fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# 배경 색상
fig.patch.set_facecolor('#ffffff')

# 타이틀
ax.text(50, 93, "주식·ETF 투자 5대 핵심 계좌 한눈에 보기", fontsize=20, fontweight='bold', ha='center', color='#1e293b')
ax.text(50, 87, "내 투자 목적과 기간에 딱 맞는 최적의 계좌를 3초 만에 선택하세요!", fontsize=12, ha='center', color='#64748b')

# 5대 계좌 카드 데이터
cards = [
    {
        "title": "1. 일반 주식 계좌 (상품코드 01)",
        "sub": "자유로운 개별주 & 해외 직투",
        "tag": "기본 필수 계좌",
        "color": "#e2e8f0",
        "header_color": "#475569",
        "desc": ["• 모든 국내/해외 주식 자유 거래", "• 양도세 22% (해외 250만 원 공제)", "• 입출금 제약 제로"],
        "x": 3, "y": 48, "w": 28, "h": 33
    },
    {
        "title": "2. ISA 중개형 계좌",
        "sub": "3년 중단기 비과세 & 분리과세",
        "tag": "중단기 절세 계좌",
        "color": "#e0f2fe",
        "header_color": "#0284c7",
        "desc": ["• 순이익 200~400만 원 비과세", "• 초과분 9.9% 저율 분리과세", "• 국내 상장 해외 ETF 투자"],
        "x": 36, "y": 48, "w": 28, "h": 33
    },
    {
        "title": "3. 연금저축펀드 (상품코드 22) 🏆",
        "sub": "연 600만 원 세액공제 & 과세이연",
        "tag": "★ K-퀀트 봇 메인 무대",
        "color": "#dcfce7",
        "header_color": "#16a34a",
        "desc": ["• 연 600만 원 세액공제 환급금", "• 건보료 0.0% (전액 100% 제외)", "• 장기 복리 스노우볼 결실"],
        "x": 69, "y": 48, "w": 28, "h": 33
    },
    {
        "title": "4. IRP 개인형 퇴직연금",
        "sub": "연금저축 합산 900만 원 확장",
        "tag": "노후 세액공제 확장",
        "color": "#fef3c7",
        "header_color": "#d97706",
        "desc": ["• 세액공제 한도 900만 원 확장", "• 안전자산 30% 의무 보유", "• 퇴직금 이치 및 은퇴 준비"],
        "x": 19.5, "y": 8, "w": 28, "h": 33
    },
    {
        "title": "5. CMA 파킹 계좌",
        "sub": "단 하루만 맡겨도 매일 이자",
        "tag": "현금 대기 파킹",
        "color": "#f1f5f9",
        "header_color": "#64748b",
        "desc": ["• 대기 현금 & 예수금 전용", "• 매일 이자 차곡차곡 지급", "• 주식 매수 전 잠시 대기"],
        "x": 52.5, "y": 8, "w": 28, "h": 33
    }
]

for card in cards:
    # 카드 외곽선 Box
    rect = patches.FancyBboxPatch((card["x"], card["y"]), card["w"], card["h"],
                                  boxstyle="round,pad=1,rounding_size=2",
                                  linewidth=1.5, edgecolor=card["header_color"], facecolor=card["color"])
    ax.add_patch(rect)
    
    # 카드 헤더
    ax.text(card["x"] + card["w"]/2, card["y"] + card["h"] - 4, card["title"],
            fontsize=11, fontweight='bold', ha='center', color=card["header_color"])
    ax.text(card["x"] + card["w"]/2, card["y"] + card["h"] - 8, card["sub"],
            fontsize=9.5, ha='center', color='#334155')
    
    # 태그
    tag_rect = patches.FancyBboxPatch((card["x"] + 3, card["y"] + card["h"] - 13.5), card["w"] - 6, 4,
                                       boxstyle="round,pad=0.5,rounding_size=1",
                                       linewidth=0, facecolor=card["header_color"])
    ax.add_patch(tag_rect)
    ax.text(card["x"] + card["w"]/2, card["y"] + card["h"] - 11.5, card["tag"],
            fontsize=9, fontweight='bold', ha='center', color='#ffffff')
    
    # 설명 Bullet points
    for idx, d in enumerate(card["desc"]):
        ax.text(card["x"] + 2.5, card["y"] + card["h"] - 18 - (idx * 4.5), d,
                fontsize=9, ha='left', color='#1e293b')

plt.tight_layout()

chart_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\5_core_investment_accounts_map.png'
plt.savefig(chart_path, dpi=300)

art_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f'
art_path = os.path.join(art_dir, '5_core_investment_accounts_map.png')
shutil.copy(chart_path, art_path)

print(f"SUCCESSFULLY GENERATED 5 ACCOUNTS MAP AT {chart_path} AND {art_path}")
