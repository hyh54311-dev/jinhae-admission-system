import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_sec41_policy = """##### 1. 결제 카드 등록 없는 100% 무상 활용
* 안티그래비티는 별도의 유료 구독이나 신용카드 등록 없이도, 구글 계정만 있으면 구글 딥마인드의 최첨단 AI 코딩 모델(Gemini)을 무상 무료 한도 내에서 넉넉하게 이용할 수 있습니다."""

repl_sec41_policy = """##### 1. 현재(2026년 기준) 무상 제공 한도와 정책 유의사항
* **현재 현황:** 2026년 현시점 기준, 안티그래비티는 신용카드 등록이나 별도의 유료 구독 없이도 구글 계정만 있으면 일일 기본 무상 제공량(Gemini Flash 일 1,000회 이상, Pro 모델 일 50~100회 내외)을 제공합니다. 봇을 처음 만들거나 코드 몇 줄을 수정하는 작업에는 하루 10~20회 대화로도 충분하므로 현시점에서는 넉넉하게 활용할 수 있습니다.
* ⚠️ **독자 유의사항 (미래 정책 변동성):** 다만, 빅테크 기업의 클라우드 및 AI 서비스 정책은 향후 구글의 운영 방침이나 라이선스 개정에 따라 무상 한도가 축소되거나 일부 기능이 유료로 전환될 수 있습니다. 따라서 책을 읽고 실행하시는 시점의 구글 안티그래비티 공식 서비스 약관과 안내를 반드시 확인하시기 바랍니다."""

if target_sec41_policy in text:
    text = text.replace(target_sec41_policy, repl_sec41_policy)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY APPLIED CAUTIOUS & BALANCED FREE TIER POLICY TO SECTION 4.1!")
else:
    print("TARGET SECTION 4.1 POLICY TEXT NOT FOUND EXACTLY - CHECKING TEXT")
