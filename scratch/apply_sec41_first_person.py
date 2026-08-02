import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_sec41_start = """### 4.1 구글 Antigravity IDE 시작 가이드 및 100% 무상 혜택 활용법"""

repl_sec41_first_person = """### 4.1 구글 안티그래비티(Antigravity) 시작 가이드 및 100% 무상 혜택 활용법

제가 육아휴직 기간 밤을 새우며 퀀트 자동매매 봇과 교직 에듀테크 앱을 직접 개발할 때 가장 큰 은인을 꼽으라면 단연 **구글 안티그래비티(Google Antigravity)**입니다.

처음 자동매매를 마음먹었을 때 저 역시 '파이썬 프로그램을 어떻게 깔아야 하나?', '에러가 나면 누구한테 물어봐야 하나?' 하는 두려움이 컸습니다. 하지만 안티그래비티를 만나고 나서 모든 생각이 바뀌었습니다. 코딩 문법을 하나도 몰라도, 제가 원하는 투자 아이디어를 한글로 챗창에 치기만 하면 AI가 알아서 소스 코드를 짜고 오류까지 수정해 주었기 때문입니다. 독자 여러분도 겁먹으실 필요가 전혀 없습니다.

---

#### 💡 [제가 직접 경험한] 안티그래비티(Antigravity) 무상 혜택 3가지 꿀팁

##### 1. 결제 카드 등록 없는 100% 무상 활용
* 안티그래비티는 별도의 유료 구독이나 신용카드 등록 없이도, 구글 계정만 있으면 구글 딥마인드의 최첨단 AI 코딩 모델(Gemini)을 무상 무료 한도 내에서 넉넉하게 이용할 수 있습니다.

##### 2. 1분 만에 끝나는 초간단 설치와 구글 로그인
* VS Code 기반의 안티그래비티 IDE를 다운로드받아 실행한 뒤, 평소 쓰시던 구글 계정으로 로그인만 하면 모든 개발 준비가 1분 만에 끝납니다. 복잡한 환경 설정은 AI가 백그라운드에서 다 알아서 처리해 줍니다.

##### 3. 한글 대화(Vibe Coding)로 완성하는 나만의 비서
* "한국투자증권 API로 12개월 모멘텀 점수 산정해 줘", "매달 장 마감 전에 텔레그램으로 메시지 보내줘"처럼 평소 말씀하시는 한글로 지시하시면 됩니다. 

---

> 🏫 **황요한 교사의 현장 이야기: "퀀트 봇을 넘어 내 업무 비서가 되었습니다"**  
> *"제가 학교로 복직한 뒤 진해고 입학 상담 AI 챗봇(`jinhae-bot2`)을 만들고, 스마트폰 음성으로 세부능력 및 특기사항을 관찰 기록하는 대시보드 웹앱을 완성할 수 있었던 비결도 바로 이 안티그래비티 덕분이었습니다. 독자 여러분께서도 이 책을 통해 퀀트 봇을 완성해 보시면, 앞으로 여러분의 일상과 업무 아이디어를 현실 앱으로 만들어내는 엄청난 무기를 얻게 되실 겁니다."*

---"""

if target_sec41_start in text:
    text = text.replace(target_sec41_start, repl_sec41_first_person)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY REPLACED SECTION 4.1 WITH AUTHOR'S NATURAL FIRST-PERSON TONE!")
else:
    print("TARGET SECTION 4.1 HEADER NOT FOUND EXACTLY - CHECKING TEXT")
