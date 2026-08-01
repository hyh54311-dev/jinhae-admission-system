import os
from PIL import Image

image_path = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\.user_uploaded\media__1785304182157.png'
output_dir = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder'
output_path = os.path.join(output_dir, 'jinhae_bot2_cropped.png')

im = Image.open(image_path)
width, height = im.size
print(f"Original image size: {width} x {height}")

# 챗봇 카드 UI 중앙 정밀 자르기
left = int(width * 0.32)
top = int(height * 0.16)
right = int(width * 0.68)
bottom = int(height * 0.92)

cropped_im = im.crop((left, top, right, bottom))
cropped_im.save(output_path, 'PNG')

# artifacts 디렉토리에도 복사
artifact_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f'
artifact_output_path = os.path.join(artifact_dir, 'jinhae_bot2_cropped.png')
cropped_im.save(artifact_output_path, 'PNG')

print(f"SUCCESSFULLY CROPPED IMAGE SAVED TO: {output_path}")
