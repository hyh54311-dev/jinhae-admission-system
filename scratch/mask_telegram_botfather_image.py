import os
from PIL import Image, ImageDraw

user_uploaded_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\.user_uploaded'
files = os.listdir(user_uploaded_dir)
latest_file = sorted(files, key=lambda x: os.path.getmtime(os.path.join(user_uploaded_dir, x)))[-1]
print(f"Latest uploaded file: {latest_file}")

src_path = os.path.join(user_uploaded_dir, latest_file)
im = Image.open(src_path)
width, height = im.size
print(f"Image size: {width} x {height}")

# 상단 상태바 크롭 및 하단 자르기
crop_top = int(height * 0.045)
crop_bottom = int(height * 0.88)
cropped = im.crop((0, crop_top, width, crop_bottom))
c_w, c_h = cropped.size

draw = ImageDraw.Draw(cropped)

# 하단 입력창 아래 살짝 비치는 토큰 암호 영역 100% 검정 솔리드 마스크 차단
# y: 0.82 ~ 1.00
token_mask_box = (0, int(c_h * 0.82), c_w, c_h)
draw.rectangle(token_mask_box, fill=(0, 0, 0))

output_dir = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder'
dest_path = os.path.join(output_dir, 'telegram_botfather_hd.png')
artifact_path = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\telegram_botfather_hd.png'

cropped.save(dest_path, 'PNG')
cropped.save(artifact_path, 'PNG')

print("SUCCESSFULLY MASKED BOTFATHER IMAGE AND SAVED!")
