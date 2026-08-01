import os
from PIL import Image

user_uploaded_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\.user_uploaded'
files = os.listdir(user_uploaded_dir)
latest_file = sorted(files, key=lambda x: os.path.getmtime(os.path.join(user_uploaded_dir, x)))[-1]
print(f"Latest uploaded file: {latest_file}")

src_path = os.path.join(user_uploaded_dir, latest_file)
im = Image.open(src_path)
width, height = im.size
print(f"Image size: {width} x {height}")

# 상단 브라우저 북마크바/주소창 아래 & 하단 윈도우 작업표시줄 제외하고 핵심 영역 정밀 자르기
# x: 150 ~ 1720, y: 130 ~ 930
crop_x1 = int(width * 0.08)
crop_y1 = int(height * 0.12)
crop_x2 = int(width * 0.91)
crop_y2 = int(height * 0.88)

cropped = im.crop((crop_x1, crop_y1, crop_x2, crop_y2))

output_dir = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder'
dest_path = os.path.join(output_dir, 'github_secrets_hd.png')
artifact_path = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\github_secrets_hd.png'

cropped.save(dest_path, 'PNG')
cropped.save(artifact_path, 'PNG')

print("SUCCESSFULLY CROPPED GITHUB SECRETS IMAGE AND SAVED!")
