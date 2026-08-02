import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 4.3절 및 에필로그 정밀 반영
target_sec43_start = """### 🗺️ [독자 맞춤형] K-퀀트 봇 3단계 마스터 로드맵"""

repl_sec43_framework = """### 4.3 [저자의 개발 에세이] Agentic AI 시대, 교사의 사고 확장과 새로운 지평

제가 육아휴직 기간 동안 밤을 새우며 완성했던 퀀트 자동매매 봇은 단순한 재테크 도구를 넘어, 제 삶과 교직관을 송두리째 바꾼 거대한 '사고 확장의 전환점'이었습니다.

---

#### 💡 [저자 황요한의 3단계 사고 확장 프레임워크] "퀀트 봇에서 교직 에듀테크로"

##### 1단계: 아이디어 발상 (Idea Generation)
* 엑셀 손수 노동과 매수 버튼 앞의 감정 고통을 없애겠다는 자산 관리 아이디어가, 학교 현장으로 복직한 뒤에는 "학생들의 탐구활동과 세특 관찰 기록을 스마트폰 음성으로 자동화할 수 없을까?"라는 교직 아이디어로 확장되었습니다.

##### 2단계: AI 에이전트 바이브 코딩 (Vibe Coding with Antigravity)
* 복잡한 코딩 문법을 몰라도 구글 안티그래비티(Antigravity) AI와 한글로 대화하며 퀀트 봇 알고리즘을 짰던 경험은, 복직 후 진해고 입학 상담 AI 챗봇(`jinhae-bot2`)과 3학년 자율교육과정 탐구보고서 세특 대시보드 웹앱을 단 며칠 만에 직접 개발해 내는 원동력이 되었습니다.

##### 3단계: 100% 무인 자동화 배포 (Serverless Automation)
* 깃허브 무인 서버(GitHub Actions)로 매달 퀀트 봇이 알아서 매매하도록 구축한 서버리스 노하우는, 학교 수업과 행정 업무에서 교사의 반복 노동을 '0'으로 만드는 에듀테크 자동화 파이프라인의 튼튼한 뼈대가 되었습니다.

---

### 🗺️ [독자 맞춤형] K-퀀트 봇 3단계 마스터 로드맵"""

if target_sec43_start in text:
    text = text.replace(target_sec43_start, repl_sec43_framework)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY APPLIED SECTION 4.3 3-STEP FRAMEWORK TO MANUSCRIPT!")
else:
    print("TARGET SECTION 4.3 START TEXT NOT FOUND EXACTLY - CHECKING TEXT")
