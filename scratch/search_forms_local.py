import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

search_dir = r"D:\OneDrive - 경상남도교육청\바탕 화면\진해고등학교\2026학년도"

print("Searching for 'forms/' in files:")
for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.endswith(('.txt', '.html', '.xlsx', '.gsheet', '.gdoc', '.hwp', '.hwpx')):
            full_path = os.path.join(root, file)
            # Skip large binary files or open them carefully
            if file.endswith(('.xlsx', '.hwp', '.hwpx')):
                continue
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if 'forms/d' in content or 'docs.google.com/forms' in content:
                        print(f"Found in {full_path}:")
                        # Print lines containing the match
                        for line in content.split('\n'):
                            if 'forms' in line:
                                print(f"  {line[:200]}")
            except Exception as e:
                pass
print("Done searching.")
