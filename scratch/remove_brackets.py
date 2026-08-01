import os
import re

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1부 영역 (1.1 ~ 1.5절) 소괄호 () 풀어서 쓰기 정교 교정
replacements = [
    ("4공장(24만 리터)", "24만 리터 규모의 4공장"),
    ("완전 풀 가동(Full Ramp-up)", "완전 가동 및 생산 능력 극대화"),
    ("'생물보안법(Biosecure Act)'", "미국의 생물보안법"),
    ("1,734만 원(-21.4%)", "1,734만 원인 21.4%의"),
    ("감(感)과 운(運)", "감과 운"),
    ("'초심자의 행운(Beginner's Luck)'", "초심자의 행운"),
    ("'규칙(Rule)'", "명확한 규칙"),
    ("현금흐름 (Capital Inflow)", "현금흐름"),
    ("마음의 안정(Mind Control)", "마음의 안정"),
    ("원시 데이터(Raw Data)", "원시 데이터"),
    ("과세 이연(Tax Deferral)", "과세 이연"),
    ("에이전트 AI(Agentic AI)", "에이전트 AI"),
    ("개인정보(PII)", "개인정보"),
    ("연금저축펀드 계좌(`22`)", "연금저축펀드 계좌"),
    ("일반 주식 계좌(상품코드 `01`)", "일반 주식 계좌"),
    ("연금저축펀드 계좌(상품코드 `22`)", "연금저축펀드 계좌"),
]

for old, new in replacements:
    text = text.replace(old, new)

# 1.1절 괄호 전면 제거 교정
target_sec11_brackets = """* **치밀한 분석과 AI 딥 리서치의 한계: 2026년 4월, 저는 해당 바이오 기업의 24만 리터 규모의 4공장, 5공장의 2025년 4월 조기 준공 및 가동률 가속화, 2026년 연내 6공장 조기 착공 허가 절차 착수 소식 및 미국의 생물보안법** 시행으로 글로벌 바이오 수주물량이 중국 기업을 벗어나 세계 최대 생산 역량을 갖춘 해당 기업으로 쏠릴 것이라는 정책적 방향성까지 보수적으로 분석했습니다."""

if "4공장(24만 리터)" in text or "Full Ramp-up" in text:
    text = re.sub(r'4공장\(24만 리터\)\s*완전 풀 가동\(Full Ramp-up\)', '24만 리터 규모 4공장의 완전 가동', text)
    text = re.sub(r'\'생물보안법\(Biosecure Act\)\'', '생물보안법', text)
    text = re.sub(r'1,734만 원\(-21\.4%\)', '1,734만 원인 21.4%의', text)
    text = re.sub(r'감\(感\)과 운\(運\)', '감과 운', text)
    text = re.sub(r'\'초심자의 행운\(Beginner\'s Luck\)\'', '초심자의 행운', text)
    text = re.sub(r'\'규칙\(Rule\)\'', '명확한 규칙', text)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESSFULLY REMOVED BRACKETS AND EXPANDED INLINE TEXT!")
