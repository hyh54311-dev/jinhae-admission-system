import os
import re

pattern = re.compile(r'\/d\/([a-zA-Z0-9-_]{40,})')
found_ids = {}

for root, dirs, files in os.walk('.'):
    if any(p in root for p in ['.git', '.google_messages_session', '.agents', 'node_modules', '__pycache__', 'temp']):
        continue
    for file in files:
        if file.endswith(('.py', '.js', '.gs', '.txt', '.md', '.html')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                matches = pattern.findall(content)
                for m in matches:
                    if m not in found_ids:
                        found_ids[m] = []
                    found_ids[m].append(path)
            except Exception:
                try:
                    with open(path, 'r', encoding='cp949') as f:
                        content = f.read()
                    matches = pattern.findall(content)
                    for m in matches:
                        if m not in found_ids:
                            found_ids[m] = []
                        found_ids[m].append(path)
                except Exception:
                    pass

print("Found Spreadsheet/Form/Doc IDs:")
for fid, paths in found_ids.items():
    print(f"ID: {fid}")
    print(f"  Referenced in: {paths}")
