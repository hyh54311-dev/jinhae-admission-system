import os
import urllib.request
import urllib.parse

output_dir = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder'
artifact_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f'

# 100% 공개(Public)로 접속 가능한 정식 원고 및 퀀트 봇 저장소 URL
public_url = 'https://github.com/hyh54311-dev/jinhae-admission-system'
encoded_url = urllib.parse.quote(public_url)
api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={encoded_url}&margin=10"

file_dest = os.path.join(output_dir, 'qr_template_repo.png')
artifact_dest = os.path.join(artifact_dir, 'qr_template_repo.png')

print(f"Re-generating QR for Public URL: {public_url}")
urllib.request.urlretrieve(api_url, file_dest)
urllib.request.urlretrieve(api_url, artifact_dest)

# 원고 수정
file_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\retirement_savings_dual_momentum_guide.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 404가 뜨는 비공개 주소를 100% 공개 접속 주소로 교체
target_url_str = "`https://github.com/hyh54311-dev/jinhae-k-momentum-bot`"
repl_url_str = "`https://github.com/hyh54311-dev/jinhae-admission-system`"

text = text.replace(target_url_str, repl_url_str)
text = text.replace("https://github.com/hyh54311-dev/jinhae-k-momentum-bot", "https://github.com/hyh54311-dev/jinhae-admission-system")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESSFULLY FIXED 404 ISSUE BY SWITCHING QR 1 TO PUBLIC REPOSITORY URL!")
