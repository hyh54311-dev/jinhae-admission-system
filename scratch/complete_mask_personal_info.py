import os
from PIL import Image, ImageDraw

user_uploaded_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\.user_uploaded'
files = os.listdir(user_uploaded_dir)
latest_file = sorted(files, key=lambda x: os.path.getmtime(os.path.join(user_uploaded_dir, x)))[-1]

src_path = os.path.join(user_uploaded_dir, latest_file)
im = Image.open(src_path)
width, height = im.size

# 상하 크롭
crop_top = int(height * 0.04)
crop_bottom = int(height * 0.90)
cropped = im.crop((0, crop_top, width, crop_bottom))
c_w, c_h = cropped.size

draw = ImageDraw.Draw(cropped)

# 계좌주 영역 전체 100% 불투명 검정 덮어씌우기
# y: 0.22 ~ 0.28, x: 0.70 ~ 0.98
name_box = (int(c_w * 0.70), int(c_h * 0.22), int(c_w * 0.97), int(c_h * 0.28))
draw.rectangle(name_box, fill=(0, 0, 0))

# 계좌번호 영역 전체 100% 불투명 검정 덮어씌우기
# y: 0.28 ~ 0.34, x: 0.60 ~ 0.98
acct_box = (int(c_w * 0.60), int(c_h * 0.28), int(c_w * 0.97), int(c_h * 0.34))
draw.rectangle(acct_box, fill=(0, 0, 0))

output_dir = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder'
dest_path = os.path.join(output_dir, 'kis_openapi_hd.png')
artifact_path = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\kis_openapi_hd.png'

cropped.save(dest_path, 'PNG')
cropped.save(artifact_path, 'PNG')

print("SUCCESSFULLY 100% COMPLETELY BLOCKED PERSONAL INFO WITH SOLID BLACK MASK!")
