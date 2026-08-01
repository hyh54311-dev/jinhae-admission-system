import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_sec14_item4 = """* **4. 교과 교수-평가-기록(교수평기) 및 세특 자동화 웹앱 (Google Apps Script 연동)**
  * **주소 및 환경:** Google Apps Script (`script.google.com`) 및 구글 워크스페이스(시트·폼·문서) 연동
  * **활용 및 가치:** 수업 시간 학생들의 탐구 활동 데이터를 실시간으로 수집하고, 교과 세부능력 및 특기사항(세특) 작성을 위한 구체적인 관찰 기록과 개별 맞춤형 피드백 생성을 돕는 웹 플랫폼입니다. 생활기록부 기재 시즌마다 밤을 새우며 겪던 행정 부담을 획기적으로 줄여줍니다."""

repl_sec14_item4_and_5 = """* **4. 교과 교수-평가-기록(교수평기) 및 세특 자동화 웹앱 (Google Apps Script 연동)**
  * **주소 및 환경:** Google Apps Script (`script.google.com`) 및 구글 워크스페이스(시트·폼·문서) 연동
  * **활용 및 가치:** 수업 시간 학생들의 탐구 활동 데이터를 실시간으로 수집하고, 교과 세부능력 및 특기사항(세특) 작성을 위한 구체적인 관찰 기록과 개별 맞춤형 피드백 생성을 돕는 웹 플랫폼입니다. 생활기록부 기재 시즌마다 밤을 새우며 겪던 행정 부담을 획기적으로 줄여줍니다.

* **5. 스마트폰 PWA 앱 연동 '음성 실시간 관찰기록 & 반별 세특 통합 대시보드 웹앱' (동료 교사 무상 공유형)**
  * **기술 및 환경:** 스마트폰 PWA(Progressive Web App) 앱 기술, 구글 앱스스크립트(GAS), 구글 시트 데이터베이스 연동
  * **활용 및 혁신적 가치:** 교사가 교실 수업이나 수행평가 중 스마트폰 PWA 앱을 켜고 말하면, 교사의 음성 관찰 기록이 실시간 텍스트로 변환되어 구글 시트에 차곡차곡 자동 저장됩니다. 교사용 모니터링 대시보드에서는 **반별로 어떤 학생에게 어떤 관찰 기록이 쌓였는지 한눈에 바로바로 정돈되어 시각화**되며, 이 데이터는 학기 말 영역별 세특 작성 시 그대로 안전하게 연동 반영됩니다.
  * **동료 교사 무상 공유 및 확장의 용이성 (★ 핵심 강점):** 이 웹앱은 고가의 솔루션을 구독할 필요 없이, 동료 선생님들이 구글 시트 복사(복사본 만들기) 단 한 번만으로 **누구나 즉시 자신의 학급과 교과에 100% 무상으로 쉽게 적용하고 공유할 수 있도록 완벽히 템플릿화**되어 있는 현장 친화적 결실입니다."""

if target_sec14_item4 in text:
    text = text.replace(target_sec14_item4, repl_sec14_item4_and_5)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESSFULLY ADDED ITEM 5 (PWA VOICE SETEUK DASHBOARD) TO SECTION 1.4!")
else:
    print("TARGET ITEM 4 NOT FOUND EXACTLY - CHECKING TEXT")
