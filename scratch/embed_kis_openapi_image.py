import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_str = "##### 4. [4단계] 화면에 뜨는 비밀열쇠 2개 (`AppKey` / `AppSecret`) 카톡에 복사해 두기 ⚠️"

replacement_str = """![한국투자증권 Open API 서비스 신청 현황 모바일 화면](kis_openapi_hd.png)
> 📸 **[도서 실전 캡처 이미지 2] 한국투자증권(KIS) 모바일 앱 Open API 서비스 신청 완료 화면 (개인정보 보호 모자이크 완료)**

##### 4. [4단계] 화면에 뜨는 비밀열쇠 2개 (`AppKey` / `AppSecret`) 카톡에 복사해 두기 ⚠️"""

if target_str in text:
    new_text = text.replace(target_str, replacement_str)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("SUCCESSFULLY EMBEDDED KIS OPENAPI MOSAIC IMAGE INTO MANUSCRIPT!")
else:
    print("TARGET STR NOT FOUND")
