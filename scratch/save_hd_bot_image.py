import os
import shutil

user_uploaded_dir = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\.user_uploaded'
files = os.listdir(user_uploaded_dir)
print("Files in user_uploaded:")
for f in files:
    print(f)

# 가장 최신 파일 복사
latest_file = sorted(files, key=lambda x: os.path.getmtime(os.path.join(user_uploaded_dir, x)))[-1]
print(f"Latest uploaded file: {latest_file}")

src_path = os.path.join(user_uploaded_dir, latest_file)
dest_path = r'g:\다른 컴퓨터\내 컴퓨터\진해고등학교\2026학년도\antigravity_folder\jinhae_bot2_hd.png'
artifact_path = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\jinhae_bot2_hd.png'

shutil.copy(src_path, dest_path)
shutil.copy(src_path, artifact_path)

print(f"SUCCESSFULLY SAVED HIGH RES IMAGE TO: {dest_path}")
