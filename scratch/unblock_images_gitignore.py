import os

gitignore_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\.gitignore'

with open(gitignore_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.strip() in ['*.png', '*.jpg', '*.jpeg']:
        new_lines.append(f"# {line}")  # 이미지 제외 해제
    else:
        new_lines.append(line)

with open(gitignore_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("SUCCESSFULLY ALLOWED IMAGE FILES IN .GITIGNORE!")
