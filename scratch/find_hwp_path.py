import os
import glob
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교"
search_pattern = os.path.join(base_dir, "**", "*학규집*.hwpx")
files = glob.glob(search_pattern, recursive=True)

if files:
    for f in files:
        size = os.path.getsize(f)
        print(f"Path: {f}")
        print(f"Size: {size:,} bytes ({size / (1024*1024):.2f} MB)")
else:
    print("No file matching '*학규집*.hwpx' found.")
