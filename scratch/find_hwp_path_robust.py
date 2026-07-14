import os
import glob
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

base_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교"
search_pattern = os.path.join(base_dir, "**", "*.hwpx")
files = glob.glob(search_pattern, recursive=True)

print("Listing all .hwpx files under Jinhae HS dir:")
count = 0
for f in files:
    if "진해고등학교" in f or "2026" in f:
        size = os.path.getsize(f)
        print(f"Path: {f}")
        print(f"Size: {size:,} bytes ({size / (1024*1024):.2f} MB)")
        count += 1
        if count >= 30:
            print("... truncated list ...")
            break
if count == 0:
    print("No .hwpx files containing '진해고등학교' or '2026' found.")
