import os
from PIL import Image

user_uploaded_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\.user_uploaded'
files = os.listdir(user_uploaded_dir)
# 3개 연속 업로드 중 세 번째(가장 최신/보고서 핵심) 파일 지정
latest_file = sorted(files, key=lambda x: os.path.getmtime(os.path.join(user_uploaded_dir, x)))[-1]
print(f"Latest uploaded file (Report): {latest_file}")

src_path = os.path.join(user_uploaded_dir, latest_file)
im = Image.open(src_path)
width, height = im.size

# 상단 상태바 & 하단 검은 여백 및 입력도구 100% 깔끔 크롭 (메시지 카드 뷰 유지)
crop_top = int(height * 0.045)
crop_bottom = int(height * 0.85)

cropped_report = im.crop((0, crop_top, width, crop_bottom))

output_dir = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder'
dest_path = os.path.join(output_dir, 'telegram_report_hd.png')
artifact_path = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\telegram_report_hd.png'

cropped_report.save(dest_path, 'PNG')
cropped_report.save(artifact_path, 'PNG')

print("SUCCESSFULLY CROPPED TELEGRAM REPORT IMAGE AND SAVED!")
