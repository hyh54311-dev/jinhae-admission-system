import os

dir_path = r'C:\Users\요한T\.gemini\antigravity\brain\215694ba-ced9-49e0-b226-cedc9de6be5f\.user_uploaded'
if os.path.exists(dir_path):
    files = os.listdir(dir_path)
    print("Files in user_uploaded:")
    for f in files:
        print(f)
else:
    print("Directory does not exist")
