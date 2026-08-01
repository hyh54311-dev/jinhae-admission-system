import os
from PIL import Image

image_path = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\.user_uploaded\media__1785304182157.png'
output_dir = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder'
output_path = os.path.join(output_dir, 'jinhae_bot2_cropped.png')

im = Image.open(image_path)
width, height = im.size

# 챗봇 카드 UI 정밀 자르기 (상단 파란색 Jinhae High School 로고부터 하단 입력창 및 버튼까지)
left = int(width * 0.33)
top = int(height * 0.17)
right = int(width * 0.67)
bottom = int(height * 0.93)

cropped_im = im.crop((left, top, right, bottom))
cropped_im.save(output_path, 'PNG')

artifact_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f'
artifact_output_path = os.path.join(artifact_dir, 'jinhae_bot2_cropped.png')
cropped_im.save(artifact_output_path, 'PNG')

print(f"PRECISION CROPPED: {cropped_im.size}")
