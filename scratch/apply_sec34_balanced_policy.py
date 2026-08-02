import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_sec34_policy = """Google Antigravity AI를 활용한 '바이브 코딩(Vibe Coding)'의 가장 뛰어난 점은, 복잡한 파이썬 코딩을 몰라도 내가 원하는 투자 로직을 자연어 대화로 지시하여 완전 무인 자동화 봇을 완성할 수 있다는 것입니다."""

repl_sec34_policy = """구글 안티그래비티(Google Antigravity) AI를 활용한 '바이브 코딩(Vibe Coding)'의 가장 뛰어난 점은, 복잡한 파이썬 코딩을 몰라도 내가 원하는 투자 로직을 자연어 대화로 지시하여 완전 무인 자동화 봇을 완성할 수 있다는 것입니다.

---

##### 💡 [저자의 신중한 안내] 현재(2026년 기준) 무상 사용 한도와 향후 정책 변동성
* **2026년 현시점 팩트:** 현재 안티그래비티는 구글 계정만 있으면 신용카드 등록 없이도 일일 기본 무상 제공량(Gemini Flash 모델 일 1,000회 이상, Pro 모델 일 50~100회 내외)을 넉넉하게 제공합니다. 나만의 연금저축 퀀트 봇(`kis_bot_multi.py`)을 구축하거나 ETF 종목을 교체하는 데에는 하루 10~20회 대화로도 충분하므로 현시점에서는 추가 비용 없이 충분히 활용할 수 있습니다.
* ⚠️ **향후 정책 변동 가능성 안내:** 다만, 빅테크 기업의 AI 서비스 및 클라우드 무료 제공 정책은 향후 구글의 운영 방침이나 라이선스 규정 개정에 따라 무료 이용 한도가 변경되거나 서비스 조건이 달라질 수 있습니다. 독자 여러분께서는 책을 읽고 실행하시는 시점의 구글 안티그래비티 공식 서비스 약관을 함께 확인해 주시기 바랍니다."""

if target_sec34_policy in text:
    text = text.replace(target_sec34_policy, repl_sec34_policy)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY APPLIED CAUTIOUS & BALANCED FREE TIER POLICY TO SECTION 3.4!")
else:
    print("TARGET SECTION 3.4 POLICY TEXT NOT FOUND EXACTLY - CHECKING TEXT")
