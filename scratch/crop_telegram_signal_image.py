import os
from PIL import Image

user_uploaded_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\.user_uploaded'
files = os.listdir(user_uploaded_dir)
# 최근 3개 파일 추출
latest_3 = sorted(files, key=lambda x: os.path.getmtime(os.path.join(user_uploaded_dir, x)))[-3:]

output_dir = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder'
artifact_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f'

# 1번: 가동 시작 & 모멘텀 선정 메시지
im1 = Image.open(os.path.join(user_uploaded_dir, latest_3[0]))
c1 = im1.crop((0, int(im1.height * 0.045), im1.width, int(im1.height * 0.85)))
c1.save(os.path.join(output_dir, 'telegram_signal_hd.png'))
c1.save(os.path.join(artifact_dir, 'telegram_signal_hd.png'))

print("ALL TELEGRAM REPORT AND SIGNAL IMAGES PREPARED!")
