import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import shutil
import os

# 한글 폰트 설정 (Windows 맑은 고딕)
plt.rc('font', family='Malgun Gothic')
plt.rc('axes', unicode_minus=False)

# 1도 흑백 출판용 캔버스 (A4 비율 고려)
fig, ax = plt.subplots(figsize=(13, 8.5), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# 배경 흰색 (1도 인쇄)
fig.patch.set_facecolor('#ffffff')

# 타이틀 (큼직하고 명확하게)
ax.text(50, 93, "[출판용 1도 마인드맵] 주식·ETF 투자 5대 핵심 계좌 지형도", fontsize=18, fontweight='bold', ha='center', color='#000000')
ax.text(50, 87, "내 투자 목적과 기간에 딱 맞는 최적의 계좌를 한눈에 선택하세요", fontsize=11, ha='center', color='#333333')

# 마인드맵 중앙 노드 (Root)
root_box = patches.FancyBboxPatch((35, 38), 30, 14,
                                   boxstyle="round,pad=1,rounding_size=2",
                                   linewidth=2.5, edgecolor='#000000', facecolor='#f0f0f0')
ax.add_patch(root_box)
ax.text(50, 46.5, "주식·ETF 투자\n5대 핵심 계좌", fontsize=14, fontweight='bold', ha='center', va='center', color='#000000')

# 좌측 매매 그룹 박스 (상단: 절세/연금계좌 3종, 하단: 일반계좌 1종)
box_top_left = patches.FancyBboxPatch((4, 58), 38, 20,
                                       boxstyle="round,pad=0.8,rounding_size=1.5",
                                       linewidth=2, edgecolor='#000000', facecolor='#ffffff')
ax.add_patch(box_top_left)
ax.text(23, 73, "■ [절세 & 연금형 계좌] (3대 무대)", fontsize=11, fontweight='bold', ha='center', color='#000000')
ax.text(23, 67, "• 연금저축펀드 (상품코드 22) [★ 봇 메인]", fontsize=9.5, fontweight='bold', ha='center', color='#000000')
ax.text(23, 63, "• ISA 중개형 (3년 비과세/분리과세)", fontsize=9, ha='center', color='#222222')
ax.text(23, 59, "• IRP 퇴직연금 (연금저축 합산 900만 공제)", fontsize=9, ha='center', color='#222222')

box_bot_left = patches.FancyBboxPatch((4, 12), 38, 20,
                                       boxstyle="round,pad=0.8,rounding_size=1.5",
                                       linewidth=2, edgecolor='#000000', facecolor='#ffffff')
ax.add_patch(box_bot_left)
ax.text(23, 27, "■ [일반 매매 계좌] (1대 무대)", fontsize=11, fontweight='bold', ha='center', color='#000000')
ax.text(23, 21, "• 일반 주식 계좌 (상품코드 01)", fontsize=9.5, fontweight='bold', ha='center', color='#000000')
ax.text(23, 16, "• 해외직투/개별주/제약 없는 자유 거래", fontsize=9, ha='center', color='#222222')

# 우측 파킹 그룹 박스 (1대 보조 계좌)
box_right = patches.FancyBboxPatch((58, 35), 38, 20,
                                    boxstyle="round,pad=0.8,rounding_size=1.5",
                                    linewidth=2, edgecolor='#000000', facecolor='#ffffff')
ax.add_patch(box_right)
ax.text(77, 50, "■ [현금 파킹 계좌] (1대 보조)", fontsize=11, fontweight='bold', ha='center', color='#000000')
ax.text(77, 44, "• CMA 계좌 (종합자산관리)", fontsize=9.5, fontweight='bold', ha='center', color='#000000')
ax.text(77, 39, "• 매수 전 대기현금 & 예수금 이자 수입", fontsize=9, ha='center', color='#222222')

# 화살표 및 가이드
ax.annotate("", xy=(35, 68), xytext=(45, 52),
            arrowprops=dict(arrowstyle="->", color="#000000", lw=2))
ax.annotate("", xy=(35, 22), xytext=(45, 40),
            arrowprops=dict(arrowstyle="->", color="#000000", lw=2))
ax.annotate("", xy=(65, 45), xytext=(55, 45),
            arrowprops=dict(arrowstyle="->", color="#000000", lw=2))

plt.tight_layout()

chart_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\5_core_investment_accounts_mindmap_mono.png'
plt.savefig(chart_path, dpi=300)

art_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f'
art_path = os.path.join(art_dir, '5_core_investment_accounts_mindmap_mono.png')
shutil.copy(chart_path, art_path)

print(f"SUCCESSFULLY GENERATED CLEAN PERFECT MONO MINDMAP AT {chart_path}")
