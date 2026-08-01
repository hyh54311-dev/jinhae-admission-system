import os
import urllib.request
import urllib.parse

output_dir = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder'
artifact_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f'

# 3대 핵심 QR 코드 정의
qr_targets = {
    'qr_template_repo.png': 'https://github.com/hyh54311-dev/jinhae-k-momentum-bot',
    'qr_kis_portal.png': 'https://apiportal.koreainvestment.com',
    'qr_kis_github.png': 'https://github.com/koreainvestment/open-trading-api'
}

for filename, url in qr_targets.items():
    encoded_url = urllib.parse.quote(url)
    api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={encoded_url}&margin=10"
    file_dest = os.path.join(output_dir, filename)
    artifact_dest = os.path.join(artifact_dir, filename)
    urllib.request.urlretrieve(api_url, file_dest)
    urllib.request.urlretrieve(api_url, artifact_dest)

print("3 CORE HIGH-RES QR CODE IMAGES RE-GENERATED SUCCESSFULLY!")

# 원고 정돈
file_path = os.path.join(output_dir, 'retirement_savings_dual_momentum_guide.md')
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 원고 4.1절의 중복 및 난잡했던 QR 섹션을 3대 QR 중심으로 전면 정돈
target_section = """##### 2. [2단계] 핸드폰으로 아래 QR 코드를 스캔하여 KIS 포털 접속하기
* 스마트폰 기본 카메라나 네이버/카카오톡 스캔 기능으로 아래 **QR 코드**를 스캔하면 한국투자증권 개발자 포털로 1초 만에 바로 이동합니다. (또는 주소창에 직접 입력하셔도 됩니다.)
  > 📱 **[스마트폰 전용 1초 접속 QR 코드]:**  
  ![한국투자증권 KIS Developers 포털 접속용 QR 코드](qr_kis_portal.png)
> 📲 **[스마트폰 1초 스캔] 한국투자증권 KIS Developers 메인 포털 접속용 QR 코드 (https://apiportal.koreainvestment.com)**
  > 🌐 **[한국투자증권 공식 개발자 사이트 3대 레퍼런스 & QR 코드 안내]:**  
  > 
  > 1. 🌐 **[한국투자증권 KIS Developers 공식 포털]:** `https://apiportal.koreainvestment.com`  
  ![KIS Developers 메인 포털 QR 코드](qr_kis_main.png)
>    * 📲 **[스마트폰 전용 QR 1]:** KIS Developers 메인 포털 접속 (`https://apiportal.koreainvestment.com`)  
  >    * **[접속 시 나오는 내용]:** KIS 개발자 센터 메인 페이지로, PC나 스마트폰으로 로그인하여 계좌 연동 신청 및 `AppKey`/`AppSecret`을 발급받는 메인 포털입니다.  
  > 
  > 2. 📘 **[한투 공식 Open API 서비스 소개 및 발급 가이드]:** `https://apiportal.koreainvestment.com/intro`  
  ![한투 공식 발급 가이드 QR 코드](qr_kis_guide.png)
>    * 📲 **[스마트폰 전용 QR 2]:** 한투 공식 API 발급 안내 페이지 접속 (`https://apiportal.koreainvestment.com/intro`)  
  >    * **[접속 시 나오는 내용]:** API 발급이 처음인 초보 독자를 위해 계좌 신청부터 앱키 수령까지 전 과정을 그림과 함께 친절하게 안내하는 한국투자증권 공식 사용 설명서 페이지입니다.  
  > 
  > 3. 💻 **[한국투자증권 공식 Open Trading API 깃허브 저장소]:** `https://github.com/koreainvestment/open-trading-api`  
  ![한투 공식 open-trading-api 깃허브 QR 코드](qr_kis_github.png)
>    * 📲 **[스마트폰 전용 QR 3]:** 한투 공식 open-trading-api 깃허브 접속 (`https://github.com/koreainvestment/open-trading-api`)  
  >    * **[접속 시 나오는 내용]:** 한투 본사 개발팀이 직접 운영하는 공식 파이썬 샘플 코드 창고로, 본서의 봇 코드 외에 다른 주식 API 기능을 확장하거나 참고할 때 활용하는 공식 예제 모음집입니다.
* 한국투자증권 계정 아이디와 비밀번호로 로그인합니다."""

replacement_section = """##### 2. [2단계] 핸드폰으로 아래 QR 코드를 스캔하여 KIS 포털 접속하기
* 스마트폰 기본 카메라나 네이버/카카오톡 스캔 기능으로 아래 **QR 코드**를 스캔하면 한국투자증권 개발자 포털로 1초 만에 바로 이동합니다. (또는 주소창에 직접 입력하셔도 됩니다.)

![한국투자증권 KIS Developers 포털 접속용 QR 코드](qr_kis_portal.png)
> 📲 **[도서 실전 QR 2] 한국투자증권 KIS Developers 공식 메인 포털 1초 접속 QR 코드 (https://apiportal.koreainvestment.com)**
> * **[접속 시 나오는 내용]:** KIS 개발자 센터 메인 페이지로, PC나 스마트폰으로 로그인하여 계좌 연동 신청 및 `AppKey`/`AppSecret`을 발급받는 메인 포털입니다.

---

> 🌐 **[한국투자증권 공식 개발자 파이썬 샘플 코드 저장소 레퍼런스]:**  
> 
> ![한투 공식 open-trading-api 깃허브 QR 코드](qr_kis_github.png)
> 📲 **[도서 실전 QR 3] 한국투자증권 공식 open-trading-api 깃허브 저장소 접속 QR 코드 (https://github.com/koreainvestment/open-trading-api)**
> * **[접속 시 나오는 내용]:** 한투 본사 개발팀이 직접 운영하는 공식 파이썬 샘플 코드 창고로, 본서의 봇 코드 외에 다른 주식 API 기능을 확장하거나 참고할 때 활용하는 공식 예제 모음집입니다.

* 한국투자증권 계정 아이디와 비밀번호로 로그인합니다."""

text = text.replace(target_section, replacement_section)

# QR 1 부분 단정하게 정돈
target_qr1 = """![1-Click 템플릿 복사용 QR 코드](qr_template_repo.png)
> 📲 **[스마트폰 1초 스캔] K-듀얼모멘텀 봇 1-Click 템플릿 복사용 QR 코드 (https://github.com/hyh54311-dev/jinhae-admission-system)**"""

repl_qr1 = """![1-Click 템플릿 복사용 QR 코드](qr_template_repo.png)
> 📲 **[도서 실전 QR 1] K-듀얼모멘텀 봇 1-Click GitHub 템플릿 복사 QR 코드 (https://github.com/hyh54311-dev/jinhae-k-momentum-bot)**
> * 💡 **[독자 접속 안내]:** 저장소가 `Public(전체 공개)`으로 설정되어 있어야 스마트폰 비로그인 상태에서도 404 오류 없이 100% 정상 접속됩니다."""

text = text.replace(target_qr1, repl_qr1)
# 혹시 이전 주소가 파싱되어 있을 수 있으니 서브 교체
text = text.replace("https://github.com/hyh54311-dev/jinhae-admission-system", "https://github.com/hyh54311-dev/jinhae-k-momentum-bot")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("MANUSCRIPT SUCCESSFULLY STREAMLINED TO 3 CORE QR CODES!")
