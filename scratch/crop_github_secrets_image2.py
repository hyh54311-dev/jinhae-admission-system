from PIL import Image
import os

user_uploaded_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\.user_uploaded'
files = os.listdir(user_uploaded_dir)
latest_file = sorted(files, key=lambda x: os.path.getmtime(os.path.join(user_uploaded_dir, x)))[-1]

src_path = os.path.join(user_uploaded_dir, latest_file)
im = Image.open(src_path)
width, height = im.size

# y: 70 ~ 530 (상단 주소창 아래 ~ 하단 작업표시줄 바로 위)
# x: 70 ~ 950
cropped = im.crop((int(width * 0.07), int(height * 0.12), int(width * 0.93), int(height * 0.91)))

output_dir = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder'
dest_path = os.path.join(output_dir, 'github_secrets_hd.png')
artifact_path = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\github_secrets_hd.png'

cropped.save(dest_path, 'PNG')
cropped.save(artifact_path, 'PNG')

print("RE-CROPPED PERFECTLY FOR 1024x576!")
