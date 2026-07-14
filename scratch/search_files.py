import os
import glob
import sys

sys.stdout.reconfigure(encoding='utf-8')

search_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도"

print(f"Searching for files containing '도움', '특수', '명렬', '명단' in {search_dir}:")
# recursive search
for root, dirs, files in os.walk(search_dir):
    for file in files:
        if any(kw in file for kw in ['도움', '특수', '명렬', '명단']):
            full_path = os.path.join(root, file)
            print(f"Found: {full_path}")
