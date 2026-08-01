import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_str = "--- \n\n### 4.3 [3단계] 저자가 수개월간 직접 겪고 해결한 Top 10 실전 트러블슈팅 디버깅집"

replacement_str = """![텔레그램 무인 매매 보고서 수신 스마트폰 화면](telegram_report_hd.png)
> 📸 **[도서 실전 캡처 이미지 5] AI 봇이 무인으로 매매를 완수한 뒤 텔레그램으로 답장해 준 실전 매매 보고서 수신 화면 (★ 도서 전체 메인 하이라이트)**

---

### 4.3 [3단계] 저자가 수개월간 직접 겪고 해결한 Top 10 실전 트러블슈팅 디버깅집"""

if target_str in text:
    new_text = text.replace(target_str, replacement_str)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("SUCCESSFULLY EMBEDDED TELEGRAM REPORT IMAGE INTO MANUSCRIPT SECTION 4.2 END!")
else:
    # Alternative target string search
    target_str2 = "### 4.3 [3단계] 저자가 수개월간 직접 겪고 해결한 Top 10 실전 트러블슈팅 디버깅집"
    if target_str2 in text:
        replacement_str2 = """![텔레그램 무인 매매 보고서 수신 스마트폰 화면](telegram_report_hd.png)
> 📸 **[도서 실전 캡처 이미지 5] AI 봇이 무인으로 매매를 완수한 뒤 텔레그램으로 답장해 준 실전 매매 보고서 수신 화면 (★ 도서 전체 메인 하이라이트)**

---

### 4.3 [3단계] 저자가 수개월간 직접 겪고 해결한 Top 10 실전 트러블슈팅 디버깅집"""
        new_text = text.replace(target_str2, replacement_str2)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_text)
        print("SUCCESSFULLY EMBEDDED TELEGRAM REPORT IMAGE VIA TARGET 2!")
    else:
        print("TARGET STR NOT FOUND")
