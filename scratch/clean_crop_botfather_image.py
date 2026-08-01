import os
from PIL import Image

user_uploaded_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\.user_uploaded'
files = os.listdir(user_uploaded_dir)
latest_file = sorted(files, key=lambda x: os.path.getmtime(os.path.join(user_uploaded_dir, x)))[-1]

src_path = os.path.join(user_uploaded_dir, latest_file)
im = Image.open(src_path)
width, height = im.size

# 상단 상태바 정리 및 하단 버튼 입력창 바로 아래까지 깔끔하게 크롭 (검은 마스크 100% 제거)
crop_top = int(height * 0.045)
crop_bottom = int(height * 0.85)

clean_cropped = im.crop((0, crop_top, width, crop_bottom))

output_dir = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder'
dest_path = os.path.join(output_dir, 'telegram_botfather_hd.png')
artifact_path = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\telegram_botfather_hd.png'

clean_cropped.save(dest_path, 'PNG')
clean_cropped.save(artifact_path, 'PNG')

print("SUCCESSFULLY REMOVED BLACK MASK AND CREATED CLEAN NATURAL CROP!")
