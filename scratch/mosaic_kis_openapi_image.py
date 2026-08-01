import os
from PIL import Image, ImageFilter, ImageDraw

user_uploaded_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\.user_uploaded'
files = os.listdir(user_uploaded_dir)
latest_file = sorted(files, key=lambda x: os.path.getmtime(os.path.join(user_uploaded_dir, x)))[-1]
print(f"Latest uploaded file: {latest_file}")

src_path = os.path.join(user_uploaded_dir, latest_file)
im = Image.open(src_path)
width, height = im.size
print(f"Image size: {width} x {height}")

# 상단 상태바와 하단 윈도우/앱바 제거하는 깔끔한 자르기
# y: 40 ~ height - 60
crop_top = int(height * 0.04)
crop_bottom = int(height * 0.90)

cropped = im.crop((0, crop_top, width, crop_bottom))
c_w, c_h = cropped.size

# 모자이크 처리 대상 좌표 산정 (크롭된 이미지 기준)
# 1. 계좌주 '황요한' 영역 (오른쪽 상단)
# y_ratio ~ 0.23, x_ratio ~ 0.80 - 0.96
name_box = (int(c_w * 0.78), int(c_h * 0.22), int(c_w * 0.96), int(c_h * 0.27))

# 2. 계좌번호 '72394127' 뒤 4자리 영역 (오른쪽 중간)
# y_ratio ~ 0.29, x_ratio ~ 0.82 - 0.96
acct_box = (int(c_w * 0.70), int(c_h * 0.28), int(c_w * 0.96), int(c_h * 0.33))

# 모자이크 함수 (픽셀화)
def apply_mosaic(img, box, pixel_size=12):
    x1, y1, x2, y2 = box
    sub_img = img.crop((x1, y1, x2, y2))
    # 축소 후 확대하여 모자이크 효과
    small = sub_img.resize((max(1, (x2 - x1) // pixel_size), max(1, (y2 - y1) // pixel_size)), Image.NEAREST)
    mosaic = small.resize((x2 - x1, y2 - y1), Image.NEAREST)
    img.paste(mosaic, (x1, y1))

apply_mosaic(cropped, name_box, pixel_size=10)
apply_mosaic(cropped, acct_box, pixel_size=10)

output_dir = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder'
dest_path = os.path.join(output_dir, 'kis_openapi_hd.png')
artifact_path = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\kis_openapi_hd.png'

cropped.save(dest_path, 'PNG')
cropped.save(artifact_path, 'PNG')

print(f"SUCCESSFULLY MOSAICED AND SAVED TO: {dest_path}")
