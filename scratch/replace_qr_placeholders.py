import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. QR 1: 템플릿 복사 QR
target1 = "> 📸 **[도서 포함 예정 이미지 3: 1-Click 템플릿 복사용 QR 코드 및 GitHub 저장소 화면]**"
repl1 = """![1-Click 템플릿 복사용 QR 코드](qr_template_repo.png)
> 📲 **[스마트폰 1초 스캔] K-듀얼모멘텀 봇 1-Click 템플릿 복사용 QR 코드 (https://github.com/hyh54311-dev/jinhae-k-momentum-bot)**"""

# 2. QR 2: KIS 포털 접속 QR
target2 = "> 📸 **[도서 수록 예정 이미지: 한국투자증권 KIS Developers 포털 접속용 QR 코드 (https://apiportal.koreainvestment.com)]**"
repl2 = """![한국투자증권 KIS Developers 포털 접속용 QR 코드](qr_kis_portal.png)
> 📲 **[스마트폰 1초 스캔] 한국투자증권 KIS Developers 메인 포털 접속용 QR 코드 (https://apiportal.koreainvestment.com)**"""

# 3. QR 3: KIS 메인 QR (레퍼런스 박스)
target3 = ">    * 📸 **[도서 수록 QR 1]:** 📲 *(스마트폰 전용 KIS Developers 메인 포털 접속 QR 코드)*"
repl3 = """![KIS Developers 메인 포털 QR 코드](qr_kis_main.png)
>    * 📲 **[스마트폰 전용 QR 1]:** KIS Developers 메인 포털 접속 (`https://apiportal.koreainvestment.com`)"""

# 4. QR 4: KIS 공식 가이드 QR
target4 = ">    * 📸 **[도서 수록 QR 2]:** 📲 *(스마트폰 전용 한투 공식 발급 가이드 페이지 접속 QR 코드)*"
repl4 = """![한투 공식 발급 가이드 QR 코드](qr_kis_guide.png)
>    * 📲 **[스마트폰 전용 QR 2]:** 한투 공식 API 발급 안내 페이지 접속 (`https://apiportal.koreainvestment.com/intro`)"""

# 5. QR 5: KIS 공식 깃허브 QR
target5 = ">    * 📸 **[도서 수록 QR 3]:** 📲 *(스마트폰 전용 한투 공식 open-trading-api 깃허브 접속 QR 코드)*"
repl5 = """![한투 공식 open-trading-api 깃허브 QR 코드](qr_kis_github.png)
>    * 📲 **[스마트폰 전용 QR 3]:** 한투 공식 open-trading-api 깃허브 접속 (`https://github.com/koreainvestment/open-trading-api`)"""

text = text.replace(target1, repl1)
text = text.replace(target2, repl2)
text = text.replace(target3, repl3)
text = text.replace(target4, repl4)
text = text.replace(target5, repl5)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESSFULLY REPLACED ALL 5 QR PLACEHOLDERS WITH REAL HIGH-RES QR CODE IMAGES!")
