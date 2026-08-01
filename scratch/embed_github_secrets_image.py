import os

file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

target_str = "템플릿 복사로 생성된 본인의 GitHub 저장소에서 **[Settings] ➔ [Secrets and variables] ➔ [Actions] ➔ [New repository secret]**을 누르고 아래 6개 Key 값을 등록합니다:"

replacement_str = """![GitHub Repository Secrets 6개 보안 변수 등록 화면](github_secrets_hd.png)
> 📸 **[도서 실전 캡처 이미지 4] GitHub Repository Secrets 6개 보안 변수 등록 목록 화면**

템플릿 복사로 생성된 본인의 GitHub 저장소에서 **[Settings] ➔ [Secrets and variables] ➔ [Actions] ➔ [New repository secret]**을 누르고 아래 6개 Key 값을 등록합니다:"""

if target_str in text:
    new_text = text.replace(target_str, replacement_str)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("SUCCESSFULLY EMBEDDED GITHUB SECRETS IMAGE INTO MANUSCRIPT!")
else:
    print("TARGET STR NOT FOUND")
